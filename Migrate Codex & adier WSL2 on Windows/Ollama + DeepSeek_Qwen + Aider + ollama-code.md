Here’s the clean, “from the developers” way to wire **Ollama + DeepSeek/Qwen + Aider + ollama-code** so it works from **Windows *and* WSL** and you can swap models easily.

I'll break it into:

1. Overall architecture (what runs where)
2. Install & configure **Ollama on Windows**
3. Install & configure **Aider in WSL**, talking to Ollama
4. Install & configure **ollama-code (CLI)** in WSL
5. Model management & easy switching (DeepSeek/Qwen/etc.)
6. Quick checklist to confirm “correct files run on Windows and WSL”

---

## Quick Start (Local Only)

1. Windows: Install/run Ollama. Verify locally:
   - `ollama --version`, `ollama list`
   - `curl http://127.0.0.1:11434/api/tags` returns JSON
2. WSL (Ubuntu): Install tools:
   - `python -m pip install aider-install && aider-install`
   - `python -m pip install ollama-code-cli`
3. WSL: Add the bashrc block below to prefer `127.0.0.1` and fall back to Windows IP. Then:
   - `source ~/.bashrc`
   - `curl "$OLLAMA_API_BASE/api/tags"` shows models
4. Run locally (no cloud):
   - `aider --model ollama_chat/qwen2.5-coder:14b`
   - `ollama-code-cli --model deepseek-coder`

All apps run local: no cloud API keys needed; avoid Git Bash, use Windows Terminal or WSL.

---

## 1. Architecture you're aiming for

Based on the official docs and what you already have installed, the **simplest stable layout** is:

* **Windows host**

  * Runs **Ollama** daemon and stores models in
    `C:\Users\richg\.ollama\models\...` (your `qwen2.5-coder`, `deepseek-coder`, `deepseek-r1` manifests here are exactly what we expect).
  * Listens on `127.0.0.1:11434` by default for the HTTP API.([Ollama Docs][1])

* **WSL (Ubuntu)**

  * Runs **Aider** (Python) and **ollama-code CLI** (Python) as coding agents.
  * Both talk to the **Windows Ollama** server via HTTP (`http://<Windows-IP>:11434`) using environment variable `OLLAMA_API_BASE`.([Aider][2])

That gives you:

* One copy of all models on Windows (DeepSeek/Qwen/etc.).
* Multiple tools in WSL reusing those models:

  * `aider --model ollama_chat/deepseek-coder`
  * `ollama-code-cli --model qwen2.5-coder:14b`
* You can change models per command or via config files.

---

### Local-Only Policy

- No cloud endpoints: use `OLLAMA_API_BASE` only. Do not set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc., in WSL when working locally.
- Keep Aider analytics off (set `analytics: false` in config if present).
- Everything runs on `localhost` or the Windows host IP that WSL sees; no external network required at runtime.

---

## 2. Install & configure **Ollama on Windows**

### 2.1 Install Ollama (Windows)

From the official docs:

1. Download the Windows installer from Ollama’s site.([Ollama Docs][3])
2. Run `OllamaSetup.exe`. It installs into your user account and sets up the background service and CLI.

After install:

```powershell
ollama --version
ollama list
```

You should already see that your models live under:

```text
C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\
  qwen2.5-coder
  deepseek-coder
  deepseek-r1
```

Those folders mean **Ollama has downloaded those models successfully** and they’re ready to run.

### 2.2 Pull / verify your coding models

From the Ollama model library pages (examples):([Ollama][4])

```powershell
# Qwen2.5 Coder
ollama pull qwen2.5-coder:14b
# or other sizes like :7b, :3b, etc.

# DeepSeek-Coder
ollama pull deepseek-coder

# DeepSeek-R1 (reasoning)
ollama pull deepseek-r1:7b
```

Test directly in Windows:

```powershell
ollama run qwen2.5-coder:14b
# or
ollama run deepseek-coder
```

If this works in PowerShell, your **Windows+Ollama+models** layer is good.

---

## 3. Install & configure **Aider in WSL** (using Ollama)

