---
doc_id: DOC-GUIDE-CODEX-867
---

# CODEX.md

This file provides guidance to OpenAI Codex when working with code in this repository through Aider workstream templates.

## 0. MANDATORY: Execution Patterns First

**CRITICAL**: Before beginning ANY task, read and follow:
📋 **`docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`**

### Pattern-First Workflow (ENFORCED)
```
Step 1: Check if N ≥ 3 similar items → Use execution pattern
Step 2: Enable 11 anti-pattern guards → Prevent 85h waste
Step 3: Execute in batches → 3x-10x faster
Step 4: Ground truth verification → Exit code, not "looks good"
```

### The Golden Rule
> **Decide once → Apply N times → Trust ground truth → Move on**

**Anti-Patterns Blocked**:
- ❌ Hallucination of success (declare complete without verification)
- ❌ Planning loops (80k tokens planning, zero execution)
- ❌ Approval loops ("Would you like me to...")
- ❌ Incomplete implementations (TODO/pass placeholders)
- ❌ Framework over-engineering (create infrastructure, never use it)

**Time Savings**: Tasks complete in 3.4h instead of 8.5h (2.5x speedup)
**ROI**: 255:1 (20 min setup saves 85h waste per project)

**Quick Reference**: See `docs/reference/ai-agents/QUICK_REFERENCE_CARD.md` for rapid lookup

---

## Codex-Specific Integration

### Workstream Template Context

When invoked through Aider workstream templates, you'll receive:

**Template Variables**:
- `ws_id`: Workstream identifier
- `repo_path`: Repository root path
- `worktree_path`: Worktree path for this execution
- `files_scope`: Files to edit (stay within scope)
- `files_create`: Files to create (if applicable)
- `tasks`: Numbered task list to complete
- `acceptance_tests`: Tests that must pass
- `classification`: Complexity, quality, domain, operation tags
- `role`: Your role for this workstream
- `openspec_change`: OpenSpec change ID (if applicable)
- `ccpm_issue`: GitHub issue reference (if applicable)
- `gate`: Quality gate requirements

### File Scope Constraints

**CRITICAL**: Stay within the defined file scope.

```markdown
# ✅ CORRECT - Edit only files in files_scope
- Modify files listed in [FILE_SCOPE] section
- Create files listed in create scope (if present)
- Read related files for context

# ❌ WRONG - Edit files outside scope
- Modifying files not in scope
- Creating files not authorized
- Changing unrelated code
```

**Why this matters**:
- Workstreams run in isolated git worktrees
- File scope prevents conflicts with parallel workstreams
- Out-of-scope changes will be rejected by validation

### Execution Pattern Integration

**For workstreams creating N ≥ 3 similar items**:

1. **Identify pattern applicability** (30 seconds):
   - Check if tasks involve creating 3+ similar files/modules/tests
   - Reference `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`

2. **Use appropriate pattern**:
   - EXEC-001: Batch File Creator (N ≥ 3 files)
   - EXEC-002: Module Generator (N ≥ 3 modules)
   - EXEC-003: Test Multiplier (N ≥ 5 tests)
   - EXEC-004: Doc Standardizer (N ≥ 3 docs)
   - EXEC-005: Config Multiplexer (N ≥ 3 configs)
   - EXEC-006: Endpoint Factory (N ≥ 3 endpoints)

3. **Execute in batches**:
   - 6 files per batch
   - 4 modules per batch
   - 8 tests per batch
   - Load template ONCE, generate all items in batch

4. **Ground truth verification**:
   ```bash
   # File creation
   test -f path/to/file && echo "✅ EXISTS" || echo "❌ MISSING"

   # Tests pass
   pytest tests/ -q && echo "✅ PASS" || echo "❌ FAIL"

   # Imports work
   python -c "import module" && echo "✅ IMPORTS" || echo "❌ BROKEN"
   ```

### Validation Requirements

**Before declaring workstream complete**:

1. **Acceptance Tests**: All tests in `[VALIDATION]` section must pass
2. **Ground Truth**: Programmatic verification (exit codes, file existence)
3. **File Scope**: No modifications outside authorized scope
4. **Quality Gates**: Meet classification requirements (e.g., production-ready if `quality: production`)

### Anti-Pattern Guards (ENABLED)

All 11 guards are active during workstream execution:

**Tier 1 - Critical**:
1. Hallucination of Success (12h saved) - Require exit_code verification
2. Incomplete Implementation (5h saved) - Detect TODO/pass placeholders
3. Silent Failures (4h saved) - Require explicit error handling
4. Framework Over-Engineering (10h saved) - Remove unused infrastructure

**Tier 2 - High**:
5. Planning Loop Trap (16h saved) - Max 2 planning iterations
6. Test-Code Mismatch (6h saved) - Mutation testing required

**Tier 3 - Medium**:
7. Configuration Drift (3h saved) - Ban hardcoded values
8. Module Integration Gap (2h saved) - Require integration tests
9. Documentation Lies (3h saved) - Type checking enforced
10. Partial Success Amnesia (12h saved) - Checkpoint after steps
11. Approval Loop (12h saved) - No human approval for safe ops

