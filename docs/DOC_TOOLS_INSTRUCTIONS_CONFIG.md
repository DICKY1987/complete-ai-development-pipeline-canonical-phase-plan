Short version:
Each of these tools has **its own “instructions file” + config** you can hook into:

* **Claude Code** → `CLAUDE.md` + `~/.claude/settings.json` + `--system-prompt*` flags
* **Codex** → `AGENTS.md` + `~/.codex/config.toml`
* **GitHub Copilot / Copilot CLI** → `.github/copilot-instructions.md` (repo) + personal custom instructions

Below I’ll show **where to put the files**, **what to put in them**, and a **minimal cross-tool pattern**.

---

## 1. Cross-tool pattern (the mental model)

For all three, think in **three layers**:

1. **Global persona / rules**

   * Applies everywhere on your machine.
   * One file per tool:

     * Claude Code → `~/.claude/CLAUDE.md`([Shipyard][1])
     * Codex → `~/.codex/AGENTS.md`([Microsoft Learn][2])
     * Copilot → personal custom instructions (set in GitHub account UI)([GitHub Docs][3])

2. **Repo / project-level instructions**

   * Live *inside* each project:

     * Claude → `./CLAUDE.md` in repo([Shipyard][1])
     * Codex → `./AGENTS.md` in repo root (and optionally deeper subdir AGENTS.md)([Microsoft Learn][2])
     * Copilot → `.github/copilot-instructions.md` in repo root([GitHub Docs][4])

3. **Per-invocation overrides**

   * CLI flags / one-off prompt text:

     * Claude: `--append-system-prompt` / `--system-prompt-file`([Claude][5])
     * Codex: just write the prompt text, or use a special profile for a certain style.([OpenAI Developers][6])
     * Copilot CLI: include specifics in the command prompt, but repo instructions still do most of the heavy lifting.([GitHub Docs][4])

If you pour your **DEVELOPMENT RULES DO and DONT**, phase spec rules, etc. into those instruction files, all three tools will consistently follow them without you re-typing them.

---

## 2. Claude Code – instructions + behavior

### a) Global + project instruction files (`CLAUDE.md`)

Claude Code automatically reads **CLAUDE.md** files in a hierarchy:

* Global: `~/.claude/CLAUDE.md`
* Project: `./CLAUDE.md` at repo root
* Subfolders: `./some/component/CLAUDE.md` for component-specific rules([Shipyard][1])

Example `~/.claude/CLAUDE.md`:

```md
# Global Claude instructions

You are a senior systems engineer working in a multi-agent, phase-based pipeline.

Global rules:
- Always obey the DEVELOPMENT_RULES_DO_AND_DONT document in this repo if present.
- Prefer small, atomic, testable changes.
- When editing files, show unified diffs and explain each chunk.
```

Project `CLAUDE.md` (in repo root):

```md
# Project-specific instructions

Project: CLI Multi-Rapid Pipeline

- Treat `UNIVERSAL_PHASE_SPECIFICATION` + `PRO_Phase Specification mandatory structure.md`
  as the source of truth for phase definitions.
- If you propose changes to any spec, emit them as unified diff patches in a separate section.

Coding preferences:
- Language priority: Python > PowerShell > Bash.
- Always add or update tests when modifying behavior.
```

### b) Behavior via `settings.json`

Claude Code’s main config is **`settings.json`** with user + project variants:([Claude][7])

* Global: `~/.claude/settings.json`
* Project: `.claude/settings.json`
* Local overrides: `.claude/settings.local.json`

Example `~/.claude/settings.json` wiring your style:

```json
{
  "defaultModel": "claude-sonnet-4-20250514",
  "autoAcceptPermissions": false,
  "permissions": {
    "allow": ["Read(*)", "Grep(*)", "Glob(*)"],
    "deny": [
      "Read(./secrets/**)",
      "Read(./.env*)"
    ]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "git diff --stat"
      }]
    }]
  }
}
```

That doesn’t “instruct” in natural language, but it **enforces behavior** (no secrets, always see git diff, etc.).

### c) Per-command system prompt flags

When you want a special mode for one run:

* **Replace** everything:
  `claude --system-prompt "You are a strict phase-spec validator…"`([Claude][5])
* **Append** to default:
  `claude --append-system-prompt "Always emit patch files, never raw edited text."`
* **Load from file**:
  `claude -p --system-prompt-file ./prompts/PHASE_VALIDATOR.txt "Validate PH-001 spec"`

---

## 3. Codex – AGENTS.md + config

### a) AGENTS.md instruction files

Codex uses **AGENTS.md** as its instruction layer:([Microsoft Learn][2])

* Global: `~/.codex/AGENTS.md`
* Repo root: `./AGENTS.md`
* Subdir: `./subsystem/AGENTS.md`

Codex merges them **top-down** (global → repo → subdir), so you can layer rules.

Example `~/.codex/AGENTS.md`:

```md
# Global Codex instructions

You are Codex, acting as an orchestrator between multiple CLI tools.

Global rules:
- Never modify files outside the current git repo.
- Prefer patch-based edits and unified diffs.
- When uncertain, ask clarifying questions instead of guessing.
```

Project-level `AGENTS.md`:

