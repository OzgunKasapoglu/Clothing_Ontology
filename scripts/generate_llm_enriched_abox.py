from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rdflib

CLO = "http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/"
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")

ALLOWED_MATERIALS = {
    "Cotton",
    "Wool",
    "Silk",
    "Polyester",
    "Nylon",
    "Denim",
    "Leather",
    "Linen",
}
ALLOWED_FORMALITIES = {
    "CasualLevel",
    "SmartCasualLevel",
    "BusinessCasualLevel",
    "FormalLevel",
}
ALLOWED_SEASONS = {
    "Spring",
    "Summer",
    "Autumn",
    "Winter",
}

FORMALITY_ALIASES = {
    "casual": "CasualLevel",
    "smart casual": "SmartCasualLevel",
    "business casual": "BusinessCasualLevel",
    "formal": "FormalLevel",
    "formal dress": "FormalLevel",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def read_catalog_rows(path: Path, limit: int) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as input_file:
        return list(csv.DictReader(input_file))[:limit]


def load_catalog_article_ids(path: Path) -> set[str]:
    graph = rdflib.Graph()
    graph.parse(path, format="turtle")
    return {str(identifier) for identifier in graph.objects(predicate=DCTERMS.identifier)}


def ttl_string(value: str, lang: str | None = None) -> str:
    literal = json.dumps(str(value), ensure_ascii=False)
    return f"{literal}@{lang}" if lang else literal


def item_uri(article_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", str(article_id).strip())
    return f"clo:HM_{normalized}"


def strip_prefix(value: str) -> str:
    text = str(value).strip()
    for prefix in ("clo:", ":"):
        if text.startswith(prefix):
            return text[len(prefix) :]  # noqa: E203
    if text.startswith(CLO):
        return text[len(CLO) :]  # noqa: E203
    return text


def normalize_value(
    value: Any,
    allowed_values: set[str],
    aliases: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    text = strip_prefix(str(value))
    if not text or text.lower() in {"none", "null", "unknown", "n/a"}:
        return None, None
    if text in allowed_values:
        return text, None

    alias = (aliases or {}).get(text.lower())
    if alias and alias in allowed_values:
        return alias, None

    return None, text


def normalize_seasons(value: Any) -> tuple[list[str], list[str]]:
    values = value if isinstance(value, list) else [value]
    seasons: list[str] = []
    invalid: list[str] = []
    for entry in values:
        season, bad_value = normalize_value(entry, ALLOWED_SEASONS)
        if season and season not in seasons:
            seasons.append(season)
        if bad_value:
            invalid.append(bad_value)
    return seasons, invalid


def confidence_value(record: dict[str, Any]) -> float:
    try:
        return float(record.get("confidence", 0.0))
    except (TypeError, ValueError):
        return 0.0


def skip_record(reason: str, record: dict[str, Any], details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "article_id": record.get("article_id"),
        "reason": reason,
        "confidence": record.get("confidence"),
        "evidence": record.get("evidence"),
    }
    if details:
        payload.update(details)
    return payload


def validate_extraction_shape(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("LLM extraction records must be JSON objects.")
    required = {"article_id", "material", "formality", "season", "confidence", "evidence"}
    missing = sorted(required.difference(record))
    if missing:
        raise ValueError(f"LLM extraction record is missing required fields: {', '.join(missing)}")
    if not isinstance(record.get("season"), list):
        raise ValueError("LLM extraction field 'season' must be a list.")
    try:
        float(record.get("confidence"))
    except (TypeError, ValueError) as exc:
        raise ValueError("LLM extraction field 'confidence' must be numeric.") from exc
    return record


def validate_extraction_records(records: list[Any]) -> list[dict[str, Any]]:
    return [validate_extraction_shape(record) for record in records]


def parse_llm_json(text: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ollama returned invalid JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise ValueError("Ollama response must be a JSON array of extraction records.")
    return validate_extraction_records(payload)


def extract_ollama_response_payload(raw_response: str) -> str:
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ollama API returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("response"), str):
        raise ValueError("Ollama API response did not include a text response.")
    return payload["response"]


def build_ollama_prompt(rows: list[dict[str, str]]) -> str:
    examples = [
        {
            "article_id": row.get("article_id", ""),
            "product_name": row.get("prod_name", ""),
            "description": row.get("detail_desc", ""),
        }
        for row in rows
    ]
    allowed = {
        "materials": sorted(ALLOWED_MATERIALS),
        "formalities": sorted(ALLOWED_FORMALITIES),
        "seasons": sorted(ALLOWED_SEASONS),
    }
    return (
        "Extract ontology attributes from the product records. Return only a JSON array. "
        "Each object must have article_id, material, formality, season, confidence, and evidence. "
        "Use only these vocabulary values: "
        f"{json.dumps(allowed, ensure_ascii=False)}. "
        "Use season as an array of one or more values and confidence as a number from 0 to 1. "
        f"Products: {json.dumps(examples, ensure_ascii=False)}"
    )


def fetch_ollama_extractions(
    sample_input: Path,
    endpoint: str,
    model: str,
    limit: int,
) -> list[dict[str, Any]]:
    rows = read_catalog_rows(sample_input, limit)
    prompt = build_ollama_prompt(rows)
    request_body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/api/generate",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw_response = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama is unavailable at {endpoint}: {exc}") from exc
    return parse_llm_json(extract_ollama_response_payload(raw_response))


def build_enrichment_block(
    record: dict[str, Any],
    material: str,
    formality: str,
    seasons: list[str],
    source_label: str,
) -> list[str]:
    confidence = confidence_value(record)
    evidence = str(record.get("evidence", "")).strip()
    note = f"{source_label} extraction: confidence={confidence:.2f}; evidence={evidence}."
    triples = [
        f"{item_uri(str(record['article_id']))} clo:hasMaterial clo:{material}",
        f"    clo:hasFormality clo:{formality}",
    ]
    triples.extend(f"    clo:isAppropriateForSeason clo:{season}" for season in seasons)
    triples.append(f"    rdfs:comment {ttl_string(note, 'en')}")
    return triples


def write_turtle(path: Path, item_blocks: list[list[str]]) -> None:
    header = """@prefix clo: <http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""
    blocks = []
    for triples in item_blocks:
        blocks.append(" ;\n".join(triples) + " .")
    path.write_text(header + "\n\n".join(blocks) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Turtle ABox triples from LLM H&M extractions.")
    parser.add_argument("--llm-mode", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--mock-input", type=Path, default=Path("data/llm/mock_extractions.jsonl"))
    parser.add_argument("--sample-input", type=Path, default=Path("data/samples/hm_articles_sample.csv"))
    parser.add_argument("--catalog-graph", type=Path, default=Path("data/generated/hm_sample_catalog.ttl"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/hm_llm_enriched_catalog.ttl"))
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/generated/llm_enrichment_metadata.json"),
    )
    parser.add_argument("--min-confidence", type=float, default=0.70)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--ollama-endpoint", default="http://localhost:11434")
    parser.add_argument("--ollama-model", default="llama3.1")
    return parser.parse_args()


def generate_llm_enriched_abox(
    llm_mode: str = "mock",
    mock_input: Path = Path("data/llm/mock_extractions.jsonl"),
    sample_input: Path = Path("data/samples/hm_articles_sample.csv"),
    catalog_graph: Path = Path("data/generated/hm_sample_catalog.ttl"),
    output_path: Path = Path("data/generated/hm_llm_enriched_catalog.ttl"),
    metadata_output: Path = Path("data/generated/llm_enrichment_metadata.json"),
    min_confidence: float = 0.70,
    limit: int = 8,
    ollama_endpoint: str = "http://localhost:11434",
    ollama_model: str = "llama3.1",
) -> dict[str, Any]:
    if llm_mode == "mock":
        records = validate_extraction_records(read_jsonl(mock_input))
        source_label = "Mock LLM"
    elif llm_mode == "ollama":
        records = fetch_ollama_extractions(sample_input, ollama_endpoint, ollama_model, limit)
        source_label = f"Ollama {ollama_model}"
    else:
        raise ValueError(f"Unsupported LLM mode: {llm_mode}")

    catalog_article_ids = load_catalog_article_ids(catalog_graph)
    counters: Counter[str] = Counter()
    item_blocks: list[list[str]] = []
    skipped: list[dict[str, Any]] = []

    for record in records:
        article_id = str(record.get("article_id", "")).strip()
        if not article_id:
            counters["skipped:missing_article_id"] += 1
            skipped.append(skip_record("missing_article_id", record))
            continue

        if article_id not in catalog_article_ids:
            counters["skipped:article_not_in_catalog"] += 1
            skipped.append(skip_record("article_not_in_catalog", record))
            continue

        confidence = confidence_value(record)
        if confidence < min_confidence:
            counters["skipped:low_confidence"] += 1
            skipped.append(
                skip_record(
                    "low_confidence",
                    record,
                    {"min_confidence": min_confidence},
                )
            )
            continue

        material, bad_material = normalize_value(record.get("material"), ALLOWED_MATERIALS)
        formality, bad_formality = normalize_value(
            record.get("formality"),
            ALLOWED_FORMALITIES,
            FORMALITY_ALIASES,
        )
        seasons, bad_seasons = normalize_seasons(record.get("season"))
        invalid_values = {
            "material": bad_material,
            "formality": bad_formality,
            "season": bad_seasons,
        }
        if bad_material or bad_formality or bad_seasons or not material or not formality or not seasons:
            counters["skipped:unknown_ontology_value"] += 1
            skipped.append(
                skip_record(
                    "unknown_ontology_value",
                    record,
                    {"invalid_values": invalid_values},
                )
            )
            continue

        item_blocks.append(build_enrichment_block(record, material, formality, seasons, source_label))
        counters["items:enriched"] += 1
        counters[f"material:{material}"] += 1
        counters[f"formality:{formality}"] += 1
        for season in seasons:
            counters[f"season:{season}"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_turtle(output_path, item_blocks)

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "llm_mode": llm_mode,
        "mock_input": str(mock_input.as_posix()) if llm_mode == "mock" else None,
        "sample_input": str(sample_input.as_posix()),
        "ollama_endpoint": ollama_endpoint if llm_mode == "ollama" else None,
        "ollama_model": ollama_model if llm_mode == "ollama" else None,
        "source_catalog_graph": str(catalog_graph.as_posix()),
        "output": str(output_path.as_posix()),
        "min_confidence": min_confidence,
        "records_read": len(records),
        "mock_records_read": len(records) if llm_mode == "mock" else 0,
        "catalog_items_available": len(catalog_article_ids),
        "enriched_products": counters["items:enriched"],
        "skipped_due_to_low_confidence": counters["skipped:low_confidence"],
        "skipped_due_to_unknown_ontology_value": counters["skipped:unknown_ontology_value"],
        "skipped_due_to_missing_article_id": counters["skipped:missing_article_id"],
        "skipped_due_to_absent_catalog_item": counters["skipped:article_not_in_catalog"],
        "skipped_total": len(skipped),
        "counters": dict(sorted(counters.items())),
        "skipped": skipped,
    }
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    args = parse_args()
    metadata = generate_llm_enriched_abox(
        llm_mode=args.llm_mode,
        mock_input=args.mock_input,
        sample_input=args.sample_input,
        catalog_graph=args.catalog_graph,
        output_path=args.output,
        metadata_output=args.metadata_output,
        min_confidence=args.min_confidence,
        limit=args.limit,
        ollama_endpoint=args.ollama_endpoint,
        ollama_model=args.ollama_model,
    )

    print(f"Generated {metadata['enriched_products']} enriched item blocks in {args.output.as_posix()}")
    print(f"Skipped {metadata['skipped_total']} extraction records")
    print(f"Wrote metadata: {args.metadata_output.as_posix()}")


if __name__ == "__main__":
    main()
