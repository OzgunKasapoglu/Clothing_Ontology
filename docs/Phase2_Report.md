# Phase 2 Report - Clothing Ontology for an Outfit Combination Engine

**Project:** Clothing Ontology  
**Phase:** 2  
**Ontology version:** v2  
**Author:** Ozgun Kasapoglu  
**Date:** 2026-05-14  
**Repository:** https://github.com/OzgunKasapoglu/Clothing_Ontology

---

## 1. Project Summary

The project develops an OWL 2 ontology that models clothing items together with their attributes: color, material, size, season, occasion, gender, and formality. Phase 2 extends the Phase 1 taxonomy with the higher-level concept of an **Outfit**, a styled combination of clothing items. The ontology is designed to support a rule-based outfit combination engine that can recommend compatible outfits based on color theory, formality consistency, season coherence, and personal user preferences.

Phase 2 also defines a data acquisition and ontology-population plan for external clothing data such as outfit datasets, fashion-image metadata, and retailer product records. The population plan is inspired by recent ontology learning research using large language models.

---

## 2. Research Integration

### 2.1 Selected Study

**Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). _LLMs4OL: Large Language Models for Ontology Learning._ ISWC 2023. DOI: 10.1007/978-3-031-47240-4_22.**

This study was selected from the Week 11/Week 12 material area on ontology population and ontology learning with LLMs.

### 2.2 Why This Study Was Selected

Phase 1 produced a small ontology that was populated manually. Scaling the outfit-recommendation use case requires many clothing-item individuals with reliable attribute coverage. Manual curation does not scale well, and rule-based extraction can be brittle for retailer descriptions such as "95% cotton / 5% elastane regular-fit oxford shirt".

LLMs4OL is directly relevant because it evaluates how LLMs can support three ontology-learning tasks:

- term typing,
- taxonomy discovery,
- non-taxonomic relation extraction.

These tasks match the needs of this project: classifying a product as a `:T-Shirt` or `:Blouse`, checking whether the current garment taxonomy covers real catalogue data, and extracting relations such as `:hasColor`, `:hasMaterial`, `:hasFormality`, and `:isAppropriateForSeason`.

### 2.3 Relevance to the Project

| LLMs4OL task | Role in this project |
|---|---|
| Term typing | Assign a scraped product to a clothing class such as `:T-Shirt`, `:Blouse`, `:Hoodie`, or `:FormalShoes`. |
| Taxonomy discovery | Detect product categories that are not yet represented in the v2 taxonomy. |
| Non-taxonomic relation extraction | Populate object/data properties such as `:hasColor`, `:hasMaterial`, `:hasFormality`, `:brandName`, and `:hasPrice`. |

### 2.4 Integration Point in the System Architecture

The selected study is integrated into the **Population Layer** of the system architecture:

```text
Layer 4 - Recommendation Engine
  SPARQL queries and ranking logic produce recommended outfits.

Layer 3 - Reasoning Layer
  OWL reasoning and SWRL-compatible execution infer compatibility relations.

Layer 2 - Ontology v2
  Item, Attribute, Outfit, and User modules define the target schema.

Layer 1 - Population Layer
  Raw product/outfit data -> schema-aware LLM extraction -> Turtle ABox triples
  -> SHACL validation -> merge into ontology/catalogue store.
```

The Phase 3 population pipeline is planned as follows:

1. Acquire product records from Polyvore-style outfit data, DeepFashion metadata, and a permitted retailer product feed.
2. Prompt an LLM with the ontology TBox and ask it to emit Turtle ABox triples.
3. Validate the emitted triples with SHACL shapes, especially for range constraints such as `:hasColor` pointing to a known `:Color` individual.
4. Merge validated triples into a catalogue graph or into `Clothing_Ontology.ttl` for small curated examples.
5. Run reasoning to catch logical or rule-level conflicts introduced by extraction.

Only the target ontology, example individuals, and mapping documentation are included in this Phase 2 repository. Bulk datasets are intentionally not committed because of size and licensing constraints.

