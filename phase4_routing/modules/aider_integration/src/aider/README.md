---
doc_id: DOC-GUIDE-README-220
---

# Aider Integration Module

> **Module**: `aider`
> **Purpose**: Aider AI coding tool integration and prompt management
> **Layer**: Adapter/Integration
> **Status**: Production

---

## Overview

The **Aider** module provides integration with the Aider AI coding assistant, including prompt template management, command generation, and execution helpers. Aider is one of the primary AI coding tools supported by the pipeline.

**Key Features**:
- ✅ **Template-based prompts** - Jinja2 templates for EDIT and FIX prompts
- ✅ **Prompt file management** - Store prompts per workstream and step
- ✅ **Tool execution helpers** - Thin wrappers around `core.tools.run_tool`
- ✅ **Workstream templates** - JSON templates for Aider-specific workstreams
- ✅ **Documentation** - Aider-specific integration guides

---

## Directory Structure

```
aider/
├── engine.py                  # Prompt engine and execution helpers
├── templates/                 # Prompt templates
│   ├── prompts/              # Jinja2 prompt templates
│   │   ├── edit.j2           # EDIT step prompt
│   │   ├── fix.j2            # FIX loop prompt
│   │   └── ...
│   └── workstream_template.json  # Workstream bundle template
│
├── docs/                      # Aider-specific documentation
│   └── README.md             # Integration guide
│
└── help/                      # Help and reference materials
```

---

## Core Components

### Prompt Engine (`engine.py`)

Manages Aider prompt templates and execution.

#### Build EDIT Prompt

```python
from aider.engine import build_edit_prompt
from pathlib import Path

# Build EDIT step prompt
prompt = build_edit_prompt(
    tasks=["Add JWT authentication", "Add unit tests"],
    repo_path=Path("/path/to/repo"),
    ws_id="ws-feature-auth",
    run_id="run-2025-11-22-001",
    worktree_path=Path("/path/to/worktree"),
    files_scope=["src/auth.py", "tests/test_auth.py"],
    files_create=["src/auth_config.py"]
)

# Prompt is rendered from templates/prompts/edit.j2
print(prompt)
```

**Example EDIT Prompt** (from template):
```
You are working on workstream ws-feature-auth.

Tasks:
1. Add JWT authentication
2. Add unit tests

Files to modify:
- src/auth.py
- tests/test_auth.py

Files to create:
- src/auth_config.py

Please implement the requested changes.
```

#### Build FIX Prompt

```python
from aider.engine import build_fix_prompt

# Build FIX loop prompt
fix_prompt = build_fix_prompt(
    error_output="E501 line too long (85 > 79 characters)",
    original_tasks=["Add JWT authentication"],
    step_name="static",
    repo_path=Path("/path/to/repo"),
    ws_id="ws-feature-auth",
    files_scope=["src/auth.py"]
)

# Prompt is rendered from templates/prompts/fix.j2
print(fix_prompt)
```

**Example FIX Prompt**:
```
The static analysis step failed with the following error:

E501 line too long (85 > 79 characters)

Original task: Add JWT authentication

Please fix the error while preserving the original functionality.

Files in scope:
- src/auth.py
```

#### Prepare Prompt File

```python
from aider.engine import prepare_aider_prompt_file
from pathlib import Path

# Save prompt to worktree
prompt_file = prepare_aider_prompt_file(
    worktree=Path(".worktrees/ws-feature-auth"),
    step_name="edit",
    content=prompt
)

# Returns: Path(".worktrees/ws-feature-auth/.aider/prompts/edit.txt")
```

**Prompt File Location**: `<worktree>/.aider/prompts/<step_name>.txt`

---

### Execute Aider

#### EDIT Step

```python
from aider.engine import run_aider_edit
from pathlib import Path

# Execute Aider for EDIT step
result = run_aider_edit(
    worktree=Path(".worktrees/ws-feature-auth"),
    files=["src/auth.py"],
    prompt="Add JWT authentication",
    tasks=["Implement JWT encoding", "Add validation"],
    repo_path=Path.cwd(),
    ws_id="ws-feature-auth",
    timeout_sec=300
)

# Result is a ToolResult from core.tools
print(f"Success: {result.success}")
print(f"Files modified: {result.content.get('files_modified')}")
print(f"Exit code: {result.exit_code}")
```

**Under the Hood**:
1. Builds EDIT prompt from template
2. Saves prompt to `.aider/prompts/edit.txt`
3. Invokes `core.tools.run_tool("aider", context)`
4. Returns `ToolResult` with execution details

