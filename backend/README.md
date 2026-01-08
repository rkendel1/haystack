# Backend API for Supabase Document Store

This directory contains a FastAPI backend that demonstrates how to use the SupabaseDocumentStore in a production-like setting.

## Features

- **Document Indexing**: Add documents to the Supabase document store
- **Hybrid Search**: Search using both semantic and keyword search
- **RAG (Retrieval-Augmented Generation)**: Chat interface with context retrieval

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

### GET /

Health check and API information.

### POST /index

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

### POST /search

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

### POST /chat

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

### GET /count

Get the total number of documents in the store.

**Response:**
```json
{
  "count": 42
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
├── main.py                  # FastAPI application
├── Dockerfile              # Docker configuration
└── requirements.txt        # Python dependencies
```

## Development

### Testing the API

Use curl or tools like Postman/Insomnia:

```bash
# Index a document
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document", "metadata": {"type": "test"}}'

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'

# Get count
curl http://localhost:8000/count
```

### API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection URL (required)
- `OPENAI_API_KEY`: OpenAI API key for embeddings and generation (required for embeddings)

## Notes

- The API requires a running Supabase PostgreSQL instance with pgvector extension
- Embeddings are generated using OpenAI by default (requires API key)
- For production use, add authentication, rate limiting, and error handling
