---
doc_id: DOC-LEGACY-AUTOMATED-CONVERSION-EXAMPLES-SHOWING-025
---

Below are automated conversion examples showing how to transform existing Codex/Claude style phase prompts into Aider-compatible workstream instruction files, plus a reference Python script that performs heuristic conversion.

---

## Overview

We’ll cover:
1. Example Original Codex/Claude Prompts (2 variants).
2. Converted Aider Workstream Files (front‑matter + structured sections).
3. A Python conversion script (heuristic, pluggable).
4. Mapping & heuristics table.
5. Extension ideas for more robust automation.

---

## 1. Example Original Codex/Claude Prompt (Variant A)

Original (unstructured, typical style):

```
PHASE: PH-02
ROLE: You are a senior backend engineer improving reliability.
OPERATING CONTEXT:
We have a database layer in src/pipeline/db.py. No schema changes allowed.
GOALS:
- Add state machine enforcing transitions: created -> running -> completed | failed
- Ensure invalid transitions are rejected.
- Provide helper: validate_state_transition(old_state, new_state) -> bool
REQUIRED OUTPUTS:
Update db.py with state logic, add tests in tests/pipeline/test_db_state.py.
Constraints: Do not touch other files. No new dependencies.
ACCEPTANCE:
Tests must pass: test_valid_transitions, test_invalid_transitions.
Add docstring summarizing state machine at top of db.py.
EXECUTION PLAN:
1. Sketch state machine and possible transitions.
2. Implement validation helper.
3. Integrate into existing update_run_status.
4. Write tests.
5. Run tests and finalize.
COMPLETION:
All tests green, lint passes, only two files changed.
```

---

## 2. Converted Aider Workstream Instruction (Variant A)

````markdown name=ws-ph02-state-machine.md
---
workstream_id: "ws-ph02-state-machine"
phase: "PH-02"
title: "Enforce run status state machine in db layer"
description: "Add deterministic state transition validation for run statuses without schema changes."
difficulty: "medium"
version_target: "v1.0"
depends_on: []
owners: ["DICKY1987"]
tags: ["phase:PH-02", "component:db"]
writable_globs:
  - "src/pipeline/db.py"
  - "tests/pipeline/test_db_state.py"
readonly_globs:
  - "schema/**/*.sql"
out_of_scope_globs:
  - "src/pipeline/tools.py"
abort_on_missing_dependencies: true
environment:
  os: "linux"
  languages: { python: "3.11" }
  tools: ["pytest", "flake8"]
preconditions:
  tests_available: true
  migrations_required: false
test_command: "pytest -q"
lint_command: "flake8"
format_command: ""
commit_convention: "conventional"
commit_scope: "ws-ph02-state-machine"
determinism:
  stable_sorting: true
  timestamps: "forbid"
  randomness: "forbid"
guardrails:
  scope_violation_action: "/undo then restate constraints"
  rollback_triggers:
    - "tests fail"
    - "lint introduces new errors"
    - "diff includes out-of-scope file"
artifacts:
  - path: "src/pipeline/db.py"
    type: "code"
    must_provide:
      - "module docstring: describes allowed transitions"
      - "function: validate_state_transition(old_state, new_state) -> bool"
      - "integration: update_run_status calls validate_state_transition before persisting"
    must_not:
      - "modify schema"
      - "introduce new dependencies"
    acceptance:
      tests: ["tests/pipeline/test_db_state.py::test_valid_transitions",
              "tests/pipeline/test_db_state.py::test_invalid_transitions"]
      lint: true
      commands: []
    determinism:
      - "logic is pure; no time-based decisions"
  - path: "tests/pipeline/test_db_state.py"
    type: "test"
    must_provide:
      - "test_valid_transitions"
      - "test_invalid_transitions"
    must_not:
      - "network calls"
    acceptance:
      tests: ["tests/pipeline/test_db_state.py::test_valid_transitions",
              "tests/pipeline/test_db_state.py::test_invalid_transitions"]
      lint: true
      commands: []
