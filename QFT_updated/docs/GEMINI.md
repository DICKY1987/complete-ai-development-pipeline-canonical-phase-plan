# GEMINI.md

This file provides context for Gemini to understand the project structure, conventions, and commands.

## Project Overview

This is a dual-component project:

1.  **QFT Orchestrator (PowerShell)**: A headless, Windows-first orchestration engine for managing parallel AI-driven code editing workflows. It uses `aider` as a headless editor and `git` worktrees for isolation. The orchestration is defined by YAML/JSON plan files.

2.  **Modular TUI Framework (Python)**: A contract-first, pluggable terminal user interface (TUI) framework based on a Redux-like state management pattern. It is designed to be extensible with modules that can visualize data from various sources, including the QFT Orchestrator.

The two components are designed for integration but can operate independently.

## Key Technologies

*   **PowerShell 7+**: For the orchestration engine.
*   **Python 3.x**: For the TUI framework.
*   **Git**: Heavily used for version control and worktree-based parallelism.
*   **Aider**: The core AI code editing tool, used in a headless manner.
*   **Pester**: For testing PowerShell code.
*   **Pytest**: For testing Python code.
*   **JSON Schema**: For validating configuration and plan files.

## Building and Running

### PowerShell Orchestrator

*   **To Run Orchestration**:
    ```powershell
    Import-Module .\src\Application\Orchestrator.ps1 -Force
    Start-Orchestration -PlanPath .\plan\phase_plan.yaml -Concurrency 5 -Verbose
    ```

*   **To Run Tests**:
    ```powershell
    Invoke-Pester .\tests\Orchestrator.Tests.ps1 -Verbose
    ```

### Python TUI Framework

*   **To Run the TUI**:
    ```bash
    cd tui_project
    python -m host.app src/modules
    ```

*   **To Run Tests**:
    ```bash
    cd tui_project
    python -m pytest tests/
    ```

## Development Conventions

### Architecture

*   **PowerShell Orchestrator**: Follows a **Hexagonal (Ports & Adapters)** architecture.
    *   `src/Application`: Orchestration logic.
    *   `src/Domain`: Core, dependency-free business logic.
    *   `src/Adapters`: External integrations (Git, Aider, etc.).
*   **Python TUI**: Follows a **Modular/Plugin** architecture with a Redux-like state pattern.
    *   `tui_project/src/host`: The core TUI application.
    *   `tui_project/src/modules`: Pluggable TUI modules.

### Commits

*   AI-generated commits should follow the convention: `Aider: <area>: <action>`.

### Configuration and Plans

*   Orchestration is driven by plan files (e.g., `plan/phase_plan.yaml`).
*   These plans are validated against JSON schemas found in the `schemas/` directory.
*   The Python TUI modules are defined by `tui.module.yaml` manifest files, which are also validated against a JSON schema.
