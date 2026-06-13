# Contributing to Clothing Ontology

Thank you for your interest in contributing! We welcome contributions from the community. This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## How to Contribute

### 1. Reporting Issues

Found a bug or have a feature request? Please create an issue on GitHub with:
- Clear title describing the problem
- Detailed description of the issue
- Steps to reproduce (for bugs)
- Expected vs. actual behavior
- Your environment (Python version, OS, etc.)

### 2. Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/clothing-ontology.git
cd clothing-ontology

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### 3. Making Changes

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# Follow code style (see below)

# Run tests
pytest

# Commit with clear message
git commit -m "feat: add new feature" -m "Description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

### 4. Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request with:
   - Clear title and description
   - Reference to related issues (if any)
   - Summary of changes
   - Any breaking changes noted

## Code Style

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Maximum line length: 100 characters
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`

```bash
# Format code
black scripts/ tests/ *.py

# Check linting
flake8 scripts/ tests/ *.py

# Type checking
mypy recommend.py app.py
```

### Ontology Changes

- Update `Clothing_Ontology.ttl` (canonical format)
- Keep both `.ttl` and `.rdf` versions in sync
- Add `rdfs:comment` and `rdfs:label` for new entities
- Update `docs/Specification_v2.md` to document changes
- Regenerate WIDOCO documentation

### Documentation

- Use Markdown for all documentation
- Include code examples where applicable
- Link to related documentation
- Keep README.md updated

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pipeline.py

# Run with coverage
pytest --cov=scripts --cov=recommend --cov-report=html

# Run specific test
pytest tests/test_recommend.py::TestColorHarmony -v
```

### Writing Tests

- Add tests for new features in `tests/`
- Use descriptive test names
- Include docstrings explaining test purpose
- Aim for >80% code coverage

Example:
```python
def test_color_harmony_black_white():
    """Test that black and white colors harmonize."""
    graph = rdflib.Graph()
    graph.parse("Clothing_Ontology.ttl", format="turtle")
    assert color_harmonizes(graph, "Black", "White")
```

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that don't affect code meaning (formatting, missing semicolons, etc.)
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `perf:` Code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to build process, dependencies, etc.

Examples:
```
feat: add user preference filtering to recommendations
fix: correct color harmony validation for complementary colors
docs: update setup instructions with virtual environment steps
test: add test cases for SHACL validation
```

## Pull Request Review Process

1. At least one maintainer will review your PR
2. Address any requested changes
3. Rebase and force push if needed (with caution)
4. Once approved, your PR will be merged

## Ontology Extension Guidelines

To extend the ontology:

1. **Design**: Document new classes/properties in `docs/`
2. **Implementation**: Add to `Clothing_Ontology.ttl`
3. **Validation**: Update `shapes/clothing_shapes.ttl`
4. **Testing**: Add SPARQL queries in `queries/`
5. **Documentation**: Update specification document
6. **Regenerate**: Run Widoco to update HTML docs

## Data Acquisition & LLM Integration

For improvements to data pipeline:

1. Update relevant script in `scripts/`
2. Add unit tests in `tests/test_pipeline.py`
3. Update mapping files in `data/mappings/` if needed
4. Document changes in `docs/LLM_Integration_Plan.md`
5. Test with mock mode first: `python scripts/run_pipeline.py --llm-mode mock`

## Performance & Scalability

When optimizing:

1. Profile before/after: `python -m cProfile -s cumtime app.py`
2. Document improvements in commit message
3. Include benchmark results in PR description
4. Ensure tests still pass

## Documentation Updates

1. Update relevant `.md` files in `docs/`
2. Keep `README.md` current
3. Update WIDOCO documentation if ontology changes
4. Add examples for new features

## Licensing

- All contributions are licensed under CC BY 4.0
- By contributing, you agree to license your work under this license
- Include proper attribution

## Questions?

- Check existing issues and discussions
- Read the documentation in `docs/`
- Review the specification: `docs/Specification_v2.md`
- Open a GitHub discussion for questions

## Acknowledgments

Thank you for contributing to the Clothing Ontology project! Your efforts help improve the semantic web and advance ontology-driven recommendation systems.
