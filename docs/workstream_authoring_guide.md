# Workstream Authoring Guide

This guide explains how to author `workstreams/*.json` files, which define discrete units of work for the AI Development Pipeline. These workstreams are crucial for guiding AI agents and human developers through the implementation of specific changes.

## 1. Purpose of Workstream Bundles

Workstream bundles (`.json` files) serve as the atomic units of execution within the AI Development Pipeline. They encapsulate all necessary information for an AI agent (like Aider) or a human to understand, implement, and verify a specific change.

They relate to:
- **OpenSpec changes (`openspec_change`, `gate`):** Each workstream should ideally correspond to a single, focused change identified in an OpenSpec document. The `gate` field indicates the specific stage or gate within the OpenSpec process this workstream addresses.
- **CCPM / issues (`ccpm_issue`):** Workstreams can be linked to specific issues or tasks in a Continuous Codebase Project Management (CCPM) system, providing traceability.
- **Files, tasks, and tests:** Each workstream explicitly defines the files it intends to modify or create, the tasks to be performed, and the acceptance criteria to verify successful completion.

## 2. Where Bundles Live

By default, workstream bundles are located in the `<PROJECT_ROOT>/workstreams/` directory.
You can override this default location by setting the `PIPELINE_WORKSTREAM_DIR` environment variable.

For the schema definition and validation logic, refer to `schema/workstream.schema.json` and `src/pipeline/bundles.py` respectively.

## 3. Required Fields (Aligned with JSON Schema)

Workstream bundles must adhere to the `workstream.schema.json`. Below are the key fields:

-   `id` (string, pattern: "ws-...")
    -   A unique identifier for the workstream, typically prefixed with `ws-` (e.g., `ws-implement-user-auth`).
-   `openspec_change` (string)
    -   The ID of the OpenSpec change this workstream addresses (e.g., `OS-1234`).
-   `ccpm_issue` (integer)
    -   The ID of the corresponding CCPM issue or task (e.g., `42`).
-   `gate` (integer)
    -   The OpenSpec gate number this workstream targets (e.g., `1`).
-   `files_scope` (array of strings)
    -   A list of file paths (relative to project root) that this workstream is allowed to modify or read.
    -   Example: `["src/module/foo.py", "scripts/something.ps1"]`
-   `files_create` (array of strings, optional)
    -   A list of file paths (relative to project root) that this workstream is expected to create.
    -   Example: `["src/module/new_component.py"]`
-   `tasks` (array of strings)
    -   A list of high-level tasks or objectives for the workstream. These should be clear, actionable statements.
    -   Example: `["Implement X feature in foo.py", "Add Y PowerShell script to automate Z"]`
-   `acceptance_tests` (array of strings, optional)
    -   A list of commands or descriptions of tests that, when executed, verify the successful completion of the workstream's tasks.
    -   Example: `["pytest -q", "pwsh -File scripts/run_smoke_tests.ps1"]`
-   `depends_on` (array of strings, optional)
    -   A list of `id`s of other workstreams that must be completed before this workstream can start.
    -   Example: `["ws-other-workstream-id"]`
-   `tool` (string)
    -   The primary tool intended to execute this workstream (e.g., `aider`, `codex`, `claude`).
-   `circuit_breaker` (object, optional)
    -   Configuration for the circuit breaker mechanism to prevent infinite loops or excessive retries.
    -   `max_attempts` (integer): Maximum number of attempts for the workstream.
    -   `max_error_repeats` (integer): Maximum number of times the same error can repeat.
    -   `oscillation_threshold` (integer): Threshold for detecting oscillation between states.
-   `metadata` (object, optional)
    -   A free-form object for additional, non-schema-critical information.
    -   `owner` (string): The team or individual responsible.
    -   `notes` (string): Any additional notes.

## 4. Authoring Rules

To ensure clarity, maintainability, and efficient execution by AI agents, follow these rules:

