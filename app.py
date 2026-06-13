from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import rdflib
from flask import Flask, abort, redirect, render_template, request, send_file, url_for

from recommend import COLORS, ROLES, get_recommendations, parse_phrase
from scripts.run_pipeline import (
    ARTIFACTS,
    PIPELINE_SUMMARY,
    aggregate_summary,
    artifact_status,
    read_json,
    run_pipeline,
)

app = Flask(__name__)

ROOT = Path(__file__).resolve().parent
CLO = rdflib.Namespace("http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/")
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")
RDFS = rdflib.RDFS
GENERATED_GRAPHS = [
    ROOT / "Clothing_Ontology.ttl",
    ROOT / "data/generated/hm_sample_catalog.ttl",
    ROOT / "data/generated/hm_llm_enriched_catalog.ttl",
]

_graph: rdflib.Graph | None = None

_RECOMMEND_FORMALITIES = [
    ("CasualLevel", "Casual"),
    ("SmartCasualLevel", "Smart Casual"),
    ("BusinessCasualLevel", "Business Casual"),
    ("FormalLevel", "Formal Dress"),
]
_RECOMMEND_SEASONS = ["Spring", "Summer", "Autumn", "Winter"]


def project_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_pipeline_summary() -> dict[str, Any]:
    summary = read_json(project_path(PIPELINE_SUMMARY))
    if summary:
        return summary
    return {
        "ok": None,
        "error": None,
        "finished_at_utc": None,
        "metrics": aggregate_summary(),
        "artifacts": {name: artifact_status(project_path(path)) for name, path in ARTIFACTS.items()},
    }


def _load_graph() -> rdflib.Graph:
    graph = rdflib.Graph()
    for path in GENERATED_GRAPHS:
        if path.exists():
            graph.parse(path, format="turtle")
    return graph


def get_graph() -> rdflib.Graph:
    global _graph
    if _graph is None:
        _graph = _load_graph()
    return _graph


def get_materials(graph: rdflib.Graph) -> list[str]:
    mats: set[str] = set()
    for node in graph.objects(None, CLO.hasMaterial):
        local = str(node).rsplit("/", 1)[-1]
        if local:
            mats.add(local)
    return sorted(mats)


def label_for(graph: rdflib.Graph, value: rdflib.term.Node | None) -> str:
    if value is None:
        return ""
    label = next(graph.objects(value, RDFS.label), None)
    return str(label) if label else str(value).rsplit("/", 1)[-1]


def compact_node(value: rdflib.term.Node | None) -> str:
    if value is None:
        return ""
    text = str(value)
    prefix = str(CLO)
    return text.removeprefix(prefix)


def parse_comment(comment: str) -> dict[str, Any]:
    confidence = None
    evidence = ""
    source = ""
    match = re.search(r"^(.*) extraction: confidence=([0-9.]+); evidence=(.*)\.$", comment)
    if match:
        source = match.group(1)
        confidence = match.group(2)
        evidence = match.group(3)
    return {"source": source, "confidence": confidence, "evidence": evidence}


def get_filter_options(products: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "materials": sorted({product["material"] for product in products if product["material"]}),
        "formalities": sorted({product["formality"] for product in products if product["formality"]}),
        "seasons": sorted({season for product in products for season in product["seasons"] if season}),
    }


def load_products() -> list[dict[str, Any]]:
    graph = get_graph()
    products: dict[str, dict[str, Any]] = {}
    for item in set(graph.subjects(CLO.hasMaterial, None)):
        article_id = next((str(value) for value in graph.objects(item, DCTERMS.identifier)), "")
        if not article_id:
            continue
        comment = next((str(value) for value in graph.objects(item, RDFS.comment) if "extraction:" in str(value)), "")
        parsed_comment = parse_comment(comment)
        products[article_id] = {
            "article_id": article_id,
            "item": compact_node(item),
            "label": label_for(graph, item),
            "material": label_for(graph, next(graph.objects(item, CLO.hasMaterial), None)),
            "formality": label_for(graph, next(graph.objects(item, CLO.hasFormality), None)),
            "seasons": sorted({label_for(graph, season) for season in graph.objects(item, CLO.isAppropriateForSeason)}),
            "confidence": parsed_comment["confidence"],
            "evidence": parsed_comment["evidence"],
            "source": parsed_comment["source"],
            "description": next((str(value) for value in graph.objects(item, DCTERMS.description)), ""),
        }
    return sorted(products.values(), key=lambda product: product["article_id"])


