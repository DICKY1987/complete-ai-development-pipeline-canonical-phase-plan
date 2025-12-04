---
doc_id: DOC-GUIDE-README-075
---

# Workstream Examples

> **Purpose**: Example workstream JSON bundles for reference and testing
> **Last Updated**: 2025-11-22
> **Status**: Production

---

## Overview

The `workstreams/` directory contains example workstream bundles that demonstrate various patterns and use cases.

## What is a Workstream?

A workstream is a structured workflow definition that:
- Defines a sequence of steps to execute
- Specifies tool configurations
- Includes validation rules
- Contains metadata for tracking

Workstreams are the primary unit of work in the pipeline system.

## Directory Structure

```
workstreams/
├── single/             # Single workstream examples
│   └── example-simple.json
├── multi/              # Multi-workstream bundles
│   └── example-coordinated.json
└── templates/          # Workstream templates (if present)
```

## Workstream Format

### Basic Structure

```json
{
  "id": "ws-001",
  "name": "Example Workstream",
  "version": "1.0.0",
  "metadata": {
    "author": "system",
    "created": "2025-11-22T00:00:00Z",
    "description": "Example workstream for demonstration"
  },
  "steps": [
    {
      "id": "step-1",
      "name": "First Step",
      "tool": "aider",
      "config": {
        "prompt": "Implement feature X"
      }
    }
  ]
}
```

### Key Fields

- **id**: Unique workstream identifier (e.g., `ws-001`)
- **name**: Human-readable name
- **version**: Semantic version
- **metadata**: Author, timestamps, description
- **steps**: Array of step definitions
- **dependencies**: Optional step dependencies

## Example Workstreams

### Simple Single-Step Workstream

**File**: `single/example-simple.json`

Demonstrates:
- Basic workstream structure
- Single step execution
- Aider integration

### Multi-Step Coordinated Workstream

**File**: `multi/example-coordinated.json`

Demonstrates:
- Multiple steps with dependencies
- Tool coordination (Aider + Codex)
- Error handling

### Parallel Execution Workstream

Demonstrates:
- Parallel step execution
- Dependency resolution
- Resource management

## Validation

Validate workstreams against schemas:

```bash
# Validate all workstreams
python ./scripts/validate_workstreams.py

# Validate specific file
python ./scripts/validate_workstreams.py --file workstreams/single/example-simple.json

# Check authoring quality
python ./scripts/validate_workstreams_authoring.py
```

## Running Workstreams

Execute a workstream:

```bash
# Run by ID
python ./scripts/run_workstream.py --ws-id ws-001

# Run specific step
python ./scripts/run_workstream.py --ws-id ws-001 --step step-1

# Dry run (validate without executing)
python ./scripts/run_workstream.py --ws-id ws-001 --dry-run
```

## Creating New Workstreams

### From OpenSpec

Convert OpenSpec change proposals to workstreams:

```bash
# Interactive mode (recommended)
python scripts/spec_to_workstream.py --interactive

# Direct conversion
python scripts/spec_to_workstream.py --change-id <id>
```

### Manual Creation

1. **Copy template**:
   ```bash
   cp workstreams/templates/basic.json workstreams/my-workstream.json
   ```

2. **Edit workstream**:
   - Set unique ID
   - Define steps
   - Configure tools
   - Add metadata

3. **Validate**:
   ```bash
   python ./scripts/validate_workstreams.py --file workstreams/my-workstream.json
   ```

4. **Test run**:
   ```bash
   python ./scripts/run_workstream.py --ws-id <your-id> --dry-run
   ```

## Workstream Authoring Guidelines

### Best Practices

1. **Use descriptive IDs**: `ws-<feature>-<number>` (e.g., `ws-auth-001`)
2. **Semantic versioning**: Increment appropriately
3. **Clear step names**: Action-oriented (e.g., "Implement user authentication")
4. **Tool-appropriate prompts**: Match prompt style to tool
5. **Include metadata**: Author, description, timestamps
6. **Define dependencies**: Explicit step ordering
7. **Error handling**: Include validation steps

### Step Configuration

Each step should specify:
- **Tool**: Which tool to use (`aider`, `codex`, `claude`)
- **Prompt**: Clear, specific instructions
- **Config**: Tool-specific configuration
- **Validation**: Success criteria
- **Timeout**: Maximum execution time

### Example Step

```json
{
  "id": "step-2",
  "name": "Add unit tests",
  "tool": "aider",
  "depends_on": ["step-1"],
  "config": {
    "prompt": "Add comprehensive unit tests for the authentication module",
    "model": "claude-3-5-sonnet-20241022",
    "timeout": 300
  },
  "validation": {
    "type": "test",
    "command": "pytest tests/test_auth.py"
  }
}
```

## Schema Reference

Workstreams must conform to schemas in `schema/workstream/`:

- **Bundle schema**: Overall structure
- **Step schema**: Individual step format
- **Metadata schema**: Metadata format

See [schema/README.md](../schema/README.md) for details.

## Related Documentation

- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository navigation
- [schema/README.md](../schema/README.md) - Schema definitions
- [core/README.md](../core/README.md) - Core pipeline implementation
- [engine/README.md](../engine/README.md) - Job-based execution
- [docs/QUICKSTART_OPENSPEC.md](../docs/QUICKSTART_OPENSPEC.md) - OpenSpec workflow

## Archiving Workstreams

Archive completed workstreams:

```bash
# Archive via OpenSpec (if from spec)
/openspec:archive <change-id>

# Archive manually
python ./scripts/archive_workstream.py --ws-id ws-001
```

Archived workstreams are moved to archive location and marked as complete.

---

**For AI Tools**: MEDIUM priority directory - use as reference for workstream structure and patterns.
