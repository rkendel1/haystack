# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional

from haystack import component, logging
from haystack.dataclasses import Document

logger = logging.getLogger(__name__)


@component
class SupabaseHybridRetriever:
    """
    A retriever that combines semantic (vector) and keyword (full-text) search using Supabase.

    This component performs hybrid search by:
    1. Running semantic search using vector embeddings
    2. Running keyword search using PostgreSQL full-text search
    3. Combining results using weighted score fusion

    Example:
        ```python
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever
        from haystack.document_stores.supabase import SupabaseDocumentStore

        document_store = SupabaseDocumentStore(
            db_url="postgresql://postgres:postgres@localhost:54322/postgres"
        )

        retriever = SupabaseHybridRetriever(
            document_store=document_store,
            alpha=0.6,  # Weight for semantic search (0.4 for keyword)
            top_k=10
        )

        # Use in a pipeline with an embedder
        results = retriever.run(
            query="What is Haystack?",
            query_embedding=[0.1, 0.2, ...]  # From an embedder component
        )
        ```
    """

    def __init__(
        self,
        document_store,
        alpha: float = 0.6,
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the SupabaseHybridRetriever.

        :param document_store: An instance of SupabaseDocumentStore.
        :param alpha: Weight for semantic search score (0.0 to 1.0).
            The keyword search weight will be (1 - alpha).
            Default is 0.6 (60% semantic, 40% keyword).
        :param top_k: Maximum number of documents to retrieve.
        :param filters: Optional filters to apply to the search.
        """
        self.document_store = document_store
        self.alpha = alpha
        self.top_k = top_k
        self.filters = filters

    @component.output_types(documents=list[Document])
    def run(
        self,
        query: str,
        query_embedding: list[float],
        top_k: Optional[int] = None,
        filters: Optional[dict[str, Any]] = None,
    ):
        """
        Run hybrid search combining semantic and keyword retrieval.

        :param query: The query string for keyword search.
        :param query_embedding: The query embedding vector for semantic search.
        :param top_k: Override the default top_k value.
        :param filters: Override the default filters.
        :returns: Dictionary with 'documents' key containing retrieved documents.
        """
        top_k = top_k or self.top_k
        filters = filters or self.filters

        # Perform semantic search
        semantic_results = self.document_store.semantic_search(query_embedding, top_k=top_k, filters=filters)

        # Perform keyword search
        keyword_results = self.document_store.keyword_search(query, top_k=top_k, filters=filters)

        # Combine scores using weighted fusion
        scores = {}
        metadata_map = {}
        content_map = {}

        # Add semantic search scores
        for doc_id, content, metadata, score in semantic_results:
            scores[doc_id] = self.alpha * score
            metadata_map[doc_id] = metadata
            content_map[doc_id] = content

        # Add keyword search scores
        for doc_id, content, metadata, score in keyword_results:
            scores[doc_id] = scores.get(doc_id, 0) + (1 - self.alpha) * score
            if doc_id not in metadata_map:
                metadata_map[doc_id] = metadata
                content_map[doc_id] = content

        # Sort by combined score
        ranked_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Create Document objects
        documents = []
        for doc_id, score in ranked_ids:
            doc = Document(
                id=doc_id,
                content=content_map[doc_id],
                meta=metadata_map[doc_id] if metadata_map[doc_id] else {},
                score=score,
            )
            documents.append(doc)

        return {"documents": documents}
