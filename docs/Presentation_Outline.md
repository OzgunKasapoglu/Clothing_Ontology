# Presentation Outline & Narration Script

**Target:** 13 slides, ~10 minutes, all members contribute. Export to PDF/PPTX for
submission. Speaker notes below each slide are written to be read aloud (~45–60 s each).
Map the slides to the rubric criteria shown in brackets.

---

### Slide 1 — Title  *(≈30 s)*
**Content:** Project title "A Clothing Ontology & Knowledge Graph for an Outfit-Combination
Engine"; team members; course; GitHub + WIDOCO URLs.
**Say:** "We built an ontology-driven, explainable outfit-recommendation system. Here are
our repository and documentation links, which we'll demo live at the end."

### Slide 2 — Problem & Motivation  *[Problem Definition]*  *(≈55 s)*
**Content:** Photo of a cluttered wardrobe / product grid. Bullets: outfit choice needs
color + formality + season coherence; e-commerce data is flat rows; "what goes with
what" is not queryable.
**Say:** "Picking an outfit is a knowledge task — colors must harmonize, formality must
match, the season must fit. But catalogues store products as flat rows with no machine
notion of compatibility. Our goal: make outfit compatibility a *queryable, explainable*
property instead of a black-box score."

### Slide 3 — Objectives & Competency Questions  *[Problem Definition]*  *(≈55 s)*
**Content:** The 8 competency questions (condensed) + the tech stack icons (Protégé,
RDFlib, pySHACL, WIDOCO, Ollama, Flask).
**Say:** "We framed the project around eight competency questions — for example, 'which
items are blue?', 'do an outfit's top and bottom colors harmonize?', and 'which
materials dominate each season?'. These drove both the ontology and the SPARQL queries."

### Slide 4 — Ontology Design: structure  *[Ontology Design]*  *(≈70 s)*
**Content:** Class-hierarchy diagram (from WIDOCO/WebVOWL). Four MOMo modules: Item,
Attribute, Outfit, User. Counts: 41 classes, 23 object props, 5 data props.
**Say:** "We used Modular Ontology Modeling with four modules. ClothingItem subclasses
into five garment regions and concrete types. Attributes — color, material, size,
season, formality — are their own module. The Outfit module composes items, and a User
module supports personalization. We reuse schema.org, Dublin Core, and VANN."

### Slide 5 — Ontology Design: key decisions  *[Ontology Design]*  *(≈75 s)*
**Content:** Three decisions side by side: (1) attribute *values as individuals* (so we
can state `Blue isComplementaryTo Orange`); (2) *roles vs. types* (`hasTop` is a role,
`Blouse` is a type); (3) *typed part-whole* + OWL restrictions **and** SHACL.
**Say:** "Three decisions show our modeling rationale. First, colors and materials are
individuals, not classes — that keeps us in OWL 2 DL while letting us relate values, like
complementary colors. Second, we separate an item's *type* from its *role* in an outfit.
Third, we model composition with typed part properties and enforce them with OWL
restrictions for requirements and SHACL for closed-world cardinality."

### Slide 6 — Reasoning & a correctness fix  *[Ontology Design / Technical Understanding]*  *(≈60 s)*
**Content:** SWRL rule R1 (color-harmony → pairsWellWith). The domain-union fix +
disjointness axioms; "reasoner confirms: consistent, no spurious inferences."
**Say:** "We encode a SWRL rule that infers a top and bottom 'pair well' when their
colors harmonize. We also fixed a real modeling bug: the season/occasion properties had
ClothingItem as their domain, so a reasoner wrongly inferred outfits to be garments. We
generalized the domain to ClothingItem-or-Outfit and added disjointness axioms, so the
reasoner now catches that class of mistake."

### Slide 7 — Data Acquisition  *[Knowledge Graph Construction]*  *(≈55 s)*
**Content:** H&M dataset → 2,000-row stride sample; mapping CSVs (color, type, gender);
1,962 mapped / 38 skipped.
**Say:** "We populated the graph from the real H&M product catalogue, taking a spread
2,000-row sample. Mapping tables normalize source colors and product types onto our
ontology terms. 1,962 rows mapped cleanly; 38 non-garment rows were filtered."

