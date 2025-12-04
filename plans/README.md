# Orchestration Plans Directory

This directory contains **JSON plan files** for the unified orchestration engine.

## Schema Reference

Each plan file follows this structure:

```json
{
  "plan_id": "PLAN-NAME-001",
  "version": "1.0",
  "description": "Human-readable description",
  "metadata": {
    "project": "project-id",
    "tags": ["tag1", "tag2"]
  },
  "globals": {
    "max_concurrency": 2,
    "default_timeout_sec": 1800,
    "default_retries": 0,
    "env": {}
  },
  "steps": [
    {
      "id": "unique_step_id",
      "name": "Human name",
      "command": "executable",
      "args": ["arg1", "arg2"],
      "depends_on": ["other_step_id"],
      "timeout_sec": 600,
      "retries": 2,
      "retry_delay_sec": 5,
      "critical": true,
      "on_failure": "abort",
      "tags": ["phase:1"]
    }
  ]
}
```

## Field Definitions

### Plan Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_id` | string | ✅ | Unique identifier (e.g., `PLAN-SAFE-MERGE-001`) |
| `version` | string | ✅ | Semantic version (e.g., `1.0`) |
| `description` | string | ❌ | Human-readable purpose |
| `metadata` | object | ❌ | Arbitrary metadata (project, tags, etc.) |
| `globals` | object | ✅ | Default values for all steps |

### Globals

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_concurrency` | int | 1 | Max parallel steps |
| `default_timeout_sec` | int | 1800 | Default step timeout (30 min) |
| `default_retries` | int | 0 | Default retry count |
| `env` | object | {} | Environment variables for all steps |

### Step Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique step identifier |
| `name` | string | ✅ | Display name |
| `description` | string | ❌ | Human-readable purpose |
| `command` | string | ✅ | Executable (e.g., `python`, `pwsh`, `git`) |
| `args` | array | ✅ | Command arguments |
| `cwd` | string | `.` | Working directory |
| `shell` | bool | `false` | Use shell invocation |
| `env` | object | `{}` | Step-specific env vars |
| `depends_on` | array | `[]` | Step IDs that must succeed first |
| `timeout_sec` | int | (global) | Override global timeout |
| `retries` | int | (global) | Override global retries |
| `retry_delay_sec` | int | 0 | Seconds between retries |
| `critical` | bool | `true` | If true + abort, kills pipeline |
| `condition` | string | `null` | Optional condition expression |
| `on_failure` | enum | `abort` | `abort` \| `skip_dependents` \| `continue` |
| `provides` | array | `[]` | Logical resources produced |
| `consumes` | array | `[]` | Logical resources required |
| `tags` | array | `[]` | Arbitrary tags for filtering/grouping |
| `ui_hints` | object | `{}` | Display hints (group, weight) |

## Variable Substitution

Plans support runtime variable substitution using `${VAR}` syntax:

```json
{
  "args": ["--branch", "${BRANCH}", "--output", "${OUTPUT_DIR}/result.json"]
}
```

Supply variables at runtime:
```bash
python -m core.engine.orchestrator plans/safe_merge.json --var BRANCH=main --var OUTPUT_DIR=/tmp
```

## Failure Policies

### `on_failure: "abort"`
Stop the entire pipeline immediately. Mark all pending steps as `CANCELED`.

**Use when**: Step failure makes continuing pointless (e.g., failed authentication).

### `on_failure: "skip_dependents"`
Mark all downstream dependent steps as `SKIPPED`, but continue running independent steps.

**Use when**: Failure affects only a sub-graph (e.g., optional deployment).

### `on_failure: "continue"`
Ignore the failure and continue executing dependent steps anyway.

**Use when**: Step is informational (e.g., logging, notifications).

## Example Plans

### Safe Merge (`safe_merge.json`)
Full 11-step merge validation pipeline with:
- Environment scanning
- Sync health gates
- Nested repo detection
- AI conflict resolution
- Guarded push with locking

**Run**:
```bash
python -m core.engine.orchestrator plans/safe_merge.json --var BRANCH=feature-123
```

### (Future) Doc-ID Restore
Planned pipeline for restoring doc-IDs from backup.

### (Future) Test Gate
Pre-commit test pipeline (lint → test → commit).

## Creating New Plans

1. **Copy template**:
   ```bash
   cp plans/safe_merge.json plans/my_plan.json
   ```

2. **Edit fields**:
   - Change `plan_id`
   - Update `steps` array
   - Set `depends_on` for DAG ordering

3. **Validate**:
   ```python
   from core.engine.plan_schema import Plan
   Plan.from_file("plans/my_plan.json")  # Raises if invalid
   ```

4. **Test**:
   ```bash
   python -m core.engine.orchestrator plans/my_plan.json --var KEY=value
   ```

## Best Practices

1. **Keep steps atomic**: Each step should do one thing well
2. **Use retries for network ops**: Set `retries: 2` for git fetch, API calls
3. **Set realistic timeouts**: Default 30min may be too long for simple steps
4. **Tag extensively**: Use `tags` for filtering in GUI/reports
5. **Mark critical gates**: Set `critical: true` + `on_failure: abort` for validation gates
6. **Document dependencies**: Add comments in JSON explaining why step A depends on B

## Troubleshooting

### Plan fails to load
- Check JSON syntax with `jq . plans/my_plan.json`
- Verify all `depends_on` step IDs exist
- Ensure no circular dependencies (A → B → A)

### Step never runs
- Check `depends_on` targets succeeded
- Verify `condition` expression (if present)
- Check `max_concurrency` limit

### Timeout issues
- Increase `timeout_sec` for slow steps
- Check if process is actually stalled (not just slow)
- Review logs in `.state/runs.db` for actual duration

### Retries not working
- Verify `retries > 0`
- Check `retry_delay_sec` is set
- Ensure failure is transient (not permanent error)

## See Also

- `INTEGRATION_PLAN.md` - Full migration plan
- `core/engine/orchestrator.py` - Orchestration engine
- `core/engine/plan_schema.py` - Schema validation
