# Dataset Download Plan

## Selected datasets

### 1. H&M article/product metadata

- **Use:** Populate clothing item individuals and attributes.
- **Sample source:** Hugging Face mirror `dinhlnd1610/HM-Personalized-Fashion-Recommendations`, config `articles`, split `train`.
- **Original source:** Kaggle competition `h-and-m-personalized-fashion-recommendations`.
- **Useful fields:** `article_id`, `prod_name`, `product_type_name`, `product_group_name`, `colour_group_name`, `perceived_colour_master_name`, `index_group_name`, `garment_group_name`, `detail_desc`.
- **Ontology fit:** Best source for `:ClothingItem`, subclasses such as `:Top` or `:Bottom`, `:hasColor`, `:isSuitableFor`, and possible material/formality extraction from `detail_desc`.

### 2. Polyvore outfit groupings

- **Use:** Populate example `:Outfit` individuals and item-combination relations.
- **Sample source:** Hugging Face dataset `owj0421/polyvore-outfits`, config `disjoint_default`, split `train`.
- **Original family:** Polyvore outfit datasets used in fashion compatibility research.
- **Useful fields:** `set_id`, `items`.
- **Ontology fit:** Best source for `:Outfit`, `:hasTop`, `:hasBottom`, `:hasFootwear`, `:hasAccessory`, and compatibility-oriented SPARQL examples.

## What I downloaded

The project includes a small reproducible downloader:

```bash
python scripts/download_dataset_samples.py --hm-length 100 --polyvore-length 50
```

It writes:

- `data/samples/hm_articles_sample.csv`
- `data/samples/hm_articles_sample.jsonl`
- `data/samples/polyvore_outfits_sample.csv`
- `data/samples/polyvore_outfits_sample.jsonl`
- `data/samples/metadata.json`

These samples are intentionally small. They are enough for mapping, SPARQL examples, SHACL shapes, and report screenshots without committing large datasets.

## Full download options

### Option A: H&M via Kaggle

Use this if the final project needs the complete H&M dataset.

Requirements:

1. Create or log into a Kaggle account.
2. Open the H&M competition page and accept the rules.
3. Create a Kaggle API token from Account settings.
4. Put `kaggle.json` in the expected Kaggle config directory.

Command:

```bash
kaggle competitions download -c h-and-m-personalized-fashion-recommendations -p data/full/hm
```

Do not commit the full downloaded archive or extracted raw files.

### Option B: Polyvore outfit JSON via Hugging Face

Use this if the final project needs all Polyvore disjoint outfit groupings.

PowerShell:

```powershell
New-Item -ItemType Directory -Force data/full/polyvore
Invoke-WebRequest `
  -Uri "https://huggingface.co/datasets/owj0421/polyvore-outfits/resolve/main/disjoint_default/train.json?download=true" `
  -OutFile "data/full/polyvore/disjoint_default_train.json"
```

Do not commit full raw files.

## Ontology mapping plan

| Dataset | Source field | Ontology target |
|---|---|---|
| H&M | `article_id` | item URI, e.g. `:HM_0108775015` |
| H&M | `prod_name` | `rdfs:label` |
| H&M | `product_type_name` | `rdf:type` mapped to a clothing subclass |
| H&M | `product_group_name` / `garment_group_name` | fallback class mapping |
| H&M | `colour_group_name` / `perceived_colour_master_name` | `:hasColor` |
| H&M | `index_group_name` | possible `:isSuitableFor` |
| H&M | `detail_desc` | material/formality/season extraction candidate |
| Polyvore | `set_id` | `:Outfit` individual |
| Polyvore | `items` | outfit component links after item-category mapping |

## Practical implementation plan

1. Use the small samples first, not the full datasets.
2. Create a mapping dictionary for H&M product types into ontology classes.
3. Normalize H&M color names into existing `:Color` individuals.
4. Generate a small Turtle ABox file from 50-100 H&M products.
5. Generate 10-20 `:Outfit` individuals from Polyvore rows.
6. Add SHACL shapes for required outfit parts and valid color ranges.
7. Add SPARQL queries that demonstrate retrieval over the populated graph.

