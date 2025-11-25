# Anti-Pattern Guards - Manual Checklist

## Phase 1: Foundation (Week 1)

### Tier 1 Critical Guards (MUST check before commit)

- [ ] **Hallucination of Success**
  - All `subprocess.run()` calls use `check=True`
  - Validation script exit codes checked programmatically
  - No "marked complete without verification"

- [ ] **Incomplete Implementation**
  - No `# TODO` markers in committed code
  - No `pass  #` placeholder implementations
  - No `raise NotImplementedError` in production code

- [ ] **Silent Failures**
  - All file operations have error handling
  - All external commands capture and check output
  - Failures logged before exit

### Tier 2 High Priority Guards (Check weekly)

- [ ] **Test-Code Mismatch**
  - Tests actually exercise the code
  - No tests with only `assert result is not None`
  - Tests verify behavior, not just existence

- [ ] **Worktree Contamination**
  - Cleanup worktrees after use (max 24h lifespan)
  - No duplicate results in searches (4x same file)
  - Git performance normal

### Tier 3 Medium Priority Guards (Check before merge)

- [ ] **Configuration Drift**
  - No hardcoded paths (use Path objects)
  - Configuration loaded from files
  - No magic numbers

- [ ] **Documentation Lies**
  - Docstrings match actual function signatures
  - Examples in docs actually work
  - Type hints accurate

---

## Guard Enforcement

### Before Each Commit
```bash
# Check for TODOs
git diff --cached | grep "# TODO"
# Should return nothing

# Run validation
python scripts/validate_migration_phase1.py
# Must exit with code 0
```

### Weekly Cleanup
```bash
# List worktrees
git worktree list

# Remove unused worktrees (> 24h old)
git worktree remove .worktrees/{name}

# Check for duplicate files
find . -name "*.py" | sort | uniq -d
# Should return nothing
```

### Before Merge to Main
```bash
# Full validation suite
python scripts/validate_migration_phase1.py

# All tests pass
pytest tests/ -x

# No syntax errors
python -m py_compile $(find modules/ -name "*.py")
```

---

## Anti-Pattern Prevention Metrics

Target Waste Prevention: **79 hours**

Breakdown:
- Hallucination debugging: 12h saved
- Incomplete implementation rework: 5h saved
- Silent failure investigation: 4h saved
- Worktree cleanup automation: 10h saved
- Test-code mismatch fixes: 6h saved
- Configuration drift refactoring: 3h saved
- Documentation sync: 3h saved

**Total: 43h minimum saved with manual guards**

---

## Quick Reference

### ✅ Good Patterns
```python
# Subprocess with check
result = subprocess.run(["pytest"], check=True)

# Error handling
try:
    data = Path("file.yaml").read_text()
except FileNotFoundError:
    logger.error("File not found")
    sys.exit(1)

# Complete implementation
def migrate_module(module_id: str) -> bool:
    """Migrate module with full error handling."""
    # Actual implementation here
    return True
```

### ❌ Bad Patterns
```python
# Silent failure
subprocess.run(["pytest"])  # ❌ No check=True

# Incomplete
def migrate_module(module_id: str):
    # TODO: implement this  # ❌ TODO in committed code
    pass

# No error handling
data = Path("file.yaml").read_text()  # ❌ Can crash
```

---

## Status Tracking

### Week 1
- [x] Tier 1 guards documented
- [x] Validation script created
- [ ] All scripts follow guards

### Week 2-3
- [ ] Worktree cleanup automated
- [ ] Test coverage checks added
- [ ] Configuration drift prevented

### Week 4
- [ ] All guards passing
- [ ] Zero anti-pattern violations
- [ ] Metrics documented

---

**Last Updated**: 2025-11-25  
**Status**: Active monitoring