---

## 3. Mandatory Paper Review

**Paper:** Fernandez, F. M. H., Venkata Ramana, T., Shabana, M., Kannagi, V., & Nalini, M. (2023). _Personalized ontology and deep training tree-based optimal gated recurrent unit-recurrent neural network for prediction of students' behavior._ Concurrency and Computation: Practice and Experience, 35(1), e7420. DOI: 10.1002/cpe.7420.

### 3.1 Core Methodology

The paper proposes a personalized digital-library system that combines ontology engineering with a neural behavior-prediction model.

1. **Personalized ontology construction.** The authors use Protege 4.3 to build digital-library ontologies and represent interrelated concepts for student/user behavior modeling.
2. **Ontology-based user modeling.** The ontology captures structured information about users and digital-library concepts so that behavior can be represented more richly than with flat tabular features alone.
3. **Deep Training Tree-based GRU-RNN.** A GRU-RNN model is used to predict user behavior styles such as cognitive behavior, learning-speed behavior, sedentary behavior, and aggressive behavior. The Deep Training Tree is introduced to improve the training process and address vanishing-gradient/training limitations associated with recurrent models.
4. **Black Widow Optimization.** A Black Widow Optimization method is used to update GRU-RNN weights and improve predictive accuracy.
5. **Evaluation.** The model is evaluated with metrics such as accuracy, F-score, loss, precision, and recall.

### 3.2 Key Contributions

- It combines a personalized ontology with machine learning instead of treating user behavior prediction as a purely statistical task.
- It demonstrates how an ontology can act as a structured knowledge layer for personalization.
- It applies a DTT-based optimal GRU-RNN to behavior prediction in a digital-library domain.
- It uses Black Widow Optimization to tune/update the GRU-RNN model.
- It provides a neuro-symbolic pattern: symbolic ontology for structured domain/user knowledge, neural model for prediction.

### 3.3 Adaptation to the Clothing Ontology Project

The same pattern can be adapted to outfit recommendation:

| In the paper | In this project |
|---|---|
| Student/user ontology | `:User` module with preferences, owned items, body type, and recommendation history |
| Digital-library concepts | Clothing items, attributes, outfits, occasions, and style categories |
| Student behavior classes | Outfit acceptance, outfit rating, purchase intent, or click/save behavior |
| DTT-GRU-RNN | Future temporal ranker over a user's outfit-interaction sequence |
| Black Widow Optimization | Optional optimizer for the neural ranking model |

In the current v2 ontology, the symbolic layer is implemented first: item classes, outfit structure, user preference properties, and one machine-readable SWRL rule for color-harmony pairing. In a later implementation phase, the GRU-RNN idea could be added as a personal ranking layer after the ontology generates or filters candidate outfits.

The corrected interpretation is that the current ontology does **not** implement the neural model. It only prepares the ontology structure needed for such a model.

---

## 4. Data Acquisition

### 4.1 Data Sources

| Source | Type | Use in this project |
|---|---|---|
| Polyvore Outfits / Polyvore-style outfit datasets | Outfit-level compatibility data | Provides examples of item combinations that humans considered compatible. Useful for evaluating rule-generated outfit candidates. |
| DeepFashion / DeepFashion2 | Fashion-image metadata with category and attribute labels | Helps validate garment taxonomy coverage and provides category/attribute labels for ontology population. |
| Retailer product feed or permitted product JSON | Product catalogue data | Provides titles, descriptions, brands, prices, colors, materials, and sizes for realistic item population. |
| Project ontology files | Internal structured source | Defines the target TBox classes, properties, individuals, and validation expectations. |

### 4.2 Data Collection Methodology

For Phase 2, the data-acquisition component is specified as a reproducible acquisition plan rather than a committed bulk dataset:

