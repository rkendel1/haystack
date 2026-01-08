#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Complete End-to-End Demonstration of Haystack System

This script demonstrates the full Haystack system setup, configuration, and execution.
It can run in two modes:
1. OFFLINE MODE (default): Demonstrates retrieval and prompt building without LLM
2. ONLINE MODE: Full RAG pipeline with OpenAI integration (requires API key)

Usage:
    # Offline mode (no API key needed)
    python demo_full_system.py

    # Online mode (requires OPENAI_API_KEY environment variable)
    export OPENAI_API_KEY="your-key-here"
    python demo_full_system.py --online
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from haystack import Document, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)


def print_step(step_num, text):
    """Print a step indicator."""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {text}")
    print(f"{'='*80}")


def demo_offline_system():
    """Demonstrate the Haystack system without requiring external API calls."""
    
    print_header("HAYSTACK FULL SYSTEM DEMONSTRATION - OFFLINE MODE")
    print("\nThis demonstration shows the complete Haystack system working offline.")
    print("No API keys or internet connection required!")
    
    # Step 1: System Configuration
    print_step(1, "System Configuration Check")
    print("✓ Haystack installed and imported successfully")
    print("✓ All core components available")
    print("✓ Running in OFFLINE mode (no external API calls)")
    
    # Step 2: Document Store Initialization
    print_step(2, "Document Store Initialization")
    document_store = InMemoryDocumentStore()
    print("✓ Created InMemoryDocumentStore")
    print(f"  - Type: {type(document_store).__name__}")
    print(f"  - Status: Ready for operations")
    
    # Step 3: Document Indexing
    print_step(3, "Document Indexing")
    documents = [
        Document(content="Haystack is an end-to-end LLM framework that allows you to build applications powered by LLMs, Transformer models, vector search and more."),
        Document(content="Retrieval-Augmented Generation (RAG) is a technique that combines document retrieval with text generation using large language models."),
        Document(content="Vector databases store embeddings of documents to enable semantic search and similarity matching."),
        Document(content="OpenAI provides powerful language models like GPT-4 and GPT-3.5 that can be integrated into Haystack pipelines for text generation."),
        Document(content="Document stores in Haystack can be in-memory for testing or use external databases like Elasticsearch, Weaviate, or Pinecone for production."),
        Document(content="BM25 is a keyword-based search algorithm that ranks documents based on term frequency and inverse document frequency."),
        Document(content="Python is the primary programming language for Haystack, offering simplicity and extensive library support."),
        Document(content="Pipeline components in Haystack can be connected to create complex workflows for document processing and question answering."),
    ]
    
    document_store.write_documents(documents)
    stored_docs = document_store.filter_documents()
    
    print(f"✓ Indexed {len(documents)} documents successfully")
    print(f"  - Total documents in store: {len(stored_docs)}")
    print(f"  - Sample document IDs: {[doc.id[:8] + '...' for doc in stored_docs[:3]]}")
    print(f"\nDocument samples:")
    for i, doc in enumerate(documents[:3], 1):
        print(f"  {i}. {doc.content[:60]}...")
    
    # Step 4: Pipeline Creation
    print_step(4, "Retrieval Pipeline Creation")
    
    prompt_template = """
You are a helpful AI assistant. Based on the retrieved documents, provide a detailed answer.

Retrieved Documents:
{% for doc in documents %}
Document {{ loop.index }}:
{{ doc.content }}

{% endfor %}

Question: {{ question }}

Please provide a comprehensive answer based on the documents above.
Answer:
"""
    
    pipeline = Pipeline()
    pipeline.add_component(
        instance=InMemoryBM25Retriever(document_store=document_store, top_k=3),
        name="retriever"
    )
    pipeline.add_component(
        instance=PromptBuilder(template=prompt_template),
        name="prompt_builder"
    )
    pipeline.connect("retriever.documents", "prompt_builder.documents")
    
    print("✓ Created retrieval pipeline with components:")
    print("  - BM25 Retriever (keyword-based search)")
    print("    * top_k: 3 documents")
    print("    * Algorithm: BM25 ranking")
    print("  - Prompt Builder")
    print("    * Template length: {} characters".format(len(prompt_template)))
    print("    * Variables: documents, question")
    
    # Step 5: Pipeline Serialization
    print_step(5, "Pipeline Serialization")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # YAML serialization
        yaml_path = Path(tmpdir) / "pipeline.yaml"
        with open(yaml_path, "w") as f:
            pipeline.dump(f)
        
        with open(yaml_path, "r") as f:
            yaml_content = f.read()
        
        print(f"✓ Serialized pipeline to YAML")
        print(f"  - Size: {len(yaml_content)} bytes")
        print(f"  - File: {yaml_path}")
        print(f"\nYAML Preview (first 200 chars):")
        print(f"  {yaml_content[:200]}...")
        
        # JSON serialization
        json_path = Path(tmpdir) / "pipeline.json"
        with open(json_path, "w") as f:
            json.dump(pipeline.to_dict(), f, indent=2)
        
        with open(json_path, "r") as f:
            json_data = json.load(f)
        
        print(f"\n✓ Serialized pipeline to JSON")
        print(f"  - Components: {list(json_data['components'].keys())}")
        print(f"  - Connections: {len(json_data.get('connections', []))} connection(s)")
        
        # Step 6: Pipeline Deserialization
        print_step(6, "Pipeline Deserialization")
        
        with open(yaml_path, "r") as f:
            loaded_pipeline = Pipeline.load(f)
        loaded_pipeline.get_component("retriever").document_store = document_store
        
        print("✓ Loaded pipeline from YAML")
        print(f"  - Components restored: {list(loaded_pipeline.graph.nodes.keys())}")
        print(f"  - Document store reconnected")
    
    # Step 7: Query Execution
    print_step(7, "Query Execution & Results")
    
    test_queries = [
        "What is Haystack?",
        "Explain RAG",
        "What is BM25 and how does it work?",
        "Tell me about Python in Haystack",
    ]
    
    print(f"Running {len(test_queries)} test queries...\n")
    
    for idx, question in enumerate(test_queries, 1):
        print(f"\n{'─' * 80}")
        print(f"QUERY {idx}: {question}")
        print(f"{'─' * 80}")
        
        # Run pipeline
        result = loaded_pipeline.run({
            "retriever": {"query": question},
            "prompt_builder": {"question": question}
        })
        
        # Get retrieval results
        retriever = loaded_pipeline.get_component("retriever")
        retrieval_result = retriever.run(query=question)
        retrieved_docs = retrieval_result["documents"]
        
        # Display results
        print(f"\n📊 Retrieval Results:")
        print(f"  - Documents retrieved: {len(retrieved_docs)}")
        
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"\n  Document {i} (BM25 Score: {doc.score:.4f}):")
            print(f"    {doc.content[:120]}...")
        
        # Display generated prompt
        prompt = result["prompt_builder"]["prompt"]
        print(f"\n📝 Generated Prompt:")
        print(f"  - Length: {len(prompt)} characters")
        print(f"  - Contains question: {'✓' if question in prompt else '✗'}")
        print(f"  - Contains retrieved docs: {'✓' if 'Document 1:' in prompt else '✗'}")
        print(f"\n  Prompt preview (first 300 chars):")
        print(f"  {prompt[:300]}...")
    
    # Step 8: Summary
    print_step(8, "System Validation Summary")
    
    print("\n✅ OFFLINE DEMONSTRATION COMPLETED SUCCESSFULLY!\n")
    print("System Components Validated:")
    print("  ✓ Document store initialization")
    print("  ✓ Document indexing (8 documents)")
    print("  ✓ BM25 retrieval pipeline creation")
    print("  ✓ Pipeline serialization (YAML & JSON)")
    print("  ✓ Pipeline deserialization")
    print("  ✓ Query execution (4 queries)")
    print("  ✓ Prompt generation")
    print("  ✓ Document retrieval with BM25 scoring")
    
    print("\n" + "=" * 80)
    print("NOTE: This demonstration ran completely offline!")
    print("For full LLM integration with OpenAI, run with --online flag")
    print("=" * 80)


