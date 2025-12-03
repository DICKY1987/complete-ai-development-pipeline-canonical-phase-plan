---
doc_id: DOC-GUIDE-HOW-TO-OPTIMIZED-FOR-MACHINE-READABILITY-437
## 1. Is this version optimized for machine readability?

**Content-wise: yes. Structure-wise: partially.**

What’s already good for machines:

* Stable, explicit headings: “Universal Phase Specification”, “Operator Execution Standard”, etc.
* Strong modal verbs: “MUST”, “FORBIDDEN” – easy to detect with regex.
* Clear required fields: `phase_id`, `workstream_id`, `file_scope.create/modify/read_only`, `acceptance`, Pre-Flight, etc.
* Lots of enumerated rules that can be mapped to checks.

What’s *not* fully optimized yet:

* It’s still primarily **Markdown prose**, not a **formal schema**.

  * A machine has to *parse* the text to infer:
    *“Oh, `phase_id` is required; `file_scope` must have these keys; acceptance tests must exist”*.
* There’s no single “source-of-truth object” like:

  * `PhaseSpec` JSON schema
  * `ExecutionRequest` JSON schema
  * `GuardrailChecklist` structure

So: the doc is **great as a human-readable spec and as a reference for an AI “brain”**, but for *hard* enforcement you want:

* A **canonical schema (JSON/YAML)** that encodes the rules.
* **Validators** that check an execution prompt against that schema **before** it hits a coding tool.

---

## 2. How to ensure checks/validation are included in execution prompts

Think of this as a 3-layer system:

1. **Schema** (what’s required)
2. **Validator** (enforce that it’s present)
3. **Prompt template** (how it’s presented to the model)

### 2.1. Define a strict “Execution Request” schema internally

You don’t need to create the file right now, just conceptualize it:

* `phase_spec` (with `phase_id`, `workstream_id`, `objective`, `file_scope`, `acceptance`, `depends_on`, etc.)
* `repo_context` (path, branch, worktree ID)
* `tooling` (which CLI/AI tools are allowed)
* `guardrails` (which rules are active)

Your orchestrator or wrapper code should **always** build a structured object like this first.

Then **all execution prompts come from this object**, never free-typed.

### 2.2. Run a validator before any AI execution

Before you generate the natural-language prompt for Aider/Codex/Claude:

* Pass the `ExecutionRequest` object to a **validator** that checks:

  * Required keys present (`phase_id`, `workstream_id`, `file_scope`, `acceptance`).
  * `file_scope` has `create/modify/read_only`.
  * There is at least one acceptance command.
  * There is some dependency information (or explicitly empty for Phase 0).
  * Phase type makes sense (no `implementation` phase with zero tests, etc.).

If validation fails:

* **Do not** send any execution prompt to the coding tool.
* Return a deterministic error (e.g., `EXECUTION_REQUEST_INVALID: missing acceptance.tests.python[0].command`).

That’s how you make “missing elements” un-runnable by design.

### 2.3. Embed a *self-check block* inside the prompt itself

On top of external validation, you can make the AI self-enforce:

* At the top or bottom of your execution prompt, include a **checklist** like:

  > Before you run any commands, parse the PHASE_SPEC block.
  > If any of the following are missing, you MUST respond with `VALIDATION_ERROR` and do nothing else:
  >
  > * phase_id
  > * workstream_id
  > * file_scope.create and file_scope.modify
  > * at least one acceptance command
  > * Pre-Flight requirements

And define:

* A **fixed error format** the AI must use:

  * e.g., `{"status":"VALIDATION_ERROR","missing":["acceptance.tests.python"]}`.

So you get **two levels of enforcement**:

1. Orchestrator/validator: blocks bad requests before they hit the model.
2. Model self-check: refuses to act if the request somehow slipped through incomplete.

### 2.4. Use rigid delimiters in the prompt

To help the model parse reliably, always wrap the structured parts:

* `<PHASE_SPEC> … </PHASE_SPEC>`
* `<REPO_CONTEXT> … </REPO_CONTEXT>`
* `<ACCEPTANCE_TESTS> … </ACCEPTANCE_TESTS>`

That way:

* The AI can reliably say:
  *“I will parse the PHASE_SPEC block, confirm required keys, else emit VALIDATION_ERROR.”*

