# Spec index and mapping

This directory hosts generated and supporting artifacts for the spec index and
mapping between documentation and code.

## Index tags

- Tags use the form `[IDX-…]` within Markdown or text files.
- The scanner in `scripts/generate_spec_index.py` collects tag, file, and line
  numbers with a short description.

## Mapping table

- The mapping table (`spec_index_map.md`) records IDX → code references and
  metadata such as version and phase.
- Keep paths relative to the repository root.

