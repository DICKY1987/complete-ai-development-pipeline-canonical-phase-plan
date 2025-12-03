---
doc_id: DOC-GUIDE-ANTHROPIC-PROMPT-GUIDE-STRUCTURE-XML-435
---


---

## 1. What the attached references add

### a) Anthropic Prompt Guide → structure, XML-ish thinking, examples

Key ideas:

* Be explicit and detailed; spell out instructions, context, and success criteria.
* Use **tags/sections** (`<instructions>`, `<context>`, `<examples>`, `<thinking>`, `<answer>`) to separate concerns and make the response parseable/consistent.
* Use chain-of-thought / “think step-by-step” where complexity is high, NOT necessarily on every task.
* Provide 3–5 examples when behavior is subtle.

**Implication for your template:**
We *don’t* want full XML (for CLI universality), but we *do* want very clear, consistent sections that mirror those tags in plain ASCII (`[INSTRUCTIONS]`, `[CONTEXT]`, `[OUTPUT_FORMAT]`, `[REASONING]`).

---

### b) “High-Quality Prompts” & “Core of a Good Prompt” → 3C pattern & persona

They hammer the same triad repeatedly: **Clarity, Context, Constraints**.

* Clarity/specificity: say exactly what to do.
* Context: who is this for, why, what environment.
* Constraints: what to include / exclude, format, length, etc.
* Persona / role (“You are a senior X…”) is *very* effective.
* Few-shot and chain-of-thought are advanced knobs, not mandatory, but really help for tricky tasks.

**Implication for your template:**
We should make **3C + Persona** *first-class fields*:

* `ROLE:` or `[ROLE]`
* `OBJECTIVE:` (clarity)
* `[CONTEXT]`
* `[CONSTRAINTS]`

---

### c) Agentic AI refs (PRR prompt ref + agentic reference) → self-healing & workflow semantics

These two are overkill for a single prompt, but they give nice patterns for:

* Task analysis block with **classification** (complexity, domain, quality tier, time constraint).
* Explicit **output spec** and **validation gates** – contract for what “done” means.
* Self-healing loops with `max_iterations`, `confidence_threshold`, error detection & validation.
* Separation between:

  * Intake / analysis
  * Plan / reasoning
  * Execution
  * Validation / self-critique

**Implication for your template:**

* Add a tiny **classification mini-block** that routers and tools can use:

  * `COMPLEXITY: simple|moderate|complex|enterprise`
  * `QUALITY_TIER: standard|production`
* Add a **VALIDATION** section: what the tool should check before declaring success.
* Add an optional **SELF_REVIEW** line like: `SELF_CHECK: yes|no` with a one-liner of what to verify.

---

## 2. Concrete improvements to your universal workstream template

Your current “slim ASCII v1” template is already good on:

* having one canonical structure
* separating meta vs task vs context
* being pure text (universal for Aider, Codex, Claude, Copilot, Ollama Code, etc.)

What these docs suggest we add (still slim, still ASCII):

### (1) Make persona explicit

Add a **ROLE** field at the top:

```text
ROLE: Senior {language}/{domain} engineer and careful refactoring assistant.
```

This is cheap and helps *every* model immediately shift into the right mode.

---

### (2) Bake in the “3 Cs”

Instead of burying them, we give each its own section:

* `[OBJECTIVE]` – short, single sentence of what success is.
* `[CONTEXT]` – 3–7 lines: repo, subsystem, why now, constraints.
* `[CONSTRAINTS]` – bullets: what to obey / avoid (no breaking tests, no new deps, etc.).

---

### (3) Small classification block for router + models

Borrowing from PRR’s `<classification>` section, compress to one line:

```text
CLASSIFICATION: complexity={simple|moderate|complex|enterprise}; quality={standard|production}; domain={code|docs|analysis}
```

* Routers can use this for scheduling / timeouts.
* Models can use it to scale their effort (e.g., more reasoning for `complex+production`).

---

### (4) Output spec as a contract

Add a strict `[OUTPUT_FORMAT]` section:

* specify **format** (markdown, plain text, JSON)
* specify **sections** that must be present (e.g. `CHANGES_SUMMARY`, `PATCH_EXPLANATION`, `NOTES`)

Example:

```text
[OUTPUT_FORMAT]
- Primary format: markdown
- Required sections (in order):
  1) CHANGES_SUMMARY (bullet list)
  2) IMPLEMENTATION_NOTES (short prose)
  3) RISK_CHECKS (bullets)
```

---

### (5) Reasoning + self-check knobs, but still minimal

Instead of heavy XML, just:

```text
[REASONING_MODE]
- For this task: {step_by_step|concise}
- If step_by_step: list key steps before presenting final answer.
```

And a tiny validation:

```text
[VALIDATION]
- Before final answer, verify:
  - [ ] All constraints honoured
  - [ ] No syntax errors in changed files
  - [ ] Tests referenced in this prompt still pass conceptually
```

