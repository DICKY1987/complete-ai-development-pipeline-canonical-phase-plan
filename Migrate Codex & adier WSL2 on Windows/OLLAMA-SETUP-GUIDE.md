# Ollama + WSL + Aider Setup Guide

**Local-Only AI Setup** - No cloud API keys needed!

---

## Current Configuration

Your WSL is configured to use **Ollama running on Windows** with these settings:

```bash
export OLLAMA_API_BASE="http://127.0.0.1:11434"
export AIDER_MODEL="ollama_chat/deepseek-coder"
```

---

## Issue: WSL Cannot Reach Windows Ollama

### The Problem

WSL runs in a separate network namespace. By default, Ollama binds to `127.0.0.1` (localhost only), which WSL cannot reach.

**Windows host IP from WSL:** `172.27.16.1`

### Solution 1: Configure Ollama to Listen on Network Interface (Recommended)

This allows WSL to connect to Ollama running on Windows.

#### Step 1: Set Ollama Environment Variable (Windows)

**Option A: PowerShell (One-time test)**
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

**Option B: System Environment Variable (Permanent)**
1. Press `Win + X` → System
2. Advanced system settings → Environment Variables
3. Add **System Variable**:
   - Name: `OLLAMA_HOST`
   - Value: `0.0.0.0:11434`
4. Restart Ollama service or reboot

**Option C: Registry (If Ollama runs as service)**
```powershell
# Run as Administrator
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Ollama"
New-ItemProperty -Path $regPath -Name "Environment" -Value "OLLAMA_HOST=0.0.0.0:11434" -PropertyType MultiString -Force
Restart-Service Ollama
```

#### Step 2: Update WSL Configuration

Update the Ollama API base to use the Windows host IP:

```bash
wsl -d Ubuntu

# Edit ~/.bashrc
nano ~/.bashrc

# Change this line:
export OLLAMA_API_BASE="http://127.0.0.1:11434"

# To this (using Windows host IP):
export OLLAMA_API_BASE="http://172.27.16.1:11434"

# Or use dynamic resolution:
export OLLAMA_API_BASE="http://$(ip route | grep default | cut -d' ' -f3):11434"

# Save and reload
source ~/.bashrc
exit
```

#### Step 3: Test Connection

```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
exit
```

**Expected:** JSON response with model list

---

### Solution 2: Run Ollama Inside WSL (Alternative)

Install Ollama directly in WSL instead of using Windows version.

#### Install Ollama in WSL
```bash
wsl -d Ubuntu
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
exit
```

Then in WSL, use:
```bash
export OLLAMA_API_BASE="http://127.0.0.1:11434"
```

**Pros:**
- No network configuration needed
- Direct localhost access

**Cons:**
- Uses WSL resources
- Separate Ollama instance from Windows

---

## Aider Configuration for Ollama

Once Ollama is accessible, configure Aider in WSL:

### Automatic Configuration (Already Done)

Your `~/.bashrc` in WSL already has:

```bash
# ============================================================
# Ollama Configuration (Local AI Models)
# No cloud API keys needed - using local Ollama server
# ============================================================
export OLLAMA_API_BASE="http://127.0.0.1:11434"  # Update this IP!

# Tell Aider to use Ollama models
export AIDER_MODEL="ollama_chat/deepseek-coder"

# Disable cloud API requirements
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset DEEPSEEK_API_KEY
```

### Manual Configuration

If you prefer command-line arguments over environment variables:

```bash
# Launch Aider with explicit Ollama settings
aider --model ollama_chat/deepseek-coder --openai-api-base http://172.27.16.1:11434
```

### Available Ollama Models

List models available in your Ollama:

```bash
# From Windows
ollama list

# From WSL (after fixing network)
curl http://172.27.16.1:11434/api/tags
```

Common models for coding:
- `deepseek-coder` - Best for code
- `codellama` - Code-focused Llama
- `qwen2.5-coder` - Qwen coding model
- `llama3.1` - General purpose
- `mistral` - Fast general model

Pull a model:
```bash
# From Windows
ollama pull deepseek-coder

# From WSL (after fixing network)
curl -X POST http://172.27.16.1:11434/api/pull -d '{"name":"deepseek-coder"}'
```

---

## Testing Aider with Ollama

### Step 1: Verify Ollama is Accessible

```bash
wsl -d Ubuntu
curl http://172.27.16.1:11434/api/tags
# Should return JSON with model list
exit
```

### Step 2: Create Test Repository

