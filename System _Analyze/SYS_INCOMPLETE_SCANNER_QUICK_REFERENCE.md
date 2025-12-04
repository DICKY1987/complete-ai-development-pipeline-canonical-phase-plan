# Incomplete Implementation Scanner - Quick Reference

**One-page cheat sheet for daily use**

---

## 🚀 Quick Commands

```bash
# Run basic scan
python scripts/scan_incomplete_implementation.py

# Generate report
python scripts/generate_incomplete_report.py

# Compare two scans
python scripts/compare_incomplete_scans.py scan1.json scan2.json

# CI check (fail if thresholds exceeded)
python scripts/scan_incomplete_implementation.py --ci-check --max-critical 0 --max-major 10
```

---

## 📊 What Gets Detected

| Category | Examples |
|----------|----------|
| **Stub Functions** | `pass`, `...`, `raise NotImplementedError` |
| **Stub Classes** | All methods are stubs |
| **Empty Dirs** | No files (or only `__pycache__`) |
| **TODO Markers** | `TODO`, `FIXME`, `WIP`, `STUB`, `XXX` |

---

## 🎯 Severity Levels

- 🔴 **Critical**: Core modules (`core/`, `engine/`, `error/`)
- 🟡 **Major**: Domain modules (`aim/`, `pm/`, `specifications/`)
- 🔵 **Minor**: Everything else
- ⚪ **Allowed**: Whitelisted (interfaces, test fixtures, examples)

---

## ✅ Whitelist a Stub

### Method 1: Inline Marker
```python
# INCOMPLETE_OK: Abstract interface for plugins
def process(self, data):
    raise NotImplementedError
```

### Method 2: Config File
Edit `incomplete_allowlist.yaml`:
```yaml
allowed_stubs:
  - path: "core/interface.py"
    reason: "Abstract base class"
```

---

## 🔍 Query Results

```bash
# Show all critical findings
jq '.findings[] | select(.severity == "critical")' .state/incomplete_scan.json

# Count by severity
jq '.summary_by_severity' .state/incomplete_scan.json

# Top 10 stub files
jq -r '.findings | group_by(.path) | map({path: .[0].path, count: length}) | sort_by(-.count) | .[:10] | .[] | "\(.count)\t\(.path)"' .state/incomplete_scan.json
```

---

## 🎛️ CI Thresholds

| Phase | Critical | Major | Use Case |
|-------|----------|-------|----------|
| **Development** | 10 | 50 | Early prototyping |
| **Feature Work** | 5 | 20 | Active development |
| **Pre-Release** | 1 | 5 | Hardening |
| **Production** | 0 | 0 | Release ready |

---

## 📈 Track Trends

```bash
# Daily scan
python scripts/scan_incomplete_implementation.py \
  --output .state/scan_$(date +%Y%m%d).json

# Compare to yesterday
python scripts/compare_incomplete_scans.py \
  .state/scan_$(date -d yesterday +%Y%m%d).json \
  .state/scan_$(date +%Y%m%d).json
```

---

## ⚠️ Common Issues

**False Positive**: Legitimate code flagged
- Add inline `# INCOMPLETE_OK: reason` marker
- Or add to `incomplete_allowlist.yaml`

**False Negative**: Actual stub not detected
- Check if file type is supported (currently Python only)
- Verify detection patterns in `INCOMPLETE_IMPLEMENTATION_RULES.md`

**Performance**: Scanner too slow
- Use `--root` to scan specific directory only
- Add patterns to `IGNORED_DIRS` in script

---

## 📄 Output Files

| File | Purpose |
|------|---------|
| `.state/incomplete_scan.json` | Raw scan results (for automation) |
| `reports/incomplete_report.md` | Human-readable summary |

---

## 🔗 Related Files

- **Rules**: `INCOMPLETE_IMPLEMENTATION_RULES.md`
- **CI Guide**: `docs/CI_INCOMPLETE_SCANNER_GUIDE.md`
- **Deployment Summary**: `INCOMPLETE_SCANNER_DEPLOYMENT_SUMMARY.md`
- **Whitelist**: `incomplete_allowlist.yaml`

---

## 💡 Pro Tips

1. **Run before every commit** to catch new stubs early
2. **Review TODO markers** quarterly to prevent accumulation
3. **Track critical stubs** as blocking issues
4. **Whitelist intentionally**, with clear reasoning
5. **Compare scans** in PRs to catch regressions

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-04
