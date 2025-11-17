# OpenSpec + Pipeline Hybrid Workflow

## Overview

This document describes the integrated workflow combining OpenSpec specification management with your pipeline orchestrator for deterministic AI-driven development.

## Conceptual Model

### CCPM's 5 Phases → Your Implementation

| CCPM Phase | OpenSpec Role | Your Pipeline Role |
|------------|---------------|-------------------|
| **Think** | Create proposals, brainstorm | Review existing code/docs |
| **Document** | Write requirements with SHALL/MUST | Define in `proposal.md` |
| **Plan** | Convert to tasks | Generate `workstreams/*.json` |
| **Execute** | Track progress | Orchestrator (EDIT → STATIC → RUNTIME) |
| **Track** | Archive completed specs | SQLite database + event log |

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: THINK                              │
│  Brainstorm feature requirements with Claude Code                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: DOCUMENT                              │
│  OpenSpec: Write formal specifications                              │
│                                                                      │
│  /openspec:proposal "Add rate limiting to API"                      │
│                                                                      │
│  Creates:                                                            │
│    openspec/changes/rate-limiting/                                  │
│    ├── proposal.md                                                  │
│    │   ---                                                           │
│    │   title: Rate Limiting                                         │
│    │   ---                                                           │
│    │   ## Requirements                                              │
│    │   ### Requirement: Request Rate Limiting                       │
│    │   The API SHALL limit requests to 100/min per client.          │
│    │                                                                 │
│    │   #### Scenario: Exceed Limit                                  │
│    │   - WHEN client makes 101 requests in 1 minute                 │
│    │   - THEN API SHALL return 429 status                           │
│    │                                                                 │
│    └── tasks.md                                                     │
│        - [ ] Add rate limiter middleware                            │
│        - [ ] Configure Redis backend                                │
│        - [ ] Add monitoring                                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PHASE 3: PLAN                                 │
│  Bridge: Convert spec to workstream bundle                          │
│                                                                      │
│  python scripts/spec_to_workstream.py --interactive                 │
│                                                                      │
│  Generates:                                                          │
│    workstreams/ws-rate-limiting.json                                │
│    {                                                                 │
│      "id": "ws-rate-limiting",                                      │
│      "openspec_change": "rate-limiting",                            │
│      "gate": 1,                                                     │
│      "files_scope": [                                               │
│        "src/api/middleware/rate_limiter.py",                        │
│        "config/rate_limits.yaml"                                    │
│      ],                                                              │
│      "tasks": [                                                     │
│        "Add rate limiter middleware",                               │
│        "Configure Redis backend",                                   │
│        "Add monitoring"                                             │
│      ],                                                              │
│      "acceptance_tests": [                                          │
│        "Verify: Exceed Limit scenario",                             │
│        "pytest tests/api/test_rate_limiting.py"                     │
│      ]                                                               │
│    }                                                                 │
│                                                                      │
│  python scripts/validate_workstreams.py  ✓                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 4: EXECUTE                               │
│  Pipeline: Orchestrated deterministic execution                     │
│                                                                      │
│  python scripts/run_workstream.py --ws-id ws-rate-limiting          │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Orchestrator: EDIT → STATIC → RUNTIME → PIPELINE              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Step 1: EDIT Phase                                                 │
│    • Create worktree: .worktrees/ws-rate-limiting/                 │
│    • Invoke Aider with tasks from workstream                        │
│    • Implement rate limiter middleware                              │
│    • Configure Redis connection                                     │
│    • Add monitoring hooks                                           │
│    • Aider commits changes                                          │
│                                                                      │
│  Step 2: STATIC Phase                                               │
│    • Run plugins: ruff, black, mypy, pyright, bandit               │
│    • Collect issues: PluginResult[]                                 │
│    • If errors: → Error Pipeline                                    │
│      - Deduplicate errors by signature                              │
│      - Generate fix prompts                                         │
│      - Invoke Aider with /fix                                       │
│      - Re-run static checks                                         │
│    • Exit condition: Zero static errors                             │
│                                                                      │
│  Step 3: RUNTIME Phase                                              │
│    • Run acceptance tests                                           │
│    • pytest tests/api/test_rate_limiting.py                         │
│    • If failures: → Error Pipeline                                  │
│    • Exit condition: All tests pass                                 │
│                                                                      │
│  Step 4: PIPELINE Phase (if needed)                                 │
│    • Error state machine: NEW → ANALYZED → FIXED → VERIFIED        │
│    • Circuit breakers prevent infinite loops                        │
│    • Recovery strategies applied                                    │
│                                                                      │
│  Database Updates (SQLite):                                         │
│    runs: status = 'completed'                                       │
│    workstreams: state = 'done'                                      │
│    step_attempts: All steps recorded                                │
│    events: Append-only audit trail                                  │
│    errors: Deduplicated error records                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PHASE 5: TRACK                                │
│  Archive and Audit                                                  │
│                                                                      │
│  Database Query:                                                    │
│    SELECT w.id, w.openspec_change, w.state, r.status               │
│    FROM workstreams w                                               │
│    JOIN runs r ON w.run_id = r.id                                  │
│    WHERE w.id = 'ws-rate-limiting'                                  │
│                                                                      │
│    Result:                                                          │
│    ┌───────────────────┬──────────────────┬────────┬───────────┐  │
│    │ id                │ openspec_change  │ state  │ status    │  │
│    ├───────────────────┼──────────────────┼────────┼───────────┤  │
│    │ ws-rate-limiting  │ rate-limiting    │ done   │ completed │  │
│    └───────────────────┴──────────────────┴────────┴───────────┘  │
│                                                                      │
│  Archive OpenSpec:                                                  │
│    /openspec:archive rate-limiting                                  │
│                                                                      │
│    Moves: openspec/changes/rate-limiting/                           │
│       → openspec/archive/rate-limiting/                             │
│                                                                      │
│  Git Commit (if desired):                                           │
│    git commit -m "feat: add API rate limiting (OpenSpec: rate-limiting)" │
└─────────────────────────────────────────────────────────────────────┘
```

## Traceability Chain

```
OpenSpec Change ID: "rate-limiting"
    │
    ├─→ proposal.md (requirements + scenarios)
    │
    ├─→ tasks.md (task checklist)
    │
    └─→ Bridge Conversion
         │
         └─→ Workstream Bundle: "ws-rate-limiting"
              │
              ├─→ Run: run-<uuid>
              │    │
              │    ├─→ Step Attempts (EDIT, STATIC, RUNTIME)
              │    │    │
              │    │    └─→ Plugin Results
              │    │         └─→ Issues (if any)
              │    │
              │    ├─→ Errors (deduplicated)
              │    │    │
              │    │    └─→ Error Context
              │    │         ├─→ State: NEW → ANALYZED → FIXED → VERIFIED
              │    │         └─→ Fix Attempts
              │    │
              │    └─→ Events (append-only log)
              │         ├─→ workstream_started
              │         ├─→ edit_phase_started
              │         ├─→ static_checks_passed
              │         ├─→ runtime_tests_passed
              │         └─→ workstream_completed
              │
              └─→ Merge to main branch
                   └─→ Archive OpenSpec change
