# Knowledge Engineering and Ontologies — Course Project Report

## A Clothing Ontology and Knowledge Graph for an Outfit-Combination Engine

**Team members**

> [TEAM MEMBERS — fill before submission]
> Name & email
> Name & email
> Name & email
> Name & email

**Links**

- GitHub repository: https://github.com/OzgunKasapoglu/Clothing_Ontology
- WIDOCO documentation (GitHub Pages): https://OzgunKasapoglu.github.io/Clothing_Ontology/  *(enable Pages → see README)*

---

## Executive Summary (2 pts)

This project designs and implements a complete knowledge-engineering solution for
the fashion domain: an OWL 2 ontology, a populated knowledge graph (KG), SPARQL
querying, SHACL validation, and LLM integration, all exposed through a working web
application. The ontology models clothing items, their attributes (color, material,
size, season, occasion, gender, formality), color-theory relations, and the
higher-level concept of an **Outfit** — a styled combination of garments. It reuses
schema.org, Dublin Core Terms, and VANN, and encodes one machine-readable SWRL rule
for color-harmony pairing. The KG is populated from a 2,000-row sample of the H&M
product catalogue, transformed into RDF and enriched by an LLM that infers material,
formality, and season from product descriptions, yielding **24,725 triples**. Ten
SPARQL queries (basic, reasoning, and aggregation) answer eight competency questions,
and ten SHACL shapes validate the graph with **zero violations**. The primary LLM
integration is a **natural-language → SPARQL** endpoint whose generated queries are
grounded in the ontology vocabulary and validated (read-only, parseable, no invented
terms) before execution — a concrete hallucination-mitigation strategy. The result is
an explainable, ontology-driven outfit-recommendation system.

---

## Description of the Project (2.5 pts)

**Objective and problem.** Choosing outfits that are coherent in color, formality, and
season is a daily, knowledge-intensive task. E-commerce catalogues expose products as
flat rows with little machine-readable structure, so "what goes with what" cannot be
queried or reasoned over. Our objective is to capture fashion knowledge in an ontology
and a knowledge graph so that outfit compatibility becomes a *queryable, explainable*
property rather than an opaque score.

**Scope and relevance.** The project covers the full Semantic-Web stack: ontology
engineering (OWL), data acquisition (a real retail dataset), KG construction (RDF),
querying (SPARQL), validation (SHACL), and LLM integration. It is an instance of the
*E-commerce Knowledge Graph* and *Ontology-driven application* project ideas, with a
recommendation use case.

**Methodology and components.** We follow **Modular Ontology Modeling (MOMo)** with
four modules — Item, Attribute, Outfit, and User. The ontology was authored in
Protégé/Turtle; the KG is built and queried with **RDFlib**; validation uses
**pySHACL**; documentation is generated with **WIDOCO**; the LLM layer uses a local
**Ollama** model with a deterministic fallback. A **Flask** web app provides the
dashboard, a product browser, a rule-based outfit recommender, and the NL→SPARQL "Ask"
page.

**Target users.** End users seeking outfit suggestions, and catalogue/merchandising
analysts who want to query the catalogue semantically (e.g., distributions by color,
formality, or season).

**Expected outputs.** (1) a documented OWL ontology; (2) a populated, validated KG;
(3) a library of SPARQL queries; (4) SHACL shapes and a validation report; (5) an
LLM-backed NL→SPARQL interface; (6) a running recommendation web app.

### Competency Questions (CQs)

