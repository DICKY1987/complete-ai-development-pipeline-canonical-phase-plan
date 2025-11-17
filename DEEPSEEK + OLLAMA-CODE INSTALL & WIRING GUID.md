# DEEPSEEK + OLLAMA-CODE INSTALL & WIRING GUIDE

*for autonomous AI agents on DICK’s machine*

> **Audience:** This document is written for an AI agent (Codex, Claude Code, Aider, etc.) that has shell access to DICK’s Windows 11 + WSL2 environment.
> **Goal:** Install and wire up:
>
> 1. **DeepSeek-Coder via Ollama** as a backend model (used by Aider + others)
> 2. **`ollama-code` CLI** as an additional coding agent
>    so they behave consistently with how **Aider** is already integrated.

---

## 0. High-level goals

1. Ensure **Ollama** is running on Windows and serving a **DeepSeek-Coder** model.
2. Configure **Aider** to use DeepSeek-Coder via the same “fake API key / local endpoint” pattern.
3. Install **`ollama-code`** and configure it to use the same Ollama backend.
4. Register both as tools in the existing **tool_profiles / orchestrator** and expose helper commands (like `aider-wsl`).

Assumptions:

* Windows username is `richg`.
* Main AI repos live under:
  `C:\Users\richg\ALL_AI`
* WSL distro is `Ubuntu`.
* Aider is already installed and working with Ollama on this machine (you may be re-pointing the model).

---

## 1. Pre-flight checks

### 1.1. Verify Ollama is installed & running (Windows)

**Action (PowerShell):**

```powershell
ollama --version
```

* If this fails, AI must **stop** and prompt the user to install Ollama for Windows from the official site.

**Check server:**

```powershell
ollama list
```

* If this errors, start the daemon:

```powershell
ollama serve
```

Keep Ollama running (it’s the model server for DeepSeek + ollama-code + Aider).

---

## 2. Install DeepSeek-Coder model in Ollama

### 2.1. Pull at least one DeepSeek-Coder model

**Action (PowerShell):**

```powershell
ollama pull deepseek-coder
# optional better model:
# ollama pull deepseek-coder-v2:16b
```

Goal: After this, `ollama list` should show at least one of:

* `deepseek-coder`
* `deepseek-coder-v2:16b`

### 2.2. Quick smoke test (optional)

```powershell
ollama run deepseek-coder -p "Write a one-line Python script that prints 42."
```

If this returns a sensible answer, the model is available.

---

## 3. Wire DeepSeek-Coder into Aider (same pattern as existing setup)

Aider expects something that **looks like** an OpenAI-compatible API:

* `OPENAI_API_BASE` or `OPENAI_API_URL`
* `OPENAI_API_KEY`

We simulate this using Ollama’s local HTTP endpoint.

### 3.1. Configure env inside WSL (Ubuntu)

AI: open a WSL shell:

```powershell
wsl -d Ubuntu
```

Inside WSL **bash**:

#### 3.1.1. Detect correct Ollama host URL

If Ollama is running on **Windows host**:

* `127.0.0.1` **inside WSL** may not point to the Windows service.
* There will be a Windows-host IP visible from WSL (e.g. `172.22.x.y`).

To keep things simple, this doc assumes the user has already identified that IP and recorded it elsewhere. If not, a common pattern is:

```bash
# Example only: AI should detect or ask user for the real value
WINDOWS_OLLAMA_IP="172.22.224.1"
```

Then construct:

```bash
export OPENAI_API_BASE="http://$WINDOWS_OLLAMA_IP:11434/v1"
```

If Ollama and Aider are both inside WSL itself, use:

```bash
export OPENAI_API_BASE="http://127.0.0.1:11434/v1"
```

#### 3.1.2. Set environment variables for Aider

Append to `~/.bashrc` (AI should use `echo >>`):

```bash
echo 'export OPENAI_API_BASE="http://<OLLAMA_HOST_IP>:11434/v1"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="ollama-local-key"' >> ~/.bashrc
echo 'export AIDER_MODEL="deepseek-coder-v2:16b"' >> ~/.bashrc
```

> Replace `<OLLAMA_HOST_IP>` with either `127.0.0.1` or the actual Windows host IP visible in WSL.

Apply changes in current shell:

```bash
source ~/.bashrc
```

### 3.2. Configure Aider’s config file

AI: locate Aider’s config file, usually:

* `/home/<user>/.aider.conf.yml` inside WSL

If not present, create it.

Minimum content:

```yaml
model: deepseek-coder-v2:16b
# Optionally:
# openai_api_base: "http://<OLLAMA_HOST_IP>:11434/v1"
# openai_api_key: "ollama-local-key"
```

This ensures that when the user (or orchestrator) runs `aider`, it:

* Uses DeepSeek-Coder via Ollama as the model.
* Talks to the local HTTP endpoint, not the cloud.

---

## 4. Install `ollama-code` CLI

### 4.1. Install Node / npm (WSL) if needed

Inside WSL:

```bash
node -v || sudo apt-get update && sudo apt-get install -y nodejs npm
```

> If `node -v` already shows a version ≥ 18, you can skip the install.

### 4.2. Install `ollama-code` globally

Inside WSL:

```bash
npm install -g @tcsenpai/ollama-code
```

Verify:

```bash
ollama-code --help
```

If this prints usage info, installation is successful.

---

## 5. Wire `ollama-code` to same Ollama backend

We want `ollama-code` to use:

* The **same Ollama server** (same host:port)
* A **DeepSeek-Coder** model (or any coder model the user chooses)

### 5.1. Set `OLLAMA`-related environment variables (WSL)

Append to `~/.bashrc`:

