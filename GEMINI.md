# GEMINI.md: AI-Powered Development Guide

This document provides a comprehensive guide for AI agents and developers on how to interact with the **Complete AI Development Pipeline**.

## Project Overview

This repository contains a sophisticated, multi-agent AI development pipeline designed to automate and accelerate software development. The project is built on a custom framework called **Universal Execution Templates (UET)** and **AI Codebase Structure (ACS)**.

*   **Purpose:** To create a complete AI-assisted development pipeline.
*   **Core Technologies:** Python 3.12, PowerShell, GitHub Actions.
*   **Architecture:** A phase-based architecture (Bootstrap, Planning, Execution, etc.) with a central orchestration engine. It uses a DAG-based parallel execution model for speed.
*   **Key Features:**
    *   **Autonomous Bootstrap:** AI agents can self-configure for any project.
    *   **Multi-tool Cooperation:** The pipeline can coordinate multiple AI tools like Claude, Copilot, and Aider.
    *   **Patch-first Development:** A unified diff-based development process with validation and a ledger.
    *   **GitHub Integration:** Deep integration with GitHub Projects v2, issues, and milestones.

## Building and Running

### Development Setup

To set up the development environment, run the appropriate script for your operating system:

*   **Windows (PowerShell):**
    ```powershell
    .\scripts\setup_dev_environment.ps1
    ```
*   **Linux/macOS (Bash):**
    ```bash
    ./scripts/setup_dev_environment.sh
    ```

These scripts will install dependencies, set up pre-commit hooks, and run validation tests.

### Running Tests

This project uses `pytest` for testing.

*   **Run fast tests (for iterative development):**
    ```bash
    python -m pytest -m "not slow"
    ```
*   **Run the full test suite (before committing or creating a PR):**
    ```bash
    python -m pytest
    ```
*   **Run a specific test:**
    ```bash
    python -m pytest tests/path/to/test_file.py -k case_name
    ```

### Linting and Formatting

This project uses `pre-commit` with `black` and `isort` for code formatting and linting.

*   **Run on all files:**
    ```bash
    pre-commit run --all-files
    ```

## Development Conventions

### Coding Style

*   **Python Version:** 3.12
*   **Formatting:** `black`
*   **Import Sorting:** `isort` with the `black` profile.
*   **Naming:**
    *   Modules and packages: `snake_case`
    *   Classes: `PascalCase`
    *   Tests: `test_*` files and functions.
*   **Type Hinting:** Use type hints for non-trivial interfaces.
*   **Error Handling:** Prefer raising explicit errors over returning `None`.

### Testing

*   Use `@pytest.mark.slow` for long-running integration tests.
*   Keep fixtures in the nearest `conftest.py`.
*   Add regression tests for any changes to routing, patching, or glossary policies.

### Commits and Pull Requests

*   **Commits:** Write small, focused commits with imperative subject lines (e.g., `Add job queue retry guard`).
*   **Pull Requests:**
    *   Describe the intent, key design decisions, and test results.
    *   Include screenshots for any UI/CLI output changes.
    *   Keep changes scoped to the current repository.
