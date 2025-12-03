In industry terms, what you’re describing is basically:

> **Schema-driven prompt templates for pattern-based execution**  

…or more loosely:

- **“Structured / schema-based prompt templates”**
- **“Spec-driven prompting”**
- **“Composable prompt blocks”** tied to patterns

There isn’t *one* universal name everyone uses, but if you say *“schema-driven prompt templates for tool / pattern invocation”* you’re speaking the same language as OpenSpec / LangChain / LangGraph / CCPM, etc.  

In **your** ecosystem, they slot perfectly as:

> **Pattern-bound Prompt Blocks**  
> (one block per `pattern_id` + template, indexed by `doc_id` + operation_kind)

---

## How to design this prompting style (best practices)

I’ll keep this opinionated and aligned with your existing pattern/template architecture.

### 1. Treat each “prompt block” as a first-class artifact

Each block = one reusable unit that can be slotted into a flow:

- 1 **execution pattern** (`pattern_id` in `PATTERN_INDEX.yaml`)  
- 1 **template** (phase template / execution template)  
- 1 **Prompt Block** = how you talk to the AI for this combo

**Give the block its own ID:**

- `doc_id` – your global join key across all docs (spec, schema, executor, prompt block)  
- `pattern_id` – which execution pattern it belongs to  
- `template_id` – which template it renders from (e.g., `module_creation_v1`)  

That lets you do precision editing and cross-file updates by ID, not by free text.

---

### 2. Use **JSON as the canonical format**, generate text prompts from it

Best practice: **store the block as JSON**, then render the human-readable prompt for Claude Code / Copilot / etc. from that.

Example “Prompt Block” for one pattern+template:

```json
{
  "doc_id": "DOC-PB-ATOMIC-CREATE-001",
  "pattern_id": "PAT-ATOMIC-CREATE-001",
  "template_id": "atomic_create_v1",
  "version": "1.0.0",
  "role": "prompt_block",
  "target_tool": "claude_code",

  "sections": {
    "meta": {
      "goal": "Create 1-3 implementation files plus tests using atomic_create pattern.",
      "when_to_use": "Small, isolated feature or helper module."
    },
    "context": {
      "project_profile_ref": "PROJECT_PROFILE.yaml",
      "codebase_index_ref": "CODEBASE_INDEX.yaml"
    },
    "inputs_schema": {
      "required": ["files_to_create", "project_root"],
      "optional": ["doc_id_prefix"]
    },
    "outputs_schema": {
      "description": "What the tool must return (JSON / patch / summary)."
    },
    "execution_pattern_ref": {
      "spec_path": "patterns/specs/atomic_create.pattern.yaml",
      "schema_path": "patterns/schemas/atomic_create.schema.json",
      "executor_path": "patterns/executors/atomic_create_executor.ps1"
    },
    "guardrails": {
      "must": [
        "Use only atomic_create pattern to create files.",
        "Do not create more than 3 files."
      ],
      "must_not": [
        "Do not modify any schema files.",
        "Do not change unrelated modules."
      ]
    },
    "prompt_template": {
      "claude_system": "You are executing the atomic_create pattern…",
      "claude_user": "Using PAT-ATOMIC-CREATE-001 and TEMPLATE atomic_create_v1, create the files listed in files_to_create…"
    }
  }
}
```

Then your CLI / orchestrator:

- Reads this JSON,
- Fills in variables (`files_to_create`, `project_root`, etc.),
- Renders the actual text prompt for the tool.

This is exactly the **template + execution pattern + registry** architecture you already have for patterns and templates, just applied to prompts.  

---

### 3. Make sections map cleanly to *operations*, not prose

You want blocks you can *compose*, so design sections around **what the machine needs**, not what a human likes to read:

Suggested core sections for **every** Prompt Block:

