# SHACL Validation Plan

## Purpose

The SHACL layer validates the populated graph under closed-world assumptions. This complements OWL reasoning: OWL restrictions describe intended semantics, while SHACL checks whether explicit data records are complete and correctly linked.

## Files

- `shapes/clothing_shapes.ttl` - SHACL node and property shapes.
- `scripts/validate_shacl.py` - validation runner using `pyshacl`.
- `data/generated/shacl_validation_report.ttl` - generated SHACL validation report.
- `data/generated/shacl_validation_summary.json` - generated machine-readable validation summary.

## Shapes included

| Shape | Target | Checks |
|---|---|---|
| `clo:GeneratedCatalogItemShape` | generated H&M records with `dcterms:identifier` | label, identifier, clothing-class typing, optional color/gender/material/formality/season ranges |
| `clo:ColoredItemShape` | subjects using `clo:hasColor` | color values are `clo:Color` individuals |
| `clo:MaterialEnrichmentShape` | subjects using `clo:hasMaterial` | material values are `clo:Material` individuals |
| `clo:FormalityEnrichmentShape` | subjects using `clo:hasFormality` | formality values are `clo:FormalityLevel` individuals |
| `clo:SeasonEnrichmentShape` | subjects using `clo:isAppropriateForSeason` | season values are `clo:Season` individuals |
| `clo:OutfitShape` | `clo:Outfit` individuals | required top, bottom, footwear, season, occasion, and valid optional outerwear/accessories |
| `clo:UserShape` | `clo:User` individuals | username, age datatype, preferences, owned items, recommendations |
| `clo:ColorHarmonyShape` | `clo:colorHarmonizesWith` relations | both sides are color individuals |
| `clo:ComplementaryColorShape` | `clo:isComplementaryTo` relations | both sides are color individuals |

## Run command

```bash
python scripts/validate_shacl.py
```

The runner validates the combined graph:

1. `Clothing_Ontology.ttl`
2. `data/generated/hm_sample_catalog.ttl`
3. `data/generated/hm_llm_enriched_catalog.ttl`

It uses RDFS inference so subclass instances such as `:Blouse` can satisfy constraints such as `sh:class clo:Top`.

## Expected result

The current graph should conform. Known dataset-to-ontology gaps such as `Gold`, `Silver`, `Light Turquoise`, underwear, and socks are documented in `docs/Dataset_Mapping_Notes.md`; the generator either maps them conservatively or omits unsafe triples so the validated graph remains internally consistent.
