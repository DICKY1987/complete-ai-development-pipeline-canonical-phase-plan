# ID Framework Analysis & Roadmap
**Generated**: 2025-11-29  
**Status**: Strategic Analysis  
**Purpose**: Map current doc_id system to AI recommendations and define next steps

---

## Executive Summary

Your repository has a **strong foundation** for the ID framework system. You've built **80% of the recommended infrastructure**, but you're missing the **critical enforcement layer** that makes IDs a "seatbelt" instead of a "nice-to-have."

### Current State ✅
- ✅ **124 documents registered** with unique `doc_id` values
- ✅ **Well-defined format** (`DOC-<CATEGORY>-<NAME>-<NNN>`)
- ✅ **Central registry** (`DOC_ID_REGISTRY.yaml`)
- ✅ **Category-based indexes** (12 categories)
- ✅ **CLI tooling** (`doc_id_registry_cli.py`)
- ✅ **Documented framework** (`DOC_ID_FRAMEWORK.md`)

### Missing Critical Components ⚠️
- ❌ **No coverage enforcement** (no preflight gate)
- ❌ **No auto-assignment tool** (manual registration only)
- ❌ **No scanner** (can't find missing IDs)
- ❌ **No CI validation** (IDs optional, not required)
- ❌ **Limited embedding** (only 124 of ~500+ eligible files)

### Bottom Line
You can **drive without seatbelts** right now, but when the module refactor crashes (path changes, merge conflicts), you'll wish everything had an ID.

---

## Gap Analysis: What AI Recommends vs What You Have

| Recommendation | Current Status | Gap | Priority |
|----------------|----------------|-----|----------|
| **1. Decide where IDs live** | ✅ Defined in framework | None | ✅ Done |
| **2. Build ID scanner + auto-assigner** | ❌ Manual only | Need automation | 🔴 Critical |
| **3. Enforce ID coverage as preflight gate** | ❌ No enforcement | Need validation | 🔴 Critical |
| **4. Handle no-ID files** | ⚠️ Undefined policy | Need decision | 🟡 Important |
| **5. Make IDs primary join key** | ⚠️ Partial adoption | Need tooling updates | 🟡 Important |
| **6. Quarantine/Legacy module** | ❌ Not defined | Nice-to-have | 🟢 Optional |

---

## Detailed Analysis

### 1. ID Placement Rules ✅ COMPLETE

**Status**: You've defined this clearly in `DOC_ID_FRAMEWORK.md`

| File Type | Placement | Example | Status |
|-----------|-----------|---------|--------|
| **Markdown** | YAML frontmatter | `doc_id: DOC-GUIDE-QUICK-START-001` | ✅ Defined |
| **Python** | Module docstring | `DOC_ID: DOC-CORE-ORCHESTRATOR-001` | ✅ Defined |
| **YAML** | Top-level field | `doc_id: DOC-CONFIG-QUALITY-GATE-001` | ✅ Defined |
| **JSON** | Top-level field | `"doc_id": "DOC-SPEC-WORKSTREAM-SCHEMA-001"` | ✅ Defined |
| **PowerShell** | Header comment | `# DOC_LINK: DOC-SCRIPT-VALIDATE-001` | ✅ Defined |
| **Sidecar (binary)** | `.id.yaml` file | `orchestrator.py.id.yaml` | ✅ Defined |

**Gap**: None. Your framework is clear and comprehensive.

---

### 2. Doc ID Scanner + Auto-Assigner ❌ MISSING

**What AI Recommends:**
> A "Doc ID lint + fixer" that runs before any serious refactor.

**What You Have:**
- ✅ `doc_id_registry_cli.py` can **mint** new IDs
- ❌ No scanner to **find files missing IDs**
- ❌ No auto-assigner to **inject IDs into files**

**What's Missing:**

#### A. Doc ID Scanner
```python
# Pattern: PAT-DOC-ID-SCAN-001
# Purpose: Find all eligible files and extract existing doc_ids

def scan_repository() -> List[DocIDEntry]:
    """
    Scan all eligible files for doc_id presence.
    
    Returns:
        [
            {
                "path": "core/engine/orchestrator.py",
                "doc_id": "DOC-CORE-ORCHESTRATOR-001",  # or None
                "status": "registered" | "missing" | "invalid",
                "file_type": "python",
                "last_modified": "2025-11-22"
            },
            ...
        ]
    """
```

**Algorithm:**
1. Glob all eligible files (`**/*.py`, `**/*.md`, `**/*.yaml`, etc.)
2. Exclude: `.venv/`, `__pycache__/`, `.git/`, `node_modules/`, `legacy/`
3. For each file:
   - Try to extract `doc_id` based on file type
   - If found: validate format, check registry
   - If not found: mark as `missing`
4. Generate `docs_inventory.jsonl` with all findings
5. Report coverage: `X% of eligible files have doc_ids`

#### B. Doc ID Auto-Assigner
```python
# Pattern: PAT-DOC-ID-AUTOASSIGN-002
# Purpose: Auto-assign doc_ids to files missing them

def auto_assign_missing_ids(dry_run: bool = True) -> AssignmentReport:
    """
    Auto-assign doc_ids to all eligible files without them.
    
    Process:
        1. Scan for missing IDs (use PAT-DOC-ID-SCAN-001)
        2. For each missing:
            - Infer category from path (core/* → CORE, error/* → ERROR)
            - Infer name from filename/module
            - Mint new doc_id
            - Inject into file (based on file type)
            - Update registry
        3. Commit changes
    
    Args:
        dry_run: If True, report what would be done but don't modify files
    
    Returns:
        {
            "total_scanned": 247,
            "already_have_id": 124,
            "assigned_new": 123,
            "failed": 0,
            "coverage_before": "50%",
            "coverage_after": "100%"
        }
    """
```

**Injection Logic (by file type):**

**Python:**
```python
# Before:
"""
Module Name

Purpose: Does stuff
"""

# After:
"""
Module Name

DOC_ID: DOC-CORE-SCHEDULER-003
MODULE: core.engine.scheduler
PURPOSE: Does stuff
"""
```

**Markdown:**
```markdown
# Before:
# Quick Start Guide

# After:
---
doc_id: DOC-GUIDE-QUICK-START-007
title: Quick Start Guide
---

# Quick Start Guide
```

**YAML:**
```yaml
# Before:
version: "1.0.0"
config: ...

# After:
doc_id: DOC-CONFIG-ORCHESTRATOR-005
version: "1.0.0"
config: ...
```

**PowerShell:**
```powershell
# Before:
param(...)

# After:
# DOC_LINK: DOC-SCRIPT-VALIDATE-WS-023
param(...)
```

---

### 3. Preflight Enforcement Gate ❌ MISSING

**What AI Recommends:**
> **REFRACTOR_GATE_001**: Module refactor MAY NOT start unless 100% of eligible files have valid `doc_id`s.

**What You Have:**
- ❌ No preflight validation
- ❌ IDs are optional, not required
- ❌ No CI check

**What's Needed:**

#### A. Preflight Validator
```python
# Pattern: PAT-DOC-ID-PREFLIGHT-003
# Purpose: Enforce 100% doc_id coverage before refactor

def validate_id_coverage(threshold: float = 1.0) -> ValidationResult:
    """
    Validate that sufficient files have doc_ids.
    
    Args:
        threshold: Required coverage (0.0 to 1.0). Default 1.0 = 100%
    
    Returns:
        {
            "passed": False,
            "coverage": 0.502,
            "threshold": 1.0,
            "total_eligible": 247,
            "with_id": 124,
            "without_id": 123,
            "offenders": [
                "core/planning/dag_builder.py",
                "error/plugins/typescript_eslint/plugin.py",
                ...
            ]
        }
    
    Exit Code:
        0 if coverage >= threshold
        1 if coverage < threshold
    """
```

**Usage in workflow:**
```bash
# Before ANY major refactor:
python scripts/doc_id_validator.py preflight --threshold 1.0

# Exit 0 → proceed with refactor
# Exit 1 → block, require ID assignment first
```

#### B. CI Integration
```yaml
# .github/workflows/doc_id_validation.yml
name: Doc ID Validation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check doc_id coverage
        run: |
          python scripts/doc_id_validator.py preflight --threshold 0.95
          # Require 95% coverage for PRs
          
      - name: Validate doc_id format
        run: |
          python scripts/doc_id_validator.py format
          # Check all existing IDs are valid
          
      - name: Check registry consistency
        run: |
          python scripts/doc_id_validator.py consistency
          # Ensure registry matches files
```

**Gate Rules (policy decision needed):**

| Scenario | Threshold | When to Use |
|----------|-----------|-------------|
| **Strict mode** | 100% | Before module refactor |
| **Moderate mode** | 95% | Normal PR review |
| **Permissive mode** | 80% | Early development |
| **Disabled** | 0% | Emergency hotfixes |

---

### 4. No-ID File Handling ⚠️ UNDEFINED

**What AI Recommends:**
Three policy options:

#### Option A: Strict Mode (Recommended for Module Refactor)
**Policy:**
> Refuse to run refactor patterns if ANY eligible file is missing an ID.

**Implementation:**
```python
# In refactor preflight:
def check_id_coverage():
    scan = scan_repository()
    missing = [f for f in scan if f['doc_id'] is None]
    
    if missing:
        print(f"[ERROR] {len(missing)} files missing doc_ids")
        print("Run: python scripts/doc_id_assigner.py auto-assign")
        sys.exit(1)
    
    print("[OK] 100% doc_id coverage")
```

**Pros:**
- Cleanest model
- Refactor patterns can assume `doc_id` exists everywhere
- Best for long-term automation

**Cons:**
- Requires upfront work (but you need this anyway)

---

#### Option B: Auto-Assign On-the-Fly
**Policy:**
> Allow refactor patterns to assign IDs on first encounter.

**Implementation:**
```python
# In refactor pattern:
def get_or_assign_doc_id(file_path: str) -> str:
    doc_id = extract_doc_id(file_path)
    
    if not doc_id:
        # Auto-assign now
        doc_id = mint_and_inject_doc_id(file_path)
        log(f"Auto-assigned {doc_id} to {file_path}")
    
    return doc_id
```

**Pros:**
- Less blocking
- Can start refactor without full coverage

**Cons:**
- Less deterministic
- ID assignment scattered across runs
- Harder to audit

---

#### Option C: Quarantine/Legacy Module
**Policy:**
> Files that can't be assigned IDs go to `mod.legacy.unclassified`

**Implementation:**
```yaml
# DOC_ID_REGISTRY.yaml
categories:
  legacy:
    prefix: LEGACY
    description: Files that couldn't be auto-classified
    count: 7
    
docs:
  - doc_id: DOC-LEGACY-UNCLASSIFIED-001
    category: legacy
    path: modules/legacy/unclassified/broken_file.py
    reason: "Failed to parse docstring"
    original_path: core/broken_file.py
```

**Pros:**
- **Never lose anything**
- All "weird" stuff corralled
- Can clean up later

**Cons:**
- Still need IDs (just deferred classification)

---

### 5. IDs as Primary Join Key ⚠️ PARTIAL

**What AI Recommends:**
> Tools MUST use `doc_id` for linking artifacts, not paths.

**Current Status:**
- ✅ Registry uses `doc_id` as key
- ⚠️ Some tools still use paths (grep, glob, etc.)
- ❌ No doc_id-based query API

**Example Gap:**

**Current (path-based):**
```python
# Find test for core/engine/orchestrator.py
test_path = "tests/engine/test_orchestrator.py"  # Brittle!
```

**Desired (doc_id-based):**
```python
# Find test for DOC-CORE-ORCHESTRATOR-001
test_doc = registry.find_related(
    doc_id="DOC-CORE-ORCHESTRATOR-001",
    artifact_type="test"
)
# Returns: DOC-TEST-ORCHESTRATOR-001
# Which points to: tests/engine/test_orchestrator.py
```

**Needed Tool:**
```python
# scripts/doc_id_query.py

class DocIDQuery:
    def find_by_id(self, doc_id: str) -> DocEntry:
        """Get full doc entry by ID."""
    
    def find_by_path(self, path: str) -> DocEntry:
        """Get doc entry by file path."""
    
    def find_related(self, doc_id: str, artifact_type: str) -> List[DocEntry]:
        """Find related artifacts (test, source, docs, etc.)."""
    
    def find_by_category(self, category: str) -> List[DocEntry]:
        """Get all docs in a category."""
    
    def find_by_module(self, module_id: str) -> List[DocEntry]:
        """Get all docs for a module (future: when module_id exists)."""
```

---

## Recommended Roadmap

### Phase 0: Doc ID Assignment (CRITICAL - DO FIRST)
**Goal**: Get 100% coverage before module refactor  
**Time**: 2-4 hours  
**Priority**: 🔴 Critical

**Steps:**
1. ✅ **Create scanner** (`PAT-DOC-ID-SCAN-001`)
   - Scan all eligible files
   - Generate `docs_inventory.jsonl`
   - Report coverage

2. ✅ **Create auto-assigner** (`PAT-DOC-ID-AUTOASSIGN-002`)
   - Infer category from path
   - Infer name from filename
   - Mint + inject doc_ids
   - Update registry

3. ✅ **Run auto-assignment**
   ```bash
   # Dry run first
   python scripts/doc_id_assigner.py scan
   python scripts/doc_id_assigner.py auto-assign --dry-run
   
   # Then real
   python scripts/doc_id_assigner.py auto-assign
   
   # Verify
   python scripts/doc_id_validator.py preflight --threshold 1.0
   ```

4. ✅ **Commit**
   ```bash
   git add .
   git commit -m "chore: assign doc_ids to all eligible files (Phase 0)"
   ```

**Deliverables:**
- `scripts/doc_id_scanner.py`
- `scripts/doc_id_assigner.py`
- `docs_inventory.jsonl`
- Updated `DOC_ID_REGISTRY.yaml`
- 100% coverage

---

### Phase 1: Enforcement & Validation (CRITICAL)
**Goal**: Make IDs required, not optional  
**Time**: 1-2 hours  
**Priority**: 🔴 Critical

**Steps:**
1. ✅ **Create preflight validator** (`PAT-DOC-ID-PREFLIGHT-003`)
   ```python
   python scripts/doc_id_validator.py preflight --threshold 1.0
   ```

2. ✅ **Add CI validation**
   - Create `.github/workflows/doc_id_validation.yml`
   - Run on all PRs
   - Block merges if coverage drops

3. ✅ **Add pre-commit hook**
   ```bash
   # .git/hooks/pre-commit
   python scripts/doc_id_validator.py format
   python scripts/doc_id_validator.py consistency
   ```

4. ✅ **Document enforcement policy**
   - When IDs required (before refactor)
   - When optional (early dev)
   - How to handle violations

**Deliverables:**
- `scripts/doc_id_validator.py`
- `.github/workflows/doc_id_validation.yml`
- Updated `DOC_ID_FRAMEWORK.md` with enforcement rules

---

### Phase 2: Tooling Enhancement (IMPORTANT)
**Goal**: Make IDs easy to use in automation  
**Time**: 2-3 hours  
**Priority**: 🟡 Important

**Steps:**
1. ✅ **Create query API** (`scripts/doc_id_query.py`)
   - Find by ID, path, category
   - Find related artifacts
   - Query language

2. ✅ **Update existing tools**
   - Refactor tools to use doc_ids
   - Keep path-based as fallback
   - Add doc_id params to scripts

3. ✅ **Create doc_id utilities**
   ```python
   # scripts/doc_id_utils.py
   
   def extract_doc_id(file_path: str) -> Optional[str]:
       """Extract doc_id from any file type."""
   
   def inject_doc_id(file_path: str, doc_id: str) -> bool:
       """Inject doc_id into file based on type."""
   
   def validate_doc_id(doc_id: str) -> ValidationResult:
       """Check format, uniqueness, registry consistency."""
   ```

**Deliverables:**
- `scripts/doc_id_query.py`
- `scripts/doc_id_utils.py`
- Updated existing scripts

---

### Phase 3: Module Integration (IMPORTANT)
**Goal**: Link doc_ids to module_ids for refactor  
**Time**: 1-2 hours  
**Priority**: 🟡 Important

**Steps:**
1. ✅ **Extend registry schema**
   ```yaml
   docs:
     - doc_id: DOC-CORE-ORCHESTRATOR-001
       module_id: mod.core.engine  # NEW FIELD
       category: core
       ...
   ```

2. ✅ **Add module_id inference**
   ```python
   def infer_module_id(file_path: str) -> str:
       """Infer module_id from path."""
       # core/engine/orchestrator.py → mod.core.engine
       # error/plugins/ruff/plugin.py → mod.error.plugins.ruff
   ```

3. ✅ **Create module → doc mapping**
   ```yaml
   # modules/MODULE_DOC_MAP.yaml
   modules:
     mod.core.engine:
       docs:
         - DOC-CORE-ORCHESTRATOR-001
         - DOC-CORE-SCHEDULER-002
         - DOC-CORE-EXECUTOR-003
       tests:
         - DOC-TEST-ORCHESTRATOR-001
         - DOC-TEST-SCHEDULER-002
   ```

**Deliverables:**
- Extended registry schema
- `modules/MODULE_DOC_MAP.yaml`
- Module ID inference logic

---

### Phase 4: Quarantine Module (OPTIONAL)
**Goal**: Safety net for edge cases  
**Time**: 30 minutes  
**Priority**: 🟢 Optional

**Steps:**
1. ✅ **Define legacy module**
   ```yaml
   categories:
     legacy:
       prefix: LEGACY
       description: Files that couldn't be auto-classified
   ```

2. ✅ **Create quarantine handler**
   ```python
   def quarantine_file(file_path: str, reason: str) -> str:
       """Move file to legacy/unclassified and assign doc_id."""
       doc_id = mint_doc_id("legacy", "unclassified")
       move_file(file_path, "modules/legacy/unclassified/")
       log_quarantine(doc_id, file_path, reason)
       return doc_id
   ```

3. ✅ **Add to auto-assigner**
   - If file can't be parsed → quarantine
   - If category ambiguous → quarantine
   - Log for manual review

**Deliverables:**
- `modules/legacy/unclassified/` directory
- Quarantine handler
- `LEGACY_QUARANTINE_REPORT.md`

---

## Execution Templates

### Template: EXEC-DOC-ID-PHASE0
**Pattern**: Scan + Auto-Assign All Files

```bash
# Step 1: Scan current state
python scripts/doc_id_scanner.py scan --output docs_inventory.jsonl

# Step 2: Review findings
python scripts/doc_id_scanner.py stats
# Output: 247 eligible files, 124 with IDs (50% coverage)

# Step 3: Dry run auto-assign
python scripts/doc_id_assigner.py auto-assign --dry-run

# Step 4: Review proposed changes
cat docs_inventory_changes.jsonl

# Step 5: Execute auto-assign
python scripts/doc_id_assigner.py auto-assign

# Step 6: Validate
python scripts/doc_id_validator.py preflight --threshold 1.0
# Output: PASS - 100% coverage (247/247)

# Step 7: Commit
git add .
git commit -m "chore: assign doc_ids to all eligible files (Phase 0 - coverage 50% → 100%)"
```

---

### Template: EXEC-DOC-ID-PHASE1
**Pattern**: Enforce IDs in CI/CD

```bash
# Step 1: Create validator
cat > scripts/doc_id_validator.py << 'EOF'
#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-DOC-ID-VALIDATOR-046

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['preflight', 'format', 'consistency'])
    parser.add_argument('--threshold', type=float, default=1.0)
    
    args = parser.parse_args()
    
    if args.command == 'preflight':
        result = validate_coverage(args.threshold)
        if not result['passed']:
            print(f"[FAIL] Coverage {result['coverage']:.1%} < {args.threshold:.1%}")
            sys.exit(1)
    # ...
EOF

# Step 2: Create CI workflow
cat > .github/workflows/doc_id_validation.yml << 'EOF'
name: Doc ID Validation
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check coverage
        run: python scripts/doc_id_validator.py preflight --threshold 0.95
EOF

# Step 3: Test locally
python scripts/doc_id_validator.py preflight --threshold 1.0

# Step 4: Commit
git add scripts/doc_id_validator.py .github/workflows/doc_id_validation.yml
git commit -m "feat: enforce doc_id coverage in CI (95% threshold)"
```

---

## Decision Points

### A. Coverage Threshold (DECIDE NOW)

| Option | Threshold | Use Case | Recommendation |
|--------|-----------|----------|----------------|
| **Strict** | 100% | Module refactor, major changes | ✅ Use for refactor |
| **Moderate** | 95% | Normal development | ✅ Use for CI |
| **Permissive** | 80% | Early prototyping | ❌ Too loose |
| **Disabled** | 0% | Emergency only | ❌ Avoid |

**Recommended Policy:**
```yaml
# quality_gates/doc_id_policy.yaml

gates:
  module_refactor:
    threshold: 1.0  # 100% required
    enforcement: strict
    
  pull_request:
    threshold: 0.95  # 95% required
    enforcement: moderate
    
  development:
    threshold: 0.80  # 80% recommended
    enforcement: warning
```

---

### B. Auto-Assignment Strategy (DECIDE NOW)

| Option | When | Pros | Cons | Recommendation |
|--------|------|------|------|----------------|
| **Phase 0** | Before refactor | Clean, deterministic | Upfront work | ✅ Best |
| **On-the-fly** | During refactor | Less blocking | Scattered, messy | ❌ Avoid |
| **Hybrid** | Phase 0 for core, on-fly for new | Flexible | Complex | ⚠️ Consider |

**Recommended**: Phase 0 (upfront)

---

### C. No-ID File Policy (DECIDE NOW)

| Scenario | Policy | Example |
|----------|--------|---------|
| **Can infer category** | Auto-assign | `core/engine/scheduler.py` → `DOC-CORE-SCHEDULER-003` |
| **Ambiguous category** | Quarantine → manual review | `utils/helpers.py` → `DOC-LEGACY-HELPERS-001` |
| **Can't parse** | Quarantine → manual review | `broken.py` → `DOC-LEGACY-BROKEN-001` |
| **Binary/generated** | Sidecar `.id.yaml` | `diagram.drawio` → `diagram.drawio.id.yaml` |

**Recommended**: Auto-assign where possible, quarantine edge cases

---

## Success Metrics

### Phase 0 Success Criteria
- ✅ 100% of eligible files have `doc_id`
- ✅ All doc_ids valid format
- ✅ Registry consistent with files
- ✅ `docs_inventory.jsonl` generated
- ✅ Committed to git

### Phase 1 Success Criteria
- ✅ CI validates doc_ids on all PRs
- ✅ Coverage threshold enforced
- ✅ Pre-commit hook validates format
- ✅ Policy documented

### Phase 2 Success Criteria
- ✅ Query API available
- ✅ Existing tools use doc_ids
- ✅ Utilities tested
- ✅ Documentation updated

### Phase 3 Success Criteria
- ✅ module_id linked to doc_id
- ✅ Module → doc mapping exists
- ✅ Module refactor uses doc_ids

---

## Risk Analysis

### Risk 1: Incomplete Coverage During Refactor
**Probability**: High (if Phase 0 skipped)  
**Impact**: High (path changes break links)  
**Mitigation**: **Do Phase 0 first**

### Risk 2: Category Inference Fails
**Probability**: Medium (edge cases)  
**Impact**: Low (quarantine handles it)  
**Mitigation**: Use quarantine module + manual review

### Risk 3: CI Slows Down Development
**Probability**: Low (validation is fast)  
**Impact**: Medium (dev friction)  
**Mitigation**: Use 95% threshold for PRs, 100% for refactor

### Risk 4: Tooling Bugs in Auto-Assigner
**Probability**: Medium (new code)  
**Impact**: High (corrupts files)  
**Mitigation**: **Always dry-run first**, test on copy

---

## Quick Start (Next 2 Hours)

### Hour 1: Create Scanner + Auto-Assigner
```bash
# 1. Create scanner (20 min)
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# 2. Create auto-assigner (30 min)
python scripts/doc_id_assigner.py auto-assign --dry-run

# 3. Test on subset (10 min)
python scripts/doc_id_assigner.py auto-assign --limit 10
git diff  # Review changes
git reset --hard  # Revert test
```

### Hour 2: Full Auto-Assignment
```bash
# 1. Run full auto-assign (10 min)
python scripts/doc_id_assigner.py auto-assign

# 2. Validate (5 min)
python scripts/doc_id_validator.py preflight --threshold 1.0

# 3. Review changes (15 min)
git diff --stat
git diff docs_inventory.jsonl
git diff DOC_ID_REGISTRY.yaml

# 4. Commit (5 min)
git add .
git commit -m "chore: assign doc_ids to all files (Phase 0 - 50% → 100%)"
```

---

## Conclusion

### What You Have ✅
- Strong foundation (80% complete)
- Clear framework and tooling
- 124 docs already registered

### What You Need 🔴
- **Auto-assignment** (critical for scale)
- **Enforcement gates** (critical for safety)
- **CI validation** (critical for maintenance)

### Time Investment 🕐
- **Phase 0**: 2-4 hours (scan + auto-assign)
- **Phase 1**: 1-2 hours (enforcement)
- **Phase 2**: 2-3 hours (tooling)
- **Total**: ~6-9 hours

### ROI 📈
- **Without IDs**: Module refactor = 20-40 hours of path debugging
- **With IDs**: Module refactor = 5-10 hours (clean automation)
- **Savings**: 15-30 hours (2x-4x speedup)
- **ROI Ratio**: ~3:1 to 5:1

### Recommendation 🎯
**Do Phase 0 (auto-assignment) before module refactor starts.**  
It's your "seatbelt" – you *can* refactor without it, but you'll regret it the moment something goes wrong.

---

**Next Steps:**
1. Read this analysis
2. Decide on policies (thresholds, auto-assign strategy)
3. Implement Phase 0 (scanner + auto-assigner)
4. Run full auto-assignment
5. Add CI enforcement
6. Begin module refactor with confidence

---

**Questions to Answer:**
- [ ] Coverage threshold for module refactor? (Recommend: 100%)
- [ ] Coverage threshold for CI? (Recommend: 95%)
- [ ] Auto-assignment strategy? (Recommend: Phase 0)
- [ ] Quarantine module needed? (Recommend: Yes, safety net)
- [ ] When to start Phase 0? (Recommend: Now, before refactor)
