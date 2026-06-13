#!/usr/bin/env python
"""Setup configuration for Clothing Ontology project."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="clothing-ontology",
    version="2.0.0",
    description="OWL 2 ontology for an outfit recommendation engine with web UI and semantic pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sedat",
    license="CC BY 4.0",
    url="https://github.com/your-username/clothing-ontology",
    packages=find_packages(exclude=["tests", "venv", "docs"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        "ontology",
        "owl",
        "semantic-web",
        "rdf",
        "sparql",
        "shacl",
        "recommendation-engine",
        "fashion",
        "clothing",
    ],
)