operations_sequence:
  - id: 1
    intent: "Design transition set & validation approach"
    files_add: ["src/pipeline/db.py"]
    command: "/architect"
    expected_diff_summary: "Adds docstring stub with transition diagram comment"
    commit_message: "docs(ws-ph02-state-machine): add state machine overview"
  - id: 2
    intent: "Add validate_state_transition function skeleton"
    files_add: ["src/pipeline/db.py"]
    command: "/code"
    expected_diff_summary: "Introduces placeholder function returning NotImplemented"
    commit_message: "feat(ws-ph02-state-machine): add validation function skeleton"
  - id: 3
    intent: "Implement validation logic and integrate into update_run_status"
    files_add: ["src/pipeline/db.py"]
    command: "/code"
    expected_diff_summary: "validate_state_transition returns bool; update_run_status raises ValueError for invalid transition"
    commit_message: "feat(ws-ph02-state-machine): enforce transitions in update_run_status"
  - id: 4
    intent: "Create tests for valid & invalid transitions"
    files_add: ["tests/pipeline/test_db_state.py"]
    command: "/code"
    expected_diff_summary: "Adds test_valid_transitions & test_invalid_transitions"
    commit_message: "test(ws-ph02-state-machine): add transition tests"
  - id: 5
    intent: "Run tests and lint"
    files_add: []
    command: "/test pytest -q"
    expected_diff_summary: "No file changes; confirm pass"
    commit_message: "chore(ws-ph02-state-machine): confirm test pass (no changes)"
completion_checklist:
  - "[ ] Module docstring documents transitions"
  - "[ ] validate_state_transition implemented"
  - "[ ] update_run_status checks transitions"
  - "[ ] Tests pass: test_valid_transitions, test_invalid_transitions"
  - "[ ] Lint passes"
  - "[ ] No out-of-scope changes"
---

## ROLE & OBJECTIVE
Implement deterministic validation for run status transitions (created → running → completed|failed) and reject invalid transitions without altering database schema.

## SCOPE & FILE BOUNDARIES
Writable: src/pipeline/db.py, tests/pipeline/test_db_state.py  
Read-only: schema/**/*.sql  
Out of Scope: All other files.

## ENVIRONMENT & PRECONDITIONS
Requires Python 3.11, pytest, flake8. If tests directory absent: create tests/pipeline/test_db_state.py skeleton then proceed.

## TARGET ARTIFACTS & ACCEPTANCE CRITERIA
(See artifacts front-matter block above for structured listing.)

## OPERATIONS SEQUENCE
(See operations_sequence block.)

## SLASH COMMAND PLAYBOOK
- Design: /architect with docstring and transition list.
- Implement functions: /code after /add.
- Inspect changes: /diff.
- Lint: /lint (after each code step).
- Test: /test pytest -q.
- Rollback scope violation: /undo.

## PROMPT TEMPLATES

Design Phase Prompt:
Implement only docstring & comment block enumerating transitions for src/pipeline/db.py.
Acceptance Criteria:
- Docstring lists allowed transitions: created→running→{completed|failed}.
- No logic change yet.
Constraints:
- Only edit src/pipeline/db.py.
Return summary of added lines.

Implementation Prompt (Validation):
Add validate_state_transition and integrate into update_run_status.
Acceptance:
- Raises ValueError on invalid transition.
- Pure function; no side effects.
Constraints:
- Only edit src/pipeline/db.py.
Return diff summary.

Test Prompt:
Add tests for valid & invalid transitions in tests/pipeline/test_db_state.py.
Validate:
- Both tests pass.
Constraints:
- Only edit tests/pipeline/test_db_state.py.
Return list of test names.

## SAFETY & GUARDRAILS
Abort if outside file set; perform /undo and restate constraints if stray edits detected.

## DETERMINISM & REPRODUCIBILITY
No randomness, time, or external IO. Identical inputs yield identical results.

## TEST & VALIDATION MATRIX
Criterion | Command | Artifacts | Failure Handling
--------- | ------- | --------- | ---------------
Valid transitions accepted | pytest -q | db.py, test_db_state.py | Patch logic in validate_state_transition
Invalid transitions rejected | pytest -q | db.py, test_db_state.py | Add/revise ValueError raise
Lint clean | flake8 | db.py, tests | Run /lint then minimal fix

## COMPLETION CHECKLIST
(See front-matter block.)

## APPENDIX
Crosswalk: ROLE→Objective, GOALS→Acceptance, EXECUTION PLAN→Operations Sequence.

