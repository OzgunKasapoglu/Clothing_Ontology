"""Tests for the NL -> SPARQL LLM-integration module."""

from __future__ import annotations

from pathlib import Path

import pytest
import rdflib

import nl2sparql as nl

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def graph() -> rdflib.Graph:
    g = rdflib.Graph()
    g.parse(ROOT / "Clothing_Ontology.ttl", format="turtle")
    return g


@pytest.fixture(scope="module")
def vocab(graph: rdflib.Graph) -> dict[str, list[str]]:
    return nl.collect_vocabulary(graph)


def test_vocabulary_contains_core_terms(vocab):
    assert "ClothingItem" in vocab["classes"]
    assert "hasColor" in vocab["object_properties"]
    assert "hasPrice" in vocab["data_properties"]
    assert "Blue" in vocab["individuals"]


def test_validate_blocks_update(vocab):
    ok, reason = nl.validate_query("DELETE WHERE { ?s ?p ?o }", vocab)
    assert not ok and "read-only" in reason.lower()


def test_validate_blocks_hallucinated_term(vocab):
    ok, reason = nl.validate_query("SELECT ?x WHERE { ?x clo:hasMadeUpProperty ?y }", vocab)
    assert not ok and "hallucination" in reason.lower()


def test_validate_blocks_unparseable(vocab):
    ok, _ = nl.validate_query("SELECT ?x WHERE { ?x clo:hasColor", vocab)
    assert not ok


def test_validate_accepts_grounded_query(vocab):
    ok, _ = nl.validate_query("SELECT ?i WHERE { ?i clo:hasColor clo:Blue }", vocab)
    assert ok


def test_extract_query_strips_code_fence():
    raw = "Sure!\n```sparql\nSELECT ?x WHERE { ?x clo:hasColor clo:Blue }\n```\nDone."
    assert nl.extract_query(raw).startswith("SELECT")
    assert "```" not in nl.extract_query(raw)


@pytest.mark.parametrize(
    "question",
    [
        "Show me blue items",
        "How many black clothes are there?",
        "What is the average price per category?",
        "formality distribution",
        "what materials for winter",
        "which female tops",
        "which colors match",
        "list outfit components",
        "something completely unrelated",
    ],
)
def test_deterministic_queries_are_valid(question, vocab):
    query, _intent = nl.deterministic_translate(question)
    ok, reason = nl.validate_query(query, vocab)
    assert ok, reason


def test_answer_without_llm_returns_rows(graph, vocab):
    result = nl.answer("Show me blue items", graph, vocab, use_llm=False)
    assert result["source"] == "fallback"
    assert result["error"] == ""
    assert len(result["rows"]) > 0


def test_answer_llm_unavailable_falls_back(graph, vocab):
    # No Ollama running on this port -> must fall back, not crash.
    result = nl.answer(
        "Show me red items",
        graph,
        vocab,
        use_llm=True,
        ollama_endpoint="http://127.0.0.1:1",
    )
    assert result["source"] == "fallback"
    assert result["llm_error"]
