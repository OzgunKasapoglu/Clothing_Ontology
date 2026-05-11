# Clothing Ontology

OWL 2 ontology for an **outfit combination engine**. Models clothing items, their attributes (color, material, size, formality, season, occasion, gender) and the higher-level concept of an **Outfit** — a styled combination of items — with SWRL rules that encode color-harmony, formality-consistency and season-coherence heuristics.

## Files

| File | Purpose |
|---|---|
| `Clothing_Ontology.ttl` | Canonical ontology (Turtle, OWL 2 + SWRL) |
| `Clothing_Ontology.rdf` | RDF/XML mirror, auto-generated from the Turtle file |
| `docs/Phase2_Report.md` | Phase 2 deliverable report |
| `docs/Specification_v2.md` | Ontology specification document, version 2 (with v1→v2 change log) |
| `docs/Widoco_Instructions.md` | How to regenerate Widoco documentation |
| `docs/widoco/` | Generated HTML documentation (created after running Widoco) |

## Versions

- `v1` — Phase 1 ontology (taxonomy only).
- `v2` — Phase 2: adds Outfit module, User module, color-theory and formality extensions, schema.org alignment, SWRL rules, full `rdfs:label`/`rdfs:comment` annotations.

## Methodology

Modular Ontology Modeling (MOMo): four modules — Item, Attribute, Outfit, User. See `docs/Specification_v2.md` §4.

## Reused vocabularies

- [schema.org](https://schema.org/) — `:ClothingItem ≡ schema:Product` and several equivalent properties.
- [Dublin Core Terms](http://purl.org/dc/terms/) — ontology metadata.
- [VANN](http://purl.org/vocab/vann/) — preferred prefix/URI for documentation tools.
- [SWRL](http://www.w3.org/2003/11/swrl#) — rule encoding.

## Quick checks

Parse with rdflib:

```bash
python -c "import rdflib; g=rdflib.Graph(); g.parse('Clothing_Ontology.ttl', format='turtle'); print(len(g), 'triples')"
```

Open in Protégé to view the SWRL rule R1 and the class hierarchy.

## License

CC BY 4.0