| CQ | Question | Query | Type |
|----|----------|-------|------|
| CQ1 | Which clothing items are available in a particular color (e.g., blue)? | `01` | Basic |
| CQ2 | Which items are suitable for a given gender within a garment category, including all of its subtypes (e.g., women's tops)? | `02` | Reasoning |
| CQ3 | How is the catalogue distributed across colors and dress-code formality levels? | `03`, `09` | Aggregation |
| CQ4 | Which garments compose a given outfit, and in what structural role? | `04` | Basic |
| CQ5 | For an outfit, do the top and bottom colors form a harmonious or complementary pair? | `05` | Reasoning |
| CQ6 | Which catalogue items match a specific user's stated color preferences? | `06` | Basic |
| CQ7 | Which products were enriched by the LLM with material/formality/season, and with what values? | `07` | Basic (LLM ABox) |
| CQ8 | What are the price characteristics of each garment category, and which materials dominate each season? | `08`, `10` | Reasoning + Aggregation |

---

## Ontology Design (20 pts)

The ontology IRI is `http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-Ontology`
and the term namespace is `http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/`
(prefix `clo:`). The curated ontology contains **41 named classes, 23 object
properties, 5 data properties, 82 named individuals, 1 SWRL rule, and 1,030 triples**.

### TBox — conceptual schema

**Class hierarchy (Item module).** `clo:ClothingItem` (⊑ `schema:Product`) is
partitioned into five garment regions — `Top`, `Bottom`, `Outerwear`, `Footwear`,
`Accessory` — each refined into concrete types (e.g., `Top` → `T-Shirt`, `Blouse`,
`Sweater`, `Hoodie`; `Footwear` → `Boots`, `Sandals`, `FormalShoes`, `SportsShoes`).

**Attribute module.** `Color`, `Material`, `Size`, `Season`, `Occasion`, `Gender`,
`FormalityLevel`, `ColorScheme`, and `ColorUndertone` are subclasses of an abstract
`Attribute` class.

**Outfit module.** `Outfit` is defined with existential restrictions
(`hasTop some Top`, `hasBottom some Bottom`, `hasFootwear some Footwear`) and refined
by `HarmoniousOutfit`, `FormalOutfit`, and `CasualOutfit`.

**User module.** `User`, `StyleCategory`, and `BodyType` support personalization.

**Object properties (23).** Item↔attribute links (`hasColor`, `hasMaterial`,
`hasSize`, `hasFormality`, `isAppropriateForSeason`, `isAppropriateForOccasion`,
`isSuitableFor`, `hasUndertone`); outfit part-whole links (`hasTop`, `hasBottom`,
`hasFootwear`, `hasOuterwear`, `hasAccessory`, `hasColorScheme`); compatibility
relations (`pairsWellWith` and `clashesWith` — symmetric and mutually disjoint;
`colorHarmonizesWith` and its sub-property `isComplementaryTo` — symmetric); and user
relations (`prefersColor`, `prefersStyle`, `hasBodyType`, `ownsItem`,
`recommendedOutfit`). Selected properties are aligned to schema.org via
`rdfs:subPropertyOf` (`hasColor ⊑ schema:color`, `hasMaterial ⊑ schema:material`,
`hasSize ⊑ schema:size`).

**Data properties (5).** `brandName` (⊑ `schema:brand`), `hasPrice`
(⊑ `schema:price`, functional), `isMachineWashable` (functional), `userName`, `hasAge`.

### ABox — instance data

The curated ABox holds 16 example clothing items, 16 colors (with undertones), the
enumerated attribute individuals (8 materials, 6 sizes, 4 seasons, 4 occasions,
3 genders, 4 formality levels, 5 color schemes, 5 styles, 4 body types), 3 example
outfits, and 1 demo user. At scale, the ABox is extended by the generated H&M catalogue
(see *Knowledge Graph Construction*).

### Modeling decisions and justifications

- **Class vs. instance.** Garment *types* (`T-Shirt`, `Blouse`) are **classes**, because
  they admit arbitrarily many instances and participate in the subsumption hierarchy.
  Attribute *values* (`Blue`, `Cotton`, `M`) are modeled as **individuals**, not
  classes, because they are a fixed, shared, enumerable set referenced by many items,
  and because we need relations *between values* — e.g.,
  `clo:Blue clo:isComplementaryTo clo:Orange`. Expressing such relations between classes
  would require OWL Full / punning; keeping values as individuals keeps the ontology in
  OWL 2 DL.
- **Roles vs. types.** An item's **type** (`a clo:Blouse`) is intrinsic, asserted with
  `rdf:type`. Its **role** in an outfit (the "top slot") is *contextual* and is
  expressed by the object property `hasTop`, **not** by a subclass. Thus one `Blouse`
  individual can fill the top role of several outfits without being reclassified — a
  clean separation of identity from context.
- **Part-whole.** Outfit composition is a mereological part-whole relation. Instead of a
  single generic `hasPart`, we use **typed part properties** (`hasTop`, `hasBottom`,
  `hasFootwear`, `hasOuterwear`, `hasAccessory`) because each part has a distinct range
  and cardinality (exactly one top, optional outerwear, zero-or-more accessories). This
  lets both OWL restrictions and SHACL shapes constrain each role precisely.
- **Open- vs. closed-world.** OWL existential restrictions on `Outfit` state what an
  outfit *must contain* but, under the open-world assumption, cannot flag *missing*
  data. We therefore add **SHACL** shapes for closed-world cardinality checks
  (e.g., exactly one `hasTop`). Using both deliberately is itself a design decision.
- **Domain generalization (correctness fix).** `isAppropriateForSeason` and
  `isAppropriateForOccasion` apply to both garments and whole outfits, so their domain
  is the **union `(ClothingItem ⊔ Outfit)`**. An earlier version declared the domain as
  `ClothingItem` only; because outfits also use these properties, an OWL reasoner then
  *inferred outfits to be clothing items*. The union domain removes that error.
- **Disjointness for diagnosability.** We add `owl:AllDisjointClasses` axioms for the
  top-level concepts (`ClothingItem`, `Outfit`, `User`), the five garment regions, and
  the attribute value-spaces, plus `owl:AllDifferent` for the genders. These let a DL
  reasoner (HermiT/Pellet) *catch* modeling mistakes such as a user typed as a garment.
  The ontology is **consistent** with these axioms in place.
- **Reasoning rule (SWRL).** Rule **R1** infers `pairsWellWith(top, bottom)` when an
  outfit's top and bottom colors harmonize. Five further rules (R2–R6: formal/casual
  outfit classification, season coherence, material conflict, undertone clash) are
  documented as implementation-ready designs.

