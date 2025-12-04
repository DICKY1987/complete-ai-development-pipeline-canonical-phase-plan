---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-WORKSTREAM-PROMPT-STRUCTURE-827
---

workstream-style” prompt structure_Aider_Ollama Code_OpenAI Codex_Claude Code
* **Aider** (with Ollama models via `aider --model ...`)
* **Ollama Code / ollama-code**([GitHub][1])
* **OpenAI Codex CLI**([OpenAI Cookbook][2])
* **Claude Code CLI**([Anthropic][3])

The trick is:

* keep it **short but structured**,
* include **explicit file scope + tasks + tests**,
* avoid tool-specific slash commands / config,
* let each tool’s own system prompt + AGENTS/contract do the heavy lifting.

Below is a vendor-neutral prompt template tuned to what those tools all like.

---

## Design principles (from the docs you asked about)

From **Aider** docs & examples:

* Works best when you **name the files**, keep tasks **small**, and specify **lint/tests** to run.([Aider][4])

From **Ollama Code** (qwen-code fork):

* It expects natural language instructions in a loop: “> Describe the architecture”, “> Refactor this function…”. No special syntax required.([GitHub][1])

From **Codex prompting & CLI guidance**:

* Provide **clear code pointers**, **verification steps**, and **split large tasks**. Keep instructions minimal but explicit.([OpenAI Developers][5])

From **Claude Code best practices**:

* Give a **clear goal**, ask for a **plan first**, request **tests**, and tell it to ask questions if anything is unclear.([Anthropic][3])

Those all happily accept a plain text prompt like:

> “Here is the goal, here are the files, here are the constraints, here’s how to report back.”

So we’ll build exactly that.

---

## Canonical “Workstream Prompt” (drop-in for all four tools)

You can treat this as your **per-workstream message file** for Aider, an initial instruction for Ollama Code, or the first user message for Codex/Claude Code.

```text
[ROLE]
You are a senior software engineer working in an existing codebase.
Follow the instructions below exactly. If anything is ambiguous, ask
clarifying questions before making risky changes.

[WORKSTREAM_META]
id: WS-<id-or-ulid>
goal: <one short sentence of the main outcome>
priority: <low|medium|high>

[REPO_CONTEXT]
tech_stack: <languages, frameworks, tools>
entry_points: <main scripts/services, if relevant>
related_docs:
- <path/to/AGENTS.md or operating contract, if any>
- <path/to/spec_or_design_doc.md, if relevant>

[FILE_SCOPE]
# Only touch these files unless explicitly told otherwise.
files_scope:
- <relative/path/to/file1>
- <relative/path/to/file2>
files_may_create:
- <relative/path/to/new_file1>
- <relative/path/to/new_file2>

[TASKS]
# Keep these as concrete, checkable steps.
1) <task 1 – what to change or add>
2) <task 2 – refactor / cleanup / rename>
3) <task 3 – update docs or config if needed>

[CONSTRAINTS]
- Keep changes minimal and coherent; prefer focused edits over rewrites.
- Preserve existing behavior unless a change is explicitly requested.
- Match existing style, patterns, and naming in this repo.
- Do not introduce new dependencies unless explicitly allowed.
- If you are unsure about a requirement, ask before proceeding.

[TESTS_AND_VALIDATION]
# What “done” looks like.
required_checks:
- <command or description, e.g. `pytest -q -k test_hello`>
- <lints or static checks, e.g. `ruff check src`>
acceptance_criteria:
- <bullet 1>
- <bullet 2>

[EXECUTION_GUIDANCE]
- First: skim the relevant files to build a mental model.
- Then: propose a short PLAN (3–7 bullet steps).
- Wait for confirmation if any part of the plan seems risky.
- After edits: run through the tests/checks above (conceptually or via tools if available).
- If tests would fail, explain why and how to fix them.

[OUTPUT_FORMAT]
When responding, follow exactly:

1) PLAN
   - Bullet list of steps you will take.
2) CHANGES
   - Explain what you changed and why.
   - Reference files like `path/to/file.py: line ranges` where possible.
3) TESTS
   - List which checks you ran (or would run) and the expected results.
4) NEXT_STEPS
   - Optional follow-ups or cleanups.

If you cannot safely complete the tasks, explain the blockers and propose
the smallest next step I should approve.
```

---

