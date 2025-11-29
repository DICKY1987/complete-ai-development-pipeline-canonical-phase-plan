# Specs Directory

**Purpose**: Specifications, standards, and canonical references  
**Last Updated**: 2025-11-29

---

## Overview

This directory contains the **authoritative specifications** for the Doc ID framework. These are the canonical references that define how the system works.

---

## Files

### Core Specification

**DOC_ID_FRAMEWORK.md** ⭐ **CANONICAL**
- **Primary reference** for the entire framework
- Complete specification of Doc ID system
- ID format and taxonomy
- Lifecycle rules
- Integration patterns
- **Start here** for understanding the system

---

### Registry

**DOC_ID_REGISTRY.yaml** 🔐 **SINGLE SOURCE OF TRUTH**
- Central registry of all doc IDs
- Minted IDs and their metadata
- Status tracking (active, retired, superseded)
- **Never edit manually** - use `tools/doc_id_registry_cli.py`

**Format**:
```yaml
metadata:
  version: "1.0"
  last_updated: "2025-11-29"

ids:
  DOC-CORE-STATE-001:
    category: CORE
    name: STATE
    sequence: 1
    status: active
    created_at: "2025-11-20T10:00:00Z"
    file_path: "core/state/db.py"
```

---

### Architecture Decision Records

**ADR-010-ulid-identity.md**
- Architecture Decision Record
- Why ULID format for IDs
- Alternatives considered
- Decision rationale

**Key Decision**: Use structured IDs (`DOC-<CAT>-<NAME>-<SEQ>`) rather than random ULIDs for human readability and semantic meaning.

---

### Supporting Specs

**UTE_ID_SYSTEM_SPEC.md**
- Universal Execution Templates ID system
- Integration with UET framework
- Cross-system ID coordination

**ID_suite-index.yml**
- Index of ID-related files
- Quick reference
- File locations

---

## ID Specification

From `DOC_ID_FRAMEWORK.md`:

### Format

```
DOC-<CATEGORY>-<NAME>-<SEQUENCE>
```

**Components**:
- `DOC`: Prefix (always constant)
- `<CATEGORY>`: Module category (CORE, ERROR, SPEC, etc.)
- `<NAME>`: Descriptive name in UPPERCASE-KEBAB-CASE
- `<SEQUENCE>`: 3-digit zero-padded number (001, 002, ...)

### Examples

| ID | Category | File |
|---|---------|------|
| `DOC-CORE-STATE-001` | Core | `core/state/db.py` |
| `DOC-ERROR-PLUGIN-002` | Error | `error/plugins/python_ruff.py` |
| `DOC-SPEC-SCHEMA-003` | Spec | `specifications/schema.md` |
| `DOC-PATTERN-EXEC-APPLY-004` | Pattern | `patterns/exec/apply.py` |

---

## Categories

Defined in `DOC_ID_FRAMEWORK.md`:

| Category | Purpose | Example |
|----------|---------|---------|
| **CORE** | Core system modules | State, engine, orchestrator |
| **ERROR** | Error detection & handling | Plugins, error engine |
| **SPEC** | Specifications | Schemas, contracts |
| **PATTERN** | Execution patterns | UET patterns |
| **DOC** | Documentation | Guides, references |
| **TOOL** | Tools & utilities | Scripts, CLI tools |
| **TEST** | Test files | Unit, integration tests |

---

## Lifecycle Rules

From `DOC_ID_FRAMEWORK.md`:

### File Operations

| Operation | ID Behavior | Metadata |
|-----------|-------------|----------|
| **Create** | Mint new ID | `created_at`, `file_path` |
| **Move/Rename** | ID unchanged | `previous_paths`, `moved_at` |
| **Edit** | ID unchanged | `last_modified` |
| **Split** | Primary keeps ID, derived get new | `split_into`, `derived_from` |
| **Merge** | New ID, originals retired | `supersedes`, `superseded_by` |
| **Delete** | Mark retired, never reuse | `retired_at`, `retirement_reason` |

### Key Principle

> **IDs are immutable** - once assigned, an ID never changes. Paths can change, content can change, but the ID is stable.

---

## Validation Rules

From `DOC_ID_FRAMEWORK.md`:

### Format Validation

```python
import re

def is_valid_doc_id(doc_id: str) -> bool:
    pattern = r"^DOC-[A-Z]+-[A-Z0-9-]+-\d{3}$"
    return bool(re.match(pattern, doc_id))
```

### Coverage Requirements

- **Module refactor**: 100% coverage required
- **CI/CD**: 95% coverage minimum
- **General**: Best effort, validated before major changes

---

## Usage

### For Developers

1. **Read the framework**:
   ```bash
   cat specs/DOC_ID_FRAMEWORK.md
   ```

2. **Understand ID format**:
   - Review examples
   - Check category definitions

3. **Mint IDs via registry**:
   ```bash
   cd ../tools
   python doc_id_registry_cli.py mint --category CORE --name MY-MODULE
   ```

### For Tools

1. **Validate against spec**:
   - Check format regex
   - Verify category exists
   - Ensure sequence uniqueness

2. **Reference registry**:
   ```python
   import yaml
   
   with open("specs/DOC_ID_REGISTRY.yaml") as f:
       registry = yaml.safe_load(f)
   ```

3. **Follow lifecycle rules**:
   - Never change existing IDs
   - Mark retired IDs properly
   - Update metadata on changes

---

## Updating Specifications

### Process

1. **Propose change**:
   - Create ADR (Architecture Decision Record)
   - Document rationale

2. **Review**:
   - Technical review
   - Impact analysis

3. **Update spec**:
   - Edit `DOC_ID_FRAMEWORK.md`
   - Update registry schema if needed
   - Version the change

4. **Communicate**:
   - Update session reports
   - Notify users
   - Update tools

---

## Registry Management

### DO ✅

- Use `doc_id_registry_cli.py` for all changes
- Backup before major operations
- Validate after changes
- Version control registry file

### DON'T ❌

- Edit `DOC_ID_REGISTRY.yaml` manually
- Reuse retired IDs
- Change existing active IDs
- Skip validation

---

## File Relationships

```
DOC_ID_FRAMEWORK.md
├─> Defines format, categories, lifecycle
│
DOC_ID_REGISTRY.yaml
├─> Implements the specification
├─> Used by tools/doc_id_registry_cli.py
│
ADR-010-ulid-identity.md
├─> Explains why this design
│
UTE_ID_SYSTEM_SPEC.md
└─> Integration with broader system
```

---

## Related Documentation

### In doc_id/
- `../tools/README.md` - Tool usage
- `../analysis/CONFLICT_ANALYSIS_AND_RESOLUTION.md` - Conflict handling
- `../plans/` - Execution plans

### In Repository Root
- `PLAN_DOC_ID_COMPLETION_001.md` - Latest phase plan
- `docs_inventory.jsonl` - Current inventory

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | 2025-11-29 | Production-ready specification |
| **0.3** | 2025-11-25 | Added lifecycle rules |
| **0.2** | 2025-11-20 | Refined ID format |
| **0.1** | 2025-11-15 | Initial specification |

---

**Primary Reference**: `DOC_ID_FRAMEWORK.md`  
**Single Source of Truth**: `DOC_ID_REGISTRY.yaml`  
**Use**: `../tools/doc_id_registry_cli.py` for registry operations
