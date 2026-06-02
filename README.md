# Clothing Ontology

OWL 2 ontology for an **outfit combination engine**. It models clothing items, their attributes (color, material, size, formality, season, occasion, gender), and the higher-level concept of an **Outfit**, a styled combination of items.

Version 2 includes one machine-readable SWRL rule for color-harmony pairing and documents additional rule designs for formality, season coherence, and conflict detection.

## Files

| File | Purpose |
|---|---|
| `Clothing_Ontology.ttl` | Canonical ontology (Turtle, OWL 2 + SWRL) |
| `Clothing_Ontology.rdf` | RDF/XML mirror of the Turtle file |
| `docs/Phase2_Report.md` | Phase 2 deliverable report |
| `docs/Specification_v2.md` | Ontology specification document, version 2, with v1 to v2 change log |
| `docs/LLM_Integration_Plan.md` | Mock local-LLM integration plan for controlled ABox enrichment |
| `docs/Widoco_Instructions.md` | How to regenerate Widoco documentation |
| `docs/Data_Acquisition_Mapping.csv` | Field-level mapping from external sources to ontology terms |
| `docs/widoco/` | Generated HTML documentation |

## Versions

- `v1` - Phase 1 ontology (taxonomy only).
- `v2` - Phase 2: adds Outfit module, User module, color-theory and formality extensions, schema.org alignment, SWRL R1, documented R2-R6 rule designs, and full `rdfs:label` / `rdfs:comment` annotations.

## Methodology

Modular Ontology Modeling (MOMo): four modules - Item, Attribute, Outfit, User. See `docs/Specification_v2.md` section 4.

## Reused vocabularies

- [schema.org](https://schema.org/) - `:ClothingItem rdfs:subClassOf schema:Product`; selected local properties use `rdfs:subPropertyOf` schema.org properties.
- [Dublin Core Terms](http://purl.org/dc/terms/) - ontology metadata.
- [VANN](http://purl.org/vocab/vann/) - preferred prefix/URI for documentation tools.
- [SWRL](http://www.w3.org/2003/11/swrl#) - machine-readable encoding for rule R1.

## Quick checks

### Browser UI for regular users

Install dependencies, start the local web app, and open `http://127.0.0.1:5000`:

```bash
pip install -r requirements.txt
python app.py
```

The dashboard provides a single default `Run pipeline` action using the mock LLM fixture. Ollama is optional; choose `Run with Ollama` in the dashboard and keep the default endpoint `http://localhost:11434` and model `llama3.1`, or edit them for your local setup.

Parse with rdflib if available:

```bash
python -c "import rdflib; g=rdflib.Graph(); g.parse('Clothing_Ontology.ttl', format='turtle'); print(len(g), 'triples')"
```

Open in Protege to view the class hierarchy, the R1 SWRL rule, and the documented R2-R6 rule designs.

Generate and validate the H&M sample catalogue plus mock LLM enrichment:

```bash
python scripts/run_pipeline.py --llm-mode mock
```

The generated artifacts are written under `data/generated/`, including `pipeline_summary.json`, SHACL validation output, SPARQL results, and enrichment metadata.

## License

CC BY 4.0
