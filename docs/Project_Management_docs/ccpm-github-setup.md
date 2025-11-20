# CCPM GitHub setup

## Prerequisites
- Install GitHub CLI: `winget install --id GitHub.cli` (Windows) or `brew install gh` (macOS)
- Authenticate: `gh auth login` then verify with `gh auth status`

## Enable sync
1. Copy env template and set flags
   - `cp .env.example .env`
   - Set `ENABLE_GH_SYNC=true`
   - Optionally set `GITHUB_OWNER` and `GITHUB_REPO`
2. Or edit `config/github.yaml` and set `enable-sync: true`

## Quick test
```powershell
python scripts/gh_epic_sync.py --title "Epic: hello-world" --label epic:hello-world
python scripts/gh_issue_update.py --issue <number> --comment "Hello from pipeline"
```

If these fail, re-run `gh auth login` and confirm the selected repo has issue permissions.

## CCPM install parity

- Windows PowerShell:
  - `pwsh ./scripts/ccpm_install.ps1`
  - `pwsh ./scripts/ccpm_update.ps1`

- Linux/macOS (bash):
  - `bash ./scripts/ccpm_install.sh`
  - `bash ./scripts/ccpm_update.sh`

## Worktree helpers (optional)

- Windows PowerShell:
  - `pwsh ./scripts/worktree_start.ps1 -EpicName feature-x`
  - `pwsh ./scripts/worktree_merge.ps1 -EpicName feature-x`

- Linux/macOS (bash):
  - `bash ./scripts/worktree_start.sh feature-x`
  - `bash ./scripts/worktree_merge.sh feature-x`