### 3.1 Install Aider in WSL (Ubuntu)

Official Aider installation:([Aider][5])

Inside WSL:

```bash
python -m pip install aider-install
aider-install
```

That installs Aider and its dependencies in WSL.

Verify:

```bash
aider --version
```

### 3.2 Wire Aider to Windows Ollama

From the official **Aider + Ollama** docs:([Aider][2])

> Aider can connect to local Ollama models.
> Configure your Ollama API endpoint with `OLLAMA_API_BASE`.

There are **two WSL networking modes** per Microsoft’s docs: NAT vs mirrored. In either case, Aider just needs an HTTP URL for the Ollama server:([Microsoft Learn][6])

#### Option A – if `localhost:11434` works from WSL

In WSL (Ubuntu):

```bash
export OLLAMA_API_BASE="http://127.0.0.1:11434"
```

You can make it permanent by adding to `~/.bashrc`:

```bash
echo 'export OLLAMA_API_BASE="http://127.0.0.1:11434"' >> ~/.bashrc
source ~/.bashrc
```

Test from WSL:

```bash
curl "$OLLAMA_API_BASE/api/tags"
```

If you see JSON listing your models, WSL is successfully talking to Windows Ollama.

#### Option B – if `localhost` **does NOT** work in WSL

Use Microsoft’s recommendation to get the Windows host IP from inside WSL:([Microsoft Learn][6])

```bash
WIN_IP=$(ip route show | awk '/default/ {print $3}')
export OLLAMA_API_BASE="http://$WIN_IP:11434"
echo "export OLLAMA_API_BASE=\"http://$WIN_IP:11434\"" >> ~/.bashrc
source ~/.bashrc
```

Again test:

```bash
curl "$OLLAMA_API_BASE/api/tags"
```

If that returns your model list, you’re good.

> **Important:** For plain local Ollama, you **do not** need an `OPENAI_API_KEY`. That earlier “set OPENAI_API_KEY” step was only for using OpenAI’s cloud models. For Ollama you use `OLLAMA_API_BASE` and optionally `OLLAMA_API_KEY` only if your Ollama endpoint is protected.([Aider][2])

### 3.3 Use Aider with Ollama models (DeepSeek/Qwen)

Per Aider docs:([Aider][2])

1. Make sure Ollama is running and models are pulled (we did that on Windows).

2. In WSL, `cd` into your repo:

   ```bash
   cd /mnt/c/Users/richg/YourRepo   # or a WSL-native path
   ```

3. Launch Aider with an Ollama model:

   ```bash
   # Recommended: use `ollama_chat/<model>` alias
   aider --model ollama_chat/qwen2.5-coder:14b

   # or DeepSeek Coder:
   aider --model ollama_chat/deepseek-coder
   ```

Aider docs explicitly recommend `ollama_chat/<model>` instead of `ollama/<model>` when possible.([Aider][2])

#### Optional: `.aider.model.settings.yml` for larger context / per-model settings

You can define per-model settings like context window in `~/.aider.model.settings.yml`. Example from docs:([Aider][2])

```yaml
- name: ollama/qwen2.5-coder:32b-instruct-fp16
  extra_params:
    num_ctx: 65536
```

You can add entries for your DeepSeek/Qwen models and Aider will use them automatically when you specify that `--model`.

---

## 4. Install & configure **ollama-code (CLI) in WSL**

I’ll recommend the **Python-based** `ollama-code-cli` because its install and usage are clearly documented.([GitHub][7])

### 4.1 Install ollama-code-cli

Inside WSL:

```bash
python -m pip install ollama-code-cli
```

Requirements from the README:([GitHub][7])

* Python 3.10+ (they call out 3.13+ as tested)
* Ollama installed and running
* A tool-calling capable model (e.g., Qwen2.5, Qwen3, etc.) on the Ollama side

Since Ollama is on Windows and we already wired `OLLAMA_API_BASE` in WSL, that’s enough.

### 4.2 Use ollama-code-cli with your models

Examples from the official README:([GitHub][7])

