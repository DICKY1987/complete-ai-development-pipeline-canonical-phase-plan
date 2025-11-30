---
doc_id: DOC-AIM-AIM-CAPABILITIES-CATALOG-160
---

# AIM Capabilities Catalog

**Version:** 1.0
**Last Updated:** 2025-11-16

---

## Overview

This document catalogs all known capabilities supported by the AIM (AI Tools Registry) system. Each capability defines a unit of work that can be routed to one or more AI tools based on the coordination rules.

**Purpose:**
- Standardize capability names and payloads
- Define expected inputs and outputs for each capability
- Document which tools support each capability
- Provide examples for integration

---

## Capability Index

1. [code_generation](#1-code_generation)
2. [linting](#2-linting)
3. [refactoring](#3-refactoring)
4. [testing](#4-testing)
5. [version_checking](#5-version_checking)

---

## 1. code_generation

**Description:**
Generate or modify code based on natural language prompts. This includes creating new functions, classes, or files, as well as editing existing code to add features or fix bugs.

**Supported Tools:**
- **jules** (primary)
- **aider** (fallback)
- **claude-cli** (fallback)

### Payload Schema

```json
{
  "files": ["string"],
  "prompt": "string",
  "context": {
    "language": "string",
    "framework": "string",
    "additional_instructions": "string"
  }
}
```

**Field Descriptions:**
- `files` (array of strings, optional): List of file paths to edit/generate
- `prompt` (string, required): Natural language description of what to generate
- `context.language` (string, optional): Programming language (e.g., "python", "javascript")
- `context.framework` (string, optional): Framework name (e.g., "flask", "react")
- `context.additional_instructions` (string, optional): Extra guidance for the tool

### Result Schema

```json
{
  "success": true,
  "message": "Code generation completed successfully",
  "content": {
    "files_modified": ["string"],
    "files_created": ["string"],
    "lines_added": 0,
    "lines_removed": 0,
    "exit_code": 0
  }
}
```

**Field Descriptions:**
- `success` (boolean): Whether operation succeeded
- `message` (string): Human-readable status message
- `content.files_modified` (array): List of files that were changed
- `content.files_created` (array): List of new files created
- `content.lines_added` (number): Total lines added
- `content.lines_removed` (number): Total lines removed
- `content.exit_code` (number): Tool's exit code

### Example Usage

```python
from src.pipeline.aim_bridge import route_capability

result = route_capability(
    capability="code_generation",
    payload={
        "files": ["src/utils.py"],
        "prompt": "Add a retry decorator with exponential backoff",
        "context": {
            "language": "python",
            "framework": "asyncio"
        }
    }
)

if result["success"]:
    print(f"Modified: {result['content']['files_modified']}")
```

---

## 2. linting

**Description:**
Run static analysis and linting tools to check code quality, style compliance, and common errors without executing the code.

**Supported Tools:**
- Currently handled by `tool_profiles.json` (ruff, black, mypy)
- Future: Integrate with AIM for unified reporting

### Payload Schema

```json
{
  "files": ["string"],
  "linters": ["string"],
  "fix": false
}
```

**Field Descriptions:**
- `files` (array of strings, optional): Files/directories to lint (default: all)
- `linters` (array of strings, optional): Specific linters to run (e.g., ["ruff", "mypy"])
- `fix` (boolean, optional): Auto-fix issues if possible (default: false)

### Result Schema

```json
{
  "success": true,
  "message": "Linting completed with 3 warnings",
  "content": {
    "linters_run": ["string"],
    "issues_found": 0,
    "issues_fixed": 0,
    "exit_code": 0
  }
}
```

**Field Descriptions:**
- `content.linters_run` (array): List of linters executed
- `content.issues_found` (number): Total issues detected
- `content.issues_fixed` (number): Issues auto-fixed (if `fix=true`)

### Example Usage

```python
result = route_capability(
    capability="linting",
    payload={
        "files": ["src/pipeline/"],
        "linters": ["ruff", "mypy"],
        "fix": False
    }
)
```

---

## 3. refactoring

**Description:**
Restructure existing code to improve readability, maintainability, or performance without changing external behavior. Includes renaming, extracting functions, simplifying logic, and applying design patterns.

**Supported Tools:**
- **jules** (primary)
- **aider** (fallback)
- **claude-cli** (fallback)

### Payload Schema

```json
{
  "files": ["string"],
  "prompt": "string",
  "refactoring_type": "string",
  "preserve_behavior": true
}
```

**Field Descriptions:**
- `files` (array of strings, required): Files to refactor
- `prompt` (string, required): Description of refactoring goal
- `refactoring_type` (string, optional): Type of refactoring ("extract_function", "rename", "simplify", "pattern")
- `preserve_behavior` (boolean, optional): Ensure no behavior changes (default: true)

### Result Schema

```json
{
  "success": true,
  "message": "Refactoring completed successfully",
  "content": {
    "files_modified": ["string"],
    "refactorings_applied": ["string"],
    "tests_passed": true,
    "exit_code": 0
  }
}
```

**Field Descriptions:**
- `content.refactorings_applied` (array): List of refactorings performed
- `content.tests_passed` (boolean): Whether tests still pass after refactoring

### Example Usage

```python
result = route_capability(
    capability="refactoring",
    payload={
        "files": ["src/pipeline/orchestrator.py"],
        "prompt": "Extract retry logic into a separate function",
        "refactoring_type": "extract_function",
        "preserve_behavior": True
    }
)
```

---

## 4. testing

**Description:**
Generate test cases, run existing tests, or analyze test coverage. Includes unit tests, integration tests, and end-to-end tests.

**Supported Tools:**
- **pytest** (test runner, via `tool_profiles.json`)
- **aider** (test generation, via AIM)
- **jules** (test generation, via AIM)

### Payload Schema

```json
{
  "action": "string",
  "files": ["string"],
  "test_type": "string",
  "coverage": false
}
```

**Field Descriptions:**
- `action` (string, required): "generate", "run", or "analyze"
- `files` (array of strings, optional): Source files to test or test files to run
- `test_type` (string, optional): "unit", "integration", "e2e"
- `coverage` (boolean, optional): Generate coverage report (default: false)

### Result Schema

```json
{
  "success": true,
  "message": "All tests passed",
  "content": {
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "coverage_percent": 0,
    "exit_code": 0
  }
}
```

**Field Descriptions:**
- `content.tests_run` (number): Total tests executed
- `content.tests_passed` (number): Passing tests
- `content.tests_failed` (number): Failing tests
- `content.coverage_percent` (number): Code coverage percentage (if enabled)

### Example Usage

```python
# Generate tests
result = route_capability(
    capability="testing",
    payload={
        "action": "generate",
        "files": ["src/pipeline/aim_bridge.py"],
        "test_type": "unit"
    }
)

# Run tests
result = route_capability(
    capability="testing",
    payload={
        "action": "run",
        "files": ["tests/pipeline/test_aim_bridge.py"],
        "coverage": True
    }
)
```

---

## 5. version_checking

**Description:**
Check the version of installed tools and verify compatibility with required versions. Useful for ensuring development environment consistency.

**Supported Tools:**
- **All tools** (via `detectCommands` and `versionCommand` in AIM registry)

### Payload Schema

```json
{
  "tools": ["string"],
  "check_updates": false
}
```

**Field Descriptions:**
- `tools` (array of strings, optional): Specific tools to check (default: all registered tools)
- `check_updates` (boolean, optional): Check for available updates (default: false)

### Result Schema

```json
{
  "success": true,
  "message": "Version check completed",
  "content": {
    "versions": {
      "tool_id": "version_string"
    },
    "updates_available": {
      "tool_id": "new_version_string"
    }
  }
}
```

**Field Descriptions:**
- `content.versions` (object): Map of tool IDs to current versions
- `content.updates_available` (object, optional): Map of tool IDs to newer versions

### Example Usage

```python
result = route_capability(
    capability="version_checking",
    payload={
        "tools": ["aider", "jules", "claude-cli"],
        "check_updates": False
    }
)

if result["success"]:
    for tool, version in result["content"]["versions"].items():
        print(f"{tool}: {version}")
```

---

## Adding New Capabilities

To add a new capability:

1. **Define Capability:**
   - Add entry to this catalog with description, payload/result schemas, and examples
   - Choose clear, descriptive name (lowercase, underscore-separated)

2. **Update AIM Registry:**
   - Add capability to relevant tools in `.AIM_ai-tools-registry/AIM_registry.json`
   - Example: `"capabilities": ["code_generation", "new_capability"]`

3. **Update Coordination Rules:**
   - Add routing rule to `.AIM_ai-tools-registry/AIM_cross-tool/AIM_coordination-rules.json`
   - Specify primary tool and fallback chain

4. **Implement Adapter Support:**
   - Update PowerShell adapters in `.AIM_ai-tools-registry/AIM_adapters/` to handle new capability
   - Add case to switch statement in adapter script

5. **Test:**
   - Add integration test in `tests/integration/test_aim_end_to_end.py`
   - Verify routing and fallback behavior

---

## Tool Support Matrix

| Capability | Jules | Aider | Claude CLI | Notes |
|------------|-------|-------|------------|-------|
| code_generation | ✅ Primary | ✅ Fallback | ✅ Fallback | Jules preferred for speed |
| linting | ❌ | ❌ | ❌ | Use tool_profiles.json directly |
| refactoring | ✅ | ✅ | ✅ | All tools support refactoring |
| testing | ✅ | ✅ | ❌ | Test generation only |
| version_checking | ✅ | ✅ | ✅ | All tools support via registry |

**Legend:**
- ✅ Supported
- ❌ Not supported
- 🔄 Planned

---

## Document Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-16 | Initial catalog for PH-08 with 5 capabilities |

---

**End of Catalog**