````

---

## 3. Example Original Codex/Claude Prompt (Variant B – Multi-Artifact)

Original:

```
PHASE: PH-03
ROLE: Data pipeline architect.
CONTEXT: Need a tool adapter layer storing tool run metadata.
GOALS:
Create src/pipeline/tools.py with:
- Dataclass ToolResult(fields: tool_id, command_line, exit_code, stdout, stderr, timed_out, started_at, completed_at, duration_sec, success)
- Functions: load_tool_profiles(), get_tool_profile(), render_command(tool_profile, args), run_tool(tool_profile, args)
Add tests in tests/pipeline/test_tools.py for run_tool happy path & timeout.
Constraints: No network calls; only stdlib.
ACCEPTANCE:
All tests pass; lint clean; deterministic outputs (strip trailing whitespace).
PLAN:
1. Draft dataclass & stub functions.
2. Implement run_tool with timeout.
3. Add tests.
4. Refine error handling.
5. Finalize.
```

---

## Converted Workstream (Variant B)

````markdown name=ws-ph03-tool-adapter.md
---
workstream_id: "ws-ph03-tool-adapter"
phase: "PH-03"
title: "Implement tool adapter layer and execution metadata"
description: "Create tool adapter with ToolResult dataclass and execution helpers ensuring deterministic behavior."
difficulty: "medium"
version_target: "v1.0"
depends_on: []
owners: ["DICKY1987"]
tags: ["phase:PH-03", "component:tools"]
writable_globs:
  - "src/pipeline/tools.py"
  - "tests/pipeline/test_tools.py"
readonly_globs:
  - "requirements/**/*.txt"
out_of_scope_globs:
  - "src/pipeline/db.py"
abort_on_missing_dependencies: false
environment:
  os: "linux"
  languages: { python: "3.11" }
  tools: ["pytest", "flake8"]
preconditions:
  tests_available: false
test_command: "pytest -q"
lint_command: "flake8"
format_command: ""
commit_convention: "conventional"
commit_scope: "ws-ph03-tool-adapter"
determinism:
  stable_sorting: true
  timestamps: "isolate"      # stamp allowed only in fields; logic deterministic
  randomness: "forbid"
guardrails:
  scope_violation_action: "/undo then restate constraints"
  rollback_triggers:
    - "tests fail"
    - "lint introduces new errors"
    - "diff includes out-of-scope file"
artifacts:
  - path: "src/pipeline/tools.py"
    type: "code"
    must_provide:
      - "dataclass: ToolResult(tool_id, command_line, exit_code, stdout, stderr, timed_out, started_at, completed_at, duration_sec, success)"
      - "function: load_tool_profiles()"
      - "function: get_tool_profile(tool_id)"
      - "function: render_command(tool_profile, args)"
      - "function: run_tool(tool_profile, args, timeout=30)"
    must_not:
      - "network calls"
      - "non-stdlib imports"
    acceptance:
      tests: ["tests/pipeline/test_tools.py::test_run_tool_success",
              "tests/pipeline/test_tools.py::test_run_tool_timeout"]
      lint: true
      commands: []
    determinism:
      - "stdout trimmed"
      - "duration_sec computed as float seconds"
  - path: "tests/pipeline/test_tools.py"
    type: "test"
    must_provide:
      - "test_run_tool_success"
      - "test_run_tool_timeout"
    must_not:
      - "sleep > 1s"
    acceptance:
      tests: ["tests/pipeline/test_tools.py::test_run_tool_success",
              "tests/pipeline/test_tools.py::test_run_tool_timeout"]
