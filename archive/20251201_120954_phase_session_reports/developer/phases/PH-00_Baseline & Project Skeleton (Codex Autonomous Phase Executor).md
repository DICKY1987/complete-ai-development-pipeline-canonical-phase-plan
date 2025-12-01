---
doc_id: DOC-GUIDE-PH-00-BASELINE-PROJECT-SKELETON-CODEX-1229
---

%# PH-00 — Baseline & Project Skeleton (Codex Autonomous Phase Executor)

Establish the initial repository structure, tooling, and conventions so later phases can execute autonomously and consistently.

## Objectives & Outcomes
- Create a clear project skeleton (dirs, seed files, scripts).
- Document build/test commands and contribution rules (see `AGENTS.md`).
- Verify local development works end-to-end (bootstrap + test).
- Produce artifacts: baseline tree, scripts, and this phase report.

## Inputs & Assumptions
- OS: Windows with PowerShell (`pwsh`) available.
- Optional: Python 3.10+, Node.js 18+, Git installed and configured.
- Network access may be restricted; prefer offline-friendly steps.

## Repository Skeleton (proposed)
```
./
├─ docs/
├─ plans/
├─ scripts/
│  ├─ bootstrap.ps1        # env checks, optional setup
│  └─ test.ps1             # runs fast test/linters if present
├─ tests/
├─ assets/
├─ AGENTS.md
└─ README.md
```
Notes: keep automation in `scripts/`; put diagrams in `assets/`; specs and ADRs in `docs/`.

## Bootstrap Checklist
- [ ] Create required folders: `docs/`, `plans/`, `scripts/`, `tests/`, `assets/`.
- [ ] Add or update `AGENTS.md` and `README.md`.
- [ ] Seed `scripts/bootstrap.ps1` and `scripts/test.ps1` (stub is acceptable).
- [ ] Confirm `pwsh scripts/test.ps1` executes (even if it no-ops initially).
- [ ] Commit with Conventional Commit (e.g., `chore: scaffold repository skeleton`).

## Example Commands (PowerShell)
```powershell
# create folders (idempotent)
New-Item -ItemType Directory docs,plans,scripts,tests,assets -Force | Out-Null

# optional: python venv
python -m venv .venv; .venv/Scripts/Activate.ps1; pip install -U pip

# optional: node setup
# npm ci

# run tests (if present)
pwsh scripts/test.ps1
```

## Acceptance Criteria
- [ ] Directory skeleton exists and matches this plan.
- [ ] Build/test commands documented in `AGENTS.md` and verified locally.
- [ ] Linting/testing (if configured) runs without errors.
- [ ] No secrets or large binaries committed; `.env.example` provided if env vars used.

## Risks & Mitigations
- Tooling drift: pin versions in scripts; prefer local venv.
- Network limits: avoid install steps in CI; cache or vendor as needed.

## Handover to PH-01
With the skeleton in place, proceed to requirements capture and architecture exploration (PH‑01), using `docs/` for artifacts and `plans/` for phase checklists.
