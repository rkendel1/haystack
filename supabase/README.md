# Local Supabase-Backed Hybrid Document Store for Haystack

This integration provides a fully self-hosted, Dockerized document store for Haystack using local Supabase (PostgreSQL + pgvector + full-text search) to support:

- ✅ Semantic vector search (pgvector)
- ✅ Keyword / lexical search (PostgreSQL FTS)
- ✅ Hybrid search (score fusion)
- ✅ Fully offline / self-hosted
- ✅ One-command Docker startup
- ✅ Automatic DB bootstrapping
- ✅ Production-ready persistence

## Architecture

```
┌─────────────┐
│  Frontend   │
│ (React)     │
└──────┬──────┘
       │
┌──────▼──────┐
│  Backend    │  FastAPI
│  Haystack   │
│  RAG API    │
└──────┬──────┘
       │ SQL + vectors
┌──────▼──────────┐
│ Supabase Local  │
│ Postgres 15     │
│ pgvector        │
│ Full-Text Search│
└─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ (for local development)
- OpenAI API key (for embeddings and generation)

### One-Command Startup

```bash
cd docker
docker compose up --build
```

This automatically:
- Starts Supabase Postgres with pgvector
- Creates document tables and indexes
- Boots the backend API
- Enables hybrid search capabilities

### Services

After starting, the following services will be available:

- **Supabase Database**: `localhost:54322` (PostgreSQL)
- **Backend API**: `http://localhost:8000` (FastAPI)
- **Frontend**: `http://localhost:3000` (React)
- **SearXNG**: `http://localhost:8888` (Web Search)

## Installation

### Local Development

Install the Supabase document store dependencies:

```bash
pip install haystack-ai sqlalchemy psycopg2-binary pgvector
```

For the backend API:

```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Using the SupabaseDocumentStore

```python
from backend.document_store.supabase_store import SupabaseDocumentStore
from haystack.dataclasses import Document

# Initialize the document store
document_store = SupabaseDocumentStore(
    db_url="postgresql://postgres:postgres@localhost:54322/postgres"
)

# Write documents
documents = [
    Document(content="Haystack is an LLM framework for building RAG applications."),
    Document(content="pgvector enables vector similarity search in PostgreSQL."),
]

document_store.write_documents(documents)

# Count documents
count = document_store.count_documents()
print(f"Total documents: {count}")
```

### Using the Hybrid Retriever

```python
from haystack import Pipeline
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.retrievers.supabase import SupabaseHybridRetriever
from backend.document_store.supabase_store import SupabaseDocumentStore

# Create document store
document_store = SupabaseDocumentStore(
    db_url="postgresql://postgres:postgres@localhost:54322/postgres"
)

# Create pipeline
pipeline = Pipeline()
pipeline.add_component("embedder", OpenAITextEmbedder())
pipeline.add_component(
    "retriever",
    SupabaseHybridRetriever(
        document_store=document_store,
        alpha=0.6,  # 60% semantic, 40% keyword
        top_k=10
    )
)

# Connect components
pipeline.connect("embedder.embedding", "retriever.query_embedding")

# Run search
result = pipeline.run({
    "embedder": {"text": "What is Haystack?"},
    "retriever": {"query": "What is Haystack?"}
})

documents = result["retriever"]["documents"]
for doc in documents:
    print(f"Score: {doc.score:.3f} - {doc.content}")
```
```

### Building a RAG Pipeline

```python
from haystack import Pipeline
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.components.retrievers.supabase import SupabaseHybridRetriever
from haystack.document_stores.supabase import SupabaseDocumentStore

# Create document store
document_store = SupabaseDocumentStore(
    db_url="postgresql://postgres:postgres@localhost:54322/postgres"
)

# Create pipeline
pipeline = Pipeline()

# Add components
pipeline.add_component("embedder", OpenAITextEmbedder())
pipeline.add_component(
    "retriever",
    SupabaseHybridRetriever(document_store=document_store, top_k=5)
)

template = """
Answer the question based on the context below.

Context:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Question: {{ query }}

Answer:
"""

pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator())

# Connect components
pipeline.connect("embedder.embedding", "retriever.query_embedding")
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.prompt")

# Run RAG
result = pipeline.run({
    "embedder": {"text": "What is Haystack?"},
    "retriever": {"query": "What is Haystack?"},
    "prompt_builder": {"query": "What is Haystack?"}
})

print(result["llm"]["replies"][0])
```

### Using the REST API

Start the backend API:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Or use Docker:

```bash
cd docker
docker compose up backend
```

#### Index a Document

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Haystack is an end-to-end LLM framework.",
    "metadata": {"source": "docs"}
  }'
```

#### Search Documents

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Haystack?",
    "top_k": 10
  }'
```

#### Chat with RAG

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Haystack?",
    "top_k": 5
  }'
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection URL (default: `postgresql://postgres:postgres@localhost:54322/postgres`)
- `OPENAI_API_KEY`: OpenAI API key for embeddings and generation

### Hybrid Search Parameters

- `alpha`: Weight for semantic search (0.0 to 1.0). Default is 0.6.
  - Higher values favor semantic search
  - Lower values favor keyword search
  - `alpha=1.0`: Pure semantic search
  - `alpha=0.0`: Pure keyword search
- `top_k`: Number of documents to retrieve

## Database Schema

The Supabase document store uses the following schema:

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  embedding VECTOR(1536),
  tsv tsvector GENERATED ALWAYS AS (
    to_tsvector('english', unaccent(content))
  ) STORED,
  created_at TIMESTAMP DEFAULT now()
);
```

### Indexes

- **Vector Index**: IVFFlat index on `embedding` for fast similarity search
- **Full-Text Index**: GIN index on `tsv` for full-text search
- **Metadata Index**: GIN index on `metadata` for metadata queries

## Advantages

| Requirement | Status |
|------------|--------|
| Fully local | ✅ |
| Docker-only | ✅ |
| Hybrid search | ✅ |
| Scales later | ✅ |
| Supabase ecosystem | ✅ |
| Haystack-native | ✅ |

## Performance Tuning

### Vector Index

Adjust the `lists` parameter in the IVFFlat index based on your dataset size:

```sql
-- For larger datasets (100k+ documents)
CREATE INDEX idx_documents_embedding
  ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 1000);
```

### Full-Text Search

Configure PostgreSQL FTS for better performance:

```sql
-- Update text search configuration
ALTER TABLE documents
  ALTER COLUMN tsv SET STATISTICS 10000;

ANALYZE documents;
```

## Troubleshooting

### pgvector Extension Not Found

If you see an error about the `vector` extension:

```bash
# Connect to the database
psql -h localhost -p 54322 -U postgres -d postgres

# Create the extension
CREATE EXTENSION vector;
```

### Connection Issues

Check that the Supabase database is running:

```bash
docker ps | grep supabase-db
```

View logs:

```bash
docker logs supabase-db
```

### Performance Issues

- Ensure indexes are created (check with `\di` in psql)
- Run `ANALYZE documents;` to update query planner statistics
- Consider increasing `shared_buffers` in PostgreSQL configuration

## License

This integration is licensed under Apache-2.0, same as Haystack.