```bash
wsl -d Ubuntu
cd ~/code
mkdir test-aider
cd test-aider
git init
echo "# Test" > README.md
git add .
git commit -m "Initial commit"

# Activate Aider venv and test
source ~/.venvs/aider/bin/activate
aider --model ollama_chat/deepseek-coder --openai-api-base http://172.27.16.1:11434

# In Aider, try:
# > Add a Python hello world script

exit
```

### Step 3: Use PowerShell Launcher

After fixing network configuration:

```powershell
aider-wsl test-aider
```

---

## Updated PowerShell Launchers for Ollama

Update your PowerShell functions to pass Ollama configuration:

### Edit Profile

```powershell
notepad $PROFILE
```

### Update aider-wsl Function

Find the `aider-wsl` function and change:

```powershell
# OLD:
wsl -d $wslDistro -- bash -lc "source ~/.venvs/aider/bin/activate && cd $wslPath && aider ."

# NEW (with explicit Ollama config):
wsl -d $wslDistro -- bash -lc "source ~/.venvs/aider/bin/activate && cd $wslPath && aider --model ollama_chat/deepseek-coder ."
```

Or just rely on the environment variables in `~/.bashrc` (already configured).

---

## Troubleshooting

### "Connection refused" or "Cannot connect"

**Check Ollama is running on Windows:**
```powershell
curl http://localhost:11434/api/tags
```

**Check from WSL:**
```bash
wsl -d Ubuntu
HOST_IP=$(ip route | grep default | cut -d' ' -f3)
echo "Windows host IP: $HOST_IP"
curl http://$HOST_IP:11434/api/tags
exit
```

**If Windows works but WSL doesn't:**
- Ollama is only listening on 127.0.0.1
- Follow "Solution 1: Configure Ollama to Listen on Network Interface" above

### "Model not found"

**List available models:**
```bash
ollama list
```

**Pull the model:**
```bash
ollama pull deepseek-coder
```

**Update Aider config:**
```bash
wsl -d Ubuntu
nano ~/.bashrc
# Change AIDER_MODEL to match your model name
export AIDER_MODEL="ollama_chat/your-model-name"
source ~/.bashrc
exit
```

### Aider asks for API key

**This means Aider isn't detecting Ollama configuration.**

**Quick fix:**
```bash
wsl -d Ubuntu
source ~/.venvs/aider/bin/activate

# Launch with explicit arguments
aider --model ollama_chat/deepseek-coder --openai-api-base http://172.27.16.1:11434

exit
```

### Slow responses

Ollama performance depends on:
- Model size (larger = slower)
- GPU availability
- System resources

**Use faster models:**
```bash
export AIDER_MODEL="ollama_chat/codellama:7b"  # Smaller, faster
```

---

## Summary: Quick Setup Checklist

### ✅ Step 1: Configure Ollama on Windows
- [ ] Set `OLLAMA_HOST=0.0.0.0:11434` (see Solution 1 above)
- [ ] Restart Ollama service
- [ ] Test: `curl http://localhost:11434/api/tags`

### ✅ Step 2: Update WSL Configuration
- [ ] Edit `~/.bashrc` in WSL
- [ ] Change `OLLAMA_API_BASE` to `http://172.27.16.1:11434`
- [ ] Run `source ~/.bashrc`

### ✅ Step 3: Test Connection
- [ ] From WSL: `curl http://172.27.16.1:11434/api/tags`
- [ ] Should return JSON with models

### ✅ Step 4: Test Aider
- [ ] Create test repo in `~/code`
- [ ] Run: `aider --model ollama_chat/deepseek-coder`
- [ ] Try a simple code change

---

## Reference: Environment Variables

### Windows (for Ollama)
```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
```

### WSL (for Aider)
```bash
export OLLAMA_API_BASE="http://172.27.16.1:11434"
export AIDER_MODEL="ollama_chat/deepseek-coder"
```

---

## Reference: Aider Model Names for Ollama

Aider uses this format for Ollama models:

```
ollama_chat/<model-name>
```

Examples:
- `ollama_chat/deepseek-coder`
- `ollama_chat/codellama`
- `ollama_chat/qwen2.5-coder`
- `ollama_chat/llama3.1`

**NOT:**
- ~~`deepseek-coder`~~ (missing prefix)
- ~~`ollama/deepseek-coder`~~ (wrong prefix)

---

*Setup guide for local Ollama + WSL + Aider - 2025-11-17*
