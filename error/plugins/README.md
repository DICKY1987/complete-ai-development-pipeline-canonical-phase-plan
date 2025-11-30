---
doc_id: DOC-ERROR-README-090
---

# Error Detection Plugins

**Purpose**: Pluggable detection tools for Python, JavaScript, Markdown, YAML, security, and testing.

## Overview

Each plugin is a self-contained directory with a `manifest.json` and `plugin.py` that implements detection logic for specific file types. Plugins are discovered automatically by the error engine and executed in dependency order.

## Plugin Structure

```
error/plugins/
├── python_ruff/
│   ├── manifest.json          # Plugin metadata and dependencies
│   ├── plugin.py              # Detection logic
│   └── __init__.py
├── python_black_fix/          # Auto-fixer example
│   ├── manifest.json
│   ├── plugin.py
│   └── __init__.py
└── ... (21 total plugins)
```

## Available Plugins

### Python Detection

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `python_ruff` | Linting and style | Ruff | ❌ |
| `python_black_fix` | Code formatting | Black | ✅ |
| `python_isort_fix` | Import sorting | isort | ✅ |
| `python_mypy` | Type checking | mypy | ❌ |
| `python_pyright` | Type checking | Pyright | ❌ |
| `python_pylint` | Comprehensive linting | Pylint | ❌ |
| `python_bandit` | Security scanning | Bandit | ❌ |
| `python_safety` | Dependency vulnerabilities | Safety | ❌ |

### JavaScript/TypeScript Detection

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `js_eslint` | Linting | ESLint | ❌ |
| `js_prettier_fix` | Code formatting | Prettier | ✅ |

### Markdown Detection

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `md_markdownlint` | Markdown linting | markdownlint-cli | ❌ |
| `md_mdformat_fix` | Markdown formatting | mdformat | ✅ |

### YAML/JSON Detection

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `yaml_yamllint` | YAML linting | yamllint | ❌ |
| `json_jq` | JSON validation | jq | ❌ |

### Security & General

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `semgrep` | SAST scanning | Semgrep | ❌ |
| `gitleaks` | Secret detection | Gitleaks | ❌ |
| `codespell` | Spell checking | Codespell | ❌ |

### PowerShell

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `powershell_pssa` | PowerShell linting | PSScriptAnalyzer | ❌ |

### Testing & Utilities

| Plugin | Purpose | Tool | Auto-Fix |
|--------|---------|------|----------|
| `test_runner` | Run tests | pytest/jest | ❌ |
| `path_standardizer` | Path validation | Custom | ✅ |
| `echo` | Test/debug plugin | echo | ❌ |

## Plugin Manifest Schema

**`manifest.json`**:
```json
{
  "plugin_id": "python_ruff",
  "name": "Ruff Linter",
  "file_extensions": ["py"],
  "requires": ["python_black_fix"],
  "tool": {
    "success_codes": [0, 1]
  }
}
```

**Fields**:
- `plugin_id` (required): Unique identifier, matches directory name
- `name` (required): Human-readable name
- `file_extensions` (required): List of file extensions this plugin handles (without dot)
- `requires` (optional): List of plugin IDs that must run before this plugin (for DAG ordering)
- `tool.success_codes` (optional): Exit codes considered successful (default: `[0]`)

## Plugin Implementation

**Minimal `plugin.py`**:
```python
from pathlib import Path
from typing import List
from error.shared.utils.types import PluginIssue, PluginResult

class MyPlugin:
    plugin_id = "my_plugin"
    name = "My Plugin"
    manifest = {}

    def check_tool_available(self) -> bool:
        """Check if the tool is installed."""
        import shutil
        return shutil.which("mytool") is not None

    def build_command(self, file_path: Path) -> List[str]:
        """Build the command to run."""
        return ["mytool", "check", str(file_path)]

    def execute(self, file_path: Path) -> PluginResult:
        """Execute the tool and parse results."""
        from core.invoke_utils import run_command
        from error.shared.utils.env import scrub_env

        cmd = self.build_command(file_path)
        result = run_command(
            ' '.join(cmd),
            timeout=120,
            cwd=file_path.parent,
            env=scrub_env(),
        )

        issues = self.parse_output(result.stdout, file_path)

        return PluginResult(
            plugin_id=self.plugin_id,
            success=result.returncode in [0],
            issues=issues,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    def parse_output(self, output: str, file_path: Path) -> List[PluginIssue]:
        """Parse tool output into normalized issues."""
        issues = []
        # Custom parsing logic here
        return issues

def register():
    """Entry point for plugin discovery."""
    return MyPlugin()
```

## Auto-Fix Plugins

Auto-fix plugins modify files in-place and return the updated content.

**Example** (`python_black_fix`):
```python
def execute(self, file_path: Path) -> PluginResult:
    cmd = ["black", "--quiet", str(file_path)]
    result = run_command(' '.join(cmd), ...)

    # Read modified file
    modified_content = file_path.read_text()

    return PluginResult(
        plugin_id=self.plugin_id,
        success=True,
        issues=[],
        metadata={"file_out": str(file_path), "content": modified_content}
    )
```

**Detection**: The error engine compares file content before/after plugin execution to determine if auto-fix occurred.

## Plugin Dependencies

Plugins can declare dependencies via the `requires` field in `manifest.json`:

```json
{
  "plugin_id": "python_ruff",
  "requires": ["python_black_fix", "python_isort_fix"]
}
```

**Behavior**:
- Plugin manager uses topological sort to determine execution order
- Circular dependencies are rejected
- Missing dependencies cause plugin to be skipped

**Example DAG**:
```
python_black_fix → python_isort_fix → python_ruff → python_mypy
```

## Issue Normalization

All plugins return issues conforming to `PluginIssue`:

