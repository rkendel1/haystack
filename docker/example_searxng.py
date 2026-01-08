"""
Example: Using SearXNG Web Search with Haystack

This example demonstrates how to use the SearXNGWebSearch component
to search the web without requiring API keys.

Prerequisites:
1. Start the SearXNG service using Docker Compose:
   cd docker && docker-compose up -d

2. Wait for the service to be ready (check with: curl http://localhost:8888/healthz)

3. Run this example
"""

from haystack.components.websearch import SearXNGWebSearch

# Create a SearXNG web search component
# The base_url points to your local SearXNG instance
web_search = SearXNGWebSearch(
    base_url="http://localhost:8888",
    top_k=5
)

# Perform a search
query = "What is Haystack LLM framework?"
results = web_search.run(query=query)

# Display the results
print(f"\nSearch Results for: {query}\n")
print("=" * 80)

for i, doc in enumerate(results["documents"], 1):
    print(f"\n{i}. {doc.meta.get('title', 'No title')}")
    print(f"   URL: {doc.meta.get('url', 'No URL')}")
    print(f"   Content: {doc.content[:200]}...")
    print(f"   Engine: {doc.meta.get('engine', 'unknown')}")

print("\n" + "=" * 80)
print(f"\nTotal results: {len(results['documents'])}")
print(f"Total links: {len(results['links'])}")
