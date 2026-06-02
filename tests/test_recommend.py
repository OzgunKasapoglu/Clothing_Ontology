from __future__ import annotations

import unittest
from pathlib import Path

import rdflib
from rdflib import RDF, RDFS, Namespace

from recommend import (
    _find_seed_proxies,
    _score_candidate,
    color_harmonizes,
    get_recommendations,
    parse_phrase,
)

CLO = Namespace("http://www.semanticweb.org/g911/ontologies/2026/3/Clothing-o/")
_ONTOLOGY_TTL = Path(__file__).parent.parent / "Clothing_Ontology.ttl"


def _load_ontology() -> rdflib.Graph:
    g = rdflib.Graph()
    g.parse(_ONTOLOGY_TTL, format="turtle")
    return g


class ParsePhraseTests(unittest.TestCase):
    def test_white_shirt_maps_to_top_white(self) -> None:
        result = parse_phrase("I have a white shirt")
        self.assertEqual(result["role"], "Top")
        self.assertEqual(result["color"], "White")

    def test_unknown_phrase_returns_none_fields(self) -> None:
        result = parse_phrase("something completely random")
        self.assertIsNone(result["role"])
        self.assertIsNone(result["color"])

    def test_empty_phrase_does_not_crash(self) -> None:
        result = parse_phrase("")
        self.assertIsNone(result["role"])
        self.assertIsNone(result["color"])

    def test_blue_jeans_maps_to_bottom_blue(self) -> None:
        result = parse_phrase("I have blue jeans")
        self.assertEqual(result["role"], "Bottom")
        self.assertEqual(result["color"], "Blue")

    def test_white_sneakers_maps_to_footwear_white(self) -> None:
        result = parse_phrase("white sneakers")
        self.assertEqual(result["role"], "Footwear")
        self.assertEqual(result["color"], "White")


class ColorHarmonyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _load_ontology()

    def test_black_harmonizes_with_white(self) -> None:
        self.assertTrue(color_harmonizes(self.graph, "Black", "White"))

    def test_white_harmonizes_with_black_inverse(self) -> None:
        # White colorHarmonizesWith Black → inverse check (c2, prop, c1)
        self.assertTrue(color_harmonizes(self.graph, "White", "Black"))

    def test_red_complementary_to_green(self) -> None:
        self.assertTrue(color_harmonizes(self.graph, "Red", "Green"))

    def test_green_complementary_to_red_inverse(self) -> None:
        self.assertTrue(color_harmonizes(self.graph, "Green", "Red"))

    def test_no_harmony_between_red_and_navy(self) -> None:
        # Neither has a direct harmony assertion with the other
        self.assertFalse(color_harmonizes(self.graph, "Red", "Navy"))


class ClashesWithTests(unittest.TestCase):
    def _graph_with_clash(self) -> rdflib.Graph:
        g = _load_ontology()
        # Add a white top and a blue bottom that clash explicitly
        g.add((CLO.TestWhiteTop, RDF.type, CLO["T-Shirt"]))
        g.add((CLO.TestWhiteTop, CLO.hasColor, CLO.White))
        g.add((CLO.TestBlueBottom, RDF.type, CLO.Jean))
        g.add((CLO.TestBlueBottom, CLO.hasColor, CLO.Blue))
        g.add((CLO.TestWhiteTop, CLO.clashesWith, CLO.TestBlueBottom))
        return g

    def test_clashes_with_excludes_candidate(self) -> None:
        g = self._graph_with_clash()
        # Seed is White Top; TestBlueBottom clashes with TestWhiteTop (the proxy)
        seed = {"role": "Top", "color": "White"}
        proxies = _find_seed_proxies(g, "White", "Top")
        result = _score_candidate(g, seed, CLO.TestBlueBottom, proxies)
        self.assertIsNone(result)

    def test_non_clashing_candidate_is_not_excluded(self) -> None:
        g = self._graph_with_clash()
        # A different blue bottom that has no clashesWith assertion
        g.add((CLO.OtherBlueBottom, RDF.type, CLO.Jean))
        g.add((CLO.OtherBlueBottom, CLO.hasColor, CLO.Blue))
        seed = {"role": "Top", "color": "White"}
        proxies = _find_seed_proxies(g, "White", "Top")
        result = _score_candidate(g, seed, CLO.OtherBlueBottom, proxies)
        self.assertIsNotNone(result)


class RecommendationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _load_ontology()

    def test_white_top_returns_grouped_recommendations(self) -> None:
        seed = {"role": "Top", "color": "White"}
        results = get_recommendations(self.graph, seed)
        self.assertIn("grouped_items", results)
        self.assertIn("outfits", results)
        groups = results["grouped_items"]
        self.assertIn("Bottom", groups)
        self.assertIn("Footwear", groups)
        self.assertGreater(len(groups["Bottom"]), 0)
        self.assertGreater(len(groups["Footwear"]), 0)

    def test_white_top_returns_complete_outfits(self) -> None:
        seed = {"role": "Top", "color": "White"}
        results = get_recommendations(self.graph, seed)
        outfits = results["outfits"]
        self.assertGreater(len(outfits), 0)
        for outfit in outfits:
            roles = outfit["roles"]
            self.assertIn("Top", roles)
            self.assertIn("Bottom", roles)
            self.assertIn("Footwear", roles)

    def test_matching_material_boosts_ranking(self) -> None:
        # Cotton-matching items should rank higher when seed specifies Cotton
        seed_with = {"role": "Top", "color": "White", "material": "Cotton"}
        seed_without = {"role": "Top", "color": "White"}
        res_with = get_recommendations(self.graph, seed_with)
        res_without = get_recommendations(self.graph, seed_without)
        names_with = [i["local_name"] for i in res_with["grouped_items"].get("Bottom", [])]
        names_without = [i["local_name"] for i in res_without["grouped_items"].get("Bottom", [])]
        # If any Bottom items have Cotton, the rankings differ
        cotton_items = [i["local_name"] for i in res_with["grouped_items"].get("Bottom", []) if i.get("material") == "Cotton"]
        if cotton_items:
            self.assertNotEqual(names_with, names_without)

    def test_no_role_returns_empty_results(self) -> None:
        seed = {"role": None, "color": "White"}
        results = get_recommendations(self.graph, seed)
        self.assertEqual(results["grouped_items"], {})
        self.assertEqual(results["outfits"], [])


try:
    import flask as _flask  # noqa: F401
    _FLASK_AVAILABLE = True
except ModuleNotFoundError:
    _FLASK_AVAILABLE = False


@unittest.skipUnless(_FLASK_AVAILABLE, "flask not installed")
class FlaskSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        import app as flask_app
        flask_app.app.config["TESTING"] = True
        self.client = flask_app.app.test_client()

    def test_recommend_get_returns_200(self) -> None:
        resp = self.client.get("/recommend")
        self.assertEqual(resp.status_code, 200)

    def test_recommend_first_post_shows_confirmation_form(self) -> None:
        resp = self.client.post("/recommend", data={"phrase": "I have a white shirt"})
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode()
        self.assertIn("confirmed", body)  # hidden confirmed=1 field present
        self.assertIn("white shirt", body.lower())

    def test_recommend_confirmed_post_shows_results(self) -> None:
        resp = self.client.post("/recommend", data={
            "phrase": "I have a white shirt",
            "role": "Top",
            "color": "White",
            "confirmed": "1",
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode()
        self.assertIn("Bottom", body)

    def test_dashboard_still_works(self) -> None:
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_products_still_works(self) -> None:
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200)

    def test_skipped_still_works(self) -> None:
        resp = self.client.get("/skipped")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
