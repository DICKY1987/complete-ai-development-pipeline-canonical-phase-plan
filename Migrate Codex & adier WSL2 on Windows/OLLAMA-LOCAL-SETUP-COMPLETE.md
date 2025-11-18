# ✅ Ollama Local Setup Complete!

**Setup Type:** Local AI only - No cloud API keys
**Date:** 2025-11-17

---

## What Has Been Configured

### ✅ WSL Configuration
Your WSL Ubuntu environment is configured for **local Ollama only**:

```bash
# In ~/.bashrc:
export OLLAMA_API_BASE="http://172.27.16.1:11434"
export AIDER_MODEL="ollama_chat/deepseek-coder"

# Cloud APIs explicitly disabled:
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset DEEPSEEK_API_KEY
```

**Windows host IP:** `172.27.16.1`

### ✅ Aider Configuration
- **Installation:** `/root/.venvs/aider` (version 0.86.1)
- **Model:** `ollama_chat/deepseek-coder`
- **API Base:** Ollama on Windows host
- **No cloud APIs:** All requests go to local Ollama

### ✅ PowerShell Launchers
- Functions in your PowerShell profile
- Launch Aider with: `aider-wsl <repo-name>`

---

## ⚠️ CRITICAL: Enable WSL Access to Ollama

**Current Issue:** Ollama runs on Windows but WSL cannot reach it yet.

### Why This Happens

By default, Ollama listens only on `127.0.0.1` (localhost). WSL needs to connect via the Windows host IP (`172.27.16.1`), which requires Ollama to listen on `0.0.0.0`.

### 🚀 Quick Fix (Choose One)

#### Option 1: Run Configuration Script (Easiest)

```powershell
cd C:\Users\richg\WSL_CODEX_AIDER
.\Configure-Ollama-For-WSL.ps1
```

This interactive script will:
1. Check if Ollama is installed
2. Configure `OLLAMA_HOST=0.0.0.0:11434`
3. Guide you through testing

#### Option 2: Manual Configuration

**Set environment variable:**

1. Press `Win + X` → System
2. Advanced system settings → Environment Variables
3. Under **User variables**, click **New**:
   - Name: `OLLAMA_HOST`
   - Value: `0.0.0.0:11434`
4. Click OK

**Restart Ollama:**
- Close any running Ollama processes
- Reboot, or run: `ollama serve`

#### Option 3: PowerShell One-Liner (Test Mode)

```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

This works for the current session only (good for testing).

---

## Testing the Setup

### Step 1: Test Ollama from Windows

```powershell
curl http://localhost:11434/api/tags
```

**Expected:** JSON response listing your models

### Step 2: Test Ollama from WSL

```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
exit
```

**Expected:** Same JSON response

**If it fails:**
- Ollama isn't configured to listen on `0.0.0.0` yet
- Run the configuration script (see above)

### Step 3: Test Aider

```bash
wsl -d Ubuntu
cd ~/code
mkdir test-repo
cd test-repo
git init
echo "# Test" > README.md
git add . && git commit -m "init"

source ~/.venvs/aider/bin/activate
aider

# In Aider prompt, try:
> Add a Python hello world script
```

**If it works:** Aider will generate code using your local Ollama!

---

## Available Models

### Check What's Installed

```powershell
ollama list
```

### Recommended Models for Coding

| Model | Size | Speed | Quality | Pull Command |
|-------|------|-------|---------|--------------|
| `deepseek-coder` | ~6GB | Medium | Best | `ollama pull deepseek-coder` |
| `qwen2.5-coder` | ~4GB | Fast | Good | `ollama pull qwen2.5-coder` |
| `codellama` | ~4GB | Fast | Good | `ollama pull codellama` |
| `llama3.1` | ~5GB | Medium | Good (general) | `ollama pull llama3.1` |

### Pull a Model

```powershell
ollama pull deepseek-coder
```

### Change Default Model

Edit `~/.bashrc` in WSL:

```bash
wsl -d Ubuntu
nano ~/.bashrc

# Change this line:
export AIDER_MODEL="ollama_chat/deepseek-coder"

# To your preferred model:
export AIDER_MODEL="ollama_chat/qwen2.5-coder"

# Save and reload:
source ~/.bashrc
exit
```

---

## Using Aider with Local Ollama

### Method 1: Use PowerShell Launcher (Automatic)

```powershell
# Reload profile first (one time)
. $PROFILE

# Launch Aider for any repo
aider-wsl <repo-name>
```

The launcher automatically:
- Activates Aider venv
- Uses Ollama configuration from `~/.bashrc`
- Connects to local models

### Method 2: Manual Launch (More Control)

```bash
wsl -d Ubuntu
cd ~/code/<your-repo>
source ~/.venvs/aider/bin/activate

# Use environment variables (from .bashrc)
aider

# Or specify explicitly:
aider --model ollama_chat/deepseek-coder --openai-api-base http://172.27.16.1:11434

