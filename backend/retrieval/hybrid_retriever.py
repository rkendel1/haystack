# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Hybrid retrieval logic combining semantic and keyword search.

This module provides functions for hybrid search using the SupabaseDocumentStore.
"""

from typing import Optional


def hybrid_search(
    store,
    query_text: str,
    query_embedding: list[float],
    top_k: int = 10,
    alpha: float = 0.6,
    filters: Optional[dict] = None,
):
    """
    Perform hybrid search combining semantic and keyword retrieval.

    :param store: SupabaseDocumentStore instance.
    :param query_text: The query text for keyword search.
    :param query_embedding: The query embedding vector for semantic search.
    :param top_k: Number of results to return.
    :param alpha: Weight for semantic search (0.0 to 1.0).
        Keyword search weight will be (1 - alpha).
    :param filters: Optional metadata filters.
    :returns: List of tuples (doc_id, content, metadata, combined_score).
    """
    # Perform semantic search
    semantic_results = store.semantic_search(query_embedding, top_k=top_k, filters=filters)

    # Perform keyword search
    keyword_results = store.keyword_search(query_text, top_k=top_k, filters=filters)

    # Combine scores using weighted fusion
    scores = {}
    metadata_map = {}
    content_map = {}

    # Add semantic search scores
    for doc_id, content, metadata, score in semantic_results:
        scores[doc_id] = alpha * score
        metadata_map[doc_id] = metadata
        content_map[doc_id] = content

    # Add keyword search scores
    for doc_id, content, metadata, score in keyword_results:
        scores[doc_id] = scores.get(doc_id, 0) + (1 - alpha) * score
        if doc_id not in metadata_map:
            metadata_map[doc_id] = metadata
            content_map[doc_id] = content

    # Sort by combined score and return top_k
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return [(doc_id, content_map[doc_id], metadata_map[doc_id], score) for doc_id, score in ranked]
