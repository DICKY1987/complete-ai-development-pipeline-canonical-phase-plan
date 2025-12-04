---
doc_id: DOC-GUIDE-QUICKSTART-OPENSPEC-832
---

# OpenSpec Integration Quick Start

## 5-Minute Quick Start

### Step 1: Create a Proposal (2 minutes)

Use Claude Code to create an OpenSpec proposal:

```
/openspec:proposal "Add rate limiting to API endpoints"
```

Claude will create:
- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/tasks.md`

### Step 2: Define Requirements (2 minutes)

Add requirements to your proposal with SHALL/MUST keywords:

```markdown
## Requirements

### Requirement: Rate Limiting
The API SHALL limit requests to 100 per minute per client.

#### Scenario: Exceed Rate Limit
- WHEN a client makes 101 requests in one minute
- THEN the API SHALL return 429 Too Many Requests
- AND include Retry-After header
```

### Step 3: Convert to Workstream (1 minute)

```bash
# Interactive mode
python scripts/spec_to_workstream.py --interactive

# Or direct
python scripts/spec_to_workstream.py --change-id <change-id>
```

Review and save the generated workstream JSON.

### Step 4: Execute

```bash
# Validate
python scripts/validate_workstreams.py

# Run
python scripts/run_workstream.py --ws-id <ws-id>
```

### Step 5: Archive

After completion:

```
/openspec:archive <change-id>
```

## Command Cheat Sheet

### OpenSpec Commands

```bash
/openspec:proposal "<description>"    # Create new proposal
/openspec:apply                       # Implement current proposal
/openspec:archive <change-id>         # Archive completed change
/openspec:view                        # Open dashboard
```

### Bridge Commands

```bash
# List changes
python scripts/spec_to_workstream.py --list
pwsh ./scripts/spec_to_workstream.ps1 -List

# Interactive conversion
python scripts/spec_to_workstream.py --interactive
pwsh ./scripts/spec_to_workstream.ps1 -Interactive

# Direct conversion
python scripts/spec_to_workstream.py --change-id <id>
pwsh ./scripts/spec_to_workstream.ps1 -ChangeId <id>

# Custom workstream ID
python scripts/spec_to_workstream.py --change-id <id> --ws-id ws-custom

# Dry run
python scripts/spec_to_workstream.py --change-id <id> --dry-run
```

### Pipeline Commands

```bash
# Validate workstreams
python scripts/validate_workstreams.py
python scripts/validate_workstreams_authoring.py --json

# Run workstream
python scripts/run_workstream.py --ws-id <id>
python scripts/run_workstream.py --ws-id <id> --dry-run

# Inspect state
python scripts/db_inspect.py
```

## File Structure

```
your-project/
├── openspec/
│   ├── changes/              # Active proposals
│   │   └── <change-id>/
│   │       ├── proposal.md   # Metadata + description
│   │       ├── tasks.md      # Task checklist
│   │       └── specs/        # Requirements + scenarios
│   ├── specs/                # Current specifications
│   ├── archive/              # Completed changes
│   └── project.md            # Project conventions
│
├── workstreams/              # Generated bundles
│   └── ws-<feature>.json
│
├── scripts/
│   ├── spec_to_workstream.py   # Bridge script (Python)
│   └── spec_to_workstream.ps1  # Bridge script (PowerShell)
│
└── state/
    └── pipeline_state.db     # Execution state
```

## Writing Good Requirements

### ✅ Good Requirements

```markdown
### Requirement: Error Handling
The system SHALL retry failed operations up to 3 times.

#### Scenario: Transient Failure
- WHEN an operation fails with a retryable error
- THEN the system SHALL retry up to 3 times
- AND wait 1 second between retries
```

### ❌ Bad Requirements

```markdown
### Task: Add Error Handling
Maybe add some error handling to make it more robust.
```

**Why bad:**
- Not a requirement (no SHALL/MUST)
- Vague ("some error handling")
- No testable scenarios

## Workflow Patterns

### Pattern 1: Single Feature

```
1. /openspec:proposal "Feature X"
2. Define requirements
3. python scripts/spec_to_workstream.py --change-id <id>
4. python scripts/run_workstream.py --ws-id <id>
5. /openspec:archive <id>
```

### Pattern 2: Multi-Workstream Feature

```
1. /openspec:proposal "Large Feature Y"
2. Define all requirements
3. Manually create multiple workstreams with dependencies:
   - ws-feature-y-part1 (depends_on: [])
   - ws-feature-y-part2 (depends_on: ["ws-feature-y-part1"])
   - ws-feature-y-part3 (depends_on: ["ws-feature-y-part2"])
