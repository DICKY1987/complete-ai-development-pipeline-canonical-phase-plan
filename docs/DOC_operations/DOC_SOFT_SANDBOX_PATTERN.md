---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-SOFT-SANDBOX-PATTERN-825
---

Cool, let’s lock this in tool-by-tool.
I’ll assume your “soft sandbox” pattern is:

* **Windows sandbox root**: `C:\Users\richg\AI_SANDBOX`
* **WSL sandbox root**: `~/ai-sandbox`
* For each repo, an **AI clone** like `pipeline_plus_sandbox` (or a worktree with that name).

You’ll **run all AI CLIs only inside those sandbox clones**, and the tools will be configured to treat them as “ok to go wild”.

---

## 0. One-time baseline (applies to ALL tools)

### Create sandbox roots

**Windows (PowerShell):**

```powershell
$env:AI_SANDBOX_ROOT = "C:\Users\richg\AI_SANDBOX"
New-Item -ItemType Directory -Path $env:AI_SANDBOX_ROOT -Force | Out-Null
```

**WSL (bash):**

```bash
export AI_SANDBOX_ROOT="$HOME/ai-sandbox"
mkdir -p "$AI_SANDBOX_ROOT"
```

### Create a sandbox clone for one repo (example: `pipeline_plus`)

**WSL:**

```bash
cd "$AI_SANDBOX_ROOT"
git clone https://github.com/YOUR_USER/pipeline_plus.git pipeline_plus_sandbox
```

**Windows:**

```powershell
cd $env:AI_SANDBOX_ROOT
git clone https://github.com/YOUR_USER/pipeline_plus.git pipeline_plus_sandbox
```

From now on, **all tools below are configured assuming you’re in that `*_sandbox` clone.**

---

## 1. Claude Code – soft-sandbox solution

Claude Code uses:

* A hierarchical **settings file**:

  * User: `~/.claude/settings.json`
  * Project: `.claude/settings.json` (in repo)
* Instruction files like **`CLAUDE.md`** for global & per-project rules. ([GitHub Docs][1])

### 1.1 Where you run Claude

* **Only inside sandbox clones**, e.g.:

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
claude
```

### 1.2 Files to create

1. **Global settings** (WSL or Windows home):

`~/.claude/settings.json` (or `C:\Users\richg\.claude\settings.json` on Windows if you use that layout).

Minimal safe example:

```json
{
  "model": "claude-3-5-sonnet"
}
```

Setting `model` here is officially supported. ([Skywork][2])

2. **Sandbox project instructions** (in each sandbox repo):

`CLAUDE.md` in `pipeline_plus_sandbox`:

```md
# Claude Instructions – AI Sandbox Clone

Context:
- This repo is an AI sandbox clone of the main project.
- All edits here are experimental and must be committed on ai-sandbox/* branches.

Rules:
- Only edit files inside this repo.
- Prefer small, atomic changes with clear explanations.
- When making code changes, propose or update tests whenever possible.
- When changes are stable, summarize them and suggest a commit message.

Safety:
- Treat destructive operations (rm, chmod, etc.) as last resort and explain before running them.
```

### 1.3 Prompt so **Claude or Codex** can wire this up

When you’re in WSL home:

```bash
cd ~
claude
```

Prompt to paste into **Claude** (or into **Codex** with the same intent):

> You are configuring Claude Code for soft-sandbox usage.
> Tasks:
>
> 1. Create or update `~/.claude/settings.json` to set `"model": "claude-3-5-sonnet"` and add comments if supported. Do NOT add any auto-approval or dangerous flags; just the model.
> 2. In `$AI_SANDBOX_ROOT/pipeline_plus_sandbox`, create a `CLAUDE.md` file with instructions that:
>
>    * Clarify that this is an AI sandbox clone.
>    * Restrict edits to this repo only.
>    * Encourage small, atomic commits and test updates.
>    * Explicitly warn before running destructive shell commands.
> 3. Show me the resulting files so I can verify them before first use.

You just confirm the edits; Claude/Codex does the file work.

---

## 2. Aider – soft-sandbox solution

Aider reads options from: ([GitHub][3])

* `.aider.conf.yml` in:

  * home dir
  * repo root
  * current directory
* Later files override earlier ones.
* Many options can also be set via env vars or `.env`.

### 2.1 Where you run Aider

Always from the sandbox clone:

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
aider
```

### 2.2 Files to create

In `pipeline_plus_sandbox`, create **`.aider.conf.yml`**:

```yaml
# Aider config – AI sandbox clone

dark-mode: true            # example option from docs
model: claude-3-5-sonnet   # or your preferred model name
auto-commits: true         # let aider commit after successful changes
branch: ai-sandbox/aider   # branch naming convention in this sandbox

# Optional: ensure we stay within this repo
subdir: .
```

(The exact set of options is defined in the Aider docs; `dark-mode` and `model` are standard options. ([The GitHub Blog][4]))

If you prefer API keys in a `.env`, you can also have Aider create a `.env` in the sandbox with just `AIDER_*` keys (no secrets in git).

### 2.3 Prompt so **Claude/Codex** configures Aider

Run Codex or Claude in WSL, then:

> You are configuring Aider for soft-sandbox usage.
>
> * Assume `$AI_SANDBOX_ROOT` is set and contains `pipeline_plus_sandbox`.
> * In `$AI_SANDBOX_ROOT/pipeline_plus_sandbox`, create an `.aider.conf.yml` file with:
>
>   * `dark-mode: true`
>   * a `model` set to `claude-3-5-sonnet`
>   * `auto-commits: true`
>   * a `branch` value of `ai-sandbox/aider`
>   * a `subdir` of `.` so edits stay in this repo.
> * Do NOT hardcode any API keys.
> * Show me the final YAML so I can copy/paste it if needed.

---

## 3. GitHub Copilot CLI – soft-sandbox solution

Copilot CLI obeys repo instructions in: ([GitHub Docs][5])

* `.github/copilot-instructions.md` (repo-wide)
* Optional path-specific `.github/copilot-instructions/**/*.instructions.md`

And you can reduce confirmation prompts using `--allow-all-tools` and env `COPILOT_ALLOW_ALL`. ([GitHub Docs][5])

### 3.1 Where you run Copilot

From the sandbox repo:

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
copilot --allow-all-tools
```