```bash
# Interactive session with a specific model:
ollama-code-cli --model qwen2.5-coder:14b

# One-shot command:
ollama-code-cli --model qwen2.5-coder:14b "Explain this stack trace"

# With DeepSeek (assuming the model supports tool calling well):
ollama-code-cli --model deepseek-coder "Refactor this function for clarity"
```

It will:

* Talk to the model through Ollama (using the API URL you set in `OLLAMA_API_BASE`).
* Provide a richer “agentic” CLI with tools like `read_file`, `write_file`, `run_command`, etc., with safety prompts.([GitHub][7])

You can use **Aider for Git-aware refactoring** and **ollama-code-cli** for more free-form agentic coding or shell tool-calling, all against the same Ollama backend.

---

## 5. Managing models & switching easily (DeepSeek/Qwen/etc.)

### 5.1 Pull and list models (Windows / Ollama)

From Windows PowerShell:

```powershell
# Pull/update models
ollama pull qwen2.5-coder:14b
ollama pull deepseek-coder
ollama pull deepseek-r1:7b

# List all
ollama list
```

Official library pages confirm the tags and sizes for **Qwen2.5-coder** and **DeepSeek-R1**.([Ollama][4])

### 5.2 Switch models in Aider (WSL)

Just change the `--model`:

```bash
# DeepSeek coder for pure coding
aider --model ollama_chat/deepseek-coder

# Qwen2.5 coder (larger, stronger) for big refactors
aider --model ollama_chat/qwen2.5-coder:14b

# DeepSeek-R1 for “thinky” reasoning about architecture/tests
aider --model ollama_chat/deepseek-r1:7b
```

If you want a “default” model, create `~/.aider.conf.yml` in WSL and set:

```yaml
model: ollama_chat/qwen2.5-coder:14b
```

(Structure based on Aider’s configuration docs.([Aider][2]))

### 5.3 Switch models in ollama-code-cli

From the README examples:([GitHub][7])

```bash
ollama-code-cli --model qwen2.5-coder:14b
ollama-code-cli --model deepseek-coder
ollama-code-cli --model deepseek-r1:7b
```

You can also wrap these into small shell aliases:

```bash
echo 'alias oc-qwen="ollama-code-cli --model qwen2.5-coder:14b"' >> ~/.bashrc
echo 'alias oc-deepseek="ollama-code-cli --model deepseek-coder"' >> ~/.bashrc
source ~/.bashrc
```

---

## 6. “Correct files on Windows vs WSL” – sanity checklist

**On Windows (host)**

* Ollama installed via official installer.([Ollama Docs][3])

* Models stored under:

  ```text
  C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\
    qwen2.5-coder
    deepseek-coder
    deepseek-r1
  ```

* `ollama list` and `ollama run qwen2.5-coder:14b` work.

**On WSL (Ubuntu)**

* `aider` installed and working:

  ```bash
  aider --version
  ```

* `OLLAMA_API_BASE` set and reachable:

  ```bash
  echo $OLLAMA_API_BASE
  curl "$OLLAMA_API_BASE/api/tags"   # returns JSON listing your models
  ```

* Aider can talk to Ollama:

  ```bash
  cd /path/to/a/test/repo
  aider --model ollama_chat/deepseek-coder
  # Ask it to summarize a file or make a tiny change
  ```

* `ollama-code-cli` installed:

  ```bash
  ollama-code-cli --model qwen2.5-coder:14b "Say hello"
  ```

If all of those pass, then:

* **Windows** owns the models and GPU/CPU heavy lifting.
* **WSL** runs Aider + ollama-code, both correctly wired to your DeepSeek/Qwen models.
* You can switch between DeepSeek/Qwen/other models by changing `--model` or the Aider config.


Nice, let’s lock this in so Future-You isn’t guessing every time you reinstall or change something.

Below is:

1. A ready-to-drop **`ENV_SETUP.md`**
2. A **WSL `~/.bashrc` block**
3. A **Windows PowerShell profile block**

You can tweak paths, but this is good “canonical wiring” for:

