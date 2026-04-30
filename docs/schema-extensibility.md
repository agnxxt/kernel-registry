# Schema Extensibility Contract

All kernel JSON schemas support semantic extension using:
- `semantic_extension.taxonomy`
- `semantic_extension.vocabulary`
- `semantic_extension.ontology`
- `semantic_extension.attributes`
- `semantic_extension.metadata`

Reference definition:
- `schemas/_semantic-extension.schema.json`

Rules:
1. Core required fields remain stable.
2. Extensions must not redefine core semantics.
3. Taxonomy/vocabulary/ontology versions should be explicit.
4. Vendor-specific additions go in `semantic_extension.attributes`.
