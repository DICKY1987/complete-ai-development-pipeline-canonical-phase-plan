# Error Pipeline Plugin Ecosystem

This document provides a comprehensive overview of all plugins in the error pipeline, their dependencies, and execution ordering.

## Plugin Categories

### Python (M1-M2) ✅ COMPLETE
**Fix Plugins:**
- `python_isort_fix` - Import sorting (no dependencies)
- `python_black_fix` - Code formatting (requires: `python_isort_fix`)

**Lint Plugins:**
- `python_ruff` - Fast linter (requires: `python_black_fix`)
- `python_pylint` - Comprehensive linter (requires: `python_black_fix`)

**Type Checking:**
- `python_mypy` - Static type checker (requires: `python_black_fix`)
- `python_pyright` - Microsoft type checker (requires: `python_black_fix`)

**Security:**
- `python_bandit` - Security vulnerability scanner (requires: `python_black_fix`)
- `python_safety` - Dependency vulnerability scanner (requires: `python_black_fix`)

### PowerShell (M3) ✅ NEW
- `powershell_pssa` - PSScriptAnalyzer for .ps1, .psm1 files
  - Extensions: `ps1`, `psm1`
  - Category: `style` (parse errors → `syntax`)
  - Severity mapping: Error→error, Warning→warning, Information→info

### JavaScript/TypeScript (M4) ✅ NEW
**Fix Plugins:**
- `js_prettier_fix` - Code formatter (no dependencies)
  - Extensions: `js`, `jsx`, `ts`, `tsx`, `json`, `md`, `yml`, `yaml`
  - No issues emitted (fix-only)

**Lint Plugins:**
- `js_eslint` - JavaScript/TypeScript linter (requires: `js_prettier_fix`)
  - Extensions: `js`, `jsx`, `ts`, `tsx`
  - Category: `style`
  - Severity mapping: 2→error, 1→warning

### Markup/Data (M5) ✅ NEW
**YAML:**
- `yaml_yamllint` - YAML linter
  - Extensions: `yml`, `yaml`
  - Category: `style` (syntax errors → `syntax`)
  - Parsable format output

**Markdown:**
- `md_mdformat_fix` - Markdown formatter (no dependencies)
  - Extensions: `md`
  - No issues emitted (fix-only)
- `md_markdownlint` - Markdown linter (requires: `md_mdformat_fix`)
  - Extensions: `md`
  - Category: `style`
  - JSON and text format parsing

**JSON:**
- `json_jq` - JSON syntax validator
  - Extensions: `json`
  - Category: `syntax`
  - Single error issue on parse failure

### Cross-Cutting (M6) ✅ NEW
- `codespell` - Spelling checker
  - Extensions: `*` (all files)
  - Category: `style`
  - Severity: `warning`

- `semgrep` - Security pattern scanner
  - Extensions: `*` (all files)
  - Category: `security`
  - Severity mapping: ERROR→error, WARNING→warning, INFO→info
  - Uses `--config auto` for community rules

- `gitleaks` - Secret detection
  - Extensions: `*` (all files)
  - Category: `security`
  - Severity: `error`
  - Filters results to target file only

## Execution Ordering

Plugins are executed in topological order based on `requires` dependencies in their `manifest.json`:

### Python Chain
```
python_isort_fix
  ↓
python_black_fix
  ↓
├── python_ruff
├── python_pylint
├── python_mypy
├── python_pyright
├── python_bandit
└── python_safety
```

### JS/TS Chain
```
js_prettier_fix
  ↓
js_eslint
```

### Markdown Chain
```
md_mdformat_fix
  ↓
md_markdownlint
```

### Independent Plugins
- `powershell_pssa`
- `yaml_yamllint`
- `json_jq`
- `codespell`
- `semgrep`
- `gitleaks`

## Plugin Architecture

### Common Patterns
All plugins follow a consistent structure:

