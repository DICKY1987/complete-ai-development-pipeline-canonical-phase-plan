# DOC_ID_FRAMEWORK – Repository-Wide Documentation Identifier System

**Spec ID:** DOC-ID-FRAMEWORK-V1  
**Status:** ACTIVE  
**Created:** 2025-11-24  
**Based on:** UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns ID system

---

## 0. Scope & Purpose

This framework defines a **unified, scalable doc_id system** for the **entire repository**, covering:
- All code modules (core, error, engine, specifications, aim, pm, etc.)
- All pattern suites (UET patterns)
- All governance documents (specs, ADRs, guides)
- All configuration and schema files
- All workstreams and project management artifacts

**Key Principle:** Every logical documentation unit gets a **unique, stable `doc_id`** that serves as the canonical join key across all related artifacts.

---

## 1. `doc_id` Format Specification

### 1.1 Universal Format

All `doc_id` values **MUST** follow this regex:

```regex
^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$
```

**Structure:**
```
DOC-<CATEGORY>-<NAME-SEGMENTS>-<NNN>
│   │          │                 │
│   │          │                 └─ 3-digit sequence number (001-999)
│   │          └─────────────────── 1+ uppercase segments describing content
│   └────────────────────────────── Category prefix (PAT, CORE, ERROR, etc.)
└────────────────────────────────── Literal "DOC" prefix
```

### 1.2 Category Prefixes

