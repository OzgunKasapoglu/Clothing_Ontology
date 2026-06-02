from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CLO = "http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/"
SKIP_STATUSES = {"skip", "out_of_scope"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as input_file:
        return list(csv.DictReader(input_file))


def load_mapping(path: Path, target_field: str) -> dict[str, dict[str, str]]:
    return {
        row["source_value"]: row
        for row in read_csv(path)
        if row.get("source_value")
    }


def ttl_string(value: str, lang: str | None = None) -> str:
    literal = json.dumps(str(value), ensure_ascii=False)
    return f"{literal}@{lang}" if lang else literal


def local_name(value: str) -> str:
    return value.removeprefix(":")


def item_uri(article_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", str(article_id).strip())
    return f"clo:HM_{normalized}"


def resolve_class(
    row: dict[str, str],
    product_type_map: dict[str, dict[str, str]],
    product_group_map: dict[str, dict[str, str]],
) -> tuple[str | None, dict[str, str] | None, str]:
    product_type = row.get("product_type_name", "")
    type_mapping = product_type_map.get(product_type)
    if type_mapping and type_mapping.get("mapping_status") in SKIP_STATUSES:
        return None, type_mapping, "product_type"
    if type_mapping and type_mapping.get("target_class"):
        return type_mapping["target_class"], type_mapping, "product_type"

    product_group = row.get("product_group_name", "")
    group_mapping = product_group_map.get(product_group)
    if group_mapping and group_mapping.get("mapping_status") in SKIP_STATUSES:
        return None, group_mapping, "product_group"
    if group_mapping and group_mapping.get("target_class"):
        return group_mapping["target_class"], group_mapping, "product_group"

    return None, None, "none"


def add_literal(triples: list[str], predicate: str, value: str, lang: str | None = None) -> None:
    cleaned = str(value).strip()
    if cleaned and cleaned.lower() != "nan":
        triples.append(f"    {predicate} {ttl_string(cleaned, lang)}")


def build_item_triples(
    row: dict[str, str],
    class_target: str,
    class_source: str,
    color_map: dict[str, dict[str, str]],
    gender_map: dict[str, dict[str, str]],
    counters: Counter[str],
) -> list[str]:
    triples = [
        f"{item_uri(row['article_id'])} rdf:type owl:NamedIndividual , clo:{local_name(class_target)}"
    ]
    add_literal(triples, "rdfs:label", row.get("prod_name", ""), "en")
    add_literal(triples, "dcterms:identifier", row.get("article_id", ""))
    add_literal(triples, "dcterms:description", row.get("detail_desc", ""), "en")

    color_value = row.get("colour_group_name", "")
    color_mapping = color_map.get(color_value)
    if color_mapping and color_mapping.get("target_individual"):
        triples.append(f"    clo:hasColor clo:{local_name(color_mapping['target_individual'])}")
        counters[f"color:{color_mapping['mapping_status']}"] += 1
    elif color_value:
        counters["color:unmapped"] += 1

    gender_value = row.get("index_group_name", "")
    gender_mapping = gender_map.get(gender_value)
    if gender_mapping and gender_mapping.get("target_individual"):
        triples.append(f"    clo:isSuitableFor clo:{local_name(gender_mapping['target_individual'])}")
        counters[f"gender:{gender_mapping['mapping_status']}"] += 1
    elif gender_value:
        counters["gender:unmapped"] += 1

    mapping_note = (
        f"Mapped from H&M sample: product_type_name={row.get('product_type_name', '')}; "
        f"product_group_name={row.get('product_group_name', '')}; "
        f"colour_group_name={color_value}; class_source={class_source}."
    )
    triples.append(f"    rdfs:comment {ttl_string(mapping_note, 'en')}")
    return triples


def write_turtle(path: Path, item_blocks: list[list[str]]) -> None:
    header = """@prefix clo: <http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""
    blocks = []
    for triples in item_blocks:
        blocks.append(" ;\n".join(triples) + " .")
    path.write_text(header + "\n\n".join(blocks) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Turtle ABox triples from sampled H&M article metadata.")
    parser.add_argument("--input", type=Path, default=Path("data/samples/hm_articles_sample.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/hm_sample_catalog.ttl"))
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/generated/hm_sample_catalog_metadata.json"),
    )
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument(
        "--product-type-map",
        type=Path,
        default=Path("data/mappings/hm_product_type_to_class.csv"),
    )
    parser.add_argument(
        "--product-group-map",
        type=Path,
        default=Path("data/mappings/hm_product_group_to_class.csv"),
    )
    parser.add_argument("--color-map", type=Path, default=Path("data/mappings/hm_color_to_ontology.csv"))
    parser.add_argument(
        "--gender-map",
        type=Path,
        default=Path("data/mappings/hm_index_group_to_gender.csv"),
    )
    return parser.parse_args()


def generate_hm_abox(
    input_path: Path = Path("data/samples/hm_articles_sample.csv"),
    output_path: Path = Path("data/generated/hm_sample_catalog.ttl"),
    metadata_output: Path = Path("data/generated/hm_sample_catalog_metadata.json"),
    limit: int = 2000,
    product_type_map_path: Path = Path("data/mappings/hm_product_type_to_class.csv"),
    product_group_map_path: Path = Path("data/mappings/hm_product_group_to_class.csv"),
    color_map_path: Path = Path("data/mappings/hm_color_to_ontology.csv"),
    gender_map_path: Path = Path("data/mappings/hm_index_group_to_gender.csv"),
) -> dict[str, Any]:
    rows = read_csv(input_path)[:limit]
    product_type_map = load_mapping(product_type_map_path, "target_class")
    product_group_map = load_mapping(product_group_map_path, "target_class")
    color_map = load_mapping(color_map_path, "target_individual")
    gender_map = load_mapping(gender_map_path, "target_individual")

    counters: Counter[str] = Counter()
    item_blocks: list[list[str]] = []
    skipped: list[dict[str, Any]] = []

    for row in rows:
        class_target, mapping, class_source = resolve_class(row, product_type_map, product_group_map)
        if not class_target:
            skipped.append(
                {
                    "article_id": row.get("article_id"),
                    "prod_name": row.get("prod_name"),
                    "product_type_name": row.get("product_type_name"),
                    "product_group_name": row.get("product_group_name"),
                    "reason": mapping.get("mapping_status") if mapping else "unmapped",
                }
            )
            counters["items:skipped"] += 1
            continue

        counters[f"class:{mapping['mapping_status'] if mapping else 'unmapped'}"] += 1
        counters[f"class_source:{class_source}"] += 1
        item_blocks.append(build_item_triples(row, class_target, class_source, color_map, gender_map, counters))
        counters["items:generated"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_turtle(output_path, item_blocks)

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path.as_posix()),
        "output": str(output_path.as_posix()),
        "rows_read": len(rows),
        "items_generated": counters["items:generated"],
        "items_skipped": counters["items:skipped"],
        "counters": dict(sorted(counters.items())),
        "skipped": skipped,
    }
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    args = parse_args()
    metadata = generate_hm_abox(
        input_path=args.input,
        output_path=args.output,
        metadata_output=args.metadata_output,
        limit=args.limit,
        product_type_map_path=args.product_type_map,
        product_group_map_path=args.product_group_map,
        color_map_path=args.color_map,
        gender_map_path=args.gender_map,
    )

    print(f"Generated {metadata['items_generated']} item individuals in {args.output.as_posix()}")
    print(f"Skipped {metadata['items_skipped']} rows")
    print(f"Wrote metadata: {args.metadata_output.as_posix()}")


if __name__ == "__main__":
    main()
