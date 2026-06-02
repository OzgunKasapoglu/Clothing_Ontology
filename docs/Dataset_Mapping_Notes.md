# Dataset Mapping Notes

## Purpose

These mappings translate sampled H&M product metadata into the current Clothing Ontology vocabulary. They are intentionally conservative: values that do not fit the ontology are marked as `needs_ontology_extension`, `broad_fallback`, `out_of_scope`, or `skip`.

## Mapping files

- `data/mappings/hm_product_type_to_class.csv` maps H&M `product_type_name` values to ontology classes.
- `data/mappings/hm_product_group_to_class.csv` provides fallback class mappings from `product_group_name`.
- `data/mappings/hm_color_to_ontology.csv` normalizes H&M color labels to ontology color individuals.
- `data/mappings/hm_index_group_to_gender.csv` maps broad H&M retail segments to ontology gender individuals where possible.

## ABox generation

Use the generator below to create a Turtle ABox file from the downloaded H&M sample:

```bash
python scripts/generate_hm_abox.py
```

The generated file is `data/generated/hm_sample_catalog.ttl`. It creates item individuals, labels, descriptions, color links, and gender suitability links where the mappings are explicit enough.

## Important gaps found

The sample contains values that the ontology does not currently model directly:

- underwear: `Bra`, `Underwear Tights`
- hosiery: `Socks`, `Leggings/Tights`
- sleepwear: `Pyjama jumpsuit/playsuit`, `Nightwear`
- extra colors: `Gold`, `Silver`, `Light Turquoise`
- age segment: `Baby/Children`

For the final project, the safest approach is to keep these as broad `:ClothingItem` examples or exclude them from the small demonstration graph. A better ontology extension would add classes such as `:Underwear`, `:Socks`, `:Sleepwear`, and color individuals such as `:Gold`, `:Silver`, and `:Turquoise`.