#### FIX Step

```python
from aider.engine import run_aider_fix

# Execute Aider for FIX loop
result = run_aider_fix(
    worktree=Path(".worktrees/ws-feature-auth"),
    files=["src/auth.py"],
    error_output="E501 line too long",
    original_tasks=["Add JWT authentication"],
    step_name="static",
    repo_path=Path.cwd(),
    ws_id="ws-feature-auth",
    timeout_sec=300
)
```

---

### Template System

Uses Jinja2 for flexible prompt templates.

#### Template Variables

Templates have access to these variables:

```python
{
    "tasks": ["Task 1", "Task 2"],           # List of tasks
    "files_scope": ["src/app.py"],           # Files to modify
    "files_create": ["src/new.py"],          # Files to create
    "ws_id": "ws-feature-auth",              # Workstream ID
    "run_id": "run-2025-11-22-001",         # Run ID
    "worktree_path": "/path/to/worktree",   # Worktree path
    "repo_path": "/path/to/repo",           # Repository path
    "error_output": "Error message",         # For FIX prompts
    "step_name": "static",                   # For FIX prompts
    "original_tasks": ["Original task"]      # For FIX prompts
}
```

#### Example Template (`templates/prompts/edit.j2`)

```jinja2
You are working on workstream {{ ws_id }}.

{% if tasks %}
Tasks:
{% for task in tasks %}
{{ loop.index }}. {{ task }}
{% endfor %}
{% endif %}

{% if files_scope %}
Files to modify:
{% for file in files_scope %}
- {{ file }}
{% endfor %}
{% endif %}

{% if files_create %}
Files to create:
{% for file in files_create %}
- {{ file }}
{% endfor %}
{% endif %}

Please implement the requested changes following best practices.
```

#### Custom Templates

Add custom templates to `templates/prompts/`:

```python
from aider.engine import TemplateRender

# Render custom template
renderer = TemplateRender(
    template="custom_template.j2",
    context={
        "custom_var": "value",
        "files": ["src/app.py"]
    }
)

prompt = renderer.render()
```

---

## Integration with Pipeline

### From Orchestrator

The orchestrator uses Aider via the tool adapter interface:

```python
from core.engine.orchestrator import run_edit_step

# Orchestrator automatically uses Aider if tool="aider" in bundle
result = run_edit_step(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    bundle_obj=bundle,  # bundle.tool == "aider"
    context={"timeout_sec": 300}
)
```

**Flow**:
1. Orchestrator calls `core.tools.run_tool("aider", context)`
2. Tool adapter loads Aider profile from `config/tool_profiles.json`
3. Renders command with variable substitution
4. Executes Aider CLI
5. Returns `ToolResult` to orchestrator

### From Workstream Bundle

Specify Aider in the workstream bundle:

```json
{
  "id": "ws-feature-auth",
  "openspec_change": "OS-AUTH-001",
  "ccpm_issue": 42,
  "gate": 2,
  "tool": "aider",
  "files_scope": ["src/auth.py"],
  "files_create": ["src/auth_config.py"],
  "tasks": [
    "Implement JWT authentication",
    "Add unit tests for auth module"
  ]
}
```

### Tool Profile Configuration

Aider configuration in `config/tool_profiles.json`:

```json
{
  "aider": {
    "binary": "aider",
    "args": [
      "--yes",
      "--no-auto-commits",
      "--message", "{prompt}",
      "{files}"
    ],
    "env": {
      "AIDER_NO_GIT": "1",
      "OPENAI_API_KEY": "{OPENAI_API_KEY}"
    },
    "timeout_sec": 300,
    "working_dir": "{worktree_path}"
  }
}
```

**Variable Substitution**:
- `{prompt}` → Rendered prompt content
- `{files}` → Space-separated list of files
- `{worktree_path}` → Path to worktree
- `{OPENAI_API_KEY}` → Environment variable

---

## Workstream Templates

Template for creating Aider-specific workstreams.

**File**: `templates/workstream_template.json`

```json
{
  "id": "ws-CHANGEME",
  "openspec_change": "OS-XXX-001",
  "ccpm_issue": 0,
  "gate": 1,
  "tool": "aider",
  "files_scope": [],
  "files_create": [],
  "tasks": [],
  "acceptance_tests": [],
  "depends_on": [],
  "parallel_ok": true,
  "metadata": {
    "notes": "Template for Aider workstreams"
  }
}
```

