# Phase G: Parallel Development Strategy

**Created**: 2025-11-21  
**Purpose**: Identify opportunities to parallelize Phase G workstreams using background tasks/workers  
**Target**: Reduce 48-62 hour sequential timeline to 24-36 hours with parallel execution  

---

## Executive Summary

**Yes, background tasks can dramatically speed up Phase G development.**

By analyzing task dependencies, **we can parallelize 3-4 concurrent workstreams** and reduce total timeline by **40-50%**.

### Key Finding
- **Sequential execution**: 48-62 hours (10-12 weeks part-time)
- **Parallel execution**: 24-36 hours (5-7 weeks part-time)
- **Optimal workers**: 3-4 concurrent developers/agents
- **Critical path**: WS-G1 → WS-G2 (24-34 hours)

---

## Dependency Analysis

### True Dependencies (Sequential Required)

```
WS-G1 (Config Foundation)  [BLOCKS EVERYTHING]
  ↓
WS-G2 (Invoke Python)      [BLOCKS WS-G3, WS-G4]
  ↓
WS-G3 (Invoke-Build)       [BLOCKS WS-G4, WS-G5]
  ↓
WS-G4 (Helper Tasks)       [OPTIONAL, BLOCKS WS-G5]
  ↓
WS-G5 (Gallery Publishing) [FINAL STEP]
```

### False Dependencies (Can Be Parallelized)