1. `meta` – goal, when to use, pattern/template references  
2. `context` – which files/configs to feed (e.g. CODEBASE_INDEX, ai_policies, quality gates)  
3. `inputs_schema` – what variables the orchestrator must provide  
4. `outputs_schema` – what structure the AI must return (JSON, patch, report ID)  
5. `execution_pattern_ref` – links into `PATTERN_INDEX.yaml` + executor/script path  
6. `guardrails` – MUST / MUST NOT rules specific to this block  
7. `prompt_template` – the *minimal* text template(s) for each tool (Claude, Copilot, etc.)

Anything that feels like “storytelling” goes in one field (e.g. `prompt_template.claude_user`). Everything else is structured.

---

### 4. Tie Prompt Blocks into your **registry layer**

Treat them like first-class citizens in the registry:

- Add a `prompt_blocks` section or a dedicated `PROMPT_BLOCK_INDEX.yaml` under `patterns/registry/` that points from `pattern_id` → one or more prompt blocks, just like you already do for specs/schemas/executors.  

Example:

```yaml
prompt_blocks:
  - doc_id: DOC-PB-ATOMIC-CREATE-001
    pattern_id: PAT-ATOMIC-CREATE-001
    template_id: atomic_create_v1
    target_tool: claude_code
    path: prompts/blocks/atomic_create.claude.json
  - doc_id: DOC-PB-ATOMIC-CREATE-002
    pattern_id: PAT-ATOMIC-CREATE-001
    template_id: atomic_create_v1
    target_tool: github_copilot_cli
    path: prompts/blocks/atomic_create.copilot.json
```

Now your orchestrator can:

1. Pick `pattern_id` from the plan,
2. Look up the right **Prompt Block** by `target_tool`,
3. Render & send the prompt automatically.

---

### 5. Design blocks to be **composable** in a DAG

You already think in terms of:

- **Templates** for phases / patterns  
- **Patterns** implementing `operation_kind`s (e.g. CREATE_FILE, RUN_TESTS)  

So for composition:

- Each Prompt Block should declare its **operation_kind(s)**:
  - e.g. `["CREATE_FILE", "SAVE_FILE"]` for atomic_create  
- And its **inputs/outputs** in a way that a planner can wire together:
  - Block A outputs `created_files`
  - Block B (RUN_TESTS) consumes `created_files` as context

That lets you build higher-level flows as pure data:

```json
[
  { "block_doc_id": "DOC-PB-ATOMIC-CREATE-001", "operation_kind": "CREATE_FILE" },
  { "block_doc_id": "DOC-PB-PYTEST-VERIFY-001", "operation_kind": "RUN_TESTS" }
]
```

Then the orchestrator just walks this list, loading each block and executing it—no ad-hoc prompts.

---

### 6. Evolve them like code, not like chat

Best practice in this style:

- **Version them** (`version: "1.1.0"`) and keep old versions for reproducibility.  
- **Test them**: for each block, keep 1–2 sample “input → output” test cases that you can rerun against a model to check it still behaves.  
- **Review them via diffs**: because they’re JSON, small edits are easy to diff/review.  
- **Keep one source of truth**: don’t hand-edit raw prompts; edit the JSON block and re-render.

This matches how your pattern system already works (spec + schema + executor + tests + index).  

---

### 7. How this lines up with “industry best practice”

You’re basically converging on the same ideas that:

- **OpenSpec** uses for “spec-driven AI coding” (spec as structured contract + templates that tools fill).  
- **Agent frameworks** (LangChain, LangGraph, etc.) call “prompt templates,” “chains,” or “nodes” – reusable blocks that get assembled into a DAG.  
- **OpenAI / tool-calling style**: JSON schemas + structured tool definitions, with minimal free text around them.

Your twist (which is good): you’re pairing them with **proven execution patterns** and your **registry layer** (doc_id + pattern_id + operation_kind + routing). That’s more rigorous than most people do.

---

If you’d like, I can next:

- Sketch a **canonical JSON schema** for `PromptBlock` (so you can drop `prompt_block.schema.json` under `patterns/schemas/` and validate every block),  
- Or take one existing pattern (like `atomic_create` or `worktree_lifecycle`) and draft the *actual* Prompt Block file you could save as `prompts/blocks/<name>.json`.