from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATASET_REQUESTS = {
    "hm_articles": {
        "dataset": "dinhlnd1610/HM-Personalized-Fashion-Recommendations",
        "config": "articles",
        "split": "train",
        "description": "H&M article/product metadata",
        "approximate_size": 105000,
    },
    "polyvore_outfits": {
        "dataset": "owj0421/polyvore-outfits",
        "config": "disjoint_default",
        "split": "train",
        "description": "Polyvore outfit grouping sample",
        "approximate_size": 50000,
    },
}


def fetch_stride(
    dataset_name: str,
    config: str,
    split: str,
    total: int,
    dataset_size: int,
) -> list[dict[str, Any]]:
    """
    Stream the dataset and take every Nth row so the sample is spread
    evenly across the full catalog rather than clustered at the start.
    """
    from datasets import load_dataset  # type: ignore[import]

    stride = max(1, dataset_size // total)
    print(f"  streaming '{dataset_name}' (config={config}), stride={stride} …")

    ds = load_dataset(dataset_name, config, split=split, streaming=True)
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(ds):
        if i % stride == 0:
            rows.append(dict(row))
            if len(rows) % 200 == 0:
                print(f"  … {len(rows)} rows collected (scanned {i + 1})")
        if len(rows) >= total:
            break

    return rows


def fetch_head(
    dataset_name: str,
    config: str,
    split: str,
    total: int,
) -> list[dict[str, Any]]:
    """Fetch the first `total` rows (used for Polyvore which is small)."""
    from datasets import load_dataset  # type: ignore[import]

    ds = load_dataset(dataset_name, config, split=split, streaming=True)
    return [dict(row) for i, row in enumerate(ds) if i < total]


def print_distribution(rows: list[dict[str, Any]]) -> None:
    group_counts: Counter[str] = Counter(r.get("product_group_name", "") for r in rows)
    type_counts: Counter[str] = Counter(r.get("product_type_name", "") for r in rows)
    print("\n  product_group_name:")
    for val, n in group_counts.most_common():
        print(f"    {n:4d}  {val}")
    print("\n  product_type_name (top 25):")
    for val, n in type_counts.most_common(25):
        print(f"    {n:4d}  {val}")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized = {
                k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                for k, v in row.items()
            }
            writer.writerow(normalized)


def write_dataset(name: str, rows: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    jsonl_path = output_dir / f"{name}_sample.jsonl"
    csv_path = output_dir / f"{name}_sample.csv"
    write_jsonl(jsonl_path, rows)
    write_csv(csv_path, rows)
    return {"name": name, "rows": len(rows), "jsonl": str(jsonl_path.as_posix()), "csv": str(csv_path.as_posix())}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download H&M article samples spread evenly across the full dataset."
    )
    parser.add_argument(
        "--hm-length", type=int, default=2000,
        help="Total H&M rows to collect (sampled with stride). Default: 2000.",
    )
    parser.add_argument(
        "--hm-dataset-size", type=int, default=105000,
        help="Approximate total rows in the H&M dataset (used to compute stride). Default: 105000.",
    )
    parser.add_argument(
        "--polyvore-length", type=int, default=50,
        help="Number of Polyvore outfit rows to collect. Default: 50.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/samples"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    req = DATASET_REQUESTS["hm_articles"]
    print(f"Fetching {args.hm_length} H&M articles (stride-sampled from ~{args.hm_dataset_size} rows) …")
    hm_rows = fetch_stride(
        req["dataset"], req["config"], req["split"],
        total=args.hm_length,
        dataset_size=args.hm_dataset_size,
    )
    print(f"\nDistribution of fetched H&M sample ({len(hm_rows)} rows):")
    print_distribution(hm_rows)

    pv_req = DATASET_REQUESTS["polyvore_outfits"]
    print(f"\nFetching {args.polyvore_length} Polyvore outfit rows …")
    try:
        pv_rows = fetch_head(pv_req["dataset"], pv_req["config"], pv_req["split"], args.polyvore_length)
    except Exception as exc:
        print(f"  [warn] Polyvore fetch failed: {exc}")
        pv_rows = []

    outputs = [
        write_dataset("hm_articles", hm_rows, args.output_dir),
        write_dataset("polyvore_outfits", pv_rows, args.output_dir),
    ]

    metadata = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Hugging Face datasets library (streaming stride sample)",
        "hm_length": args.hm_length,
        "hm_dataset_size": args.hm_dataset_size,
        "requests": {k: {kk: vv for kk, vv in v.items() if kk != "approximate_size"} for k, v in DATASET_REQUESTS.items()},
        "outputs": outputs,
        "note": "Samples are for ontology mapping/prototyping. Do not commit full raw datasets.",
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for output in outputs:
        print(f"\nWrote {output['rows']} rows → {output['csv']}")


if __name__ == "__main__":
    main()