```python
@dataclass
class PluginIssue:
    tool: str                    # Plugin ID
    path: str                    # File path
    line: Optional[int]          # Line number (1-indexed)
    column: Optional[int]        # Column number (1-indexed)
    code: Optional[str]          # Error code (e.g., "E501")
    category: Optional[str]      # "syntax", "type", "style", "security", etc.
    severity: Optional[str]      # "error", "warning", "info"
    message: Optional[str]       # Human-readable message
```

**Categories**:
- `syntax` - Parse errors
- `type` - Type errors
- `style` - Code style violations
- `formatting` - Whitespace/indentation
- `security` - Security vulnerabilities
- `test_failure` - Test failures
- `dependency` - Dependency issues

**Severity Mapping**:
- `error` → Blocks quality gate
- `warning` → Logged but non-blocking (configurable)
- `info` → Informational only

## Creating a New Plugin

1. **Create plugin directory**:
   ```bash
   mkdir error/plugins/my_plugin
   cd error/plugins/my_plugin
   ```

2. **Add `manifest.json`**:
   ```json
   {
     "plugin_id": "my_plugin",
     "name": "My Plugin",
     "file_extensions": ["ext"],
     "requires": [],
     "tool": {
       "success_codes": [0]
     }
   }
   ```

3. **Add `plugin.py`**:
   ```python
   from error.shared.utils.types import PluginResult
   
   class MyPlugin:
       plugin_id = "my_plugin"
       name = "My Plugin"
       manifest = {}
       
       def check_tool_available(self) -> bool:
           return True
       
       def build_command(self, file_path):
           return ["my_tool", str(file_path)]
       
       def execute(self, file_path):
           # Implementation
           return PluginResult(plugin_id=self.plugin_id, success=True)
   
   def register():
       return MyPlugin()
   ```

4. **Add `__init__.py`**:
   ```python
   # Empty or re-export plugin class
   ```

5. **Test plugin**:
   ```bash
   pytest tests/plugins/test_my_plugin.py -v
   ```

6. **Verify discovery**:
   ```python
   from error.engine.plugin_manager import PluginManager
   pm = PluginManager()
   pm.discover()
   assert "my_plugin" in pm._plugins
   ```

## Plugin Testing

**Unit test template** (`tests/plugins/test_my_plugin.py`):
```python
from pathlib import Path
from error.plugins.my_plugin.plugin import register

def test_plugin_available():
    plugin = register()
    assert plugin.check_tool_available()

def test_plugin_execute(tmp_path):
    test_file = tmp_path / "test.ext"
    test_file.write_text("content")
    
    plugin = register()
    result = plugin.execute(test_file)
    
    assert result.success
    assert result.plugin_id == "my_plugin"
```

**Integration test**:
```python
from error.engine.plugin_manager import PluginManager

def test_plugin_discovery():
    pm = PluginManager()
    pm.discover()
    assert "my_plugin" in pm._plugins

def test_plugin_dag_ordering():
    pm = PluginManager()
    pm.discover()
    plugins = pm.get_plugins_for_file(Path("file.ext"))
    # Verify ordering respects dependencies
```

## Configuration

### Global Tool Profiles (`config/tool_profiles.json`)

Some plugins reference tool profiles for advanced configuration:

```json
{
  "pytest": {
    "type": "test",
    "command": "pytest",
    "args": ["-q"],
    "timeout-sec": 600,
    "success-exit-codes": [0, 5]
  }
}
```

### Plugin-Specific Settings

Some plugins support configuration files in the repository root:
- `ruff.toml` - Ruff configuration
- `.eslintrc.json` - ESLint rules
- `.markdownlint.json` - Markdown linting rules
- `pyproject.toml` - Black, isort, mypy settings

## Environment Variables

- `PIPELINE_ERROR_PLUGINS_PATH` - Override plugin discovery path
- Tool-specific variables (e.g., `RUFF_CACHE_DIR`, `MYPY_CACHE_DIR`)

## Performance Optimization

1. **Incremental validation**: File hash cache skips unchanged files
2. **Parallel execution**: Plugins run in parallel when no dependencies exist (future enhancement)
3. **Caching**: Tools like mypy/Ruff maintain internal caches
4. **Selective plugins**: Use `file_extensions` to minimize irrelevant plugin execution

## Troubleshooting

**Issue**: Plugin not discovered
- Verify `manifest.json` and `plugin.py` exist
- Check `plugin_id` matches directory name
- Ensure `register()` function exists

**Issue**: Tool not found
- Install tool: `pip install tool-name` or `npm install -g tool-name`
- Verify tool in PATH: `which tool-name` (Unix) or `where tool-name` (Windows)

**Issue**: Dependency cycle detected
- Review `requires` fields in `manifest.json`
- Remove circular dependencies

**Issue**: Parsing errors
- Check tool output format matches parser expectations
- Add logging to `parse_output()` method
- Verify tool supports required output format (JSON, SARIF, etc.)

## Best Practices

1. **Use structured output**: Prefer JSON/SARIF over plaintext parsing
2. **Timeout handling**: Set reasonable timeouts (default: 120s)
3. **Error isolation**: Plugin failures shouldn't crash the engine
4. **Category consistency**: Use standard categories for issue classification
5. **Exit codes**: Document all success/failure exit codes in `manifest.json`

## Related Sections

- **Error Engine**: `error/engine/` - Plugin orchestration
- **Shared Utils**: `error/shared/utils/` - Types and utilities
- **Configuration**: `config/` - Tool profiles
- **Tests**: `tests/plugins/` - Plugin unit tests

## See Also

- [Error Engine README](../engine/README.md)
- [Plugin Development Guide](../../docs/plugin_development.md)
- [Operating Contract](../../docs/operating_contract.md)
