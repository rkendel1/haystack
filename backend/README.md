# Backend API for Supabase Document Store

This directory contains a FastAPI backend that demonstrates how to use the SupabaseDocumentStore in a production-like setting.

## Features

- **Document Indexing**: Add documents to the Supabase document store
- **Hybrid Search**: Search using both semantic and keyword search
- **RAG (Retrieval-Augmented Generation)**: Chat interface with context retrieval
- **Smart Onboarding**: Automated business context discovery and management
- **First-Class Context Canonicalization**: Business reasoning layer with 6 canonical document types
- **Relationship Graph**: Explicit links between context artifacts for reasoning
- **Context Management**: Full CRUD operations with versioning and soft deletes

## Setup

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:54322/postgres"
export OPENAI_API_KEY="your-api-key"
```

3. Run the server:

```bash
uvicorn main:app --reload --port 8000
```

### Docker

Build and run using Docker Compose:

```bash
cd ../docker
docker compose up backend
```

## API Endpoints

### Document Store Endpoints

#### GET /

Health check and API information.

#### POST /index

Index a document into the store.

**Request:**
```json
{
  "content": "Your document content here",
  "metadata": {
    "source": "web",
    "category": "docs"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "documents_indexed": 1
}
```

#### POST /search

Search for documents using hybrid retrieval.

**Request:**
```json
{
  "query": "What is Haystack?",
  "top_k": 10
}
```

**Response:**
```json
{
  "query": "What is Haystack?",
  "documents": [
    {
      "content": "Haystack is an LLM framework...",
      "metadata": {"source": "docs"},
      "score": 0.95
    }
  ]
}
```

#### POST /chat

Chat with RAG using retrieved context.

**Request:**
```json
{
  "query": "What is Haystack?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is Haystack?",
  "answer": "Haystack is an end-to-end LLM framework..."
}
```

#### GET /count

Get the total number of documents in the store.

**Response:**
```json
{
  "count": 42
}
```

### Smart Onboarding Endpoints

#### POST /onboarding/start

Start a new onboarding session and trigger context discovery.

**Request:**
```json
{
  "name": "Acme Corp",
  "website": "https://acme.com",
  "industry": "Technology"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "demo_user",
  "company_name": "Acme Corp",
  "company_website": "https://acme.com",
  "industry": "Technology",
  "current_step": "context_review",
  "status": "in_progress",
  "created_at": "2024-01-08T...",
  "updated_at": "2024-01-08T..."
}
```

#### GET /onboarding/{session_id}/context

Get discovered context for an onboarding session.

**Response:**
```json
{
  "session_id": "uuid",
  "contexts": [
    {
      "id": "uuid",
      "type": "company",
      "content": {
        "description": "...",
        "business_model": "B2B"
      },
      "source": "inferred",
      "confidence": 0.7,
      "status": "pending",
      "evidence_refs": ["https://acme.com"]
    }
  ],
  "progress": {
    "discovered": 12,
    "total_categories": 6,
    "categories": ["company", "regulation", "persona", "competitor", "industry", "assumption"]
  }
}
```

### Context Management Endpoints

#### GET /context

List context objects with optional filters.

**Query Parameters:**
- `type`: Filter by context type (company, industry, regulation, competitor, persona, assumption)
- `status`: Filter by status (pending, confirmed, rejected)
- `source`: Filter by source (external, inferred, user)
- `limit`: Maximum results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "type": "regulation",
    "content": {
      "name": "GDPR",
      "jurisdiction": "EU",
      "category": "privacy"
    },
    "source": "inferred",
    "confidence": 0.8,
    "status": "confirmed",
    "evidence_refs": [],
    "version": 1,
    "created_at": "2024-01-08T...",
    "updated_at": "2024-01-08T..."
  }
]
```

#### GET /context/{id}

Get a specific context object by ID.

#### PATCH /context/{id}

Update a context object.

**Request:**
```json
{
  "content": {"updated": "data"},
  "status": "confirmed",
  "confidence": 0.9
}
```

#### DELETE /context/{id}

Soft delete a context object.

**Response:**
```json
{
  "status": "deleted",
  "id": "uuid"
}
```

#### POST /context/{id}/confirm

Confirm a context object (shortcut for updating status to 'confirmed').

#### POST /context/{id}/reject

Reject a context object (shortcut for updating status to 'rejected').

### Relationship Endpoints

#### POST /context/relationships

Create a relationship between two context objects.

**Request:**
```json
{
  "from_context_id": "uuid1",
  "to_context_id": "uuid2",
  "relationship_type": "supports",
  "metadata": {"strength": "strong"}
}
```

#### GET /context/{id}/relationships

Get all relationships for a context object.

**Query Parameters:**
- `direction`: 'outgoing', 'incoming', or 'both' (default: both)

#### GET /context/{id}/related

Get related context objects.

**Query Parameters:**
- `relationship_type`: Filter by relationship type (optional)
- `direction`: 'outgoing' or 'incoming' (default: outgoing)

#### DELETE /context/relationships

Delete a specific relationship.

**Query Parameters:**
- `from_context_id`: Source context ID
- `to_context_id`: Target context ID
- `relationship_type`: Type of relationship

### Canonical Type Endpoints

#### POST /context/validate

Validate that content conforms to canonical schema for a given type.

**Query Parameters:**
- `context_type`: The canonical type (idea, decision, assumption, evidence, plan, outcome)

**Request:**
```json
{
  "problem_statement": "Sales team lacks context",
  "proposed_solution": "Build context panel",
  "target_user": "Account Executives",
  "claimed_advantage": "Reduces prep time",
  "confidence": 0.7
}
```

**Response:**
```json
{
  "valid": true,
  "type": "idea",
  "validated_content": {...}
}
```

#### GET /context/types

Get information about all canonical types, including required fields and schemas.

**Response:**
```json
{
  "canonical_types": ["idea", "decision", "assumption", "evidence", "plan", "outcome"],
  "types_info": {
    "idea": {
      "required_fields": ["problem_statement", "proposed_solution", "target_user", "claimed_advantage", "confidence"],
      "schema": {...}
    }
  }
}
```

## Project Structure

```
backend/
├── document_store/
│   └── supabase_store.py    # Document store utilities
├── retrieval/
│   └── hybrid_retriever.py  # Hybrid search logic
├── pipelines/
│   └── rag_pipeline.py      # RAG pipeline setup
├── models/
│   ├── __init__.py          # Models exports
│   ├── context.py           # Base context models (ContextObject, OnboardingSession)
│   └── canonical_types.py   # Canonical document types (6 first-class types)
├── services/
│   └── context_db.py        # Database service layer with relationship support
├── reasoning/
│   ├── context_extraction.py # AI-powered context extraction pipelines
│   └── type_mapper.py       # Legacy to canonical type migration
├── scripts/
│   └── migrate_to_canonical.py # Migration script for existing data
├── tests/
│   ├── test_context_api.py  # API tests
│   ├── test_canonical_types.py # Canonical type validation tests
│   ├── test_type_mapper.py  # Migration logic tests
│   └── test_relationships.py # Relationship graph tests
├── main.py                  # FastAPI application
├── CANONICAL_TYPES.md      # Canonical types documentation
├── Dockerfile              # Docker configuration
└── requirements.txt        # Python dependencies
```

## Smart Onboarding System

The Smart Onboarding system automatically discovers business context during user signup:

1. **Company Info Collection**: User provides company name, website, and optional industry
2. **Context Discovery**: AI pipelines extract:
   - Company profile (description, business model, geography)
   - Industry classification
   - Applicable regulations
   - Competitive landscape
   - Customer personas (constraint-based)
   - Baseline assumptions
3. **User Review**: All inferred context is presented for review, editing, approval, or rejection
4. **Context Management**: Users can continuously manage context objects post-onboarding

## First-Class Context Canonicalization

All context artifacts are normalized into **six canonical document types**:

1. **Ideas** - Uncommitted concepts and hypotheses
2. **Decisions** - Explicit commitments
3. **Assumptions** - Beliefs taken as true
4. **Evidence** - Support or refutation
5. **Plans** - Intent and execution tracking
6. **Outcomes** - What actually happened

### Canonical Context Benefits

- **Prevents Decision Re-litigation**: Past decisions are explicitly documented
- **Enables Historical Reasoning**: "What assumptions supported this decision?"
- **Surfaces Hidden Risk**: Track assumption decay and contradicting evidence
- **Bridges Strategy → Reality**: Link plans to outcomes
- **Enables Learning**: Compare expected vs actual outcomes

### Legacy Type Migration

Legacy context types (company, regulation, competitor, persona) are automatically migrated to canonical Evidence format. The system includes:

- **Type Inference**: Automatically determines canonical type from content
- **Content Migration**: Converts legacy structures to canonical schemas
- **Validation**: Ensures all content meets canonical requirements
- **Backward Compatibility**: No breaking changes to existing APIs

To migrate existing data:

```bash
# Dry run (see what would change)
python backend/scripts/migrate_to_canonical.py --dry-run

# Apply migration
python backend/scripts/migrate_to_canonical.py
```

For detailed documentation, see [CANONICAL_TYPES.md](CANONICAL_TYPES.md).

### Context Object Types (Legacy)

**Note**: These are legacy types that map to canonical Evidence:

- **company**: Company profile and business information → Evidence
- **industry**: Industry classification and characteristics → Evidence
- **regulation**: Applicable regulatory frameworks → Evidence
- **competitor**: Competitive landscape and market adjacencies → Evidence  
- **persona**: Customer archetypes (roles, not individuals) → Evidence
- **assumption**: Baseline business assumptions → Assumption (canonical)

### Security Principles

- ✅ All inferred data requires user review (nothing auto-confirmed)
- ✅ Input sanitization to prevent prompt injection
- ✅ Evidence tracking for all inferred context
- ✅ Clear distinction between inferred and confirmed knowledge
- ✅ Full user control (edit, confirm, reject, delete)

### Production Deployment Notes

⚠️ **Before Production:**

1. **Authentication**: Replace `user_id = "demo_user"` with actual authenticated user ID from JWT/session
2. **Background Processing**: Move long-running context discovery to background tasks (Celery, FastAPI BackgroundTasks)
3. **Rate Limiting**: Add rate limiting for AI endpoints to prevent abuse
4. **Error Handling**: Enhance error handling and logging
5. **Monitoring**: Add metrics and monitoring for context discovery performance

## Development

### Testing the API

Use curl or tools like Postman/Insomnia:

```bash
# Start onboarding
curl -X POST http://localhost:8000/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "website": "https://acme.com", "industry": "Technology"}'

# Get discovered contexts
curl http://localhost:8000/onboarding/{session_id}/context

# List all contexts
curl http://localhost:8000/context?status=pending

# Confirm a context
curl -X POST http://localhost:8000/context/{context_id}/confirm

# Index a document
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document", "metadata": {"type": "test"}}'

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'
```

### Running Tests

```bash
# Run all backend tests
pytest backend/tests/

# Run specific test files
pytest backend/tests/test_canonical_types.py
pytest backend/tests/test_type_mapper.py
pytest backend/tests/test_relationships.py
```

### API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection URL (required)
- `OPENAI_API_KEY`: OpenAI API key for embeddings and generation (required)

## Database Migrations

The Smart Onboarding system requires additional database tables. Run the migration:

```bash
psql $DATABASE_URL < ../supabase/init/003_context_management.sql
```

## Documentation

For detailed documentation, see:
- [Canonical Types Documentation](CANONICAL_TYPES.md) - Complete guide to the 6 canonical document types
- [Smart Onboarding Documentation](../docs/SMART_ONBOARDING.md) - Smart Onboarding system overview
- API Documentation (when server is running):
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## Notes

- The API requires a running Supabase PostgreSQL instance with pgvector extension
- Embeddings are generated using OpenAI by default (requires API key)
- For production use, implement authentication, rate limiting, and proper error handling
- Context discovery uses GPT-4o-mini for cost-effective inference