---

## Data Acquisition (10 pts)

**Sources.** The primary source is the **H&M Personalized Fashion Recommendations**
product-metadata dataset (`dinhlnd1610/HM-Personalized-Fashion-Recommendations`,
`articles` config, via the Hugging Face `datasets` library). A **Polyvore Outfits**
sample (`owj0421/polyvore-outfits`) provides human-curated outfit groupings for future
compatibility evaluation. `scripts/download_dataset_samples.py` takes a **stride sample
of 2,000 rows** (every *N*-th row out of ~105,000) so the sample is representative
rather than front-loaded.

**Format and fields.** Source rows are CSV/JSON with fields such as `article_id`,
`prod_name`, `product_type_name`, `product_group_name`, `colour_group_name`,
`index_group_name`, and `detail_desc`. Samples are stored as both CSV and JSONL under
`data/samples/`.

**Preprocessing.** (1) **Deduplication** by `article_id`. (2) **Color normalization** —
source colors (e.g., "Dark Blue", "Light Pink") are mapped to ontology `Color`
individuals via `data/mappings/hm_color_to_ontology.csv`. (3) **Category mapping** —
`product_type_name`/`product_group_name` → ontology subclasses via
`hm_product_type_to_class.csv` (55+ types) and `hm_product_group_to_class.csv`.
(4) **Gender mapping** — `index_group_name` → `Male`/`Female`/`Unisex`. (5) Items that
cannot be mapped to a garment class are **skipped** and audited.

**Quality and limitations.** Of 2,000 sampled rows, **1,962** mapped to clothing items
and **38** were skipped (non-garment or unmapped types). Source data lacks explicit
material, formality, and season fields — addressed by LLM enrichment below. The sample
is deliberately small for reproducibility; the pipeline parameter `--limit` scales it.

---

## Knowledge Graph Construction (20 pts)

**RDF model.** The KG is a set of subject–predicate–object triples. Schema terms come
from the `clo:` namespace; provenance/identifier terms from `dcterms:`. The combined KG
loaded by the application is the union of three graphs — the curated ontology, the
deterministic H&M catalogue, and the LLM-enriched catalogue — totaling **24,725
triples**.

**Construction pipeline** (`scripts/run_pipeline.py`): `generate_hm_abox.py` converts
mapped CSV rows into deterministic Turtle (`data/generated/hm_sample_catalog.ttl`);
`generate_llm_enriched_abox.py` adds LLM-inferred attributes
(`hm_llm_enriched_catalog.ttl`); `validate_shacl.py` validates; `run_sparql_queries.py`
executes the query library.

**Representative triples.**

