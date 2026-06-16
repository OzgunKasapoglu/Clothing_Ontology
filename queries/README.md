# SPARQL Queries

These 10 queries run over the combined graph:

1. `Clothing_Ontology.ttl` (TBox + curated ABox)
2. `data/generated/hm_sample_catalog.ttl` (deterministic H&M ABox)
3. `data/generated/hm_llm_enriched_catalog.ttl` (LLM-enriched ABox)

Each query is tagged with its **type** (basic retrieval / reasoning / aggregation)
and the **competency question (CQ)** it answers. See `docs/Final_Report.md`
section "Description of the Project" for the full CQ list.

| # | File | Type | CQ | Purpose |
|---|------|------|----|---------|
| 01 | `01_blue_items.rq` | Basic retrieval | CQ1 | Items whose normalized color is `:Blue`. |
| 02 | `02_female_tops.rq` | Reasoning (subclass) | CQ2 | Female-suitable tops, including every subclass of `:Top`. |
| 03 | `03_catalog_color_counts.rq` | Aggregation | CQ3 | Item count per ontology color individual. |
| 04 | `04_outfit_components.rq` | Basic retrieval | CQ4 | Component garments of each modeled outfit, by role. |
| 05 | `05_harmonious_top_bottom_pairs.rq` | Reasoning (property paths) | CQ5 | Outfit top/bottom pairs whose colors are harmonious or complementary. |
| 06 | `06_user_preferred_color_items.rq` | Basic retrieval (join) | CQ6 | Items matching the demo user's preferred colors. |
| 07 | `07_llm_enriched_products.rq` | Basic retrieval (LLM ABox) | CQ7 | H&M products enriched with LLM material/formality/season. |
| 08 | `08_avg_price_by_category.rq` | Reasoning + Aggregation | CQ8 | Item count and average price per garment category (via class hierarchy). |
| 09 | `09_items_by_formality_count.rq` | Aggregation | CQ3 | Catalogue distribution across formality levels. |
| 10 | `10_material_by_season_count.rq` | Aggregation (2-D) | CQ8 | Dominant materials per season. |

Run all queries:

```bash
python scripts/run_sparql_queries.py
```

Results (row counts + preview rows) are written to
`data/generated/sparql_results.json`.