4. Run in order (orchestrator handles dependencies)
5. /openspec:archive <id>
```

### Pattern 3: Iterative Refinement

```
1. /openspec:proposal "Feature Z"
2. Generate initial workstream
3. Run workstream → errors detected
4. Refine OpenSpec requirements based on learnings
5. Regenerate workstream or edit manually
6. Re-run
7. /openspec:archive <id>
```

## Common Scenarios

### Scenario: Adding a New Plugin

**OpenSpec Proposal:**
```markdown
---
title: Add ESLint Plugin
---

## Requirements

### Requirement: JavaScript Linting
The system SHALL integrate ESLint for JavaScript validation.

#### Scenario: Detect Style Issues
- WHEN JavaScript files have style violations
- THEN ESLint plugin SHALL report them as errors

#### Scenario: Fix Auto-Fixable Issues
- WHEN ESLint detects auto-fixable issues
- THEN the plugin SHALL offer automatic fixes
```

**Tasks:**
```markdown
- [ ] Create src/plugins/eslint/ directory
- [ ] Add manifest.json with plugin metadata
- [ ] Implement plugin.py with parse() and fix()
- [ ] Add tests in tests/plugins/test_js.py
- [ ] Update src/plugins/README.md
```

**Generated Workstream:**
```json
{
  "id": "ws-add-eslint-plugin",
  "openspec_change": "add-eslint",
  "files_scope": [
    "src/plugins/eslint/",
    "tests/plugins/test_js.py",
    "src/plugins/README.md"
  ],
  "files_create": [
    "src/plugins/eslint/manifest.json",
    "src/plugins/eslint/plugin.py"
  ],
  "tasks": [
    "Create src/plugins/eslint/ directory",
    "Add manifest.json with plugin metadata",
    "Implement plugin.py with parse() and fix()",
    "Add tests in tests/plugins/test_js.py",
    "Update src/plugins/README.md"
  ]
}
```

### Scenario: Refactoring Existing Code

**OpenSpec Proposal:**
```markdown
---
title: Refactor Error Pipeline State Machine
---

## Requirements

### Requirement: State Transition Clarity
The state machine SHALL use explicit state enums instead of strings.

#### Scenario: Type Safety
- WHEN code references a state
- THEN the type system SHALL validate it at compile time
```

**Generated Workstream:**
```json
{
  "id": "ws-refactor-error-state-machine",
  "openspec_change": "refactor-state-machine",
  "files_scope": [
    "src/pipeline/error_state_machine.py",
    "tests/pipeline/test_error_state_machine.py"
  ]
}
```

### Scenario: Bug Fix

**OpenSpec Proposal:**
```markdown
---
title: Fix Workstream Dependency Cycle Detection
---

## Requirements

### Requirement: Cycle Detection
The system SHALL detect circular dependencies in workstreams.

#### Scenario: Direct Cycle
- WHEN ws-a depends on ws-b AND ws-b depends on ws-a
- THEN validation SHALL fail with error "Circular dependency detected"

#### Scenario: Indirect Cycle
- WHEN ws-a → ws-b → ws-c → ws-a
- THEN validation SHALL detect the 3-node cycle
```

## Troubleshooting

### Issue: "Change directory not found"

```bash
# List available changes
python scripts/spec_to_workstream.py --list

# Verify change exists
ls openspec/changes/
```

### Issue: Generated workstream has empty tasks

**Cause:** Tasks in `tasks.md` not formatted as markdown checklist.

**Fix:**
```markdown
# ✅ Correct format
- [ ] Task one
- [ ] Task two

# ❌ Wrong format
1. Task one
2. Task two
```

### Issue: Validation fails after generation

```bash
# Check detailed validation
python scripts/validate_workstreams_authoring.py --json

# Common fixes:
# - Add missing files to files_scope
# - Set gate >= 1
# - Ensure tool is specified
```

### Issue: Files not detected in files_scope

**Manual fix:** Edit the generated JSON:

```json
{
  "files_scope": [
    "src/pipeline/orchestrator.py",
    "src/pipeline/scheduler.py",
    "tests/pipeline/test_orchestrator.py"
  ]
}
```

Or mention files explicitly in tasks:

```markdown
- [ ] Modify src/pipeline/orchestrator.py to add feature X
```

## Next Steps

1. **Read full documentation**: [OpenSpec Bridge Guide](./openspec_bridge.md)
2. **Review examples**: Check `workstreams/example_*.json`
3. **Practice**: Create a test proposal and convert it
4. **Integrate**: Add to your team workflow

## Tips

- **Write specs first** before implementing
- **Use SHALL/MUST** for requirements
- **Include scenarios** for every requirement
- **Review generated bundles** before running
- **Link commits to OpenSpec** with change IDs
- **Archive completed changes** to keep `changes/` clean

## Resources

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [Pipeline Architecture](./ARCHITECTURE.md)
- [Workstream Authoring Guide](./workstream_authoring_guide.md)
- [Plugin Development](../src/plugins/README.md)