```

## Comparison: Traditional CCPM vs Your Hybrid

### Traditional CCPM (GitHub-Centric)

```
PRD → Epic → Tasks → GitHub Issues → Agents → Commits → PRs
  ↑                                                        ↓
  └────────────────── Manual Sync ──────────────────────────┘
```

**Pros:**
- Team visibility (GitHub)
- Parallel agents via worktrees
- Comment-based audit trail

**Cons:**
- GitHub dependency
- Manual sync overhead
- No deterministic execution
- Limited error recovery

### Your Hybrid (OpenSpec + Pipeline)

```
OpenSpec → Bridge → Workstream → Orchestrator → SQLite
    ↑                                             ↓
    └─────────────── Archive After Success ──────┘
```

**Pros:**
- Specification-first (OpenSpec)
- Deterministic execution (Orchestrator)
- Sophisticated error pipeline
- SQLite state (no GitHub required)
- Plugin-based validation (17+ plugins)
- Circuit breakers & recovery
- Parallel workstreams via scheduler

**Cons:**
- Less team visibility (unless shared DB)
- No built-in issue tracking (can add)

**Best of Both:**
- You could add GitHub sync as an optional feature later
- Keep SQLite as primary, GitHub as secondary
- OpenSpec provides better spec management than PRDs

## Key Decisions

### 1. State Storage: SQLite vs GitHub

**Your Choice: SQLite**

Rationale:
- Deterministic queries
- No API rate limits
- Offline capable
- Structured schema
- Fast local access

Optional: Add GitHub sync for team visibility

### 2. Specification Format: PRDs vs OpenSpec

**Your Choice: OpenSpec**

Rationale:
- Formal requirement language (SHALL/MUST)
- Testable scenarios (WHEN/THEN)
- Native Claude Code integration
- Version control friendly (Markdown)
- Change tracking built-in

### 3. Execution Model: Manual vs Orchestrated

**Your Choice: Orchestrated**

Rationale:
- Deterministic phases
- Error recovery automation
- Plugin extensibility
- Circuit breakers
- State machine clarity

### 4. Bridge vs Manual: Automation Level

**Your Choice: Bridge with Review**

Rationale:
- Automated generation reduces errors
- Review step maintains control
- Defaults are sensible
- Override options available

## Workflow Variations

### Variation 1: Simple Feature (Single Workstream)

```bash
# 1. Specify
/openspec:proposal "Add JSON export for reports"

# 2. Convert
python scripts/spec_to_workstream.py --interactive

# 3. Execute
python scripts/run_workstream.py --ws-id ws-json-export

# 4. Archive
/openspec:archive json-export
```

Time: ~30 minutes (mostly spec writing)

### Variation 2: Complex Feature (Multiple Workstreams)

```bash
# 1. Specify (comprehensive)
/openspec:proposal "Implement caching layer"

# 2. Manually create dependent workstreams
# ws-caching-backend (foundation)
# ws-caching-api (depends: backend)
# ws-caching-monitoring (depends: api)