## How this maps to each tool

**Aider**

* You can store this as a **message file** and call:

  ```bash
  aider --message-file path/to/workstream_prompt.txt <files...>
  ```

* Aider already understands file scope from the CLI arguments, but repeating it in `[FILE_SCOPE]` is harmless and reinforces intent.

* Your *static* project rules (coding conventions, “never touch X”, etc.) go into `AGENTS.md` or a read-only doc added with `--read`, leaving this prompt focused on the specific workstream.([Aider][6])

**Ollama Code (ollama-code)**([GitHub][1])

* Start `ollama-code` in your repo, then paste the whole prompt as your first `>` message.
* It’s just text, so it doesn’t conflict with their own task planning logic.
* The `[OUTPUT_FORMAT]` section gives you consistent, parseable responses you can feed back into your pipeline.

**OpenAI Codex CLI**

* Use this as the **first message** in Agent mode or as the content of a task in your pipeline.
* It respects Codex guidance: clear code pointers (`[FILE_SCOPE]`), verification (`[TESTS_AND_VALIDATION]`), and small, explicit tasks (`[TASKS]`).([OpenAI Developers][5])
* Keep the text fairly short per workstream to stay within token limits and Codex’s “minimal extra instructions” recommendation.

**Claude Code CLI**

* Works well as the initial instruction after you run `claude` in the repo.
* It matches Claude Code best practices: clear role, explicit plan, tests, and an output format.([Anthropic][3])
* You can also mirror the same structure in `.claude/operating-contract.md` as a persistent project contract, then use only a slimmer per-task version at runtime.

---

## How to integrate with your existing pipeline

Given your repo already has **workstream bundles** with:

* `id`
* `files_scope`
* `files_create`
* `tasks`
* `acceptance_tests`

…you can generate this prompt automatically:

* Fill `[WORKSTREAM_META]` from `id` / metadata.
* Fill `[FILE_SCOPE]` from `files_scope` + `files_create`.
* Fill `[TASKS]` from `tasks`.
* Fill `[TESTS_AND_VALIDATION]` from `acceptance_tests` and any repo-level lint commands.

That gives you **one canonical prompt template** that:

* is friendly to **Aider** and **Ollama Code** (natural language, clear scope),
* is aligned with **Codex** and **Claude Code** best-practice guidance,
* and is easy to auto-generate from your workstream JSON.


Below is:

1. A **small “prompt renderer” design** wired to your existing `workstream.schema.json`.
2. A **ready-to-use Python script** (`render_workstream_prompt.py`) that turns each `ws-*.json` into a canonical prompt for Aider, Ollama Code, Codex, and Claude Code.
3. A few **usage examples per tool**.

---

## 1. Design: “Prompt Renderer” for Workstream Bundles

We’ll treat each workstream file (conforming to your existing schema) as the *single source of truth*, and render the canonical prompt structure you liked earlier.

### 1.1. Input: your existing schema

From `copy_workstream.schema.json` / `copy_example_single.json`, your fields are:

```json
{
  "id": "ws-hello-world",
  "openspec_change": "OS-001",
  "ccpm_issue": 1001,
  "gate": 1,
  "files_scope": ["src/hello/world.py"],
  "files_create": ["src/hello/world.py"],
  "tasks": ["Create a simple hello world module", "Add unit tests"],
  "acceptance_tests": ["pytest -q -k test_hello"],
  "depends_on": [],
  "tool": "aider",
  "circuit_breaker": {"max_attempts": 3, "max_error_repeats": 2},
  "metadata": {"owner": "dev@example.com"}
}
```

We’ll map them like this:

| JSON field                      | Prompt section                                     | Notes                          |
| ------------------------------- | -------------------------------------------------- | ------------------------------ |
| `id`                            | `[WORKSTREAM_META].id`                             | Used everywhere (`ws-…`)       |
| `openspec_change`               | `[WORKSTREAM_META].openspec_change`                | Nice trace to OpenSpec         |
| `ccpm_issue`                    | `[WORKSTREAM_META].ccpm_issue`                     | CCPM / GitHub mapping          |
| `gate`                          | `[WORKSTREAM_META].gate` + `priority`              | Simple gate→priority mapping   |
| `files_scope`                   | `[FILE_SCOPE].files_scope`                         | Only files to touch            |
| `files_create`                  | `[FILE_SCOPE].files_may_create`                    | New files agent may create     |
| `tasks[]`                       | `[TASKS]` numbered list                            | First task also used as `goal` |
| `acceptance_tests[]`            | `[TESTS_AND_VALIDATION].required_checks`           | Commands like `pytest …`       |
| `tool`                          | `[WORKSTREAM_META].tool_hint`                      | Which agent you *prefer*       |
| `metadata`                      | `[WORKSTREAM_META].metadata` + optional repo hints | e.g., owner, tech_stack, docs  |
| `depends_on`, `circuit_breaker` | Not in prompt body (or optional comments)          | Mostly orchestrator internal   |