**Usage**:
```bash
# Copy template
cp aider/templates/workstream_template.json workstreams/ws-my-feature.json

# Edit and fill in details
# Run validation
python scripts/validate_workstreams.py
```

---

## Best Practices

1. **Use templates** - Don't hardcode prompts; use Jinja2 templates
2. **Keep prompts focused** - One clear task per EDIT step
3. **Provide context in FIX prompts** - Include error output and original intent
4. **Limit file scope** - Aider works best with 3-5 files per workstream
5. **Save prompt files** - Stored in `.aider/prompts/` for debugging
6. **Set timeouts** - Prevent hanging on complex tasks
7. **Use tool profiles** - Centralize Aider configuration

---

## Debugging

### View Generated Prompts

```python
from aider.engine import build_edit_prompt, prepare_aider_prompt_file
from pathlib import Path

# Build prompt
prompt = build_edit_prompt(...)

# View content
print(prompt)

# Or read from saved file
prompt_file = Path(".worktrees/ws-feature-auth/.aider/prompts/edit.txt")
print(prompt_file.read_text())
```

### Dry-Run Mode

```python
from core.engine.orchestrator import run_edit_step

# Run without executing Aider
result = run_edit_step(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    bundle_obj=bundle,
    context={"dry_run": True}  # Skip Aider execution
)
```

### Verbose Logging

Set environment variable:
```bash
export PIPELINE_LOG_LEVEL=DEBUG
python scripts/run_workstream.py ws-feature-auth
```

---

## Configuration

### Environment Variables

- **`OPENAI_API_KEY`** - OpenAI API key (required for Aider)
- **`ANTHROPIC_API_KEY`** - Anthropic API key (for Claude models)
- **`AIDER_NO_GIT`** - Disable git integration (default: `1`)
- **`PIPELINE_DRY_RUN`** - Skip Aider execution (default: `0`)

### Tool Profile Settings

Customize Aider behavior in `config/tool_profiles.json`:

```json
{
  "aider": {
    "binary": "aider",
    "args": [
      "--yes",
      "--no-auto-commits",
      "--model", "gpt-4",
      "--message", "{prompt}",
      "{files}"
    ],
    "timeout_sec": 600
  }
}
```

---

## Testing

Tests are located in `tests/`:

```bash
# Test prompt rendering
pytest tests/test_aider_engine.py::test_build_edit_prompt -v

# Test Aider execution (requires Aider installed)
pytest tests/test_aider_integration.py -v

# Test template rendering
pytest tests/test_template_render.py -v
```

---

## Troubleshooting

### Aider Not Found

**Error**: `aider: command not found`

**Solution**:
```bash
# Install Aider
pip install aider-chat

# Or via pipx
pipx install aider-chat

# Verify installation
aider --version
```

### Timeout Errors

**Error**: `Tool execution timed out after 300s`

**Solution**: Increase timeout in tool profile or context:
```json
{
  "aider": {
    "timeout_sec": 600  // Increase from 300 to 600
  }
}
```

### Template Not Found

**Error**: `Template not found: edit.j2`

**Solution**: Verify template directory structure:
```bash
ls aider/templates/prompts/
# Should contain: edit.j2, fix.j2, etc.
```

---

## Related Documentation

- **Tool Adapter**: `core/engine/tools.py` - Unified tool interface
- **Orchestrator**: `core/engine/README.md` - Execution engine
- **Tool Profiles**: `config/tool_profiles.json` - Tool configuration
- **AIM Integration**: `aim/README.md` - Capability-based routing
- **Workstream Schema**: `schema/workstream_bundle.schema.json` - Bundle format
- **Documentation**: `aider/docs/README.md` - Aider-specific guides

---

## Roadmap

### Phase 1 (Current - Production)
- ✅ Template-based prompts
- ✅ EDIT and FIX prompt generation
- ✅ Tool execution helpers
- ✅ Prompt file management
- ✅ Workstream templates

### Phase 2 (Planned)
- 🔜 Multi-model support (GPT-4, Claude, Gemini)
- 🔜 Cost optimization (select cheapest model per task)
- 🔜 Prompt caching
- 🔜 Interactive mode support
- 🔜 Prompt A/B testing

### Phase 3 (Future)
- 🔜 Custom prompt library
- 🔜 Prompt versioning and rollback
- 🔜 AI-powered prompt generation
- 🔜 Aider plugin system integration
- 🔜 Multi-agent coordination
