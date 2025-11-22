# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This directory (`pipeline_plus/`) contains **documentation and specifications** for an AI development pipeline. It defines:

- **Workstream prompt templates** (WORKSTREAM_V1.1 format) for multiple AI tools
- **Agent Operations Specification** (v1.0.0) governing prompt rendering, task routing, patch management, and multi-agent cooperation
- **Integration guidance** for orchestration scripts, tool routing, and refactoring workflows

This is a **specification/documentation directory** rather than executable code. Files here define templates, rules, and contracts that are implemented in the parent `pipeline_plus/` orchestration codebase.

## Key Documents

### Core Specifications

- **`AGENT_OPERATIONS_SPEC version1.0.0`** - Master specification containing:
  - `PROMPT_RENDERING_SPEC` - Principles for clarity, constraints, ASCII-only output, section structures
  - `TASK_ROUTING_SPEC` - Capability registry, tool selection rules, circuit breakers, timeouts
  - `PATCH_MANAGEMENT_SPEC` - Unified diff as canonical change format, rollback strategies
  - `COOPERATION_SPEC` - Orchestrator contracts, queue protocols, prohibited behaviors

- **`Aider-tuned WORKSTREAM_V1.md`** - Tool-specific prompt templates for Aider and Codex CLI

### Integration Documentation

- **`orchestration-scripts.md`** - Comprehensive reference for all pipeline scripts, triggers, and data flow
- **`seven pipeline_plus docs fit together.md`** - Guide for integrating the doc set into an existing pipeline

### Supplementary Specs

- **`# ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC_V1.md`** - Router configuration and prompt template details
- **`# Comprehensive Integration Specification Enhanced Prompt Engineering.md`** - Extended prompt engineering guidance
- **`# Patch Files as Unified Diff & Optimal .md`** - Patch file format specification

## Working with These Specifications

### Workstream Prompt Template (WORKSTREAM_V1.1)

All workstream prompts follow this section order:
```
[HEADER] -> [OBJECTIVE] -> [CONTEXT] -> [FILE_SCOPE] -> [TASKS/TASK_BREAKDOWN]
-> [CONSTRAINTS] -> [EXPECTED_OUTPUT/OUTPUT_FORMAT] -> [VALIDATION_PLAN/VALIDATION]
-> [NEXT_STEPS] -> [EXECUTION_NOTES_FOR_ROUTER]
```

Required fields in `[HEADER]`:
- `WORKSTREAM_ID`, `REPO_ROOT`, `ENTRY_FILES`, `TARGET_APP`, `CLASSIFICATION`, `RISK_LEVEL`

### Key Principles (from AGENT_OPERATIONS_SPEC)

1. **ASCII-only output** - No emojis, smart quotes, or unicode in prompts for CLI tools
2. **Tool-neutral core** - Base templates work across Aider, Codex, Claude Code; tool hints are separate sections
3. **File scope first** - Always declare `files_scope` and `files_may_create` before listing tasks
4. **Unified diff as canonical** - All code changes are represented as patch files
5. **Circuit breakers** - Prevent infinite loops with max retries, timeout limits, error signature detection

### Tool-Specific Execution Hints

- **Aider**: Files passed via CLI args, not `/add` in prompt; expect patch-friendly diffs
- **Codex CLI**: TUI/non-interactive mode, edits files on disk directly
- **Claude Code**: Request explicit plan section before code edits

## Relationship to Parent Codebase

These specifications are implemented in the parent pipeline repository at:

```
../          (parent directory)
  core/      - State management, orchestrator engine
  error/     - Error detection engine and plugins
  scripts/   - CLI entry points (run_workstream.py, validate_workstreams.py, etc.)
  config/    - tool_profiles.json, circuit_breakers.yaml
  schema/    - workstream.schema.json, schema.sql
  aider/     - Prompt engine and Jinja templates
```

When modifying these specs, corresponding changes may be needed in:
- `config/tool_profiles.json` - Tool adapter configurations
- `aider/templates/prompts/*.j2` - Prompt rendering templates
- `core/engine/orchestrator.py` - Orchestration logic
- `schema/workstream.schema.json` - Bundle validation schema

## Authoring Conventions

### Document Naming
Files with `#` prefix indicate major specification documents that define formal contracts.

### Section Delimiters
Use bracketed uppercase headers: `[HEADER]`, `[OBJECTIVE]`, `[CONSTRAINTS]`, etc.

### Classification Enums
- **complexity_level**: `simple | moderate | complex | enterprise`
- **risk_level**: `low | medium | high | critical`
- **domain**: `code | docs | infra | analysis`
- **operation_type**: `refactor | bugfix | feature | analysis_only | test_only`

### State Machine States
- **Run states**: `pending -> running -> completed/failed`
- **Workstream states**: `pending -> editing -> static_check -> runtime_tests -> done/failed`
- **Error states**: `NEW -> ANALYZING -> ANALYZED -> FIXING -> FIXED -> VERIFYING -> VERIFIED`

## Important Rules

### From Parent CLAUDE.md
- **DateTime**: Always use real system datetime (ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`)
- **Paths**: Use relative paths from project root, never absolute paths
- **GitHub**: Check for template repo before write operations

### Specification-Specific
- Do not embed tool-specific syntax (Aider slash commands, etc.) in core templates
- Tool hints must live in `[*_EXECUTION_HINTS]` sections
- Patches must include `task_id`, `workstream_id`, `source_tool_id` metadata
- Do not alter Agent Operations Spec from within workstreams; use governance workstreams