(You can also add `--deny-tool` for truly scary things like `shell(rm)` if you want a guardrail).

### 3.2 Files to create

In the sandbox repo:

1. **`.github/copilot-instructions.md`**:

```md
# Copilot CLI Instructions – AI Sandbox

Context:
- This repository is an AI sandbox clone of the main project.
- All changes here are experimental and may be discarded.

Rules:
- Only modify files within this repository.
- Prefer small, incremental changes with clear explanations.
- When changing behavior, propose or update tests where possible.
- When you run tools that modify files, summarize what was changed.

Safety:
- Avoid destructive `rm -rf` style commands; if such commands are proposed, explain the risk first.
```

This file is officially how you give Copilot repo-level guidance. ([GitHub Docs][5])

2. **Environment variable for fewer prompts** (in sandbox shell):

```bash
# WSL – in ~/.bashrc
export COPILOT_ALLOW_ALL="true"
```

Docs show `COPILOT_ALLOW_ALL` allows all tools to run automatically when set to `"true"`. ([Zenn][6])

Then you can simply:

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
copilot --allow-all-tools
```

### 3.3 Prompt so Claude/Codex sets this up

> Configure GitHub Copilot CLI for soft-sandbox usage in WSL.
>
> 1. In `$AI_SANDBOX_ROOT/pipeline_plus_sandbox`, create the directory `.github` if missing, then create `.github/copilot-instructions.md` with:
>
>    * A note that this repo is an AI sandbox clone.
>    * Instructions to keep changes small and test-focused.
>    * A warning against destructive shell commands like `rm -rf`.
> 2. In my `~/.bashrc`, append a line to set `COPILOT_ALLOW_ALL="true"` so Copilot CLI can run tools without repeated confirmation.
> 3. Show me the diff to confirm before saving.

(If you want extra safety, you can also ask it to add `--deny-tool 'shell(rm)'` to a shell alias or function. ([GitHub Docs][5]))

---

## 4. Codex on **WSL** – soft-sandbox solution

Codex CLI uses: ([xylem | Gordon Beeming][7])

* Config file: `~/.codex/config.toml`
* Instruction files: `AGENTS.md` (global & per-project)
* It reads/edits files in the directory where you run it.

### 4.1 Where you run Codex (WSL)

Always from sandbox clones:

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
codex
```

### 4.2 Files to create

1. **WSL config**: `/home/richg/.codex/config.toml`

Minimal sandbox-friendly example:

```toml
# Codex config – WSL

model = "gpt-5.1-codex"

# Workspace policy: only write inside current workspace
sandbox_mode = "workspace-write"
```

(`sandbox_mode` is part of Codex’s config for controlling where it can write. Exact options are described in the Codex configuration docs.) ([xylem | Gordon Beeming][7])

2. **Sandbox repo instructions**: `$AI_SANDBOX_ROOT/pipeline_plus_sandbox/AGENTS.md`:

```md
# Codex Instructions – AI Sandbox Clone

Context:
- This repository is an AI sandbox clone used for autonomous Codex runs.
- All edits must stay within this repo.

Behavior:
- Use small, incremental changes and explain your plan before large refactors.
- Prefer creating or updating tests when changing behavior.
- When preparing work for the main repo, summarize changes and propose branch/PR names.

Safety:
- Do not run destructive commands affecting parent directories.
- Treat this repo as disposable, but still keep commits clean and readable.
```

