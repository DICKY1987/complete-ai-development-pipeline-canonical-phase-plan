
---

## 1. Aider-tuned WORKSTREAM_V1.1 template

Key goals:

* Make it crystal clear how **files** are passed to Aider (via CLI args, not `/add` in the prompt).
* Phrase diff / change expectations in a way that fits **Aider’s patching behavior**.
* Still keep it usable by *other* tools if needed (so no Aider-only slash commands).

```text
=== WORKSTREAM_AIDER_V1.1 ===

[HEADER]
WORKSTREAM_ID: {{workstream_id}}
CALLING_APP: {{source_app}}          # e.g. codex-cli, claude-code, router
TARGET_APP: aider
REPO_ROOT: {{repo_path}}
ENTRY_FILES: {{primary_files_or_globs}}   # Files passed to Aider CLI as initial context

ROLE: {{persona_line}}                # e.g. "Senior Python engineer and careful refactoring assistant."

CLASSIFICATION: complexity={{simple|moderate|complex|enterprise}}; quality={{standard|production}}; domain={{code|docs|analysis}}

[OBJECTIVE]
{{1–3 sentences describing the exact goal and what success looks like.}}

[CONTEXT]
- Project: {{project_name_or_subsystem}}
- Current state: {{short description of existing behavior or structure}}
- Why this workstream: {{reason / triggering change request}}
- Relevant architecture or constraints: {{e.g. layered architecture, key patterns}}
- Related tickets or docs: {{optional short IDs or links}}

[FILE_SCOPE]
- Files in ENTRY_FILES are already available to you and are the primary focus:
  - {{list or summarize key files in ENTRY_FILES}}
- You may reference other files conceptually, but do not assume they are loaded.
- If you need additional files beyond ENTRY_FILES, mention them explicitly in NEXT_STEPS.

[CONSTRAINTS]
- Must:
  - Keep changes minimal and scoped to this workstream’s objective.
  - Preserve existing behavior unless the change is explicitly requested.
  - Follow existing code style and patterns in this repository.
- Must NOT:
  - Introduce new external dependencies unless clearly justified.
  - Perform large rewrites that are not anchored to the stated objective.
- Safety:
  - Prefer small, composable edits over broad restructuring.
  - If you see a risky change, call it out and suggest safer alternatives.

[TASK_BREAKDOWN]
- Main task type: {{refactor|implement_feature|write_tests|analysis|docs}}
- Suggested steps:
  1) {{step 1}}
  2) {{step 2}}
  3) {{step 3}}
- Focus areas:
  - {{functions, classes, modules, or behaviors to prioritize}}

[REASONING_MODE]
- Mode: {{step_by_step|concise}}
- If step_by_step: briefly outline your plan first, then apply it.
- Keep reasoning compact and focused on decisions that affect the code.

[OUTPUT_FORMAT]
- Primary format: markdown
- Required sections in the final answer (in this order):

CHANGES_SUMMARY:
- Bullet list summarizing what you changed and why.
- Mention which files changed.

IMPLEMENTATION_NOTES:
- Short explanation of important design or refactoring decisions.
- Point out any non-obvious tradeoffs or constraints.

RISK_CHECKS:
- Potential risks or edge cases introduced or exposed by these changes.
- Any assumptions you made that should be verified.

NEXT_STEPS:
- Additional files that should be loaded or inspected in future workstreams.
- Follow-up tasks, tests, or cleanup you recommend.

- When showing code, prefer minimal focused snippets or short unified diff blocks
  that clearly illustrate the key changes.

[VALIDATION]
- Before final answer, self-check that:
  - [ ] Changes you describe match the stated OBJECTIVE.
  - [ ] You respected the constraints in [CONSTRAINTS].
  - [ ] There are no obvious syntax or structural errors in changed files.
- If you detect blocking ambiguity or missing context, STOP and output only:
  "CLARIFICATION_NEEDED: {{your concise questions}}"

[AIDER_EXECUTION_HINTS]
- Assume ENTRY_FILES were passed to Aider via CLI; you do not need to run /add
  on them in the chat.
- If additional files are important, list them under NEXT_STEPS rather than
  assuming they are already loaded.
- Avoid prompting for interactive user input; treat this as a headless run.

[EXECUTION_NOTES_FOR_ROUTER]
- Preferred timeout_seconds: {{default_for_this_class}}
- Retry_on_failure: {{true|false}}
- Escalation_hint: if Aider cannot reasonably complete this, suggest a follow-up
  workstream for a more powerful or broader-context tool (e.g. claude-code).

=== END_WORKSTREAM_AIDER_V1.1 ===
```

Notes:

* Everything is still **plain text**; if some other tool receives it, it will still understand `[HEADER]`, `[OBJECTIVE]`, etc.
* The only Aider-specific bit is `[AIDER_EXECUTION_HINTS]`, which other tools can harmlessly ignore.

---

## 2. Codex-CLI–tuned WORKSTREAM_V1.1 template

Goals:

* Assume Codex CLI is running in a **TUI / non-interactive mode** where it edits files on disk.
* Nudge Codex to produce **clear diff-like descriptions** and minimal necessary code snippets.
* Keep it safe for other tools if it gets routed elsewhere.