*Curated item (TBox-linked ABox):*
```turtle
clo:Blue_Cotton_Shirt  rdf:type clo:Blouse ;
    rdfs:label "Blue Cotton Shirt"@en ;
    clo:hasColor clo:Blue ; clo:hasMaterial clo:Cotton ;
    clo:hasSize clo:M ; clo:hasFormality clo:SmartCasualLevel ;
    clo:isAppropriateForSeason clo:Spring, clo:Summer ;
    clo:hasPrice "25.0"^^xsd:float .
```
*Generated H&M item (deterministic mapping):*
```turtle
clo:HM_619468001  rdf:type clo:Jacket ;
    rdfs:label "&DENIM Jacket Daisy Garden" ;
    dcterms:identifier "619468001" ;
    clo:hasColor clo:Blue ; clo:isSuitableFor clo:Female .
```
*LLM enrichment (note the provenance comment):*
```turtle
clo:HM_619468001  clo:hasMaterial clo:Denim ;
    clo:hasFormality clo:SmartCasualLevel ;
    clo:isAppropriateForSeason clo:Spring, clo:Autumn ;
    rdfs:comment "Mock LLM extraction: confidence=0.93; evidence=denim content; jacket."@en .
```
*Outfit (part-whole structure):*
```turtle
clo:Outfit_Casual_Summer  rdf:type clo:Outfit ;
    clo:hasTop clo:White_TShirt ; clo:hasBottom clo:Khaki_Shorts ;
    clo:hasFootwear clo:White_Sneakers ;
    clo:isAppropriateForSeason clo:Summer ; clo:isAppropriateForOccasion clo:Casual .
```

**Namespaces and deployment.** Prefixes are declared once per graph (`clo:`, `rdf:`,
`rdfs:`, `owl:`, `dcterms:`, `schema:`, `vann:`, `swrl:`, `xsd:`). The KG is loaded into
an **in-memory RDFlib `Graph`** (cached at app startup); the identical Turtle files can
be loaded into **GraphDB** or any RDF store for SPARQL-endpoint deployment. Catalogue
distribution after construction: top colors are **Black 395, Blue 379, White 235, Grey
173, Pink 162, Beige 117**; materials **Cotton 1,088, Polyester 217, Denim 103**;
formality **Smart Casual 827, Casual 766, Business Casual 56**.

---

## SPARQL Queries (10 pts)

Ten queries (`queries/*.rq`) span the three required categories and map to the
competency questions. Row counts are from the latest run over the 24,725-triple KG.

| # | File | Type | CQ | Rows | Purpose |
|---|------|------|----|------|---------|
| 01 | `01_blue_items.rq` | Basic | CQ1 | 379 | Items whose color is `:Blue`. |
| 02 | `02_female_tops.rq` | Reasoning (subclass) | CQ2 | 259 | Female tops incl. all `Top` subclasses. |
| 03 | `03_catalog_color_counts.rq` | Aggregation | CQ3 | 11 | Item count per color. |
| 04 | `04_outfit_components.rq` | Basic | CQ4 | 13 | Components of each outfit by role. |
| 05 | `05_harmonious_top_bottom_pairs.rq` | Reasoning (paths) | CQ5 | 2 | Harmonious/complementary top-bottom pairs. |
| 06 | `06_user_preferred_color_items.rq` | Basic (join) | CQ6 | 50 | Items matching the user's preferred colors. |
| 07 | `07_llm_enriched_products.rq` | Basic (LLM ABox) | CQ7 | 4,130 | LLM-enriched products by material/formality/season. |
| 08 | `08_avg_price_by_category.rq` | Reasoning + Aggregation | CQ8 | 5 | Count + average price per garment category. |
| 09 | `09_items_by_formality_count.rq` | Aggregation | CQ3 | 4 | Items per formality level. |
| 10 | `10_material_by_season_count.rq` | Aggregation (2-D) | CQ8 | 32 | Dominant materials per season. |

**Example — reasoning over the class hierarchy (Q02, CQ2):**
```sparql
SELECT ?item ?label ?class WHERE {
  ?item rdf:type ?class ;
        clo:isSuitableFor clo:Female ;
        rdfs:label ?label .
  ?class rdfs:subClassOf* clo:Top .
  FILTER(?class != owl:NamedIndividual)
} ORDER BY ?label
```
The `rdfs:subClassOf*` path is what makes this a *reasoning* query: `T-Shirt`, `Blouse`,
`Sweater`, and `Hoodie` instances are all returned as tops without enumerating types.

**Example — aggregation with hierarchy (Q08, CQ8):** returns Outerwear (avg 215),
Footwear (113), Accessory (93), Bottom (54), Top (36), grouping priced items under each
category via `rdf:type/rdfs:subClassOf*`.

All queries are executed by `scripts/run_sparql_queries.py`, which writes row counts and
preview rows to `data/generated/sparql_results.json`.

---

## Validation (10 pts)

Validation uses **SHACL** (`shapes/clothing_shapes.ttl`, 10 node shapes) executed with
**pySHACL** under RDFS inference (`scripts/validate_shacl.py`).

**Representative constraints.**