| Category | Prefix | Examples | Scope |
|----------|--------|----------|-------|
| **Patterns** | `PAT` | `DOC-PAT-SAVE-FILE-001` | UET patterns |
| **Core Engine** | `CORE` | `DOC-CORE-ORCHESTRATOR-001` | core/* modules |
| **Error System** | `ERROR` | `DOC-ERROR-PLUGIN-RUFF-001` | error/* modules |
| **Specifications** | `SPEC` | `DOC-SPEC-WORKSTREAM-SCHEMA-001` | Specs and schemas |
| **Architecture** | `ARCH` | `DOC-ARCH-LAYERED-DESIGN-001` | ADRs and architecture docs |
| **AIM** | `AIM` | `DOC-AIM-BRIDGE-ADAPTER-001` | AIM environment manager |
| **Project Mgmt** | `PM` | `DOC-PM-WORKSTREAM-WS001-001` | Project management artifacts |
| **Infrastructure** | `INFRA` | `DOC-INFRA-CI-PIPELINE-001` | CI/CD, deployment |
| **Configuration** | `CONFIG` | `DOC-CONFIG-QUALITY-GATE-001` | Config files |
| **Scripts** | `SCRIPT` | `DOC-SCRIPT-VALIDATE-WS-001` | Automation scripts |
| **Tests** | `TEST` | `DOC-TEST-CORE-ENGINE-001` | Test suites |
| **Guides** | `GUIDE` | `DOC-GUIDE-QUICK-START-001` | User guides |

### 1.3 Naming Conventions

**Name segments** should:
- Use **uppercase letters, digits, and dashes** only
- Be **concise but descriptive** (2-5 segments ideal)
- Represent the **logical content**, not the filename
- Use **domain terminology** consistent with the codebase

**Good examples:**
- `DOC-CORE-ORCHESTRATOR-STATE-001`
- `DOC-ERROR-PLUGIN-PYTHON-RUFF-001`
- `DOC-SPEC-WORKSTREAM-JSON-SCHEMA-001`
- `DOC-ARCH-CIRCUIT-BREAKER-PATTERN-001`

**Bad examples:**
- `DOC-CORE-ORCH-001` (too abbreviated)
- `DOC-CORE-orchestrator.py-001` (filename, not concept)
- `DOC-CORE-THAT-THING-001` (vague)

---

## 2. Category-Specific Guidelines

### 2.1 Patterns (`DOC-PAT-*`)

**Format:** `DOC-PAT-<PATTERN-NAME>-<NNN>`

Applies to all UET patterns under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/`.

**Artifacts tied to same `doc_id`:**
- Index entry in `PATTERN_INDEX.yaml`
- Spec file in `patterns/specs/*.pattern.yaml`
- Schema file in `patterns/schemas/*.schema.json`
- Executor in `patterns/executors/*_executor.*`
- Tests in `patterns/tests/test_*`
- Examples in `patterns/examples/*/`

**Example:**
```yaml
doc_id: DOC-PAT-SAVE-FILE-001
pattern_id: PAT-SAVE-FILE-001
name: save_file
spec_path: patterns/specs/save_file.pattern.yaml
schema_path: patterns/schemas/save_file.schema.json
executor_path: patterns/executors/save_file_executor.ps1
```

---

### 2.2 Core Modules (`DOC-CORE-*`)

**Format:** `DOC-CORE-<MODULE-CONCEPT>-<NNN>`

Applies to `core/*` modules (state, engine, planning).

**Artifacts tied to same `doc_id`:**
- Module source file(s) (e.g., `core/engine/orchestrator.py`)
- API documentation (docstrings, .md files)
- Related tests (`tests/engine/test_orchestrator.py`)
- Configuration schemas
- Usage examples

**Placement:**
- **Source files:** Docstring header with `doc_id` reference
- **Test files:** `# DOC_LINK: <DOC_ID>` header
- **Docs:** YAML front matter with `doc_id`

**Example:**
```python
# core/engine/orchestrator.py
"""
Workstream Orchestrator

DOC_ID: DOC-CORE-ORCHESTRATOR-001
MODULE: core.engine
PURPOSE: Coordinate workstream execution across tools
"""
```

```python
# tests/engine/test_orchestrator.py
# DOC_LINK: DOC-CORE-ORCHESTRATOR-001
# Tests for core.engine.orchestrator

import pytest
from core.engine.orchestrator import Orchestrator
```

---

### 2.3 Error System (`DOC-ERROR-*`)

**Format:** `DOC-ERROR-<COMPONENT>-<NNN>`

Applies to `error/*` modules (engine, plugins).

**Artifacts:**
- Plugin implementation files
- Error detection schemas
- Fix strategy specs
- Tests
- Example error patterns

**Example:**
```python
# error/plugins/python_ruff/plugin.py
"""
Python Ruff Error Plugin

DOC_ID: DOC-ERROR-PLUGIN-PYTHON-RUFF-001
PURPOSE: Detect and auto-fix Python code quality issues using Ruff
"""
```

---

### 2.4 Specifications (`DOC-SPEC-*`)

**Format:** `DOC-SPEC-<SPEC-NAME>-<NNN>`

Applies to formal specs, schemas, and contracts.

**Artifacts:**
- Spec documents (markdown, YAML)
- JSON schemas
- Validation logic
- Example conformant instances

**Example:**
```yaml
# schema/workstream.schema.json
{
  "doc_id": "DOC-SPEC-WORKSTREAM-JSON-SCHEMA-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Workstream Specification Schema",
  "type": "object",
  ...
}
```

---

### 2.5 Architecture Decisions (`DOC-ARCH-*`)

**Format:** `DOC-ARCH-<DECISION-TOPIC>-<NNN>`

Applies to ADRs and architecture documentation.

**Artifacts:**
- ADR markdown files (`adr/*.md`)
- Architecture diagrams
- Design discussion documents
- Implementation guides

**Example:**
```markdown
---
doc_id: DOC-ARCH-CIRCUIT-BREAKER-001
adr_number: 007
title: Circuit Breaker Pattern for Tool Failures
status: accepted
date: 2025-11-24
---

# ADR 007: Circuit Breaker Pattern for Tool Failures
...
```

---

### 2.6 Project Management (`DOC-PM-*`)

**Format:** `DOC-PM-<ARTIFACT-TYPE>-<NNN>`

Applies to workstreams, phases, milestones.

**Artifacts:**
- Workstream JSON files (`workstreams/*.json`)
- Phase planning docs
- Progress reports
- Milestone trackers

**Example:**
```json
{
  "doc_id": "DOC-PM-WORKSTREAM-WS001-001",
  "workstream_id": "WS-001",
  "title": "Core Engine Implementation",
  "phase": "development",
  ...
}
```

---

### 2.7 Scripts (`DOC-SCRIPT-*`)

**Format:** `DOC-SCRIPT-<SCRIPT-NAME>-<NNN>`

Applies to automation scripts in `scripts/`.

**Artifacts:**
- Script file (Python, PowerShell, Bash)
- Usage documentation
- Tests for the script
- Example invocations

**Example:**
```python
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-VALIDATE-WORKSTREAMS-001
"""
Validate Workstreams Script

PURPOSE: Validate all workstream JSON files against schema
USAGE: python scripts/validate_workstreams.py
"""
```

---

### 2.8 Guides (`DOC-GUIDE-*`)

**Format:** `DOC-GUIDE-<GUIDE-NAME>-<NNN>`

Applies to user-facing documentation.

**Artifacts:**
- README files
- Quick start guides
- Tutorial documents
- FAQ documents

**Example:**
```markdown
---
doc_id: DOC-GUIDE-QUICK-START-001
title: Quick Start Guide
audience: new_users
---

# Quick Start Guide
...
```

---

## 3. Repository Index System

### 3.1 Central Index File

**Location:** `DOC_ID_REGISTRY.yaml`

Contains all `doc_id` assignments across the entire repository.

**Structure:**
```yaml
metadata:
  version: "1.0.0"
  last_updated: "2025-11-24"
  total_docs: 247

categories:
  patterns:
    prefix: "PAT"
    count: 15
    next_id: 16
    
  core:
    prefix: "CORE"
    count: 23
    next_id: 24
    
  error:
    prefix: "ERROR"
    count: 8
    next_id: 9

docs:
  - doc_id: DOC-PAT-SAVE-FILE-001
    category: patterns
    name: save_file
    status: stable
    artifacts:
      - type: spec
        path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/save_file.pattern.yaml
      - type: schema
        path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/schemas/save_file.schema.json
      - type: executor
        path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/executors/save_file_executor.ps1
      - type: test
        path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/tests/test_save_file_main.ps1
      - type: examples
        path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/examples/save_file/
    created: "2025-11-20"
    last_modified: "2025-11-24"
    
  - doc_id: DOC-CORE-ORCHESTRATOR-001
    category: core
    name: orchestrator
    status: stable
    artifacts:
      - type: source
        path: core/engine/orchestrator.py
      - type: test
        path: tests/engine/test_orchestrator.py
      - type: doc
        path: docs/core/engine/ORCHESTRATOR.md
    created: "2025-09-15"
    last_modified: "2025-11-22"
```

### 3.2 Category-Specific Indexes

Each major section maintains its own index:

| Index File | Location | Covers |
|------------|----------|--------|
| `PATTERN_INDEX.yaml` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/registry/` | All patterns |
| `CORE_MODULE_INDEX.yaml` | `core/` | Core modules |
| `ERROR_PLUGIN_INDEX.yaml` | `error/` | Error plugins |
| `SPEC_INDEX.yaml` | `specifications/` | Specs and schemas |
| `ADR_INDEX.yaml` | `adr/` | Architecture decisions |

These feed into the central `DOC_ID_REGISTRY.yaml`.

---

## 4. Embedding `doc_id` in Files

### 4.1 Python Files

**Module docstring:**
```python
"""
Module Name

DOC_ID: DOC-CORE-ORCHESTRATOR-001
MODULE: core.engine.orchestrator
PURPOSE: Brief description
"""
```

**Test file header:**
```python
# DOC_LINK: DOC-CORE-ORCHESTRATOR-001
# Tests for core.engine.orchestrator

import pytest
```

### 4.2 PowerShell/Scripts

**Header comment:**
```powershell
# DOC_LINK: DOC-SCRIPT-VALIDATE-WORKSTREAMS-001
# Validate Workstreams Script
param(...)
```

### 4.3 YAML Files

**Top-level field:**
```yaml
doc_id: DOC-CONFIG-QUALITY-GATE-001
version: "1.0.0"
# ... rest of config
```

### 4.4 JSON Files

**Top-level field:**
```json
{
  "doc_id": "DOC-SPEC-WORKSTREAM-SCHEMA-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  ...
}
```

### 4.5 Markdown Files

**YAML front matter:**
```markdown
---
doc_id: DOC-GUIDE-QUICK-START-001
title: Quick Start Guide
version: 1.0.0
---

# Quick Start Guide
...
```

### 4.6 Sidecar Files (when embedding not possible)

**Format:** `<filename>.id.yaml`

```yaml
# orchestrator.py.id.yaml
source_file: core/engine/orchestrator.py
doc_id: DOC-CORE-ORCHESTRATOR-001
role: source_metadata
```

---

## 5. Minting New `doc_id` Values

### 5.1 Procedure

1. **Determine category** based on content type (PAT, CORE, ERROR, etc.)
2. **Choose name segments** that describe the logical unit
3. **Check existing IDs** in the appropriate index
4. **Assign next sequence number** (001, 002, ...)
5. **Update registry** with new `doc_id`
6. **Embed in all artifacts** for that doc unit

### 5.2 Example: New Core Module

**Goal:** Document the new `core.engine.scheduler` module

**Steps:**
1. Category = `CORE` (core engine module)
2. Name segments = `SCHEDULER` (single concept)
3. Check `CORE_MODULE_INDEX.yaml`:
   - Existing: `DOC-CORE-ORCHESTRATOR-001`, `DOC-CORE-EXECUTOR-001`
   - Next available: `003`
4. Assign: `DOC-CORE-SCHEDULER-001`
5. Add to `CORE_MODULE_INDEX.yaml`:
   ```yaml
   - doc_id: DOC-CORE-SCHEDULER-001
     name: scheduler
     path: core/engine/scheduler.py
     test_path: tests/engine/test_scheduler.py
   ```
6. Embed in source file docstring, test header, docs front matter

### 5.3 Collision Handling

If a name collision occurs (very unlikely with 999 sequence numbers):
- Add a disambiguating segment: `DOC-CORE-SCHEDULER-V2-001`
- Or use different naming: `DOC-CORE-TASK-SCHEDULER-001`

---

## 6. Cross-Artifact Consistency Rules

### 6.1 Canonical Join Key

`doc_id` is the **only** canonical key for joining artifacts. Tools **MUST** use `doc_id` for:
- Linking tests to source code
- Linking specs to implementations
- Linking docs to code modules
- Finding all artifacts for a logical unit

### 6.2 Consistency Requirement

For any given `doc_id`, **all** related artifacts **MUST**:
- Reference the **same** `doc_id` value
- Use the **exact** format (case-sensitive, no variations)
- Appear in the appropriate index

**Validation:**
```python
def validate_doc_id_consistency(doc_id: str) -> dict:
    """
    Check that all artifacts for a doc_id reference it correctly.
    
    Returns:
        {
            "doc_id": "DOC-CORE-ORCHESTRATOR-001",
            "artifacts_found": 4,
            "artifacts_expected": 4,
            "consistency": "PASS",
            "errors": []
        }
    """
```

---

## 7. Tooling and Automation

### 7.1 Required Tools

**`doc_id_validator.py`**
- Validate `doc_id` format
- Check cross-artifact consistency
- Report missing or mismatched IDs

**`doc_id_registry_cli.py`**
- Mint new `doc_id` values
- Search by category, name, or path
- Update indexes
- Generate reports

**`doc_id_migrator.py`**
- Migrate legacy files to use `doc_id`
- Batch update operations
- Verify no regressions

### 7.2 CI/CD Integration

**Pre-commit hooks:**
- Validate `doc_id` format in modified files
- Check consistency with registry
- Fail if `doc_id` missing where required

**CI pipeline:**
- Full `doc_id` validation on all files
- Report coverage (% of files with `doc_id`)
- Block merges if violations detected

---

## 8. Migration Strategy

### 8.1 Phases

**Phase 1: Patterns** ✅
- UET patterns already use `DOC-PAT-*` format
- Validate existing IDs
- Fill gaps

**Phase 2: Core Modules**
- Add `doc_id` to all `core/*` modules
- Create `CORE_MODULE_INDEX.yaml`
- Link tests to source

**Phase 3: Error System**
- Add `doc_id` to all `error/*` modules and plugins
- Create `ERROR_PLUGIN_INDEX.yaml`

**Phase 4: Specifications**
- Add `doc_id` to all schema files
- Create `SPEC_INDEX.yaml`

**Phase 5: Architecture & Guides**
- Add `doc_id` to ADRs
- Add `doc_id` to all guide docs

**Phase 6: Remaining Categories**
- Scripts, tests, configs, PM artifacts

### 8.2 Backward Compatibility

During migration:
- **Don't remove** existing identifiers (e.g., `pattern_id`)
- **Add** `doc_id` alongside existing IDs
- **Use** `doc_id` as primary key in new code
- **Deprecate** old join methods gradually

---

## 9. Benefits

### 9.1 For AI Tools

- **Single source of truth** for finding related artifacts
- **Stable references** across refactors (filename changes don't break links)
- **Machine-readable** join key for automation
- **Consistent semantics** across all doc types

### 9.2 For Developers

- **Easy navigation** from code to docs to tests
- **Clear ownership** of documentation units
- **Auditability** of changes to logical units
- **Conflict prevention** via unique IDs

### 9.3 For CI/CD

- **Enforceable standards** via validation
- **Coverage metrics** (% of code with doc IDs)
- **Automated linking** in generated docs
- **Change tracking** at doc-unit granularity

---

## 10. Examples by Use Case

### 10.1 Adding a New Core Module

**Scenario:** Creating `core/engine/recovery.py`

```python
# core/engine/recovery.py
"""
Recovery Manager

DOC_ID: DOC-CORE-RECOVERY-001
MODULE: core.engine.recovery
PURPOSE: Handle workstream recovery after failures
"""

class RecoveryManager:
    ...
```

```python
# tests/engine/test_recovery.py
# DOC_LINK: DOC-CORE-RECOVERY-001

import pytest
from core.engine.recovery import RecoveryManager

def test_recovery_from_checkpoint():
    ...
```

Update `CORE_MODULE_INDEX.yaml`:
```yaml
- doc_id: DOC-CORE-RECOVERY-001
  name: recovery
  module: core.engine.recovery
  source: core/engine/recovery.py
  tests: tests/engine/test_recovery.py
  status: development
```

### 10.2 Adding a New Error Plugin

**Scenario:** Creating `error/plugins/typescript_eslint/`

```python
# error/plugins/typescript_eslint/plugin.py
"""
TypeScript ESLint Error Plugin

DOC_ID: DOC-ERROR-PLUGIN-TYPESCRIPT-ESLINT-001
PURPOSE: Detect and fix TypeScript code quality issues
"""

def parse(output: str) -> List[Error]:
    ...
```

Update `ERROR_PLUGIN_INDEX.yaml`:
```yaml
- doc_id: DOC-ERROR-PLUGIN-TYPESCRIPT-ESLINT-001
  name: typescript_eslint
  plugin_path: error/plugins/typescript_eslint/plugin.py
  config_schema: error/plugins/typescript_eslint/config.schema.json
  tests: tests/error/plugins/test_typescript_eslint.py
```

### 10.3 Adding a New ADR

**Scenario:** Documenting decision to use async task queues

```markdown
---
doc_id: DOC-ARCH-ASYNC-TASK-QUEUE-001
adr_number: 015
title: Async Task Queue for Tool Invocations
status: proposed
date: 2025-11-24
---

# ADR 015: Async Task Queue for Tool Invocations

## Context
...
```

Update `ADR_INDEX.yaml`:
```yaml
- doc_id: DOC-ARCH-ASYNC-TASK-QUEUE-001
  adr_number: 015
  file: adr/015-async-task-queue.md
  status: proposed
  related_docs:
    - DOC-CORE-EXECUTOR-001
    - DOC-CORE-SCHEDULER-001
```

---

## 11. Validation Rules

### 11.1 Format Validation

**MUST:**
- Match regex: `^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$`
- Use valid category prefix (PAT, CORE, ERROR, etc.)
- Have 3-digit sequence number (001-999)

**MUST NOT:**
- Contain lowercase letters
- Contain special characters (except dash)
- Have leading zeros beyond 3 digits
- Be empty or whitespace-only

### 11.2 Uniqueness Validation

**MUST:**
- Be globally unique across entire repository
- Not be reused after deletion/deprecation
- Be registered in central registry

### 11.3 Consistency Validation

For each `doc_id` in registry:
- All listed artifacts MUST exist
- All artifacts MUST reference the correct `doc_id`
- No artifacts may reference unlisted `doc_id`

---

## 12. FAQ

**Q: What if I change a filename?**  
A: `doc_id` stays the same. Update the path in the index.

**Q: What if I split a module into two?**  
A: Mint two new `doc_id` values. Deprecate the old one.

**Q: Can I have multiple `doc_id`s in one file?**  
A: No. One file = one primary `doc_id`. Use artifact lists in index for multi-file units.

**Q: What about generated files?**  
A: Generated files inherit `doc_id` from their generator (with `.generated` suffix).

**Q: Do all files need a `doc_id`?**  
A: No. Only files that are "documentation units" (code modules, specs, guides, tests, etc.). Temporary/cache files don't need IDs.

---

## 13. References

- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PAT-CHECK-001  Pattern Directory & ID System Compliance (v2).md`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/PATTERN_DOC_SUITE_SPEC.md`
- `CODEBASE_INDEX.yaml` (module structure)
- `ai_policies.yaml` (edit zones)

---

## 14. Versioning

**Current Version:** 1.0.0  
**Status:** ACTIVE  
**Next Review:** 2025-12-24

### Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-24 | Initial framework based on UET patterns system |

---

## Appendix A: Quick Reference Card

```
DOC_ID FORMAT: DOC-<CATEGORY>-<NAME>-<NNN>

CATEGORIES:
  PAT      Patterns
  CORE     Core modules
  ERROR    Error system
  SPEC     Specifications
  ARCH     Architecture
  AIM      AIM manager
  PM       Project mgmt
  INFRA    Infrastructure
  CONFIG   Configuration
  SCRIPT   Scripts
  TEST     Tests
  GUIDE    Guides

EMBEDDING:
  Python:      """...\nDOC_ID: DOC-...\n..."""
  Tests:       # DOC_LINK: DOC-...
  YAML:        doc_id: DOC-...
  JSON:        "doc_id": "DOC-..."
  Markdown:    ---\ndoc_id: DOC-...\n---

TOOLS:
  Validate:    python scripts/doc_id_validator.py
  Mint new:    python scripts/doc_id_registry_cli.py mint --category CORE --name SCHEDULER
  Search:      python scripts/doc_id_registry_cli.py search --pattern "CORE-.*-001"
```

---

**END OF DOC_ID_FRAMEWORK**
