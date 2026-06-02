# Preliminary SPARQL Queries

These queries are designed to run over the combined graph:

1. `Clothing_Ontology.ttl`
2. `data/generated/hm_sample_catalog.ttl`
3. `data/generated/hm_llm_enriched_catalog.ttl`

## Query list

- `01_blue_items.rq` - retrieves items whose normalized color is `:Blue`.
- `02_female_tops.rq` - retrieves female-suitable tops, including subclasses of `:Top`.
- `03_catalog_color_counts.rq` - counts catalogue items by ontology color individual.
- `04_outfit_components.rq` - lists the manually modeled outfit components in the ontology.
- `05_harmonious_top_bottom_pairs.rq` - finds outfit top/bottom pairs whose colors are asserted as harmonious or complementary.
- `06_user_preferred_color_items.rq` - retrieves items matching the demo user's preferred colors.
- `07_llm_enriched_products.rq` - retrieves H&M products enriched with mock LLM material, formality, and season values.

Run all queries:

```bash
python scripts/run_sparql_queries.py
```
