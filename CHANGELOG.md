# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-13

### Added

- **Outfit Module**: New classes for `Outfit`, `HarmoniousOutfit`, `FormalOutfit`, `CasualOutfit`
- **User Module**: Support for user preferences, style categories, body types
- **Color Theory Extensions**: `colorHarmonizesWith`, `isComplementaryTo`, `ColorUndertone`
- **Formality Levels**: `CasualLevel`, `SmartCasualLevel`, `BusinessCasualLevel`, `FormalLevel`
- **SWRL Rule R1**: Machine-readable color-harmony pairing rule
- **LLM Integration**: Mock and Ollama-based ontology enrichment pipeline
- **SHACL Validation**: 9 shape definitions for data quality assurance
- **Flask Web UI**: Dashboard, product catalog browser, outfit recommendation engine
- **SPARQL Queries**: 7 predefined queries for outfit discovery and analytics
- **H&M Dataset**: 1,962 products mapped to ontology (98.1% acceptance rate)
- **Data Pipeline**: End-to-end CSV→RDF generation with LLM enrichment
- **WIDOCO Documentation**: Generated HTML documentation with ontology hierarchy
- **Recommendation Engine**: Color harmony-aware scoring with material and season matching
- **Test Suite**: 20+ unit tests for pipeline, recommendation, and validation

### Changed

- **Ontology Alignment**: schema.org integration via `rdfs:subClassOf` and `rdfs:subPropertyOf`
- **Property Ranges**: All properties now have explicit domain and range definitions
- **Functional Properties**: Marked `hasMaterial`, `hasFormality`, `hasColor` as functional
- **Deprecation**: Removed unused `untitled-ontology-3:` prefix (backwards compatible)

### Fixed

- Color mapping normalization (8 base materials supported)
- Season/formality inference from product descriptions
- SHACL validation for combined TBox + ABox graphs

### Removed

- Phase 1 taxonomy-only approach (superseded by full ontology)

---

## [1.0.0] - 2026-05-14

### Added

- **Initial Ontology (TBox)**: Clothing item taxonomy with attributes
- **Core Classes**: `ClothingItem`, `Top`, `Bottom`, `Outerwear`, `Footwear`, `Accessory`
- **Base Attributes**: Color, Material, Size, Season, Occasion, Gender
- **Dublin Core Integration**: Metadata support via DC Terms vocabulary
- **VANN Vocabulary**: Preferred prefix and namespace declarations
- **Widoco Documentation**: Initial HTML generation
- **SPARQL Query Foundation**: Query templates for exploration

---

## Unreleased (In Progress)

### Planned Features

- [ ] Real LLM fine-tuning for improved extraction
- [ ] User collaborative filtering for personalized recommendations
- [ ] Temporal trend analysis for seasonal collections
- [ ] Multi-user outfit sharing and curation platform
- [ ] Fashion influencer integration
- [ ] Price-based recommendation filtering
- [ ] Brand/designer attribute support
- [ ] Sustainability metrics (eco-friendly materials)
- [ ] Mobile app (React Native)
- [ ] GraphQL API endpoint

### Known Issues

- Color mapping coverage at 77% (375 items unmapped)
- Ontology missing categories (Underwear, Socks, Sleepwear, Hosiery)
- Mock LLM uses heuristics vs. neural inference
- Single-user mode (no multi-user support yet)

---

## Version History Details

### Phase 2 Accomplishments (v2.0.0)

- **Research Integration**: Incorporated findings from Babaei Giglou et al. (2023) "LLMs4OL"
- **Neuro-symbolic Approach**: Cited Fernandez et al. (2023) for future learning improvements
- **Modular Design**: Four independent modules following MOMo methodology
- **Competency Questions**: All 7 CQs addressed by ontology
- **Validation**: SHACL shapes ensure data quality (0 violations)
- **Reproducibility**: Mock LLM fixture enables offline testing

### Phase 1 Foundations (v1.0.0)

- Core ontology structure
- Basic attribute modeling
- Documentation scaffolding

---

## Installation & Usage

### For End Users

```bash
pip install -r requirements.txt
python app.py
# Navigate to http://127.0.0.1:5000
```

### For Developers

```bash
pip install -e ".[dev]"
pytest
black . && flake8 .
```

### Run Data Pipeline

```bash
# Mock mode (no external LLM)
python scripts/run_pipeline.py --llm-mode mock

# Ollama mode (requires local LLM)
python scripts/run_pipeline.py --llm-mode ollama --ollama-model llama3.1
```

---

## Citation

If you use this ontology in your research, please cite:

```bibtex
@software{clothing_ontology_2026,
  title={Clothing Ontology: An OWL 2 Ontology for Outfit Recommendation},
  author={Sedat},
  year={2026},
  url={https://github.com/your-username/clothing-ontology},
  license={CC BY 4.0}
}
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Babaei Giglou et al. (2023) - LLMs for Ontology Learning
- Fernandez et al. (2023) - Neuro-symbolic learning approaches
- Schema.org team - Reusable vocabulary foundation
- RDFlib, pyshacl, Flask communities - Excellent open-source tools

## Roadmap

- Q3 2026: Real LLM integration and fine-tuning
- Q4 2026: User preference learning system
- Q1 2027: Mobile application launch
- Q2 2027: GraphQL API and REST endpoints