### Slide 8 — Knowledge Graph Construction  *[Knowledge Graph Construction]*  *(≈65 s)*
**Content:** Three-graph union diagram (ontology + deterministic H&M + LLM-enriched) =
**24,725 triples**. A sample triple block. Distributions (Black 395, Blue 379…).
**Say:** "The knowledge graph is the union of three Turtle graphs — the ontology, the
deterministic H&M catalogue, and the LLM-enriched catalogue — about 24,700 triples. Here
is a product as triples: its type, color, material, and a provenance comment. It loads
into RDFlib in memory and is portable to GraphDB."

### Slide 9 — SPARQL Queries  *[SPARQL & CQs]*  *(≈70 s)*
**Content:** Table of 10 queries by type (basic / reasoning / aggregation) mapped to CQs.
Show one reasoning query (`subClassOf*` for women's tops) and its result count.
**Say:** "Ten queries cover the three required types and answer our competency questions.
This reasoning query uses a subclass-path so it returns every kind of top — t-shirts,
blouses, sweaters — without listing them. Aggregation queries give distributions like
average price per category and materials per season."

### Slide 10 — Validation with SHACL  *[Validation]*  *(≈60 s)*
**Content:** Shapes list (Outfit cardinality, User, enrichment shapes). Result:
**conforms = true, 0 violations** over 24,725 triples. Note the two-layer OWL+SHACL idea.
**Say:** "Ten SHACL shapes enforce data quality — outfit cardinality, user constraints,
and crucially that every LLM-added value is a real ontology term. The graph conforms with
zero violations. During development these shapes caught genuine errors, like an outfit
missing a season. OWL handles requirements open-world; SHACL handles validation
closed-world."

### Slide 11 — LLM Integration  *[LLM Integration]*  *(≈80 s)*
**Content:** Two integrations. (A) NL→SPARQL pipeline diagram:
question → LLM/fallback → **validate (read-only, parses, grounded)** → execute. (B) LLM
ABox enrichment (vocab-constrained, confidence-gated, SHACL-checked). Highlight
"hallucination mitigation."
**Say:** "We integrate LLMs two ways. The main one turns a natural-language question into
SPARQL. The prompt is constrained to our exact vocabulary, and — this is the key part —
every generated query is validated before it runs: it must be read-only, must parse, and
every term must exist in the ontology. An invented predicate is rejected. If the model is
unavailable, a deterministic grounded translator takes over. Second, an LLM enriches
products with material, formality, and season, gated by confidence and validated by
SHACL."

### Slide 12 — Live Demo  *[Communication / Technical Understanding]*  *(≈90 s)*
**Content:** Screenshots as backup. Demo steps: (1) Ask page — type "How many blue items
are there?" → show generated SPARQL + answer 379; (2) type a question with a nonsense
term to show rejection→fallback; (3) Recommendations page — seed item → outfit cards.
**Say:** "Live: I ask 'how many blue items are there', and you can see the generated,
validated SPARQL and the answer, 379. Now the recommender: I give it a white shirt and it
builds complete, color-harmonious outfits ranked by score."

### Slide 13 — Evaluation, Limitations, Conclusion  *[Discussion / Q&A readiness]*  *(≈70 s)*
**Content:** Strengths (consistent ontology, validated KG, grounded LLM). Limitations
(fallback intent set, unverified enrichment confidence, only R1 encoded, 2k sample).
Future work (encode R2–R6, GraphDB endpoint, preference ranking). Thank-you + links.
**Say:** "In summary: a consistent, documented ontology; a validated 24k-triple graph;
ten CQ-driven queries; and a grounded LLM front-end. Limitations include our fixed
fallback intents and that only one rule is machine-encoded. Future work is to encode the
remaining rules, deploy on a GraphDB endpoint, and add preference-based ranking. Thank
you — questions welcome."

---

## Q&A preparation *(for the "Technical Understanding" rubric criterion)*

- **Why are colors individuals, not classes?** To relate values directly
  (`isComplementaryTo`) and stay in OWL 2 DL; classes would need punning/OWL Full.
- **OWL restrictions vs SHACL?** OWL is open-world (states requirements, can't detect
  *missing* data); SHACL is closed-world (flags missing/extra data). We use both.
- **How do you prevent LLM hallucination?** Vocabulary-constrained prompt + post-
  generation validation (read-only, parseable, every term grounded) + SHACL on enriched
  triples + confidence gating; invalid output is rejected, never executed.
- **Is the ontology consistent?** Yes — verified with an OWL reasoner including the
  disjointness axioms; the domain-union fix removed the earlier spurious inferences.
- **Why MOMo?** The domain splits cleanly into Item/Attribute/Outfit/User modules that
  can be developed and tested independently.
