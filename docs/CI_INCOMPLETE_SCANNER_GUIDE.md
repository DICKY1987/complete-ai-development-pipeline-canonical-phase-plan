# Incomplete Implementation Scanner - CI Integration Guide

**DOC_ID**: `DOC-GUIDE-INCOMPLETE-SCANNER-CI`

## Quick Start

### Run Scanner Locally
```bash
# Basic scan
python scripts/scan_incomplete_implementation.py

# Custom output location
python scripts/scan_incomplete_implementation.py --output reports/incomplete.json

# CI threshold check (fails if critical > 0 or major > 10)
python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0 --max-major 10
```

---

## CI Integration

### GitHub Actions Workflow

Add to `.github/workflows/incomplete-check.yml`:

```yaml
name: Incomplete Implementation Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run incomplete implementation scanner
        run: |
          python scripts/scan_incomplete_implementation.py \
            --ci-check \
            --max-critical 0 \
            --max-major 5 \
            --output .state/incomplete_scan.json

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: incomplete-scan-results
          path: .state/incomplete_scan.json

      - name: Comment PR with summary
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('.state/incomplete_scan.json', 'utf8'));

            const critical = results.summary_by_severity.critical || 0;
            const major = results.summary_by_severity.major || 0;
            const minor = results.summary_by_severity.minor || 0;

            const body = `## 🔍 Incomplete Implementation Scan

            - 🔴 Critical: ${critical}
            - 🟡 Major: ${major}
            - 🔵 Minor: ${minor}

            ${critical > 0 ? '⚠️ **Action required**: Critical stubs found in core modules' : '✅ No critical issues'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: incomplete-scan
        name: Scan for incomplete implementations
        entry: python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0
        language: system
        pass_filenames: false
        stages: [commit]
```

Or create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0 --max-major 10
exit $?
```

---

## Threshold Configuration

### Development Phase Thresholds

**Early Development** (MVP, prototyping):
```bash
--max-critical 10 --max-major 50
```

**Feature Development** (adding new modules):
```bash
--max-critical 5 --max-major 20
```

**Pre-Release** (hardening):
```bash
--max-critical 1 --max-major 5
```

**Production Ready**:
```bash
--max-critical 0 --max-major 0
```

### Module-Specific Gates

For phased rollouts, create separate checks:

```bash
# Check only core modules (strict)
python scripts/scan_incomplete_implementation.py --root core/ --ci-check --max-critical 0

# Check experimental modules (lenient)
python scripts/scan_incomplete_implementation.py --root experiments/ --ci-check --max-critical 50
```

---

## Whitelist Management

### When to Whitelist

**✅ Legitimate whitelisting**:
- Abstract base classes / interfaces
- Test fixtures and mocks
- Documentation examples
- Intentional extension points

**❌ Bad whitelisting** (fix instead):
- Core business logic
- Public API methods
- Referenced by tests but not implemented
- TODOs in production code paths

### Add to Whitelist

Edit `incomplete_allowlist.yaml`:

```yaml
allowed_stubs:
  - path: "core/new_interface.py"
    symbol: "process_data"
    reason: "Extension point for plugins, documented in PLUGIN_API.md"
    approved_by: "tech-lead"
    review_date: "2025-12-04"
```

Or use inline marker in code:

```python
# INCOMPLETE_OK: Abstract interface for plugin system
def process_data(self, data: Any) -> Result:
    raise NotImplementedError("Implement in subclass")
```

---

## Reading Scan Results

### JSON Output Structure

```json
{
  "scan_timestamp": "2025-12-04T04:48:48Z",
  "codebase_root": ".",
  "stats": {
    "stub_function": 107,
    "stub_class": 15,
    "empty_dir": 125,
    "todo_marker": 24
  },
  "summary_by_severity": {
    "critical": 0,
    "major": 0,
    "minor": 271
  },
  "findings": [
    {
      "kind": "stub_function",
      "path": "core/engine/router.py",
      "symbol": "route_request",
      "line": 42,
      "reason": "function_body_is_pass",
      "severity": "critical",
      "context_score": 3.0,
      "body_preview": "    pass"
    }
  ]
}
```

### Query Findings

Use `jq` to filter:

```bash
# Show all critical findings
jq '.findings[] | select(.severity == "critical")' .state/incomplete_scan.json

# Count stubs by module
jq '.findings | group_by(.path | split("/")[0]) | map({module: .[0].path | split("/")[0], count: length})' .state/incomplete_scan.json

# List top stub files
jq -r '.findings | group_by(.path) | map({path: .[0].path, count: length}) | sort_by(-.count) | .[:10] | .[] | "\(.count)\t\(.path)"' .state/incomplete_scan.json
```

---

## Monitoring and Trends

### Track Over Time

Store scan results by date:

```bash
# Daily scan
python scripts/scan_incomplete_implementation.py \
  --output ".state/incomplete_scan_$(date +%Y%m%d).json"

# Compare to previous
python scripts/compare_scans.py \
  .state/incomplete_scan_20251203.json \
  .state/incomplete_scan_20251204.json
```

### Metrics to Track

1. **Total stubs**: Overall code completeness
2. **Critical stubs**: Blockers for release
3. **Stubs per module**: Module health
4. **New stubs in PR**: Regression detection
5. **Stub age**: How long TODOs have existed

---

## Integration with Phase Planning

### Automatic Task Generation

Use scan results to generate phase plan tasks:

```python
# Example: Convert critical findings to workstream tasks
import json

with open('.state/incomplete_scan.json') as f:
    scan = json.load(f)

critical = [f for f in scan['findings'] if f['severity'] == 'critical']

for finding in critical:
    print(f"""
    - task_id: IMPL-{finding['line']:04d}
      title: Implement {finding['symbol']}
      file: {finding['path']}
      reason: {finding['reason']}
      priority: critical
    """)
```

### Pre-release Checklist

Add to `RELEASE_CHECKLIST.md`:

```markdown
## Pre-Release Verification

- [ ] Run incomplete implementation scanner
- [ ] Verify zero critical stubs: `python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0`
- [ ] Review and clear all major stubs or whitelist with justification
- [ ] Update `incomplete_allowlist.yaml` with review dates
```

---

## Troubleshooting

### False Positives

**Problem**: Legitimate code flagged as stub

**Solution**:
1. Add inline marker: `# INCOMPLETE_OK: reason`
2. Add to `incomplete_allowlist.yaml`
3. Check if detection rules are too strict

### False Negatives

**Problem**: Actual stubs not detected

**Solution**:
1. Check if file type is supported (currently Python only)
2. Verify stub patterns in `INCOMPLETE_IMPLEMENTATION_RULES.md`
3. Add custom detection rules for project-specific patterns

### Performance Issues

**Problem**: Scanner is too slow on large codebase

**Solution**:
1. Use `--root` to scan specific directories only
2. Add more patterns to `IGNORED_DIRS` in script
3. Run in parallel for different modules
4. Cache results and only scan changed files

---

## Advanced Usage

### Custom Severity Rules

Modify `SEVERITY_MULTIPLIERS` in script:

```python
SEVERITY_MULTIPLIERS = {
    "core/": 5.0,           # Extra critical
    "api/public/": 4.0,     # Public API is important
    "internal/": 0.5,       # Internal tools less critical
}
```

### Plugin Detection

Add detection for project-specific patterns:

```python
def detect_custom_stubs(content: str, file_path: Path) -> List[Finding]:
    """Custom detection for project-specific stubs."""
    findings = []

    # Example: Detect route handlers with no implementation
    if re.search(r'@app\.route.*\n\s+pass', content):
        findings.append(Finding(
            kind="stub_route_handler",
            path=str(file_path),
            reason="route_handler_is_empty"
        ))

    return findings
```

---

## Version History

- **v1.0.0** (2025-12-04): Initial implementation
  - Python stub detection
  - Empty structure detection
  - CI integration support
  - Severity scoring
  - Whitelist mechanism
