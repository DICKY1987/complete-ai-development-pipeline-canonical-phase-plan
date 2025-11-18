Here’s a troubleshooting playbook you can literally hand to an AI agent (Codex, Claude Code, Gemini, etc.) to debug Aider + Ollama + DeepSeek/Qwen on your machine **systematically**.

I’ll write it as a single, self-contained procedure the AI can follow step-by-step.

---

# AIDER + OLLAMA + DEEPSEEK/QWEN

##  AIDER_OLLAMA_DEEPSEEK_QWEN_Systematic Troubleshooting Guide for AI Agents

### 0. Scope & Goal

You (the AI) are debugging issues where:

* Aider is configured to use **Ollama models** (DeepSeek, Qwen, etc.).
* Errors seen include:

  * `OllamaError: ... [WinError 10061] No connection could be made because the target machine actively refused it`
  * `PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt: file not found error`
  * `Set-Location: Cannot find path ... because it does not exist.`
* The target project is (examples from this environment):

```text
C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan
```

Your job is to:

1. Verify and fix **Ollama connectivity**.
2. Verify and fix **Aider model configuration**.
3. Verify and fix **working directory and file paths** (especially `PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt`).
4. Validate **message-file** execution and ensure Aider can actually run the PH-07 instructions.

Follow the steps **in order**. At each step, run the commands, inspect output, and branch accordingly.

---

## 1. Discover Environment & Repo State

### 1.1 Confirm the target project folder exists

**Shell commands (PowerShell):**

```powershell
Get-Item "C:\Users\richg\ALL_AI" | Format-List FullName

Get-ChildItem "C:\Users\richg\ALL_AI" | Select-Object FullName
```

**Check:**

* Look for a folder whose name matches or closely matches:

  `Complete AI Development Pipeline – Canonical Phase Plan`

  Pay attention to:

  * Special characters (en dash `–` vs hyphen `-`).
  * Extra spaces before/after words.
  * Any slight spelling differences.

**If the exact folder is NOT listed:**

* The project root moved, was renamed, or lives under a slightly different path.
* Search for it:

```powershell
Get-ChildItem "C:\Users\richg" -Recurse -Directory |
  Where-Object { $_.Name -like "*Canonical Phase Plan*" } |
  Select-Object FullName
```

* Once found, record that as `PROJECT_ROOT`.

**If the folder IS listed:**

* Set:

```powershell
$PROJECT_ROOT = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
```

(or the discovered path).

---

### 1.2 Confirm Git repo & file layout at PROJECT_ROOT

**Command:**

```powershell
Set-Location $PROJECT_ROOT
git rev-parse --show-toplevel
git status --short --branch
```

**Expected success:**

* `git rev-parse` outputs a path equal to `$PROJECT_ROOT` (or a parent).
* `git status` runs without error.

**If Git commands fail:**

* There is no repo at this folder. Aider will still run, but some features break.
* If this is supposed to be a repo, run (only if user wants):

```powershell
git init
git remote -v   # to inspect remote, if any
```

---

### 1.3 Verify the PHASE_DEV_DOCS paths

You saw this error:

```text
PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt: file not found error
```

This usually means Aider is being run from a directory where `PHASE_DEV_DOCS\...` doesn’t exist.

**Command:**

```powershell
Set-Location $PROJECT_ROOT
Get-ChildItem "$PROJECT_ROOT\PHASE_DEV_DOCS" | Select-Object Name, FullName
```

**Check:**

* Confirm that `AIDER_INSTRUCTIONS_PH07.txt` is present.

  * If yes: the **correct working directory** for Aider is `$PROJECT_ROOT`.

  * If not: locate it:

    ```powershell
    Get-ChildItem $PROJECT_ROOT -Recurse -File -Filter "AIDER_INSTRUCTIONS_PH07.txt" |
      Select-Object FullName
    ```

  * If still not found: the file is missing; AI should prompt user to recreate/restore it.

---

## 2. Verify Ollama Server & API Connectivity

Most of your original error messages:

```text
OllamaError: Error getting model info ... [WinError 10061] No connection could be made because the target machine actively refused it
```

= “No service is listening at the Ollama endpoint Aider is trying to reach.”

### 2.1 Check if Ollama service is running

**Command (PowerShell, from anywhere):**

```powershell
# See if any Ollama process is running
Get-Process | Where-Object { $_.ProcessName -like "*ollama*" }

# Simple HTTP probe
curl http://127.0.0.1:11434/api/tags
```

**Interpretation:**

* If `curl` returns JSON similar to:

  ```json
  {"models":[{"name":"deepseek-r1:latest", ...}, ...]}
  ```

  → **Ollama is running and listening on 127.0.0.1:11434**.
* If you see:

  * `curl : Unable to connect to the remote server`
  * Or timeouts / connection refused

  → Ollama is **not** running on that port.

**If Ollama is NOT running:**

Start it:

```powershell
# In a dedicated terminal
ollama serve
```

Then re-run:

```powershell
curl http://127.0.0.1:11434/api/tags
```