Additional context (tech stack, entry points, global docs) can be either:

* pulled from `metadata` (`tech_stack`, `entry_points`, `docs` keys), **or**
* passed as CLI flags when rendering a specific prompt.

---

## 2. The renderer script: `render_workstream_prompt.py`

This script:

* Reads a single workstream JSON (conforming to your schema).
* Optionally takes `--tech-stack`, `--entry-point`, and `--doc` overrides.
* Emits the **canonical prompt** we designed earlier.
* Writes to a file (`-o`) or prints to stdout.

You can drop this into your repo (e.g. `tools/render_workstream_prompt.py`).

```python
#!/usr/bin/env python3
"""
render_workstream_prompt.py

Render a canonical workstream prompt (for Aider, Ollama Code, Codex, Claude Code)
from a JSON workstream bundle conforming to workstream.schema.json.
"""

import argparse
import json
from pathlib import Path

def gate_to_priority(gate: int | None) -> str:
    if gate is None:
        return "medium"
    if gate <= 0:
        return "low"
    if gate == 1:
        return "medium"
    return "high"

def render_prompt(
    ws: dict,
    tech_stack: str | None = None,
    entry_points: list[str] | None = None,
    extra_docs: list[str] | None = None,
) -> str:
    ws_id = ws.get("id", "<missing-id>")
    tasks = ws.get("tasks", [])
    files_scope = ws.get("files_scope", [])
    files_create = ws.get("files_create", [])
    acceptance_tests = ws.get("acceptance_tests", [])
    gate = ws.get("gate")
    metadata = ws.get("metadata", {}) or {}
    tool = ws.get("tool", "unspecified")

    goal = tasks[0] if tasks else f"Complete workstream {ws_id}"
    priority = gate_to_priority(gate)

    # Repo context (defaults from metadata, overridable via CLI)
    tech_stack = tech_stack or metadata.get("tech_stack", "<unspecified>")
    entry_points = entry_points or metadata.get("entry_points", [])
    extra_docs = extra_docs or metadata.get("docs", [])

    parts: list[str] = []

    # [ROLE]
    parts.append("[ROLE]")
    parts.append(
        "You are a senior software engineer working in an existing codebase.\n"
        "Follow the instructions below exactly. If anything is ambiguous, ask\n"
        "clarifying questions before making risky changes."
    )

    # [WORKSTREAM_META]
    parts.append("\n[WORKSTREAM_META]")
    parts.append(f"id: {ws_id}")
    parts.append(f"goal: {goal}")
    parts.append(f"priority: {priority}")
    parts.append(f"gate: {gate if gate is not None else '<unspecified>'}")
    parts.append(f"tool_hint: {tool}")
    if ws.get("openspec_change"):
        parts.append(f"openspec_change: {ws['openspec_change']}")
    if ws.get("ccpm_issue") is not None:
        parts.append(f"ccpm_issue: {ws['ccpm_issue']}")
    if metadata:
        parts.append("metadata:")
        for k, v in metadata.items():
            parts.append(f"  {k}: {v}")

    # [REPO_CONTEXT]
    parts.append("\n[REPO_CONTEXT]")
    parts.append(f"tech_stack: {tech_stack}")
    if entry_points:
        parts.append("entry_points:")
        for ep in entry_points:
            parts.append(f"  - {ep}")
    else:
        parts.append("entry_points: []")
    if extra_docs:
        parts.append("related_docs:")
        for doc in extra_docs:
            parts.append(f"  - {doc}")

    # [FILE_SCOPE]
    parts.append("\n[FILE_SCOPE]")
    parts.append("# Only touch these files unless explicitly told otherwise.")
    parts.append("files_scope:")
    for path in files_scope:
        parts.append(f"  - {path}")
    parts.append("files_may_create:")
    for path in files_create:
        parts.append(f"  - {path}")

    # [TASKS]
    parts.append("\n[TASKS]")
    if not tasks:
        parts.append("# No tasks listed; ask for clarification before editing.")
    else:
        for idx, t in enumerate(tasks, start=1):
            parts.append(f"{idx}) {t}")

    # [CONSTRAINTS]
    parts.append("\n[CONSTRAINTS]")
    parts.extend([
        "- Keep changes minimal and coherent; prefer focused edits over rewrites.",
        "- Preserve existing behavior unless a change is explicitly requested.",
        "- Match existing style, patterns, and naming in this repo.",
        "- Do not introduce new dependencies unless explicitly allowed.",
        "- If you are unsure about a requirement, ask before proceeding.",
    ])

    # [TESTS_AND_VALIDATION]
    parts.append("\n[TESTS_AND_VALIDATION]")
    parts.append("required_checks:")
    if acceptance_tests:
        for t in acceptance_tests:
            parts.append(f"  - {t}")
    else:
        parts.append("  - <no explicit tests; propose reasonable checks>")
    parts.append("acceptance_criteria:")
    parts.append("  - All required checks above pass.")
    parts.append("  - Changes are consistent with existing code style and conventions.")

    # [EXECUTION_GUIDANCE]
    parts.append("\n[EXECUTION_GUIDANCE]")
    parts.extend([
        "- First: skim the relevant files to build a mental model.",
        "- Then: propose a short PLAN (3–7 bullet steps).",
        "- After edits: conceptually run through the tests/checks above.",
        "- If tests would fail, explain why and how to fix them.",
    ])

    # [OUTPUT_FORMAT]
    parts.append("\n[OUTPUT_FORMAT]")
    parts.extend([
        "When responding, follow exactly:",
        "",
        "1) PLAN",
        "   - Bullet list of steps you will take.",
        "2) CHANGES",
        "   - Explain what you changed and why.",
        "   - Reference files like `path/to/file.py: line ranges` where possible.",
        "3) TESTS",
        "   - List which checks you ran (or would run) and the expected results.",
        "4) NEXT_STEPS",
        "   - Optional follow-ups or cleanups.",
        "",
        "If you cannot safely complete the tasks, explain the blockers and propose",
        "the smallest next step I should approve.",
    ])

    return "\n".join(parts) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render canonical workstream prompt from a JSON bundle."
    )
    parser.add_argument(
        "workstream_json",
        help="Path to workstream JSON (conforms to workstream.schema.json).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--tech-stack",
        help="Override tech_stack in [REPO_CONTEXT].",
    )
    parser.add_argument(
        "--entry-point",
        action="append",
        dest="entry_points",
        help="Entry point path; may be given multiple times.",
    )
    parser.add_argument(
        "--doc",
        action="append",
        dest="docs",
        help="Related doc path; may be given multiple times.",
    )

    args = parser.parse_args()

    ws_path = Path(args.workstream_json)
    with ws_path.open("r", encoding="utf-8") as f:
        ws = json.load(f)

    prompt = render_prompt(
        ws,
        tech_stack=args.tech_stack,
        entry_points=args.entry_points,
        extra_docs=args.docs,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)

if __name__ == "__main__":
    main()
```

