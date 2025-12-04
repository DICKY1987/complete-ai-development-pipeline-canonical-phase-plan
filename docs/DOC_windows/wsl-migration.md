---
doc_id: DOC-GUIDE-WSL-MIGRATION-862
---

# WSL migration: Codex CLI and Aider on Windows

This document centralizes the Windows‑first WSL2 migration guides and scripts to run Codex CLI and Aider with local Ollama models. Scripts remain in their original folder to avoid breaking changes; thin wrappers are provided under `scripts/wsl/` for convenience and consistency with repository conventions.

## Quick start

- Run `pwsh scripts/wsl/start-here.ps1` to open the guided entry.
- Validate your environment with `pwsh scripts/wsl/validate-all.ps1`.

## Common tasks

- Configure Ollama for WSL: `pwsh scripts/wsl/configure-ollama-for-wsl.ps1`
- Aider launcher for WSL: `pwsh scripts/wsl/aider-wsl.ps1`
- Ollama Code helpers: `pwsh scripts/wsl/ollama-code-wsl.ps1`

## Install sequence (wrappers)

- Step 1 (Admin): `pwsh scripts/wsl/wsl-install-step1-admin.ps1`
- Step 2 (Verify): `pwsh scripts/wsl/wsl-install-step2-verify.ps1`
- Step 3 (Ubuntu setup): `pwsh scripts/wsl/wsl-setup-step3-ubuntu.ps1`
- API keys: `pwsh scripts/wsl/wsl-setup-api-keys.ps1`
- Install Aider: `pwsh scripts/wsl/wsl-install-aider.ps1`
- Install Codex CLI: `pwsh scripts/wsl/wsl-install-codex.ps1`
- Create launchers: `pwsh scripts/wsl/wsl-create-launchers.ps1`

## Source materials

The original scripts and detailed guides live under:

- `Migrate Codex & adier WSL2 on Windows/`

Key references in that folder include:

- `README-WSL-MIGRATION.md` — migration overview
- `WSL-INSTALLATION-GUIDE.md` — end‑to‑end install guide
- `OLLAMA-SETUP-GUIDE.md`, `OLLAMA-LOCAL-SETUP-COMPLETE.md` — Ollama setup
- `Migrate Codex CLI to run inside WSL2 on Windows.md`
- `Migrate Aider to run inside WSL2 on Windows.txt`

## Notes

- The wrappers resolve paths relative to this repository, so they can be invoked from any working directory.
- Script names with spaces are preserved in place to avoid breaking existing notes and links.
- If you prefer a full relocation/rename into `scripts/` with kebab‑case filenames, say the word and we can perform a clean move and update cross‑references.

