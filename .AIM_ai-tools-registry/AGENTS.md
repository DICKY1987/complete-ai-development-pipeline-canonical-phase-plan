# Repository Guidelines

## Project Structure & Module Organization
- Root registry: `AIM_registry.json` (canonical tool metadata and IDs).
- Adapters: `AIM_adapters/*.ps1` (one script per tool; name as `AIM_<tool>.ps1`).
- Cross‑tool rules: `AIM_cross-tool/AIM_coordination-rules.json`.
- Audit snapshots: `AIM_audit/YYYY-MM-DD/*.json` (dated capability logs).

## Build, Test, and Development Commands
- Run adapter help: `pwsh -File AIM_adapters/AIM_aider.ps1 -?` (replace with target script).
- Lint/format: `pwsh -Command "Invoke-ScriptAnalyzer .; Invoke-Formatter -Path AIM_adapters"`.
- Validate JSON quickly: `pwsh -Command "Get-ChildItem -Recurse *.json | % { Get-Content $_ | ConvertFrom-Json | Out-Null }"`.

## Coding Style & Naming Conventions
- PowerShell 7+, 2‑space indentation, no tabs.
- Functions: PascalCase; private helpers may prefix `_`.
- Parameters: PascalCase; prefer clear switches (e.g., `-DryRun`).
- Include comment‑based help in each public script/function.
- Naming pattern: `AIM_<area>` (e.g., `AIM_aider.ps1`, `AIM_coordination-rules.json`).

## Testing Guidelines
- Use Pester 5 for unit/smoke tests (store in `Tests/*.Tests.ps1`).
- At minimum, add a smoke test per adapter (loads, shows help, exits cleanly).
- Run all tests: `pwsh -Command "Invoke-Pester"`.

## Commit & Pull Request Guidelines
- Commit style: imperative + scope, e.g., `adapters: add aider adapter`, `registry: update IDs`.
- Link issues (`Fixes #123`) when applicable.
- PRs must include: concise summary, affected paths, test evidence (logs/screenshots), and rollback notes.

## Security & Configuration Tips
- Never commit secrets; read from environment or `SecureString`.
- Prefer idempotent scripts; support `-WhatIf`/`-Confirm` when practical.
- Validate incoming JSON and sanitize file paths.

## Agent‑Specific Instructions
- Adding a new tool: create `AIM_adapters/AIM_<tool>.ps1`, update `AIM_registry.json`, and extend coordination rules if needed.
- Include comment‑based help and at least one Pester smoke test.

