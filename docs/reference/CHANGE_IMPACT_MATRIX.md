# Change Impact Matrix

**Purpose:** Document critical dependencies in the codebase so that AI agents and developers can predict ripple effects before making changes.

**Last Updated:** 2025-11-22  
**Maintainer:** System Architecture Team

---

## How to Use This Matrix

When changing a component, check this matrix to see what else must be updated. Each entry includes:
- **Triggering Changes:** What kind of changes to the component
- **Mandatory Updates:** What files/systems MUST be updated
- **Validation:** How to verify the change didn't break anything

---

## Component: Schema Definitions (`schema/`)

### Triggering Changes
- Adding/removing fields in JSON schemas
- Changing field types or constraints
- Adding new schema files

### Mandatory Updates
- [ ] **Regenerate Indices:** Run `python scripts/generate_spec_index.py`
- [ ] **Update Code:** Modify code that reads/writes the changed schema
- [ ] **Update Tests:** Add/modify tests for schema validation
- [ ] **Update Documentation:** Document schema changes in relevant specs
- [ ] **Version Bump:** Update schema version if breaking change

### Validation
```bash
# Validate all schemas
python scripts/validate_schemas.py

# Validate all workstreams against new schema
python scripts/validate_workstreams.py

# Run schema-related tests
pytest tests/ -k schema
```

### Examples
- **Change:** Add `priority` field to `workstream.schema.json`
- **Impact:** Update `core/engine/orchestrator.py`, add priority scheduling logic, update all example workstreams

---

## Component: Core State Database (`core/state/db.py`)

### Triggering Changes
- Database schema migrations
- Adding new CRUD functions
- Changing transaction semantics

### Mandatory Updates
- [ ] **Migration Script:** Create migration in `schema/migrations/XXX_description.sql`
- [ ] **Update Tests:** Add/update tests in `tests/core/test_db.py`
- [ ] **Update Orchestrator:** If state machine changes, update `core/engine/orchestrator.py`
- [ ] **Update Documentation:** Document new functions in docstrings and `docs/reference/`
- [ ] **Bump Schema Version:** Increment `SCHEMA_VERSION` constant

### Validation
```bash
# Run database tests
pytest tests/core/test_db.py -v

# Test migration on fresh database
rm -f .worktrees/pipeline_state.db
python -c "from core.state.db import init_db; init_db('.worktrees/pipeline_state.db')"

# Verify schema version
sqlite3 .worktrees/pipeline_state.db "SELECT version FROM schema_version;"
```

### Examples
- **Change:** Add `estimated_duration` column to `workstreams` table
- **Impact:** Create migration, update `create_workstream()` function, add to tests

---

## Component: Workstream Bundles (`workstreams/`)

### Triggering Changes
- Adding new example workstreams
- Modifying existing workstream structure
- Changing step dependencies

### Mandatory Updates
- [ ] **Validate Bundle:** Run `python scripts/validate_workstreams.py <bundle>`
- [ ] **Test Execution:** Actually execute the workstream to verify it works
- [ ] **Update Index:** If adding new bundle, update workstream index
- [ ] **Update Documentation:** Add description to workstream catalog

### Validation
```bash
# Validate single bundle
python scripts/validate_workstreams.py workstreams/your-bundle.json

# Validate all bundles
python scripts/validate_workstreams.py

# Test execution (dry-run mode if available)
python scripts/run_workstream.py workstreams/your-bundle.json --dry-run
```

### Examples
- **Change:** Add new `phase-k-plus-bundle.json`
- **Impact:** Validate against schema, test execution, document in README

---

## Component: Error Detection Plugins (`error/plugins/`)

### Triggering Changes
- Adding new error detection plugin
- Modifying plugin interface
- Changing error reporting format

### Mandatory Updates
- [ ] **Plugin Manifest:** Create/update `manifest.json` in plugin directory
- [ ] **Update Plugin Manager:** If interface changes, update `error/engine/plugin_manager.py`
- [ ] **Update Tests:** Add plugin tests in `tests/error/plugins/test_<plugin>.py`
- [ ] **Update Documentation:** Add plugin to `error/plugins/README.md`
- [ ] **Update Error Catalog:** Document new error types in `docs/reference/ERROR_CATALOG.md`

### Validation
```bash
# Test plugin discovery
python -c "from error.engine.plugin_manager import discover_plugins; print(discover_plugins())"

# Test specific plugin
pytest tests/error/plugins/test_your_plugin.py -v

# Run plugin on sample files
python error/engine/error_engine.py --plugin your_plugin --files test_data/
```

