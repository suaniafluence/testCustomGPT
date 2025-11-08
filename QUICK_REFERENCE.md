# Quick Reference - Custom GPT Testing

## Run Tests Locally (30 seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
set OPENAI_API_KEY=sk_test_...

# 3. Run tests
pytest tests/test_runner.py -v
```

---

## Test Commands

```bash
# All tests
pytest tests/test_runner.py -v

# Golden tests only
pytest tests/test_runner.py::TestGoldenTests -v

# Robustness tests only
pytest tests/test_runner.py::TestRobustness -v

# Specific sample
pytest tests/test_runner.py::TestGoldenTests[sample1] -v

# First failure stops test
pytest tests/test_runner.py -x

# With coverage
pytest tests/test_runner.py --cov=tests

# Generate report
pytest tests/test_runner.py --junit-xml=test-results.xml
python scripts/generate_test_report.py tests/output test-results.xml
```

---

## File Structure

```
tests/
├── input/              ← Your test inputs (sample1.txt, sample2.txt)
├── expected/           ← Reference outputs (sample1_expected.rtf, ...)
├── output/             ← Generated during tests (auto-created)
└── test_runner.py      ← Main test suite (320 lines)

.github/workflows/
└── test-custom-gpt.yml ← GitHub Actions (auto-runs on push)

scripts/
└── generate_test_report.py ← Report generator

requirements.txt        ← Dependencies (pytest, requests, etc)
TESTING.md             ← Comprehensive guide
```

---

## Adding a Test Case (2 minutes)

1. Create `tests/input/sample3.txt`
2. Create `tests/expected/sample3_expected.rtf`
3. Update parametrize: `["sample1", "sample2", "sample3"]`
4. Run: `pytest tests/test_runner.py::TestGoldenTests[sample3] -v`

---

## Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestRTFValidation` | 3 | Format integrity |
| `TestGoldenTests` | 6 | Output comparison |
| `TestRobustness` | 4 | Stability |
| `TestIntegration` | 2 | End-to-end |
| **Total** | **15** | |

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk_test_...

# Optional (defaults to g-68fb932716ac8191abf323ea80f99a7a)
OPENAI_MODEL_ID=g_...
```

---

## GitHub Setup (1 minute)

1. Go to repo Settings → Secrets → New repository secret
2. Add `OPENAI_API_KEY`
3. Add `OPENAI_MODEL_ID` (optional)
4. Push to main → workflow auto-runs

---

## What Gets Tested

✅ RTF structure (headers, braces, format)
✅ Content accuracy (85% similarity)
✅ Special characters (é, ©, £, €)
✅ Output consistency
✅ Format stability

---

## Expected Test Duration

- **Local**: 45-60 seconds
- **GitHub Actions**: 2-3 minutes
- **Bottleneck**: OpenAI API calls (~5-10s each)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Check `OPENAI_API_KEY` env var |
| `RTF format invalid` | Review Custom GPT system prompt |
| `Content mismatch` | Update expected files or adjust tolerance |
| `Import errors` | Run `pip install -r requirements.txt` |

---

## Key Files

- **test_runner.py** (320 lines): Main test suite
- **TESTING.md** (454 lines): Detailed guide
- **test-custom-gpt.yml** (93 lines): GitHub Actions
- **generate_test_report.py** (182 lines): Report tool

---

**Total Setup**: 1,582 lines of code & documentation
**Ready to use**: ✅ Yes

See **TESTING.md** for complete documentation.
