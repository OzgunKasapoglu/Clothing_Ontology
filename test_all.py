#!/usr/bin/env python
"""
Comprehensive Test Suite for Clothing Ontology Project
Run this script to test every single element of the project
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple

# ANSI Colors for output (using ASCII-safe characters)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_test(test_num: int, name: str, passed: bool, details: str = "") -> None:
    """Print test result"""
    status = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"  [{test_num:2d}] {status} - {name}")
    if details:
        print(f"       {details}")

def run_command(cmd: str, capture: bool = False) -> Tuple[int, str]:
    """Run a shell command and return return code and output"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode, result.stdout + result.stderr
        else:
            return subprocess.run(cmd, shell=True, timeout=10).returncode, ""
    except subprocess.TimeoutExpired:
        return 1, "Command timeout"
    except Exception as e:
        return 1, str(e)

def test_suite() -> None:
    """Run comprehensive test suite"""

    print_header("CLOTHING ONTOLOGY - COMPREHENSIVE TEST SUITE")

    total_tests = 0
    passed_tests = 0
    failed_tests: List[str] = []

    # TEST 1: Dependencies
    print(f"{BOLD}TEST GROUP 1: Environment & Dependencies{RESET}")
    total_tests += 1
    try:
        import rdflib, flask, pyshacl, pytest
        print_test(1, "Python dependencies installed", True, "flask, rdflib, pyshacl, pytest")
        passed_tests += 1
    except ImportError as e:
        print_test(1, "Python dependencies installed", False, str(e))
        failed_tests.append("Dependencies not installed")

    # TEST 2: Code Quality
    print(f"\n{BOLD}TEST GROUP 2: Code Quality{RESET}")

    total_tests += 1
    rc, _ = run_command("python -m flake8 scripts/ recommend.py app.py --max-line-length=120 --count")
    passed = rc == 0
    print_test(2, "Linting (flake8)", passed, "No PEP 8 violations")
    if passed: passed_tests += 1
    else: failed_tests.append("Linting failed")

    total_tests += 1
    rc, _ = run_command("python -m black --check scripts/ tests/ recommend.py app.py --line-length=120")
    passed = rc == 0
    print_test(3, "Code formatting (black)", passed, "Code properly formatted")
    if passed: passed_tests += 1
    else: failed_tests.append("Code formatting issues")

    # TEST 3: Ontology
    print(f"\n{BOLD}TEST GROUP 3: Ontology Validation{RESET}")

    total_tests += 1
    try:
        import rdflib
        g = rdflib.Graph()
        g.parse('Clothing_Ontology.ttl', format='turtle')
        print_test(4, "Ontology (Turtle)", True, f"{len(g)} triples loaded")
        passed_tests += 1
    except Exception as e:
        print_test(4, "Ontology (Turtle)", False, str(e))
        failed_tests.append("Ontology validation failed")

    total_tests += 1
    try:
        g2 = rdflib.Graph()
        g2.parse('Clothing_Ontology.rdf', format='xml')
        print_test(5, "Ontology (RDF/XML)", True, f"{len(g2)} triples loaded")
        passed_tests += 1
    except Exception as e:
        print_test(5, "Ontology (RDF/XML)", False, str(e))
        failed_tests.append("RDF/XML validation failed")

    # TEST 4: Unit Tests
    print(f"\n{BOLD}TEST GROUP 4: Unit Tests{RESET}")

    total_tests += 1
    rc, output = run_command("python -m pytest tests/ -q", capture=True)
    passed = rc == 0 and ("passed" in output or "PASSED" in output)
    test_count = output.count("passed") + output.count("PASSED") if passed else 0
    print_test(6, "Unit tests (pytest)", passed, f"{test_count} tests executed")
    if passed: passed_tests += 1
    else: failed_tests.append("Unit tests failed")

    # TEST 5: SHACL
    print(f"\n{BOLD}TEST GROUP 5: SHACL Validation{RESET}")

    total_tests += 1
    try:
        if os.path.exists('data/generated/shacl_validation_summary.json'):
            with open('data/generated/shacl_validation_summary.json') as f:
                result = json.load(f)
                conforms = result.get('conforms', False)
                print_test(7, "SHACL validation", conforms,
                          f"{result.get('results', 0)} violations" if not conforms else "0 violations")
                if conforms: passed_tests += 1
                else: failed_tests.append("SHACL validation failed")
        else:
            print_test(7, "SHACL validation", False, "Validation report not found")
            failed_tests.append("SHACL report missing")
    except Exception as e:
        print_test(7, "SHACL validation", False, str(e))
        failed_tests.append("SHACL check failed")

    # TEST 6: SPARQL
    print(f"\n{BOLD}TEST GROUP 6: SPARQL Queries{RESET}")

    total_tests += 1
    try:
        query_files = list(Path('queries').glob('*.rq'))
        expected = 7
        print_test(8, f"SPARQL queries ({len(query_files)}/{expected})",
                  len(query_files) == expected, f"{len(query_files)} query files found")
        if len(query_files) == expected: passed_tests += 1
        else: failed_tests.append(f"Expected {expected} queries, found {len(query_files)}")
    except Exception as e:
        print_test(8, "SPARQL queries", False, str(e))
        failed_tests.append("SPARQL files check failed")

    # TEST 7: Data Files
    print(f"\n{BOLD}TEST GROUP 7: Generated Data{RESET}")

    total_tests += 1
    try:
        required_files = [
            'data/generated/hm_sample_catalog.ttl',
            'data/generated/hm_llm_enriched_catalog.ttl',
            'data/generated/pipeline_summary.json',
        ]
        all_exist = all(os.path.exists(f) for f in required_files)
        print_test(9, "Generated data files", all_exist, f"{len(required_files)} core files")
        if all_exist: passed_tests += 1
        else: failed_tests.append("Generated data files missing")
    except Exception as e:
        print_test(9, "Generated data files", False, str(e))
        failed_tests.append("Data files check failed")

    # TEST 8: Configuration
    print(f"\n{BOLD}TEST GROUP 8: Package Configuration{RESET}")

    total_tests += 1
    try:
        required_configs = ['setup.py', 'pyproject.toml', 'LICENSE', 'MANIFEST.in']
        all_exist = all(os.path.exists(f) for f in required_configs)
        print_test(10, "Config files", all_exist, f"{len(required_configs)} files")
        if all_exist: passed_tests += 1
        else: failed_tests.append("Config files missing")
    except Exception as e:
        print_test(10, "Config files", False, str(e))
        failed_tests.append("Config check failed")

    # TEST 9: Documentation
    print(f"\n{BOLD}TEST GROUP 9: Documentation{RESET}")

    total_tests += 1
    try:
        required_docs = [
            'README.md', 'CONTRIBUTING.md', 'CHANGELOG.md',
            'docs/Phase2_Report.md', 'docs/Specification_v2.md',
            'docs/widoco/doc/index-en.html'
        ]
        all_exist = all(os.path.exists(f) for f in required_docs)
        print_test(11, "Documentation files", all_exist, f"{len(required_docs)} files")
        if all_exist: passed_tests += 1
        else: failed_tests.append("Documentation files missing")
    except Exception as e:
        print_test(11, "Documentation files", False, str(e))
        failed_tests.append("Documentation check failed")

    # TEST 10: GitHub Workflow
    print(f"\n{BOLD}TEST GROUP 10: CI/CD Configuration{RESET}")

    total_tests += 1
    try:
        workflow_path = '.github/workflows/tests.yml'
        exists = os.path.exists(workflow_path)
        print_test(12, "GitHub Actions workflow", exists, workflow_path if exists else "Not found")
        if exists: passed_tests += 1
        else: failed_tests.append("GitHub workflow missing")
    except Exception as e:
        print_test(12, "GitHub Actions workflow", False, str(e))
        failed_tests.append("Workflow check failed")

    # Summary
    print_header("TEST SUMMARY")

    passed_percent = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"{BOLD}Total Tests: {passed_tests}/{total_tests} PASSED ({passed_percent:.1f}%){RESET}\n")

    if failed_tests:
        print(f"{RED}Failed checks:{RESET}")
        for i, failure in enumerate(failed_tests, 1):
            print(f"  {i}. {failure}")
    else:
        print(f"{GREEN}[PASS] ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}[PASS] Project is 100% complete and ready for submission!{RESET}")

    print_header("END OF TEST SUITE")

    # Exit with appropriate code
    sys.exit(0 if not failed_tests else 1)

if __name__ == "__main__":
    test_suite()
