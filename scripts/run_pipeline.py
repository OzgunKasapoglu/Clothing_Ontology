from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_hm_abox import generate_hm_abox
from scripts.generate_llm_enriched_abox import generate_llm_enriched_abox
from scripts.run_sparql_queries import run_sparql_queries
from scripts.validate_shacl import validate_shacl


GENERATED_DIR = Path("data/generated")
PIPELINE_SUMMARY = GENERATED_DIR / "pipeline_summary.json"
ARTIFACTS = {
    "hm_sample_catalog.ttl": GENERATED_DIR / "hm_sample_catalog.ttl",
    "hm_llm_enriched_catalog.ttl": GENERATED_DIR / "hm_llm_enriched_catalog.ttl",
    "llm_enrichment_metadata.json": GENERATED_DIR / "llm_enrichment_metadata.json",
    "shacl_validation_summary.json": GENERATED_DIR / "shacl_validation_summary.json",
    "sparql_results.json": GENERATED_DIR / "sparql_results.json",
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def artifact_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path.as_posix()), "exists": False, "size_bytes": 0, "modified_at_utc": None}
    stat = path.stat()
    return {
        "path": str(path.as_posix()),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }


def aggregate_summary(
    hm_metadata: dict[str, Any] | None = None,
    enrichment_metadata: dict[str, Any] | None = None,
    shacl_summary: dict[str, Any] | None = None,
    sparql_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    hm_metadata = hm_metadata if hm_metadata is not None else read_json(GENERATED_DIR / "hm_sample_catalog_metadata.json")
    enrichment_metadata = (
        enrichment_metadata if enrichment_metadata is not None else read_json(GENERATED_DIR / "llm_enrichment_metadata.json")
    )
    shacl_summary = shacl_summary if shacl_summary is not None else read_json(GENERATED_DIR / "shacl_validation_summary.json")
    sparql_results = sparql_results if sparql_results is not None else read_json(GENERATED_DIR / "sparql_results.json")
    counters = enrichment_metadata.get("counters", {})
    sparql_rows = {
        Path(result.get("query", "")).name: result.get("row_count", 0)
        for result in sparql_results.get("results", [])
        if isinstance(result, dict)
    }
    return {
        "hm_items_generated": hm_metadata.get("items_generated", 0),
        "hm_items_skipped": hm_metadata.get("items_skipped", 0),
        "enriched_products": enrichment_metadata.get("enriched_products", 0),
        "skipped_due_to_low_confidence": enrichment_metadata.get("skipped_due_to_low_confidence", 0),
        "skipped_due_to_unknown_ontology_value": enrichment_metadata.get(
            "skipped_due_to_unknown_ontology_value", 0
        ),
        "skipped_due_to_missing_article_id": enrichment_metadata.get("skipped_due_to_missing_article_id", 0),
        "skipped_due_to_absent_catalog_item": enrichment_metadata.get("skipped_due_to_absent_catalog_item", 0),
        "skipped_total": enrichment_metadata.get("skipped_total", 0),
        "material_counts": {
            key.removeprefix("material:"): value for key, value in counters.items() if key.startswith("material:")
        },
        "formality_counts": {
            key.removeprefix("formality:"): value for key, value in counters.items() if key.startswith("formality:")
        },
        "season_counts": {
            key.removeprefix("season:"): value for key, value in counters.items() if key.startswith("season:")
        },
        "shacl_conforms": shacl_summary.get("conforms"),
        "validation_result_count": shacl_summary.get("validation_result_count"),
        "sparql_query_row_counts": sparql_rows,
    }


def write_pipeline_summary(summary: dict[str, Any], output_path: Path = PIPELINE_SUMMARY) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_pipeline(
    llm_mode: str = "mock",
    ollama_endpoint: str = "http://localhost:11434",
    ollama_model: str = "llama3.1",
    min_confidence: float = 0.70,
    limit: int = 100,
    enrichment_limit: int | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    stages: list[dict[str, Any]] = []
    hm_metadata: dict[str, Any] = {}
    enrichment_metadata: dict[str, Any] = {}
    shacl_summary: dict[str, Any] = {}
    sparql_results: dict[str, Any] = {}
    ok = False
    error: str | None = None

    try:
        hm_metadata = generate_hm_abox(limit=limit)
        stages.append({"name": "hm_abox", "ok": True})

        enrichment_metadata = generate_llm_enriched_abox(
            llm_mode=llm_mode,
            min_confidence=min_confidence,
            limit=enrichment_limit or min(limit, 25),
            ollama_endpoint=ollama_endpoint,
            ollama_model=ollama_model,
        )
        stages.append({"name": "llm_enrichment", "ok": True})

        shacl_summary = validate_shacl()
        stages.append({"name": "shacl_validation", "ok": bool(shacl_summary.get("conforms"))})
        if not shacl_summary.get("conforms"):
            raise RuntimeError("SHACL validation did not conform.")

        sparql_results = run_sparql_queries()
        stages.append({"name": "sparql_queries", "ok": True})
        ok = True
    except Exception as exc:
        error = str(exc)
        if not stages or stages[-1].get("ok"):
            stages.append({"name": "failed", "ok": False, "error": error})

    summary = {
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "error": error,
        "options": {
            "llm_mode": llm_mode,
            "ollama_endpoint": ollama_endpoint if llm_mode == "ollama" else None,
            "ollama_model": ollama_model if llm_mode == "ollama" else None,
            "min_confidence": min_confidence,
            "limit": limit,
        },
        "stages": stages,
        "metrics": aggregate_summary(hm_metadata, enrichment_metadata, shacl_summary, sparql_results),
        "artifacts": {name: artifact_status(path) for name, path in ARTIFACTS.items()},
    }
    write_pipeline_summary(summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full Clothing Ontology population pipeline.")
    parser.add_argument("--llm-mode", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--ollama-endpoint", default="http://localhost:11434")
    parser.add_argument("--ollama-model", default="llama3.1")
    parser.add_argument("--min-confidence", type=float, default=0.70)
    parser.add_argument("--limit", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_pipeline(
        llm_mode=args.llm_mode,
        ollama_endpoint=args.ollama_endpoint,
        ollama_model=args.ollama_model,
        min_confidence=args.min_confidence,
        limit=args.limit,
    )
    print(json.dumps(summary["metrics"], indent=2, ensure_ascii=False))
    if not summary["ok"]:
        print(f"Pipeline failed: {summary['error']}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