operations_sequence:
  - id: 1
    intent: "Design dataclass & function signatures"
    files_add: ["src/pipeline/tools.py"]
    command: "/architect"
    expected_diff_summary: "Adds ToolResult skeleton & function stubs"
    commit_message: "docs(ws-ph03-tool-adapter): add adapter skeleton"
  - id: 2
    intent: "Implement load/get/render helpers"
    files_add: ["src/pipeline/tools.py"]
    command: "/code"
    expected_diff_summary: "Adds concrete logic for profile retrieval & command rendering"
    commit_message: "feat(ws-ph03-tool-adapter): implement profile helpers"
  - id: 3
    intent: "Implement run_tool with timeout and metadata collection"
    files_add: ["src/pipeline/tools.py"]
    command: "/code"
    expected_diff_summary: "Captures stdout/stderr, exit_code, timing, sets success"
    commit_message: "feat(ws-ph03-tool-adapter): add run_tool execution"
  - id: 4
    intent: "Add tests for success & timeout cases"
    files_add: ["tests/pipeline/test_tools.py"]
    command: "/code"
    expected_diff_summary: "Introduces test_run_tool_success, test_run_tool_timeout"
    commit_message: "test(ws-ph03-tool-adapter): add tool adapter tests"
  - id: 5
    intent: "Refine error handling (edge cases) & trim output"
    files_add: ["src/pipeline/tools.py"]
    command: "/code"
    expected_diff_summary: "Ensures stdout trimmed, ValueError on missing profile"
    commit_message: "refactor(ws-ph03-tool-adapter): finalize adapter robustness"
  - id: 6
    intent: "Validate tests & lint"
    files_add: []
    command: "/test pytest -q"
    expected_diff_summary: "No file changes"
    commit_message: "chore(ws-ph03-tool-adapter): confirm passing tests"
completion_checklist:
  - "[ ] ToolResult dataclass implemented"
  - "[ ] Helper functions implemented"
  - "[ ] run_tool handles timeout & success"
  - "[ ] Tests added & pass"
  - "[ ] Lint passes"
  - "[ ] Deterministic output trimming"
  - "[ ] No out-of-scope edits"
---

## ROLE & OBJECTIVE
Provide a tool adapter layer capturing execution metadata via ToolResult and helper functions.

## TARGET ARTIFACTS & ACCEPTANCE CRITERIA
(See front-matter artifacts block.)

## PROMPT TEMPLATES

Design:
Design skeleton for ToolResult and stub functions in src/pipeline/tools.py.
Acceptance:
- Dataclass fields enumerated.
- Only stubs; no logic yet.
Constraints:
- Only edit src/pipeline/tools.py.

Implementation (run_tool):
Implement run_tool capturing start time, completion time, exit code, stdout/stderr trimmed, success flag (exit_code==0), timeout kill after provided seconds.
Constraints:
- Stdlib only.
- Only edit src/pipeline/tools.py.

Test:
Add tests: test_run_tool_success (echo command) and test_run_tool_timeout (force timeout).
Constraints:
- Only edit tests/pipeline/test_tools.py.

## SAFETY & GUARDRAILS
If non-stdlib import appears: rollback with /undo. No network calls permitted.

## DETERMINISM
Trim trailing newline from stdout/stderr. Duration computed as completion-start in seconds.

## COMPLETION CHECKLIST
(See front-matter.)

````

---

## 4. Python Conversion Script (Heuristic)

