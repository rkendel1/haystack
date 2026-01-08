# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
RAG Pipeline using Supabase Document Store.

This module demonstrates how to build a RAG pipeline using the SupabaseDocumentStore
and hybrid retrieval.
"""

import os
from typing import Optional

from backend.document_store.supabase_store import get_supabase_store
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.supabase import SupabaseHybridRetriever


def create_indexing_pipeline(db_url: Optional[str] = None) -> Pipeline:
    """
    Create a pipeline for indexing documents into Supabase.

    :param db_url: PostgreSQL connection URL.
    :returns: Haystack Pipeline for indexing.
    """
    document_store = get_supabase_store(db_url)

    pipeline = Pipeline()
    pipeline.add_component("embedder", OpenAIDocumentEmbedder())

    return pipeline, document_store


def create_rag_pipeline(db_url: Optional[str] = None) -> Pipeline:
    """
    Create a RAG pipeline using Supabase hybrid retrieval.

    :param db_url: PostgreSQL connection URL.
    :returns: Haystack Pipeline for RAG.
    """
    document_store = get_supabase_store(db_url)

    # Create pipeline
    pipeline = Pipeline()

    # Add components
    pipeline.add_component("text_embedder", OpenAITextEmbedder())
    pipeline.add_component("retriever", SupabaseHybridRetriever(document_store=document_store, top_k=5))

    # Prompt template for RAG
    template = """
    Answer the question based on the given context.

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
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    pipeline.connect("retriever.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder.prompt", "llm.prompt")

    return pipeline


def retrieve(query: str, db_url: Optional[str] = None):
    """
    Retrieve documents using hybrid search.

    :param query: The query string.
    :param db_url: PostgreSQL connection URL.
    :returns: Retrieved documents.
    """
    # Create embedder
    embedder = OpenAITextEmbedder()
    embedding_result = embedder.run(query)
    query_embedding = embedding_result["embedding"]

    # Get document store
    store = get_supabase_store(db_url)

    # Create retriever
    retriever = SupabaseHybridRetriever(document_store=store, top_k=10)

    # Run retrieval
    result = retriever.run(query=query, query_embedding=query_embedding)
    return result["documents"]


if __name__ == "__main__":
    # Example usage
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

    print("Creating RAG pipeline...")
    pipeline = create_rag_pipeline(db_url)

    print("Pipeline created successfully!")
    print(f"Components: {list(pipeline.graph.nodes.keys())}")
