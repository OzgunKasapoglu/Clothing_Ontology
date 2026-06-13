from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rdflib

PREFIXES = {
    "clo": "http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/",
    "dcterms": "http://purl.org/dc/terms/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
DEFAULT_GRAPHS = [
    Path("Clothing_Ontology.ttl"),
    Path("data/generated/hm_sample_catalog.ttl"),
    Path("data/generated/hm_llm_enriched_catalog.ttl"),
]


def compact(value: Any) -> str:
    text = str(value)
    for prefix, iri in PREFIXES.items():
        if text.startswith(iri):
            return f"{prefix}:{text[len(iri):]}"
    return text


def load_graph(paths: list[Path]) -> rdflib.Graph:
    graph = rdflib.Graph()
    for prefix, iri in PREFIXES.items():
        graph.bind(prefix, iri)
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def run_query(graph: rdflib.Graph, query_path: Path, max_preview_rows: int) -> dict[str, Any]:
    result = graph.query(query_path.read_text(encoding="utf-8"))
    variables = [str(variable) for variable in result.vars]
    rows = [{variable: compact(row[index]) for index, variable in enumerate(variables)} for row in result]
    return {
        "query": str(query_path.as_posix()),
        "variables": variables,
        "row_count": len(rows),
        "preview_rows": rows[:max_preview_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run preliminary SPARQL queries for the Clothing Ontology.")
    parser.add_argument(
        "--graph",
        type=Path,
        action="append",
        default=None,
        help="Turtle graph file. Can be supplied multiple times.",
    )
    parser.add_argument("--query-dir", type=Path, default=Path("queries"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/sparql_results.json"))
    parser.add_argument("--max-preview-rows", type=int, default=10)
    args = parser.parse_args()
    if args.graph is None:
        args.graph = DEFAULT_GRAPHS.copy()
    return args


def run_sparql_queries(
    graph_paths: list[Path] | None = None,
    query_dir: Path = Path("queries"),
    output_path: Path = Path("data/generated/sparql_results.json"),
    max_preview_rows: int = 10,
) -> dict[str, Any]:
    graph_paths = graph_paths or DEFAULT_GRAPHS.copy()
    graph = load_graph(graph_paths)
    query_paths = sorted(query_dir.glob("*.rq"))
    results = [run_query(graph, query_path, max_preview_rows) for query_path in query_paths]

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "graphs": [str(path.as_posix()) for path in graph_paths],
        "triple_count": len(graph),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = run_sparql_queries(
        graph_paths=args.graph,
        query_dir=args.query_dir,
        output_path=args.output,
        max_preview_rows=args.max_preview_rows,
    )

    print(f"Loaded {payload['triple_count']} triples from {len(args.graph)} graph files")
    for result in payload["results"]:
        print(f"{result['query']}: {result['row_count']} rows")
    print(f"Wrote results: {args.output.as_posix()}")


if __name__ == "__main__":
    main()
