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

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.document_store.supabase_store import get_supabase_store
from backend.pipelines.rag_pipeline import create_rag_pipeline, retrieve
from haystack.dataclasses import Document

app = FastAPI(title="Haystack Supabase RAG API")


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
        "message": "Haystack Supabase RAG API",
        "endpoints": {
            "index": "/index - POST - Index a document",
            "search": "/search - POST - Search for documents",
            "chat": "/chat - POST - Chat with RAG",
            "count": "/count - GET - Get document count",
        },
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
