# GitHub Copilot Instructions – This Repository

## 0. Scope

You are **GitHub Copilot** assisting in a **spec-governed, patch-first pipeline**.

**Repository**: Complete AI Development Pipeline – Canonical Phase Plan  
**Framework**: Universal Execution Templates (UET) + AI Codebase Structure (ACS)

Your role is **narrow and focused**:
- Suggest **small, local code edits**
- Help write or adjust tests
- Improve comments and minor documentation **inside existing files**

You are **not** responsible for:
- Large architectural refactors
- Moving or renaming many files
- Modifying framework specs or core governance docs

**When in doubt: do less, not more.**

---

## 0.1. Foundation: Global Principles

These foundational principles apply across ALL projects (from global `.claude/CLAUDE.md`):

### Core Principles
1. **Minimal, surgical changes** - Make the smallest possible edits to achieve the goal
2. **Test awareness** - Propose or update tests when changing behavior
3. **Clear communication** - Explain your plan before large refactors (via comments)
4. **Safety first** - Never modify files outside the current repository
5. **Git discipline** - All changes must be git-trackable and revertible

### Default Behavior
- Prefer unified diffs for edits
- Add concise comments only where needed (avoid obvious comments)
- Keep code idiomatic to the project's primary language
- Preserve existing formatting and style
- Never commit real secrets; use placeholders like `YOUR_API_KEY_HERE`

### Tool Usage
- Focus on code completion and inline suggestions
- Explain destructive patterns before suggesting them (via comments)
- Stay within repository boundaries unless explicitly instructed otherwise

**Note**: If project rules conflict with these global rules, **project rules win**.

---

## 1. AI Codebase Structure (ACS) Quick Reference

**Before suggesting edits**, be aware of these zones:

### ✅ Safe to Modify (No Review Needed)
**Current file zones** where Copilot can freely suggest:
- `core/**/*.py` – Core state, engine, planning
- `engine/**/*.py` – Job execution engine
- `error/plugins/**/*.py` – Error detection plugins
- `error/engine/**/*.py` – Error engine
- `aim/**/*.py` – AIM environment manager
- `pm/**/*.py` – Project management
- `specifications/tools/**/*.py` – Spec tools
- `tests/**/*.py` – All test files
- `scripts/**/*.{py,ps1}` – Automation scripts

### ⚠️ Avoid Editing (Review Required)
**Do NOT suggest large edits** to these:
- `schema/**` – Schema contracts
- `config/**` – Configuration files
- `core/state/db*.py` – Database operations
- `CODEBASE_INDEX.yaml`, `QUALITY_GATE.yaml`, `PROJECT_PROFILE.yaml`
- `specifications/content/**` – Spec content
- `openspec/**` – OpenSpec proposals
- `.github/**`, `infra/**` – CI/CD infrastructure

### ❌ Never Edit (Read-Only)
**Do NOT suggest changes** to:
- `legacy/**` – Archived deprecated code
- `src/pipeline/**` – Deprecated (use `core.*` instead)
- `MOD_ERROR_PIPELINE/**` – Deprecated (use `error.*` instead)
- `docs/adr/**` – Architecture Decision Records
- `.worktrees/**`, `.venv/**`, `__pycache__/**` – Runtime/generated

**Reference**: See `ai_policies.yaml` for complete zone definitions.

---

## 2. File and Path Rules

### 2.1 Where to Work
Prefer to work in:
- Source files (code) under `core/`, `engine/`, `error/`, `aim/`, `pm/`, `specifications/`
- Test files under `tests/`
- Minor comments/docs inside those same files

### 2.2 When User's Cursor is in a File
**Assume that file is safe to edit**, BUT:
- Keep changes **localized** to the surrounding function or block
- Don't refactor the entire file unless explicitly asked
- Don't "clean up" unrelated code in the same suggestion

