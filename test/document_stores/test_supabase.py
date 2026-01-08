# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import pytest

from haystack import Document
from backend.document_store.supabase_store import DuplicateDocumentError, DuplicatePolicy


# Skip all tests if sqlalchemy or psycopg2 not available
pytest.importorskip("sqlalchemy")
pytest.importorskip("psycopg2")


@pytest.fixture
def db_url():
    """Database URL for testing."""
    # This should be set to a test database
    # In CI/CD, you would set up a test PostgreSQL instance
    return "postgresql://postgres:postgres@localhost:54322/postgres"


@pytest.fixture
def document_store(db_url):
    """Create a SupabaseDocumentStore for testing."""
    from backend.document_store.supabase_store import SupabaseDocumentStore

    store = SupabaseDocumentStore(db_url=db_url)

    # Clean up any existing documents before each test
    try:
        with store.engine.begin() as conn:
            conn.execute(store._sqlalchemy_text("DELETE FROM documents"))
    except Exception:
        pass  # Table might not exist yet

    yield store

    # Cleanup after test
    try:
        with store.engine.begin() as conn:
            conn.execute(store._sqlalchemy_text("DELETE FROM documents"))
    except Exception:
        pass


class TestSupabaseDocumentStore:
    """Test SupabaseDocumentStore's features."""

    @pytest.mark.integration
    def test_to_dict(self, db_url):
        """Test serialization to dictionary."""
        from backend.document_store.supabase_store import SupabaseDocumentStore

        store = SupabaseDocumentStore(db_url=db_url)
        data = store.to_dict()

        assert data["type"] == "backend.document_store.supabase_store.SupabaseDocumentStore"
        assert data["init_parameters"]["db_url"] == db_url

    @pytest.mark.integration
    def test_from_dict(self, db_url):
        """Test deserialization from dictionary."""
        from backend.document_store.supabase_store import SupabaseDocumentStore

        data = {
            "type": "backend.document_store.supabase_store.SupabaseDocumentStore",
            "init_parameters": {"db_url": db_url},
        }

        store = SupabaseDocumentStore.from_dict(data)
        assert store.db_url == db_url

    @pytest.mark.integration
    def test_write_documents(self, document_store):
        """Test writing documents to the store."""
        docs = [
            Document(content="First document", meta={"category": "test"}),
            Document(content="Second document", meta={"category": "test"}),
        ]

        count = document_store.write_documents(docs)
        assert count == 2

        total = document_store.count_documents()
        assert total == 2

    @pytest.mark.integration
    def test_write_documents_with_embeddings(self, document_store):
        """Test writing documents with embeddings."""
        embedding = [0.1] * 1536  # OpenAI embedding size

        docs = [Document(content="Document with embedding", embedding=embedding)]

        count = document_store.write_documents(docs)
        assert count == 1

    @pytest.mark.integration
    def test_write_documents_duplicate_skip(self, document_store):
        """Test duplicate policy SKIP."""
        doc = Document(id="test-id", content="Test document")

        # Write first time
        count1 = document_store.write_documents([doc])
        assert count1 == 1

        # Write again with SKIP policy
        count2 = document_store.write_documents([doc], policy=DuplicatePolicy.SKIP)
        assert count2 == 0

        # Should still have only 1 document
        assert document_store.count_documents() == 1

    @pytest.mark.integration
    def test_write_documents_duplicate_overwrite(self, document_store):
        """Test duplicate policy OVERWRITE."""
        doc1 = Document(id="test-id", content="Original content")
        doc2 = Document(id="test-id", content="Updated content")

        # Write first time
        document_store.write_documents([doc1])

        # Overwrite
        count = document_store.write_documents([doc2], policy=DuplicatePolicy.OVERWRITE)
        assert count == 1

        # Should still have only 1 document
        assert document_store.count_documents() == 1

    @pytest.mark.integration
    def test_write_documents_duplicate_fail(self, document_store):
        """Test duplicate policy FAIL."""
        doc = Document(id="test-id", content="Test document")

        # Write first time
        document_store.write_documents([doc])

        # Try to write again with FAIL policy
        with pytest.raises(DuplicateDocumentError):
            document_store.write_documents([doc], policy=DuplicatePolicy.FAIL)

    @pytest.mark.integration
    def test_delete_documents(self, document_store):
        """Test deleting documents."""
        docs = [
            Document(id="doc1", content="First"),
            Document(id="doc2", content="Second"),
            Document(id="doc3", content="Third"),
        ]

        document_store.write_documents(docs)
        assert document_store.count_documents() == 3

        # Delete two documents
        document_store.delete_documents(["doc1", "doc2"])
        assert document_store.count_documents() == 1

    @pytest.mark.integration
    def test_filter_documents(self, document_store):
        """Test filtering documents by metadata."""
        docs = [
            Document(content="Doc 1", meta={"category": "A"}),
            Document(content="Doc 2", meta={"category": "B"}),
            Document(content="Doc 3", meta={"category": "A"}),
        ]

        document_store.write_documents(docs)

        # Filter by category A
        filters = {"field": "meta.category", "operator": "==", "value": "A"}
        filtered = document_store.filter_documents(filters)

        assert len(filtered) == 2

    @pytest.mark.integration
    def test_semantic_search(self, document_store):
        """Test semantic search with embeddings."""
        embedding = [0.1] * 1536

        docs = [
            Document(content="First document", embedding=embedding),
            Document(content="Second document", embedding=[0.2] * 1536),
        ]

        document_store.write_documents(docs)

        # Search with similar embedding
        results = document_store.semantic_search(embedding, top_k=1)

        assert len(results) == 1
        assert results[0][1] == "First document"  # content
        assert results[0][3] > 0.9  # high similarity score

    @pytest.mark.integration
    def test_keyword_search(self, document_store):
        """Test keyword search using full-text search."""
        docs = [
            Document(content="Haystack is a framework for building LLM applications"),
            Document(content="PostgreSQL is a powerful database system"),
            Document(content="Python is a programming language"),
        ]

        document_store.write_documents(docs)

        # Search for "framework"
        results = document_store.keyword_search("framework", top_k=2)

        assert len(results) >= 1
        assert "framework" in results[0][1].lower() or "haystack" in results[0][1].lower()

    @pytest.mark.integration
    def test_count_documents(self, document_store):
        """Test counting documents."""
        assert document_store.count_documents() == 0

        docs = [Document(content=f"Document {i}") for i in range(5)]
        document_store.write_documents(docs)

        assert document_store.count_documents() == 5
