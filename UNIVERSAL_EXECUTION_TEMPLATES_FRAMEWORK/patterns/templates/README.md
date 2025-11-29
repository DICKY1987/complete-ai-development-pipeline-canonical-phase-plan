# Templates Directory

**Purpose**: Template assets and examples used across pattern authoring and documentation.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `example-items.json` | Sample data items for template-driven generation |
| `gui-doc-assembly-pattern.yaml` | Template for GUI/TUI documentation assembly |
| `module-readme.md` | Starter README template for generated modules |
| `README.yaml` | Machine-readable directory metadata |

---

## Usage

### Copy and Adapt Templates

```bash
# Copy module README template
cp module-readme.md ../path/to/new/module/README.md

# Edit for your module
```

### Template-Driven Generation

Use `example-items.json` structure when creating:

- Pattern examples
- Documentation bundles
- Module scaffolding

### GUI Documentation

The `gui-doc-assembly-pattern.yaml` provides:

- Structure for GUI/TUI documentation
- Standard sections and formatting
- Integration points

---

## Template Structure

### module-readme.md

Standard sections:

1. Title and purpose
2. Contents/structure
3. Usage instructions
4. Related resources

### example-items.json

```json
{
  "items": [
    {
      "id": "item-001",
      "name": "Example Item",
      "properties": {}
    }
  ]
}
```

---

## Contributing

When adding new templates:

1. Follow existing naming conventions
2. Include usage instructions in the template
3. Add entry to this README

---

## Related

- `../specs/` - Pattern specifications (may use templates)
- `../examples/` - Generated examples from templates
- `../docs/` - Documentation that may use templates
