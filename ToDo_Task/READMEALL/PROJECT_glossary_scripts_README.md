# Glossary Tooling

**Purpose**: Tools for maintaining, validating, and updating the repository glossary.

---

## Quick Start

```bash
# Validate glossary
python scripts/glossary/validate_glossary.py

# Check for orphaned terms
python scripts/glossary/validate_glossary.py --check-orphans

# Verify implementation paths
python scripts/glossary/validate_glossary.py --check-paths

# Quick structure check
python scripts/glossary/validate_glossary.py --quick
```

---

## Available Tools

### validate_glossary.py

**Purpose**: Validate glossary structure, content, and cross-references

**Usage**:
```bash
# Full validation (all checks)
python validate_glossary.py

# Quick validation (structure only)
python validate_glossary.py --quick

# Check for orphaned terms (not linked by any other term)
python validate_glossary.py --check-orphans

# Verify implementation paths exist
python validate_glossary.py --check-paths
```

**Checks**:
- ✅ Required sections present
- ✅ Alphabetical ordering
- ✅ Required fields (Category, Definition)
- ✅ Definition quality (length, style)
- ✅ Cross-reference validity
- ✅ Metadata schema compliance
- ✅ Implementation paths exist
- ⚠️ Orphaned terms
- ⚠️ Missing examples
- ⚠️ Quality metrics

**Exit Codes**:
- `0` - All checks passed (warnings allowed)
- `1` - Validation errors found

---

### update_term.py *(Coming Soon)*

**Purpose**: Update glossary terms using patch-based workflow

**Usage**:
```bash
# Update single term field
python update_term.py \
  --term TERM-ENGINE-001 \
  --field implementation \
  --value "core/engine/orchestrator.py"

# Bulk update from specification
python update_term.py \
  --spec glossary-updates/add-schemas.yaml \
  --dry-run  # Preview changes first

# Apply patch
python update_term.py \
  --spec glossary-updates/add-schemas.yaml \
  --apply
```

**Features**:
- Patch-based updates (atomic, reviewable)
- Dry-run mode
- Automatic metadata updates
- Changelog generation
- Validation before apply

---

### extract_terms.py *(Coming Soon)*

**Purpose**: Auto-extract term definitions from code and documentation

**Usage**:
```bash
# Scan codebase for new terms
python extract_terms.py --scan core/ engine/ error/

# Extract from markdown glossary
python extract_terms.py --from-markdown glossary.md

# Propose new terms
python extract_terms.py --scan core/ --propose
```

**Output**:
```yaml
proposed_terms:
  - name: "Circuit Breaker"
    category: "Core Engine"
    source_file: "core/engine/circuit_breakers.py"
    definition_hint: "Resilience pattern that prevents cascading failures"
    confidence: 0.85
    status: "proposed"
```

---

### add_term.py *(Coming Soon)*

**Purpose**: Interactive tool for adding new terms

**Usage**:
```bash
# Interactive mode
python add_term.py --interactive

# From template
python add_term.py --template docs/glossary-templates/core-engine.yaml

# From proposal
python add_term.py --from-proposal glossary-proposals/new-term.yaml
```

**Interactive Prompts**:
1. Term name
2. Category selection
3. Definition
4. Implementation files (optional)
5. Related terms (optional)
6. Status (proposed/draft/active)

---

### generate_glossary_index.py *(Coming Soon)*

**Purpose**: Generate machine-readable indices and relationship graphs

**Usage**:
```bash
# Generate all outputs
python generate_glossary_index.py

# JSON index only
python generate_glossary_index.py --json-only

# Graph visualization only
python generate_glossary_index.py --graph-only
```

**Outputs**:
- `docs/glossary_index.json` - Full term index
- `docs/glossary_graph.dot` - Graphviz relationship graph
- `docs/glossary_stats.md` - Quality metrics report

---

## File Structure

```
scripts/glossary/
├── README.md                    # This file
├── validate_glossary.py         # ✅ Validation tool (available)
├── update_term.py               # 🚧 Update tool (coming soon)
├── extract_terms.py             # 🚧 Extraction tool (coming soon)
├── add_term.py                  # 🚧 Interactive add (coming soon)
└── generate_glossary_index.py  # 🚧 Index generator (coming soon)

glossary-updates/                # Patch specifications
├── add-uet-schemas.yaml
├── add-uet-schemas.patch
└── README.md

glossary-proposals/              # New term proposals
├── new-term-1.yaml
└── README.md

config/
└── glossary_policy.yaml         # Validation rules

docs/
├── DOC_GLOSSARY_GOVERNANCE.md   # Governance framework
├── DOC_GLOSSARY_SCHEMA.md       # Term schema
├── DOC_GLOSSARY_CHANGELOG.md    # Update history
├── glossary_index.json          # Generated index
└── glossary_graph.dot           # Generated graph

.glossary-metadata.yaml          # Term metadata (git-tracked)
glossary.md                      # Main glossary (user-facing)
```

