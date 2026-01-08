# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import pytest

from haystack import Document

# Skip all tests if sqlalchemy or psycopg2 not available
pytest.importorskip("sqlalchemy")
pytest.importorskip("psycopg2")


@pytest.fixture
def db_url():
    """Database URL for testing."""
    return "postgresql://postgres:postgres@localhost:54322/postgres"


@pytest.fixture
def document_store(db_url):
    """Create a SupabaseDocumentStore for testing."""
    from haystack.document_stores.supabase import SupabaseDocumentStore

    store = SupabaseDocumentStore(db_url=db_url)

    # Clean up any existing documents
    try:
        with store.engine.begin() as conn:
            conn.execute(store._sqlalchemy_text("DELETE FROM documents"))
    except Exception:
        pass

    yield store

    # Cleanup after test
    try:
        with store.engine.begin() as conn:
            conn.execute(store._sqlalchemy_text("DELETE FROM documents"))
    except Exception:
        pass


class TestSupabaseHybridRetriever:
    """Test SupabaseHybridRetriever component."""

    @pytest.mark.integration
    def test_init(self, document_store):
        """Test retriever initialization."""
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever

        retriever = SupabaseHybridRetriever(document_store=document_store, alpha=0.6, top_k=10)

        assert retriever.document_store == document_store
        assert retriever.alpha == 0.6
        assert retriever.top_k == 10

    @pytest.mark.integration
    def test_hybrid_search(self, document_store):
        """Test hybrid search retrieval."""
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever

        # Create documents with embeddings
        embedding1 = [0.1] * 1536
        embedding2 = [0.2] * 1536

        docs = [
            Document(content="Haystack is an LLM framework", embedding=embedding1, meta={"topic": "haystack"}),
            Document(
                content="PostgreSQL with pgvector for vector search", embedding=embedding2, meta={"topic": "database"}
            ),
        ]

        document_store.write_documents(docs)

        # Create retriever
        retriever = SupabaseHybridRetriever(document_store=document_store, alpha=0.6, top_k=2)

        # Run search
        result = retriever.run(query="Haystack framework", query_embedding=embedding1)

        # Check results
        assert "documents" in result
        documents = result["documents"]
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        assert all(hasattr(doc, "score") for doc in documents)

    @pytest.mark.integration
    def test_different_alpha_values(self, document_store):
        """Test retrieval with different alpha values."""
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever

        embedding = [0.1] * 1536

        docs = [
            Document(content="Vector search with embeddings", embedding=embedding),
            Document(content="Keyword based full text search", embedding=[0.5] * 1536),
        ]

        document_store.write_documents(docs)

        # Test with pure semantic search (alpha=1.0)
        retriever_semantic = SupabaseHybridRetriever(document_store=document_store, alpha=1.0, top_k=2)
        result_semantic = retriever_semantic.run(query="keyword", query_embedding=embedding)

        # Test with pure keyword search (alpha=0.0)
        retriever_keyword = SupabaseHybridRetriever(document_store=document_store, alpha=0.0, top_k=2)
        result_keyword = retriever_keyword.run(query="keyword", query_embedding=embedding)

        # Both should return results
        assert len(result_semantic["documents"]) > 0
        assert len(result_keyword["documents"]) > 0

    @pytest.mark.integration
    def test_top_k_parameter(self, document_store):
        """Test top_k parameter limits results."""
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever

        embedding = [0.1] * 1536

        # Create more documents than top_k
        docs = [Document(content=f"Document {i}", embedding=[float(i) / 100] * 1536) for i in range(10)]

        document_store.write_documents(docs)

        # Test with top_k=3
        retriever = SupabaseHybridRetriever(document_store=document_store, alpha=0.6, top_k=3)
        result = retriever.run(query="Document", query_embedding=embedding)

        assert len(result["documents"]) <= 3

    @pytest.mark.integration
    def test_empty_results(self, document_store):
        """Test retrieval with no matching documents."""
        from haystack.components.retrievers.supabase import SupabaseHybridRetriever

        embedding = [0.1] * 1536

        # Create retriever with empty store
        retriever = SupabaseHybridRetriever(document_store=document_store, alpha=0.6, top_k=10)

        # Search in empty store
        result = retriever.run(query="test query", query_embedding=embedding)

        assert "documents" in result
        assert len(result["documents"]) == 0
