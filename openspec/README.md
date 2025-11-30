---
doc_id: DOC-GUIDE-README-433
---

# OpenSpec Specifications

**Purpose**: Source OpenSpec proposals, specifications, and bridge documentation before conversion into workstreams.

## Overview

The `openspec/` directory contains the canonical source for OpenSpec change proposals, specification documents, and bridge integration that converts OpenSpec to executable workstreams.

## Structure

```
openspec/
├── specs/                           # Specification documents
│   ├── orchestration/
│   ├── plugin-system/
│   └── validation-pipeline/
├── changes/                         # Active change proposals
│   └── test-001/
│       ├── proposal.md
│       ├── tasks.md
│       └── spec.md
├── OPENSPEC_BRIDGE_SUMMARY.md      # Bridge implementation guide
├── project.md                       # Project-level OpenSpec metadata
└── .tmp_openspec_README.md         # Temporary notes
```

## Specifications (`openspec/specs/`)

Organized by domain, these directories contain detailed specification documents.

### Orchestration Specs

**Location**: `openspec/specs/orchestration/`

Specifications for workstream orchestration, scheduling, and execution.

**Topics**:
- Orchestrator lifecycle
- Step execution contracts
- Parallel execution strategies
- Circuit breaker patterns
- Recovery mechanisms

### Plugin System Specs

**Location**: `openspec/specs/plugin-system/`

Specifications for the error detection plugin architecture.

**Topics**:
- Plugin discovery and registration
- Manifest schema
- Dependency resolution (DAG)
- Plugin isolation
- Issue normalization

### Validation Pipeline Specs

**Location**: `openspec/specs/validation-pipeline/`

Specifications for error detection and quality gates.

**Topics**:
- State machine transitions
- Agent escalation strategy
- Incremental validation
- Auto-fix protocols
- Quality gate enforcement

## Change Proposals (`openspec/changes/`)

Active OpenSpec change proposals that will be converted to workstreams.

### Change Structure

Each change proposal is a directory containing:

```
openspec/changes/<change-id>/
├── proposal.md      # Problem statement and solution overview
├── tasks.md         # Breakdown of implementation tasks
└── spec.md          # Technical specification (optional)
```

### Example: test-001

**Location**: `openspec/changes/test-001/`

**Contents**:

#### proposal.md

```markdown
# Change Proposal: Test Integration

## Problem
The pipeline lacks comprehensive test coverage.

## Solution
Add pytest-based test suite with fixtures.

## Requirements
- SHALL provide temp database fixture
- SHALL support parallel test execution
- MUST integrate with CI pipeline
```

#### tasks.md

```markdown
# Implementation Tasks

1. Create `conftest.py` with fixtures
2. Add `tests/pipeline/` directory
3. Implement `temp_db` fixture
4. Write orchestrator tests
5. Update CI workflow
```

#### spec.md (optional)

```markdown
# Technical Specification

## Test Fixtures

### temp_db
Creates isolated SQLite database for each test.

**Signature**: `temp_db() -> Path`
**Scope**: Function-level
**Cleanup**: Automatic
```

## OpenSpec Bridge

**Documentation**: `OPENSPEC_BRIDGE_SUMMARY.md`

Describes the conversion process from OpenSpec change proposals to workstream bundles.

### Conversion Workflow

1. **Author change proposal** in `openspec/changes/<id>/`
2. **Run converter**:
   ```bash
   python scripts/spec_to_workstream.py --change-id <id>
   ```
3. **Review generated workstream** in `workstreams/`
4. **Execute workstream**:
   ```bash
   python scripts/run_workstream.py --workstream-id <id>
   ```

### Converter Features

- **Requirement extraction**: Parses SHALL/MUST keywords
- **Task decomposition**: Converts tasks.md to workstream steps
- **Metadata injection**: Adds spec references, timestamps, authors
- **Schema validation**: Ensures output conforms to workstream schema

### Usage

**Interactive mode**:
```bash
python scripts/spec_to_workstream.py --interactive
```

**Direct conversion**:
```bash
python scripts/spec_to_workstream.py --change-id test-001
```

**List available changes**:
```bash
python scripts/spec_to_workstream.py --list
```

