# Testing Strategy for Custom GPT RTF Converter

## Overview

This document outlines the comprehensive testing strategy for the Custom GPT RTF converter. The testing approach combines multiple strategies: **Golden tests**, **Robustness tests**, and **RTF format validation**.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Testing Strategies](#testing-strategies)
3. [Running Tests Locally](#running-tests-locally)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Test Organization](#test-organization)
6. [Adding New Tests](#adding-new-tests)

---

## Test Structure

```
testCustomGPT/
├── tests/
│   ├── input/                    # Input test cases
│   │   ├── sample1.txt
│   │   └── sample2.txt
│   ├── expected/                 # Expected reference outputs
│   │   ├── sample1_expected.rtf
│   │   └── sample2_expected.rtf
│   ├── output/                   # Generated test outputs (created during tests)
│   │   ├── sample1_output.rtf
│   │   └── sample2_output.rtf
│   └── test_runner.py            # Main test suite
├── .github/
│   └── workflows/
│       └── test-custom-gpt.yml  # GitHub Actions pipeline
├── scripts/
│   └── generate_test_report.py  # Report generation tool
└── requirements.txt              # Python dependencies
```

---

## Testing Strategies

### 1. Golden Tests (Input/Output Comparison)

**What it does**: Compares the Custom GPT output against reference ("golden") files.

**How it works**:
1. Input file from `tests/input/sample*.txt` is sent to the Custom GPT
2. Generated RTF is saved to `tests/output/`
3. Output is normalized (spaces, line breaks, formatting variations handled)
4. Extracted visible text is compared with expected reference from `tests/expected/`

**Files involved**:
- `test_runner.py` → `TestGoldenTests` class
- Specifically: `test_content_matches_expected()` method

**Tolerance**: 85% text similarity by default (configurable)

**Example**:
```python
def test_content_matches_expected(self, sample):
    # Load input and expected output
    # Call Custom GPT API
    # Extract and normalize text
    # Assert 85%+ similarity
```

### 2. Robustness Tests

**What it does**: Ensures the Custom GPT produces consistent and stable output across variations.

**Tests include**:
- **Consistency**: Multiple calls with same input produce valid RTF
- **Special characters**: Handles accented characters (é, è, ù), symbols (©, £, €)
- **Format stability**: Output format remains consistent

**Files involved**:
- `test_runner.py` → `TestRobustness` class

**Example outputs tested**:
```
Café ✓
Naïve ✓
£500, © 2025 ✓
```

### 3. RTF Format Validation

**What it does**: Ensures RTF structure is valid and not corrupted.

**Validations**:
- ✅ RTF header present (`{\rtf1\ansi...}`)
- ✅ Balanced braces `{...}`
- ✅ Required RTF elements present
- ✅ No control sequence corruption
- ✅ Proper paragraph markers (`\par`)

**Files involved**:
- `test_runner.py` → `RTFValidator` class
- `TestRTFValidation` class for specific RTF checks

**Implementation**:
```python
class RTFValidator:
    @staticmethod
    def is_valid_rtf(content: str) -> Tuple[bool, str]:
        # Check RTF header
        # Validate brace balance
        # Verify required elements
```

---

## Running Tests Locally

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
set OPENAI_API_KEY=sk_test_...
set OPENAI_MODEL_ID=g_...
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/test_runner.py -v

# Run with coverage report
pytest tests/test_runner.py --cov=tests --cov-report=html

# Run specific test class
pytest tests/test_runner.py::TestGoldenTests -v

# Run specific test
pytest tests/test_runner.py::TestGoldenTests::test_rtf_format_validity -v
```

### Run Test Categories

```bash
# Only golden tests
pytest tests/test_runner.py::TestGoldenTests -v

# Only robustness tests
pytest tests/test_runner.py::TestRobustness -v

# Only format validation tests
pytest tests/test_runner.py::TestRTFValidation -v

# Only integration tests
pytest tests/test_runner.py::TestIntegration -v
```

### Generate Test Report

```bash
# Run tests and generate report
pytest tests/test_runner.py -v --junit-xml=test-results.xml
python scripts/generate_test_report.py tests/output test-results.xml > TEST_REPORT.md
```

### Expected Output Example

```
tests/test_runner.py::TestRTFValidation::test_rtf_header_present PASSED     [ 5%]
tests/test_runner.py::TestGoldenTests[sample1]::test_rtf_format_validity PASSED     [ 10%]
tests/test_runner.py::TestGoldenTests[sample1]::test_content_matches_expected PASSED     [ 15%]
tests/test_runner.py::TestGoldenTests[sample1]::test_no_rtf_corruption PASSED     [ 20%]
tests/test_runner.py::TestGoldenTests[sample2]::test_rtf_format_validity PASSED     [ 25%]
...

====================== 12 passed in 45.23s ======================
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

File: `.github/workflows/test-custom-gpt.yml`

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Daily schedule (2 AM UTC)

**Pipeline Steps**:

1. **Checkout code**: Clone repository
2. **Setup Python 3.11**: Configure Python environment
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run tests**: Execute full test suite with JUnit XML output
5. **Generate report**: Create markdown test report
6. **Upload artifacts**: Store results and outputs
7. **Comment on PR**: Post results to pull request (if applicable)
8. **Test summary**: Final status check

### Environment Variables (GitHub Secrets)

Set these in your GitHub repository settings:

```
OPENAI_API_KEY: Your OpenAI API key
OPENAI_MODEL_ID: Your Custom GPT model ID (optional)
```

### Example GitHub Actions Output

```
✅ test-custom-gpt / run-tests (Ubuntu Latest)
  Completed in 2m 15s

Test Results:
  ✅ 12 passed
  ⏭️  0 skipped
  ❌ 0 failed

Artifacts:
  📄 TEST_REPORT.md
  📊 test-results.xml
  📁 tests/output/
```

---

## Test Organization

### Test Classes

| Class | Purpose | Count |
|-------|---------|-------|
| `TestRTFValidation` | Format validation | 3 tests |
| `TestGoldenTests` | Output comparison | 6 tests (3 per sample) |
| `TestRobustness` | Stability verification | 4 tests |
| `TestIntegration` | End-to-end pipeline | 2 tests |
| **Total** | | **15 tests** |

### Test Parametrization

The `@pytest.mark.parametrize` decorator automatically runs tests for multiple samples:

```python
@pytest.mark.parametrize("sample", ["sample1", "sample2"])
class TestGoldenTests:
    def test_rtf_format_validity(self, sample):
        # Runs twice: once for sample1, once for sample2
```

### Test Dependencies

- **No external services**: All tests use mocked or API calls
- **Isolated test files**: Each test is independent
- **Cleanup**: Output files are preserved for inspection

---

## Adding New Tests

### Step 1: Create Input File

Create a new input test file in `tests/input/`:

```text
# tests/input/sample3.txt

Convertir en RTF: Mon nouveau test...
```

### Step 2: Generate Expected Output

Run the Custom GPT manually with the input and save the output:

```text
# tests/expected/sample3_expected.rtf

{\rtf1\ansi\ansicpg1252...
...
}
```

### Step 3: Parameterize Tests

Update the parametrize decorator:

```python
@pytest.mark.parametrize("sample", ["sample1", "sample2", "sample3"])
class TestGoldenTests:
    # Tests automatically run for all three samples
```

### Step 4: Run Tests

```bash
pytest tests/test_runner.py::TestGoldenTests[sample3] -v
```

---

## Handling Test Failures

### Common Issues

#### 1. RTF Format Invalid

**Error**: `Invalid RTF output: Missing RTF header {\rtf`

**Solution**:
- Verify Custom GPT system prompt generates valid RTF
- Check API response isn't truncated
- Increase timeout in workflow (currently 30s)

#### 2. Content Mismatch

**Error**: `Text similarity too low: 60% (expected >= 85%)`

**Solution**:
- Review expected output relevance
- Adjust tolerance threshold in `TextNormalizer.assert_normalized_equal()`
- Update expected reference if model behavior changed

#### 3. API Authentication Error

**Error**: `401 Unauthorized`

**Solution**:
- Verify `OPENAI_API_KEY` environment variable set
- Check API key has permission for Custom GPT model
- Verify model ID is correct

### Debug Mode

Run with additional logging:

```bash
# Show full stack traces
pytest tests/test_runner.py -v --tb=long

# Show print statements
pytest tests/test_runner.py -v -s

# Stop on first failure
pytest tests/test_runner.py -x
```

---

## Best Practices

### ✅ Do

- ✅ Add test cases for new Custom GPT features
- ✅ Update expected output when model behavior improves
- ✅ Run full test suite before pushing to main
- ✅ Review test outputs in `tests/output/` for quality
- ✅ Document complex test scenarios

### ❌ Don't

- ❌ Commit API keys or secrets to repository
- ❌ Create very large test files (keep under 5KB)
- ❌ Ignore test failures without understanding
- ❌ Modify test logic without updating documentation
- ❌ Run tests with different Python versions without testing

---

## Performance

### Expected Test Execution Time

- **Local tests**: ~45-60 seconds (includes API calls)
- **GitHub Actions**: ~2-3 minutes (with setup)
- **Bottleneck**: OpenAI API response time (~5-10s per request)

### Optimization Tips

- Use `pytest-xdist` for parallel test execution: `pytest -n auto`
- Cache responses during development
- Use smaller test samples for rapid iteration

```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/test_runner.py -n auto
```

---

## Reporting

### Test Report Generation

The GitHub Actions workflow automatically generates a markdown report with:

- ✅ Test summary (passed/failed/skipped)
- 📊 Pass rate percentage
- 📋 Detailed test results
- 🔍 Error messages for failures
- 📁 Links to generated RTF files

### Example Report Output

```markdown
# Custom GPT Test Report

✅ **Status**: PASSED

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 12 |
| **Passed** | 12 ✅ |
| **Failed** | 0 ❌ |
| **Pass Rate** | 100.0% |

## Test Details

### TestGoldenTests[sample1]
- ✅ **test_rtf_format_validity** (8.23s)
- ✅ **test_content_matches_expected** (7.45s)
- ✅ **test_no_rtf_corruption** (0.15s)
```

---

## References

- [pytest documentation](https://docs.pytest.org/)
- [OpenAI API docs](https://platform.openai.com/docs/api-reference)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [RTF specification](https://www.microsoft.com/en-us/download/details.aspx?id=10725)

---

## Support

For issues or questions:

1. Check test output in `tests/output/`
2. Review GitHub Actions logs
3. Run tests locally with `-v -s` flags
4. Check environment variables are set correctly

---

*Last updated: 2025-11-08*
