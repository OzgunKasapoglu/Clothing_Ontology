from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import rdflib
from rdflib.namespace import RDF

SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
DEFAULT_GRAPHS = [
    Path("Clothing_Ontology.ttl"),
    Path("data/generated/hm_sample_catalog.ttl"),
    Path("data/generated/hm_llm_enriched_catalog.ttl"),
]


def load_graph(paths: list[Path]) -> rdflib.Graph:
    graph = rdflib.Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SHACL validation for the Clothing Ontology project.")
    parser.add_argument(
        "--graph",
        type=Path,
        action="append",
        default=None,
        help="Turtle graph file to validate. Can be supplied multiple times.",
    )
    parser.add_argument("--shapes", type=Path, default=Path("shapes/clothing_shapes.ttl"))
    parser.add_argument("--report", type=Path, default=Path("data/generated/shacl_validation_report.ttl"))
    parser.add_argument("--summary", type=Path, default=Path("data/generated/shacl_validation_summary.json"))
    parser.add_argument("--inference", default="rdfs", choices=["none", "rdfs", "owlrl", "both"])
    parser.add_argument("--fail-on-violation", action="store_true")
    args = parser.parse_args()
    if args.graph is None:
        args.graph = DEFAULT_GRAPHS.copy()
    return args


def validate_shacl(
    graph_paths: list[Path] | None = None,
    shapes_path: Path = Path("shapes/clothing_shapes.ttl"),
    report_path: Path = Path("data/generated/shacl_validation_report.ttl"),
    summary_path: Path = Path("data/generated/shacl_validation_summary.json"),
    inference: str = "rdfs",
) -> dict[str, object]:
    try:
        from pyshacl import validate
    except ImportError:
        print("pyshacl is not installed. Install it with: python -m pip install pyshacl", file=sys.stderr)
        raise SystemExit(2)

    graph_paths = graph_paths or DEFAULT_GRAPHS.copy()
    data_graph = load_graph(graph_paths)
    shapes_graph = load_graph([shapes_path])

    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference=inference,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        advanced=True,
        js=False,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_graph.serialize(destination=report_path, format="turtle")

    result_count = len(set(report_graph.subjects(RDF.type, SH.ValidationResult)))
    summary = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "graphs": [str(path.as_posix()) for path in graph_paths],
        "shapes": str(shapes_path.as_posix()),
        "inference": inference,
        "data_triples": len(data_graph),
        "shape_triples": len(shapes_graph),
        "conforms": bool(conforms),
        "validation_result_count": result_count,
        "report": str(report_path.as_posix()),
        "report_text": report_text,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    summary = validate_shacl(
        graph_paths=args.graph,
        shapes_path=args.shapes,
        report_path=args.report,
        summary_path=args.summary,
        inference=args.inference,
    )

    print(f"Loaded {summary['data_triples']} data triples")
    print(f"Loaded {summary['shape_triples']} shape triples")
    print(f"Conforms: {summary['conforms']}")
    print(f"Validation results: {summary['validation_result_count']}")
    print(f"Wrote report: {args.report.as_posix()}")
    print(f"Wrote summary: {args.summary.as_posix()}")

    if args.fail_on_violation and not summary["conforms"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
