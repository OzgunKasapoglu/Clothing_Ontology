# H&M Description Ontology Extraction Prompt

You are extracting controlled ontology values from one H&M product row.

Use only the product text provided by the caller. Focus on `detail_desc`; use `prod_name`, `product_type_name`, and `product_group_name` only as supporting context when the description is ambiguous.

Return exactly one JSON object matching `prompts/llm_extraction_schema.json`. Do not include prose, markdown, or extra keys.

Extraction rules:

- `article_id`: copy the source `article_id` exactly.
- `material`: choose one ontology material individual only when directly supported by text.
- `formality`: choose the closest ontology formality level from the allowed list.
- `season`: return one or more allowed season individuals when supported by fabric, garment type, or explicit seasonal language.
- `confidence`: number from `0.0` to `1.0`.
- `evidence`: short phrase copied or paraphrased from the input that supports the extraction.

If a value is uncertain or outside the ontology vocabulary, return `null` for that field and lower the confidence. Do not invent new ontology individuals.

Input format:

```json
{
  "article_id": "...",
  "prod_name": "...",
  "product_type_name": "...",
  "product_group_name": "...",
  "detail_desc": "..."
}
```
