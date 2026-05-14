# Ontology Specification Document - Clothing Ontology

**Version:** 2.0  
**Date:** 2026-05-14  
**Status:** Phase 2 deliverable  
**Previous version:** 1.0 (Phase 1)  
**Canonical file:** `Clothing_Ontology.ttl`  
**Namespace:** `http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/`  
**Preferred prefix:** `clo:`  
**License:** CC BY 4.0

---

## 1. Purpose

The Clothing Ontology provides a formal, machine-readable model of clothing items, their attributes, and the higher-level concept of an **Outfit**, a styled combination of items. It is designed to support an outfit combination engine that can reason over:

- color theory,
- material and formality consistency,
- season and occasion appropriateness,
- user preferences and wardrobe ownership.

## 2. Scope

In scope:

- Garment taxonomy: `:Top`, `:Bottom`, `:Outerwear`, `:Footwear`, `:Accessory`, and common leaf classes.
- Attributes: color, material, size, season, occasion, gender, formality level, color scheme, and color undertone.
- Outfit structure: top, bottom, footwear, outerwear, accessory, and color scheme.
- Compatibility relations: color harmony, complementarity, pair compatibility, and conflict relation.
- User model: preferences, body type, owned items, and recommendation history.
- Reuse of schema.org, Dublin Core Terms, VANN, and SWRL.

Out of scope:

- Computer-vision attribute extraction.
- The GRU-RNN neural ranker.
- Bulk dataset storage.
- Multi-currency price modeling.
- Full closed-world validation; SHACL is planned for data validation during ontology population.

## 3. Competency Questions

| ID | Question |
|---|---|
| CQ1 | Which clothing items are appropriate for Winter and Formal occasions? |
| CQ2 | Given a starting `:Top`, which `:Bottom` items have a harmonious color with it? |
| CQ3 | Which outfits contain items at `:FormalLevel` formality? |
| CQ4 | What can be recommended for a user whose `:prefersColor` is `:Blue` and whose `:prefersStyle` is `:Minimalist`? |
| CQ5 | Which colors are complementary to `:Blue`? |
| CQ6 | Which catalogue items clash with a silk item in a sport context? |
| CQ7 | For a given outfit, what color scheme is asserted or inferred? |

## 4. Modular Structure

The ontology follows Modular Ontology Modeling (MOMo).

| Module | Anchor classes | New in v2 |
|---|---|---|
| Item | `:ClothingItem` and its taxonomy | No |
| Attribute | `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender`, `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel` | Last three are new |
| Outfit | `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit` | Yes |
| User | `:User`, `:StyleCategory`, `:BodyType` | Yes |

## 5. Reused Vocabularies

| Prefix | IRI | Use |
|---|---|---|
| `schema:` | https://schema.org/ | `:ClothingItem rdfs:subClassOf schema:Product`; selected properties use `rdfs:subPropertyOf` schema.org properties. |
| `dcterms:` | http://purl.org/dc/terms/ | Ontology metadata. |
| `vann:` | http://purl.org/vocab/vann/ | Preferred namespace prefix and URI declarations. |
| `swrl:` / `swrlb:` | http://www.w3.org/2003/11/swrl# | Machine-readable encoding for R1. |
| `foaf:` | http://xmlns.com/foaf/0.1/ | Reserved for possible future user identity extension. |

The schema.org alignment is intentionally modeled as subclass/subproperty reuse rather than equivalence. `schema:Product` includes many non-clothing products, so declaring all schema products equivalent to `:ClothingItem` would be too broad.

## 6. Class Inventory

### 6.1 Item Module

- `:ClothingItem` - top-level wearable article, modeled as a subclass of `schema:Product`.
- `:Top` - subclasses: `:T-Shirt`, `:Blouse`, `:Sweater`, `:Hoodie`.
- `:Bottom` - subclasses: `:Jean`, `:Trouser`, `:Short`, `:Skirt`.
- `:Outerwear` - subclasses: `:Jacket`, `:Coat`.
- `:Footwear` - subclasses: `:Boots`, `:Sandals`, `:FormalShoes`, `:SportsShoes`.
- `:Accessory` - subclasses: `:Belt`, `:Hat`, `:Scarf`, `:Watch`.

### 6.2 Attribute Module

- `:Attribute` - grouping class for item/outfit attributes.
- `:Color`, `:Material`, `:Size`, `:Season`, `:Occasion`, `:Gender`.
- `:ColorScheme` - individuals: `:Monochromatic`, `:Analogous`, `:Complementary`, `:Triadic`, `:NeutralScheme`.
- `:ColorUndertone` - individuals: `:Warm`, `:Cool`, `:NeutralUndertone`.
- `:FormalityLevel` - individuals: `:CasualLevel`, `:SmartCasualLevel`, `:BusinessCasualLevel`, `:FormalLevel`.

### 6.3 Outfit Module

- `:Outfit` - a styled combination of clothing items.
- `:HarmoniousOutfit` - target class for outfits satisfying harmony rules.
- `:FormalOutfit` - target class for outfits satisfying formal outfit rules.
- `:CasualOutfit` - target class for outfits satisfying casual outfit rules.

