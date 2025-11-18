# WSL2 Migration Guide: Aider & Codex CLI

**Complete Installation Guide for Windows 10/11**
Generated: 2025-11-16
User: richg

---

## Overview

This guide will help you migrate **Aider** and **Codex CLI** to run inside **WSL2 (Windows Subsystem for Linux)** with Ubuntu. This provides:

- Real Linux environment for better compatibility
- Proper Unicode/UTF-8 handling for TUI applications
- Better performance for file operations
- Fewer path and line-ending issues
- Canonical development environment in `~/code`

---

## Prerequisites

- Windows 10 (version 2004+) or Windows 11
- Administrator access
- Internet connection
- ~5-10 GB free disk space

---

## Installation Steps

### Step 1: Install WSL2 (Admin Required)

**Script:** `WSL-Install-Step1-ADMIN-REQUIRED.ps1`

1. **Right-click PowerShell** and select **"Run as Administrator"**
2. Run:
   ```powershell
   .\WSL-Install-Step1-ADMIN-REQUIRED.ps1
   ```
3. **Follow prompts** - you will likely need to reboot
4. **After reboot**, Ubuntu will launch automatically and ask you to:
   - Create a UNIX username (recommended: `richg`)
   - Set a password

**What this does:**
- Installs WSL2 feature in Windows
- Downloads and installs Ubuntu as the default distro
- Sets WSL2 as the default version

---

### Step 2: Verify WSL2 Installation

**Script:** `WSL-Install-Step2-Verify.ps1`

After reboot and Ubuntu first-time setup:

```powershell
.\WSL-Install-Step2-Verify.ps1
```

**What this does:**
- Verifies WSL2 is installed correctly
- Confirms Ubuntu is running WSL version 2
- Tests connectivity to Ubuntu
- Sets WSL2 as default version if needed

---

### Step 3: Configure Ubuntu Environment

**Script:** `WSL-Setup-Step3-Ubuntu.ps1`

```powershell
.\WSL-Setup-Step3-Ubuntu.ps1
```

**What this does:**
- Updates Ubuntu packages (`apt update && upgrade`)
- Installs Python 3, pip, venv, git
- Installs Node.js and npm (for Codex CLI)
- Configures UTF-8 locale
- Creates `~/code` directory for repositories
- Creates `~/.venvs` directory for Python virtual environments

**Duration:** 5-10 minutes (depending on internet speed)

---

### Step 4: Install Aider

**Script:** `WSL-Install-Step4-Aider.ps1`

```powershell
.\WSL-Install-Step4-Aider.ps1
```

**What this does:**
- Creates Python virtual environment at `~/.venvs/aider`
- Installs `aider-chat` package
- Verifies installation

---

### Step 5: Install Codex CLI

**Script:** `WSL-Install-Step5-Codex.ps1`

```powershell
.\WSL-Install-Step5-Codex.ps1
```

**What this does:**
- Installs Codex CLI globally via npm
- Verifies installation

---

### Step 6: Configure API Keys (Optional but Recommended)

**Script:** `WSL-Setup-API-Keys.ps1`

```powershell
.\WSL-Setup-API-Keys.ps1
```

**What this does:**
- Prompts for OpenAI API key
- Prompts for Anthropic API key
- Stores keys in `~/.bashrc` in WSL
- Creates backup of existing `.bashrc`

**Security Note:** API keys are stored in plaintext in `~/.bashrc`. Keep your WSL filesystem secure.

---

### Step 7: Create PowerShell Launcher Functions

**Script:** `WSL-Create-Launchers.ps1`

```powershell
.\WSL-Create-Launchers.ps1
```

**What this does:**
- Adds launcher functions to your PowerShell profile
- Creates backup of existing profile
- Enables convenient commands to launch tools from Windows

**Functions added:**
- `aider-wsl <RepoName>` - Launch Aider in specified repo
- `aider-here-wsl` - Launch Aider in current directory's repo
- `codex-wsl <RepoName>` - Launch Codex in specified repo
- `codex-here-wsl` - Launch Codex in current directory's repo
- `wsl-code [RepoName]` - Open WSL terminal in repo or ~/code
- `wsl-repos` - List all repos in ~/code

**After running, reload your profile:**
```powershell
. $PROFILE
```

---

### Step 8: Validate Installation

**Script:** `WSL-Validate-All.ps1`

```powershell
.\WSL-Validate-All.ps1
```

**What this does:**
- Runs comprehensive validation of entire setup
- Checks WSL2, Ubuntu, Python, Node.js, Aider, Codex
- Verifies directory structure
- Checks API keys configuration
- Reports any issues

---

## Using the Tools

### Working with Repositories

All repositories should be in `~/code` inside WSL for best performance.

**Option A: Clone directly in WSL**
```bash
# Open WSL Ubuntu
wsl -d Ubuntu

# Navigate to code directory
cd ~/code

# Clone your repository
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

**Option B: Copy existing Windows repos to WSL**
```bash
# From inside WSL
cp -a /mnt/c/Users/richg/your-repo ~/code/
```

---

### Launching Aider from Windows

After cloning a repo to `~/code/my-project`:

```powershell
# From anywhere in Windows
aider-wsl my-project

