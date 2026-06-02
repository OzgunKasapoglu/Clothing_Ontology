# LLM Integration Plan

## Purpose

This project uses a reproducible mock LLM integration to demonstrate ontology population from H&M product descriptions without requiring an API key, network access, or a local model runtime. The mocked extraction task is intentionally narrow: infer material, formality, and season from the `detail_desc` field and add only ontology-safe values to the generated catalogue graph.

## Pipeline

1. H&M sample row from `data/samples/hm_articles_sample.csv`.
2. Prompt templates in `prompts/` instruct an LLM to extract ontology-controlled values.
3. Mocked JSONL outputs in `data/llm/mock_extractions.jsonl` stand in for local model responses.
4. `scripts/generate_llm_enriched_abox.py` validates confidence and vocabulary values.
5. Valid outputs become Turtle triples in `data/generated/hm_llm_enriched_catalog.ttl`.
6. SHACL validates the combined ontology, deterministic H&M catalogue, and LLM enrichment graphs.
7. SPARQL queries can retrieve products by inferred material, formality, and season.

## Files

| File | Purpose |
|---|---|
| `prompts/llm_extraction_instruction.md` | Task prompt for local-LLM extraction. |
| `prompts/llm_extraction_schema.json` | Required response schema. |
| `prompts/ontology_vocabulary_constraints.md` | Allowed ontology individuals for extraction. |
| `data/llm/mock_extractions.jsonl` | Reproducible mocked LLM responses. |
| `scripts/generate_llm_enriched_abox.py` | Converts validated mock responses into Turtle. |
| `data/generated/hm_llm_enriched_catalog.ttl` | Generated enrichment triples. |
| `data/generated/llm_enrichment_metadata.json` | Generation summary and skipped-record audit trail. |
| `queries/07_llm_enriched_products.rq` | Retrieves enriched H&M products by material, formality, and season. |

## Run Commands

Generate the deterministic H&M catalogue first:

```bash
python scripts/generate_hm_abox.py
```

Generate the mock LLM enrichment graph:

```bash
python scripts/generate_llm_enriched_abox.py
```

Validate the combined graph:

```bash
python scripts/validate_shacl.py
```

Run all SPARQL queries, including the LLM-enrichment query:

```bash
python scripts/run_sparql_queries.py
```

## Validation Policy

The generator writes triples only when:

- `confidence` is greater than or equal to the configured threshold.
- `material` is one of the modeled `clo:Material` individuals.
- `formality` is one of the modeled `clo:FormalityLevel` individuals.
- every `season` value is one of the modeled `clo:Season` individuals.
- the article exists in the deterministic generated H&M catalogue.

Records with low confidence, unknown ontology values, missing article IDs, or article IDs absent from the deterministic catalogue are skipped and listed in `data/generated/llm_enrichment_metadata.json`.

## Current Scope

This is honest to present as: LLM integration design and mock extraction pipeline implemented; real local model execution is future work.
