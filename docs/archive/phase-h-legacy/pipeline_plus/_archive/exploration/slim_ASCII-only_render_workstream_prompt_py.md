
1. A **slim, ASCII-only, v1-delimited canonical template**
2. A **drop-in `render_workstream_prompt.py`** that emits exactly that format from your `workstream.schema.json` bundles

You can paste both straight into your repo.

---

## 1. Slim, ASCII-only, v1-delimited canonical template

This is the human-facing “spec” version with placeholders.
Every runtime prompt your router generates should look like this, with the `<...>` parts filled in from the bundle.

```text
=== WORKSTREAM_PROMPT v1 START ===

[ROLE]
You are a senior software engineer working in an existing codebase.
Follow the instructions below. If anything is unclear or risky, explain
why and describe safer alternatives before making risky changes.

[WORKSTREAM_META]
id: <workstream id, e.g. ws-hello-world>
gate: <minimum gate or approval level, e.g. 1>
openspec_change: <OpenSpec change id, if any, else "none">
ccpm_issue: <issue id, if any, else "none">
depends_on:
- <other workstream ids this depends on, or "none">
tool: <preferred primary tool, e.g. aider>
metadata:
- key: value pairs with any useful hints (owner, priority, tags)

[FILE_SCOPE]
files_scope:
- <paths of files this workstream owns>
files_may_create:
- <paths of files that may be created>

[TASKS]
1) <first concrete task>
2) <second concrete task>
3) <add more as needed>

[CONSTRAINTS]
- Keep changes minimal and targeted to this workstream.
- Preserve existing behavior unless the task explicitly changes it.
- Match the existing style and patterns in this repository.
- Do not introduce new dependencies unless necessary and clearly justified.

[TESTS_AND_VALIDATION]
required_checks:
- <command or description, for example: pytest -q -k test_hello>
- <lints or static checks, for example: ruff check src>
acceptance_criteria:
- All required checks pass, or you clearly explain why they cannot.
- The code builds and runs without errors in the documented workflows.

[OUTPUT_FORMAT]
Respond in this exact structure:

PLAN:
- Short bullet list of steps you will take.

CHANGES:
- Bullet list or short paragraphs summarizing the changes.
- Mention which files you changed and why.

TESTS:
- What checks or tests you ran, real or conceptual.
- Their outcomes.

NEXT_STEPS:
- Follow up work or verification needed.
- Any risks, limitations, or open questions.

=== WORKSTREAM_PROMPT END ===
```

That’s the **contract** all your CLI tools see.

---

## 2. `render_workstream_prompt.py` that emits that format

This script assumes your workstream JSON matches `workstream.schema.json` (fields like `id`, `files_scope`, `files_create`, `tasks`, `acceptance_tests`, etc.).

Drop this in (for example) as `tools/render_workstream_prompt.py` and wire it into your pipeline.

