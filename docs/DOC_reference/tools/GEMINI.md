---
doc_id: DOC-GUIDE-GEMINI-1373
---

# GEMINI.md

## Project Overview

This project is a Python-based AI development pipeline orchestrator. It is designed to automate the process of software development by running a series of steps, including code generation, static analysis, and testing. The pipeline is driven by "workstreams," which are defined in YAML files and represent a set of tasks to be completed.

The core of the project is the orchestrator, located in `src/pipeline/orchestrator.py`. The orchestrator runs a workstream through a sequence of steps:

*   **EDIT**: This step uses an AI-powered tool called "aider" to modify the codebase based on a given prompt.
*   **STATIC**: This step runs static analysis tools to check the code for errors and style issues.
*   **RUNTIME**: This step runs runtime tests (using `pytest`) to ensure the code is working correctly.

A key feature of this pipeline is the "FIX loop," which attempts to automatically fix errors detected in the STATIC and RUNTIME steps by using `aider` to generate a patch.

The project also includes a system for managing and integrating AI tools, referred to as the "AI Tools Registry" (AIM).

## Building and Running

The project uses a set of PowerShell scripts for bootstrapping and testing.

*   **Bootstrap:** `pwsh ./scripts/bootstrap.ps1`
*   **Run tests:** `pwsh ./scripts/test.ps1`

### OpenSpec Workflow

The primary workflow for using the pipeline is the "OpenSpec" workflow:

1.  **Create a proposal:**
    ```
    /openspec:proposal "Your feature description"
    ```

2.  **Convert to workstream:**
    ```bash
    python scripts/spec_to_workstream.py --interactive
    ```

3.  **Validate and run:**
    ```bash
    python scripts/validate_workstreams.py
    python scripts/run_workstream.py --ws-id ws-<id>
    ```

4.  **Archive completed work:**
    ```
    /openspec:archive <change-id>
    ```

## Development Conventions

*   **Contributing:** See `AGENTS.md` for coding style, testing guidance, and PR conventions.
*   **Commit Messages:** Use Conventional Commits (e.g., `docs: add phase overview`, `chore: scaffold skeleton`).
*   **Dependencies:** The project's Python dependencies are listed in `requirements.txt`.
