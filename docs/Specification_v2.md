# Ontology Specification Document — Clothing Ontology

**Version:** 2.0
**Date:** 2026-05-11
**Status:** Phase 2 deliverable
**Previous version:** 1.0 (Phase 1)
**Canonical file:** `Clothing_Ontology.ttl`
**Namespace:** `http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/`
**Preferred prefix:** `clo:`
**License:** CC BY 4.0

---

## 1. Purpose

The Clothing Ontology provides a formal, machine-readable model of clothing items, their attributes, and the higher-level concept of an **Outfit** — a styled combination of items. Its purpose is to support a *rule-based outfit combination engine* that, given a starting item or a user context, recommends harmonious outfits by reasoning over:

- color theory (harmony, complementarity, undertone),
- material and formality consistency,
- season and occasion appropriateness,
- per-user preference data (color, style, body type, owned items).

## 2. Scope

In scope:
- Garment taxonomy (Top, Bottom, Outerwear, Footwear, Accessory) and common leaf categories.
- Attributes: color (with undertone), material, size, season, occasion, gender, formality level, color scheme.
- Outfit as a first-class entity with part-of relations to its components and compatibility relations to other items.
- User model for personalisation: preferences, ownership, body type, recommendation history.
- Alignment with schema.org for interoperability with e-commerce data.
- SWRL rules encoding the engine's compatibility heuristics.

Out of scope (deferred to later phases):
- Image-based attribute extraction (computer vision).
- The neural ranker itself (GRU-RNN, Phase 3).
- Multi-currency price modelling.
- Garment-fit modelling beyond `:BodyType`.

## 3. Competency Questions

The ontology must answer the following SPARQL competency questions:

| # | Question |
|---|---|
| CQ1 | Which clothing items in the wardrobe are appropriate for *Winter* and *Formal* occasions? |
| CQ2 | Given a starting `Top` *X*, which `Bottom`s have a harmonious color with *X*? |
| CQ3 | Which `Outfit`s contain only items at `FormalLevel` formality? (→ classified as `:FormalOutfit`) |
| CQ4 | What does the engine recommend for a user whose `:prefersColor` is `:Blue` and whose `:prefersStyle` is `:Minimalist`? |
| CQ5 | Which colors are complementary to `:Blue`? |
| CQ6 | Which items in the catalogue clash with a *Silk* scarf in a *Sport* context? |
| CQ7 | For a given `Outfit`, what is its inferred `:ColorScheme`? |

## 4. Modular Structure (MOMo)

| Module | Anchor classes | New in v2 |
|---|---|---|
| Item | `:ClothingItem` and its taxonomy | No (Phase 1) |
| Attribute | `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender`, `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel` | Last three are new |
| Outfit | `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit` + structural and compatibility properties | Yes — entire module |
| User | `:User`, `:StyleCategory`, `:BodyType` + preference/ownership properties | Yes — entire module |

## 5. Reused Vocabularies

| Prefix | IRI | Use |
|---|---|---|
| `schema:` | https://schema.org/ | `equivalentClass`/`equivalentProperty` alignment with `schema:Product`, `schema:color`, `schema:material`, `schema:size`, `schema:price`, `schema:brand` |
| `dcterms:` | http://purl.org/dc/terms/ | Ontology metadata (title, description, creator, dates, license) |
| `vann:` | http://purl.org/vocab/vann/ | Preferred prefix / namespace declarations for tooling |
| `swrl:` / `swrlb:` | http://www.w3.org/2003/11/swrl# | Rule encoding |
| `foaf:` | http://xmlns.com/foaf/0.1/ | Reserved for future user-identity extension |

## 6. Class Inventory

### 6.1 Item Module

- `:ClothingItem` — top-level wearable article. Equivalent to `schema:Product`.
- `:Top` ⊏ `:ClothingItem`; subclasses: `:T-Shirt`, `:Blouse`, `:Sweater`, `:Hoodie`.
- `:Bottom` ⊏ `:ClothingItem`; subclasses: `:Jean`, `:Trouser`, `:Short`, `:Skirt`.
- `:Outerwear` ⊏ `:ClothingItem`; subclasses: `:Jacket`, `:Coat`.
- `:Footwear` ⊏ `:ClothingItem`; subclasses: `:Boots`, `:Sandals`, `:FormalShoes`, `:SportsShoes`.
- `:Accessory` ⊏ `:ClothingItem`; subclasses: `:Belt`, `:Hat`, `:Scarf`, `:Watch`.

### 6.2 Attribute Module

- `:Attribute` (abstract grouping).
- `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender` — Phase-1 attributes, retained.
- `:ColorScheme` *(new)* — instances `:Monochromatic`, `:Analogous`, `:Complementary`, `:Triadic`, `:NeutralScheme`.
- `:ColorUndertone` *(new)* — instances `:Warm`, `:Cool`, `:NeutralUndertone`.
- `:FormalityLevel` *(new)* — instances `:CasualLevel`, `:SmartCasualLevel`, `:BusinessCasualLevel`, `:FormalLevel`.

### 6.3 Outfit Module *(new in v2)*

