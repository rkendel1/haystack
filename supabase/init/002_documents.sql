-- SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
--
-- SPDX-License-Identifier: Apache-2.0

-- Create documents table with support for vector and full-text search

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',

  -- Vector embedding for semantic search (1536 dimensions for OpenAI embeddings)
  embedding VECTOR(1536),

  -- Full-text search vector (automatically generated from content)
  tsv tsvector GENERATED ALWAYS AS (
    to_tsvector('english', unaccent(content))
  ) STORED,

  created_at TIMESTAMP DEFAULT now()
);

-- Create indexes for efficient search

-- IVFFlat index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding
  ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_documents_tsv
  ON documents USING GIN (tsv);

-- GIN index for metadata queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata
  ON documents USING GIN (metadata);