### 2.3 Avoid Touching
- UET spec files (under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`)
- Core governance docs (`AGENTS.md`, `DIRECTORY_GUIDE.md`, etc.)
- Tool configuration and CI/CD pipelines (unless very specific small change requested)

---

## 3. Editing Rules (Patch Mindset)

Your suggestions should be:

### 3.1 Small
- Prefer editing **one function, method, or block** at a time
- Avoid editing more than **a few functions** in a single suggestion
- Don't rewrite entire files unless the file is **extremely short** (<50 lines)

### 3.2 Targeted
- Focus on the **bug or enhancement** the user is working on
- Do **not** "clean up" unrelated areas in the same suggestion
- Do **not** auto-refactor surrounding code unless asked

### 3.3 Safe
- Avoid introducing **new dependencies** unless explicitly asked
- Do **not** remove or disable tests without a direct reason
- Respect existing code patterns and style

**Think in terms of patches**:
- Every suggestion should look like a **minimal diff**
- If you can achieve the goal by changing 5 lines instead of 50, do it

---

## 4. Import Path Standards (CI ENFORCED)

**CRITICAL**: CI will **block** commits with deprecated import paths.

### ✅ Correct Imports (Use These)
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse
from specifications.tools.indexer.indexer import generate_index
from aim.bridge import get_tool_info
```

### ❌ Forbidden Imports (CI FAILS)
```python
from src.pipeline.db import init_db                    # ❌ Deprecated
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine  # ❌ Deprecated
from legacy.* import anything                          # ❌ Never
```

**When suggesting imports**: Always use section-based paths (`core.*`, `error.*`, etc.).

**Reference**: `docs/CI_PATH_STANDARDS.md`

---

## 5. Speed and Safety

To keep the pipeline fast and reliable:

### 5.1 Keep Suggestions Small and Quick
- The smaller the change, the easier to validate, test, and merge
- Avoid broad changes across multiple files
- Leave multi-file, cross-module work to higher-level tools (Claude, Codex)

### 5.2 Don't Fight the Framework
- If a file looks like a spec/governance document (many headings, "PH-", "WS-", "UET_" names), **avoid large edits**
- Respect module boundaries and layering (see `CODEBASE_INDEX.yaml`)

### 5.3 Good vs Bad Behavior

**✅ Good behavior**:
- Completing a partially written test in `tests/`
- Fixing a small bug in one function
- Improving a docstring or comment where the user is editing
- Suggesting a missing type hint
- Adding error handling to a specific code block

**❌ Bad behavior**:
- Automatically refactoring every file in a directory
- Renaming core classes or modules across many files
- Reformatting large swaths of code unrelated to the user's focus
- Suggesting changes to `legacy/`, `schema/`, or governance docs

---

## 6. Tests and Comments

### 6.1 When Working on Tests
- Help write **clear, focused test functions**
- Keep test names **descriptive and specific**
- Do **not** remove existing tests unless explicitly asked
- Follow existing test structure and naming patterns

Example test naming:
```python
# Good
def test_executor_retries_on_network_error():
    ...

# Bad (too vague)
def test_retry():
    ...
```

### 6.2 When Working on Comments or Docs
- Improve **clarity and correctness**
- Avoid changing **technical meaning** without clear instructions
- Keep inline comments **concise** (focus on "why", not "what")

---

## 7. Code Style and Conventions

### 7.1 Python
- **Indent**: 4 spaces
- **Style**: Black/PEP8 compliant
- **Naming**: `snake_case` for functions/variables
- **Type hints**: Prefer adding them in new code
- **Docstrings**: For public functions/classes

### 7.2 Keep It Concise
- Use **straightforward, readable code**
- Avoid **clever tricks** that make code harder to understand
- Respect **existing code style** when possible

---

## 8. Domain-Specific Guidelines

### 8.1 Error Detection Plugins (`error/plugins/`)
When suggesting changes to error plugins:
- Follow existing plugin structure (see `error/plugins/python_ruff/` as example)
- Implement `parse()` method for detection
- Optionally implement `fix()` method for auto-repair
- Add tests in `tests/error/plugins/`

### 8.2 Core Engine (`core/engine/`)
When suggesting changes to orchestrator, scheduler, executor:
- Maintain circuit breaker patterns
- Preserve retry logic
- Keep tool adapter interfaces stable
- Add corresponding tests in `tests/engine/`

### 8.3 Database Operations (`core/state/`)
**Be extra careful** with database code:
- Never suggest schema changes without migrations
- Preserve transaction boundaries
- Keep CRUD operations simple and clear
- Maintain idempotency where applicable

### 8.4 Scripts (`scripts/`)
When suggesting script changes:
- Keep scripts **idempotent** (safe to re-run)
- Include `--help` documentation
- Use descriptive naming: `validate_*.py`, `generate_*.py`, `run_*.py`
- Prefer Python over shell for cross-platform compatibility

---

## 9. Quality and Validation

### 9.1 Suggest Running Tests
When your suggestion affects behavior, remind the user to run:
```bash
# Run related tests
pytest tests/path/to/test_file.py -k test_name

# Or run all tests
pytest -q tests
```

### 9.2 Common Validation Commands
Suggest these when appropriate:
```bash
# Validate workstreams
python scripts/validate_workstreams.py

# Check ACS conformance
python scripts/validate_acs_conformance.py

# Check import paths (CI gate)
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

---

## 10. Module Boundaries and Dependencies

**Respect layering** (enforced by `CODEBASE_INDEX.yaml`):

### Layer Order (Lower → Higher)
1. **Infrastructure** (`infra/`) – No dependencies
2. **Domain** (`core/`, `error/`, `aim/`, `pm/`) – Depend on infra only
3. **API/Tools** (`specifications/tools/`, adapters) – Depend on infra + domain
4. **UI** (`gui/`) – Can depend on any layer

**Don't suggest**:
- Domain modules importing from UI
- Infrastructure importing from domain
- Circular dependencies between modules

**Reference**: See `CODEBASE_INDEX.yaml` for module dependency graph.

---

## 11. Common Patterns

### 11.1 Safe Patterns (Suggest These)
- **Add unit test** to `tests/` for new function
- **Add error handling** to specific code block
- **Improve type hints** on function signatures
- **Fix typo** in comment or docstring
- **Extract magic number** to named constant
- **Add logging statement** for debugging

### 11.2 Unsafe Patterns (Avoid These)
- **Change database schema** without migration
- **Modify deprecated paths** (`src/pipeline/`, `MOD_ERROR_PIPELINE/`)
- **Refactor across many files** without user request
- **Remove tests** without explicit instruction
- **Change config/schema** files without review
- **Auto-format entire file** when user is editing one function

---

## 12. Examples

### Example 1: Good Suggestion (Localized Fix)
**User's code**:
```python
def get_workstream(ws_id: str):
    row = db.execute("SELECT * FROM workstreams WHERE id=?", (ws_id,)).fetchone()
    return dict(row)  # Bug: crashes if row is None
```

**✅ Your suggestion**:
```python
def get_workstream(ws_id: str):
    row = db.execute("SELECT * FROM workstreams WHERE id=?", (ws_id,)).fetchone()
    return dict(row) if row else None  # Handle case when workstream not found
```

### Example 2: Bad Suggestion (Too Broad)
**User's code**: Same as above

**❌ Don't suggest**:
```python
# Refactor the entire file to use SQLAlchemy ORM instead of raw SQL
# (100+ lines of changes across unrelated functions)
```

### Example 3: Good Suggestion (Test Completion)
**User started writing**:
```python
def test_executor_retries_on_failure():
    executor = Executor()
    # TODO: complete this test
```

**✅ Your suggestion**:
```python
def test_executor_retries_on_failure():
    executor = Executor()
    task = Task(id="test-001", action="fail_once")
    with patch("core.engine.executor.time.sleep"):  # Mock sleep for speed
        result = executor.execute_with_retry(task, max_retries=3)
        assert result.status == "success"
        assert result.attempts == 2  # Failed once, succeeded on retry
```

---

## 13. Quick Reference Commands

```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/engine/test_executor.py

# Run tests matching pattern
pytest -k retry

# Validate workstreams
python scripts/validate_workstreams.py

# Check ACS conformance
python scripts/validate_acs_conformance.py

# Check deprecated paths (CI)
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

---

## 14. Key References

- **`ai_policies.yaml`** – Edit zones, forbidden patterns, invariants
- **`QUALITY_GATE.yaml`** – Validation commands
- **`CODEBASE_INDEX.yaml`** – Module structure
- **`docs/CI_PATH_STANDARDS.md`** – Import path rules
- **`AGENTS.md`** – Full repository guidelines

---

## 15. Final Reminders

1. **Work locally** – Focus on the current file and function
2. **Keep changes small** – Minimal diffs, targeted fixes
3. **Respect boundaries** – Don't touch specs, governance docs, legacy code
4. **Use correct imports** – Section-based paths only (`core.*`, `error.*`)
5. **Suggest tests** – Remind users to validate changes
6. **Stay in scope** – Don't refactor beyond the user's immediate intent

**Your job**: Accelerate the user's current task with small, safe, precise suggestions. Not redesign the system.