* **Ollama (Windows)**
* **DeepSeek & Qwen coder models (via Ollama)**
* **Aider (in WSL)**
* **`ollama-code-cli` (in WSL)**

---

## 1. `ENV_SETUP.md` (drop this in your repo)

````markdown
# ENV_SETUP: Windows + WSL for Ollama, DeepSeek/Qwen, Aider & ollama-code

This document defines the **canonical environment wiring** so that:

- **Windows** runs the Ollama server and stores all models.
- **WSL (Ubuntu)** runs:
  - `aider` (AI pair programmer, Git-aware)
  - `ollama-code-cli` (agentic coding CLI)
- Both tools use the **same Ollama models** (DeepSeek, Qwen, etc.).
- You can easily switch models per command or via small aliases.

---

## 0. High-level architecture

- **Windows host**
  - Installs and runs **Ollama**.
  - Stores models under:

    ```text
    C:\Users\<USERNAME>\.ollama\models\...
    ```

  - Default HTTP API: `http://127.0.0.1:11434`

- **WSL (Ubuntu)**
  - Has **Python 3.10+** and `pip`.
  - Installs:
    - `aider` (via `aider-install`)
    - `ollama-code-cli` (via `pip`)
  - Communicates with Windows Ollama via:

    ```bash
    export OLLAMA_API_BASE="http://<WINDOWS_HOST_IP>:11434"
    ```

---

## 1. Windows: Install & configure Ollama

### 1.1 Install Ollama (Windows)

1. Download the Windows installer from the official site.  
2. Run the installer and complete setup.  
   Ollama will run a local HTTP server on port **11434** by default.

Verify in PowerShell:

```powershell
ollama --version
ollama list
````

You should see downloaded models under:

```text
C:\Users\<USERNAME>\.ollama\models\manifests\registry.ollama.ai\library\
  qwen2.5-coder
  deepseek-coder
  deepseek-r1
```

### 1.2 Pull / update coding models

In **PowerShell**:

```powershell
# Qwen 2.5 Coder (pick size you want)
ollama pull qwen2.5-coder:14b

# DeepSeek Coder
ollama pull deepseek-coder

# DeepSeek-R1 (reasoning)
ollama pull deepseek-r1:7b
```

Test that a model runs:

```powershell
ollama run qwen2.5-coder:14b
```

If you get a prompt and a response, the model is functional.

### 1.3 Optional: expose Ollama more broadly

By default, Ollama binds to `127.0.0.1:11434`.
In most modern WSL setups, **WSL can reach `127.0.0.1:11434` directly**. If not, you can:

1. Quit Ollama completely.

2. Set `OLLAMA_HOST` as a user env var (Control Panel → System → Environment Variables), e.g.:

   ```text
   OLLAMA_HOST=0.0.0.0:11434
   ```

3. Restart Ollama.

This makes the server listen on all interfaces, which WSL will definitely see.

---

## 2. WSL (Ubuntu): Install & configure Aider

### 2.1 Prereqs

Inside WSL:

```bash
# Update packages
sudo apt update

# Make sure Python & pip exist (Python 3.10+ recommended)
python3 --version
python3 -m pip --version
```

If needed:

```bash
sudo apt install -y python3 python3-pip git
```

### 2.2 Install Aider (WSL)

Use the official `aider-install` method:

```bash
python3 -m pip install aider-install
aider-install
```

Verify:

```bash
aider --version
```

### 2.3 Wire Aider to Windows Ollama

Aider uses `OLLAMA_API_BASE` to connect to Ollama.

#### Option A: `localhost` works

Try the simple case first:

```bash
echo 'export OLLAMA_API_BASE="http://127.0.0.1:11434"' >> ~/.bashrc
source ~/.bashrc
curl "$OLLAMA_API_BASE/api/tags"
```

If you see JSON listing your models, this is enough.

#### Option B: use Windows host IP (if localhost fails)

If `curl http://127.0.0.1:11434` fails in WSL, detect the Windows host IP:

