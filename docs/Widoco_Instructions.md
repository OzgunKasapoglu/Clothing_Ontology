# Widoco Documentation — How to Generate

Widoco is a Java tool. I cannot execute it from this environment, but the steps below are exactly what you should run yourself. After running them, commit the generated `docs/widoco/` folder.

## 1. Download Widoco

Go to the latest release page:

  https://github.com/dgarijo/Widoco/releases

Download the file named like `widoco-VERSION-jar-with-dependencies.jar` (one file, ~80 MB) and put it in the project root (next to `Clothing_Ontology.ttl`).

## 2. Run Widoco

From the project root, in a terminal:

```bash
java -jar widoco-*-jar-with-dependencies.jar \
    -ontFile Clothing_Ontology.ttl \
    -outFolder docs/widoco \
    -rewriteAll \
    -getOntologyMetadata \
    -webVowl \
    -includeAnnotationProperties \
    -lang en
```

Notes:
- `-rewriteAll` overwrites any previous output. Safe.
- `-webVowl` includes the interactive WebVOWL visualisation.
- `-getOntologyMetadata` populates the documentation header from the `dcterms:*` annotations already in the Turtle file.
- `-lang en` selects English (the labels and comments are in `@en`).

## 3. Verify

After it finishes you should have:

```
docs/widoco/
  index-en.html
  ontology.html
  webvowl/
  resources/
  ...
```

Open `docs/widoco/index-en.html` in a browser. Confirm that:
- The header shows "Clothing Ontology for Outfit Combination Engine" (from `dcterms:title`).
- Every class has a non-empty description.
- The "Cross reference" section lists Item / Attribute / Outfit / User modules implicitly via the class tree.

## 4. Commit

```bash
git add docs/widoco
git commit -m "Add Widoco-generated documentation for ontology v2"
```

## If Java is not installed

On macOS:
```bash
brew install --cask temurin
```

Then re-run the `java -jar` command above.
