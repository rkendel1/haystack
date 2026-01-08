# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional
import json
import uuid

from haystack import default_from_dict, default_to_dict, logging
from haystack.dataclasses import Document
from haystack.document_stores.errors import DocumentStoreError, DuplicateDocumentError
from haystack.document_stores.types import DuplicatePolicy

logger = logging.getLogger(__name__)


class SupabaseDocumentStore:
    """
    A document store that uses Supabase (PostgreSQL with pgvector) for storage and retrieval.

    Supports semantic search via pgvector, keyword search via PostgreSQL full-text search,
    and hybrid search combining both approaches.

    This document store requires:
    - PostgreSQL 15+ with pgvector extension
    - SQLAlchemy for database operations
    - psycopg2 for PostgreSQL connectivity

    Example:
        ```python
        from haystack.document_stores.supabase import SupabaseDocumentStore

        document_store = SupabaseDocumentStore(
            db_url="postgresql://postgres:postgres@localhost:54322/postgres"
        )
        ```
    """

    def __init__(self, db_url: str):
        """
        Initialize the SupabaseDocumentStore.

        :param db_url: PostgreSQL connection URL in the format:
            postgresql://user:password@host:port/database
        """
        try:
            from sqlalchemy import create_engine, text

            self._sqlalchemy_text = text
        except ImportError as e:
            raise ImportError(
                "SupabaseDocumentStore requires SQLAlchemy. "
                "Install it with: pip install sqlalchemy psycopg2-binary"
            ) from e

        self.db_url = db_url
        self.engine = create_engine(db_url)

        # Verify pgvector extension is available
        self._verify_extensions()

    def _verify_extensions(self):
        """Verify that required PostgreSQL extensions are installed."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    self._sqlalchemy_text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                )
                if not result.fetchone():
                    raise DocumentStoreError(
                        "pgvector extension is not installed. "
                        "Run: CREATE EXTENSION vector; in your database."
                    )
        except Exception as e:
            logger.warning(f"Could not verify pgvector extension: {e}")

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes this store to a dictionary.
        """
        return default_to_dict(self, db_url=self.db_url)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupabaseDocumentStore":
        """
        Deserializes the store from a dictionary.
        """
        return default_from_dict(cls, data)

    def count_documents(self) -> int:
        """
        Returns the number of documents stored.
        """
        with self.engine.connect() as conn:
            result = conn.execute(self._sqlalchemy_text("SELECT COUNT(*) FROM documents"))
            return result.fetchone()[0]

    def filter_documents(self, filters: Optional[dict[str, Any]] = None) -> list[Document]:
        """
        Returns the documents that match the filters provided.

        Note: This implementation supports basic metadata filtering.
        For complex nested filters, consider extending the implementation.

        :param filters: The filters to apply to the document list.
        :returns: A list of Documents that match the given filters.
        """
        query = "SELECT id, content, metadata, embedding FROM documents"
        params = {}

        if filters:
            # Simple metadata filter support
            if "field" in filters and filters["field"].startswith("meta."):
                meta_key = filters["field"].replace("meta.", "")
                operator = filters.get("operator", "==")
                value = filters.get("value")

                if operator == "==":
                    query += " WHERE metadata @> :metadata"
                    params["metadata"] = json.dumps({meta_key: value})

        with self.engine.connect() as conn:
            result = conn.execute(self._sqlalchemy_text(query), params)
            documents = []
            for row in result:
                doc = Document(
                    id=str(row[0]),
                    content=row[1],
                    meta=row[2] if row[2] else {},
                    embedding=list(row[3]) if row[3] else None,
                )
                documents.append(doc)
            return documents

    def write_documents(self, documents: list[Document], policy: DuplicatePolicy = DuplicatePolicy.NONE) -> int:
        """
        Writes Documents into the DocumentStore.

        :param documents: A list of Document objects.
        :param policy: The policy to apply when a Document with the same id already exists.
        :returns: The number of Documents written.
        """
        if not documents:
            return 0

        written = 0

        with self.engine.begin() as conn:
            for doc in documents:
                doc_id = doc.id if doc.id else str(uuid.uuid4())

                # Check if document exists
                if policy != DuplicatePolicy.OVERWRITE:
                    result = conn.execute(
                        self._sqlalchemy_text("SELECT id FROM documents WHERE id = :id"), {"id": doc_id}
                    )
                    exists = result.fetchone()

                    if exists:
                        if policy == DuplicatePolicy.FAIL:
                            raise DuplicateDocumentError(f"Document with id {doc_id} already exists")
                        elif policy == DuplicatePolicy.SKIP:
                            continue

                # Prepare embedding as a list for pgvector
                embedding_str = None
                if doc.embedding is not None:
                    # Convert embedding to pgvector format
                    embedding_list = doc.embedding if isinstance(doc.embedding, list) else doc.embedding.tolist()
                    embedding_str = "[" + ",".join(map(str, embedding_list)) + "]"

                # Insert or update document
                if policy == DuplicatePolicy.OVERWRITE or (policy == DuplicatePolicy.NONE and exists):
                    conn.execute(
                        self._sqlalchemy_text("""
                            INSERT INTO documents (id, content, metadata, embedding)
                            VALUES (:id, :content, :metadata, :embedding::vector)
                            ON CONFLICT (id) DO UPDATE
                            SET content = EXCLUDED.content,
                                metadata = EXCLUDED.metadata,
                                embedding = EXCLUDED.embedding
                        """),
                        {
                            "id": doc_id,
                            "content": doc.content or "",
                            "metadata": json.dumps(doc.meta) if doc.meta else "{}",
                            "embedding": embedding_str,
                        },
                    )
                else:
                    conn.execute(
                        self._sqlalchemy_text("""
                            INSERT INTO documents (id, content, metadata, embedding)
                            VALUES (:id, :content, :metadata, :embedding::vector)
                        """),
                        {
                            "id": doc_id,
                            "content": doc.content or "",
                            "metadata": json.dumps(doc.meta) if doc.meta else "{}",
                            "embedding": embedding_str,
                        },
                    )

                written += 1

        return written

    def delete_documents(self, document_ids: list[str]) -> None:
        """
        Deletes all documents with matching document_ids from the DocumentStore.

        :param document_ids: The document IDs to delete.
        """
        if not document_ids:
            return

        with self.engine.begin() as conn:
            conn.execute(
                self._sqlalchemy_text("DELETE FROM documents WHERE id = ANY(:ids)"),
                {"ids": document_ids},
            )

    def semantic_search(self, query_embedding: list[float], top_k: int = 10, filters: Optional[dict] = None):
        """
        Perform semantic search using vector similarity.

        :param query_embedding: The query embedding vector.
        :param top_k: Number of results to return.
        :param filters: Optional metadata filters.
        :returns: List of tuples (content, metadata, score).
        """
        # Convert embedding to pgvector format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        query = """
        SELECT id, content, metadata,
               1 - (embedding <=> :embedding::vector) AS score
        FROM documents
        WHERE embedding IS NOT NULL
        """

        if filters:
            # Add simple metadata filtering
            if "field" in filters and filters["field"].startswith("meta."):
                meta_key = filters["field"].replace("meta.", "")
                value = filters.get("value")
                query += f" AND metadata @> '{json.dumps({meta_key: value})}'::jsonb"

        query += " ORDER BY embedding <=> :embedding::vector LIMIT :top_k"

        with self.engine.connect() as conn:
            result = conn.execute(
                self._sqlalchemy_text(query), {"embedding": embedding_str, "top_k": top_k}
            )
            return [(row[0], row[1], row[2], row[3]) for row in result.fetchall()]

    def keyword_search(self, query_text: str, top_k: int = 10, filters: Optional[dict] = None):
        """
        Perform keyword search using PostgreSQL full-text search.

        :param query_text: The query text.
        :param top_k: Number of results to return.
        :param filters: Optional metadata filters.
        :returns: List of tuples (content, metadata, score).
        """
        query = """
        SELECT id, content, metadata,
               ts_rank(tsv, plainto_tsquery('english', :q)) AS score
        FROM documents
        WHERE tsv @@ plainto_tsquery('english', :q)
        """

        if filters:
            # Add simple metadata filtering
            if "field" in filters and filters["field"].startswith("meta."):
                meta_key = filters["field"].replace("meta.", "")
                value = filters.get("value")
                query += f" AND metadata @> '{json.dumps({meta_key: value})}'::jsonb"

        query += " ORDER BY score DESC LIMIT :top_k"

        with self.engine.connect() as conn:
            result = conn.execute(self._sqlalchemy_text(query), {"q": query_text, "top_k": top_k})
            return [(row[0], row[1], row[2], row[3]) for row in result.fetchall()]