This lines up well with your self-healing error pipeline pattern and the agentic references.

---

### (6) Keep examples optional + lightweight

All the docs like 3–5 examples, but examples are token-heavy.

Recommendation:

* Add an optional `[EXAMPLE_TASKS]` section that’s usually either:

  * empty, or
  * 1–2 **very short** “good vs bad” micro examples.

That way you keep “slim by default” but have a place to inject few-shot when it really matters.

---

## 3. Revised “SLIM ASCII V1.1” universal workstream template

Here’s a **drop-in upgraded version** that applies everything above but stays:

* ASCII only
* single canonical structure
* safe for *any* AI CLI tool that just consumes text

You can literally have `render_workstream_prompt.py` emit this:

```text
=== WORKSTREAM_V1.1 ===

[HEADER]
WORKSTREAM_ID: {{workstream_id}}
CALLING_APP: {{source_app}}        # e.g. codex-cli, claude-code, aider, etc.
TARGET_APP: {{target_app}}        # e.g. aider, codex-cli, claude-code
REPO_ROOT: {{repo_path}}
ENTRY_FILES: {{primary_files_or_globs}}

ROLE: {{persona_line}}            # e.g. "Senior Python engineer and careful refactoring assistant."

CLASSIFICATION: complexity={{simple|moderate|complex|enterprise}}; quality={{standard|production}}; domain={{code|docs|analysis}}

[OBJECTIVE]
{{1–3 sentences, explicit & measurable goal}}

[CONTEXT]
- Project: {{project_name_or_subsystem}}
- Current state: {{short description of what exists today}}
- Why this workstream: {{reason / triggering event}}
- Relevant architecture/constraints: {{e.g. hexagonal, feature-flagged, no breaking changes}}
- Related tickets/links: {{optional}}

[CONSTRAINTS]
- Must:
  - {{bullet 1 – hard requirements}}
  - {{bullet 2}}
- Must NOT:
  - {{bullet 1 – prohibited behaviors (e.g., no new external deps)}}
  - {{bullet 2}}
- Safety:
  - Prefer minimal, well-scoped changes
  - Preserve existing behavior unless explicitly requested

[TASK_BREAKDOWN]
- Main task type: {{refactor|implement_feature|write_tests|analysis|docs}}
- Suggested steps:
  1) {{step 1}}
  2) {{step 2}}
  3) {{step 3}}
- Focus areas:
  - {{specific files/functions/modules}}

[REASONING_MODE]
- Mode: {{step_by_step|concise}}
- If step_by_step: briefly outline your plan, then apply it.

[OUTPUT_FORMAT]
- Primary format: {{markdown|plain_text|json}}
- Required sections in the final answer:
  1) CHANGES_SUMMARY
  2) IMPLEMENTATION_NOTES
  3) RISK_CHECKS
  4) NEXT_STEPS (if any)
- If code is shown, include only the minimal necessary snippets or unified diffs.

[VALIDATION]
- Before final answer, self-check that:
  - [ ] All constraints in [CONSTRAINTS] are satisfied.
  - [ ] The proposed changes are consistent with the [OBJECTIVE].
  - [ ] No obvious syntax or structural errors are present.
- If you detect blocking ambiguity, STOP and output only:
  "CLARIFICATION_NEEDED: {{your concise questions}}"

[EXAMPLE_TASKS]   # optional; usually empty
- Example_good:
  - Objective: "Refactor function X to remove duplication with Y while keeping behavior identical."
  - Constraints: "No new deps, keep public API unchanged."
- Example_bad:
  - "Rewrite the whole module from scratch" (too broad, violates minimal change principle).

[EXECUTION_NOTES_FOR_ROUTER]
- Preferred timeout_seconds: {{default_for_this_class}}
- Retry_on_failure: {{true|false}}
- Escalation_hint: if this tool cannot complete due to limits, recommend a follow-up workstream for {{more_powerful_app}}

=== END_WORKSTREAM_V1.1 ===
```

### Why this is still “universal”

* It’s **pure ASCII**: no XML, no JSON that any particular CLI has to parse.
* For Codex / Claude / Gemini / Copilot / Aider, it’s just a well-structured prompt with clearly labeled sections.
* For your router and logging layer, it’s *machine-friendly*:

  * you can regex the bracketed sections (`^\[CONTEXT\]` etc.)
  * you can parse `CLASSIFICATION:` and `EXECUTION_NOTES_FOR_ROUTER` into your task registry.

---

## 4. Direct answer to your question

> **Do these files offer information that can strengthen the prompt template?**

Yes, very much so. They validate your overall approach and push you to:

* Make **role/persona and 3C (clarity, context, constraints)** explicit.
* Add **classification + output contracts + validation hooks**, giving both the model and your router better guidance.
* Add a skinny but powerful **reasoning + self-check** layer that plays nicely with your error pipeline and agentic design.

