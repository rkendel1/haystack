# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Example: Hybrid Search with SupabaseHybridRetriever

This script demonstrates how to use the SupabaseHybridRetriever component
to combine semantic and keyword search in a Haystack pipeline.
"""

import os

from haystack import Pipeline
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.retrievers.supabase import SupabaseHybridRetriever
from haystack.dataclasses import Document
from haystack.document_stores.supabase import SupabaseDocumentStore

# Set your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Database URL
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")


def setup_documents(document_store):
    """Populate the document store with sample documents."""
    print("Setting up sample documents...")

    documents = [
        Document(
            content=(
                "Haystack is an end-to-end framework for building LLM applications with retrieval-augmented generation."
            ),
            meta={"topic": "haystack", "type": "overview"},
        ),
        Document(
            content=("The SupabaseDocumentStore uses PostgreSQL with pgvector for efficient vector similarity search."),
            meta={"topic": "database", "type": "technical"},
        ),
        Document(
            content="Hybrid search combines the benefits of semantic understanding and exact keyword matching.",
            meta={"topic": "search", "type": "concept"},
        ),
        Document(
            content="RAG (Retrieval-Augmented Generation) improves LLM responses by providing relevant context.",
            meta={"topic": "rag", "type": "concept"},
        ),
        Document(
            content="FastAPI enables building high-performance REST APIs with automatic OpenAPI documentation.",
            meta={"topic": "api", "type": "framework"},
        ),
        Document(
            content="Docker Compose orchestrates multi-container applications with simple YAML configuration.",
            meta={"topic": "deployment", "type": "tools"},
        ),
    ]

    # Generate embeddings
    embedder = OpenAIDocumentEmbedder()
    docs_with_embeddings = embedder.run(documents)["documents"]

    # Write to store
    count = document_store.write_documents(docs_with_embeddings)
    print(f"✓ Wrote {count} documents to store\n")


def main():
    """Run the hybrid search example."""
    print("=" * 70)
    print("Hybrid Search Example with SupabaseHybridRetriever")
    print("=" * 70)

    # Initialize document store
    print("\n1. Initializing document store...")
    document_store = SupabaseDocumentStore(db_url=DB_URL)

    # Setup sample documents
    print("\n2. Populating document store...")
    setup_documents(document_store)

    # Create hybrid search pipeline
    print("3. Creating hybrid search pipeline...")
    pipeline = Pipeline()

    # Add components
    pipeline.add_component("text_embedder", OpenAITextEmbedder())
    pipeline.add_component(
        "retriever",
        SupabaseHybridRetriever(
            document_store=document_store,
            alpha=0.6,  # 60% semantic, 40% keyword
            top_k=5,
        ),
    )

    # Connect components
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

    print("✓ Pipeline created\n")

    # Example queries
    queries = [
        "Tell me about Haystack framework",
        "How does hybrid search work?",
        "What is RAG?",
        "PostgreSQL vector search",
    ]

    # Run queries
    print("4. Running hybrid searches...\n")

    for query in queries:
        print(f"Query: '{query}'")
        print("-" * 70)

        # Run pipeline
        result = pipeline.run({"text_embedder": {"text": query}, "retriever": {"query": query}})

        documents = result["retriever"]["documents"]

        if documents:
            print(f"Found {len(documents)} results:\n")
            for i, doc in enumerate(documents, 1):
                print(f"  {i}. Score: {doc.score:.4f}")
                print(f"     Content: {doc.content}")
                print(f"     Metadata: {doc.meta}")
                print()
        else:
            print("No results found.\n")

        print()

    # Demonstrate different alpha values
    print("5. Comparing different alpha values...\n")
    query = "vector database"
    print(f"Query: '{query}'")
    print("=" * 70)

    for alpha in [0.0, 0.3, 0.6, 1.0]:
        alpha_desc = (
            "pure keyword" if alpha == 0 else "pure semantic" if alpha == 1 else f"{int(alpha * 100)}% semantic"
        )
        print(f"\nAlpha = {alpha} ({alpha_desc})")
        print("-" * 70)

        # Create retriever with specific alpha
        retriever = SupabaseHybridRetriever(document_store=document_store, alpha=alpha, top_k=3)

        # Generate embedding
        text_embedder = OpenAITextEmbedder()
        embedding = text_embedder.run(query)["embedding"]

        # Run search
        result = retriever.run(query=query, query_embedding=embedding)
        documents = result["documents"]

        for i, doc in enumerate(documents, 1):
            print(f"  {i}. Score: {doc.score:.4f} - {doc.content[:60]}...")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
