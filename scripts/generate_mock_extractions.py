"""
Generate mock LLM extraction records for the H&M sample catalog.

Assigns material, formality, and season using keyword heuristics on the
product description and product type. Re-run whenever hm_articles_sample.csv
changes to keep mock_extractions.jsonl in sync with the catalog.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

# ── material heuristics ─────────────────────────────────────────────────────
# Checked in order; first match wins.
_MATERIAL_KEYWORDS: list[tuple[list[str], str, float]] = [
    (["leather"], "Leather", 0.92),
    (["silk", "satin", "chiffon"], "Silk", 0.90),
    (["linen"], "Linen", 0.91),
    (["denim", "washed denim"], "Denim", 0.93),
    (["merino", "cashmere"], "Wool", 0.94),
    (["wool", "felted wool", "knit wool"], "Wool", 0.91),
    (["nylon", "polyamide"], "Nylon", 0.89),
    (
        ["polyester", "recycled polyester", "functional fabric", "fleece", "sweatshirt fabric", "microfibre"],
        "Polyester",
        0.88,
    ),
    (["organic cotton", "cotton blend", "cotton jersey", "cotton weave", "cotton"], "Cotton", 0.91),
]

_DEFAULT_MATERIAL = ("Cotton", 0.78)

# ── formality by product type ────────────────────────────────────────────────
_FORMALITY_BY_TYPE: dict[str, str] = {
    "T-shirt": "CasualLevel",
    "Hoodie": "CasualLevel",
    "Shorts": "CasualLevel",
    "Sneakers": "CasualLevel",
    "Trainers": "CasualLevel",
    "Sweater": "CasualLevel",
    "Cardigan": "SmartCasualLevel",
    "Top": "CasualLevel",
    "Vest top": "CasualLevel",
    "Bodysuit": "CasualLevel",
    "Leggings/Tights": "CasualLevel",
    "Sandals": "CasualLevel",
    "Other shoe": "SmartCasualLevel",
    "Slippers": "CasualLevel",
    "Dress": "SmartCasualLevel",
    "Skirt": "SmartCasualLevel",
    "Blouse": "SmartCasualLevel",
    "Shirt": "SmartCasualLevel",
    "Polo shirt": "SmartCasualLevel",
    "Trousers": "SmartCasualLevel",
    "Jacket": "SmartCasualLevel",
    "Coat": "SmartCasualLevel",
    "Boots": "SmartCasualLevel",
    "Flat shoe": "SmartCasualLevel",
    "Ballerinas": "SmartCasualLevel",
    "Loafers": "SmartCasualLevel",
    "Dungarees": "CasualLevel",
    "Blazer": "BusinessCasualLevel",
    "Waistcoat": "BusinessCasualLevel",
    "Outdoor Waistcoat": "SmartCasualLevel",
    "Pumps": "BusinessCasualLevel",
    "Heeled sandals": "BusinessCasualLevel",
    "Wedge": "BusinessCasualLevel",
    "Tie": "BusinessCasualLevel",
    "Hat/beanie": "CasualLevel",
    "Hat/brim": "SmartCasualLevel",
    "Cap/peaked": "CasualLevel",
    "Scarf": "SmartCasualLevel",
    "Belt": "SmartCasualLevel",
    "Watch": "SmartCasualLevel",
}

_DEFAULT_FORMALITY = "CasualLevel"

# ── season by product type ────────────────────────────────────────────────────
_SEASON_BY_TYPE: dict[str, list[str]] = {
    "T-shirt": ["Spring", "Summer", "Autumn"],
    "Shorts": ["Summer"],
    "Sneakers": ["Spring", "Summer", "Autumn"],
    "Trainers": ["Spring", "Summer", "Autumn"],
    "Sandals": ["Summer"],
    "Slippers": ["Autumn", "Winter"],
    "Heeled sandals": ["Spring", "Summer"],
    "Coat": ["Autumn", "Winter"],
    "Hoodie": ["Autumn", "Winter"],
    "Sweater": ["Autumn", "Winter"],
    "Cardigan": ["Spring", "Autumn", "Winter"],
    "Jacket": ["Spring", "Autumn"],
    "Blazer": ["Spring", "Summer", "Autumn"],
    "Waistcoat": ["Spring", "Autumn"],
    "Outdoor Waistcoat": ["Autumn", "Winter"],
    "Boots": ["Autumn", "Winter"],
    "Flat shoe": ["Spring", "Summer", "Autumn"],
    "Pumps": ["Spring", "Summer", "Autumn"],
    "Ballerinas": ["Spring", "Summer", "Autumn"],
    "Loafers": ["Spring", "Summer", "Autumn"],
    "Wedge": ["Spring", "Summer"],
    "Skirt": ["Spring", "Summer"],
    "Dress": ["Spring", "Summer"],
    "Blouse": ["Spring", "Summer", "Autumn"],
    "Shirt": ["Spring", "Summer", "Autumn"],
    "Polo shirt": ["Spring", "Summer", "Autumn"],
    "Top": ["Spring", "Summer"],
    "Vest top": ["Spring", "Summer"],
    "Bodysuit": ["Spring", "Summer", "Autumn"],
    "Trousers": ["Spring", "Summer", "Autumn", "Winter"],
    "Dungarees": ["Spring", "Summer"],
    "Scarf": ["Autumn", "Winter"],
    "Hat/beanie": ["Autumn", "Winter"],
    "Hat/brim": ["Spring", "Summer"],
    "Cap/peaked": ["Spring", "Summer"],
    "Belt": ["Spring", "Summer", "Autumn", "Winter"],
    "Watch": ["Spring", "Summer", "Autumn", "Winter"],
    "Tie": ["Spring", "Summer", "Autumn", "Winter"],
}

_DEFAULT_SEASONS = ["Spring", "Summer", "Autumn"]

# Product types to skip entirely (out of scope for outfit recommendations)
_SKIP_TYPES = {
    "Bra",
    "Underwear Tights",
    "Socks",
    "Pyjama jumpsuit/playsuit",
    "Underwear bottom",
    "Underwear body",
    "Underwear set",
    "Kids Underwear top",
    "Long John",
    "Nipple covers",
    "Pyjama set",
    "Pyjama bottom",
    "Pyjama top",
    "Night gown",
    "Robe",
    "Sleeping sack",
    "Swimwear",
    "Swimwear bottom",
    "Swimwear top",
    "Swimwear set",
    "Swimsuit",
    "Bikini top",
    "Bikini bottom",
    "Sarong",
    "Bag",
    "Wallet",
    "Sunglasses",
    "Costumes",
    "Fine cosmetics",
    "Giftbox",
    "Garment Set",
    "Hair clip",
    "Hair string",
    "Hair/alice band",
    "Hair ties",
    "Other accessories",
    "Earring",
    "Necklace",
    "Bracelet",
    "Ring",
    "Gloves",
    "Unknown",
}


def _guess_material(desc: str) -> tuple[str, float, str]:
    lower = desc.lower()
    for keywords, material, confidence in _MATERIAL_KEYWORDS:
        for kw in keywords:
            if kw in lower:
                return material, confidence, kw
    return _DEFAULT_MATERIAL[0], _DEFAULT_MATERIAL[1], "general textile"


def _guess_formality(product_type: str, desc: str) -> str:
    if product_type in _FORMALITY_BY_TYPE:
        return _FORMALITY_BY_TYPE[product_type]
    lower = desc.lower()
    if any(w in lower for w in ["formal", "office", "suit", "tuxedo"]):
        return "BusinessCasualLevel"
    if any(w in lower for w in ["casual", "relaxed", "everyday"]):
        return "CasualLevel"
    return _DEFAULT_FORMALITY


def _guess_seasons(product_type: str, desc: str) -> list[str]:
    if product_type in _SEASON_BY_TYPE:
        return _SEASON_BY_TYPE[product_type]
    lower = desc.lower()
    if any(w in lower for w in ["summer", "beach", "swim"]):
        return ["Summer"]
    if any(w in lower for w in ["winter", "padded", "warm", "fleece", "lined"]):
        return ["Autumn", "Winter"]
    if any(w in lower for w in ["spring"]):
        return ["Spring", "Summer"]
    return _DEFAULT_SEASONS


def generate_record(row: dict[str, str]) -> dict[str, Any] | None:
    product_type = row.get("product_type_name", "").strip()
    if product_type in _SKIP_TYPES:
        return None

    article_id = row.get("article_id", "").strip()
    if not article_id:
        return None

    desc = row.get("detail_desc", "") or ""
    material, confidence, evidence_kw = _guess_material(desc)
    formality = _guess_formality(product_type, desc)
    seasons = _guess_seasons(product_type, desc)
    evidence = f"{evidence_kw} content; {product_type.lower()}"

    return {
        "article_id": article_id,
        "material": material,
        "formality": formality,
        "season": seasons,
        "confidence": round(confidence, 2),
        "evidence": evidence,
    }


def generate_mock_extractions(
    sample_input: Path = Path("data/samples/hm_articles_sample.csv"),
    output: Path = Path("data/llm/mock_extractions.jsonl"),
) -> int:
    with sample_input.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    records = [r for row in rows if (r := generate_record(row)) is not None]

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mock LLM extraction records from the H&M sample CSV.")
    parser.add_argument("--sample-input", type=Path, default=Path("data/samples/hm_articles_sample.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/llm/mock_extractions.jsonl"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = generate_mock_extractions(args.sample_input, args.output)
    print(f"Wrote {count} mock extraction records to {args.output}")


if __name__ == "__main__":
    main()