Only proceed when this returns JSON successfully.

---

### 2.2 Confirm models are installed

You’ve used models like:

* `qwen2.5-coder:7b`
* `deepseek-r1:latest`

**Commands:**

```powershell
ollama list
```

**Check:**

* Ensure lines like:

  ```text
  qwen2.5-coder:7b
  deepseek-r1:latest
  ```

  actually appear.

**If a model is missing:**

```powershell
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:latest
```

Verify with `ollama list` again.

---

### 2.3 Validate OLLAMA_API_BASE environment variable

Aider expects `OLLAMA_API_BASE` to point to the Ollama server; per official docs, a typical value is:

```text
http://127.0.0.1:11434
```

#### 2.3.1 Check current session value

```powershell
$env:OLLAMA_API_BASE
```

**Interpretation:**

* If blank / null → Aider falls back to defaults; can still work if Ollama is on 127.0.0.1:11434, but it’s safer to set it.
* If set: confirm it matches where `curl` worked (usually `http://127.0.0.1:11434`).

#### 2.3.2 Fix for current session

If needed:

```powershell
$env:OLLAMA_API_BASE = "http://127.0.0.1:11434"
```

Then verify:

```powershell
$env:OLLAMA_API_BASE
curl "$env:OLLAMA_API_BASE/api/tags"
```

#### 2.3.3 Persistent setting (optional)

To persist across shells (user may already have this):

```powershell
setx OLLAMA_API_BASE "http://127.0.0.1:11434"
```

> AI note: After `setx`, a **new** PowerShell session is required for the persisted value to apply.

---

## 3. Validate Aider Configuration (Models & Settings)

### 3.1 Inspect `.aider.conf.yml`

**Command:**

```powershell
Get-Content "C:\Users\richg\.aider.conf.yml"
```

In this environment, we’ve seen configurations like:

```yaml
model: ollama/qwen2.5-coder:7b        # earlier
editor-model: ollama_chat/deepcoder:14b
weak-model: ollama_chat/deepcoder:14b
# later:
model: ollama/deepseek-r1:latest
editor-model: ollama/deepseek-r1:latest
weak-model: ollama/deepseek-r1:latest
```

**Checks:**

1. **Model names must match `ollama list`.**

   * If `ollama list` shows `deepseek-r1:latest` but not `ollama/deepseek-r1:latest`, that’s still okay: Aider prefixes `ollama/` logically via litellm.
   * For safest alignment, use patterns recommended in docs:

     * `aider --model ollama/deepseek-v3`
     * or `aider --model ollama_chat/<model>` for chat-optimized interface.

2. **All three models should be valid:**

   * `model`
   * `editor-model`
   * `weak-model`

   If you are mainly using DeepSeek R1, a simple, consistent config is:

   ```yaml
   model: ollama/deepseek-r1:latest
   editor-model: ollama/deepseek-r1:latest
   weak-model: ollama/deepseek-r1:latest
   ```

3. **Optional improvement:** For better editing behavior and performance with Ollama, docs recommend `ollama_chat/<model>` for many models.

   For example:

   ```yaml
   model: ollama_chat/qwen2.5-coder:7b
   editor-model: ollama_chat/qwen2.5-coder:7b
   weak-model: ollama_chat/qwen2.5-coder:7b
   ```

   (This depends on Ollama’s model packaging; AI should confirm via `ollama list`.)

---

### 3.2 Verify `.aider.model.settings.yml` (context window etc.)

Given you’re using DeepSeek/Qwen through Ollama, context window is important; official guidance suggests setting `num_ctx` to avoid silent truncation.

**Command (from `$PROJECT_ROOT`):**

```powershell
Get-Content "$HOME\.aider.model.settings.yml" -ErrorAction SilentlyContinue
Get-Content ".aider.model.settings.yml" -ErrorAction SilentlyContinue
```

**If none exists:**

AI can propose creating one (with user approval) like:

```yaml
- name: ollama/deepseek-r1:latest
  edit_format: diff
  use_repo_map: true
  examples_as_sys_msg: true
  cache_control: false
  caches_by_default: false
  use_system_prompt: true
  use_temperature: true
  streaming: true
  extra_params:
    num_ctx: 8192
```

(Adjust `name` to match actual `model` value.)

---

### 3.3 Smoke test Aider + Ollama in a tiny sandbox

Before running on the big pipeline repo, verify connectivity in a minimal directory.

**Commands:**

```powershell
# 1. Create sandbox
New-Item -ItemType Directory -Path "$HOME\aider_sandbox" -Force | Out-Null
Set-Location "$HOME\aider_sandbox"
git init

# 2. Create a trivial Python file
"def greet(name: str) -> str:`n    return f'Hello {name}'" |
  Set-Content "app.py"

git add app.py
git commit -m "init" --author "Test <test@example.com>" --no-edit