```bash
WIN_IP=$(ip route show | awk '/default/ {print $3}')
echo "export OLLAMA_API_BASE=\"http://$WIN_IP:11434\"" >> ~/.bashrc
source ~/.bashrc
curl "$OLLAMA_API_BASE/api/tags"
```

You should now get model tags from the Windows Ollama server.

> **Note:** For local Ollama, you do **not** need `OPENAI_API_KEY`. That’s only for cloud APIs.

### 2.4 Run Aider with DeepSeek/Qwen models

From inside WSL:

```bash
cd /mnt/c/Users/<USERNAME>/YourRepo   # or a WSL-native path

# DeepSeek Coder
aider --model ollama_chat/deepseek-coder

# Qwen 2.5 Coder, 14B
aider --model ollama_chat/qwen2.5-coder:14b

# DeepSeek-R1 (for reasoning-heavy tasks)
aider --model ollama_chat/deepseek-r1:7b
```

* The `ollama_chat/...` prefix tells Aider to use Ollama’s `/api/chat` endpoint via `OLLAMA_API_BASE`.
* If you want a default model, create `~/.aider.conf.yml` in WSL:

  ```yaml
  model: ollama_chat/qwen2.5-coder:14b
  ```

### 2.5 Optional: per-model tuning (`.aider.model.settings.yml`)

Create `~/.aider.model.settings.yml`:

```yaml
- name: ollama_chat/qwen2.5-coder:14b
  extra_params:
    num_ctx: 32768
    num_predict: 1024

- name: ollama_chat/deepseek-coder
  extra_params:
    num_ctx: 32768
    num_predict: 1024
```

Aider uses this to set larger context windows with Ollama.

---

## 3. WSL (Ubuntu): Install & configure `ollama-code-cli`

We’ll use the official **Python-based** `ollama-code-cli` as the “ollama-code” tool.

### 3.1 Install

In WSL:

```bash
python3 -m pip install ollama-code-cli
```

Requirements: Python 3.10+ and a running Ollama server.

### 3.2 Use with your models

Because `OLLAMA_API_BASE` is already set, you only need to supply the model:

```bash
# Interactive:
ollama-code-cli --model qwen2.5-coder:14b

# One-shot:
ollama-code-cli --model deepseek-coder "List the main modules in this repo and suggest a refactor plan."
```

You can define aliases in `~/.bashrc`:

```bash
alias oc-qwen="ollama-code-cli --model qwen2.5-coder:14b"
alias oc-deepseek="ollama-code-cli --model deepseek-coder"
```

---

## 4. Quick model switching strategy

* **Aider**: switch with `--model` or set a default in `~/.aider.conf.yml`.
* **ollama-code-cli**: switch with `--model` or use aliases.

Examples:

```bash
# DeepSeek as main coding model:
aider --model ollama_chat/deepseek-coder

# Qwen for heavy lifting:
aider --model ollama_chat/qwen2.5-coder:14b

# DeepSeek-R1 for high-reasoning tasks:
aider --model ollama_chat/deepseek-r1:7b

# ollama-code-cli variants:
oc-qwen
oc-deepseek
```

---

## 5. Troubleshooting checklist

1. **From Windows PowerShell:**

   ```powershell
   ollama list
   curl http://127.0.0.1:11434/api/tags
   ```

   * If these fail, fix Ollama on Windows first.

2. **From WSL:**

   ```bash
   echo "$OLLAMA_API_BASE"
   curl "$OLLAMA_API_BASE/api/tags"
   ```

   * If this fails, fix `OLLAMA_API_BASE` or `OLLAMA_HOST` binding.

3. **Aider test:**

   ```bash
   cd /path/to/small/test/repo
   aider --model ollama_chat/deepseek-coder
   ```

   Make a tiny edit and confirm the file changes and git commit work.

4. **`ollama-code-cli` test:**

   ```bash
   cd /path/to/small/test/repo
   ollama-code-cli --model qwen2.5-coder:14b "Print the list of files in this repo."
   ```

If all 4 steps work, your **Windows + WSL + Ollama + DeepSeek/Qwen + Aider + ollama-code-cli** stack is correctly wired.