-   **Single OpenSpec Change:** Use a SINGLE `openspec_change` per workstream. If a larger OpenSpec change requires multiple distinct implementation steps, break it down into multiple workstreams.
-   **Reasonable Size:** Keep workstreams reasonably sized, typically 3–7 tasks. Overly large workstreams become difficult to manage and debug.
-   **Avoid Overlapping `files_scope`:** Minimize overlapping `files_scope` entries between different workstreams unless absolutely necessary and carefully managed. Overlaps can lead to conflicts and unpredictable behavior.
-   **Use `depends_on` for Logical Sequencing:** Use the `depends_on` field when one workstream logically requires another to finish first (e.g., a backend API change must precede a frontend integration).
-   **Meaningful Descriptions:** Provide clear and meaningful descriptions for `tasks` and `acceptance_tests`. These descriptions are critical for both AI agents and humans to understand what "done" looks like and how to verify it.

## 5. Step-by-Step Authoring Workflow

1.  **Identify OpenSpec Change(s):** Begin by identifying the specific OpenSpec change(s) you intend to implement.
2.  **Break into Workstreams:** Decompose the larger change into smaller, manageable workstreams. Consider logical groupings such as:
    -   Backend changes vs. Frontend changes
    -   PowerShell scripts vs. Python modules
    -   Core logic vs. Tests vs. Documentation
3.  **Define Workstream Details:** For each workstream:
    -   Define a unique `id` (e.g., `ws-add-user-model`).
    -   Specify the `openspec_change`, `ccpm_issue`, and `gate`.
    -   List the `files_scope` (files to be modified/read) and `files_create` (files to be created).
    -   Outline the `tasks` to be performed.
    -   Provide `acceptance_tests` to verify completion.
    -   Select the appropriate `tool` (e.g., `aider`).
    -   Add `depends_on` if necessary.
4.  **Fill in the Template:** Use the canonical template (`templates/workstream_template.json`) as a starting point. Copy it, rename it (e.g., `workstreams/ws-my-new-feature.json`), and fill in the details.
5.  **Run the Validator:** After authoring, run the workstream validator script:
    ```bash
    python scripts/validate_workstreams_authoring.py
    ```
    This script will check for schema compliance, dependency issues, and file scope overlaps.
6.  **Fix Validation Errors:** Address any errors reported by the validator. Repeat step 5 until all workstreams pass validation.
7.  **Commit Bundles to Git:** Once validated, commit your workstream bundles to your Git repository.

## 6. Example

Consider an OpenSpec change `OS-5678` to add a new user authentication module. This might be broken down into two workstreams:

-   `ws-implement-auth-backend`: Handles database schema, API endpoints, and core authentication logic.
-   `ws-integrate-auth-frontend`: Updates UI components to use the new backend, adds login/logout forms.

Here's a simplified example of `workstreams/ws-implement-auth-backend.json`:

```json
{
  "id": "ws-implement-auth-backend",
  "openspec_change": "OS-5678",
  "ccpm_issue": 101,
  "gate": 2,
  "files_scope": [
    "src/backend/auth.py",
    "src/backend/models.py",
    "schema/database.sql"
  ],
  "files_create": [
    "src/backend/auth_routes.py"
  ],
  "tasks": [
    "Define User model in models.py",
    "Implement authentication logic in auth.py",
    "Create API routes in auth_routes.py",
    "Update database.sql with user table schema"
  ],
  "acceptance_tests": [
    "pytest tests/backend/test_auth.py",
    "curl -X POST /api/register -d '{\"username\": \"test\", \"password\": \"pass\"}'"
  ],
  "depends_on": [],
  "tool": "aider",
  "circuit_breaker": {
    "max_attempts": 5,
    "max_error_repeats": 3,
    "oscillation_threshold": 2
  },
  "metadata": {
    "owner": "backend-team",
    "notes": "Initial implementation of user authentication backend."
  }
}
```

This example demonstrates how a larger feature is decomposed, with clear tasks, file scopes, and verification steps. The `depends_on` field is empty here, assuming this is a foundational workstream. If a frontend workstream depended on this, its `depends_on` would include `"ws-implement-auth-backend"`.
