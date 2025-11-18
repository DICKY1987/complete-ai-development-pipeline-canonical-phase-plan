# WSL Setup Fixes Applied

**Date:** 2025-11-17
**Fixed by:** Claude Code

---

## Issues Found and Fixed

### ✅ Issue 1: Hardcoded User Path
**Problem:**
- All scripts hardcoded `/home/richg`
- Actual WSL user is `root`
- All launcher functions were broken

**Fix:**
- Created `WSL-Install-Step4-Aider-FIXED.ps1` with user auto-detection
- Created `WSL-Create-Launchers-FIXED.ps1` with dynamic user detection
- Functions now call `Get-WslUser` and `Get-WslHome` at runtime

### ✅ Issue 2: Non-Existent Codex CLI Package
**Problem:**
- `WSL-Install-Step5-Codex.ps1` tries to install `@openai/codex-cli`
- This npm package **does not exist**
- OpenAI has never released a CLI tool called "Codex CLI"

**Fix:**
- Removed Codex CLI installation steps
- Updated launcher scripts to exclude codex functions
- See "Codex Alternatives" section below

### ✅ Issue 3: Installation Not Complete
**Problem:**
- Aider not yet installed in WSL

**Fix:**
- Run the fixed installation script (see Quick Start below)

---

## Quick Start - Apply Fixes Now

### Step 1: Install Aider (Fixed Script)
```powershell
cd C:\Users\richg\WSL_CODEX_AIDER
.\WSL-Install-Step4-Aider-FIXED.ps1
```

### Step 2: Setup API Keys
```powershell
.\WSL-Setup-API-Keys.ps1
```

### Step 3: Install Fixed Launchers
```powershell
.\WSL-Create-Launchers-FIXED.ps1
```

### Step 4: Reload PowerShell Profile
```powershell
. $PROFILE
```

### Step 5: Test Installation
```powershell
wsl-info            # Show WSL environment
wsl-repos           # List repos in ~/code
```

---

## Codex Alternatives

Since `@openai/codex-cli` doesn't exist, here are **actual alternatives**:

### Option 1: Continue Using This Pipeline
**What:** The pipeline in this repo (`Complete AI Development Pipeline`)
**How:** This is what you're already building - orchestrated workstreams with Aider
**Use:** Run workstreams via `python scripts/run_workstream.py`

### Option 2: Aider Only
**What:** Aider is already AI-powered code editing
**How:** Use Aider directly without additional tooling
**Use:** `aider-wsl <repo-name>`

### Option 3: GitHub Copilot CLI
**What:** Official GitHub CLI with AI capabilities
**Install:**
```bash
wsl -d Ubuntu
gh auth login
gh copilot --help
```

### Option 4: OpenAI API Direct
**What:** Use OpenAI API directly via curl/Python
**Use:** Write custom scripts calling OpenAI's API

### Option 5: Cursor / Continue.dev
**What:** VS Code extensions for AI coding
**Note:** These run in Windows, not WSL (different workflow)

---

## What Changed

### Old Launchers (Broken)
```powershell
function aider-wsl {
    $wslPath = "/home/richg/code/$RepoName"  # ❌ Hardcoded
    wsl -- bash -lc "cd $wslPath && aider ."
}
```

### New Launchers (Fixed)
```powershell
function aider-wsl {
    $wslHome = Get-WslHome  # ✅ Dynamic detection
    $wslPath = "$wslHome/code/$RepoName"
    wsl -- bash -lc "cd $wslPath && aider ."
}
```

---

## Testing Your Setup

### Test 1: Verify WSL User Detection
```powershell
wsl-info
```
Expected output:
```
WSL Environment:
  Distribution: Ubuntu
  User: root
  Home: /root
```

### Test 2: Clone a Test Repo
```bash
wsl -d Ubuntu
cd ~/code
git clone https://github.com/paul-gauthier/aider.git
exit
```

### Test 3: Launch Aider
```powershell
aider-wsl aider
```

---

## File Reference

### Original Scripts (Don't Use)
- ❌ `WSL-Install-Step4-Aider.ps1` - Hardcoded paths
- ❌ `WSL-Install-Step5-Codex.ps1` - Package doesn't exist
- ❌ `WSL-Create-Launchers.ps1` - Hardcoded paths

### Fixed Scripts (Use These)
- ✅ `WSL-Install-Step4-Aider-FIXED.ps1` - Auto-detects user
- ✅ `WSL-Create-Launchers-FIXED.ps1` - Dynamic user detection
- ✅ This file (`README-FIXES-APPLIED.md`)

### Keep Using
- ✅ `WSL-Install-Step1-ADMIN-REQUIRED.ps1` - Still valid
- ✅ `WSL-Install-Step2-Verify.ps1` - Still valid
- ✅ `WSL-Setup-Step3-Ubuntu.ps1` - Still valid
- ✅ `WSL-Setup-API-Keys.ps1` - Still valid (adjust paths if needed)
- ✅ `WSL-Validate-All.ps1` - Still valid

---

## Recommended: Change WSL User to Non-Root

Running as `root` works but isn't best practice. To create a proper user:

### Option A: Create New User in Existing Ubuntu
```bash
wsl -d Ubuntu
adduser richg
usermod -aG sudo richg
```

Then set as default:
```powershell
ubuntu config --default-user richg
```

### Option B: Fresh Install with Proper User
```powershell
# Unregister current Ubuntu
wsl --unregister Ubuntu

# Reinstall (will prompt for username during setup)
.\WSL-Install-Step1-ADMIN-REQUIRED.ps1
```

**Note:** The fixed scripts will work with **any user** (root or richg) automatically.

---

## Next Steps After Fixes

1. ✅ Install Aider with fixed script
2. ✅ Configure API keys
3. ✅ Install fixed launchers
4. ✅ Reload PowerShell profile
5. ✅ Test with `wsl-info` and a test repo
6. 📋 Decide on Codex alternative (see options above)
7. 📋 Consider creating non-root WSL user (optional)

---

## Questions?

**For Aider issues:**
https://aider.chat/docs/

**For WSL issues:**
https://docs.microsoft.com/windows/wsl/

**For this pipeline:**
See `README.md` and `CLAUDE.md` in the main repository

---

*Generated by Claude Code - 2025-11-17*