````

---

## 2. WSL `~/.bashrc` block (copy-paste)

Append this to your `~/.bashrc` in WSL (or a dedicated `ws-env.sh` that you source):

```bash
########## OLLAMA + AIDER + OLLAMA-CODE (WSL) ##########

# Resolve local Ollama endpoint: prefer localhost, else Windows host IP
if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  export OLLAMA_API_BASE="http://127.0.0.1:11434"
else
  WIN_IP=$(ip route show | awk '/default/ {print $3}')
  export OLLAMA_API_BASE="http://$WIN_IP:11434"
fi

# Local-only: avoid accidental cloud usage in this session (optional)
unset OPENAI_API_KEY ANTHROPIC_API_KEY

# Optional: quick Aider aliases for your favorite models
alias aider-ds="aider --model ollama_chat/deepseek-coder"
alias aider-qwen="aider --model ollama_chat/qwen2.5-coder:14b"
alias aider-r1="aider --model ollama_chat/deepseek-r1:7b"

# Optional: quick ollama-code-cli aliases
alias oc-qwen="ollama-code-cli --model qwen2.5-coder:14b"
alias oc-deepseek="ollama-code-cli --model deepseek-coder"

########## END OLLAMA + AIDER + OLLAMA-CODE ##########
````

Then:

```bash
source ~/.bashrc
curl "$OLLAMA_API_BASE/api/tags"
```

You should see the JSON tag list from the Windows Ollama server.

---

## 3. Windows PowerShell profile block

Pick one profile (usually `$PROFILE` for your main PowerShell) and add:

```powershell
########## OLLAMA / WSL HELPERS ##########

# Show current Ollama status quickly
function Show-OllamaStatus {
    Write-Host "Ollama models:"
    ollama list
    Write-Host "`nTesting API at http://127.0.0.1:11434/api/tags ..."
    try {
        curl http://127.0.0.1:11434/api/tags
    } catch {
        Write-Warning "Unable to reach Ollama API from Windows."
    }
}

# Launch Aider in WSL in a given repo
function aider-wsl {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoPath
    )

    if (-not (Test-Path $RepoPath)) {
        Write-Error "Repo path not found: $RepoPath"
        return
    }

    $wslPath = (wsl -d Ubuntu -- wslpath -a "$RepoPath").Trim()
    wsl -d Ubuntu -- bash -lc "cd '$wslPath' && aider"
}

# Launch ollama-code-cli in WSL in a given repo
function ollama-code-wsl {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoPath,
        [string]$Model = "qwen2.5-coder:14b"
    )

    if (-not (Test-Path $RepoPath)) {
        Write-Error "Repo path not found: $RepoPath"
        return
    }

    $wslPath = (wsl -d Ubuntu -- wslpath -a "$RepoPath").Trim()
    wsl -d Ubuntu -- bash -lc "cd '$wslPath' && ollama-code-cli --model $Model"
}

########## END OLLAMA / WSL HELPERS ##########
```

Usage from Windows:

```powershell
# Check Ollama quickly
Show-OllamaStatus

# Run Aider (WSL) on a repo
aider-wsl "C:\Users\richg\ALL_AI\SomeRepo"

# Run ollama-code-cli (WSL) on a repo using Qwen
ollama-code-wsl "C:\Users\richg\ALL_AI\SomeRepo" -Model "qwen2.5-coder:14b"
```
Cool, let’s finish wiring this up so WSL+Aider is “drop in and go” and also clear up **what lives where**.

I’ll do two things:

1. Give you **WSL-friendly Aider config files** you can paste in.
2. Answer the earlier “**what files should be in the same folder**” question at a practical level.

---

## 1. WSL Aider configs: where they go and what to put in them

Inside **WSL (Ubuntu)**:

* Aider looks for config files in your **home directory**:

  * `~/.aider.conf.yml`
  * `~/.aider.model.settings.yml`

These are **per-user**, not per-repo. They don’t live next to `engine.py` or in your Windows repo.

### 1.1 `~/.aider.conf.yml` for WSL

In WSL, run:

```bash
nano ~/.aider.conf.yml
```

Paste this as a **starting template** and adjust as needed:

```yaml
# ~/.aider.conf.yml  (WSL)