**WS-G2 and WS-G3 are INDEPENDENT after WS-G1 completes:**
- WS-G2 modifies **Python code** (core/engine/tools.py, error/plugins/*)
- WS-G3 modifies **PowerShell scripts** (scripts/*.ps1, build.ps1)
- **No file overlap** → can run simultaneously

**WS-G4 can start partially during WS-G3:**
- Requires Invoke-Build installed (Part 1 of WS-G3)
- Can proceed with helper integration while WS-G3 finishes

---

## Parallelization Strategy

### Phase 1: Foundation (Sequential) - **8-10 hours**
**1 Worker** completes WS-G1:
- Create invoke.yaml
- Migrate config files
- Update config consumers
- **Checkpoint**: Config system operational

### Phase 2: Dual Track (Parallel) - **16-24 hours**
**Worker A** tackles WS-G2 (Invoke Python):
- Part 1: Create invoke_utils.py + tasks.py (4-6 hrs)
- Part 2: Refactor tool adapters (8-12 hrs)
- Part 3: Update tests with MockContext (4-6 hrs)
- Part 4: Documentation (2-3 hrs)

**Worker B** tackles WS-G3 (Invoke-Build):
- Part 1: Install Invoke-Build + build.ps1 (1 hr)
- Part 2: Incremental build support (3-4 hrs)
- Part 3: Parallel execution tasks (2-3 hrs)
- Part 4: Migrate existing scripts (2-3 hrs)
- Part 5: Documentation (1 hr)

**Worker C** prepares WS-G4/WS-G5:
- Research InvokeBuildHelper usage (2 hrs)
- Draft module manifests for PSGallery (3-4 hrs)
- Prepare documentation templates (2 hrs)
- Create example code (3 hrs)

### Phase 3: Finalization (Parallel) - **8-12 hours**
**Worker A** completes WS-G2 testing and integration

**Worker B** starts WS-G4 (Helper Tasks):
- Requires WS-G3 Part 1 complete (Invoke-Build installed)
- Can proceed immediately (4-6 hrs)

**Worker C** starts WS-G5 (Gallery Publishing):
- Requires WS-G3 complete (build.ps1 exists)
- Module manifests + build pipeline (12-16 hrs)

### Phase 4: Integration & Testing (Parallel) - **4-6 hours**
**All Workers** collaborate:
- Cross-workstream integration testing
- CI pipeline validation
- Documentation finalization
- Performance benchmarking

---

## Optimal Worker Allocation

### Scenario A: 3 Workers (Recommended)

**Total Timeline: 26-38 hours (wall-clock time)**

| Phase | Worker A (Python Expert) | Worker B (PowerShell Expert) | Worker C (DevOps/Docs) |
|-------|-------------------------|------------------------------|------------------------|
| **1** | WS-G1 Config (8-10h) | *Idle* | *Idle* |
| **2** | WS-G2 Invoke Python (16-24h) | WS-G3 Invoke-Build (8-12h) | WS-G4 Prep + WS-G5 Prep (8-10h) |
| **3** | WS-G2 Testing (4h) | WS-G4 Helper Tasks (4-6h) | WS-G5 Gallery Publishing (12-16h) |
| **4** | Integration Testing (4h) | Integration Testing (4h) | Integration Testing (4h) |

**Critical Path**: WS-G1 (10h) → WS-G2 (24h) = **34 hours**  
**Parallelism Gain**: 48-62h sequential → 34h critical path = **40% faster**

### Scenario B: 4 Workers (Maximum Parallelism)

**Total Timeline: 24-36 hours (wall-clock time)**

| Phase | Worker A | Worker B | Worker C | Worker D |
|-------|----------|----------|----------|----------|
| **1** | WS-G1 Config (8-10h) | *Idle* | *Idle* | *Idle* |
| **2** | WS-G2 Python Utils (4-6h) | WS-G3 Invoke-Build (8-12h) | WS-G4 Prep (4h) | WS-G5 Prep (4h) |
| **2.5** | WS-G2 Tool Adapters (8-12h) | WS-G3 Incremental (3-4h) | WS-G4 Research (2h) | WS-G5 Manifests (4-5h) |
| **3** | WS-G2 Test Updates (4-6h) | WS-G4 Helper Tasks (4-6h) | WS-G5 Build Pipeline (4-5h) | Documentation (6-8h) |
| **4** | Integration (3h) | Integration (3h) | Integration (3h) | Integration (3h) |

**Critical Path**: WS-G1 (10h) → WS-G2 (18h) → Integration (3h) = **31 hours**  
**Parallelism Gain**: 48-62h sequential → 31h critical path = **48% faster**

### Scenario C: 2 Workers (Minimal)

**Total Timeline: 36-48 hours (wall-clock time)**

| Phase | Worker A (Full-Stack) | Worker B (Full-Stack) |
|-------|----------------------|----------------------|
| **1** | WS-G1 Config (8-10h) | *Idle* |
| **2** | WS-G2 Invoke Python (16-24h) | WS-G3 + WS-G4 (12-18h) |
| **3** | WS-G2 Completion (4h) | WS-G5 Gallery (12-16h) |
| **4** | Integration (4h) | Integration (4h) |

**Critical Path**: WS-G1 (10h) → WS-G2 (24h) → Integration (4h) = **38 hours**  
**Parallelism Gain**: 48-62h sequential → 38h critical path = **27% faster**

---

## Task-Level Parallelization Within Workstreams

### WS-G2: Invoke Python (Most Benefit)

**Can be split into 3 parallel sub-tasks after Part 1 complete:**

```
Part 1: Core Utils (Sequential - 4-6h)
  ↓
├─ Worker A: Error Plugins Batch 1 (plugins 1-5) [3-4h]
├─ Worker B: Error Plugins Batch 2 (plugins 6-10) [3-4h]
└─ Worker C: Error Plugins Batch 3 (plugins 11-15) + Engine Adapters [4-5h]
  ↓
Part 3: Test Updates (Sequential - 4-6h)
```

**Savings**: 15 plugins + 4 adapters = 19 files  
- Sequential: 10-14 hours  
- Parallel (3 workers): 4-5 hours  
- **Gain: 6-9 hours**

### WS-G5: Gallery Publishing

**Can be split into 3 parallel modules:**

```
Part 1: Module Creation (Parallel)
├─ Worker A: AIPipeline.Core manifest + functions [4-5h]
├─ Worker B: AIPipeline.CCPM manifest + functions [4-5h]
└─ Worker C: AIPipeline.ErrorEngine manifest + functions [4-5h]
  ↓
Part 2: Build Pipeline (Sequential - 2h)
  ↓
Part 3: Documentation (Parallel)
├─ Worker A: AIPipeline.Core docs [1-2h]
├─ Worker B: AIPipeline.CCPM docs [1-2h]
└─ Worker C: AIPipeline.ErrorEngine docs [1-2h]
```

**Savings**: 12-16h sequential → 7-9h parallel = **5-7 hours**

---

## Background Task Opportunities

### Automated Background Tasks (AI Agents/CI)

**Type 1: File Transformations (High Confidence)**
Can run **unattended** with validation:

1. **Batch Plugin Refactoring** (WS-G2 Part 2)
   - Pattern: Replace `subprocess.run()` → `run_command()`
   - Files: 15 error plugins
   - Automation: Search/replace with AST validation
   - **Time saved**: 6-8 hours → 1 hour review

2. **Test Mock Updates** (WS-G2 Part 3)
   - Pattern: Replace `unittest.mock` → `MockContext`
   - Files: 15+ test files
   - Automation: Template-based refactor
   - **Time saved**: 4-6 hours → 1 hour review

3. **Script Wrapper Generation** (WS-G3 Part 4)
   - Pattern: Create thin wrappers calling `Invoke-Build`
   - Files: 10 PowerShell scripts
   - Automation: Template expansion
   - **Time saved**: 2-3 hours → 30 min review

**Type 2: Documentation Tasks (Medium Confidence)**
Can run **in background** with human review:

1. **Generate Configuration Docs** (WS-G1 Part 1)
   - Extract config schema → markdown tables
   - **Time saved**: 1-2 hours

2. **Generate API Docs** (WS-G2 Part 4)
   - Docstrings → structured markdown
   - **Time saved**: 1-2 hours

3. **Module README Generation** (WS-G5 Part 3)
   - Templates + metadata → README files
   - **Time saved**: 2-3 hours

**Type 3: Validation/Testing Tasks (Run Continuously)**
Can run **in parallel** with development:

1. **Continuous Test Execution**
   - Run pytest on every file save
   - Immediate feedback on breakage
   - **Time saved**: 4-6 hours debugging

2. **Config Validation**
   - Validate invoke.yaml changes on every commit
   - Catch syntax errors immediately
   - **Time saved**: 2-3 hours debugging

3. **Import Checker**
   - Scan for deprecated patterns continuously
   - Flag violations in real-time
   - **Time saved**: 2-3 hours debugging

---

## Maximum Parallelization Scenario

### Using 4 Human Workers + 5 Background Agents

**Phase 1: Foundation (8-10 hours)**
- **Worker A**: WS-G1 Config (hands-on)
- **Agent 1**: Generate config documentation (background)
- **Agent 2**: Validate existing config files (background)

**Phase 2: Parallel Execution (12-16 hours)**
- **Worker A**: WS-G2 Core Utils (hands-on)
- **Worker B**: WS-G3 Invoke-Build (hands-on)
- **Worker C**: WS-G5 Module Manifests (hands-on)
- **Worker D**: Documentation framework (hands-on)
- **Agent 1**: Batch plugin refactoring (automated)
- **Agent 2**: Test mock generation (automated)
- **Agent 3**: Script wrapper generation (automated)
- **Agent 4**: Continuous pytest (monitoring)
- **Agent 5**: Import checker (monitoring)

**Phase 3: Integration (8-10 hours)**
- **All Workers**: Review agent output
- **All Workers**: Integration testing
- **Agent 4-5**: Continuous validation

**Total Wall-Clock Time: 20-26 hours**  
**Human Effort: 24-30 hours** (4 workers × 6-8 hours each)  
**Agent Effort: 15-20 hours** (automated, running in background)

**Effective Speedup: 62h → 26h = 58% faster**

---

## Risk Assessment: Parallel Development

### High Risk (Requires Coordination)

❌ **WS-G1 + WS-G2 simultaneously**: Config changes conflict  
❌ **WS-G2 + WS-G3 modifying same CI files**: Merge conflicts  
❌ **Multiple workers editing tests/conftest.py**: Lock contention

### Medium Risk (Manageable)

⚠️ **Plugin refactoring conflicts**: If 3 workers edit different plugins → merge needed  
**Mitigation**: Assign specific file ranges (plugins 1-5, 6-10, 11-15)

⚠️ **Documentation conflicts**: Multiple READMEs being updated  
**Mitigation**: Use separate feature branches per workstream

### Low Risk (Safe to Parallelize)

✅ **WS-G2 (Python) + WS-G3 (PowerShell)**: Different file sets  
✅ **WS-G5 module creation**: 3 independent modules  
✅ **Background agents**: Read-only analysis or isolated file generation

---

## Recommended Approach

### For 1 Developer (Solo)
**Don't parallelize workstreams, but use agents:**
- Execute sequentially: G1 → G2 → G3 → G4 → G5
- Use **3 background agents** for automation:
  - Agent 1: Batch plugin refactoring
  - Agent 2: Test mock generation
  - Agent 3: Continuous testing
- **Timeline**: 36-48 hours → **28-36 hours** (25% faster)

### For 2-3 Developers (Small Team)
**Recommended parallelization:**
- Developer 1: WS-G1 → WS-G2 (critical path)
- Developer 2: WS-G3 (starts after G1) → WS-G4
- Developer 3: WS-G5 prep → WS-G5 completion
- **3-5 background agents** for automation
- **Timeline**: 48-62 hours → **26-34 hours** (40% faster)

### For 4+ Developers (Large Team)
**Maximum parallelization:**
- Developer 1: WS-G1 → WS-G2 core
- Developer 2: WS-G2 plugins (batch 1-5)
- Developer 3: WS-G2 plugins (batch 6-10) + WS-G3
- Developer 4: WS-G2 plugins (batch 11-15) + WS-G4 + WS-G5
- **5-7 background agents** for automation
- **Timeline**: 48-62 hours → **20-26 hours** (58% faster)

---

## Answer to Original Question

### How many background tasks can be used?

**5-7 background agents/tasks optimally**, split by type:

1. **Agent 1**: Batch plugin refactoring (WS-G2)
2. **Agent 2**: Test mock generation (WS-G2)
3. **Agent 3**: Script wrapper generation (WS-G3)
4. **Agent 4**: Continuous pytest runner
5. **Agent 5**: Import deprecation checker
6. **Agent 6** (optional): Documentation generator
7. **Agent 7** (optional): Config validator

### Speed improvement?

- **With 1 developer + 5 agents**: **25-30% faster** (48h → 36h)
- **With 3 developers + 5 agents**: **40-45% faster** (48h → 28h)
- **With 4 developers + 7 agents**: **50-60% faster** (48h → 24h)

### Diminishing returns beyond 4 workers + 7 agents
- Critical path (WS-G1 → WS-G2) cannot be further parallelized
- Coordination overhead increases
- Merge conflicts become more frequent

---

## Implementation: Background Task Assignment

### Using GitHub Copilot CLI / Aider Agents

```bash
# Start Agent 1: Batch plugin refactoring
aider --message "Refactor error/plugins/python_ruff/plugin.py to use run_command()" \
      --yes-always --output-log agent1.log &

# Start Agent 2: Test mock generation  
aider --message "Update tests/test_tools.py to use MockContext fixture" \
      --yes-always --output-log agent2.log &

# Start Agent 3: Script wrappers
aider --message "Create scripts/bootstrap.ps1 wrapper calling Invoke-Build" \
      --yes-always --output-log agent3.log &

# Start Agent 4: Continuous testing
while true; do pytest tests/ -q; sleep 60; done &

# Start Agent 5: Import checker
while true; do python scripts/validate_error_imports.py; sleep 120; done &
```

### Using Workstream Orchestrator

```json
// workstreams/ws-g2-plugin-batch.json
{
  "id": "ws-g2-plugin-batch-1",
  "tasks": [
    "Refactor error/plugins/python_ruff/plugin.py",
    "Refactor error/plugins/python_mypy/plugin.py",
    "Refactor error/plugins/python_pylint/plugin.py",
    "Refactor error/plugins/python_pyright/plugin.py",
    "Refactor error/plugins/python_bandit/plugin.py"
  ],
  "files_scope": ["error/plugins/python_*/plugin.py"],
  "tool": "aider",
  "parallel": true
}
```

```bash
# Launch parallel workstream execution
python scripts/run_workstream.py --ws-id ws-g2-plugin-batch-1 --parallel
```

---

## Conclusion

**Yes, background tasks can dramatically accelerate Phase G:**

✅ **Optimal configuration**: 3-4 human workers + 5-7 background agents  
✅ **Speed improvement**: 40-60% faster than sequential execution  
✅ **Safe parallelization**: WS-G1 → (WS-G2 ∥ WS-G3) → WS-G4/WS-G5  
✅ **Automation targets**: Plugin refactoring, test updates, script generation, continuous validation  

**Critical success factors:**
- Clear file ownership to avoid merge conflicts
- Background agents run automated, low-risk transformations
- Human review gates for agent output before integration
- Continuous testing to catch breakage early