---

## 3. How to use this with each agent

### 3.1. Generate prompts from your workstreams

Assume:

* Workstreams live in: `workstreams/ws-*.json`
* Prompts go to: `prompts/ws-*.txt`

Example:

```bash
# Single workstream
python tools/render_workstream_prompt.py \
  workstreams/ws-hello-world.json \
  --tech-stack "python, pytest" \
  --entry-point "src/hello/world.py" \
  --doc "AGENTS.md" \
  -o prompts/ws-hello-world.txt
```

You can loop this from PowerShell or a Makefile to render all workstreams in one go.

---

### 3.2. Aider

Aider supports a `--message-file` option that sends a single message from a file and then exits, which is exactly what we want for “one workstream, one run.”([Aider][1])

```bash
cd path/to/repo

python tools/render_workstream_prompt.py `
  workstreams/ws-hello-world.json `
  -o prompts/ws-hello-world.txt

aider --model ollama:qwen2.5-coder `
      --message-file prompts/ws-hello-world.txt `
      src/hello/world.py
```

You can also put global rules in a file like `CONVENTIONS.md` or `AGENTS.md` and configure Aider to always load it via `.aider.conf.yml`, so every workstream inherits those rules.([GitHub][2])

For new files, you can still follow the Aider recommendation of adding them first (`/add <file>`) if you’re using interactive runs; the prompt itself tells the model which files it **may** create.([Aider][3])