```python name=convert_codex_to_aider.py
import re
import textwrap
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class RawPrompt:
    text: str

@dataclass
class ConvertedWorkstream:
    front_matter: Dict
    body_sections: Dict[str, str]

PHASE_PATTERN = re.compile(r'PHASE:\s*(PH-\d+)', re.I)
ROLE_PATTERN = re.compile(r'ROLE:\s*(.+)', re.I)
GOALS_PATTERN = re.compile(r'GOALS:\s*(.+?)(?=\n[A-Z ]{3,}:|$)', re.I | re.S)
CONTEXT_PATTERN = re.compile(r'CONTEXT|OPERATING CONTEXT:\s*(.+?)(?=\n[A-Z ]{3,}:|$)', re.I | re.S)
ACCEPT_PATTERN = re.compile(r'ACCEPTANCE:\s*(.+?)(?=\n[A-Z ]{3,}:|$)', re.I | re.S)
PLAN_PATTERN = re.compile(r'(EXECUTION PLAN|PLAN):\s*(.+?)(?=\n[A-Z ]{3,}:|$)', re.I | re.S)

FUNC_HINT = re.compile(r'\b(functions?|helper[s]?)\b.*?:\s*(.+)', re.I)
DATACLASS_HINT = re.compile(r'\bdataclass\b.*?:\s*(.+)', re.I)
TEST_HINT = re.compile(r'\btests?\b.*?:\s*(.+)', re.I)

def extract(pattern, text):
    m = pattern.search(text)
    return m.group(1).strip() if m else ""

def split_list_block(raw):
    # Split bullet-like lines
    lines = [l.strip('-* ') for l in raw.splitlines() if l.strip()]
    return [l for l in lines if l]

def infer_functions(goals_section: str) -> List[str]:
    funcs = []
    fm = FUNC_HINT.search(goals_section)
    if fm:
        for part in re.split(r'[,\n]', fm.group(1)):
            p = part.strip()
            if '(' in p and ')' in p:
                name = p.split('(')[0].strip()
                funcs.append(f"function: {name}")
    # Additional parse from lines
    for line in goals_section.splitlines():
        if 'function' in line.lower():
            bits = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)\(', line)
            for b in bits:
                funcs.append(f"function: {b}")
    return sorted(set(funcs))

def infer_dataclass(goals_section: str) -> Optional[str]:
    dm = DATACLASS_HINT.search(goals_section)
    if dm:
        return dm.group(1).strip()
    return None

def infer_tests(accept_section: str) -> List[str]:
    tests = []
    for line in accept_section.splitlines():
        if 'test_' in line:
            for t in re.findall(r'(test_[a-zA-Z0-9_]+)', line):
                tests.append(t)
    return sorted(set(tests))

def convert(raw: RawPrompt, workstream_id: str, title_hint: str) -> ConvertedWorkstream:
    text = raw.text
    phase = extract(PHASE_PATTERN, text) or "PH-XX"
    role = extract(ROLE_PATTERN, text)
    context = extract(CONTEXT_PATTERN, text)
    goals = extract(GOALS_PATTERN, text)
    acceptance = extract(ACCEPT_PATTERN, text)
    plan = extract(PLAN_PATTERN, text)

    functions = infer_functions(goals)
    dataclass_def = infer_dataclass(goals)
    tests = infer_tests(acceptance)

    front_matter = {
        "workstream_id": workstream_id,
        "phase": phase,
        "title": title_hint,
        "description": (goals.splitlines()[0][:120] if goals else "").strip(),
        "difficulty": "medium",
        "version_target": "v1.0",
        "depends_on": [],
        "owners": ["DICKY1987"],
        "tags": [f"phase:{phase}"],
        "writable_globs": ["src/pipeline/db.py", "tests/pipeline/test_db_state.py"],
        "readonly_globs": ["schema/**/*.sql"],
        "out_of_scope_globs": [],
        "abort_on_missing_dependencies": True,
        "environment": {
            "os": "linux",
            "languages": {"python": "3.11"},
            "tools": ["pytest", "flake8"]
        },
        "preconditions": {"tests_available": True, "migrations_required": False},
        "test_command": "pytest -q",
        "lint_command": "flake8",
        "format_command": "",
        "commit_convention": "conventional",
        "commit_scope": workstream_id,
        "determinism": {"stable_sorting": True, "timestamps": "forbid", "randomness": "forbid"},
        "guardrails": {
            "scope_violation_action": "/undo then restate constraints",
            "rollback_triggers": ["tests fail", "lint introduces new errors", "diff includes out-of-scope file"]
        },
        "artifacts": [
            {
                "path": "src/pipeline/db.py",
                "type": "code",
                "must_provide": ([f"dataclass: {dataclass_def}"] if dataclass_def else []) + functions,
                "must_not": ["modify schema"],
                "acceptance": {
                    "tests": [f"tests/pipeline/test_db_state.py::{t}" for t in tests],
                    "lint": True,
                    "commands": []
                },
                "determinism": ["pure logic"]
            }
        ],
        "operations_sequence": [],
        "completion_checklist": []
    }

    # Build operations from plan lines
    plan_steps = split_list_block(plan)
    for i, step in enumerate(plan_steps, start=1):
        front_matter["operations_sequence"].append({
            "id": i,
            "intent": step[:80],
            "files_add": ["src/pipeline/db.py"],
            "command": "/code" if "implement" in step.lower() else "/architect",
            "expected_diff_summary": f"{step[:60]}",
            "commit_message": f"feat({workstream_id}): {step[:50].lower()}"
        })

    # Checklist
    if dataclass_def:
        front_matter["completion_checklist"].append(f"[ ] Dataclass implemented: {dataclass_def}")
    for f in functions:
        name = f.replace("function: ", "")
        front_matter["completion_checklist"].append(f"[ ] Function implemented: {name}")
    for t in tests:
        front_matter["completion_checklist"].append(f"[ ] Test passes: {t}")
    front_matter["completion_checklist"].extend([
        "[ ] Lint passes",
        "[ ] No out-of-scope changes"
    ])

    body_sections = {
        "ROLE & OBJECTIVE": role or "",
        "OPERATING CONTEXT": context or "",
        "GOALS RAW": goals or "",
        "ACCEPTANCE RAW": acceptance or "",
        "PLAN RAW": plan or ""
    }

    return ConvertedWorkstream(front_matter=front_matter, body_sections=body_sections)

def emit_markdown(ws: ConvertedWorkstream) -> str:
    import yaml
    fm_yaml = yaml.safe_dump(ws.front_matter, sort_keys=False)
    body_parts = []
    for k, v in ws.body_sections.items():
        body_parts.append(f"## {k}\n\n{v}\n")
    return f"---\n{fm_yaml}---\n\n" + "\n".join(body_parts)

# Example usage
if __name__ == "__main__":
    raw_text = """
PHASE: PH-02
ROLE: Senior backend engineer.
OPERATING CONTEXT: Work on db.py; no schema changes.
GOALS:
- Add validate_state_transition(old_state, new_state) -> bool
- Integrate with update_run_status
- Provide dataclass: RunAudit(fields: run_id, old_state, new_state, ts)
ACCEPTANCE:
Tests: test_valid_transitions, test_invalid_transitions
PLAN:
1. Sketch transitions
2. Implement validation
3. Integrate
4. Add tests
5. Final check
"""
    ws = convert(RawPrompt(raw_text), "ws-ph02-state-machine", "Enforce state transitions")
    print(emit_markdown(ws))
```