**Dry run**:
```bash
python scripts/spec_to_workstream.py --change-id test-001 --dry-run
```

## Project Metadata (`project.md`)

**Purpose**: High-level OpenSpec metadata for the entire project.

**Contents**:
- Project name and description
- Key stakeholders
- High-level requirements
- Success criteria

## Creating a New Change Proposal

1. **Create change directory**:
   ```bash
   mkdir -p openspec/changes/<change-id>
   cd openspec/changes/<change-id>
   ```

2. **Write proposal.md**:
   ```markdown
   # Change Proposal: Title
   
   ## Problem
   Description of problem.
   
   ## Solution
   Proposed solution.
   
   ## Requirements
   - SHALL requirement 1
   - MUST requirement 2
   ```

3. **Write tasks.md**:
   ```markdown
   # Implementation Tasks
   
   1. Task 1 description
   2. Task 2 description
   ```

4. **Optional: Write spec.md**:
   ```markdown
   # Technical Specification
   
   Detailed technical design.
   ```

5. **Convert to workstream**:
   ```bash
   python scripts/spec_to_workstream.py --change-id <change-id>
   ```

## Requirement Keywords

OpenSpec uses RFC 2119 keywords for requirements:

- **SHALL** / **MUST**: Mandatory requirement
- **SHOULD**: Recommended but not mandatory
- **MAY**: Optional
- **SHALL NOT** / **MUST NOT**: Prohibited

**Parser Behavior**:
- SHALL/MUST → Extracted as hard requirements
- SHOULD → Extracted as soft requirements
- MAY → Extracted as optional features

## Integration with Workstreams

### Mapping

**OpenSpec Change** → **Workstream Bundle**

| OpenSpec | Workstream |
|----------|------------|
| `proposal.md` requirements | `workstream.requirements` |
| `tasks.md` tasks | `workstream.steps` |
| `spec.md` sections | `workstream.context` |
| Change ID | `workstream_id` |

### Traceability

Workstreams generated from OpenSpec include:

```json
{
  "workstream_id": "test-001",
  "metadata": {
    "source_type": "openspec",
    "source_path": "openspec/changes/test-001/",
    "generated_by": "spec_to_workstream.py",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Best Practices

1. **One change per directory**: Each change ID is isolated
2. **Clear requirements**: Use SHALL/MUST for critical requirements
3. **Atomic tasks**: Break tasks into small, executable units
4. **Versioning**: Use semantic versioning for change IDs (e.g., `v1.2.0-feature-name`)
5. **Review before conversion**: Validate proposal completeness

## Related Tools

### Converter Script

**Location**: `scripts/spec_to_workstream.py`

**Features**:
- Interactive mode for guided conversion
- Dry-run preview
- Change listing
- Validation

### Bridge Documentation

**Location**: `openspec/OPENSPEC_BRIDGE_SUMMARY.md`

**Contents**:
- Architecture overview
- Workflow steps
- Command reference
- Best practices
- Troubleshooting

## Validation

**Validate change proposals**:
```bash
python scripts/validate_openspec_changes.py
```

**Checks**:
- Required files exist (proposal.md, tasks.md)
- Requirements use correct keywords
- Tasks are numbered sequentially
- Spec references are valid

## Migration to Specifications

**Note**: OpenSpec content is gradually being migrated to `specifications/` for unified management.

**Migration path**:
1. OpenSpec changes → `openspec/changes/`
2. Conversion → `workstreams/`
3. Execution → Workstream execution
4. Archival → `specifications/content/archive/`

## Related Sections

- **Specifications**: `specifications/` - Unified spec management (migration target)
- **Workstreams**: `workstreams/` - Executable workstream bundles
- **Scripts**: `scripts/spec_to_workstream.py` - Conversion tool
- **Docs**: `docs/openspec_bridge.md` - Comprehensive guide

## See Also

- [OpenSpec Bridge Guide](../docs/openspec_bridge.md)
- [Workstream Authoring Guide](../docs/workstream_authoring.md)
- [Specifications README](../specifications/README.md)
- [Quick Start OpenSpec](../docs/QUICKSTART_OPENSPEC.md)
