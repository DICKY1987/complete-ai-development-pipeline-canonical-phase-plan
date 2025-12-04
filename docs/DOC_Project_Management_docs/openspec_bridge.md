---
doc_id: DOC-GUIDE-OPENSPEC-BRIDGE-831
---

# OpenSpec Bridge Documentation

## Overview

The OpenSpec Bridge connects OpenSpec specification management with the pipeline's workstream execution system. It automates the conversion of OpenSpec change proposals into workstream bundles.

## Architecture

```
OpenSpec Change Proposal
  └─ openspec/changes/<change-id>/
      ├─ proposal.md       (metadata, description)
      ├─ tasks.md          (task checklist)
      └─ spec-deltas.md    (requirements, scenarios)
                ↓
        spec_to_workstream.py
                ↓
Workstream Bundle
  └─ workstreams/<ws-id>.json
      ├─ id, openspec_change, gate
      ├─ files_scope, files_create
      ├─ tasks, acceptance_tests
      └─ depends_on, metadata
                ↓
        Pipeline Orchestrator
                ↓
        Execution (EDIT → STATIC → RUNTIME)
```

## Workflow

### 1. Create OpenSpec Proposal

Use Claude Code with OpenSpec slash commands:

```bash
# Create new proposal
/openspec:proposal "Add security scanning to pipeline"
```

This creates:
- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/tasks.md`

### 2. Define Requirements

Add requirements with SHALL/MUST keywords to spec files:

```markdown
## Requirements

### Requirement: Security Scan Integration
The system SHALL integrate Bandit security scanning into the STATIC phase.

#### Scenario: Detect Security Issues
- WHEN security vulnerabilities exist in Python code
- THEN Bandit SHALL report them as errors
- AND the pipeline SHALL transition to error fixing state
```

### 3. Convert to Workstream

Use the bridge script to generate workstream bundles:

```bash
# Interactive mode (recommended)
python scripts/spec_to_workstream.py --interactive

# Direct conversion
python scripts/spec_to_workstream.py --change-id <change-id>

# PowerShell wrapper
pwsh ./scripts/spec_to_workstream.ps1 -Interactive
```

### 4. Review and Refine

Edit the generated workstream JSON:

```json
{
  "id": "ws-security-scanning",
  "openspec_change": "OS-042",
  "gate": 1,
  "files_scope": [
    "src/pipeline/orchestrator.py",
    "src/plugins/bandit/"
  ],
  "tasks": [
    "Integrate Bandit plugin into STATIC phase",
    "Add security error handling",
    "Update orchestrator to run security checks"
  ],
  "acceptance_tests": [
    "Verify: Detect Security Issues",
    "pytest tests/pipeline/test_security_integration.py"
  ]
}
```

### 5. Validate

Run workstream validation:

```bash
# Validate schema compliance
python scripts/validate_workstreams.py

# Authoring-friendly validation
python scripts/validate_workstreams_authoring.py --json
```

### 6. Execute

Run the workstream through the pipeline:

```bash
# Dry run (simulate without external tools)
python scripts/run_workstream.py --ws-id ws-security-scanning --dry-run

# Real execution
python scripts/run_workstream.py --ws-id ws-security-scanning
```

### 7. Archive Completed Spec

After successful execution:

```bash
/openspec:archive <change-id>
```

This moves the change to `openspec/archive/`.

## Bridge Script Features

### Automatic Extraction

The bridge script automatically extracts:

1. **Metadata**: Change ID, title, description
2. **Tasks**: From markdown task lists in `tasks.md`
3. **Requirements**: From spec files with SHALL/MUST keywords
4. **Scenarios**: Acceptance criteria from scenario blocks
5. **File Scope**: Files mentioned in tasks and specs
6. **Files to Create**: Detected from "create"/"add" keywords

### Intelligent Defaults

- **Workstream ID**: Auto-generated from proposal title (kebab-case)
- **Gate**: Defaults to 1 (can override)
- **Tool**: Defaults to "aider"
- **Circuit Breaker**: Standard configuration (5 attempts, 3 repeats)
- **Files Scope**: Extracted from task descriptions or defaults to `["src/"]`

### Command-Line Options

```bash
# List all available changes
python scripts/spec_to_workstream.py --list

# Interactive selection
python scripts/spec_to_workstream.py --interactive

# Direct conversion
python scripts/spec_to_workstream.py --change-id <id>

# Custom workstream ID
python scripts/spec_to_workstream.py --change-id <id> --ws-id ws-custom

# Custom output path
python scripts/spec_to_workstream.py --change-id <id> --output path/to/ws.json

# Dry run (print without saving)
python scripts/spec_to_workstream.py --change-id <id> --dry-run
```

## Integration with Pipeline

### Database Tracking

The workstream's `openspec_change` field links to OpenSpec:

```sql
SELECT w.id, w.openspec_change, w.state, r.status
FROM workstreams w
JOIN runs r ON w.run_id = r.id
WHERE w.openspec_change = 'OS-042';
```

### Error Pipeline Integration

Errors detected during execution reference the OpenSpec change:

```python
error_context = {
    "workstream_id": "ws-security-scanning",
    "openspec_change": "OS-042",
    "requirement": "Security Scan Integration",
    "scenario": "Detect Security Issues"
}
```

### Traceability Chain

```
OpenSpec Change OS-042
  ↓
Workstream ws-security-scanning
  ↓
Run run-<uuid>
  ↓
Step Attempts (EDIT, STATIC, RUNTIME)
  ↓
