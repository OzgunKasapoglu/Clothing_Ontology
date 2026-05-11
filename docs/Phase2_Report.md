# Phase 2 Report — Clothing Ontology for an Outfit Combination Engine

**Project:** Clothing Ontology
**Phase:** 2
**Ontology version:** v2
**Author:** g911
**Date:** 2026-05-11
**Repository:** https://github.com/g911/Clothing_Ontology (replace with the actual URL)

---

## 1. Project Summary

The project develops an OWL 2 ontology that models clothing items together with their attributes (color, material, size, season, occasion, gender, formality) and the higher-level concept of an **Outfit** — a styled combination of items. Phase 2 extends the Phase 1 taxonomy so that the ontology can support a rule-based **outfit combination engine**: given a starting item or a user context, the engine reasons over color theory, formality consistency, season coherence, and personal preference to recommend harmonious outfits.

Phase 2 also formalises the road-map for **ontology population** from external clothing data (Polyvore, DeepFashion, retailer product feeds) using a Large-Language-Model assisted pipeline inspired by the LLMs4OL methodology.

---

## 2. Research Integration (Item 1)

### 2.1 Selected Study

**Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). *LLMs4OL: Large Language Models for Ontology Learning.* International Semantic Web Conference (ISWC 2023).**

### 2.2 Why This Study Was Selected

Phase 1 produced a small ontology that was populated entirely by hand. Scaling the outfit-recommendation use case requires *hundreds* of clothing-item individuals with full attribute coverage. Manual curation does not scale; classical NLP rule extractors are brittle on free-text product descriptions ("95 % cotton / 5 % elastane regular-fit oxford shirt with mother-of-pearl buttons"). LLMs4OL is the most directly relevant recent study because it formalises an evaluation framework for using LLMs in three ontology-learning sub-tasks — term typing, taxonomy discovery, and non-taxonomic relation extraction — exactly the sub-tasks needed to turn a retailer product page into a `:ClothingItem` instance with `:hasColor`, `:hasMaterial`, `:hasFormality`, `:isAppropriateForSeason` triples.

### 2.3 Relevance to the Project

The Phase-2 ontology defines the *target schema*. LLMs4OL provides a *method* for mapping unstructured product text onto that schema. The fit is one-to-one:

| LLMs4OL sub-task | Phase-2 ontology role |
|---|---|
| Term typing (assign a concept to a term) | Decide whether a scraped product is a `:T-Shirt`, `:Blouse`, `:Hoodie`, etc. |
| Taxonomy discovery | Validate that the subclass hierarchy in v2 still covers the real-world catalogue; flag novel sub-categories |
| Non-taxonomic relation extraction | Populate `:hasColor`, `:hasMaterial`, `:hasFormality`, `:isAppropriateForSeason`, `:brandName`, `:hasPrice` |

### 2.4 Integration Point in the System Architecture

The study is integrated as the **Population Layer** of the four-layer architecture:

```
┌────────────────────────────────────────────────────────┐
│  Layer 4 — Recommendation Engine                       │
│  SPARQL queries + SWRL rules → Outfit individuals      │
└──────────────────────────▲─────────────────────────────┘
                           │
┌──────────────────────────┴─────────────────────────────┐
│  Layer 3 — Reasoning Layer                             │
│  Pellet / HermiT-SWRL: classify Outfit subtypes,       │
│  infer pairsWellWith / clashesWith                     │
└──────────────────────────▲─────────────────────────────┘
                           │
┌──────────────────────────┴─────────────────────────────┐
│  Layer 2 — Ontology (v2)                               │
│  Item · Attribute · Outfit · User modules (MOMo)       │
└──────────────────────────▲─────────────────────────────┘
                           │
┌──────────────────────────┴─────────────────────────────┐
│  Layer 1 — Population Layer  (LLMs4OL-inspired)        │
│  Scraped/raw text  →  LLM with schema-aware prompt     │
│                    →  Turtle individuals  →  SHACL     │
│                       validation  →  merged ontology   │
└────────────────────────────────────────────────────────┘
```

Concretely, the population pipeline planned for Phase 3 is:

1. **Acquire** product records from Polyvore, DeepFashion and a small retailer scrape (see §4).
2. **Prompt** an LLM (Claude / GPT-class) with the ontology TBox serialised as Turtle, instructing the model to emit valid Turtle ABox triples for each product.
3. **Validate** the emitted Turtle with SHACL shapes that enforce range constraints (e.g. `:hasColor` must point to a known `:Color` individual).
4. **Merge** validated triples into `Clothing_Ontology.ttl`.
5. **Reason** with Pellet to catch logical inconsistencies introduced by the LLM (e.g. an item declared both `:Silk` and `:Sport`-suited would fire SWRL rule R5 and be flagged for review).