def apply_product_filters(products: list[dict[str, Any]], filters: dict[str, str]) -> list[dict[str, Any]]:
    filtered = products
    material = filters.get("material", "")
    formality = filters.get("formality", "")
    season = filters.get("season", "")
    query = filters.get("q", "").strip().lower()
    if material:
        filtered = [product for product in filtered if product["material"] == material]
    if formality:
        filtered = [product for product in filtered if product["formality"] == formality]
    if season:
        filtered = [product for product in filtered if season in product["seasons"]]
    if query:
        filtered = [
            product
            for product in filtered
            if query in product["article_id"].lower() or query in product["label"].lower()
        ]
    return filtered


@app.get("/")
def dashboard() -> str:
    summary = load_pipeline_summary()
    return render_template("dashboard.html", summary=summary, artifacts=summary.get("artifacts", {}))


@app.post("/run")
def run() -> Any:
    global _graph
    llm_mode = request.form.get("llm_mode", "mock")
    summary = run_pipeline(
        llm_mode=llm_mode,
        ollama_endpoint=request.form.get("ollama_endpoint", "http://localhost:11434"),
        ollama_model=request.form.get("ollama_model", "llama3.1"),
        min_confidence=float(request.form.get("min_confidence", "0.70")),
        limit=int(request.form.get("limit", "100")),
    )
    _graph = None  # invalidate cache so next request re-loads fresh artifacts
    return redirect(url_for("dashboard", status="ok" if summary["ok"] else "failed"))


@app.get("/products")
def products() -> str:
    all_products = load_products()
    filters = {
        "material": request.args.get("material", ""),
        "formality": request.args.get("formality", ""),
        "season": request.args.get("season", ""),
        "q": request.args.get("q", ""),
    }
    filtered_products = apply_product_filters(all_products, filters)
    return render_template(
        "products.html",
        products=filtered_products,
        total_count=len(all_products),
        filters=filters,
        options=get_filter_options(all_products),
    )


@app.get("/skipped")
def skipped() -> str:
    metadata = read_json(ROOT / "data/generated/llm_enrichment_metadata.json")
    skipped_rows = metadata.get("skipped", []) if isinstance(metadata.get("skipped"), list) else []
    return render_template("skipped.html", skipped_rows=skipped_rows, metadata=metadata)


def _recommend_context(graph: rdflib.Graph) -> dict[str, Any]:
    return {
        "colors": COLORS,
        "roles": ROLES,
        "formalities": _RECOMMEND_FORMALITIES,
        "seasons": _RECOMMEND_SEASONS,
        "materials": get_materials(graph),
    }


@app.get("/recommend")
def recommend_get() -> str:
    graph = get_graph()
    return render_template("recommend.html", step="input", **_recommend_context(graph))


@app.post("/recommend")
def recommend_post() -> str:
    graph = get_graph()
    phrase = request.form.get("phrase", "")
    confirmed = request.form.get("confirmed", "")
    ctx = _recommend_context(graph)
    if not confirmed:
        parsed = parse_phrase(phrase)
        return render_template("recommend.html", step="confirm", phrase=phrase, parsed=parsed, **ctx)
    seed = {
        "role": request.form.get("role") or None,
        "color": request.form.get("color") or None,
        "material": request.form.get("material") or None,
        "formality": request.form.get("formality") or None,
        "season": request.form.get("season") or None,
    }
    results = get_recommendations(graph, seed)
    return render_template("recommend.html", step="results", phrase=phrase, seed=seed, results=results, **ctx)


@app.get("/artifacts/<name>")
def artifacts(name: str) -> Any:
    path = ARTIFACTS.get(name)
    if path is None:
        abort(404)
    resolved = project_path(path)
    if not resolved.exists():
        abort(404)
    return send_file(resolved)


@app.template_filter("json_pretty")
def json_pretty(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