```md
# Project instructions: R_PIPELINE

- Follow the AGENT_OPERATIONS_SPEC v1.0 if present.
- When the user says "execute a phase", consult the phase spec file
  and treat it as the source of truth for inputs/outputs.
- For PowerShell/Python edits, emit patches and a short execution checklist.
```

### b) Codex config: `~/.codex/config.toml`

Behavior defaults (model, sandbox, reasoning depth, instructions file) live in `~/.codex/config.toml`.([OpenAI Developers][6])

Example:

```toml
model = "gpt-5.1-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

# Use AGENTS.md (global + repo) as the main instruction source
project_doc_max_bytes = 200000

[features]
apply_patch_freeform = true
web_search_request = false
```

If you ever want to point at a **single instructions file instead of AGENTS.md**, there is an experimental knob:

```toml
experimental_instructions_file = "/home/richg/ALL_AI/AGENT_OPERATIONS_SPEC_rendered.md"
```

But in most cases using `AGENTS.md` is the “official” path.

---

## 4. GitHub Copilot & Copilot CLI – instructions files

You’ve got two main layers here:

### a) Personal custom instructions (account-wide)

Set these once in the GitHub UI under **Copilot → Configure custom instructions**; they apply across IDE, web, and Copilot CLI.([GitHub Docs][3])

Use that for things like:

* “I use a phase-based ACMS system; prefer atomic changes + tests.”
* “Never generate secrets; assume env vars instead.”
* “Prefer pytest / Pester / etc.”

### b) Repo instructions: `.github/copilot-instructions.md`

For **project-specific rules**, Copilot uses repo files:([GitHub Docs][4])

* Repo-wide:
  `.github/copilot-instructions.md`
* Path-specific (optional):
  `.github/instructions/NAME.instructions.md`
* These instructions are used in IDEs **and Copilot CLI** (same mechanism).([GitHub Docs][4])

Example `.github/copilot-instructions.md`:

```md
# Repository instructions for GitHub Copilot

Context:
- This repo implements a multi-agent CLI pipeline for AI coding tools.

Rules:
- Always follow the documented phase specs when generating or editing code.
- Prefer creating or updating tests in the same PR as code changes.
- Use small, focused commits and write descriptive messages.
- Never generate real API keys or passwords; use placeholders like `YOUR_API_KEY_HERE`.

Tech stack preferences:
- Python 3.12, PowerShell 7, Node LTS.
- Use type hints in Python and Pester for PowerShell tests.
```

Path-specific example (only for, say, `scripts/`):

`.github/instructions/scripts.instructions.md`:

```md
# Path-specific instructions for scripts/

- Scripts must be idempotent and safe to re-run.
- Always include a dry-run option if you modify files.
- When in doubt, default to logging instead of destructive actions.
```

Copilot CLI will honor these when you run things like `gh copilot` or `github-copilot-cli` commands from that repo.

---

## 5. Unified minimal example for all three

Let’s say you want a **single behavior spec** and then tool-specific shells:

1. Put your canonical rules in the repo, e.g.:

`docs/DEV_RULES_CORE.md`

2. In each tool’s instruction file, **point at that doc + restate the key contract**:

**Claude** `CLAUDE.md`:

```md
# Instructions

Primary contract: see docs/DEV_RULES_CORE.md.

Obey those rules. If any incoming prompt conflicts with them, warn the user and ask before continuing.
```

**Codex** `AGENTS.md`:

```md
# Codex instructions

Treat docs/DEV_RULES_CORE.md as the governing spec.
If a requested action violates those rules, stop and explain why.
```

**Copilot** `.github/copilot-instructions.md`:

```md
# Copilot instructions

This repo is governed by docs/DEV_RULES_CORE.md.
Align suggestions and refactors with those rules.
```

Now you’ve got **one source of truth** and three adapters.

---

## 6. Concrete “do this next” checklist

1. **Claude Code**

   * Create `~/.claude/CLAUDE.md` and a project `./CLAUDE.md`.
   * Add your global + project rules.
   * Optionally add behavior enforcement in `~/.claude/settings.json`.

2. **Codex**

   * Create `~/.codex/AGENTS.md` and repo `./AGENTS.md`.
   * Make sure `~/.codex/config.toml` exists and is sane (model, sandbox, etc.).

3. **GitHub Copilot**

   * Set personal custom instructions in GitHub.
   * In each repo, create `.github/copilot-instructions.md`.
   * (Optional) Add `.github/instructions/*.instructions.md` for path-specific behavior.

If you’d like, I can draft **exact contents** for these three instruction files tailored to your ACMS / phase specs so you can drop them straight into your repos.

[1]: https://shipyard.build/blog/claude-code-cheat-sheet/?utm_source=chatgpt.com "Claude Code CLI Cheatsheet: config, commands, prompts, + ..."
[2]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/codex "Codex with Azure OpenAI in Foundry Models - Microsoft Foundry | Microsoft Learn"
[3]: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions "Configure custom instructions for GitHub Copilot - GitHub Docs"
[4]: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot "Adding repository custom instructions for GitHub Copilot - GitHub Docs"
[5]: https://code.claude.com/docs/en/cli-reference "CLI reference - Claude Code Docs"
[6]: https://developers.openai.com/codex/local-config/ "Configuring Codex"
[7]: https://code.claude.com/docs/en/settings?utm_source=chatgpt.com "Claude Code settings - Claude Code Docs"
