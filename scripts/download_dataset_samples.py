from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests


DATASETS_SERVER = "https://datasets-server.huggingface.co/rows"

DATASET_REQUESTS = {
    "hm_articles": {
        "dataset": "dinhlnd1610/HM-Personalized-Fashion-Recommendations",
        "config": "articles",
        "split": "train",
        "description": "H&M article/product metadata sample",
    },
    "polyvore_outfits": {
        "dataset": "owj0421/polyvore-outfits",
        "config": "disjoint_default",
        "split": "train",
        "description": "Polyvore outfit grouping sample",
    },
}


def fetch_rows(dataset: str, config: str, split: str, offset: int, length: int) -> list[dict[str, Any]]:
    query = urlencode(
        {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )
    response = requests.get(f"{DATASETS_SERVER}?{query}", timeout=60)
    response.raise_for_status()
    payload = response.json()
    return [entry["row"] for entry in payload["rows"]]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized = {
                key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                for key, value in row.items()
            }
            writer.writerow(normalized)


def write_dataset(name: str, rows: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    jsonl_path = output_dir / f"{name}_sample.jsonl"
    csv_path = output_dir / f"{name}_sample.csv"
    write_jsonl(jsonl_path, rows)
    write_csv(csv_path, rows)
    return {
        "name": name,
        "rows": len(rows),
        "jsonl": str(jsonl_path.as_posix()),
        "csv": str(csv_path.as_posix()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download small public samples for the Clothing Ontology project."
    )
    parser.add_argument("--hm-length", type=int, default=100, help="Number of H&M article rows to download.")
    parser.add_argument(
        "--polyvore-length", type=int, default=50, help="Number of Polyvore outfit rows to download."
    )
    parser.add_argument("--offset", type=int, default=0, help="Dataset row offset for both samples.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/samples"),
        help="Directory for sample CSV/JSONL files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    hm_request = DATASET_REQUESTS["hm_articles"]
    hm_rows = fetch_rows(
        hm_request["dataset"],
        hm_request["config"],
        hm_request["split"],
        args.offset,
        args.hm_length,
    )

    polyvore_request = DATASET_REQUESTS["polyvore_outfits"]
    polyvore_rows = fetch_rows(
        polyvore_request["dataset"],
        polyvore_request["config"],
        polyvore_request["split"],
        args.offset,
        args.polyvore_length,
    )

    outputs = [
        write_dataset("hm_articles", hm_rows, args.output_dir),
        write_dataset("polyvore_outfits", polyvore_rows, args.output_dir),
    ]

    metadata = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Hugging Face datasets-server rows API",
        "offset": args.offset,
        "requests": DATASET_REQUESTS,
        "outputs": outputs,
        "note": "Samples are for ontology mapping/prototyping. Do not commit full raw datasets.",
    }
    metadata_path = args.output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for output in outputs:
        print(f"Wrote {output['rows']} rows: {output['jsonl']} and {output['csv']}")
    print(f"Wrote metadata: {metadata_path.as_posix()}")


if __name__ == "__main__":
    main()