```python
#!/usr/bin/env python3
"""
Render a slim, ASCII-only, v1-delimited workstream prompt from a workstream
bundle JSON that follows workstream.schema.json.

Usage:
    python render_workstream_prompt.py workstreams/ws-hello-world.json \
        -o prompts/ws-hello-world.txt
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _format_list(values: List[str], empty_msg: str = "- none") -> List[str]:
    if not values:
        return [empty_msg]
    return [f"- {v}" for v in values]


def _format_metadata(metadata: Dict[str, Any]) -> List[str]:
    if not metadata:
        return ["- none"]
    lines: List[str] = []
    for key in sorted(metadata.keys()):
        value = metadata[key]
        lines.append(f"- {key}: {value}")
    return lines


def render_workstream_prompt(bundle: Dict[str, Any]) -> str:
    """
    Render a single workstream bundle dict into the canonical
    slim, ASCII-only, v1-delimited prompt text.
    """
    wid = bundle.get("id", "<missing id>")
    gate = bundle.get("gate")
    gate_str = str(gate) if gate is not None else "<unspecified>"

    openspec_change = bundle.get("openspec_change") or "none"
    ccpm_issue = bundle.get("ccpm_issue") or "none"

    depends_on = bundle.get("depends_on") or []
    files_scope = bundle.get("files_scope") or []
    files_create = bundle.get("files_create") or []
    tasks = bundle.get("tasks") or []
    acceptance_tests = bundle.get("acceptance_tests") or []
    tool = bundle.get("tool") or "<unspecified>"
    metadata = bundle.get("metadata") or {}

    lines: List[str] = []

    # Header
    lines.append("=== WORKSTREAM_PROMPT v1 START ===")
    lines.append("")

    # ROLE
    lines.append("[ROLE]")
    lines.append("You are a senior software engineer working in an existing codebase.")
    lines.append("Follow the instructions below. If anything is unclear or risky, explain")
    lines.append("why and describe safer alternatives before making risky changes.")
    lines.append("")

    # WORKSTREAM_META
    lines.append("[WORKSTREAM_META]")
    lines.append(f"id: {wid}")
    lines.append(f"gate: {gate_str}")
    lines.append(f"openspec_change: {openspec_change}")
    lines.append(f"ccpm_issue: {ccpm_issue}")
    lines.append("depends_on:")
    lines.extend(_format_list(depends_on))
    lines.append(f"tool: {tool}")
    lines.append("metadata:")
    lines.extend(_format_metadata(metadata))
    lines.append("")

    # FILE_SCOPE
    lines.append("[FILE_SCOPE]")
    lines.append("files_scope:")
    lines.extend(_format_list(files_scope))
    lines.append("files_may_create:")
    lines.extend(_format_list(files_create))
    lines.append("")

    # TASKS
    lines.append("[TASKS]")
    if not tasks:
        lines.append("1) <no concrete tasks were defined in this workstream>")
    else:
        for idx, task in enumerate(tasks, start=1):
            lines.append(f"{idx}) {task}")
    lines.append("")

    # CONSTRAINTS
    lines.append("[CONSTRAINTS]")
    lines.append("- Keep changes minimal and targeted to this workstream.")
    lines.append("- Preserve existing behavior unless the task explicitly changes it.")
    lines.append("- Match the existing style and patterns in this repository.")
    lines.append("- Do not introduce new dependencies unless necessary and clearly justified.")
    lines.append("")

    # TESTS_AND_VALIDATION
    lines.append("[TESTS_AND_VALIDATION]")
    lines.append("required_checks:")
    lines.extend(_format_list(acceptance_tests, empty_msg="- none specified"))
    lines.append("acceptance_criteria:")
    lines.append("- All required checks pass, or you clearly explain why they cannot.")
    lines.append("- The code builds and runs without errors in the documented workflows.")
    lines.append("")

    # OUTPUT_FORMAT
    lines.append("[OUTPUT_FORMAT]")
    lines.append("Respond in this exact structure:")
    lines.append("")
    lines.append("PLAN:")
    lines.append("- Short bullet list of steps you will take.")
    lines.append("")
    lines.append("CHANGES:")
    lines.append("- Bullet list or short paragraphs summarizing the changes.")
    lines.append("- Mention which files you changed and why.")
    lines.append("")
    lines.append("TESTS:")
    lines.append("- What checks or tests you ran, real or conceptual.")
    lines.append("- Their outcomes.")
    lines.append("")
    lines.append("NEXT_STEPS:")
    lines.append("- Follow up work or verification needed.")
    lines.append("- Any risks, limitations, or open questions.")
    lines.append("")
    lines.append("=== WORKSTREAM_PROMPT END ===")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a slim, ASCII-only workstream prompt from a JSON bundle."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to workstream bundle JSON (matches workstream.schema.json).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for the rendered prompt. If omitted, prints to stdout.",
    )

    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as f:
        bundle = json.load(f)

    prompt_text = render_workstream_prompt(bundle)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as f:
            f.write(prompt_text)
    else:
        print(prompt_text)


if __name__ == "__main__":
    main()
```

---

## 3. How to plug this into your pipeline

Quick wiring sketch:

* For each `workstreams/ws-*.json`:

```bash
python tools/render_workstream_prompt.py workstreams/ws-hello-world.json \
  -o prompts/ws-hello-world.txt
```

* When you enqueue a task for Aider / Codex / Claude / Ollama Code, your task object includes:

```jsonc
{
  "workstream_id": "ws-hello-world",
  "prompt_file": "prompts/ws-hello-world.txt",
  "repo_path": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
  ...
}
```

* The adapter for each CLI app simply:

  * `cd` to `repo_path`
  * feeds `prompt_file` as the **first user message** (or `--message-file` for Aider)
  * captures output and streams it back to your central logs

That gives you:

* One **universal format** for all tools
* A **single source of truth** (`ws-*.json`) that drives the prompt
* v1 delimiters so you can evolve later (v2, etc.) without confusion

If you want, next step we can:

* Add a tiny PowerShell wrapper (`New-WorkstreamPrompt`), or
* Show how to integrate `prompt_file` into your existing `SubmitTask.ps1` / `.tasks` JSONL task format.
