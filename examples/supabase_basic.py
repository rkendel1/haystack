#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Example: Basic usage of SupabaseDocumentStore

This script demonstrates how to:
1. Connect to a Supabase document store
2. Write documents with embeddings
3. Perform semantic search
4. Perform keyword search
5. Use hybrid search
"""

import os
from haystack.dataclasses import Document
from haystack.document_stores.supabase import SupabaseDocumentStore
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder

# Set your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Database URL - change if using different credentials
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")


def main():
    print("=" * 60)
    print("Supabase Document Store Example")
    print("=" * 60)

    # Initialize document store
    print("\n1. Initializing SupabaseDocumentStore...")
    document_store = SupabaseDocumentStore(db_url=DB_URL)
    print(f"   Connected to database")

    # Create sample documents
    print("\n2. Creating sample documents...")
    documents = [
        Document(
            content="Haystack is an end-to-end LLM framework that allows you to build applications powered by LLMs.",
            meta={"source": "docs", "category": "introduction"},
        ),
        Document(
            content="pgvector is a PostgreSQL extension for vector similarity search.",
            meta={"source": "docs", "category": "database"},
        ),
        Document(
            content="Hybrid search combines semantic vector search with keyword-based full-text search.",
            meta={"source": "docs", "category": "search"},
        ),
        Document(
            content="FastAPI is a modern web framework for building APIs with Python.",
            meta={"source": "docs", "category": "api"},
        ),
    ]

    # Generate embeddings for documents
    print("   Generating embeddings...")
    embedder = OpenAIDocumentEmbedder()
    docs_with_embeddings = embedder.run(documents)["documents"]

    # Write documents to the store
    print("   Writing documents to store...")
    count = document_store.write_documents(docs_with_embeddings)
    print(f"   ✓ Wrote {count} documents")

    # Check document count
    print("\n3. Checking document count...")
    total = document_store.count_documents()
    print(f"   Total documents in store: {total}")

    # Perform semantic search
    print("\n4. Performing semantic search...")
    query = "What is Haystack?"
    print(f"   Query: '{query}'")

    # Generate query embedding
    text_embedder = OpenAITextEmbedder()
    query_embedding = text_embedder.run(query)["embedding"]

    # Search
    semantic_results = document_store.semantic_search(query_embedding, top_k=3)

    print("   Semantic search results:")
    for i, (doc_id, content, metadata, score) in enumerate(semantic_results, 1):
        print(f"   {i}. Score: {score:.3f}")
        print(f"      Content: {content[:80]}...")
        print(f"      Metadata: {metadata}")

    # Perform keyword search
    print("\n5. Performing keyword search...")
    keyword_query = "vector search"
    print(f"   Query: '{keyword_query}'")

    keyword_results = document_store.keyword_search(keyword_query, top_k=3)

    print("   Keyword search results:")
    for i, (doc_id, content, metadata, score) in enumerate(keyword_results, 1):
        print(f"   {i}. Score: {score:.3f}")
        print(f"      Content: {content[:80]}...")

    # Demonstrate filtering
    print("\n6. Searching with filters...")
    filter_dict = {"field": "meta.category", "operator": "==", "value": "introduction"}
    filtered_docs = document_store.filter_documents(filter_dict)
    print(f"   Documents with category='introduction': {len(filtered_docs)}")
    for doc in filtered_docs:
        print(f"   - {doc.content[:60]}...")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
