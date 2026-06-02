from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_llm_enriched_abox import generate_llm_enriched_abox, parse_llm_json
from scripts.run_pipeline import aggregate_summary


class PipelineSummaryTests(unittest.TestCase):
    def test_aggregate_summary_extracts_counts(self) -> None:
        summary = aggregate_summary(
            hm_metadata={"items_generated": 9, "items_skipped": 1},
            enrichment_metadata={
                "enriched_products": 3,
                "skipped_due_to_low_confidence": 2,
                "skipped_due_to_unknown_ontology_value": 1,
                "skipped_due_to_missing_article_id": 1,
                "skipped_due_to_absent_catalog_item": 4,
                "skipped_total": 8,
                "counters": {"material:Cotton": 2, "formality:CasualLevel": 3, "season:Summer": 1},
            },
            shacl_summary={"conforms": True, "validation_result_count": 0},
            sparql_results={"results": [{"query": "queries/example.rq", "row_count": 7}]},
        )

        self.assertEqual(summary["hm_items_generated"], 9)
        self.assertEqual(summary["enriched_products"], 3)
        self.assertEqual(summary["skipped_due_to_absent_catalog_item"], 4)
        self.assertEqual(summary["material_counts"], {"Cotton": 2})
        self.assertEqual(summary["sparql_query_row_counts"], {"example.rq": 7})


class EnrichmentValidationTests(unittest.TestCase):
    def test_mock_records_are_validated_and_classified(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mock_input = root / "mock.jsonl"
            catalog_graph = root / "catalog.ttl"
            output = root / "enriched.ttl"
            metadata_output = root / "metadata.json"

            records = [
                {
                    "article_id": "1",
                    "material": "Cotton",
                    "formality": "casual",
                    "season": ["Summer"],
                    "confidence": 0.95,
                    "evidence": "cotton jersey",
                },
                {
                    "article_id": "2",
                    "material": "Cotton",
                    "formality": "CasualLevel",
                    "season": ["Summer"],
                    "confidence": 0.2,
                    "evidence": "unclear",
                },
                {
                    "article_id": "3",
                    "material": "Fleece",
                    "formality": "CasualLevel",
                    "season": ["Winter"],
                    "confidence": 0.9,
                    "evidence": "fleece",
                },
                {
                    "article_id": "",
                    "material": "Cotton",
                    "formality": "CasualLevel",
                    "season": ["Summer"],
                    "confidence": 0.9,
                    "evidence": "missing id",
                },
                {
                    "article_id": "999",
                    "material": "Cotton",
                    "formality": "CasualLevel",
                    "season": ["Summer"],
                    "confidence": 0.9,
                    "evidence": "not in catalog",
                },
            ]
            mock_input.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            catalog_graph.write_text(
                """@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix clo: <http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/> .

clo:HM_1 dcterms:identifier "1" .
clo:HM_2 dcterms:identifier "2" .
clo:HM_3 dcterms:identifier "3" .
""",
                encoding="utf-8",
            )

            metadata = generate_llm_enriched_abox(
                mock_input=mock_input,
                catalog_graph=catalog_graph,
                output_path=output,
                metadata_output=metadata_output,
                min_confidence=0.7,
            )

            self.assertEqual(metadata["enriched_products"], 1)
            self.assertEqual(metadata["skipped_due_to_low_confidence"], 1)
            self.assertEqual(metadata["skipped_due_to_unknown_ontology_value"], 1)
            self.assertEqual(metadata["skipped_due_to_missing_article_id"], 1)
            self.assertEqual(metadata["skipped_due_to_absent_catalog_item"], 1)
            self.assertTrue(output.exists())

    def test_invalid_ollama_json_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_llm_json("{not json")

    def test_invalid_ollama_schema_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_llm_json(json.dumps([{"article_id": "1"}]))


if __name__ == "__main__":
    unittest.main()