```text
=== WORKSTREAM_CODEX_V1.1 ===

[HEADER]
WORKSTREAM_ID: {{workstream_id}}
CALLING_APP: {{source_app}}           # e.g. router, claude-code, aider
TARGET_APP: codex-cli
REPO_ROOT: {{repo_path}}
ENTRY_FILES: {{primary_files_or_globs}}   # Files most relevant to this workstream

ROLE: {{persona_line}}                 # e.g. "Senior Python backend engineer and refactoring specialist."

CLASSIFICATION: complexity={{simple|moderate|complex|enterprise}}; quality={{standard|production}}; domain={{code|docs|analysis}}

[OBJECTIVE]
{{Clear description of what Codex should achieve and how success will be evaluated.}}

[CONTEXT]
- Project: {{project_name_or_subsystem}}
- Current state: {{short description of existing implementation or pain point}}
- Why this workstream: {{triggering feature request, bug, or refactor initiative}}
- Important invariants: {{things that must not change, e.g. public API, behavior, SLAs}}
- Related tickets or specs: {{optional IDs / short labels}}

[FILE_SCOPE]
- Primary focus files (should be examined and updated as needed):
  - {{list key files from ENTRY_FILES}}
- Other files may be consulted if relevant, but avoid expanding the change
  surface beyond what is necessary to satisfy the OBJECTIVE.
- If you believe more files must be touched, clearly justify this in RISK_CHECKS
  and NEXT_STEPS.

[CONSTRAINTS]
- Must:
  - Keep changes aligned with the OBJECTIVE and scoped to this workstream.
  - Maintain existing tests and behavior unless required to change.
  - Follow repository coding standards and patterns.
- Must NOT:
  - Introduce breaking changes to public interfaces unless explicitly requested.
  - Add new external libraries without explicit justification.
- Safety:
  - Prefer incremental refactors to big-bang rewrites.
  - Call out any behavior changes explicitly in CHANGES_SUMMARY.

[TASK_BREAKDOWN]
- Main task type: {{refactor|implement_feature|write_tests|analysis|docs}}
- Suggested steps:
  1) Inspect current implementation in the key files.
  2) Plan a minimal change set that meets the OBJECTIVE.
  3) Apply changes with clear, localized edits.
- Focus areas:
  - {{specific functions, classes, modules, or behaviors}}

[REASONING_MODE]
- Mode: {{step_by_step|concise}}
- If step_by_step: list the key modifications you will make before editing.
- Keep reasoning anchored in the actual code and OBJECTIVE.

[OUTPUT_FORMAT]
- Primary format: markdown
- Required sections in the final answer (in this order):

CHANGES_SUMMARY:
- Bullet list summarizing changes and the files they apply to.
- Explicitly mention any behavior changes or new edge cases.

IMPLEMENTATION_NOTES:
- Short explanation of design and refactoring decisions.
- Mention any non-trivial patterns or tradeoffs.

RISK_CHECKS:
- Potential risks, regressions, or assumptions that should be tested.
- Note if any areas feel under-tested or fragile.

NEXT_STEPS:
- Additional tests, cleanup, or refactors you recommend.
- Any further files or modules that should be addressed later.

- When showing code:
  - Prefer minimal, focused snippets that clearly show changed sections.
  - If needed, you may use short unified diff-style blocks to clarify changes.

[VALIDATION]
- Before final answer, self-check that:
  - [ ] The proposed changes align with the OBJECTIVE.
  - [ ] All CONSTRAINTS are respected.
  - [ ] There are no obvious syntax errors in changed files.
- If you cannot safely complete the task with the current context, output:
  "CLARIFICATION_NEEDED: {{your concise questions}}"

[CODEX_EXECUTION_HINTS]
- Assume you are editing files directly in the REPO_ROOT on disk.
- Keep edits as small and targeted as possible to minimize merge conflicts.
- Avoid making speculative changes outside the scope of this workstream.
- Do not request interactive user input; treat this as a headless run.

[EXECUTION_NOTES_FOR_ROUTER]
- Preferred timeout_seconds: {{default_for_this_class}}
- Retry_on_failure: {{true|false}}
- Escalation_hint: if Codex cannot complete this due to context or complexity,
  suggest a follow-up workstream for a broader-context tool (e.g. claude-code).

=== END_WORKSTREAM_CODEX_V1.1 ===
```

Again, all section names and most semantics are **shared with the Aider template**. Only the tool hint block and a few phrasing details differ.

---

## 3. Universal vs per-tool: where you can share vs customize

**Shared / universal parts** (you can keep 1 implementation in the renderer):

* `[HEADER]` (except `TARGET_APP` value)
* `ROLE`, `CLASSIFICATION`
* `[OBJECTIVE]`
* `[CONTEXT]`
* `[FILE_SCOPE]` semantics
* `[CONSTRAINTS]`
* `[TASK_BREAKDOWN]`
* `[REASONING_MODE]`
* `[OUTPUT_FORMAT]` section names (CHANGES_SUMMARY, IMPLEMENTATION_NOTES, RISK_CHECKS, NEXT_STEPS)
* `[VALIDATION]`
* `[EXECUTION_NOTES_FOR_ROUTER]`

These can be rendered from the same logic and just filled with bundle data.

**Tool-specific parts** (worth branching on `target_app`):

* The top marker and footer (e.g. `=== WORKSTREAM_AIDER_V1.1 ===` vs `CODEX`).
* The wording inside:

  * `[FILE_SCOPE]` (for Aider we stress “ENTRY_FILES are already added to the chat”).
  * `[OUTPUT_FORMAT]` (for Aider we mention “minimal diffs”; for Codex we talk about “editing files on disk”).
* The `[AIDER_EXECUTION_HINTS]` vs `[CODEX_EXECUTION_HINTS]` sections.

In code, that can just be a small conditional block:

```python
if target_app == "aider":
    emit_aider_hints(...)
elif target_app == "codex-cli":
    emit_codex_hints(...)
else:
    emit_generic_hints(...)
```

Everything else can be shared.

---

If you’d like, I can next:

* Show a patched version of `render_workstream_prompt.py` with a `--target-app aider|codex-cli|generic` flag, so it emits the correct variant automatically from the same bundle JSON.