# 3. Execute in order (scheduler handles deps)
python scripts/run_workstream.py --ws-id ws-caching-backend
python scripts/run_workstream.py --ws-id ws-caching-api
python scripts/run_workstream.py --ws-id ws-caching-monitoring

# 4. Archive
/openspec:archive caching-layer
```

Time: Hours to days (depending on complexity)

### Variation 3: Bug Fix (Fast Track)

```bash
# 1. Lightweight spec
/openspec:proposal "Fix rate limiter edge case"

# 2. Convert with specific files
python scripts/spec_to_workstream.py --change-id rate-limiter-fix \
  --ws-id ws-fix-rate-limiter

# Manually edit bundle to reduce scope:
{
  "files_scope": ["src/api/middleware/rate_limiter.py"],
  "tasks": ["Fix off-by-one error in rate calculation"],
  "acceptance_tests": ["pytest tests/api/test_rate_limiting.py::test_edge_case"]
}

# 3. Execute
python scripts/run_workstream.py --ws-id ws-fix-rate-limiter

# 4. Archive
/openspec:archive rate-limiter-fix
```

Time: ~15 minutes

### Variation 4: Refactoring (No New Features)

```bash
# 1. Spec the refactor
/openspec:proposal "Extract rate limiter to separate module"

# 2. Convert and adjust files_scope
python scripts/spec_to_workstream.py --interactive
# Review: Ensure all affected files in scope

# 3. Execute
python scripts/run_workstream.py --ws-id ws-refactor-rate-limiter

# 4. Verify (important for refactors!)
python scripts/db_inspect.py
# Check: runtime tests passed, no new errors

# 5. Archive
/openspec:archive refactor-rate-limiter
```

Time: ~1 hour

## Error Handling Example

```
Workstream: ws-rate-limiting
Phase: STATIC
Plugin: mypy

Error Detected:
  src/api/middleware/rate_limiter.py:42
  error: Argument 1 to "set" has incompatible type "int"; expected "str"

Pipeline Actions:
  1. Deduplicate (check signature)
  2. Create error context (NEW state)
  3. Generate fix prompt
  4. Invoke Aider with /fix
  5. Re-run mypy
  6. If fixed: VERIFIED
  7. If still broken: Escalate or circuit-break

Database Records:
  errors table:
    - signature: "mypy:incompatible-type:rate_limiter.py:42"
    - occurrence_count: 1
    - state: VERIFIED

  events table:
    - error_detected
    - error_analyzing
    - error_fixed
    - error_verified
    - static_checks_passed (retry)
```

## Best Practices

### 1. Always Spec First
```
❌ /openspec:proposal "Implement stuff" → run immediately
✓ /openspec:proposal "..." → write requirements → review → convert → run
```

### 2. Use Meaningful IDs
```
❌ ws-feature-123
✓ ws-rate-limiting-api
```

### 3. Link Everything
```json
{
  "id": "ws-rate-limiting",
  "openspec_change": "rate-limiting",  // ← Traceability
  "ccpm_issue": 0,  // ← Optional GitHub issue
  "metadata": {
    "owner": "api-team",
    "notes": "Addresses security audit finding #42"
  }
}
```

### 4. Review Generated Bundles
```bash
# Always dry-run first
python scripts/spec_to_workstream.py --change-id <id> --dry-run

# Review output, then save
python scripts/spec_to_workstream.py --change-id <id>

# Edit if needed
nano workstreams/ws-<feature>.json

# Validate before running
python scripts/validate_workstreams.py
```

### 5. Archive Completed Work
```bash
# Don't let openspec/changes/ accumulate
/openspec:archive <change-id>

# Archive moves to openspec/archive/ (still in version control)
```

## Summary

Your hybrid workflow combines:

| Component | Purpose |
|-----------|---------|
| **OpenSpec** | Specification management (requirements, scenarios) |
| **Bridge** | Automation (spec → workstream) |
| **Orchestrator** | Deterministic execution (EDIT → STATIC → RUNTIME) |
| **SQLite** | State tracking (runs, workstreams, errors, events) |
| **Plugins** | Validation (17+ tools) |
| **Error Pipeline** | Recovery (state machine, deduplication, fixes) |

Result: **Spec-driven, deterministic, AI-powered development with full traceability**

## Next: Try It!

```bash
# 1. Create a test proposal
/openspec:proposal "Add hello world endpoint"

# 2. Write a simple requirement
# In proposal.md:
# ### Requirement: Hello Endpoint
# The API SHALL respond to GET /hello with "Hello, World!".

# 3. Add a task
# In tasks.md:
# - [ ] Create GET /hello endpoint in src/api/routes/hello.py

# 4. Convert
python scripts/spec_to_workstream.py --interactive

# 5. Run
python scripts/run_workstream.py --ws-id ws-add-hello-world-endpoint --dry-run

# 6. Review (no external changes in dry-run)
python scripts/db_inspect.py

# 7. Run for real
python scripts/run_workstream.py --ws-id ws-add-hello-world-endpoint

# 8. Archive
/openspec:archive add-hello-endpoint
```

You've now completed a full spec → execute → archive cycle!