### 4.3 Prompt so Codex configures itself (WSL)

From your WSL shell:

```bash
cd ~
codex
```

Then:

> Configure Codex CLI for soft-sandbox operation in WSL:
>
> 1. Ensure the directory `~/.codex` exists and create/update `~/.codex/config.toml` with:
>
>    * `model = "gpt-5.1-codex"`
>    * `sandbox_mode = "workspace-write"`
> 2. In `$AI_SANDBOX_ROOT/pipeline_plus_sandbox`, create an `AGENTS.md` that:
>
>    * States this is an AI sandbox clone.
>    * Restricts edits to the repo.
>    * Encourages atomic changes, tests, and clean commit messages.
> 3. Show me the file contents when you’re done.

---

## 5. Codex on **Windows** – soft-sandbox solution

On Windows, Codex uses the same config file concept, just under your Windows home: `C:\Users\richg\.codex\config.toml`. ([xylem | Gordon Beeming][7])

The sandbox repos are under `C:\Users\richg\AI_SANDBOX\...`.

### 5.1 Where you run Codex (Windows)

```powershell
cd C:\Users\richg\AI_SANDBOX\pipeline_plus_sandbox
codex
```

### 5.2 Files to create

1. **Windows config**: `C:\Users\richg\.codex\config.toml`

```toml
# Codex config – Windows

model = "gpt-5.1-codex"
sandbox_mode = "workspace-write"
```

2. **Sandbox repo instructions** – you can reuse the same `AGENTS.md` content as WSL, but created in the Windows clone (if you’re using separate clones). If both WSL and Windows share the same repo via the NTFS mount, they’ll share that same `AGENTS.md`.

### 5.3 Prompt so Codex on Windows sets itself up

Open a Windows terminal:

```powershell
cd $env:USERPROFILE
codex
```

Then prompt:

> You are configuring Codex CLI on Windows for soft-sandbox usage.
>
> 1. Ensure `C:\Users\richg\.codex` exists and create/update `C:\Users\richg\.codex\config.toml` with:
>
>    * `model = "gpt-5.1-codex"`
>    * `sandbox_mode = "workspace-write"`
> 2. In `C:\Users\richg\AI_SANDBOX\pipeline_plus_sandbox`, create an `AGENTS.md` file similar to my WSL sandbox, stating that:
>
>    * This is an AI sandbox clone.
>    * Edits must be confined to the repo.
>    * Changes should be atomic and test-aware.
> 3. Show the full TOML and AGENTS.md contents when you’re done.

---

## 6. What you’ve got after this

Once you run those per-tool prompts and confirm the files:

* **Claude Code** respects sandbox instructions via `CLAUDE.md` + global `settings.json`.
* **Aider** defaults to sandbox behavior via `.aider.conf.yml` in each sandbox clone.
* **GitHub Copilot CLI** reads `.github/copilot-instructions.md` and can be allowed to use tools automatically, scoped to the sandbox repos.
* **Codex (WSL + Windows)** reads `~/.codex/config.toml` and per-repo `AGENTS.md` so it knows these are AI playgrounds.

If you want, next step I can give you **a single “master setup” prompt** that tells Codex (on WSL) to:

* Create the sandbox clones,
* Generate all of these config/ instruction files for *every* repo under `AI_SANDBOX_ROOT`,
* And keep them consistent across tools.

[1]: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli?utm_source=chatgpt.com "Using GitHub Copilot CLI"
[2]: https://skywork.ai/blog/ai-agent/how-to-build-chat-based-developer-tools-claude-code-plugin/?utm_source=chatgpt.com "How to Build Chat-Based Developer Tools with Claude ..."
[3]: https://github.com/microsoft/vscode/issues/272921?utm_source=chatgpt.com "Add copilot CLI fig spec · Issue #272921 · microsoft/vscode"
[4]: https://github.blog/ai-and-ml/github-copilot-cli-101-how-to-use-github-copilot-from-the-command-line/?utm_source=chatgpt.com "How to use GitHub Copilot from the command line"
[5]: https://docs.github.com/copilot/concepts/agents/about-copilot-cli?utm_source=chatgpt.com "About GitHub Copilot CLI"
[6]: https://zenn.dev/10q89s/articles/4a42fb779fde89?utm_source=chatgpt.com "ターミナル派待望の GitHub Copilot CLI 使い方まとめ"
[7]: https://gordonbeeming.com/blog/2025-10-03/taming-the-ai-my-paranoid-guide-to-running-copilot-cli-in-a-secure-docker-sandbox?utm_source=chatgpt.com "Taming the AI: My Paranoid Guide to Running Copilot CLI ..."
