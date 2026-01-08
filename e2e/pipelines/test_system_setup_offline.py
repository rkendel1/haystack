# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Offline end-to-end test that validates system setup without external API calls.

This test demonstrates that the Haystack system can be fully configured and 
set up without requiring internet connectivity or API keys.
"""

import json
import os

import pytest

from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore


def test_system_setup_offline(tmp_path):
    """
    Offline end-to-end test of Haystack system setup.
    
    This test validates the complete setup without requiring external API access:
    1. Document store initialization
    2. Document indexing
    3. Pipeline creation (retriever + prompt builder)
    4. Pipeline serialization/deserialization
    5. Retrieval execution
    """
    
    print("\n" + "="*70)
    print("OFFLINE END-TO-END SYSTEM TEST - NO API REQUIRED")
    print("="*70)
    
    # Step 1: Initialize document store
    document_store = InMemoryDocumentStore()
    assert document_store is not None
    print("\n✓ Step 1: Document store initialized")
    
    # Step 2: Index documents
    documents = [
        Document(content="Haystack is an end-to-end LLM framework that allows you to build applications powered by LLMs, Transformer models, vector search and more."),
        Document(content="Retrieval-Augmented Generation (RAG) is a technique that combines document retrieval with text generation using large language models."),
        Document(content="Vector databases store embeddings of documents to enable semantic search and similarity matching."),
        Document(content="OpenAI provides powerful language models like GPT-4 and GPT-3.5 that can be integrated into Haystack pipelines for text generation."),
        Document(content="Document stores in Haystack can be in-memory for testing or use external databases like Elasticsearch, Weaviate, or Pinecone for production."),
        Document(content="BM25 is a keyword-based search algorithm that ranks documents based on term frequency and inverse document frequency."),
    ]
    
    document_store.write_documents(documents)
    stored_docs = document_store.filter_documents()
    assert len(stored_docs) == len(documents)
    print(f"✓ Step 2: Indexed {len(documents)} documents successfully")
    print(f"  - Document IDs: {[doc.id[:8] for doc in stored_docs[:3]]}...")
    
    # Step 3: Create retrieval pipeline (without LLM)
    prompt_template = """
    You are a helpful AI assistant. Use the following documents to answer the question accurately.
    
    Documents:
    {% for doc in documents %}
    {{ loop.index }}. {{ doc.content }}
    {% endfor %}
    
    Question: {{ question }}
    
    Answer:
    """
    
    retrieval_pipeline = Pipeline()
    retrieval_pipeline.add_component(
        instance=InMemoryBM25Retriever(document_store=document_store, top_k=3),
        name="retriever"
    )
    retrieval_pipeline.add_component(
        instance=PromptBuilder(template=prompt_template),
        name="prompt_builder"
    )
    retrieval_pipeline.connect("retriever.documents", "prompt_builder.documents")
    
    print("✓ Step 3: Pipeline created with components:")
    print("  - BM25 Retriever (top_k=3)")
    print("  - Prompt Builder")
    
    # Step 4: Test pipeline serialization to YAML
    yaml_path = tmp_path / "offline_pipeline.yaml"
    with open(yaml_path, "w") as f:
        retrieval_pipeline.dump(f)
    assert yaml_path.exists()
    
    # Read and display a sample
    with open(yaml_path, "r") as f:
        yaml_content = f.read()
    print(f"\n✓ Step 4: Pipeline serialized to YAML ({len(yaml_content)} bytes)")
    print(f"  - File: {yaml_path}")
    
    # Step 5: Test pipeline serialization to JSON
    json_path = tmp_path / "offline_pipeline.json"
    with open(json_path, "w") as f:
        json.dump(retrieval_pipeline.to_dict(), f, indent=2)
    assert json_path.exists()
    
    with open(json_path, "r") as f:
        json_data = json.load(f)
    print(f"✓ Step 5: Pipeline serialized to JSON")
    print(f"  - Components: {list(json_data.get('components', {}).keys())}")
    
    # Step 6: Load pipeline from YAML
    with open(yaml_path, "r") as f:
        loaded_pipeline = Pipeline.load(f)
    assert loaded_pipeline is not None
    loaded_pipeline.get_component("retriever").document_store = document_store
    print("\n✓ Step 6: Pipeline loaded from YAML successfully")
    
    # Step 7: Load pipeline from JSON
    with open(json_path, "r") as f:
        loaded_pipeline_json = Pipeline.from_dict(json.load(f))
    assert loaded_pipeline_json is not None
    loaded_pipeline_json.get_component("retriever").document_store = document_store
    print("✓ Step 7: Pipeline loaded from JSON successfully")
    
    # Step 8: Run retrieval queries (no LLM needed)
    test_queries = [
        "What is Haystack?",
        "What is RAG?",
        "What is BM25?",
    ]
    
    print("\n" + "="*70)
    print("RUNNING RETRIEVAL QUERIES")
    print("="*70)
    
    for idx, question in enumerate(test_queries, 1):
        result = loaded_pipeline.run({
            "retriever": {"query": question},
            "prompt_builder": {"question": question}
        })
        
        # The pipeline returns the last component's output (prompt_builder)
        assert "prompt_builder" in result
        assert "prompt" in result["prompt_builder"]
        prompt = result["prompt_builder"]["prompt"]
        assert question in prompt
        
        # Get retrieval results by running retriever separately
        retriever = loaded_pipeline.get_component("retriever")
        retrieval_result = retriever.run(query=question)
        retrieved_docs = retrieval_result["documents"]
        assert len(retrieved_docs) > 0
        
        print(f"\n✓ Query {idx}: {question}")
        print(f"  - Retrieved {len(retrieved_docs)} documents")
        print(f"  - Top document: {retrieved_docs[0].content[:80]}...")
        print(f"  - BM25 score: {retrieved_docs[0].score:.4f}")
        print(f"  - Prompt generated: {len(prompt)} characters")
    
    print("\n" + "="*70)
    print("OFFLINE SYSTEM TEST PASSED!")
    print("="*70)
    print("\nSystem components validated:")
    print("  ✓ Document store initialization")
    print("  ✓ Document indexing (6 documents)")
    print("  ✓ BM25 retrieval pipeline creation")
    print("  ✓ Pipeline serialization (YAML & JSON)")
    print("  ✓ Pipeline deserialization (YAML & JSON)")
    print("  ✓ Retrieval execution (3 queries)")
    print("  ✓ Prompt generation")
    print("\nNote: This test runs completely offline without external API calls.")
    print("For full LLM integration testing, use test_full_system_e2e.py with")
    print("OPENAI_API_KEY environment variable set.")
    print("="*70)


def test_system_component_verification():
    """
    Verify all core Haystack components can be imported and instantiated.
    """
    print("\n" + "="*70)
    print("COMPONENT VERIFICATION TEST")
    print("="*70)
    
    # Test document store
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    doc_store = InMemoryDocumentStore()
    assert doc_store is not None
    print("✓ InMemoryDocumentStore can be instantiated")
    
    # Test retrievers
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
    retriever = InMemoryBM25Retriever(document_store=doc_store)
    assert retriever is not None
    print("✓ InMemoryBM25Retriever can be instantiated")
    
    # Test builders
    from haystack.components.builders.prompt_builder import PromptBuilder
    from haystack.components.builders.answer_builder import AnswerBuilder
    prompt_builder = PromptBuilder(template="Test: {{text}}")
    answer_builder = AnswerBuilder()
    assert prompt_builder is not None
    assert answer_builder is not None
    print("✓ PromptBuilder can be instantiated")
    print("✓ AnswerBuilder can be instantiated")
    
    # Test pipeline
    from haystack import Pipeline
    pipeline = Pipeline()
    assert pipeline is not None
    print("✓ Pipeline can be instantiated")
    
    # Test document
    from haystack import Document
    doc = Document(content="Test document")
    assert doc is not None
    assert doc.content == "Test document"
    print("✓ Document can be instantiated")
    
    print("\n✓ All core components verified successfully!")
    print("="*70)


if __name__ == "__main__":
    """
    Run tests directly without pytest for demonstration.
    """
    import tempfile
    import pathlib
    
    print("\n" + "="*70)
    print("RUNNING OFFLINE END-TO-END TESTS")
    print("="*70)
    
    # Run component verification
    test_system_component_verification()
    
    # Run offline system test
    with tempfile.TemporaryDirectory() as tmpdir:
        test_system_setup_offline(pathlib.Path(tmpdir))
    
    print("\n" + "="*70)
    print("ALL OFFLINE TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