```bash
echo 'export OLLAMA_BASE_URL="http://<OLLAMA_HOST_IP>:11434/v1"' >> ~/.bashrc
echo 'export OLLAMA_MODEL="deepseek-coder-v2:16b"' >> ~/.bashrc
```

Re-source:

```bash
source ~/.bashrc
```

> Again, `<OLLAMA_HOST_IP>` must match the same value used for Aider.

### 5.2. Optional config file for `ollama-code`

If `ollama-code` supports a config at `~/.config/ollama-code/config.json`, AI can create:

```bash
mkdir -p ~/.config/ollama-code
cat > ~/.config/ollama-code/config.json << 'EOF'
{
  "baseUrl": "http://<OLLAMA_HOST_IP>:11434/v1",
  "model":   "deepseek-coder-v2:16b"
}
EOF
```

Now `ollama-code` will:

* Default to the same Ollama server.
* Use `deepseek-coder-v2:16b` as the model unless overridden.

---

## 6. Register both tools in `tool_profiles.json`

> This section assumes the project has a central `tool_profiles.json` (or similar) used by the orchestrator / scheduler.
> AI: **do not overwrite** the file; carefully merge these entries.

### 6.1. DeepSeek-backed Aider (already present, ensure correctness)

Locate the existing `aider` entry and update it to reflect the DeepSeek/Ollama usage, e.g.:

```jsonc
"aider": {
  "type": "ai",
  "command": "aider",
  "args": [],
  "env": {
    "OPENAI_API_BASE": "http://<OLLAMA_HOST_IP>:11434/v1",
    "OPENAI_API_KEY": "ollama-local-key"
  },
  "working_dir": "{worktree_path}",
  "timeout_sec": 3600,
  "success_exit_codes": [0],
  "capture_output": true,
  "aim_tool_id": "aider",
  "aim_capabilities": ["code_edit", "refactor", "explain"],
  "preferred_model": "deepseek-coder-v2:16b"
}
```

The AI should:

* Preserve any existing, project-specific keys.
* Only add/update the minimal fields required for DeepSeek via Ollama.

### 6.2. New `ollama-code` entry

Add a new top-level entry:

```jsonc
"ollama-code": {
  "type": "ai",
  "command": "ollama-code",
  "args": [],
  "env": {
    "OLLAMA_BASE_URL": "http://<OLLAMA_HOST_IP>:11434/v1",
    "OLLAMA_MODEL": "deepseek-coder-v2:16b"
  },
  "working_dir": "{worktree_path}",
  "timeout_sec": 3600,
  "success_exit_codes": [0],
  "capture_output": true,
  "aim_tool_id": "ollama-code",
  "aim_capabilities": [
    "code_generation",
    "refactoring",
    "multi-file_edits",
    "explanation"
  ]
}
```

Notes for the AI:

* Use the **same `<OLLAMA_HOST_IP>`** as for Aider.
* `working_dir` should be the repo/worktree path the orchestrator passes in.
* `timeout_sec` can be adjusted if needed for large tasks.

---

## 7. Add PowerShell helpers (mirror `aider-wsl` style)

These helpers live in the user’s **PowerShell profile**, typically at:

* `C:\Users\richg\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`

### 7.1. `ollama-code-wsl` helper

Append something like:

```powershell
function ollama-code-wsl {
    param(
        [Parameter(Mandatory=$true)]
        [string]$RepoPath
    )

    wsl -d Ubuntu -- bash -lc @"
        cd '$RepoPath'
        export OLLAMA_BASE_URL='http://<OLLAMA_HOST_IP>:11434/v1'
        export OLLAMA_MODEL='deepseek-coder-v2:16b'
        ollama-code
"@
}
```

This gives the user a symmetric UX:

```powershell
ollama-code-wsl "C:\Path\To\Repo"
```

just like:

```powershell
aider-wsl "C:\Path\To\Repo"
```

> AI must not delete or override existing profile functions; only append.

---

## 8. Validation steps for AI

After everything is wired, AI should perform a basic smoke test:

### 8.1. Test Aider + DeepSeek

From WSL, in a test repo:

```bash
mkdir -p ~/test-deepseek-aider && cd ~/test-deepseek-aider
git init
echo "print('hello world')" > test.py
aider --version
aider << 'EOF'
You are connected to DeepSeek-Coder via Ollama. 
Please add a function named 'square' that returns x*x in test.py.
EOF
```

Check `test.py` for correct modifications.

### 8.2. Test `ollama-code`

From the same repo:

```bash
ollama-code << 'EOF'
Task: Open test.py and add a new function cube(x) that returns x*x*x.
EOF
```

Confirm that `test.py` now has `cube`.

If both tests pass, installation and wiring are considered **successful**.

---

## 9. Summary for future AI agents

When a future AI agent reads this doc and needs to **reproduce or repair** the setup, it should:

1. Confirm Ollama is installed and running on Windows.
2. Confirm DeepSeek-Coder is pulled via `ollama pull`.
3. Ensure WSL env variables point to the correct `http://<OLLAMA_HOST_IP>:11434/v1`.
4. Make sure:

   * Aider uses `OPENAI_API_BASE`, `OPENAI_API_KEY`, and `AIDER_MODEL` pointing to DeepSeek-Coder.
   * `ollama-code` uses `OLLAMA_BASE_URL` and `OLLAMA_MODEL` pointing to the same server/model.
5. Verify that both tools are declared in `tool_profiles.json` and callable via:

   * Orchestrator
   * PowerShell helpers (`aider-wsl`, `ollama-code-wsl`).

If anything breaks, the AI should compare the current state against these steps and correct any missing env vars, config files, or tool profile entries.
