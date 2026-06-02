from __future__ import annotations

import re
from itertools import product as iproduct
from typing import Any

import rdflib
from rdflib import RDF, RDFS, Namespace

CLO = Namespace("http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

COLORS = [
    "Red", "Orange", "Yellow", "Brown", "Blue", "Green", "Purple", "Pink",
    "Black", "White", "Grey", "Beige", "Navy", "Gold", "Silver", "Turquoise",
]

ROLES = ["Top", "Bottom", "Footwear", "Outerwear", "Accessory"]

ROLE_SYNONYMS: dict[str, list[str]] = {
    "Top": ["shirt", "t-shirt", "tee", "blouse", "sweater", "hoodie", "top"],
    "Bottom": ["pants", "trousers", "jeans", "shorts", "skirt", "bottom"],
    "Footwear": ["shoes", "boots", "sandals", "sneakers", "footwear"],
    "Outerwear": ["coat", "jacket", "blazer", "outerwear"],
    "Accessory": ["belt", "watch", "scarf", "hat", "accessory"],
}

COMPLEMENT_ROLES: dict[str, list[str]] = {
    "Top": ["Bottom", "Footwear", "Outerwear", "Accessory"],
    "Bottom": ["Top", "Footwear", "Outerwear", "Accessory"],
    "Footwear": ["Top", "Bottom", "Outerwear", "Accessory"],
    "Outerwear": ["Top", "Bottom", "Footwear", "Accessory"],
    "Accessory": ["Top", "Bottom", "Footwear"],
}

FORMALITY_ORDER = ["CasualLevel", "SmartCasualLevel", "BusinessCasualLevel", "FormalLevel"]

_OPTIONAL_THRESHOLD = 5.0


def parse_phrase(phrase: str) -> dict[str, str | None]:
    lower = phrase.lower()
    role: str | None = None
    color: str | None = None
    for role_name, synonyms in ROLE_SYNONYMS.items():
        for syn in synonyms:
            if re.search(r"\b" + re.escape(syn) + r"\b", lower):
                role = role_name
                break
        if role:
            break
    for c in COLORS:
        if re.search(r"\b" + re.escape(c.lower()) + r"\b", lower):
            color = c
            break
    return {"role": role, "color": color}


def color_harmonizes(graph: rdflib.Graph, c1_local: str, c2_local: str) -> bool:
    c1 = CLO[c1_local]
    c2 = CLO[c2_local]
    for prop in (CLO.colorHarmonizesWith, CLO.isComplementaryTo):
        if (c1, prop, c2) in graph or (c2, prop, c1) in graph:
            return True
    return False


def _get_subclasses(graph: rdflib.Graph, cls: rdflib.URIRef) -> set[rdflib.URIRef]:
    result: set[rdflib.URIRef] = {cls}
    queue = [cls]
    while queue:
        current = queue.pop()
        for sub in graph.subjects(RDFS.subClassOf, current):
            if sub not in result:
                result.add(sub)
                queue.append(sub)
    return result


def _collect_items_by_role(graph: rdflib.Graph) -> dict[str, list[rdflib.URIRef]]:
    items_by_role: dict[str, list[rdflib.URIRef]] = {r: [] for r in ROLES}
    seen: set[rdflib.URIRef] = set()
    for role in ROLES:
        for cls in _get_subclasses(graph, CLO[role]):
            for item in graph.subjects(RDF.type, cls):
                if isinstance(item, rdflib.URIRef) and item not in seen:
                    items_by_role[role].append(item)
                    seen.add(item)
    return items_by_role


def _get_color(graph: rdflib.Graph, item: rdflib.URIRef) -> str | None:
    node = next(graph.objects(item, CLO.hasColor), None)
    return str(node).rsplit("/", 1)[-1] if node else None


def _get_material(graph: rdflib.Graph, item: rdflib.URIRef) -> str | None:
    node = next(graph.objects(item, CLO.hasMaterial), None)
    return str(node).rsplit("/", 1)[-1] if node else None


def _get_formality(graph: rdflib.Graph, item: rdflib.URIRef) -> str | None:
    node = next(graph.objects(item, CLO.hasFormality), None)
    return str(node).rsplit("/", 1)[-1] if node else None


def _get_seasons(graph: rdflib.Graph, item: rdflib.URIRef) -> set[str]:
    return {str(s).rsplit("/", 1)[-1] for s in graph.objects(item, CLO.isAppropriateForSeason)}


def _get_label(graph: rdflib.Graph, item: rdflib.URIRef) -> str:
    label = next(graph.objects(item, RDFS.label), None)
    return str(label) if label else str(item).rsplit("/", 1)[-1]


def _get_article_id(graph: rdflib.Graph, item: rdflib.URIRef) -> str:
    node = next(graph.objects(item, DCTERMS.identifier), None)
    return str(node) if node else ""


def _find_seed_proxies(
    graph: rdflib.Graph, seed_color: str, seed_role: str
) -> set[rdflib.URIRef]:
    color_uri = CLO[seed_color]
    proxies: set[rdflib.URIRef] = set()
    for cls in _get_subclasses(graph, CLO[seed_role]):
        for item in graph.subjects(RDF.type, cls):
            if isinstance(item, rdflib.URIRef) and (item, CLO.hasColor, color_uri) in graph:
                proxies.add(item)
    return proxies


def _score_candidate(
    graph: rdflib.Graph,
    seed: dict[str, Any],
    candidate: rdflib.URIRef,
    seed_proxies: set[rdflib.URIRef],
) -> float | None:
    for proxy in seed_proxies:
        if (proxy, CLO.clashesWith, candidate) in graph or (candidate, CLO.clashesWith, proxy) in graph:
            return None

    seed_color = seed.get("color")
    cand_color = _get_color(graph, candidate)

    if seed_color and cand_color and not color_harmonizes(graph, seed_color, cand_color):
        return None

    score = 0.0

    if seed_color and cand_color:
        score += 10.0

    seed_material = seed.get("material")
    cand_material = _get_material(graph, candidate)
    if seed_material and cand_material and seed_material == cand_material:
        score += 2.0

    seed_formality = seed.get("formality")
    cand_formality = _get_formality(graph, candidate)
    if (
        seed_formality
        and cand_formality
        and seed_formality in FORMALITY_ORDER
        and cand_formality in FORMALITY_ORDER
    ):
        dist = abs(FORMALITY_ORDER.index(seed_formality) - FORMALITY_ORDER.index(cand_formality))
        if dist == 0:
            score += 3.0
        elif dist == 1:
            score += 1.0

    seed_season = seed.get("season")
    cand_seasons = _get_seasons(graph, candidate)
    if seed_season and seed_season in cand_seasons:
        score += 3.0

    return score


def _pairwise_harmony_bonus(graph: rdflib.Graph, items: list[rdflib.URIRef]) -> float:
    colors = [c for c in (_get_color(graph, i) for i in items) if c]
    bonus = 0.0
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            if color_harmonizes(graph, colors[i], colors[j]):
                bonus += 2.0
    return bonus


def get_recommendations(graph: rdflib.Graph, seed: dict[str, Any]) -> dict[str, Any]:
    seed_role = seed.get("role")
    if not seed_role:
        return {"grouped_items": {}, "outfits": []}

    seed_color = seed.get("color")
    seed_proxies = (
        _find_seed_proxies(graph, seed_color, seed_role)
        if seed_color and seed_role
        else set()
    )

    target_roles = COMPLEMENT_ROLES.get(seed_role, [])
    items_by_role = _collect_items_by_role(graph)

    scored_by_role: dict[str, list[tuple[float, rdflib.URIRef]]] = {}
    grouped: dict[str, list[dict]] = {}

    for role in target_roles:
        scored = []
        for item in items_by_role.get(role, []):
            s = _score_candidate(graph, seed, item, seed_proxies)
            if s is not None:
                scored.append((s, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        scored_by_role[role] = scored
        grouped[role] = [
            {
                "label": _get_label(graph, item),
                "color": _get_color(graph, item) or "",
                "material": _get_material(graph, item) or "",
                "formality": _get_formality(graph, item) or "",
                "seasons": sorted(_get_seasons(graph, item)),
                "score": s,
                "local_name": str(item).rsplit("/", 1)[-1],
                "article_id": _get_article_id(graph, item),
            }
            for s, item in scored[:10]
        ]

    outfits = _generate_outfits(graph, seed, seed_role, scored_by_role)
    return {"grouped_items": grouped, "outfits": outfits}


def _generate_outfits(
    graph: rdflib.Graph,
    seed: dict[str, Any],
    seed_role: str,
    scored_by_role: dict[str, list[tuple[float, rdflib.URIRef]]],
) -> list[dict[str, Any]]:
    required = {"Top", "Bottom", "Footwear"}
    target_roles = set(COMPLEMENT_ROLES.get(seed_role, []))
    required_from_rec = sorted(required - {seed_role})
    optional_from_rec = sorted(target_roles - required)

    cand_lists: list[tuple[str, list[tuple[float, rdflib.URIRef]]]] = []
    for role in required_from_rec:
        top3 = scored_by_role.get(role, [])[:3]
        if not top3:
            return []
        cand_lists.append((role, top3))

    seed_label = f"Your {seed.get('color', '')} {seed_role}".strip()
    outfits_raw: list[dict[str, Any]] = []

    for combo in iproduct(*[cands for _, cands in cand_lists]):
        outfit_items: dict[str, dict] = {}
        total_score = 0.0
        real_items: list[rdflib.URIRef] = []

        for (role, _), (s, item) in zip(cand_lists, combo):
            outfit_items[role] = {
                "label": _get_label(graph, item),
                "color": _get_color(graph, item) or "",
                "article_id": _get_article_id(graph, item),
                "is_seed": False,
            }
            total_score += s
            real_items.append(item)

        outfit_items[seed_role] = {
            "label": seed_label,
            "color": seed.get("color") or "",
            "article_id": "",
            "is_seed": True,
        }

        for role in optional_from_rec:
            top_cands = scored_by_role.get(role, [])
            if top_cands and top_cands[0][0] >= _OPTIONAL_THRESHOLD:
                opt_score, opt_item = top_cands[0]
                outfit_items[role] = {
                    "label": _get_label(graph, opt_item),
                    "color": _get_color(graph, opt_item) or "",
                    "article_id": _get_article_id(graph, opt_item),
                    "is_seed": False,
                }
                total_score += opt_score
                real_items.append(opt_item)

        total_score += _pairwise_harmony_bonus(graph, real_items)
        outfits_raw.append({"roles": outfit_items, "total_score": round(total_score, 2)})

    outfits_raw.sort(key=lambda o: o["total_score"], reverse=True)
    return outfits_raw[:10]
