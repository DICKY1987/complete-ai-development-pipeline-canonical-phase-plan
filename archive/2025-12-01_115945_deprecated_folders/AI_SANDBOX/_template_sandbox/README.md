---
doc_id: DOC-GUIDE-README-1113
---

# AI Sandbox Template

This is a template directory containing all the configuration files needed for AI-assisted development with multiple tools.

## Files Included

- `docs/DEV_RULES_CORE.md` - Canonical development rules (all tools)
- `CLAUDE.md` - Claude Code instructions
- `AGENTS.md` - Codex CLI instructions
- `.codex/config.toml` - Codex repository config
- `.aider.conf.yml` - Aider configuration
- `.github/copilot-instructions.md` - GitHub Copilot instructions

## Usage

To create a new sandbox clone:

1. Clone your project repository into AI_SANDBOX directory:
   ```powershell
   cd C:\Users\richg\AI_SANDBOX
   git clone <repo_url> project_name_sandbox
   ```

2. Copy config files from this template:
   ```powershell
   Copy-Item -Path "_template_sandbox\*" -Destination "project_name_sandbox\" -Recurse -Force
   ```

3. Initialize git if needed and commit configs:
   ```powershell
   cd project_name_sandbox
   git add .
   git commit -m "Add AI tool configurations"
   ```

4. Start using your preferred AI tool in the sandbox.

## Tool-Specific Commands

**Claude Code:**
```powershell
cd C:\Users\richg\AI_SANDBOX\project_name_sandbox
claude
```

**Codex CLI:**
```powershell
cd C:\Users\richg\AI_SANDBOX\project_name_sandbox
codex
```

**Aider:**
```powershell
cd C:\Users\richg\AI_SANDBOX\project_name_sandbox
aider
```

**GitHub Copilot CLI:**
```powershell
cd C:\Users\richg\AI_SANDBOX\project_name_sandbox
copilot --allow-all-tools
```
