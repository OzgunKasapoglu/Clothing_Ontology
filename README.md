# Clothing Ontology — Outfit Combination Engine

An OWL 2 ontology and knowledge graph for an **outfit-combination engine**. It models
clothing items, their attributes (color, material, size, formality, season, occasion,
gender), color-theory relations, and the higher-level concept of an **Outfit** — a
styled combination of items. The project covers the full Semantic-Web stack: ontology
design, knowledge-graph construction from a real retail dataset, SPARQL querying, SHACL
validation, and **two LLM integrations** (natural-language → SPARQL, and LLM-based ABox
enrichment).

- **GitHub repository:** https://github.com/OzgunKasapoglu/Clothing_Ontology
- **WIDOCO documentation (GitHub Pages):** https://OzgunKasapoglu.github.io/Clothing_Ontology/
  *(see "Hosting the documentation" below to enable Pages)*
- **License:** CC BY 4.0

## Project objective

Outfit choices depend on coherence in color, formality, and season. E-commerce
catalogues store products as flat rows with no machine-readable notion of "what goes
with what." This project captures fashion knowledge in an ontology and a knowledge
graph so that outfit compatibility becomes **queryable and explainable**, and exposes it
through a web app that recommends outfits and answers natural-language questions.

## Dataset sources

- **H&M Personalized Fashion Recommendations** — product metadata
  (`dinhlnd1610/HM-Personalized-Fashion-Recommendations`, `articles` config, via the
  Hugging Face `datasets` library). A stride sample of 2,000 rows is used.
- **Polyvore Outfits** (`owj0421/polyvore-outfits`) — human-curated outfit groupings
  (sample), for future compatibility evaluation.
- **Reused vocabularies:** [schema.org](https://schema.org/) (`:ClothingItem ⊑
  schema:Product`; selected properties `rdfs:subPropertyOf` schema.org),
  [Dublin Core Terms](http://purl.org/dc/terms/), [VANN](http://purl.org/vocab/vann/),
  and [SWRL](http://www.w3.org/2003/11/swrl#).

Raw bulk datasets are **not** committed; only the documented samples under
`data/samples/` are included.

## Installation / setup

```bash
# 1. Create a virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. (Optional) Re-download the dataset samples
python scripts/download_dataset_samples.py

# 3. Build + validate + query the knowledge graph (mock LLM, no API key needed)
python scripts/run_pipeline.py --llm-mode mock

# 4. Launch the web app and open http://127.0.0.1:5000
python app.py
```

The web app provides: a pipeline **Dashboard**, a **Products** browser, the
**Recommendations** outfit engine, and the **Ask (NL→SPARQL)** page.

**Optional local LLM (Ollama).** Install [Ollama](https://ollama.com/), run
`ollama pull llama3.1`, then either run the pipeline with `--llm-mode ollama` or tick
"Use local LLM" on the Ask page. Without Ollama, both features fall back to a
deterministic, vocabulary-grounded path so everything still works offline.

```bash
# Quick checks
python -c "import rdflib; g=rdflib.Graph(); g.parse('Clothing_Ontology.ttl'); print(len(g), 'triples')"
python -m pytest -q                 # run the test suite
python scripts/validate_shacl.py    # SHACL validation
python scripts/run_sparql_queries.py
```

## Repository structure

```
Clothing_Ontology/
├── Clothing_Ontology.ttl        # Canonical ontology (Turtle, OWL 2 + SWRL R1)
├── Clothing_Ontology.rdf        # RDF/XML mirror
├── app.py                       # Flask web app (dashboard, products, recommend, ask)
├── recommend.py                 # Rule-based outfit recommendation engine
├── nl2sparql.py                 # Natural-language → SPARQL (LLM + grounded fallback)
├── requirements.txt
├── shapes/
│   └── clothing_shapes.ttl      # SHACL shapes
├── queries/                     # 10 SPARQL queries (.rq) + README (CQ mapping)
├── scripts/                     # download, ABox generation, LLM enrichment, pipeline,
│                                #   SHACL validation, SPARQL runner
├── prompts/                     # LLM extraction prompt, schema, vocab constraints
├── data/
│   ├── samples/                 # H&M + Polyvore sample data
│   ├── mappings/                # source-value → ontology CSV mappings
│   ├── llm/                     # mock LLM extractions (reproducible fixture)
│   └── generated/               # generated catalogue TTL, SHACL & SPARQL results
├── templates/ , static/         # web app views & styles
├── tests/                       # pytest suite (pipeline, recommender, nl2sparql)
└── docs/
    ├── Final_Report.md          # Project report (course template)
    ├── Specification_v2.md      # Ontology specification (v1→v2 changelog)
    ├── LLM_Integration_Plan.md
    ├── Data_Acquisition_Mapping.csv
    └── widoco/doc/              # WIDOCO-generated HTML documentation
```

## Documentation (WIDOCO)

HTML documentation is generated with [WIDOCO](https://github.com/dgarijo/Widoco) under
`docs/widoco/doc/`. To regenerate (see `docs/Widoco_Instructions.md`):

```bash
java -jar widoco-1.4.25-jar-with-dependencies_JDK-17.jar \
  -ontFile Clothing_Ontology.ttl -outFolder docs/widoco/ \
  -rewriteAll -getOntologyMetadata -webVowl -includeAnnotationProperties -lang en
```

### Hosting the documentation (GitHub Pages)

The repo ships a workflow (`.github/workflows/pages.yml`) that publishes
`docs/widoco/doc/` to GitHub Pages on every push to `main`. To turn it on:
**Settings → Pages → Build and deployment → Source: GitHub Actions.** The docs are then
served at `https://OzgunKasapoglu.github.io/Clothing_Ontology/`.

## Methodology

Modular Ontology Modeling (MOMo) with four modules — **Item, Attribute, Outfit, User**.
See `docs/Final_Report.md` (Ontology Design) and `docs/Specification_v2.md`.
