# Complete AI Development Pipeline – Canonical Phase Plan

This repository hosts a structured, phase-based plan and lightweight tooling for building and operating an AI development pipeline. Start with PH-00 to establish the baseline skeleton, then proceed through subsequent phases.

## Quick Start
- Ensure PowerShell (`pwsh`) is available on Windows.
- Bootstrap directories and basic checks:
  - `pwsh ./scripts/bootstrap.ps1`
  - `pwsh ./scripts/test.ps1`

## Repository Layout
- `docs/` — architecture notes, ADRs, and specifications
- `plans/` — phase checklists and templates
- `scripts/` — automation (bootstrap, tests, exports)
- `tests/` — test files for scripts/templates
- `assets/` — diagrams and images

## Contributing
Read `AGENTS.md` for coding style, testing guidance, and PR conventions. Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).

## Phases
- `PH-00_Baseline & Project Skeleton (Codex Autonomous Phase Executor).md` — create the base structure and verify local execution.