**Total Impact**: 85 hours waste prevented per project

---

## Workstream Execution Guidelines

### Phase Understanding

Workstreams typically execute in phases:
- **EDIT**: Code changes using Aider or AI tools
- **STATIC**: Static analysis (linting, type checking)
- **RUNTIME**: Runtime tests (pytest, integration tests)

Your execution happens during the **EDIT** phase.

### Tool Integration

You may be invoked through:
- **Aider CLI**: With rendered Jinja2 prompts
- **Direct Codex API**: Through tool profiles in `config/tool_profiles.json`

In both cases:
- Follow execution patterns (if N ≥ 3)
- Enable anti-pattern guards
- Verify ground truth before completion

### Git Worktree Awareness

**Context**: Each workstream runs in an isolated git worktree.

```bash
# Worktree structure
.worktrees/
  └── <ws-id>/           # Your execution environment
      ├── files...       # Repository files
      └── .aider/        # Aider prompts and state
```

**Implications**:
- Changes are isolated from main repository
- Multiple workstreams can run in parallel
- After completion, changes are merged back via git

### Windows Platform Notes

**Primary Platform**: Windows with PowerShell (`pwsh`)

```powershell
# DateTime format (Windows PowerShell)
Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

# Path handling (use pathlib in Python)
from pathlib import Path
repo_root = Path(__file__).parent.parent
```

**Cross-platform compatibility**:
- Use `Path` from `pathlib` for paths
- Use `python -m` for module execution
- Prefer PowerShell wrappers for Windows-first operations

---

## Common Patterns

### Pattern 1: Multi-File Creation

**When**: Creating N ≥ 3 similar files (e.g., plugin manifests)

```
1. Identify pattern: EXEC-001 Batch File Creator
2. Create first 2-3 examples manually
3. Extract invariants (template)
4. Mark variables (name, path, config)
5. Generate remaining files in batches of 6
6. Verify: ls -la output/*.json | wc -l (matches expected count)
```

### Pattern 2: Test Suite Generation

**When**: Writing N ≥ 5 similar tests

```
1. Identify pattern: EXEC-003 Test Multiplier
2. Create first 2 test cases manually
3. Extract test structure template
4. Generate remaining tests in batches of 8
5. Verify: pytest tests/ -q && echo "✅ PASS"
```

### Pattern 3: Module Generation

**When**: Creating N ≥ 3 similar code modules

```
1. Identify pattern: EXEC-002 Module Generator
2. Create first module with full implementation
3. Extract module structure and common code
4. Generate remaining modules in batches of 4
5. Verify: python -c "import module" for each
```

---

## Quick Reference Commands

```bash
# Verify execution pattern applicability
# If N ≥ 3 similar items → Use pattern

# Check file exists (ground truth)
test -f path/to/file && echo "✅" || echo "❌"

# Run acceptance tests (ground truth)
pytest tests/ -q && echo "✅ PASS" || echo "❌ FAIL"

# Verify imports (ground truth)
python -c "import module" && echo "✅" || echo "❌"

# Count files created (batch verification)
ls -la output/*.py | wc -l
```

---

## References

### Core Documentation
- **Execution Patterns**: `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`
- **Quick Reference**: `docs/reference/ai-agents/QUICK_REFERENCE_CARD.md`
- **AI Agents Overview**: `docs/reference/ai-agents/README.md`

### Repository Documentation
- **Architecture**: `docs/ARCHITECTURE.md`
- **Workstream Authoring**: `docs/workstream_authoring_guide.md`
- **Aider Contract**: `docs/aider_contract.md`
- **Plugin Ecosystem**: `docs/plugin-ecosystem-summary.md`

### Schema & Validation
- **Workstream Schema**: `schema/workstream.schema.json`
- **Database Schema**: `schema/schema.sql`

### Templates
- **Workstream Template**: `aider/templates/workstream_template.json`
- **Prompt Templates**: `aider/templates/prompts/*.txt.j2`

---

## Tips for Codex via Aider

### 1. Understand Your Context First
- Read the `[CONTEXT]` section to understand repo and worktree paths
- Review `[FILE_SCOPE]` to know what files you can modify
- Check `[TASKS]` for what needs to be accomplished
- Review `[VALIDATION]` for success criteria

### 2. Apply Execution Patterns
- Before starting, check if N ≥ 3 similar items
- If yes, use execution pattern (see EXECUTION_PATTERNS_MANDATORY.md)
- If no, proceed with single implementation

### 3. Stay Within Scope
- Only edit files listed in `files_scope`
- Only create files listed in `files_create`
- Modifications outside scope will be rejected

### 4. Verify Ground Truth
- Don't declare success based on "looks good"
- Use programmatic verification (exit codes, file existence)
- Run acceptance tests before claiming completion

### 5. Respect Quality Classification
- `production` classification requires:
  - Comprehensive error handling
  - Type hints and documentation
  - Full test coverage
  - Security considerations

---

## Remember

> **Decide once → Apply N times → Trust ground truth → Move on**

This is **MANDATORY** and **ENFORCED**. No exceptions.