# 3. Run aider with a trivial message
aider --model ollama/deepseek-r1:latest --message "Change the greeting to be more casual"
```

**Expected success:**

* No `WinError 10061` errors.
* Aider prints a **diff** that modifies `app.py`, commits changes (since `auto-commits` is true), and exits.

**If you still get `WinError 10061` here:**

* Re-check:

  * Ollama server is running (`ollama serve`).
  * `curl $env:OLLAMA_API_BASE/api/tags` works.
  * `OLLAMA_API_BASE` is set **in the same session** where you run `aider`.
* If `curl` works but Aider doesn’t, there may be firewall/AV interference or incorrect host/port in environment; verify with:

  ```powershell
  $env:OLLAMA_API_BASE
  ```

---

## 4. Verify Working Directory & Message-File Usage for PH-07

Your last error:

```text
PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt: file not found error
```

happened when running:

```powershell
PS C:\Users\richg> aider --message-file "PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt"
```

from **C:\Users\richg**, NOT from the project root. The relative path obviously doesn’t exist there.

### 4.1 Always `cd` to project root before running Aider on PH-07

**Command:**

```powershell
Set-Location $PROJECT_ROOT
Test-Path "PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt"
```

**Expected:**

* `True` if the file exists.

**If `False`:**

* Locate it:

  ```powershell
  Get-ChildItem $PROJECT_ROOT -Recurse -File -Filter "AIDER_INSTRUCTIONS_PH07.txt" |
    Select-Object FullName
  ```

* Adjust your path accordingly.

---

### 4.2 Run Aider with the PH-07 message-file

Once at `$PROJECT_ROOT`:

```powershell
Set-Location $PROJECT_ROOT

aider --message-file "PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt"
```

**Expected behavior:**

* Aider logs should show:

  ```text
  Git repo: .git with 324 files
  Repo-map: using ... tokens, auto refresh
  ```
* No `file not found` errors for `PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt`.
* Aider begins executing the instructions from that file:

  * Reading `PH_07_GUI_Layer_and_Plugin_System...` spec.
  * Proposing code changes in the repo.
  * Using auto-commits if enabled.

**If Aider still errors on the message file:**

* Confirm the content & encoding:

  ```powershell
  Get-Content "PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt"
  ```

* Ensure there are **no weird path assumptions** inside the file (for example, instructions that assume a different root folder).

* AI can rewrite/normalize the instructions file to refer to relative paths from `$PROJECT_ROOT`.

---

## 5. Systematic “All Possibilities” Checklist

Below is a **compact matrix** the AI should walk through and mark off:

### 5.1 Environment & Path

* [ ] `PROJECT_ROOT` exists and is correct.
* [ ] `Set-Location $PROJECT_ROOT` works with no error.
* [ ] `git rev-parse --show-toplevel` returns `$PROJECT_ROOT` (or known parent).
* [ ] `PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt` exists from `$PROJECT_ROOT`.

### 5.2 Ollama Connectivity

* [ ] `ollama serve` is running (confirmed with `Get-Process`).
* [ ] `curl http://127.0.0.1:11434/api/tags` returns JSON with model list.
* [ ] `ollama list` shows all required models (qwen2.5-coder, deepseek-r1).
* [ ] `$env:OLLAMA_API_BASE` is set to `http://127.0.0.1:11434`.
* [ ] `curl $env:OLLAMA_API_BASE/api/tags` matches `curl http://127.0.0.1:11434/api/tags`.

### 5.3 Aider Configuration

* [ ] `C:\Users\richg\.aider.conf.yml` exists and references valid models.
* [ ] `model`, `editor-model`, and `weak-model` are **all** installed in Ollama.
* [ ] Optional: `.aider.model.settings.yml` exists with appropriate `num_ctx` for chosen model.
* [ ] `aider --version` runs without error.

### 5.4 Minimal Sanity Test

* [ ] In `$HOME\aider_sandbox`, `aider --model <ollama model> --message "Change this function"` succeeds with no `WinError 10061`.
* [ ] Changes are applied & committed by Aider in the sandbox repo.

### 5.5 Full Project Execution

* [ ] From `$PROJECT_ROOT`, running:

  ```powershell
  aider --message-file "PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt"
  ```

  does **not** produce:

  * `file not found error`
  * or `WinError 10061`.

* [ ] Aider begins scanning repo & proposing edits accordingly.

If any box is unchecked, the AI should:

1. Capture the failing command and full error message.
2. Map it back to:

   * Path problem?
   * Ollama connection problem?
   * Model configuration problem?
3. Apply the relevant fix from sections 1–4, then re-run the failed step.

---

## 6. Optional Hardening / Improvements

For a more robust setup (AI can propose, user approves):

1. **Pin one “canonical” Ollama model for Aider** (e.g. `ollama/deepseek-r1:latest`).
2. **Use `.aider.model.settings.yml`** to set `num_ctx` and `edit_format: diff` explicitly for that model.
3. **Persist `OLLAMA_API_BASE`** via `setx` and document it in your pipeline docs.
4. **Create a small script** `test_aider_ollama.ps1` that:

   * Checks `curl` connectivity.
   * Runs the sandbox test.
   * Prints PASS/FAIL summary before you ever invoke big workstreams.

---

