# Widoco Instructions

Use this command from the repository root to regenerate the ontology documentation after changing `Clothing_Ontology.ttl`:

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

The generated entry point is:

```text
docs/widoco/doc/index-en.html
```

Keep `Clothing_Ontology.ttl` as the canonical source and regenerate Widoco whenever the ontology TBox, ABox examples, metadata, or annotations change.