This integration directly closes the scalability gap noted at the start of §2.

---

## 3. Mandatory Paper Review (Item 2)

**Paper:** *Personalized Ontology and Deep Training Tree-Based Optimal GRU-RNN for Prediction of Students' Behavior.*

### 3.1 Core Methodology

The paper proposes a hybrid neuro-symbolic architecture for predicting student behavioural outcomes (engagement, drop-out risk, performance). The pipeline has four stages:

1. **Personalised Ontology Construction.** A domain ontology is instantiated per learner — each student becomes a `User`-like individual whose properties capture demographics, learning style, prior performance, and contextual signals. The ontology serves as a *structured feature store* for the downstream learner.
2. **Feature Selection via a Deep Training Tree (DTT).** A tree-structured selector is trained to prune the ontology-derived feature vector and keep only the features most predictive of the target behaviour, addressing the curse of dimensionality typical of ontology embeddings.
3. **Optimised GRU-RNN Classifier.** A Gated Recurrent Unit recurrent network consumes the selected features as a temporal sequence; hyper-parameters are tuned with a meta-heuristic optimiser (the paper benchmarks several swarm/evolutionary variants).
4. **Behaviour Prediction.** The trained GRU-RNN outputs probability distributions over behavioural classes; results are compared against SVM, plain RNN, LSTM and CNN baselines and reported to outperform them on standard metrics (accuracy, F1, sensitivity, specificity).

### 3.2 Key Contributions

- A **per-user personalised ontology** as the canonical user model — richer than a flat feature vector, queryable by SPARQL, extensible without retraining the classifier.
- A **DTT feature selector** that operates on the ontology-derived vector, reducing redundancy and improving training stability.
- A **GRU-RNN optimised by a metaheuristic** that beats the standard temporal-classifier baselines on the same task.
- An end-to-end **neuro-symbolic blueprint**: ontology supplies the structure, neural model supplies the prediction, optimiser tunes the bridge.

### 3.3 Adaptation to the Clothing Ontology Project

The blueprint maps onto an outfit-recommendation engine with very minor relabelling:

| In the paper | Equivalent in this project |
|---|---|
| Student (the User) | `:User` individual (already in the v2 ontology, User module) |
| Personalised ontology of the learner | Per-user view: `:User`'s `:prefersColor`, `:prefersStyle`, `:hasBodyType`, `:ownsItem`, history of `:recommendedOutfit` |
| Domain ontology (learning resources) | Clothing ontology TBox (Item / Attribute / Outfit modules) |
| Behavioural target (engagement, drop-out) | Outfit acceptance / rating / purchase intent |
| DTT feature selector | Feature-importance pruning over ontology-derived signals (color undertone, formality, season, brand affinity) |
| Optimised GRU-RNN | Sequence model over the user's outfit-interaction history; outputs ranked candidate outfits |
| Metaheuristic hyper-parameter search | Same role; could reuse the paper's optimiser unchanged |

**Concretely**, the recommendation engine then operates as a *symbolic candidate generator* followed by a *neural personaliser*:

1. SWRL rules R1–R6 over the v2 ontology generate a set of **candidate Outfit individuals** that are color-harmonious, formality-consistent and season-appropriate.
2. For each candidate, ontology-derived features (color undertones, formality level, material set, distance from the user's `:prefersColor`/`:prefersStyle`) form the feature vector.
3. A DTT prunes those features.
4. A GRU-RNN scores the candidate against the user's past interactions and produces a personalised ranking.

This is **the same architectural pattern as the paper**, applied to a different domain. It also explains why the v2 ontology already includes a User module: it is the prerequisite for adopting this approach in Phase 3.

---

## 4. Data Acquisition (Item 3)

### 4.1 Data Sources

| Source | Type | Why selected |
|---|---|---|
| **Polyvore Outfits** (Han et al., 2017; ACM MM dataset) | Outfit-level compatibility dataset (~21 k positive outfits, ~365 k items) | Provides ground-truth examples of *what humans consider compatible*. Essential for training the future GRU-RNN scorer and for validating the SWRL rule outputs. |
| **DeepFashion / DeepFashion2** (Liu et al., 2016; Ge et al., 2019) | Image dataset with category, attribute and landmark labels | Rich per-item attribute labels (50 categories, 1000 attributes). Used to enrich `:hasColor`, `:hasMaterial`-adjacent attributes and to validate the subclass coverage of `:ClothingItem`. |
| **Retailer product feed** (Zalando / H&M public product JSON) | Live product catalogue (title, description, price, color, material, images) | Real-world unstructured text — the actual input to the LLMs4OL-style population pipeline. Provides `:hasPrice`, `:brandName`, free-text descriptions. |

### 4.2 Data Collection Methodology

- **Polyvore Outfits.** Downloaded the dataset release distributed with the Han et al. paper (`polyvore_outfits.zip`). Use the *disjoint* split for evaluation later (no item appears in both train and test outfits).
- **DeepFashion(2).** Downloaded the category-attribute split. Only the metadata CSV/JSON files are required for ontology population; images are retained for future image-based attribute extraction (Phase 3).
- **Retailer scrape.** A small, polite scrape (≤ 1 request/sec, respect `robots.txt`, identify with a project User-Agent). Approximately 500 product pages, hitting the publicly served product-JSON endpoint rather than rendering HTML, to stay within fair-use limits. No personal data, no images of identifiable persons, no payment data.

### 4.3 Data Preprocessing

1. **Deduplication.** Remove duplicates by `(brand, productID)` for the retailer feed; by Polyvore item ID for Polyvore.
2. **Color normalisation.** Map free-text color strings (`"navy blue"`, `"midnight"`, `"royal"`) to the closed set of `:Color` individuals defined in v2 (`Red`, `Blue`, `Navy`, `Black`, ...). Mapping table maintained as a CSV; nearest-named-color fallback for HEX values using CIEDE2000 distance.
3. **Material normalisation.** Parse fabric-composition strings ("95 % cotton, 5 % elastane") and assign the primary fibre as the `:Material`. Compositions are kept in an `rdfs:comment` annotation for traceability.
4. **Category normalisation.** Map source-specific category labels (Polyvore's 11 master categories, DeepFashion's 50, retailer-specific labels) onto the `:ClothingItem` subclass hierarchy via a small mapping dictionary.
5. **Language normalisation.** All free-text attribute values lower-cased and stripped of marketing adjectives ("luxurious", "limited edition") before LLM ingestion.

### 4.4 Mapping of Data to Ontology Concepts

| Source field | Target predicate | Target class/value |
|---|---|---|
| `product.title` | `rdfs:label` | xsd:string |
| `product.category` | `rdf:type` | subclass of `:ClothingItem` (e.g., `:T-Shirt`) |
| `product.color` | `:hasColor` | individual of `:Color` |
| `product.material` | `:hasMaterial` | individual of `:Material` |
| `product.size` | `:hasSize` | individual of `:Size` |
| `product.brand` | `:brandName` | xsd:string |
| `product.price` | `:hasPrice` | xsd:float |
| `product.season_tag` (when present) | `:isAppropriateForSeason` | individual of `:Season` |
| `product.formality_tag` (inferred from category + material via LLM) | `:hasFormality` | individual of `:FormalityLevel` |
| `polyvore.outfit_id` | groups items into | one `:Outfit` individual |

Unmapped fields (image URLs, review counts, stock status) are deliberately *not* lifted into the ontology; they belong in a separate operational data store.

---

## 5. Ontology Usage and Expansion (Item 4)

### 5.1 Existing Ontologies Reused

| Vocabulary | Source | How it is reused |
|---|---|---|
| **schema.org** | https://schema.org/ | `:ClothingItem owl:equivalentClass schema:Product`. `:hasColor`, `:hasMaterial`, `:hasSize`, `:hasPrice`, `:brandName` are declared `owl:equivalentProperty` to their schema.org counterparts. This gives the ontology immediate interoperability with the wider Web-of-Data and with any RDFa-marked-up e-commerce site. |
| **Dublin Core Terms (dcterms)** | http://purl.org/dc/terms/ | Ontology-level metadata (`dcterms:title`, `dcterms:description`, `dcterms:creator`, `dcterms:issued`, `dcterms:modified`, `dcterms:license`). |
| **VANN** | http://purl.org/vocab/vann/ | Preferred namespace prefix and URI declarations — picked up by Widoco when rendering the documentation. |
| **SWRL** | http://www.w3.org/2003/11/swrl# | Rule-language vocabulary used to encode rule R1 in machine-readable form. |

### 5.2 Methodology — Modular Ontology Modeling (MOMo)

The ontology has been refactored into **four modules** following the MOMo methodology (Hitzler & Krisnadhi, 2016 — *A Tutorial on Modular Ontology Modeling*). MOMo was preferred over METHONTOLOGY because the outfit-engine domain decomposes naturally into orthogonal sub-domains; MOMo lets each sub-domain be developed, documented and reused independently while a single integration layer composes them.

| Module | Scope | Anchor classes |
|---|---|---|
| **Item module** | The garment taxonomy from Phase 1, lightly extended | `:ClothingItem`, `:Top`, `:Bottom`, `:Outerwear`, `:Footwear`, `:Accessory` and 17 leaf subclasses |
| **Attribute module** | Properties used to describe items; extended with color theory and formality | `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender`, plus **new** `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel` |
| **Outfit module** *(new in v2)* | The styled combination concept and its compatibility semantics | `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit`; properties `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasOuterwear`, `:hasAccessory`, `:pairsWellWith`, `:clashesWith`, `:colorHarmonizesWith`, `:isComplementaryTo` |
| **User module** *(new in v2)* | End-user model for personalisation | `:User`, `:StyleCategory`, `:BodyType`; properties `:prefersColor`, `:prefersStyle`, `:hasBodyType`, `:ownsItem`, `:recommendedOutfit` |

### 5.3 What Was Extended

Compared with v1:

- **New classes:** `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit`, `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel`, `:User`, `:StyleCategory`, `:BodyType`. Plus a missing Top subclass `:Pink` color individual and three additional materials (`:Denim`, `:Leather`, `:Linen`).
- **New object properties:** `:hasUndertone`, `:hasFormality`, `:hasColorScheme`, `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasOuterwear`, `:hasAccessory`, `:pairsWellWith`, `:clashesWith`, `:colorHarmonizesWith`, `:isComplementaryTo`, `:prefersColor`, `:prefersStyle`, `:hasBodyType`, `:ownsItem`, `:recommendedOutfit`.
- **New data properties:** `:userName`, `:hasAge`.
- **Restrictions:** `:Outfit` carries existential restrictions on `:hasTop`, `:hasBottom`, `:hasFootwear` so that an Outfit individual without these three components is logically incomplete.
- **Annotations:** every class, property and individual has an `rdfs:label` and (for non-trivial entities) an `rdfs:comment` — required for non-empty Widoco output.
- **Alignment axioms:** `owl:equivalentClass`/`owl:equivalentProperty` to schema.org as listed in §5.1.
- **SWRL rules R1–R6** documented in comment form; R1 also encoded as a machine-readable `swrl:Imp`.

---

## 6. Ontology Documentation (Widoco — Item 6)

The Widoco command to regenerate documentation against the v2 file:

```bash
java -jar widoco-1.4.25-jar-with-dependencies.jar \
    -ontFile Clothing_Ontology.ttl \
    -outFolder docs/widoco/ \
    -rewriteAll \
    -getOntologyMetadata \
    -webVowl \
    -includeAnnotationProperties \
    -lang en
```

The generated documentation lives under `docs/widoco/` and is also linked from the repository README. Because every class and property in v2 carries an `rdfs:label` and `rdfs:comment`, the generated HTML now has populated descriptions in every section (the v1 Widoco run produced empty cells).

---

## 7. Specification Document (Item 7)

The Specification Document has been re-issued as **v2**, with a *Change Log vs v1* section. See `docs/Specification_v2.md`. Headline changes are summarised in §5.3 above.

---

## 8. GitHub (Item 5)

- The v1 state was tagged on git before any v2 edits: `git tag v1`.
- Phase-2 changes were committed on the `main` branch.
- After the final commit the v2 state is tagged: `git tag v2`.
- The repository now contains: `Clothing_Ontology.ttl` (canonical), `Clothing_Ontology.rdf` (RDF/XML serialisation, auto-generated), `docs/Phase2_Report.md`, `docs/Specification_v2.md`, and `docs/widoco/` (generated documentation).

---

## 9. Submission Checklist

- [x] Updated report with completed Data Acquisition section (this document)
- [x] Explanation of selected research integration — §2 (LLMs4OL)
- [x] Summary of the mandatory paper — §3
- [x] Updated ontology in GitHub — `Clothing_Ontology.ttl`, tag `v2`
- [x] Widoco documentation — generated, see §6
- [x] Specification Document v2 — `docs/Specification_v2.md`
