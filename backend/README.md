# Backend API for Supabase Document Store

This directory contains a FastAPI backend that demonstrates how to use the SupabaseDocumentStore in a production-like setting.

## Features

- **Document Indexing**: Add documents to the Supabase document store
- **Hybrid Search**: Search using both semantic and keyword search
- **RAG (Retrieval-Augmented Generation)**: Chat interface with context retrieval
- **Smart Onboarding**: Automated business context discovery and management
- **Context Management**: First-class context objects with full CRUD operations

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
│   └── context.py           # Pydantic models for context objects
├── services/
│   └── context_db.py        # Database service layer for context management
├── reasoning/
│   └── context_extraction.py # AI-powered context extraction pipelines
├── tests/
│   └── test_context_api.py  # API tests
├── main.py                  # FastAPI application
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

### Context Object Types

- **company**: Company profile and business information
- **industry**: Industry classification and characteristics
- **regulation**: Applicable regulatory frameworks
- **competitor**: Competitive landscape and market adjacencies
- **persona**: Customer archetypes (roles, not individuals)
- **assumption**: Baseline business assumptions

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
pytest backend/tests/
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

For detailed documentation on the Smart Onboarding system, see:
- [Smart Onboarding Documentation](../docs/SMART_ONBOARDING.md)

## Notes

- The API requires a running Supabase PostgreSQL instance with pgvector extension
- Embeddings are generated using OpenAI by default (requires API key)
- For production use, implement authentication, rate limiting, and proper error handling
- Context discovery uses GPT-4o-mini for cost-effective inference