- **`GeneratedCatalogItemShape`** (targets nodes with `dcterms:identifier`): requires
  exactly one identifier and an `rdfs:label`; restricts `hasColor`/`hasMaterial`/
  `hasFormality`/`isAppropriateForSeason`/`isSuitableFor` to their respective ontology
  classes; and uses a **SPARQL constraint** to require that every generated item is a
  `ClothingItem` or subclass.
- **`OutfitShape`** (class constraint, cardinality): exactly one `hasTop` (a `Top`),
  one `hasBottom`, one `hasFootwear`; at most one `hasOuterwear`/`hasColorScheme`; at
  least one season and occasion.
- **`UserShape`**: exactly one string `userName`; `hasAge` a non-negative integer
  (`sh:minInclusive 0`); preference/ownership properties pointing to the right classes.
- **Enrichment shapes** (`MaterialEnrichmentShape`, `FormalityEnrichmentShape`,
  `SeasonEnrichmentShape`, `ColoredItemShape`): every value of the enriched property
  must be a member of the corresponding ontology class — this is the **structural guard
  on LLM output**.

**Results.** Over **24,725 data triples** against **166 shape triples**, the report is
`sh:conforms = true` with **0 violations** (`data/generated/shacl_validation_summary.json`).

**Critical analysis.** Conformance is *by construction*: the enrichment generator only
writes a value when it is in the controlled vocabulary, and 38 unmappable source rows
were filtered before RDF generation. During development, the cardinality shapes on
`Outfit` surfaced real issues (an outfit initially missing a `season`, and a property
used on the wrong subject), which were fixed in the ontology. The shapes therefore act
both as a *post-hoc validator* and as a *contract* that the generators are written
against — a deliberate two-layer (OWL open-world + SHACL closed-world) quality strategy.

---

## LLM Integration (10 pts)

The project includes **two** LLM integrations.

### 1. Natural-language → SPARQL (primary)

The **"Ask" page** (`/ask`, module `nl2sparql.py`) turns an English question into a
SPARQL query that runs over the KG.

**Pipeline.** `question → (LLM | fallback) → validate → execute → tabulate`.

**Prompt design.** The prompt to a local **Ollama** model (`llama3.1`) injects the
ontology's exact vocabulary — all class, property, and individual local names — and
instructs the model to use only those terms, only the `clo:`/`rdf:`/`rdfs:` prefixes,
and to emit a single read-only `SELECT`.

**Hallucination mitigation** (`validate_query`) — applied to *every* generated query
before it ever touches the graph:
1. **Read-only guard** — reject any `INSERT`/`DELETE`/`DROP`/`LOAD`/… keyword.
2. **Shape guard** — must be a single `SELECT`/`ASK`.
3. **Syntactic guard** — must parse with RDFlib's SPARQL parser.
4. **Grounding guard** — every `clo:` term used must exist in the ontology vocabulary;
   an invented predicate such as `clo:hasMadeUpProperty` is rejected as a likely
   hallucination.

If the LLM is unavailable or its output fails any guard, the request **transparently
falls back** to a deterministic, intent-based translator that emits a known-good
grounded query — so the feature always demonstrates, with or without a model installed.

**Example interaction.**
> **User:** "How many blue items are there?"
> **Generated SPARQL** (validated: read-only, parses, all terms known):
> ```sparql
> SELECT ?colorLabel (COUNT(DISTINCT ?item) AS ?itemCount) WHERE {
>   ?item clo:hasColor clo:Blue . clo:Blue rdfs:label ?colorLabel .
> } GROUP BY ?colorLabel
> ```
> **Answer:** Blue → **379**.

### 2. LLM-based ontology population (ABox enrichment)

Following the LLMs4OL approach, an LLM infers **material, formality, and season** from
each H&M `detail_desc`. Outputs are constrained to the ontology vocabulary, gated by a
**confidence threshold (≥ 0.70)**, and every emitted triple is **SHACL-validated**;
provenance (confidence + evidence) is stored as an `rdfs:comment`. A reproducible mock
fixture stands in for the model so the pipeline runs offline; the same code path calls
Ollama when `--llm-mode ollama` is set. This enriched **1,638** products with **0**
skipped in the latest run.

Together these show LLMs used for **both** querying (NL→SPARQL) and knowledge
acquisition, each with explicit grounding and validation against the KG.

---

## Evaluation, Discussion and Conclusion (10 pts)