Error Reports
  ↓
Fix Attempts
  ↓
Verification
```

## Best Practices

### 1. Write Spec-First

Always create OpenSpec proposals before coding:

```markdown
# ✅ Good: Spec defines requirements
## Requirements
### Requirement: Performance Optimization
The system SHALL complete workstream execution in < 5 minutes.

# ❌ Bad: Implementation details without requirements
## Tasks
- Optimize the loop in orchestrator.py line 42
```

### 2. Use SHALL/MUST Keywords

Enforce requirement language:

```markdown
# ✅ Good: Clear requirement
The system SHALL validate all workstreams before execution.

# ❌ Bad: Ambiguous language
The system should probably validate workstreams.
```

### 3. Include Scenarios

Every requirement needs scenarios:

```markdown
### Requirement: Error Deduplication
The system SHALL deduplicate identical errors.

#### Scenario: Same Error Multiple Times
- WHEN the same error occurs 5 times
- THEN the system SHALL create 1 error record
- AND track occurrence_count = 5
```

### 4. Review Generated Bundles

Always review and refine:

1. Check `files_scope` is complete
2. Verify `tasks` are actionable
3. Add `depends_on` if needed
4. Customize `acceptance_tests`
5. Update `metadata` with owner

### 5. Link Back to Specs

Reference OpenSpec in commits:

```bash
git commit -m "feat: add security scanning (OpenSpec OS-042)"
```

## Troubleshooting

### Issue: No tasks extracted

**Cause**: Tasks not formatted as markdown checklist

**Fix**: Use proper markdown task format in `tasks.md`:

```markdown
- [ ] Task one
- [ ] Task two
```

### Issue: Empty files_scope

**Cause**: No file paths detected in tasks/specs

**Fix**: Mention files explicitly in tasks:

```markdown
- [ ] Modify src/pipeline/orchestrator.py
- [ ] Create tests/test_security.py
```

Or manually edit the generated bundle.

### Issue: Generic workstream ID

**Cause**: Title contains special characters or is too generic

**Fix**: Use `--ws-id` to override:

```bash
python scripts/spec_to_workstream.py --change-id test-001 --ws-id ws-specific-feature
```

### Issue: Validation fails after generation

**Cause**: Schema requirements not met (missing required fields)

**Fix**: Check validation output and edit bundle:

```bash
python scripts/validate_workstreams_authoring.py --json
```

## Advanced Usage

### Batch Conversion

Convert multiple changes:

```bash
for change in $(ls openspec/changes); do
    python scripts/spec_to_workstream.py --change-id $change
done
```

### Custom Templates

Modify the generator to use custom templates:

```python
# In spec_to_workstream.py
class WorkstreamGenerator:
    def __init__(self, spec_data: Dict[str, Any], template: Optional[Dict] = None):
        self.spec_data = spec_data
        self.template = template or self._load_default_template()
```

### Integration with CI

Add to GitHub Actions:

```yaml
- name: Convert OpenSpec Changes
  run: |
    python scripts/spec_to_workstream.py --list
    # Add logic to convert pending changes
```

### Programmatic API

Use as a library:

```python
from scripts.spec_to_workstream import OpenSpecParser, WorkstreamGenerator

parser = OpenSpecParser("OS-042")
spec_data = parser.parse()

generator = WorkstreamGenerator(spec_data)
bundle = generator.generate(ws_id="ws-custom")

# Use bundle programmatically
```

## Examples

### Example 1: Simple Feature

**OpenSpec Proposal** (`openspec/changes/add-logging/proposal.md`):
```markdown
---
title: Add Structured Logging
---

# Proposal
Add structured JSON logging to the pipeline orchestrator.
```

**Tasks** (`openspec/changes/add-logging/tasks.md`):
```markdown
- [ ] Add structlog dependency
- [ ] Replace print statements in src/pipeline/orchestrator.py
- [ ] Add log configuration in src/pipeline/config.py
```

**Generated Workstream**:
```json
{
  "id": "ws-add-structured-logging",
  "openspec_change": "add-logging",
  "files_scope": [
    "src/pipeline/orchestrator.py",
    "src/pipeline/config.py"
  ],
  "tasks": [
    "Add structlog dependency",
    "Replace print statements in src/pipeline/orchestrator.py",
    "Add log configuration in src/pipeline/config.py"
  ]
}
```

### Example 2: Multi-Workstream Feature

**OpenSpec Proposal** (`openspec/changes/parallel-execution/proposal.md`):
```markdown
---
title: Parallel Workstream Execution
---

# Proposal
Enable parallel execution of independent workstreams using process pools.
```

**Strategy**: Create multiple workstreams with dependencies:

```bash
# Convert to initial workstream
python scripts/spec_to_workstream.py --change-id parallel-execution --ws-id ws-parallel-scheduler

# Manually create dependent workstreams
# ws-parallel-executor (depends_on: ws-parallel-scheduler)
# ws-parallel-monitoring (depends_on: ws-parallel-executor)
```

## References

- [OpenSpec Documentation](https://github.com/Fission-AI/OpenSpec)
- [Workstream Authoring Guide](./workstream_authoring_guide.md)
- [Workstream Schema](../schema/workstream.schema.json)
- [Pipeline Architecture](./ARCHITECTURE.md)

## Version History

- **v1.0.0** (2025-01-17): Initial bridge implementation
  - OpenSpec proposal parsing
  - Automatic workstream generation
  - Interactive and batch modes
  - PowerShell wrapper for Windows