---

## 3. How to make AI reject execution instructions that are missing elements

You do this at **two levels**: system behavior + instruction contract.

### 3.1. System-level: the orchestrator refuses to call the coding tool

* Never call Aider/Codex/Gemini/Copilot directly from raw user text.
* Always:

  1. Convert user intent → `ExecutionRequest` object.
  2. Validate object against the schema.
  3. Only if valid → generate execution prompt → call the model/tool.

If the user gives you:

> “Just refactor the whole repo for better structure”

Your orchestrator:

* Fails to construct a valid `ExecutionRequest` (no `file_scope`, no `phase_id`, no `acceptance`).
* Returns a structured error and/or asks the user for **specific missing fields**.
* Does **not** proceed to code-generation.

### 3.2. Model-level: explicit “strict mode” instructions

In the system prompt (or model-internal “role” instructions), bake in:

* “You are in STRICT_MODE. You must first validate that the PHASE_SPEC is complete. If any required field is missing or invalid, respond with VALIDATION_ERROR and do not run any commands or propose code.”

Then the AI’s behavior contract becomes:

1. Step 1: validate `PHASE_SPEC`.
2. Step 2: if invalid → emit error and stop.
3. Step 3: if valid → follow Operator Execution Standard (pre-flight, run commands, self-heal, test, etc.).

If you consistently include this in every execution prompt, the model will **refuse** to proceed on incomplete instructions.

---

## 4. How the development process leading up to the final prompt should be structured

You basically want a **small pipeline** that “hardens” the work before any model sees it.

Think of it as **phases before Phase 0**:

### 4.1. Upstream process: from idea → valid ExecutionRequest

Roughly:

1. **User intent / requirements**

   * Free-form text: “I want to add a patch manager”, “I want to integrate CCPM into the pipeline”.
2. **Planning / scoping step**

   * A *planning agent* (or you) maps this into:

     * A specific `phase_id` (e.g., `PH-02`).
     * A `workstream_id`.
     * A tight `objective`.
     * Initial `file_scope`.
3. **Schema fill step**

   * Populate the `ExecutionRequest` with:

     * `phase_spec` (all required fields).
     * `repo_context` (root path, branch, worktree).
     * `tooling` (languages, AI tools, test runners).
     * `acceptance` (concrete CLI commands).
4. **Validation step**

   * Run the schema validator.
   * Fix missing pieces until the request is valid.

Only **after this** does the “real” execution prompt get generated.

### 4.2. Automatic prompt generation from the ExecutionRequest

The final prompt to the coding model should be generated by code, something like:

* `render_execution_prompt(ExecutionRequest)`

That renderer:

* Inserts `<PHASE_SPEC>`, `<REPO_CONTEXT>`, `<ACCEPTANCE_TESTS>` blocks.
* Embeds the Operator rules and strict-mode validation instructions.
* Avoids ad-hoc free-typing, so all prompts share the same shape.

### 4.3. Don’t let the final prompt be the first time constraints appear

The trap you want to avoid:

* Human writes a clever, long “execution prompt” by hand.
* It *mentions* some rules, maybe misses others.
* The model has to juggle too many things, with no external enforcement.

Instead, the **development process** should:

* Treat **the schema + validator** as the real “source of truth”.
* Treat the **prompt** as just a formatted view of a validated object.

So:

* You maintain the guard docs (like we have) as conceptual rules.
* You implement them in:

  * a schema (required fields), and
  * a validator (code).
* You always go:
  **Idea → Structured ExecutionRequest → Validated → Prompt → Model.**

---

## TL;DR

* The guard docs you have now are **semantically strong** and model-friendly, but **not yet a formal machine schema**.
* To enforce them in execution prompts:

  * Define a strict `ExecutionRequest` schema.
  * Validate every request before it becomes a prompt.
  * Embed a self-check / strict-mode block in the prompt so the AI rejects incomplete specs.
* The upstream dev process should be a pipeline:

  * requirements → scoped phase → filled schema → validation → auto-generated prompt → execution.

Do that, and you get a system where:

* Bad instructions literally **cannot** reach the coding agent, and
* Even if they do, the agent is trained to say “VALIDATION_ERROR: missing X” rather than trying to guess.
