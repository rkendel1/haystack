# Full System End-to-End Test

## Overview

The `test_full_system_e2e.py` file contains comprehensive end-to-end tests that validate the complete setup, configuration, and execution of the Haystack system. These tests ensure that all components work together seamlessly from installation through query execution.

## What This Test Validates

### Test 1: `test_full_system_setup_and_run`

This comprehensive test performs a complete workflow including:

1. **System Configuration Verification**
   - Validates OpenAI API key is properly configured
   - Checks API key format and presence

2. **Document Store Initialization**
   - Creates an in-memory document store
   - Verifies store is ready for operations

3. **Document Indexing**
   - Indexes 6 sample documents using BM25
   - Validates all documents are successfully stored

4. **RAG Pipeline Creation**
   - Creates a complete Retrieval-Augmented Generation pipeline
   - Connects BM25 retriever, prompt builder, OpenAI generator, and answer builder
   - Validates all component connections

5. **Pipeline Serialization**
   - Serializes pipeline to YAML format
   - Serializes pipeline to JSON format
   - Verifies files are created successfully

6. **Pipeline Deserialization**
   - Loads pipeline from YAML
   - Loads pipeline from JSON
   - Reconnects document stores
   - Validates loaded pipelines are functional

7. **Query Execution**
   - Runs 3 different test queries through the pipeline
   - Validates OpenAI integration works correctly
   - Checks that relevant documents are retrieved
   - Verifies answers are generated with expected content

8. **Result Validation**
   - Validates result structure and metadata
   - Checks for expected keywords in answers
   - Ensures document attribution is maintained

### Test 2: `test_full_system_alternative_configuration`

A secondary test that validates the system with alternative documents and queries to ensure robustness across different datasets.

## Requirements

### Dependencies

- Python 3.9+
- haystack-ai
- pytest
- OpenAI Python SDK
- Jinja2

Install dependencies:
```bash
pip install haystack-ai pytest
```

### Environment Variables

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key for running LLM queries

Set the environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Network Access

These tests require:
- **Internet connectivity** to access the OpenAI API
- **Outbound HTTPS access** to `api.openai.com`

## Running the Tests

### Run All Full System Tests

```bash
cd /path/to/haystack
pytest e2e/pipelines/test_full_system_e2e.py -v -s
```

### Run Specific Test

```bash
# Run the main comprehensive test
pytest e2e/pipelines/test_full_system_e2e.py::test_full_system_setup_and_run -v -s

# Run the alternative configuration test
pytest e2e/pipelines/test_full_system_e2e.py::test_full_system_alternative_configuration -v -s
```

### Expected Output

When successful, you should see output like:

```
✓ OpenAI API key configured (length: XXX)
✓ Document store initialized
✓ Indexed 6 documents with BM25
✓ RAG pipeline created with all components connected
✓ Pipeline serialized to YAML: /tmp/.../full_system_rag_pipeline.yaml
✓ Pipeline serialized to JSON: /tmp/.../full_system_rag_pipeline.json
✓ Pipeline loaded from YAML
✓ Pipeline loaded from JSON

============================================================
Running test queries...
============================================================

Query 1: What is Haystack?
Answer: Haystack is an end-to-end LLM framework...
✓ Retrieved 3 relevant documents
✓ Generated answer with XXX characters
✓ Found relevant keywords: ['LLM', 'framework']

... (more queries) ...

============================================================
FULL SYSTEM TEST PASSED!
============================================================

All components verified:
  ✓ OpenAI API configuration
  ✓ Document store initialization
  ✓ Document indexing with BM25
  ✓ RAG pipeline creation
  ✓ Pipeline serialization (YAML & JSON)
  ✓ Pipeline deserialization
  ✓ Query execution with OpenAI
  ✓ Result validation
============================================================
```

## Test Behavior

### When API Key is Not Set

The tests will be **skipped** with the message:
```
SKIPPED [1] e2e/pipelines/test_full_system_e2e.py:31: Export an env var called OPENAI_API_KEY containing the OpenAI API key to run this test.
```

### When Network is Unavailable

The tests will **fail** with a connection error if:
- No internet connection is available
- OpenAI API is unreachable
- Firewall blocks access to api.openai.com

### Test Duration

- First run: ~20-30 seconds (including OpenAI API calls)
- Subsequent runs: Similar duration (API calls are not cached)

## Troubleshooting

### "Connection error" when running test

**Cause:** No internet access or OpenAI API is unreachable

**Solution:** 
- Verify internet connection
- Check firewall settings
- Ensure `api.openai.com` is accessible

### "Invalid API key"

**Cause:** API key is incorrect or expired

**Solution:**
- Verify your OpenAI API key at https://platform.openai.com/api-keys
- Ensure key has proper permissions
- Check for any extra spaces or characters in the environment variable

### Import errors

**Cause:** Missing dependencies

**Solution:**
```bash
pip install haystack-ai pytest openai Jinja2
```

## CI/CD Integration

To integrate these tests into CI/CD:

```yaml
test_full_system:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install haystack-ai pytest
    - name: Run full system tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest e2e/pipelines/test_full_system_e2e.py -v -s
```

## Notes

- These tests use **real OpenAI API calls** and will **consume API credits**
- The BM25 retriever is used instead of embedding-based retrieval to avoid dependency on HuggingFace models
- Tests are designed to be deterministic but LLM outputs may vary slightly
- The tests validate system integration, not individual component functionality

## Related Tests

- `e2e/pipelines/test_rag_pipelines_e2e.py` - Other RAG pipeline tests
- `test/` - Unit tests for individual components

## Support

For issues or questions:
- Check the [Haystack documentation](https://docs.haystack.deepset.ai/)
- Open an issue on [GitHub](https://github.com/deepset-ai/haystack/issues)
- Join the [Haystack Discord](https://discord.com/invite/xYvH6drSmA)