# Default model – you can change this anytime
model: ollama_chat/qwen2.5-coder:14b

# Optional editor/weak models – keep it simple at first
editor-model: ollama_chat/qwen2.5-coder:14b
weak-model: ollama_chat/deepseek-coder

# History / metadata – use WSL paths (under your Linux home)
llm-history-file: /home/<your_wsl_user>/.aider/history/.aider.llm.history
chat-history-file: /home/<your_wsl_user>/.aider/history/.aider.chat.history.md
input-history-file: /home/<your_wsl_user>/.aider/history/.aider.input.history
model-metadata-file: /home/<your_wsl_user>/.aider/config/.aider.model.metadata.json

# General behavior
timeout: 600
verbose: true
stream: false          # you can turn this on later if you like streaming
analytics: false
dark-mode: true
auto-commits: true     # Aider will commit automatically; disable if you want manual control
show-diffs: true
```

**Replace** `<your_wsl_user>` with your actual Ubuntu username (likely `richg` or similar).

You can of course simplify and just keep the `model:` line at first; the rest is “nice to have.”

---

### 1.2 `~/.aider.model.settings.yml` for WSL

Now define per-model behavior so Aider plays nicely with your Ollama models.

```bash
nano ~/.aider.model.settings.yml
```

Paste this starter version:

```yaml
# ~/.aider.model.settings.yml  (WSL)

# Qwen – big coder, general refactors
- name: ollama_chat/qwen2.5-coder:14b
  edit_format: diff
  editor_edit_format: editor-diff
  use_repo_map: true
  use_temperature: true
  streaming: false
  extra_params:
    num_ctx: 32768      # adjust based on your hardware
    num_predict: 1024   # how many tokens to generate

# DeepSeek Coder – strong pure coding model
- name: ollama_chat/deepseek-coder
  edit_format: diff
  editor_edit_format: editor-diff
  use_repo_map: true
  use_temperature: true
  streaming: false
  extra_params:
    num_ctx: 32768
    num_predict: 1024

# DeepSeek R1 – reasoning-heavy model
- name: ollama_chat/deepseek-r1:7b
  edit_format: diff
  editor_edit_format: editor-diff
  use_repo_map: true
  use_temperature: false   # keep it more deterministic
  streaming: false
  # If your Ollama template wraps reasoning in tags, you can tell Aider to strip them:
  remove_reasoning: think
  extra_params:
    num_ctx: 32768
    num_predict: 1024