`Outfit` has OWL existential restrictions for `:hasTop`, `:hasBottom`, and `:hasFootwear`. These restrictions express intended model semantics under open-world reasoning. They do not by themselves reject an individual that lacks explicit top/bottom/footwear triples; that validation should be performed with SHACL during data acquisition.

### 6.4 User Module

- `:User` - end user of the outfit recommendation engine.
- `:StyleCategory` - style preference class, with individuals such as `:Minimalist`, `:Classic`, `:Streetwear`, `:BohoChic`, `:Sporty`.
- `:BodyType` - future fit-aware recommendation attribute, with individuals such as `:Slim`, `:Athletic`, `:Average`, `:Plus`.

## 7. Property Inventory

### 7.1 Object Properties

Phase-1 properties retained and completed with domain/range:

- `:hasColor`
- `:hasMaterial`
- `:hasSize`
- `:isAppropriateForOccasion`
- `:isAppropriateForSeason`
- `:isSuitableFor`

New in v2:

- Attribute extensions: `:hasUndertone`, `:hasFormality`.
- Outfit structure: `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasOuterwear`, `:hasAccessory`, `:hasColorScheme`.
- Compatibility: `:pairsWellWith`, `:clashesWith`, `:colorHarmonizesWith`, `:isComplementaryTo`.
- User model: `:prefersColor`, `:prefersStyle`, `:hasBodyType`, `:ownsItem`, `:recommendedOutfit`.

### 7.2 Data Properties

- `:brandName`
- `:hasPrice`
- `:isMachineWashable`
- `:userName`
- `:hasAge`

## 8. SWRL Rules

| ID | Status | Informal reading |
|---|---|---|
| R1 | Machine-readable `swrl:Imp` in `Clothing_Ontology.ttl` | If an outfit's top and bottom have colors that harmonize, the two items pair well together. |
| R2 | Documented design rule | If an outfit's top, bottom, and footwear are all `:FormalLevel`, the outfit is a `:FormalOutfit`. |
| R3 | Documented design rule | If an outfit's top, bottom, and footwear are all `:CasualLevel`, the outfit is a `:CasualOutfit`. |
| R4 | Documented design rule | A winter outfit that contains outerwear can be classified as season-coherent/harmonious. |
| R5 | Documented design rule | An item made of `:Silk` and declared appropriate for `:Sport` should be flagged as a conflict. |
| R6 | Documented design rule | A warm-color top and cool-color bottom without a neutral color should be flagged as a color clash. |

Only R1 is implemented as machine-readable SWRL in v2. R2-R6 are documented in comments as implementation-ready designs for Phase 3.

## 9. Change Log - v1 to v2

### Added

- Outfit module: `:Outfit`, `:HarmoniousOutfit`, `:FormalOutfit`, `:CasualOutfit`, and structural/compatibility properties.
- User module: `:User`, `:StyleCategory`, `:BodyType`, and user preference/ownership properties.
- Attribute extensions: `:ColorScheme`, `:ColorUndertone`, `:FormalityLevel`.
- New color individuals `:Pink`, `:Navy`; new material individuals `:Denim`, `:Leather`, `:Linen`.
- Example clothing items, example outfits, and one example user.
- Ontology metadata using Dublin Core Terms and VANN.
- Machine-readable SWRL R1.
- Documented R2-R6 rule designs.
- Field-level data acquisition mapping in `docs/Data_Acquisition_Mapping.csv`.
- Widoco regeneration instructions in `docs/Widoco_Instructions.md`.

### Changed

- schema.org alignment changed from equivalence axioms to `rdfs:subClassOf` / `rdfs:subPropertyOf` reuse.
- All Phase-1 object properties received `rdfs:domain` and `rdfs:range`.
- Functional-property declarations were added where a single value is expected, such as `:hasSize`, `:hasPrice`, `:hasUndertone`, `:hasBodyType`, `:userName`, and `:hasAge`.
- `:Blue_Cotton_Shirt` was typed as `:Blouse` and given a fuller attribute profile.
- `:White_Sneakers` was typed as `:SportsShoes` and given a fuller attribute profile.
- The description of OWL restrictions was corrected to account for open-world semantics.
- The documentation now distinguishes implemented SWRL R1 from documented future rules R2-R6.

### Removed

- The unused `untitled-ontology-3:` prefix from v1.

### Backwards Compatibility

All Phase-1 local IRIs are preserved. Existing references to individuals such as `:Blue`, `:Cotton`, and `:Blue_Cotton_Shirt` still resolve.

## 10. Quality Notes

- `Clothing_Ontology.ttl` is the canonical ontology file.
- `Clothing_Ontology.rdf` is maintained as an RDF/XML mirror.
- Widoco documentation is generated under `docs/widoco/`.
- Pair compatibility and clash relations are separated with `owl:propertyDisjointWith`.
- Closed-world validation of complete outfit records should be handled by SHACL during data acquisition rather than by OWL existential restrictions alone.