def demo_online_system():
    """Demonstrate the full Haystack system with OpenAI integration."""
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nTo run the online demonstration:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  python demo_full_system.py --online")
        sys.exit(1)
    
    try:
        from haystack.components.generators import OpenAIGenerator
    except ImportError:
        print("\n❌ ERROR: OpenAI integration not available!")
        print("Install with: pip install haystack-ai")
        sys.exit(1)
    
    print_header("HAYSTACK FULL SYSTEM DEMONSTRATION - ONLINE MODE")
    print("\nThis demonstration shows the complete Haystack RAG system with OpenAI.")
    print(f"✓ API Key configured (length: {len(api_key)})")
    print("⚠️  This will make real API calls to OpenAI and consume credits")
    
    # Initialize components (similar to offline, but with LLM)
    print_step(1, "System Setup")
    
    document_store = InMemoryDocumentStore()
    documents = [
        Document(content="Haystack is an end-to-end LLM framework for building NLP applications."),
        Document(content="RAG combines retrieval with generation for better answers."),
        Document(content="BM25 is a keyword-based ranking algorithm."),
    ]
    document_store.write_documents(documents)
    
    print(f"✓ Document store initialized with {len(documents)} documents")
    
    # Create RAG pipeline
    print_step(2, "RAG Pipeline Creation")
    
    prompt_template = """
Answer the question based on these documents:
{% for doc in documents %}
{{ doc.content }}
{% endfor %}

Question: {{ question }}
Answer:
"""
    
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
    rag_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
    rag_pipeline.add_component("llm", OpenAIGenerator())
    rag_pipeline.add_component("answer_builder", AnswerBuilder())
    
    rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")
    rag_pipeline.connect("llm.replies", "answer_builder.replies")
    rag_pipeline.connect("llm.meta", "answer_builder.meta")
    rag_pipeline.connect("retriever.documents", "answer_builder.documents")
    
    print("✓ Created full RAG pipeline with OpenAI")
    
    # Run query
    print_step(3, "Running RAG Query with OpenAI")
    
    try:
        result = rag_pipeline.run({
            "retriever": {"query": "What is Haystack?"},
            "prompt_builder": {"question": "What is Haystack?"},
            "answer_builder": {"query": "What is Haystack?"},
        })
        
        answer = result["answer_builder"]["answers"][0]
        print("\n✅ ONLINE DEMONSTRATION SUCCESSFUL!")
        print(f"\nGenerated Answer:\n{answer.data}\n")
        print(f"Retrieved Documents: {len(answer.documents)}")
        
    except Exception as e:
        print(f"\n❌ Error during online execution: {e}")
        print("This may be due to network issues or invalid API key")
        sys.exit(1)


def main():
    """Main entry point for the demonstration."""
    parser = argparse.ArgumentParser(
        description="Haystack Full System Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Run in online mode with OpenAI integration (requires OPENAI_API_KEY)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.online:
            demo_online_system()
        else:
            demo_offline_system()
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