---

### 3.3. Ollama Code

Ollama Code is a CLI coding agent built on Ollama, designed to work with locally hosted models like Qwen coders.([GitHub][4])

Basic flow:

```bash
# Render prompt
python tools/render_workstream_prompt.py \
  workstreams/ws-hello-world.json \
  -o prompts/ws-hello-world.txt

# Start ollama-code in the repo
cd path/to/repo
ollama-code
```

Then paste the content of `prompts/ws-hello-world.txt` as your initial instruction in the Ollama Code session. Because the prompt is pure text with clear sections, Qwen/Ollama models handle it fine.

If you later wrap `ollama-code` in your orchestrator, you can:

* read the prompt file,
* send it as the **first user message** to the agent,
* then let the agent drive subsequent steps.

---

### 3.4. Codex CLI

Codex CLI is installed via `npm i -g @openai/codex` and is intended to run in macOS/Linux or WSL on Windows.([OpenAI Developers][5])

The prompt renderer doesn’t care where Codex is running; you just need to get the text into the Codex session:

```bash
# Render prompt
python tools/render_workstream_prompt.py \
  workstreams/ws-hello-world.json \
  -o prompts/ws-hello-world.txt

# Start Codex in WSL in the repo, then paste the prompt as the first message
codex
# (inside Codex agent session)
# > [paste the prompt contents here]
```

Because the prompt explicitly lists `files_scope`, `tasks`, and `required_checks`, it matches Codex best practices: clear scope and verifiable outcomes.

---

### 3.5. Claude Code

Claude Code is a CLI agent and now also has web/iOS access; the CLI still works great for repo-scale work.([GitHub][6])

CLI flow:

```bash
python tools/render_workstream_prompt.py \
  workstreams/ws-hello-world.json \
  --tech-stack "python, pytest" \
  --entry-point "src/hello/world.py" \
  --doc "AGENTS.md" \
  -o prompts/ws-hello-world.txt

cd path/to/repo
claude
# Then paste the prompt as the first message
```

Since the prompt tells Claude to:

* produce a PLAN,
* describe CHANGES,
* report TESTS,
* suggest NEXT_STEPS,

it lines up cleanly with Anthropic’s “best practices for agentic coding” patterns.([Anthropic][7])

---


[1]: https://aider.chat/docs/config/options.html?utm_source=chatgpt.com "Options reference"
[2]: https://github.com/paul-gauthier/aider/issues/660?utm_source=chatgpt.com "Configure aider to always add specific files to the chat (eg, ..."
[3]: https://aider.chat/docs/usage/tips.html?utm_source=chatgpt.com "Tips"
[4]: https://github.com/tcsenpai/ollama-code?utm_source=chatgpt.com "ollama-code is a privacy first coding agent."
[5]: https://developers.openai.com/codex/cli/?utm_source=chatgpt.com "Codex CLI"
[6]: https://github.com/anthropics/claude-code?utm_source=chatgpt.com "GitHub - anthropics/claude-code"
[7]: https://www.anthropic.com/engineering/claude-code-best-practices?utm_source=chatgpt.com "Claude Code: Best practices for agentic coding"


[1]: https://github.com/tcsenpai/ollama-code "GitHub - tcsenpai/ollama-code: ollama-code is a privacy first coding agent."
[2]: https://cookbook.openai.com/examples/gpt-5-codex_prompting_guide?utm_source=chatgpt.com "GPT-5-Codex Prompting Guide"
[3]: https://www.anthropic.com/engineering/claude-code-best-practices?utm_source=chatgpt.com "Claude Code: Best practices for agentic coding"
[4]: https://aider.chat/docs/ "Aider Documentation | aider"
[5]: https://developers.openai.com/codex/prompting/?utm_source=chatgpt.com "Prompting guide"
[6]: https://aider.chat/docs/benchmarks.html?utm_source=chatgpt.com "GPT code editing benchmarks"
