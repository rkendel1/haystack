# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
FastAPI backend for Supabase-backed RAG system.

This module provides a simple REST API for indexing and searching documents.

To run:
    pip install fastapi uvicorn
    uvicorn backend.main:app --reload --port 8000
"""

from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.document_store.supabase_store import get_supabase_store
from backend.models.context import (
    CompanyInfo,
    ContextObject,
    ContextObjectUpdate,
    OnboardingContextResponse,
    OnboardingSession,
    OnboardingSessionCreate,
)
from backend.pipelines.rag_pipeline import create_rag_pipeline, retrieve
from backend.reasoning.context_extraction import OnboardingPipeline
from backend.services.context_db import ContextDatabaseService
from haystack.dataclasses import Document

app = FastAPI(title="Haystack Supabase RAG API")

# Initialize services
context_service = ContextDatabaseService()
onboarding_pipeline = OnboardingPipeline()


class IndexRequest(BaseModel):
    """Request model for indexing documents."""

    content: str
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    """Request model for search."""

    query: str
    top_k: Optional[int] = 10


class ChatRequest(BaseModel):
    """Request model for chat/RAG."""

    query: str
    top_k: Optional[int] = 5


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Haystack Supabase RAG API - First-Class Context Canonicalization",
        "endpoints": {
            "index": "/index - POST - Index a document",
            "search": "/search - POST - Search for documents",
            "chat": "/chat - POST - Chat with RAG",
            "count": "/count - GET - Get document count",
            "onboarding": {
                "start": "/onboarding/start - POST - Start onboarding",
                "context": "/onboarding/{session_id}/context - GET - Get discovered context",
            },
            "context": {
                "list": "/context - GET - List context objects",
                "get": "/context/{id} - GET - Get context object",
                "update": "/context/{id} - PATCH - Update context object",
                "delete": "/context/{id} - DELETE - Delete context object",
                "confirm": "/context/{id}/confirm - POST - Confirm context object",
                "reject": "/context/{id}/reject - POST - Reject context object",
            },
            "relationships": {
                "create": "/context/relationships - POST - Create relationship between contexts",
                "get": "/context/{id}/relationships - GET - Get relationships for a context",
                "related": "/context/{id}/related - GET - Get related context objects",
                "delete": "/context/relationships - DELETE - Delete a relationship",
            },
            "canonical_types": {
                "validate": "/context/validate - POST - Validate content against canonical schema",
                "types": "/context/types - GET - Get information about canonical types",
            },
        },
        "canonical_types": [
            "idea - Uncommitted concepts and hypotheses",
            "decision - Explicit commitments",
            "assumption - Beliefs taken as true",
            "evidence - Support or refutation",
            "plan - Intent and execution tracking",
            "outcome - What actually happened",
        ],
    }


@app.post("/index")
async def index_document(request: IndexRequest):
    """
    Index a document into the Supabase document store.

    Example:
        POST /index
        {
            "content": "Haystack is an LLM framework...",
            "metadata": {"source": "docs", "type": "tutorial"}
        }
    """
    try:
        store = get_supabase_store()

        # Create document
        doc = Document(content=request.content, meta=request.metadata or {})

        # Write to store
        count = store.write_documents([doc])

        return {"status": "success", "documents_indexed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search for documents using hybrid retrieval.

    Example:
        POST /search
        {
            "query": "What is Haystack?",
            "top_k": 10
        }
    """
    try:
        documents = retrieve(request.query)
        return {
            "query": request.query,
            "documents": [
                {"content": doc.content, "metadata": doc.meta, "score": doc.score} for doc in documents[: request.top_k]
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_with_rag(request: ChatRequest):
    """
    Chat with RAG using the Supabase document store.

    Example:
        POST /chat
        {
            "query": "What is Haystack?",
            "top_k": 5
        }
    """
    try:
        # Create RAG pipeline
        pipeline = create_rag_pipeline()

        # Run pipeline with all required inputs
        result = pipeline.run(
            {
                "text_embedder": {"text": request.query},
                "retriever": {"query": request.query},
                "prompt_builder": {"query": request.query},
            }
        )

        return {"query": request.query, "answer": result["llm"]["replies"][0] if result.get("llm") else "No answer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/count")
async def count_documents():
    """Get the total number of documents in the store."""
    try:
        store = get_supabase_store()
        count = store.count_documents()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================


@app.post("/onboarding/start", response_model=OnboardingSession)
async def start_onboarding(company_info: CompanyInfo):
    """
    Start a new onboarding session.

    Example:
        POST /onboarding/start
        {
            "name": "Acme Corp",
            "website": "https://acme.com",
            "industry": "Technology"
        }
    """
    try:
        # Create onboarding session
        # TODO: Replace with actual user ID from authentication middleware
        # For production, implement proper authentication and extract user_id from JWT/session
        user_id = "demo_user"  # SECURITY: This must be replaced with authenticated user ID

        session = context_service.create_onboarding_session(
            OnboardingSessionCreate(
                user_id=user_id,
                company_name=company_info.name,
                company_website=company_info.website,
                industry=company_info.industry,
            )
        )

        # Run context discovery in background
        # TODO: Move to background task processing (e.g., Celery, FastAPI BackgroundTasks)
        # For production, this should use async background processing to avoid request timeouts
        # Example: background_tasks.add_task(run_context_discovery, session.id, company_info)
        discovered_contexts = onboarding_pipeline.run(
            company_name=company_info.name, website=company_info.website, industry=company_info.industry
        )

        # Store discovered contexts
        from backend.models.context import ContextObjectCreate

        context_objects = [ContextObjectCreate(**ctx) for ctx in discovered_contexts]
        context_service.bulk_create_context_objects(context_objects)

        # Update session step
        context_service.update_onboarding_session(session.id, OnboardingSessionUpdate(current_step="context_review"))

        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/onboarding/{session_id}/context", response_model=OnboardingContextResponse)
async def get_onboarding_context(session_id: UUID):
    """
    Get discovered context for an onboarding session.

    Returns all inferred context objects for user review.
    """
    try:
        session = context_service.get_onboarding_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")

        # Get all pending contexts (could filter by session in production)
        contexts = context_service.list_context_objects(status="pending", limit=100)

        # Calculate progress
        context_types = set(ctx.type for ctx in contexts)
        progress = {"discovered": len(contexts), "total_categories": len(context_types), "categories": list(context_types)}

        return OnboardingContextResponse(session_id=session_id, contexts=contexts, progress=progress)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONTEXT MANAGEMENT ENDPOINTS
# ============================================================================


@app.get("/context", response_model=List[ContextObject])
async def list_contexts(
    type: Optional[str] = None, status: Optional[str] = None, source: Optional[str] = None, limit: int = 100, offset: int = 0
):
    """
    List context objects with optional filters.

    Query Parameters:
        - type: Filter by context type (company, industry, regulation, etc.)
        - status: Filter by status (pending, confirmed, rejected)
        - source: Filter by source (external, inferred, user)
        - limit: Maximum number of results (default: 100)
        - offset: Offset for pagination (default: 0)
    """
    try:
        contexts = context_service.list_context_objects(
            context_type=type, status=status, source=source, limit=limit, offset=offset
        )
        return contexts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/{context_id}", response_model=ContextObject)
async def get_context(context_id: UUID):
    """Get a specific context object by ID."""
    try:
        context = context_service.get_context_object(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Context object not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/context/{context_id}", response_model=ContextObject)
async def update_context(context_id: UUID, update: ContextObjectUpdate):
    """
    Update a context object.

    Example:
        PATCH /context/{id}
        {
            "content": {"updated": "data"},
            "status": "confirmed"
        }
    """
    try:
        context = context_service.update_context_object(context_id, update)
        if not context:
            raise HTTPException(status_code=404, detail="Context object not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/context/{context_id}")
async def delete_context(context_id: UUID):
    """Soft delete a context object."""
    try:
        deleted = context_service.delete_context_object(context_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Context object not found")
        return {"status": "deleted", "id": str(context_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context/{context_id}/confirm", response_model=ContextObject)
async def confirm_context(context_id: UUID):
    """Confirm a context object (change status to 'confirmed')."""
    try:
        context = context_service.confirm_context_object(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Context object not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context/{context_id}/reject", response_model=ContextObject)
async def reject_context(context_id: UUID):
    """Reject a context object (change status to 'rejected')."""
    try:
        context = context_service.reject_context_object(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Context object not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RELATIONSHIP ENDPOINTS
# ============================================================================


class CreateRelationshipRequest(BaseModel):
    """Request model for creating a relationship."""

    from_context_id: UUID
    to_context_id: UUID
    relationship_type: str
    metadata: Optional[dict] = None


@app.post("/context/relationships")
async def create_relationship(request: CreateRelationshipRequest):
    """
    Create a relationship between two context objects.

    Example:
        POST /context/relationships
        {
            "from_context_id": "uuid1",
            "to_context_id": "uuid2",
            "relationship_type": "supports",
            "metadata": {"strength": "strong"}
        }
    """
    try:
        relationship = context_service.create_relationship(
            from_context_id=request.from_context_id,
            to_context_id=request.to_context_id,
            relationship_type=request.relationship_type,
            metadata=request.metadata,
        )
        if not relationship:
            raise HTTPException(status_code=409, detail="Relationship already exists")
        return relationship
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/{context_id}/relationships")
async def get_relationships(context_id: UUID, direction: str = "both"):
    """
    Get relationships for a context object.

    Query Parameters:
        - direction: 'outgoing', 'incoming', or 'both' (default: both)
    """
    try:
        relationships = context_service.get_relationships(context_id, direction=direction)
        return {"context_id": str(context_id), "direction": direction, "relationships": relationships}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/{context_id}/related")
async def get_related_contexts(
    context_id: UUID, relationship_type: Optional[str] = None, direction: str = "outgoing"
):
    """
    Get context objects related to a given context.

    Query Parameters:
        - relationship_type: Filter by relationship type (optional)
        - direction: 'outgoing' or 'incoming' (default: outgoing)
    """
    try:
        related = context_service.get_related_contexts(
            context_id=context_id, relationship_type=relationship_type, direction=direction
        )
        return {"context_id": str(context_id), "relationship_type": relationship_type, "related_contexts": related}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/context/relationships")
async def delete_relationship(from_context_id: UUID, to_context_id: UUID, relationship_type: str):
    """
    Delete a specific relationship.

    Query Parameters:
        - from_context_id: Source context ID
        - to_context_id: Target context ID
        - relationship_type: Type of relationship
    """
    try:
        deleted = context_service.delete_relationship(
            from_context_id=from_context_id, to_context_id=to_context_id, relationship_type=relationship_type
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Relationship not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CANONICAL TYPE VALIDATION ENDPOINTS
# ============================================================================


@app.post("/context/validate")
async def validate_canonical_type(context_type: str, content: dict):
    """
    Validate that content conforms to canonical schema for the given type.

    Example:
        POST /context/validate?context_type=idea
        {
            "problem_statement": "...",
            "proposed_solution": "...",
            ...
        }
    """
    try:
        from backend.models.canonical_types import validate_canonical_content

        validated = validate_canonical_content(context_type, content)
        return {"valid": True, "type": context_type, "validated_content": validated.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/types")
async def get_canonical_types():
    """
    Get information about canonical context types.

    Returns the list of canonical types and their required fields.
    """
    try:
        from backend.models.canonical_types import CANONICAL_TYPE_MAP, get_required_fields

        types_info = {}
        for type_name in CANONICAL_TYPE_MAP.keys():
            types_info[type_name] = {
                "required_fields": get_required_fields(type_name),
                "schema": CANONICAL_TYPE_MAP[type_name].model_json_schema(),
            }
        return {"canonical_types": list(CANONICAL_TYPE_MAP.keys()), "types_info": types_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