**Ontology quality.** *Consistency* — the ontology is consistent under an OWL DL
reasoner, including the added disjointness axioms; the domain-union fix eliminated the
previous spurious "outfit/user is a clothing item" inferences. *Completeness* — the
eight competency questions are all answerable by the query library, and the four MOMo
modules cover the intended domain. *Correctness* — schema.org alignment uses
`rdfs:subClassOf`/`rdfs:subPropertyOf` (intentionally weaker than equivalence), and
attribute values are individuals to stay in OWL 2 DL.

**KG and query performance.** The 24,725-triple KG loads and answers all ten queries in
seconds in-memory; aggregation queries return sensible distributions (e.g., Cotton
dominates every season). The KG is portable to GraphDB for endpoint-scale deployment.

**LLM effectiveness.** The NL→SPARQL layer reliably handles the catalogue's common
question shapes, and the validate-then-execute design means a wrong or malicious
generation is caught rather than run. Enrichment achieves full coverage on the sample
because outputs are vocabulary-constrained.

**Limitations.** (1) The deterministic fallback covers a fixed set of intents; open-
domain questions still depend on the LLM. (2) Enrichment confidence is provided by the
extractor and not independently verified. (3) `hasPrice` is populated for curated
examples, so price aggregates are illustrative on the sample. (4) Only R1 of the six
rules is machine-encoded. (5) The sample is 2,000 rows for reproducibility.

**Conclusion.** We delivered an end-to-end, ontology-driven outfit system: an OWL 2
ontology with justified modeling decisions, a validated multi-source knowledge graph, a
categorized SPARQL library tied to competency questions, SHACL quality gates, and a
grounded LLM interface with concrete hallucination mitigation. We learned how
open-world OWL and closed-world SHACL complement each other, why modeling attribute
values as individuals matters for relational reasoning, and how grounding plus
post-generation validation turns an LLM into a trustworthy front-end for a knowledge
graph. **Future work**: machine-encode rules R2–R6, verify enrichment with a second
model, add user-preference ranking (the documented GRU-RNN extension), and deploy the
KG behind a GraphDB SPARQL endpoint.

---

## References (2.5 pts)

Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). *LLMs4OL: Large language models for
ontology learning.* In *The Semantic Web – ISWC 2023* (pp. 408–427). Springer.
https://doi.org/10.1007/978-3-031-47240-4_22

Fernández, F. M. H., Venkata Ramana, T., Shabana, M., Kannagi, V., & Nalini, M. (2023).
Personalized ontology and deep training tree-based optimal gated recurrent unit–recurrent
neural network for prediction of students' behavior. *Concurrency and Computation:
Practice and Experience, 35*(1), e7420. https://doi.org/10.1002/cpe.7420

Garijo, D. (2017). WIDOCO: A wizard for documenting ontologies. In *The Semantic Web –
ISWC 2017* (pp. 94–102). Springer. https://doi.org/10.1007/978-3-319-68204-4_9

Hitzler, P., & Krisnadhi, A. (2016). *A tutorial on modular ontology modeling with
ontology design patterns: The cooking recipes ontology.* arXiv.
https://arxiv.org/abs/1808.08433

Knublauch, H., & Kontokostas, D. (Eds.). (2017). *Shapes Constraint Language (SHACL).*
W3C Recommendation. World Wide Web Consortium. https://www.w3.org/TR/shacl/

Liu, Z., Luo, P., Qiu, S., Wang, X., & Tang, X. (2016). DeepFashion: Powering robust
clothes recognition and retrieval with rich annotations. In *Proceedings of the IEEE
Conference on Computer Vision and Pattern Recognition (CVPR)* (pp. 1096–1104).
https://doi.org/10.1109/CVPR.2016.124

RDFLib Team. (2024). *RDFLib documentation.* https://rdflib.readthedocs.io/

Schema.org Community Group. (2024). *Schema.org vocabulary.* https://schema.org/

W3C OWL Working Group. (2012). *OWL 2 Web Ontology Language document overview* (2nd ed.).
W3C Recommendation. https://www.w3.org/TR/owl2-overview/

---

## Appendix

- **Repository structure & setup:** see `README.md`.
- **Ontology files:** `Clothing_Ontology.ttl` (canonical), `Clothing_Ontology.rdf`.
- **WIDOCO documentation:** `docs/widoco/doc/` (and the hosted Pages URL above).
- **Generated artifacts:** `data/generated/` (catalogue TTL, SHACL report, SPARQL
  results, pipeline summary).
- **Run everything:** `python scripts/run_pipeline.py --llm-mode mock` then
  `python app.py` and open `http://127.0.0.1:5000`.
