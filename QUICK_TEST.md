# Quick Start Testing - 30 Minutes

## One-Command Quick Test

Run this single command to test everything:

```bash
python test_all.py
```

**Expected Result:**
```
===============================================================================
          CLOTHING ONTOLOGY - COMPREHENSIVE TEST SUITE
===============================================================================

TEST GROUP 1: Environment & Dependencies
  [ 1] ✓ PASS - Python dependencies installed
       flask, rdflib, pyshacl, pytest

TEST GROUP 2: Code Quality
  [ 2] ✓ PASS - Linting (flake8)
       No PEP 8 violations
  [ 3] ✓ PASS - Code formatting (black)
       Code properly formatted

TEST GROUP 3: Ontology Validation
  [ 4] ✓ PASS - Ontology (Turtle)
       4XXX triples loaded
  [ 5] ✓ PASS - Ontology (RDF/XML)
       4XXX triples loaded

TEST GROUP 4: Unit Tests
  [ 6] ✓ PASS - Unit tests (pytest)
       20+ tests executed

TEST GROUP 5: SHACL Validation
  [ 7] ✓ PASS - SHACL validation
       0 violations

TEST GROUP 6: SPARQL Queries
  [ 8] ✓ PASS - SPARQL queries (7/7)
       7 query files found

TEST GROUP 7: Generated Data
  [ 9] ✓ PASS - Generated data files
       3 core files

TEST GROUP 8: Package Configuration
  [10] ✓ PASS - Config files
       4 files

TEST GROUP 9: Documentation
  [11] ✓ PASS - Documentation files
       6 files

TEST GROUP 10: CI/CD Configuration
  [12] ✓ PASS - GitHub Actions workflow
       .github/workflows/tests.yml

===============================================================================
                          TEST SUMMARY
===============================================================================

Total Tests: 12/12 PASSED (100.0%)

✓ ALL TESTS PASSED!
✓ Project is 100% complete and ready for submission!

===============================================================================
```

---

## Using Makefile Commands

If you prefer individual commands:

```bash
# View all available commands
make help

# Install dependencies
make install-dev

# Run tests
make test
make test-cov          # with coverage

# Code quality
make lint
make format
make format-check
make type-check

# Ontology validation
make validate-ontology
make validate-shacl

# Run pipeline
make pipeline-mock

# SPARQL queries
make queries

# Start web server
make web               # Then visit http://127.0.0.1:5000

# Clean artifacts
make clean

# Build package
make build
```

---

## Step-by-Step Manual Testing (Advanced)

If you want detailed control, follow `TESTING_GUIDE.md`:

```bash
# Test 1: Environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Test 2: Code quality
black --check scripts/ recommend.py app.py --line-length=100
flake8 scripts/ recommend.py app.py --max-line-length=100

# Test 3: Ontology
python -c "import rdflib; g=rdflib.Graph(); g.parse('Clothing_Ontology.ttl'); print(f'✓ {len(g)} triples')"

# Test 4: Tests
pytest tests/ -v

# Test 5: SHACL
python scripts/validate_shacl.py

# Test 6: SPARQL
python scripts/run_sparql_queries.py

# Test 7: Pipeline
python scripts/run_pipeline.py --llm-mode mock --limit 10

# Test 8: Web UI
python app.py
# Visit http://127.0.0.1:5000
```

---

## Expected Results Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Ontology** | ✓ | 4000+ triples, valid RDF |
| **Code Quality** | ✓ | PEP 8 compliant, properly formatted |
| **Unit Tests** | ✓ | 20+ tests passing |
| **SHACL** | ✓ | 0 violations |
| **SPARQL** | ✓ | 7 queries, all executable |
| **Data** | ✓ | 1,962 items, 1,638 enriched |
| **Package** | ✓ | setup.py, pyproject.toml, LICENSE |
| **CI/CD** | ✓ | GitHub Actions workflow configured |
| **Documentation** | ✓ | All required files present |

---

## If Any Test Fails

1. **Run full test**: `python test_all.py` (gives detailed error)
2. **Check specific area**: Review `TESTING_GUIDE.md` for that section
3. **Fix the issue**: Follow error message recommendations
4. **Re-run test**: Verify fix

---

## Timeline

- ⏱ **5 minutes**: `python test_all.py`
- ⏱ **10 minutes**: Make commands (if doing individually)
- ⏱ **30 minutes**: Full manual testing (all tests in TESTING_GUIDE.md)

---

## Next Steps After Testing

Once all tests pass ✓:

1. **Add files to Git**:
   ```bash
   git add LICENSE setup.py pyproject.toml CONTRIBUTING.md CHANGELOG.md MANIFEST.in Makefile TESTING_GUIDE.md test_all.py .gitignore .github/
   git commit -m "feat: add complete project infrastructure (LICENSE, setup, CI/CD, documentation)"
   ```

2. **Push to GitHub**:
   ```bash
   git push origin main
   ```

3. **Create Project Report** (only after all tests pass)
4. **Create Presentation Slides** (only after all tests pass)

---

## Success Criteria

✅ **Project is complete when:**
- [ ] `python test_all.py` → 12/12 PASSED
- [ ] All Git files committed
- [ ] No outstanding issues
- [ ] Ready for Report & Presentation

🎉 **Then**: Create formal submission documents
