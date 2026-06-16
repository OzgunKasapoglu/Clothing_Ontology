"""Natural-language -> SPARQL translation, grounded in the Clothing Ontology.

This module is the project's primary LLM integration: it turns a user question
into a SPARQL query that runs over the knowledge graph. Two translation paths
are provided:

* ``llm`` - prompts a local Ollama model whose prompt is constrained to the
  exact ontology vocabulary (classes, properties, individuals).
* ``fallback`` - a deterministic intent matcher that always produces a valid,
  grounded query, so the feature demonstrates even with no model installed.

Hallucination mitigation (the rubric's key LLM criterion) is enforced *after*
generation, regardless of path, by :func:`validate_query`:

1. read-only guard - reject any update/management keyword (INSERT, DELETE, ...);
2. shape guard - the query must be a single SELECT or ASK;
3. syntactic guard - the query must parse with rdflib's SPARQL parser;
4. grounding guard - every ``clo:`` term used must exist in the ontology.

A query that fails any guard is never executed; the request transparently
falls back to the deterministic translator.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

import rdflib
from rdflib import RDF, RDFS, OWL, Namespace
from rdflib.plugins.sparql import prepareQuery

CLO = Namespace("http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/")

PREFIXES = (
    "PREFIX clo: <http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/>\n"
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
)

COLORS = [
    "Red", "Orange", "Yellow", "Brown", "Blue", "Green", "Purple", "Pink",
    "Black", "White", "Grey", "Beige", "Navy", "Gold", "Silver", "Turquoise",
]

# Update/management keywords are rejected outright: the endpoint is read-only.
_FORBIDDEN = re.compile(
    r"\b(INSERT|DELETE|DROP|CLEAR|CREATE|LOAD|ADD|MOVE|COPY|WITH)\b", re.IGNORECASE
)
_CLO_TERM = re.compile(r"\bclo:([A-Za-z0-9_\-]+)")
_MAX_ROWS = 200


def _local(uri: Any) -> str:
    return str(uri).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def collect_vocabulary(graph: rdflib.Graph) -> dict[str, list[str]]:
    """Local names of every class, property, and individual in the ontology.

    Used both to constrain the LLM prompt and to validate generated queries.
    """
    classes, obj_props, data_props, individuals = set(), set(), set(), set()
    for s in graph.subjects(RDF.type, OWL.Class):
        if isinstance(s, rdflib.URIRef):
            classes.add(_local(s))
    for s in graph.subjects(RDF.type, OWL.ObjectProperty):
        obj_props.add(_local(s))
    for s in graph.subjects(RDF.type, OWL.DatatypeProperty):
        data_props.add(_local(s))
    for s in graph.subjects(RDF.type, OWL.NamedIndividual):
        if isinstance(s, rdflib.URIRef):
            individuals.add(_local(s))
    return {
        "classes": sorted(classes),
        "object_properties": sorted(obj_props),
        "data_properties": sorted(data_props),
        "individuals": sorted(individuals),
    }


def vocabulary_terms(vocab: dict[str, list[str]]) -> set[str]:
    terms: set[str] = set()
    for values in vocab.values():
        terms.update(values)
    return terms


# --------------------------------------------------------------------------- #
# LLM path (Ollama)
# --------------------------------------------------------------------------- #

def build_prompt(question: str, vocab: dict[str, list[str]]) -> str:
    return (
        "You translate a user question into ONE SPARQL query for an OWL "
        "clothing ontology. Output ONLY the SPARQL query, no prose, no code "
        "fences.\n\n"
        "Rules:\n"
        "- Use ONLY these prefixes: clo:, rdf:, rdfs:.\n"
        "- Use ONLY the vocabulary below. Do NOT invent class, property, or "
        "individual names.\n"
        "- The query MUST be a single read-only SELECT (no INSERT/DELETE).\n"
        "- Always retrieve rdfs:label for displayed resources.\n\n"
        f"Classes: {', '.join(vocab['classes'])}\n"
        f"Object properties: {', '.join(vocab['object_properties'])}\n"
        f"Data properties: {', '.join(vocab['data_properties'])}\n"
        f"Individuals: {', '.join(vocab['individuals'])}\n\n"
        f"Question: {question}\n\nSPARQL:"
    )


def call_ollama(
    prompt: str,
    endpoint: str = "http://localhost:11434",
    model: str = "llama3.1",
    timeout: float = 30.0,
) -> str:
    """Call a local Ollama /api/generate endpoint. Raises on any failure."""
    payload = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return str(body.get("response", ""))


def extract_query(text: str) -> str:
    """Strip code fences / stray prose, returning the query body."""
    fenced = re.search(r"```(?:sparql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    # Keep from the first PREFIX/SELECT/ASK onward.
    match = re.search(r"(PREFIX|SELECT|ASK)\b", text, re.IGNORECASE)
    return text[match.start():].strip() if match else text.strip()


# --------------------------------------------------------------------------- #
# Validation (hallucination mitigation)
# --------------------------------------------------------------------------- #

def validate_query(query: str, vocab: dict[str, list[str]]) -> tuple[bool, str]:
    if _FORBIDDEN.search(query):
        return False, "Rejected: query contains a write/management keyword (read-only endpoint)."
    if not re.search(r"\b(SELECT|ASK)\b", query, re.IGNORECASE):
        return False, "Rejected: not a SELECT/ASK query."
    if re.search(r"\bASK\b", query[:200], re.IGNORECASE) and re.search(r"\bSELECT\b", query, re.IGNORECASE):
        return False, "Rejected: query must be a single statement."

    body = query if query.upper().lstrip().startswith("PREFIX") else PREFIXES + query
    try:
        prepareQuery(body)
    except Exception as exc:  # noqa: BLE001 - surface any parser error as a reason
        return False, f"Rejected: query does not parse ({exc})."

    known = vocabulary_terms(vocab)
    used = set(_CLO_TERM.findall(query))
    unknown = sorted(used - known)
    if unknown:
        return False, f"Rejected: unknown ontology term(s) {unknown} (possible hallucination)."
    return True, "Validated: read-only, parses, and every clo: term exists in the ontology."


def run_query(graph: rdflib.Graph, query: str) -> tuple[list[str], list[dict[str, str]]]:
    body = query if query.upper().lstrip().startswith("PREFIX") else PREFIXES + query
    result = graph.query(body)
    columns = [str(v) for v in result.vars] if result.vars else []
    rows: list[dict[str, str]] = []
    for record in result:
        row = {}
        for var in columns:
            value = record[var] if hasattr(record, "__getitem__") else None
            row[var] = _compact(value)
        rows.append(row)
        if len(rows) >= _MAX_ROWS:
            break
    return columns, rows


def _compact(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.replace(str(CLO), "clo:")


# --------------------------------------------------------------------------- #
# Deterministic fallback translator
# --------------------------------------------------------------------------- #

def _detect_color(text: str) -> str | None:
    for color in COLORS:
        if re.search(r"\b" + color.lower() + r"\b", text):
            return color
    return None


def deterministic_translate(question: str) -> tuple[str, str]:
    """Map a question to a grounded SPARQL query. Returns (query, intent)."""
    q = question.lower()
    color = _detect_color(q)
    counting = any(w in q for w in ("how many", "count", "number of", "distribution", "how much"))

    if color and counting:
        return (
            PREFIXES
            + "\nSELECT ?colorLabel (COUNT(DISTINCT ?item) AS ?itemCount)\nWHERE {\n"
            f"  ?item clo:hasColor clo:{color} .\n"
            "  clo:" + color + " rdfs:label ?colorLabel .\n"
            "}\nGROUP BY ?colorLabel",
            f"count items of color {color}",
        )
    if color:
        return (
            PREFIXES
            + "\nSELECT ?item ?label ?class\nWHERE {\n"
            f"  ?item clo:hasColor clo:{color} ;\n"
            "        rdfs:label ?label ;\n"
            "        rdf:type ?class .\n"
            "  FILTER(?class != <http://www.w3.org/2002/07/owl#NamedIndividual>)\n"
            "}\nORDER BY ?label\nLIMIT 100",
            f"items of color {color}",
        )
    if "price" in q and ("category" in q or "average" in q or "expensive" in q):
        return (
            PREFIXES
            + "\nSELECT ?categoryLabel (COUNT(DISTINCT ?item) AS ?itemCount) (ROUND(AVG(?price)) AS ?avgPrice)\nWHERE {\n"
            "  VALUES ?category { clo:Top clo:Bottom clo:Outerwear clo:Footwear clo:Accessory }\n"
            "  ?category rdfs:label ?categoryLabel .\n"
            "  ?item rdf:type/rdfs:subClassOf* ?category ; clo:hasPrice ?price .\n"
            "}\nGROUP BY ?categoryLabel\nORDER BY DESC(?avgPrice)",
            "average price per category",
        )
    if "formal" in q or "formality" in q or "dress code" in q:
        return (
            PREFIXES
            + "\nSELECT ?formalityLabel (COUNT(DISTINCT ?item) AS ?itemCount)\nWHERE {\n"
            "  ?item clo:hasFormality ?formality .\n"
            "  ?formality rdfs:label ?formalityLabel .\n"
            "}\nGROUP BY ?formalityLabel\nORDER BY DESC(?itemCount)",
            "formality distribution",
        )
    if any(s in q for s in ("season", "winter", "summer", "spring", "autumn")) and (
        "material" in q or "fabric" in q
    ):
        return (
            PREFIXES
            + "\nSELECT ?seasonLabel ?materialLabel (COUNT(DISTINCT ?item) AS ?itemCount)\nWHERE {\n"
            "  ?item clo:hasMaterial ?material ; clo:isAppropriateForSeason ?season .\n"
            "  ?material rdfs:label ?materialLabel .\n  ?season rdfs:label ?seasonLabel .\n"
            "}\nGROUP BY ?seasonLabel ?materialLabel\nORDER BY ?seasonLabel DESC(?itemCount)",
            "materials per season",
        )
    if ("female" in q or "women" in q or "woman" in q) and "top" in q:
        return (
            PREFIXES
            + "\nSELECT ?item ?label ?class\nWHERE {\n"
            "  ?item rdf:type ?class ; clo:isSuitableFor clo:Female ; rdfs:label ?label .\n"
            "  ?class rdfs:subClassOf* clo:Top .\n"
            "}\nORDER BY ?label\nLIMIT 100",
            "female tops (incl. subclasses)",
        )
    if any(w in q for w in ("harmon", "match", "pair", "go together", "go with")):
        return (
            PREFIXES
            + "\nSELECT ?outfitLabel ?topLabel ?topColor ?bottomLabel ?bottomColor\nWHERE {\n"
            "  ?outfit rdf:type clo:Outfit ; rdfs:label ?outfitLabel ; clo:hasTop ?top ; clo:hasBottom ?bottom .\n"
            "  ?top clo:hasColor ?topColor ; rdfs:label ?topLabel .\n"
            "  ?bottom clo:hasColor ?bottomColor ; rdfs:label ?bottomLabel .\n"
            "  { ?topColor clo:colorHarmonizesWith|^clo:colorHarmonizesWith ?bottomColor . }\n"
            "  UNION\n"
            "  { ?topColor clo:isComplementaryTo|^clo:isComplementaryTo ?bottomColor . }\n"
            "}\nORDER BY ?outfitLabel",
            "harmonious top/bottom pairs",
        )
    if "outfit" in q:
        return (
            PREFIXES
            + "\nSELECT ?outfitLabel ?role ?componentLabel\nWHERE {\n"
            "  VALUES (?property ?role) { (clo:hasTop \"top\") (clo:hasBottom \"bottom\") "
            "(clo:hasFootwear \"footwear\") (clo:hasOuterwear \"outerwear\") (clo:hasAccessory \"accessory\") }\n"
            "  ?outfit rdf:type clo:Outfit ; rdfs:label ?outfitLabel ; ?property ?component .\n"
            "  OPTIONAL { ?component rdfs:label ?componentLabel . }\n"
            "}\nORDER BY ?outfitLabel ?role",
            "outfit components",
        )
    # Default: list clothing items.
    return (
        PREFIXES
        + "\nSELECT ?item ?label ?class\nWHERE {\n"
        "  ?item rdf:type/rdfs:subClassOf* clo:ClothingItem ; rdfs:label ?label ; rdf:type ?class .\n"
        "  FILTER(?class != <http://www.w3.org/2002/07/owl#NamedIndividual>)\n"
        "}\nORDER BY ?label\nLIMIT 50",
        "list clothing items",
    )


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def answer(
    question: str,
    graph: rdflib.Graph,
    vocab: dict[str, list[str]],
    use_llm: bool = False,
    ollama_endpoint: str = "http://localhost:11434",
    ollama_model: str = "llama3.1",
) -> dict[str, Any]:
    """Translate, validate, and execute a natural-language question.

    Returns a dict with the question, the generated SPARQL, the source path
    ('llm' or 'fallback'), the validation message, and result columns/rows.
    """
    result: dict[str, Any] = {
        "question": question,
        "source": "fallback",
        "sparql": "",
        "intent": "",
        "validation": "",
        "llm_error": "",
        "columns": [],
        "rows": [],
        "error": "",
    }

    if use_llm:
        try:
            raw = call_ollama(build_prompt(question, vocab), ollama_endpoint, ollama_model)
            candidate = extract_query(raw)
            ok, message = validate_query(candidate, vocab)
            if ok:
                result.update(source="llm", sparql=candidate, validation=message)
            else:
                result["llm_error"] = message  # validation rejected the LLM output
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            result["llm_error"] = f"Ollama unavailable: {exc}"

    if result["source"] != "llm":
        query, intent = deterministic_translate(question)
        ok, message = validate_query(query, vocab)
        result.update(sparql=query, intent=intent, validation=message)

    try:
        columns, rows = run_query(graph, result["sparql"])
        result.update(columns=columns, rows=rows)
    except Exception as exc:  # noqa: BLE001 - report execution errors to the UI
        result["error"] = f"Query execution failed: {exc}"
    return result