```python
class PluginClass:
    plugin_id = "plugin_id"
    name = "Plugin Name"
    manifest = {}

    def check_tool_available(self) -> bool:
        return shutil.which("tool") is not None

    def build_command(self, file_path: Path) -> List[str]:
        return ["tool", "args", str(file_path)]

    def execute(self, file_path: Path) -> PluginResult:
        # Execute with scrub_env(), timeout, shell=False
        # Parse output to normalized PluginIssue objects
        # Return PluginResult
```

### Normalized Issue Format
```python
PluginIssue(
    tool="tool_name",
    path="file/path",
    line=123,                    # Optional
    column=45,                   # Optional
    code="RULE_CODE",           # Optional
    category="style|syntax|type|security|test_failure",
    severity="error|warning|info",
    message="Description"
)
```

### Category Mappings
- **syntax**: Parse errors, JSON/YAML syntax issues
- **style**: Code style, formatting, linting rules
- **type**: Type checking errors (mypy, Pyright)
- **security**: Security vulnerabilities, secrets, patterns
- **test_failure**: Test execution failures (optional Pester)

### Severity Mappings
- **error**: Critical issues that must be fixed
- **warning**: Important issues that should be reviewed
- **info**: Informational notices

## Graceful Degradation

Plugins handle tool absence gracefully:
- `check_tool_available()` returns `False` → plugin not registered
- No failures for missing tools
- Users install only tools they need

## Non-Destructive Execution

All plugins follow the Operating Contract:
- Original files never modified
- Fixes occur in temp directories
- Validated outputs copied to target location
- Mechanical autofix updates `ctx.python_files` for recheck

## Testing

Plugin tests are specified in `plans/test-specs-plugins.md` and implemented separately:
- Tolerant parsing for version differences
- Timeout enforcement (120-180s)
- Environment scrubbing
- Deterministic ordering verification

## Tool Installation

Users must install tools locally:

**Python:**
```bash
pip install black isort ruff pylint mypy pyright bandit safety
```

**PowerShell:**
```powershell
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
```

**JavaScript/TypeScript:**
```bash
npm install -g prettier eslint
```

**Markup/Data:**
```bash
pip install yamllint mdformat
npm install -g markdownlint-cli
# jq: platform-specific (apt/brew/choco)
```

**Cross-Cutting:**
```bash
pip install codespell
pip install semgrep
# gitleaks: download from GitHub releases
```

## Success Codes

Plugins specify acceptable return codes in `manifest.json`:
- `[0]`: Fix plugins, syntax validators (must succeed)
- `[0, 1]`: Lint plugins (1 = issues found, still valid execution)

## Performance Considerations

- **Timeouts**: 120s default, 180s for Semgrep/Gitleaks
- **Isolation**: `cwd=file_path.parent` for relative path resolution
- **Environment**: `scrub_env()` removes potentially problematic variables
- **No Shell**: `shell=False` prevents injection and platform issues

## Total Plugin Count

- **Python**: 8 plugins (2 fix, 2 lint, 2 type, 2 security)
- **PowerShell**: 1 plugin
- **JS/TS**: 2 plugins (1 fix, 1 lint)
- **Markup/Data**: 4 plugins (1 YAML, 2 Markdown, 1 JSON)
- **Cross-Cutting**: 3 plugins
- **Total**: 18 plugins

## Status

- ✅ M1: Python baseline (DONE)
- ✅ M2: Python security/deps (DONE)
- ✅ M3: PowerShell (DONE)
- ✅ M4: JS/TS (DONE)
- ✅ M5: Markup/Data (DONE)
- ✅ M6: Cross-Cutting (DONE)
- 🔄 M7: Testing & docs handoff (in progress)

## References

- Operating Contract: `MOD_ERROR_PIPELINE/ERROR_Operating Contract.txt`
- State Machine Spec: `MOD_ERROR_PIPELINE/state-machine specification.txt`
- Architecture: `MOD_ERROR_PIPELINE/ARCHITECTURE.md`
- Execution Guide: `plans/phase-08-copilot-execution-guide.md`
- Test Specs: `plans/test-specs-plugins.md`