# Or if you're in C:\Users\richg\code\my-project
aider-here-wsl
```

---

### Launching Codex from Windows

```powershell
# From anywhere in Windows
codex-wsl my-project

# Or from matching Windows directory
codex-here-wsl
```

---

### Launching Aider directly in WSL

```bash
# Open WSL
wsl -d Ubuntu

# Activate Aider virtual environment
source ~/.venvs/aider/bin/activate

# Navigate to your project
cd ~/code/my-project

# Run Aider
aider .
```

---

### Launching Codex directly in WSL

```bash
# Open WSL
wsl -d Ubuntu

# Navigate to your project
cd ~/code/my-project

# Run Codex
codex
```

---

## Terminal Configuration

### Recommended: Use Windows Terminal

1. Open **Windows Terminal**
2. Ensure there's a profile for **Ubuntu** (WSL)
3. Use this profile for best Unicode/UTF-8 support

### Font Recommendations

In Windows Terminal settings, set the Ubuntu profile font to:
- **Cascadia Mono** or **Cascadia Code** (included with Windows Terminal)
- **Fira Code**
- **MesloLGS NF** (Nerd Font variant)

These fonts have excellent Unicode coverage for:
- Box drawing characters
- Powerline symbols
- Emojis and icons

---

## Troubleshooting

### WSL won't install
- Ensure Windows is up to date
- Ensure virtualization is enabled in BIOS
- Run PowerShell as Administrator

### Ubuntu won't start after reboot
- Open Microsoft Store
- Search for "Ubuntu"
- Launch Ubuntu from there to complete first-time setup

### Aider shows broken Unicode characters
- Verify locale in WSL: `locale` (should show UTF-8)
- Use Windows Terminal instead of cmd.exe or PowerShell console
- Change font to Cascadia Code or similar

### Can't connect to WSL
```powershell
# Restart WSL service
wsl --shutdown
wsl -d Ubuntu
```

### API keys not working
```bash
# Verify keys are set in WSL
source ~/.bashrc
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

### PowerShell functions not available
```powershell
# Reload profile
. $PROFILE

# Or restart PowerShell
```

---

## File Locations

### Windows Side
- Scripts: `C:\Users\richg\WSL-*.ps1`
- PowerShell Profile: `C:\Users\richg\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`

### WSL Side
- Home directory: `/home/richg`
- Code repositories: `/home/richg/code` (or `~/code`)
- Aider venv: `/home/richg/.venvs/aider`
- Config file: `/home/richg/.bashrc`

### Accessing Windows from WSL
Windows drives are mounted at `/mnt/`:
- `C:\Users\richg` = `/mnt/c/Users/richg`

### Accessing WSL from Windows
Use the `\\wsl$\` path:
- `~/code` = `\\wsl$\Ubuntu\home\richg\code`

---

## Maintenance

### Update Ubuntu packages
```bash
sudo apt update
sudo apt upgrade -y
```

### Update Aider
```bash
source ~/.venvs/aider/bin/activate
pip install --upgrade aider-chat
```

### Update Codex CLI
```bash
npm update -g @openai/codex-cli
```

### Update WSL
```powershell
wsl --update
```

---

## Uninstallation

### Remove Aider
```bash
rm -rf ~/.venvs/aider
```

### Remove Codex CLI
```bash
npm uninstall -g @openai/codex-cli
```

### Remove Ubuntu distro
```powershell
wsl --unregister Ubuntu
```

### Completely remove WSL
```powershell
# In PowerShell as Admin
wsl --unregister Ubuntu
# Then disable WSL feature in Windows Features
```

---

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `wsl -d Ubuntu` | Open WSL Ubuntu |
| `wsl --shutdown` | Shutdown all WSL instances |
| `wsl --list --verbose` | List installed distros |
| `aider-wsl <repo>` | Launch Aider (from Windows) |
| `codex-wsl <repo>` | Launch Codex (from Windows) |
| `wsl-repos` | List repos in ~/code |

### Directory Paths

| Description | Windows Path | WSL Path |
|-------------|--------------|----------|
| User home | `C:\Users\richg` | `/home/richg` or `~` |
| Code repos | `\\wsl$\Ubuntu\home\richg\code` | `~/code` |
| Windows C: drive | `C:\` | `/mnt/c` |

---

## Support & Documentation

- WSL Documentation: https://docs.microsoft.com/windows/wsl/
- Aider Documentation: https://aider.chat/docs/
- Codex CLI: OpenAI documentation
- Windows Terminal: https://aka.ms/terminal

---

## Summary

You now have a complete Linux development environment running inside Windows via WSL2:

✓ WSL2 with Ubuntu
✓ Python 3 + virtual environments
✓ Node.js + npm
✓ Aider installed and ready
✓ Codex CLI installed and ready
✓ PowerShell launchers for easy access
✓ Proper UTF-8/Unicode support

**Next:** Clone a repository to `~/code` and try `aider-wsl <repo-name>`!

---

*Generated by Claude Code*
*Date: 2025-11-16*