### Examples
- **Change:** Add `javascript_eslint` plugin
- **Impact:** Create manifest.json, implement plugin.py, add tests, update README

---

## Component: Specification Tools (`specifications/tools/`)

### Triggering Changes
- Adding new spec processing tool
- Modifying spec URI resolution logic
- Changing spec index generation

### Mandatory Updates
- [ ] **Regenerate Spec Index:** Run `python specifications/tools/indexer/indexer.py`
- [ ] **Update Cross-References:** Run `python scripts/generate_cross_references.py`
- [ ] **Update Tests:** Test tool changes with sample specs
- [ ] **Update Documentation:** Document tool usage in `specifications/tools/README.md`

### Validation
```bash
# Regenerate and validate spec index
python specifications/tools/indexer/indexer.py
python specifications/tools/guard/guard.py --validate-all

# Test URI resolution
python -c "from specifications.tools.resolver import resolve_uri; print(resolve_uri('spec://core/state/db'))"

# Run spec tool tests
pytest tests/specifications/tools/ -v
```

### Examples
- **Change:** Modify spec indexer to include implementation status
- **Impact:** Regenerate index, update tests, verify all specs index correctly

---

## Component: Documentation (`docs/`)

### Triggering Changes
- Adding new documentation files
- Moving/renaming documentation
- Changing documentation structure

### Mandatory Updates
- [ ] **Update Doc Index:** Run `python scripts/generate_doc_index.py`
- [ ] **Fix Broken Links:** Run `python scripts/generate_doc_index.py --fail-on-broken-links`
- [ ] **Update DOCUMENTATION_INDEX.md:** Add new docs to manual index if needed
- [ ] **Update Cross-References:** Ensure bidirectional links work

### Validation
```bash
# Generate doc index and check for broken links
python scripts/generate_doc_index.py --fail-on-broken-links

# Lint markdown (if configured)
npm run lint:md  # or markdownlint docs/**/*.md

# Check for orphaned docs (not linked from anywhere)
python scripts/find_orphaned_docs.py
```

### Examples
- **Change:** Move `docs/spec/` to `specifications/content/`
- **Impact:** Update all links, regenerate doc index, fix broken references

---

## Component: Scripts (`scripts/`)

### Triggering Changes
- Adding new automation scripts
- Changing script interfaces (arguments, environment variables)
- Moving scripts to different locations

### Mandatory Updates
- [ ] **Update Tests:** Add tests in `tests/scripts/` if testable logic
- [ ] **Update Documentation:** Document script usage in comments or `scripts/README.md`
- [ ] **Update CI:** If CI uses the script, update `.github/workflows/`
- [ ] **Update Other Scripts:** If other scripts call this one, update them

### Validation
```bash
# Run script with --help to verify interface
python scripts/your_script.py --help

# Test script on sample data
python scripts/your_script.py --test-mode

# Check for hardcoded paths (anti-pattern)
grep -r "/Users/\|C:\\\\" scripts/
```

### Examples
- **Change:** Add `--fail-on-warnings` flag to `validate_workstreams.py`
- **Impact:** Update CI to use new flag, document in help text, test both modes

---

## Component: ADRs (`docs/adr/`)

### Triggering Changes
- Adding new Architecture Decision Record
- Superseding existing ADR
- Marking ADR as deprecated

### Mandatory Updates
- [ ] **Update ADR Index:** Add to `docs/adr/README.md` table
- [ ] **Update Related ADRs:** Add cross-references to related decisions
- [ ] **Update Documentation:** Link from relevant specs/guides
- [ ] **Update Implementation:** If ADR describes new pattern, ensure code follows it

### Validation
```bash
# Verify ADR follows template
diff docs/adr/XXXX-title.md docs/adr/template.md  # Should have same sections

# Check for broken links in ADR
python scripts/generate_doc_index.py --fail-on-broken-links --files docs/adr/

# Ensure ADR is linked from somewhere
grep -r "XXXX-title" docs/
```

### Examples
- **Change:** Add ADR-0009 for new decision
- **Impact:** Update ADR README index, link from ARCHITECTURE.md, update related ADRs

---

## Component: Test Suites (`tests/`)

### Triggering Changes
- Adding new test files
- Changing test fixtures
- Modifying test data

