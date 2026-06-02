# SPARQL Query Plan

## Purpose

These preliminary queries demonstrate that the ontology and generated H&M sample graph can support retrieval over item attributes, outfit structure, color compatibility, and user preferences.

## Graphs used

- `Clothing_Ontology.ttl` - ontology TBox plus manually modeled examples.
- `data/generated/hm_sample_catalog.ttl` - generated ABox from sampled H&M product metadata.
- `data/generated/hm_llm_enriched_catalog.ttl` - mock LLM-enriched material, formality, and season assertions.

## Queries

| Query | Demonstrates |
|---|---|
| `queries/01_blue_items.rq` | Attribute lookup by normalized ontology color. |
| `queries/02_female_tops.rq` | Class hierarchy lookup using `rdf:type/rdfs:subClassOf*`. |
| `queries/03_catalog_color_counts.rq` | Aggregation over populated catalogue items. |
| `queries/04_outfit_components.rq` | Retrieval of outfit structure from the ontology examples. |
| `queries/05_harmonious_top_bottom_pairs.rq` | Color-harmony compatibility over outfit top/bottom pairs. |
| `queries/06_user_preferred_color_items.rq` | User-preference matching against catalogue items. |
| `queries/07_llm_enriched_products.rq` | Retrieval over mock LLM-inferred material, formality, and season. |

## Run command

```bash
python scripts/run_sparql_queries.py
```

The runner writes machine-readable results to `data/generated/sparql_results.json`.
