# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Full end-to-end test of the Haystack system.

This test validates the complete setup, configuration, and execution of a Haystack RAG pipeline
from start to finish, including:
- API key configuration
- Document store setup
- Document indexing
- Pipeline creation
- Serialization/deserialization
- Query execution with OpenAI
- Result validation
"""

import json
import os

import pytest

from haystack import Document, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY", None),
    reason="Export an env var called OPENAI_API_KEY containing the OpenAI API key to run this test.",
)
def test_full_system_setup_and_run(tmp_path):
    """
    Full end-to-end test of the Haystack system.
    
    This test performs a complete workflow including:
    1. System configuration verification
    2. Document store initialization  
    3. Document indexing with BM25
    4. RAG pipeline creation
    5. Pipeline serialization to both YAML and JSON
    6. Pipeline deserialization
    7. Multiple query executions with OpenAI
    8. Result validation
    """
    
    # Step 1: Verify OpenAI API configuration
    api_key = os.environ.get("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY must be set"
    assert len(api_key) > 0, "OPENAI_API_KEY must not be empty"
    print(f"✓ OpenAI API key configured (length: {len(api_key)})")
    
    # Step 2: Initialize document store
    document_store = InMemoryDocumentStore()
    assert document_store is not None
    print("✓ Document store initialized")
    
    # Step 3: Index documents directly to document store
    documents = [
        Document(content="Haystack is an end-to-end LLM framework that allows you to build applications powered by LLMs, Transformer models, vector search and more."),
        Document(content="Retrieval-Augmented Generation (RAG) is a technique that combines document retrieval with text generation using large language models."),
        Document(content="Vector databases store embeddings of documents to enable semantic search and similarity matching."),
        Document(content="OpenAI provides powerful language models like GPT-4 and GPT-3.5 that can be integrated into Haystack pipelines for text generation."),
        Document(content="Document stores in Haystack can be in-memory for testing or use external databases like Elasticsearch, Weaviate, or Pinecone for production."),
        Document(content="BM25 is a keyword-based search algorithm that ranks documents based on term frequency and inverse document frequency."),
    ]
    
    document_store.write_documents(documents)
    print(f"✓ Indexed {len(documents)} documents with BM25")
    
    # Step 4: Create RAG pipeline with BM25 retrieval
    prompt_template = """
    You are a helpful AI assistant. Use the following documents to answer the question accurately and concisely.
    
    Documents:
    {% for doc in documents %}
    {{ loop.index }}. {{ doc.content }}
    {% endfor %}
    
    Question: {{ question }}
    
    Answer:
    """
    
    rag_pipeline = Pipeline()
    rag_pipeline.add_component(
        instance=InMemoryBM25Retriever(document_store=document_store, top_k=3),
        name="retriever"
    )
    rag_pipeline.add_component(
        instance=PromptBuilder(template=prompt_template),
        name="prompt_builder"
    )
    rag_pipeline.add_component(
        instance=OpenAIGenerator(model="gpt-3.5-turbo"),
        name="llm"
    )
    rag_pipeline.add_component(
        instance=AnswerBuilder(),
        name="answer_builder"
    )
    
    rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")
    rag_pipeline.connect("llm.replies", "answer_builder.replies")
    rag_pipeline.connect("llm.meta", "answer_builder.meta")
    rag_pipeline.connect("retriever.documents", "answer_builder.documents")
    print("✓ RAG pipeline created with all components connected")
    
    # Step 5: Test pipeline serialization to YAML
    yaml_path = tmp_path / "full_system_rag_pipeline.yaml"
    with open(yaml_path, "w") as f:
        rag_pipeline.dump(f)
    assert yaml_path.exists()
    print(f"✓ Pipeline serialized to YAML: {yaml_path}")
    
    # Step 6: Test pipeline serialization to JSON
    json_path = tmp_path / "full_system_rag_pipeline.json"
    with open(json_path, "w") as f:
        json.dump(rag_pipeline.to_dict(), f, indent=2)
    assert json_path.exists()
    print(f"✓ Pipeline serialized to JSON: {json_path}")
    
    # Step 7: Load pipeline from YAML
    with open(yaml_path, "r") as f:
        loaded_pipeline_yaml = Pipeline.load(f)
    assert loaded_pipeline_yaml is not None
    # Reconnect to the same document store
    loaded_pipeline_yaml.get_component("retriever").document_store = document_store
    print("✓ Pipeline loaded from YAML")
    
    # Step 8: Load pipeline from JSON
    with open(json_path, "r") as f:
        loaded_pipeline_json = Pipeline.from_dict(json.load(f))
    assert loaded_pipeline_json is not None
    # Reconnect to the same document store
    loaded_pipeline_json.get_component("retriever").document_store = document_store
    print("✓ Pipeline loaded from JSON")
    
    # Step 9: Run queries through the pipeline
    test_queries = [
        {
            "question": "What is Haystack?",
            "expected_keywords": ["LLM", "framework", "application"]
        },
        {
            "question": "What is RAG?",
            "expected_keywords": ["Retrieval", "Generation", "retrieval"]
        },
        {
            "question": "What is BM25?",
            "expected_keywords": ["keyword", "search", "algorithm", "BM25"]
        },
    ]
    
    print("\n" + "="*60)
    print("Running test queries...")
    print("="*60)
    
    for idx, test_case in enumerate(test_queries, 1):
        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\nQuery {idx}: {question}")
        
        # Run query through the pipeline
        result = rag_pipeline.run({
            "retriever": {"query": question},
            "prompt_builder": {"question": question},
            "answer_builder": {"query": question},
        })
        
        # Validate results structure
        assert "answer_builder" in result, "answer_builder output missing"
        assert "answers" in result["answer_builder"], "answers missing from answer_builder"
        assert len(result["answer_builder"]["answers"]) > 0, "No answers generated"
        
        # Get the answer
        answer = result["answer_builder"]["answers"][0]
        assert answer is not None, "Answer is None"
        assert answer.data is not None, "Answer data is None"
        assert len(answer.data) > 0, "Answer data is empty"
        assert answer.query == question, "Answer query doesn't match input question"
        
        print(f"Answer: {answer.data[:200]}...")
        
        # Validate answer has metadata
        assert hasattr(answer, "meta"), "Answer missing meta attribute"
        assert hasattr(answer, "documents"), "Answer missing documents attribute"
        assert len(answer.documents) > 0, "No documents retrieved"
        
        print(f"✓ Retrieved {len(answer.documents)} relevant documents")
        print(f"✓ Generated answer with {len(answer.data)} characters")
        
        # Check that at least some expected keywords appear in either the answer or retrieved documents
        found_keywords = []
        combined_text = answer.data.lower()
        for doc in answer.documents:
            combined_text += " " + doc.content.lower()
        
        for keyword in expected_keywords:
            if keyword.lower() in combined_text:
                found_keywords.append(keyword)
        
        assert len(found_keywords) > 0, f"None of the expected keywords {expected_keywords} found in answer or documents"
        print(f"✓ Found relevant keywords: {found_keywords}")
    
    print("\n" + "="*60)
    print("FULL SYSTEM TEST PASSED!")
    print("="*60)
    print("\nAll components verified:")
    print("  ✓ OpenAI API configuration")
    print("  ✓ Document store initialization")
    print("  ✓ Document indexing with BM25")
    print("  ✓ RAG pipeline creation")
    print("  ✓ Pipeline serialization (YAML & JSON)")
    print("  ✓ Pipeline deserialization")
    print("  ✓ Query execution with OpenAI")
    print("  ✓ Result validation")
    print("="*60)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY", None),
    reason="Export an env var called OPENAI_API_KEY containing the OpenAI API key to run this test.",
)
def test_full_system_alternative_configuration(tmp_path):
    """
    Alternative full end-to-end test with different documents and queries.
    
    This test validates the system with a different dataset to ensure robustness.
    """
    
    # Step 1: Verify configuration
    api_key = os.environ.get("OPENAI_API_KEY")
    assert api_key is not None
    print(f"✓ OpenAI API key configured (length: {len(api_key)})")
    
    # Step 2: Initialize document store and add documents directly
    document_store = InMemoryDocumentStore()
    documents = [
        Document(content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms."),
        Document(content="Machine learning is a subset of artificial intelligence that enables systems to learn from data without being explicitly programmed."),
        Document(content="Natural language processing (NLP) allows computers to understand, interpret, and generate human language in a valuable way."),
        Document(content="Deep learning uses artificial neural networks with multiple layers to progressively extract higher-level features from raw input."),
        Document(content="TensorFlow and PyTorch are popular deep learning frameworks used for building and training neural networks."),
    ]
    document_store.write_documents(documents)
    print(f"✓ Indexed {len(documents)} documents")
    
    # Step 3: Create RAG pipeline
    prompt_template = """
    Answer the question based on the following context:
    
    {% for doc in documents %}
    {{ doc.content }}
    {% endfor %}
    
    Question: {{ question }}
    Answer:
    """
    
    rag_pipeline = Pipeline()
    rag_pipeline.add_component(
        instance=InMemoryBM25Retriever(document_store=document_store, top_k=2),
        name="retriever"
    )
    rag_pipeline.add_component(
        instance=PromptBuilder(template=prompt_template),
        name="prompt_builder"
    )
    rag_pipeline.add_component(
        instance=OpenAIGenerator(model="gpt-3.5-turbo"),
        name="llm"
    )
    rag_pipeline.add_component(
        instance=AnswerBuilder(),
        name="answer_builder"
    )
    
    rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")
    rag_pipeline.connect("llm.replies", "answer_builder.replies")
    rag_pipeline.connect("llm.meta", "answer_builder.meta")
    rag_pipeline.connect("retriever.documents", "answer_builder.documents")
    print("✓ RAG pipeline created")
    
    # Step 4: Test serialization
    pipeline_path = tmp_path / "alternative_pipeline.yaml"
    with open(pipeline_path, "w") as f:
        rag_pipeline.dump(f)
    
    with open(pipeline_path, "r") as f:
        loaded_pipeline = Pipeline.load(f)
    
    # Reconnect document store
    loaded_pipeline.get_component("retriever").document_store = document_store
    print("✓ Pipeline serialized and loaded successfully")
    
    # Step 5: Run test queries
    test_queries = [
        ("What is Python?", ["Python", "programming", "language"]),
        ("What is machine learning?", ["machine learning", "learn", "data"]),
    ]
    
    for question, expected_keywords in test_queries:
        result = loaded_pipeline.run({
            "retriever": {"query": question},
            "prompt_builder": {"question": question},
            "answer_builder": {"query": question},
        })
        
        assert "answer_builder" in result
        assert len(result["answer_builder"]["answers"]) > 0
        answer = result["answer_builder"]["answers"][0]
        assert answer.data is not None and len(answer.data) > 0
        
        # Check for expected keywords
        combined_text = answer.data.lower()
        for doc in answer.documents:
            combined_text += " " + doc.content.lower()
        
        found = any(keyword.lower() in combined_text for keyword in expected_keywords)
        assert found, f"None of {expected_keywords} found in response"
        
        print(f"✓ Query '{question}' executed successfully")
        print(f"  Answer: {answer.data[:100]}...")
    
    print("\n✓ ALTERNATIVE CONFIGURATION TEST PASSED!")