- `:Outfit` — a styled combination. Carries existential restrictions: every `:Outfit` must have at least one `:hasTop` filler, one `:hasBottom`, one `:hasFootwear`.
- `:HarmoniousOutfit` ⊏ `:Outfit` — inferred when color and formality rules are satisfied.
- `:FormalOutfit` ⊏ `:Outfit` — all components at `:FormalLevel`.
- `:CasualOutfit` ⊏ `:Outfit` — all components at `:CasualLevel`.

### 6.4 User Module *(new in v2)*

- `:User`, `:StyleCategory`, `:BodyType` with named individuals listed in `Clothing_Ontology.ttl`.

## 7. Property Inventory

### 7.1 Object Properties

Phase-1: `:hasColor`, `:hasMaterial`, `:hasSize`, `:isAppropriateForOccasion`, `:isAppropriateForSeason`, `:isSuitableFor` — all kept, now with `rdfs:domain`/`rdfs:range` filled in.

New in v2:
- Attribute extensions: `:hasUndertone`, `:hasFormality`.
- Outfit structure: `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasOuterwear`, `:hasAccessory`, `:hasColorScheme`.
- Compatibility: `:pairsWellWith` (symmetric), `:clashesWith` (symmetric, disjoint with `:pairsWellWith`), `:colorHarmonizesWith` (symmetric), `:isComplementaryTo` (sub-property of `:colorHarmonizesWith`).
- User: `:prefersColor`, `:prefersStyle`, `:hasBodyType` (functional), `:ownsItem`, `:recommendedOutfit`.

### 7.2 Data Properties

Phase-1: `:brandName`, `:hasPrice`, `:isMachineWashable` — kept, with domain/range and (where appropriate) `owl:FunctionalProperty`.
New in v2: `:userName`, `:hasAge`.

## 8. SWRL Rules

| ID | Informal Reading |
|---|---|
| R1 | If an Outfit's Top and Bottom have colors that harmonize, the two items pair well together. |
| R2 | If an Outfit's Top, Bottom and Footwear are all `:FormalLevel`, the Outfit is a `:FormalOutfit`. |
| R3 | If an Outfit's Top, Bottom and Footwear are all `:CasualLevel`, the Outfit is a `:CasualOutfit`. |
| R4 | A Winter Outfit that contains some Outerwear is a `:HarmoniousOutfit`. |
| R5 | An item made of `:Silk` declared appropriate for `:Sport` is internally inconsistent (`:clashesWith` itself — diagnostic). |
| R6 | If an Outfit's Top has a `:Warm` color and its Bottom has a `:Cool` color and neither is a neutral, the Top and Bottom clash. |

R1 is encoded in machine-readable SWRL inside `Clothing_Ontology.ttl`; R2–R6 are documented as comments and are intended to be added in Protégé's SWRL tab in Phase 3 (each is mechanical given R1 as a template).

## 9. Change Log — v1 → v2

### Added
- **Outfit module** (entire): `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit` and 9 structural/compatibility properties.
- **User module** (entire): `:User`, `:StyleCategory`, `:BodyType` and 7 user-side properties / data properties.
- **Attribute module extensions**: `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel` and their individuals.
- **schema.org alignment**: equivalence axioms for `:ClothingItem`, `:hasColor`, `:hasMaterial`, `:hasSize`, `:hasPrice`, `:brandName`.
- **Ontology metadata**: dcterms title/description/creator/dates/license; vann namespace prefix; owl:versionIRI and owl:versionInfo.
- **Existential restrictions on `:Outfit`** (must have at least one Top, Bottom and Footwear).
- **SWRL rule R1** in machine-readable form; R2–R6 documented.
- **15 new example individuals** (clothing items spanning each subclass), 3 example `:Outfit` individuals, and 1 example `:User`.
- **`rdfs:label` and `rdfs:comment`** on every class, property and individual (Widoco-ready).
- New color individual `:Pink`, `:Navy`; new materials `:Denim`, `:Leather`, `:Linen`.
- **Methodology declaration**: MOMo (Modular Ontology Modeling) adopted.

### Changed
- All Phase-1 object properties received `rdfs:domain` and `rdfs:range`.
- `:hasSize`, `:hasPrice`, `:isMachineWashable`, `:hasUndertone`, `:hasBodyType`, `:userName`, `:hasAge` declared `owl:FunctionalProperty`.
- The `Blue_Cotton_Shirt` example individual was promoted from `:Top` to its proper leaf class `:Blouse` and given a full attribute profile.
- `White_Sneakers` example was promoted from `:Footwear` to `:SportsShoes` and given a full attribute profile.

### Removed
- The dangling `untitled-ontology-3:` prefix that was imported but unused in v1.

### Backwards compatibility
- All Phase-1 IRIs are preserved; existing references to `:Blue`, `:Cotton`, `:Blue_Cotton_Shirt`, etc. continue to resolve.
- v1 is preserved as the git tag `v1`. v2 is tagged `v2`.

## 10. Quality Notes

- The TBox parses cleanly with `rdflib` (914 triples).
- Disjointness between `:pairsWellWith` and `:clashesWith` ensures the engine cannot simultaneously infer both for the same pair.
- The existential restrictions on `:Outfit` mean a "valid" Outfit *cannot* be missing a Top, Bottom or Footwear under OWL semantics — exactly the constraint the engine needs.