exit
```

### Method 3: One-Line from PowerShell

```powershell
wsl -d Ubuntu -- bash -lc "source ~/.venvs/aider/bin/activate && cd ~/code/<repo> && aider"
```

---

## Troubleshooting

### "Connection refused" or "Cannot connect to API"

**Cause:** Ollama not configured for WSL access

**Solution:**
```powershell
.\Configure-Ollama-For-WSL.ps1
```

Then test:
```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
exit
```

### "Model 'deepseek-coder' not found"

**Cause:** Model not pulled yet

**Solution:**
```powershell
ollama pull deepseek-coder
```

### Aider asks for OpenAI API key

**Cause:** Aider isn't detecting Ollama config

**Solution:** Launch with explicit arguments:
```bash
aider --model ollama_chat/deepseek-coder --openai-api-base http://172.27.16.1:11434
```

Or check `~/.bashrc` has the Ollama configuration:
```bash
wsl -d Ubuntu
grep OLLAMA ~/.bashrc
exit
```

### Slow responses

**Cause:** Model too large for your hardware

**Solution:** Use a smaller/faster model:
```bash
export AIDER_MODEL="ollama_chat/qwen2.5-coder:7b"
```

### WSL can't find Ollama at 172.27.16.1

**Cause:** Windows host IP changed (dynamic)

**Solution:** Update IP in `~/.bashrc`:
```bash
wsl -d Ubuntu

# Get current Windows IP
ip route | grep default

# Update ~/.bashrc with new IP
nano ~/.bashrc
# Change: export OLLAMA_API_BASE="http://172.27.16.1:11434"
# To:     export OLLAMA_API_BASE="http://<new-ip>:11434"

source ~/.bashrc
exit
```

---

## Complete Workflow Example

### 1. Configure Ollama (One Time)

```powershell
cd C:\Users\richg\WSL_CODEX_AIDER
.\Configure-Ollama-For-WSL.ps1
# Choose option 1 or 2, then restart Ollama
```

### 2. Pull a Coding Model

```powershell
ollama pull deepseek-coder
```

### 3. Test Connection

```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
exit
```

### 4. Clone Your Project to WSL

```bash
wsl -d Ubuntu
cd ~/code
git clone https://github.com/your/repo.git my-project
exit
```

### 5. Launch Aider

```powershell
aider-wsl my-project
```

### 6. Use Aider

```
Aider v0.86.1
Model: ollama_chat/deepseek-coder
Repo: /root/code/my-project

> Add a Python script that prints "Hello, Local AI!"
```

Aider will:
1. Connect to local Ollama (no internet needed)
2. Generate code using deepseek-coder
3. Make changes to your repository
4. All processing happens locally!

---

## Benefits of Local Setup

### ✅ Advantages

- **Privacy:** Code never leaves your machine
- **Cost:** No API fees
- **Speed:** No network latency (LAN speed only)
- **Offline:** Works without internet
- **Control:** Choose any open-source model

### ⚠️ Considerations

- **Hardware:** Requires GPU for good performance
- **Models:** Smaller than GPT-4 (but often good enough)
- **Setup:** Slightly more complex than cloud APIs

---

## Configuration Files Reference

### Windows
- **Ollama config:** Environment variable `OLLAMA_HOST=0.0.0.0:11434`
- **Check:** System Properties → Environment Variables

### WSL (`/root/.bashrc`)
```bash
export OLLAMA_API_BASE="http://172.27.16.1:11434"
export AIDER_MODEL="ollama_chat/deepseek-coder"
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset DEEPSEEK_API_KEY
```

### PowerShell Profile
```powershell
# Location: C:\Users\richg\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1

function aider-wsl { ... }  # Launches Aider with Ollama config
function wsl-info { ... }    # Shows WSL environment
```

---

## Documentation

All documentation in `C:\Users\richg\WSL_CODEX_AIDER\`:

- **`OLLAMA-LOCAL-SETUP-COMPLETE.md`** (this file) - Complete guide
- **`OLLAMA-SETUP-GUIDE.md`** - Detailed technical reference
- **`Configure-Ollama-For-WSL.ps1`** - Configuration script
- **`SETUP-COMPLETE.md`** - Original setup documentation
- **`QUICK-FIX-GUIDE.md`** - Quick fixes reference

---

## Next Steps

### 1. ⚠️ Configure Ollama for WSL (Required)

```powershell
.\Configure-Ollama-For-WSL.ps1
```

### 2. Pull a Model

```powershell
ollama pull deepseek-coder
```

### 3. Test Everything

```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
exit
```

### 4. Start Coding!

```powershell
aider-wsl <your-repo>
```

---

## Summary

✅ **Aider installed** in WSL
✅ **Ollama configured** to use local models only
✅ **No cloud API keys** needed or used
✅ **PowerShell launchers** ready
⚠️ **Action required:** Configure Ollama to listen on network interface

**Run this to enable:**
```powershell
.\Configure-Ollama-For-WSL.ps1
```

---

*Local AI setup - privacy-focused, cloud-free - 2025-11-17*