- **Polyvore-style outfit data:** use publicly available dataset releases where redistribution is allowed. The disjoint split should be preferred for future evaluation so that train/test outfits do not share items.
- **DeepFashion metadata:** use metadata files for category and attribute labels. Full image files are not required for the Phase 2 ontology and should not be committed to Git.
- **Retailer product feed:** use only permitted public product JSON or API-style records. The collection process must respect `robots.txt`, rate limits, and site terms. No payment data, account data, or personal data should be collected.
- **Repository artifacts:** the field-level mapping is included in `docs/Data_Acquisition_Mapping.csv`.

### 4.3 Data Preprocessing

1. **Deduplication:** remove duplicate products by source product ID or by `(brand, normalized title, category)`.
2. **Color normalization:** map source values such as "navy blue", "midnight", or "royal" to known `:Color` individuals such as `:Navy` or `:Blue`.
3. **Material normalization:** parse fabric strings such as "95% cotton, 5% elastane" and map the primary material to `:Material`.
4. **Category normalization:** map source categories to ontology subclasses such as `:T-Shirt`, `:Blouse`, `:Trouser`, `:SportsShoes`, or `:Coat`.
5. **Formality inference:** infer `:FormalityLevel` from category, material, and product text when no explicit formality field exists.
6. **Text cleaning:** normalize case, remove marketing adjectives, and preserve original labels as traceability comments where useful.

### 4.4 Mapping of Data to Ontology Concepts

| Source field | Target predicate | Target class/value |
|---|---|---|
| `product.title` | `rdfs:label` | `xsd:string` |
| `product.category` | `rdf:type` | subclass of `:ClothingItem` |
| `product.color` | `:hasColor` | individual of `:Color` |
| `product.material` | `:hasMaterial` | individual of `:Material` |
| `product.size` | `:hasSize` | individual of `:Size` |
| `product.brand` | `:brandName` | `xsd:string` |
| `product.price` | `:hasPrice` | `xsd:float` |
| `product.season_tag` | `:isAppropriateForSeason` | individual of `:Season` |
| `product.formality_tag` | `:hasFormality` | individual of `:FormalityLevel` |
| `polyvore.outfit_id` | outfit grouping predicates | one `:Outfit` individual |

Unmapped operational fields such as image URLs, stock status, and review counts are intentionally excluded from the ontology unless a later requirement needs them.

---

## 5. Ontology Usage and Expansion

### 5.1 Existing Ontologies Reused

| Vocabulary | Source | How it is reused |
|---|---|---|
| schema.org | https://schema.org/ | `:ClothingItem rdfs:subClassOf schema:Product`; selected local properties use `rdfs:subPropertyOf` schema.org properties such as `schema:color`, `schema:material`, `schema:size`, `schema:price`, and `schema:brand`. This is intentionally weaker than equivalence because not every `schema:Product` is a clothing item. |
| Dublin Core Terms | http://purl.org/dc/terms/ | Ontology-level metadata such as title, description, creator, issue date, modified date, and license. |
| VANN | http://purl.org/vocab/vann/ | Preferred namespace prefix and namespace URI declarations for documentation tools. |
| SWRL | http://www.w3.org/2003/11/swrl# | Rule vocabulary used to encode R1 as a machine-readable SWRL implication. |

### 5.2 Methodology - Modular Ontology Modeling

The ontology follows **Modular Ontology Modeling (MOMo)**. MOMo was selected because the domain separates naturally into modules that can be understood and tested independently.

| Module | Scope | Anchor classes |
|---|---|---|
| Item module | Garment taxonomy | `:ClothingItem`, `:Top`, `:Bottom`, `:Outerwear`, `:Footwear`, `:Accessory` |
| Attribute module | Item and outfit attributes | `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender`, `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel` |
| Outfit module | Styled combinations and compatibility semantics | `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit` |
| User module | Personalization | `:User`, `:StyleCategory`, `:BodyType` |

### 5.3 What Was Extended

Compared with v1:

- **New classes:** `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit`, `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel`, `:User`, `:StyleCategory`, and `:BodyType`.
- **New object properties:** `:hasUndertone`, `:hasFormality`, `:hasColorScheme`, `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasOuterwear`, `:hasAccessory`, `:pairsWellWith`, `:clashesWith`, `:colorHarmonizesWith`, `:isComplementaryTo`, `:prefersColor`, `:prefersStyle`, `:hasBodyType`, `:ownsItem`, and `:recommendedOutfit`.
- **New data properties:** `:userName`, `:hasAge`.
- **Restrictions:** `:Outfit` has OWL existential restrictions for top, bottom, and footwear components. Under OWL open-world semantics, these restrictions imply required fillers but do not by themselves validate missing explicit data. SHACL is planned for closed-world data validation in the population pipeline.
- **Annotations:** classes and properties include `rdfs:label` and `rdfs:comment` values for Widoco.
- **Alignment axioms:** schema.org reuse is modeled with `rdfs:subClassOf` and `rdfs:subPropertyOf`.
- **SWRL status:** R1 is encoded as a machine-readable `swrl:Imp`; R2-R6 are documented as rule designs/comments for future implementation.

---

## 6. Ontology Documentation

Widoco documentation is generated under `docs/widoco/`. Regeneration instructions are documented in `docs/Widoco_Instructions.md`.

The command is:

```bash
java -jar widoco-1.4.25-jar-with-dependencies_JDK-17.jar \
  -ontFile Clothing_Ontology.ttl \
  -outFolder docs/widoco/ \
  -rewriteAll \
  -getOntologyMetadata \
  -webVowl \
  -includeAnnotationProperties \
  -lang en
```

---

## 7. Specification Document

The Specification Document has been re-issued as **Version 2** in `docs/Specification_v2.md`. It includes the v1 to v2 change log and reflects the updated module structure, schema.org alignment, SWRL implementation status, and OWL/SHACL validation distinction.

---

## 8. GitHub

- The v1 state was tagged on git before any v2 edits: `git tag v1`.
- Phase-2 changes were committed on the `main` branch.
- After the final commit the v2 state is tagged: `git tag v2`.
- The repository now contains: `Clothing_Ontology.ttl` (canonical), `Clothing_Ontology.rdf` (RDF/XML serialisation), `docs/Phase2_Report.md`, `docs/Specification_v2.md`, and `docs/widoco/` (generated documentation).

---

## 9. References

- Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). _LLMs4OL: Large Language Models for Ontology Learning._ ISWC 2023. DOI: 10.1007/978-3-031-47240-4_22.
- Fernandez, F. M. H., Venkata Ramana, T., Shabana, M., Kannagi, V., & Nalini, M. (2023). _Personalized ontology and deep training tree-based optimal gated recurrent unit-recurrent neural network for prediction of students' behavior._ Concurrency and Computation: Practice and Experience, 35(1), e7420. DOI: 10.1002/cpe.7420.
- Han, X., Wu, Z., Jiang, Y.-G., & Davis, L. S. (2017). _Learning Fashion Compatibility with Bidirectional LSTMs._ ACM Multimedia.
- Liu, Z., Luo, P., Qiu, S., Wang, X., & Tang, X. (2016). _DeepFashion: Powering Robust Clothes Recognition and Retrieval with Rich Annotations._ CVPR.
- Ge, Y., Zhang, R., Wang, X., Tang, X., & Luo, P. (2019). _DeepFashion2: A Versatile Benchmark for Detection, Pose Estimation, Segmentation and Re-Identification of Clothing Images._ CVPR.
- Hitzler, P., & Krisnadhi, A. (2016). _A Tutorial on Modular Ontology Modeling with Ontology Design Patterns._
- schema.org. _Product, color, material, size, price, brand._ https://schema.org/

---

## 10. Submission Checklist

- [x] Updated report with completed Data Acquisition section.
- [x] Explanation of selected research integration.
- [x] Summary of the mandatory paper.
- [x] Updated ontology in GitHub.
- [x] Widoco documentation.
- [x] Specification Document v2.