```

You can tweak:

* `num_ctx` based on how big a context your box can handle.
* `num_predict` if you find it cutting off or being too verbose.
* Which model is your **default** (`model:` in `.aider.conf.yml`).

Once saved:

```bash
mkdir -p ~/.aider/history ~/.aider/config
```

Then test:

```bash
cd /mnt/c/Users/richg/SomeRepo
aider   # should use qwen2.5-coder:14b via Ollama
```

If that works, WSL+Aider is now using your best models with clean Linux paths.

---

## 2. “What files should be in the same folder?” – practical grouping

You’ve uploaded a lot of files across this project. Instead of trying to jam everything into one folder, the key is **which files belong together logically**.

Here’s a simple, safe layout you can keep in your head.

### 2.1 Your **project repo** (code + pipeline)

This is the folder you open in Git / Aider / Codex. For example:

```text
C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\
```

Inside that repo, it makes sense to keep together:

* **Pipeline code & launchers**

  * `engine.py`
  * `run_ws_wrapper.py`
  * `scripts/run_workstream.py`
* **Contracts & docs**

  * `aider_contract.md`
  * `ENV_SETUP.md` (the document we just wrote)
  * Any `*_INTEGRATION_CONTRACT.md`, `*_OPERATING_CONTRACT.md`
* **Migration/architecture docs** (if they’re part of the repo)

  * `WSL-INSTALLATION-GUIDE.md`
  * `README-WSL-MIGRATION.md`
  * `OLLAMA-LOCAL-SETUP-COMPLETE.md`
  * `START-HERE-OLLAMA.txt`

Rule of thumb:

> If it’s part of the **pipeline logic or documentation**, it belongs **inside the repo** so Git tracks it.

On **WSL**, that same repo is visible as:

```text
/mnt/c/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan/
```

and Aider should be run from there.

---

### 2.2 Your **Windows helper scripts** (PowerShell)

These can live either **inside the repo** (under a `scripts/` or `tools/` folder) or in a dedicated folder like:

```text
C:\Users\richg\ALL_AI\WSL_SETUP\
```

Examples that naturally go together:

* `WSL-Install-Step1-ADMIN-REQUIRED.ps1`
* `WSL-Install-Step2-Verify.ps1`
* `WSL-Setup-Step3-Ubuntu.ps1`
* `WSL-Install-Step4-Aider-FIXED.ps1`
* `Configure-Ollama-For-WSL.ps1`
* `WSL-Create-Launchers.ps1`
* `WSL-Validate-All.ps1`
* `START-HERE-OLLAMA.ps1` / `START-HERE.ps1`

Those do **not** need to be in the same folder as `engine.py`; they just need a stable location you remember, plus any paths they reference should match where your repo actually lives.

---

### 2.3 Your **Aider configuration** (per environment)

These **must not** live in the repo. They are **per-user / per-OS**:

* **On Windows** (if you’re still running Windows Aider sometimes):

  * `C:\Users\richg\.aider.conf.yml`
  * `C:\Users\richg\.aider.model.settings.yml`
* **On WSL** (what we just built):

  * `/home/<wsl_user>/.aider.conf.yml`
  * `/home/<wsl_user>/.aider.model.settings.yml`

They don’t have to match 1:1, but you can keep them logically similar (same defaults, same models) so you don’t get surprised when you switch environments.

---

### 2.4 Ollama’s own files

You asked earlier about:

```text
C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\qwen2.5-coder
C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\deepcoder
C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\deepseek-coder
C:\Users\richg\.ollama\models\manifests\registry.ollama.ai\library\deepseek-r1
```

All of that is **Ollama’s internal world**, and it’s already correctly grouped:

* All Ollama models and manifests are underneath:
  `C:\Users\richg\.ollama\...`

You don’t need to move or reorganize those. Just let Ollama own that tree.

---

### 2.5 Tiny mental map

* **Repo root**
  `engine.py`, `run_ws_wrapper.py`, `aider_contract.md`, `ENV_SETUP.md`, etc.
  → “Things Git should track.”

* **Windows setup folder**
  WSL/Ollama PowerShell scripts (`WSL-Install-*.ps1`, `Configure-Ollama-For-WSL.ps1`)
  → “Scripts I run manually on Windows.”

* **WSL home**
  `~/.aider.conf.yml`, `~/.aider.model.settings.yml`, `~/.bashrc` changes
  → “My Linux-side personal config.”

* **Windows home (hidden)**
  `C:\Users\richg\.ollama\...`
  → “Ollama’s stuff; leave it alone.”

---

---



[1]: https://docs.ollama.com/faq?utm_source=chatgpt.com "FAQ"
[2]: https://aider.chat/docs/llms/ollama.html "Ollama | aider"
[3]: https://docs.ollama.com/windows?utm_source=chatgpt.com "Windows"
[4]: https://ollama.com/library/qwen2.5-coder?utm_source=chatgpt.com "qwen2.5-coder"
[5]: https://aider.chat/docs/install.html "Installation | aider"
[6]: https://learn.microsoft.com/en-us/windows/wsl/networking?utm_source=chatgpt.com "Accessing network applications with WSL"
[7]: https://github.com/vigyatgoel/ollama-code-cli "GitHub - VigyatGoel/ollama-code-cli: Ollama Code CLI is an interactive command-line tool that uses local LLMs via Ollama for coding tasks and advanced tool calling."
