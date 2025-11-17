# Error Pipeline Plugin Quick Reference

## Plugin Matrix

| Plugin ID | Type | Extensions | Category | Requires | Success Codes |
|-----------|------|------------|----------|----------|---------------|
| **Python** |
| python_isort_fix | fix | py | - | - | [0] |
| python_black_fix | fix | py | - | python_isort_fix | [0] |
| python_ruff | lint | py | style | python_black_fix | [0,1] |
| python_pylint | lint | py | style | python_black_fix | [0,1] |
| python_mypy | type | py | type | python_black_fix | [0,1] |
| python_pyright | type | py | type | python_black_fix | [0,1] |
| python_bandit | security | py | security | python_black_fix | [0,1] |
| python_safety | security | py | security | python_black_fix | [0,1] |
| **PowerShell** |
| powershell_pssa | lint | ps1,psm1 | style/syntax | - | [0] |
| **JavaScript/TypeScript** |
| js_prettier_fix | fix | js,jsx,ts,tsx,json,md,yml,yaml | - | - | [0] |
| js_eslint | lint | js,jsx,ts,tsx | style | js_prettier_fix | [0,1] |
| **YAML** |
| yaml_yamllint | lint | yml,yaml | style/syntax | - | [0,1] |
| **Markdown** |
| md_mdformat_fix | fix | md | - | - | [0] |
| md_markdownlint | lint | md | style | md_mdformat_fix | [0,1] |
| **JSON** |
| json_jq | syntax | json | syntax | - | [0] |
| **Cross-Cutting** |
| codespell | lint | * | style | - | [0,1] |
| semgrep | security | * | security | - | [0,1] |
| gitleaks | security | * | security | - | [0,1] |

## Tool Installation Commands

### Python Tools
```bash
pip install black isort ruff pylint mypy pyright bandit safety
```

### PowerShell Tools
```powershell
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
```

### JavaScript/TypeScript Tools
```bash
npm install -g prettier eslint
```

### Markup/Data Tools
```bash
pip install yamllint mdformat
npm install -g markdownlint-cli
# jq: apt-get install jq | brew install jq | choco install jq
```

### Cross-Cutting Tools
```bash
pip install codespell semgrep
# gitleaks: download from https://github.com/gitleaks/gitleaks/releases
```

## Execution Order Examples

### Python File (example.py)
1. python_isort_fix
2. python_black_fix
3. python_ruff (parallel with 4-8)
4. python_pylint
5. python_mypy
6. python_pyright
7. python_bandit
8. python_safety
9. codespell
10. semgrep
11. gitleaks

### JavaScript File (example.js)
1. js_prettier_fix
2. js_eslint
3. codespell
4. semgrep
5. gitleaks

### Markdown File (example.md)
1. js_prettier_fix (if enabled for .md)
2. md_mdformat_fix
3. md_markdownlint
4. codespell
5. semgrep
6. gitleaks

### PowerShell File (example.ps1)
1. powershell_pssa
2. codespell
3. semgrep
4. gitleaks

### JSON File (example.json)
1. js_prettier_fix (if enabled for .json)
2. json_jq
3. codespell
4. semgrep
5. gitleaks

### YAML File (example.yml)
1. js_prettier_fix (if enabled for .yml)
2. yaml_yamllint
3. codespell
4. semgrep
5. gitleaks

## Category Mappings

| Category | Tools | Usage |
|----------|-------|-------|
| syntax | json_jq, yaml_yamllint*, powershell_pssa* | Parse errors |
| style | ruff, pylint, eslint, yamllint, markdownlint, pssa, codespell | Code style |
| type | mypy, pyright | Type checking |
| security | bandit, safety, semgrep, gitleaks | Security issues |

*Conditional: only for parse errors

## Severity Mappings

| Severity | Tools | Meaning |
|----------|-------|---------|
| error | Most tools (2→error in eslint) | Must fix |
| warning | Most tools (1→warning in eslint) | Should review |
| info | pssa (Information), semgrep (INFO) | Informational |

## Plugin States

- **Available**: Tool installed, plugin registered
- **Skipped**: Tool not installed, graceful skip
- **Executed**: Tool ran successfully
- **Failed**: Tool crashed or timed out

## Common Patterns

### Check Tool Availability
```python
def check_tool_available(self) -> bool:
    return shutil.which("tool_name") is not None
```

### Execute with Timeout
```python
proc = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=120,  # 180 for semgrep/gitleaks
    cwd=str(file_path.parent),
    env=scrub_env(),
    shell=False,
)
```

### Parse to Normalized Issues
```python
PluginIssue(
    tool="tool_name",
    path=file_path,
    line=123,
    column=45,
    code="RULE_ID",
    category="style",
    severity="warning",
    message="Description"
)
```

## Timeout Values

- **Standard**: 120 seconds (most plugins)
- **Extended**: 180 seconds (semgrep, gitleaks)

## File Extension Coverage

- **Python**: .py
- **PowerShell**: .ps1, .psm1
- **JavaScript**: .js, .jsx
- **TypeScript**: .ts, .tsx
- **JSON**: .json
- **YAML**: .yml, .yaml
- **Markdown**: .md
- **All**: * (cross-cutting tools)

## Quick Diagnostic Commands

### List all plugins
```bash
ls src/plugins/
```

### Check plugin structure
```bash
find src/plugins -name "manifest.json" | wc -l
find src/plugins -name "plugin.py" | wc -l
```

### Verify tool availability
```bash
black --version
isort --version
ruff --version
pylint --version
mypy --version
pyright --version
bandit --version
safety --version
pwsh -Command "Get-Module PSScriptAnalyzer -ListAvailable"
prettier --version
eslint --version
yamllint --version
mdformat --version
markdownlint --version
jq --version
codespell --version
semgrep --version
gitleaks version
```

## Non-Destructive Workflow

1. Original file: `file.py`
2. Copy to temp: `/tmp/pipeline-RUN/file.py`
3. Run fixes in temp
4. Validate in temp
5. Copy validated back to: `file_validated.py`
6. Never modify `file.py`

## References

- Full Documentation: `src/plugins/README.md`
- Implementation Summary: `docs/plugin-ecosystem-summary.md`
- Phase 08 Guide: `plans/phase-08-copilot-execution-guide.md`
- Test Specs: `plans/test-specs-plugins.md`