---

## Development Workflow

### Adding a New Term

1. **Propose term**:
   ```bash
   python scripts/glossary/add_term.py --interactive
   # Or create YAML in glossary-proposals/
   ```

2. **Review**: Architecture team reviews proposal

3. **Draft**: Write full definition
   ```bash
   # Edit glossary.md directly or use:
   python scripts/glossary/update_term.py --term TERM-XXX-NNN --status draft
   ```

4. **Activate**: Promote to active
   ```bash
   python scripts/glossary/update_term.py --term TERM-XXX-NNN --status active
   ```

5. **Validate**:
   ```bash
   python scripts/glossary/validate_glossary.py
   ```

### Updating Existing Terms

1. **Small edits**: Edit `glossary.md` directly
2. **Large/bulk updates**: Use patch workflow
   ```bash
   # Create spec
   cat > glossary-updates/update-001.yaml <<EOF
   patch_id: "01J4XY..."
   description: "Add schemas"
   terms:
     - term_id: TERM-ENGINE-001
       action: update
       field: schema_refs
       value: ["schema/workstream.schema.json"]
   EOF
   
   # Generate and apply patch
   python scripts/glossary/update_term.py --spec glossary-updates/update-001.yaml
   ```

3. **Validate**:
   ```bash
   python scripts/glossary/validate_glossary.py
   ```

### Deprecating Terms

1. **Mark deprecated**:
   ```bash
   python scripts/glossary/update_term.py \
     --term TERM-OLD-XXX \
     --status deprecated \
     --replacement TERM-NEW-XXX \
     --reason "Replaced by improved implementation"
   ```

2. **Add migration guide** in glossary.md

3. **Keep for 2+ releases** before archiving

### CI Integration

Add to `.github/workflows/glossary-validation.yml`:

```yaml
name: Glossary Validation

on:
  pull_request:
    paths:
      - 'glossary.md'
      - '.glossary-metadata.yaml'
      - 'docs/DOC_GLOSSARY_*.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Validate glossary
        run: python scripts/glossary/validate_glossary.py
```

---

## Configuration

### glossary_policy.yaml

```yaml
# config/glossary_policy.yaml

validation:
  definition:
    min_length: 20
    max_length: 1000
    required_patterns:
      - "\\b(Component|Process|Pattern|System|Tool)\\b"
    forbidden_patterns:
      - "^It is"
      - "^This is"
      - "\\bTODO\\b"
  
  related_terms:
    min_count: 1
    max_count: 10
    require_bidirectional: true
  
  implementation:
    verify_files_exist: true
  
  cross_references:
    max_orphaned_terms: 0
    max_dead_links: 0

quality_targets:
  terms_with_implementation_pct: 90
  terms_with_examples_pct: 85
  avg_related_terms: 3.0
```

---

## Troubleshooting

### "Missing required section"

**Cause**: Glossary.md missing required section header

**Fix**: Add the section header, e.g.:
```markdown
## Quick Reference
```

### "Term out of alphabetical order"

**Cause**: Terms not sorted within their alphabetical section

**Fix**: Move the term to correct alphabetical position

### "Invalid term_id format"

**Cause**: Term ID doesn't match `TERM-XXX-NNN` pattern

**Fix**: Rename to correct format, e.g., `TERM-ENGINE-001`

### "Term links to non-existent term"

**Cause**: Related term reference is broken

**Fix**: Either:
- Add the missing term
- Remove the broken link
- Fix the term name spelling

### "Orphaned terms found"

**Cause**: Term has no incoming links from other terms

**Fix**: Add related term links in other relevant terms

---

## Future Enhancements

### Planned Features

1. **Auto-sync with codebase**
   - Detect new classes/functions
   - Propose glossary entries
   - Update implementation paths

2. **Visual relationship graph**
   - Interactive web viewer
   - Filter by category
   - Highlight orphans/clusters

3. **LLM-assisted definitions**
   - Generate draft definitions from code
   - Suggest related terms
   - Improve clarity

4. **Version control integration**
   - Git hooks for validation
   - Auto-update changelog
   - Track term evolution

---

## Related Documents

- **[DOC_GLOSSARY_GOVERNANCE.md](../../docs/DOC_GLOSSARY_GOVERNANCE.md)** - Governance framework
- **[DOC_GLOSSARY_SCHEMA.md](../../docs/DOC_GLOSSARY_SCHEMA.md)** - Term schema
- **[DOC_GLOSSARY_CHANGELOG.md](../../docs/DOC_GLOSSARY_CHANGELOG.md)** - Update history
- **[glossary.md](../../glossary.md)** - Main glossary

---

## Support

**Questions?** Contact architecture team or create issue with label `glossary-tooling`

**Contribute**: Submit PRs for new tools or improvements
