# Widoco Instructions

WIDOCO is a build tool and is **not committed** to the repository. Download the
`widoco-x.y.z-jar-with-dependencies_JDK-17.jar` from the
[WIDOCO releases page](https://github.com/dgarijo/Widoco/releases) and place it at the
repository root (it is git-ignored). Requires Java 17.

Use this command from the repository root to regenerate the ontology documentation after
changing `Clothing_Ontology.ttl`:

```bash
java -jar widoco-*-jar-with-dependencies_JDK-17.jar \
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
