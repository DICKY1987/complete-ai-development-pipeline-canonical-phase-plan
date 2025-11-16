# SPEC: Migrate Codex CLI to run inside WSL2 on Windows

## 0. GOAL

Run OpenAI Codex CLI on Windows using **WSL2 + Ubuntu**, so that:

- Codex runs in a real Linux environment (Ubuntu on WSL2).
- Codex can use Linux sandboxing & semantics as intended.   
- Repos are under `~/code/...` in WSL for better performance and fewer path issues.   
- From Windows, I can still launch Codex via a simple PowerShell function, but all real work happens inside WSL.

Assume:
- Host OS: Windows 10/11 with admin access.
- Current Windows home: `C:\Users\richg`.
- Preferred WSL distro: **Ubuntu**.
- Node.js and Codex will be installed **inside WSL**, even if they already exist in Windows.

--- 

## 1. DETECT & ENABLE WSL2 (WINDOWS SIDE)

### 1.1 Detect WSL installation

In **PowerShell (Admin)**, run:

```powershell
wsl --status
