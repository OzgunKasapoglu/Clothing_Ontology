.PHONY: help install install-dev test lint format clean build docs

help:
	@echo "Clothing Ontology - Available Commands"
	@echo "========================================"
	@echo "install           Install project dependencies"
	@echo "install-dev       Install with development dependencies"
	@echo "test              Run test suite"
	@echo "test-cov          Run tests with coverage report"
	@echo "lint              Check code quality (flake8)"
	@echo "format            Format code (black)"
	@echo "format-check      Check if code needs formatting"
	@echo "type-check        Run type checking (mypy)"
	@echo "validate-ontology Validate RDF/OWL syntax"
	@echo "validate-shacl    Run SHACL validation"
	@echo "pipeline-mock     Run pipeline with mock LLM"
	@echo "pipeline-ollama   Run pipeline with Ollama LLM"
	@echo "queries           Execute SPARQL queries"
	@echo "web               Start Flask web server"
	@echo "clean             Remove build artifacts"
	@echo "docs              Generate/view documentation"
	@echo "build             Build distribution packages"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=scripts --cov=recommend --cov=nl2sparql --cov-report=html --cov-report=term-missing

lint:
	flake8 scripts/ recommend.py app.py nl2sparql.py --max-line-length=120

format:
	black scripts/ tests/ recommend.py app.py nl2sparql.py --line-length=120

format-check:
	black --check scripts/ tests/ recommend.py app.py nl2sparql.py --line-length=120

type-check:
	mypy recommend.py app.py nl2sparql.py --ignore-missing-imports

validate-ontology:
	python -c "import rdflib; g=rdflib.Graph(); g.parse('Clothing_Ontology.ttl', format='turtle'); print(f'✓ Valid ontology: {len(g)} triples')"

validate-shacl:
	python scripts/validate_shacl.py

pipeline-mock:
	python scripts/run_pipeline.py --llm-mode mock

pipeline-ollama:
	python scripts/run_pipeline.py --llm-mode ollama --ollama-endpoint http://localhost:11434 --ollama-model llama3.1

queries:
	python scripts/run_sparql_queries.py

web:
	python app.py

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .coverage htmlcov .pytest_cache

docs:
	@echo "Opening WIDOCO documentation in browser..."
	@python -m webbrowser "docs/widoco/doc/index-en.html"

build: clean
	python -m build

.DEFAULT_GOAL := help