### Mandatory Updates
- [ ] **Run Tests:** Ensure new tests pass locally
- [ ] **Update CI:** If new test requirements, update CI config
- [ ] **Update Test Documentation:** Document complex fixtures or test patterns
- [ ] **Update Coverage:** Ensure coverage doesn't drop significantly

### Validation
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/your_new_test.py -v

# Check coverage
pytest --cov=core --cov=error --cov-report=html

# Verify CI will pass
pytest --no-cov -q  # Quick CI-style run
```

### Examples
- **Change:** Add integration tests for workstream execution
- **Impact:** Ensure tests are deterministic, add to CI, document test data requirements

---

## Component: Configuration Files (`config/`)

### Triggering Changes
- Adding new tool profiles
- Changing circuit breaker settings
- Modifying decomposition rules

### Mandatory Updates
- [ ] **Validate Config:** Ensure valid JSON/YAML against schema
- [ ] **Update Tests:** Test code that reads this config
- [ ] **Update Documentation:** Document config options in comments or docs
- [ ] **Update Examples:** Provide example config for common use cases

### Validation
```bash
# Validate JSON config
python -m json.tool config/your_config.json > /dev/null

# Validate YAML config
python -c "import yaml; yaml.safe_load(open('config/your_config.yaml'))"

# Test config is loaded correctly
python -c "from core.engine.tools import load_tool_profiles; print(load_tool_profiles())"
```

### Examples
- **Change:** Add timeout setting to `config/tool_profiles.json`
- **Impact:** Update tool adapter to respect timeout, add tests, document setting

---

## Cross-Cutting Concerns

### Python Import Path Changes

**Trigger:** Refactoring code location (e.g., `src/pipeline/` → `core/`)

**Mandatory Updates:**
- [ ] Update all import statements across codebase
- [ ] Update `__init__.py` exports
- [ ] Update tests imports
- [ ] Update documentation code examples
- [ ] Add deprecation warnings for old imports (if public API)
- [ ] Update CI path checks

**Validation:**
```bash
# Find old import patterns
grep -r "from src.pipeline" .

# Verify new imports work
python -c "from core.state import db; from error.engine import error_engine"

# Run all tests with new imports
pytest -v
```

---

## Dependency Changes

**Trigger:** Adding/removing Python dependencies in `requirements.txt`

**Mandatory Updates:**
- [ ] Update virtual environment: `pip install -r requirements.txt`
- [ ] Update CI dependencies
- [ ] Run security check: `pip-audit` or `safety check`
- [ ] Update documentation if user-facing dependency
- [ ] Test that all imports still work

**Validation:**
```bash
# Install and verify
pip install -r requirements.txt
python -c "import new_dependency; print(new_dependency.__version__)"

# Run tests
pytest -v
```

---

## Summary Table

| Component | Key Files | Validation Command | Regenerate Command |
|-----------|-----------|-------------------|-------------------|
| **Schemas** | `schema/*.json` | `python scripts/validate_schemas.py` | N/A |
| **Database** | `core/state/db.py` | `pytest tests/core/test_db.py` | Create migration SQL |
| **Workstreams** | `workstreams/*.json` | `python scripts/validate_workstreams.py` | N/A |
| **Plugins** | `error/plugins/*/` | `pytest tests/error/plugins/` | Update manifest |
| **Specs** | `specifications/` | `specifications/tools/guard/guard.py` | `specifications/tools/indexer/indexer.py` |
| **Docs** | `docs/` | `python scripts/generate_doc_index.py --fail-on-broken-links` | `python scripts/generate_doc_index.py` |
| **Scripts** | `scripts/` | `pytest tests/scripts/` | N/A |
| **ADRs** | `docs/adr/` | Check links | Update `adr/README.md` |
| **Tests** | `tests/` | `pytest -v` | N/A |
| **Config** | `config/` | Validate JSON/YAML | N/A |

---

## Related Documentation

- [ADR-0004: Section-Based Organization](../adr/0004-section-based-organization.md) - Code organization rationale
- [CI Path Standards](../CI_PATH_STANDARDS.md) - Enforced import path rules
- [Testing Strategy](../guidelines/TESTING_STRATEGY.md) - How to test changes
- [Anti-Patterns Catalog](../guidelines/ANTI_PATTERNS.md) - Common mistakes to avoid

---

## Maintenance

This matrix should be updated when:
- New components are added to the system
- New dependencies between components are discovered
- Validation procedures change
- Breaking changes occur

**Owner:** System Architecture Team  
**Review Frequency:** Monthly or after major refactorings