---

## 5. Mapping & Heuristics Table

| Codex/Claude Element | Detection Heuristic | Output Placement |
|----------------------|---------------------|------------------|
| PHASE                | Regex PHASE: PH-\d+ | front_matter.phase |
| ROLE                 | ROLE: line          | Body section ROLE & OBJECTIVE |
| OPERATING CONTEXT    | OPERATING CONTEXT:  | Body section OPERATING CONTEXT |
| GOALS bullets        | After GOALS: block  | front_matter.artifacts.must_provide (functions/dataclasses) |
| Dataclass definition | “dataclass” keyword | artifacts.must_provide (prefixed) |
| Function signatures  | Lines with name(    | artifacts.must_provide |
| Tests                | Lines with test_    | artifacts.acceptance.tests + checklist |
| Acceptance block     | ACCEPTANCE:         | Body section + test extraction |
| Plan steps           | EXECUTION PLAN / PLAN | operations_sequence (intent per step) |
| Constraints (schema) | “No schema” phrase  | artifacts.must_not |
| Determinism cues     | “deterministic/timeout/random” | front_matter.determinism adjustments |

---

## 6. Extending Automation

Potential improvements:
- NLP classification for differentiating “must_not” (negatives) vs “must_provide”.
- Add semantic grouping (data vs behavior).
- Auto-infer writable_globs from file path mentions.
- Version bump integration: scan for “vX.Y”.
- Generate /architect vs /code decision using verbs (design/spec vs implement/refine/test).

---

## 7. Usage Workflow

1. Feed raw Codex/Claude prompt text to converter.
2. Review emitted front-matter; manually adjust owners/tags/scopes.
3. Insert into repository as ws-*.md file.
4. Use with Aider session: /read-only ws-*.md then execute operations_sequence.

---

## 8. Quick Quality Checklist for Converted Output

Before adoption:
- Functions listed are complete & correct.
- Dataclass fields accurately captured.
- Tests enumerated exist or will be created.
- No stray out-of-scope paths.
- Commit messages carry workstream_id.

---

If you provide additional raw Codex/Claude prompt samples, I can run them through a more tailored transformation logic or refine the script for edge cases.

Let me know if you’d like:
- A version that outputs JSON instead of Markdown.
- Integration with a validation schema.
- A GitHub Action snippet to auto-convert new prompts.

Feel free to paste a real prompt next for live conversion.