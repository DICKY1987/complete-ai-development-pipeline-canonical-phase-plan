# Game Board Protocol - Agentic Development System

A self-referential AI development system that uses its own methodology to build itself. The Game Board Protocol provides a structured, validated approach to autonomous AI-driven development with phase-based execution, dependency management, and strict validation guardrails.

## Overview

This system implements the "Game Board Protocol" - a comprehensive framework for AI-assisted software development that includes:

- **Machine-readable specifications** with stable section IDs (UPS-*, PPS-*, DR-*)
- **Multi-layer validation** (schema validation + semantic guard rules)
- **Phase-based execution** with dependency resolution and parallel execution
- **Tool-agnostic adapters** for Aider, GitHub Codex CLI, and Claude Code
- **Patch-based isolation** with scope validation and rollback capability
- **Self-healing workflows** with programmatic acceptance tests

## Project Status

**Current Phase:** Bootstrap (Foundation)

This is the complete phase implementation plan for building the entire system across 19 phases in 7 milestones.

## Quick Start

### Prerequisites

- Python 3.8+
- Git
- PowerShell 7+ (for Windows) or Bash (for Unix-like systems)
- At least one AI CLI tool (Aider, Codex CLI, or Claude Code)

### Installation

1. **Clone or initialize the repository:**
   ```bash
   git init
   ```

2. **Run the bootstrap script:**
   ```powershell
   # PowerShell
   .\scripts\bootstrap.ps1
   
   # Or with dry-run to preview
   .\scripts\bootstrap.ps1 -DryRun
   ```
   
   This creates the required directory structure:
   - `.tasks/` - Task queue (queued, running, complete, failed)
   - `.ledger/` - Execution history and phase state
   - `.runs/` - Runtime logs (gitignored)
   - `config/` - Schema and validation rules
   - `specs/` - Machine-readable specifications
   - `src/` - Source code
   - `tests/` - Test suites

3. **Validate the setup:**
   ```bash
   python scripts/validate_phase_spec.py --all phase_specs/
   ```

4. **Review the master phase plan:**
   ```bash
   python scripts/validate_phase_spec.py --plan master_phase_plan.json
   ```

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Validation Gateway                       │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │   Schema     │→ │   Guard     │→ │   Dependency     │   │
│  │  Validator   │  │    Rules    │  │    Checker       │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Core                           │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │    State     │  │  Dependency │  │    Parallel      │   │
│  │   Machine    │  │  Resolver   │  │   Executor       │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Tool Adapters                             │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │    Aider     │  │   Codex     │  │     Claude       │   │
│  │   Adapter    │  │  Adapter    │  │    Adapter       │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Phase Execution Flow

1. **Validation** - Phase spec validated against schema and guard rules
2. **Queue** - Phase queued with dependencies checked
3. **Pre-flight** - Pre-flight checks executed (verify dependencies satisfied)
4. **Render** - Prompt rendered in WORKSTREAM_V1.1 format with context
5. **Execute** - Tool adapter invokes AI CLI with rendered prompt
6. **Test** - Acceptance tests executed to verify completion
7. **Complete** - Phase marked complete or failed based on test results

## Phase Plan

### Milestones

- **M0: Foundation** (PH-00) - Bootstrap project structure
- **M1: Machine-Readable Specs** (PH-1A through PH-1F) - Convert specs to structured format
- **M2: Validation System** (PH-2A through PH-2C) - Build validation pipeline
- **M3: Prompt & Orchestration** (PH-3A through PH-3C) - Build orchestrator core
- **M4: Patch & Task Management** (PH-4A through PH-4B) - Build patch manager and queue
- **M5: Tool Integration** (PH-5A through PH-5C) - Build tool adapters
- **M6: Validation & Production** (PH-6A through PH-6C) - Tests, CLI, documentation

**Total Effort:** ~150 hours sequential, ~105 hours with parallelism (30% reduction)

See `master_phase_plan.json` for complete phase details and dependency graph.

## Usage Examples

### Validate a Phase Spec

```bash
python scripts/validate_phase_spec.py phase_specs/phase_0_bootstrap.json
```

### Validate All Phase Specs

```bash
python scripts/validate_phase_spec.py --all phase_specs/
```

### Validate Master Plan

```bash
python scripts/validate_phase_spec.py --plan master_phase_plan.json
```

### Execute a Phase (after system is built)

```bash
cli/gameboard execute phase_specs/phase_1a_universal_spec.json
```

### Check Phase Status

```bash
cli/gameboard status PH-1A
```

### View Execution Plan

```bash
cli/gameboard plan master_phase_plan.json --check
```

## Directory Structure

```
.
├── phase_specs/          # Individual phase specification files (JSON)
├── master_phase_plan.json # Master plan with all phases and dependencies
├── scripts/              # Bootstrap and validation scripts
│   ├── bootstrap.ps1     # Initialize project structure
│   └── validate_phase_spec.py # Validate phase specs
├── .tasks/               # File-based task queue
│   ├── queued/
│   ├── running/
│   ├── complete/
│   └── failed/
├── .ledger/              # Execution history and state
├── config/               # Schema and validation rules
│   ├── schema.json
│   └── validation_rules.json
├── specs/                # Machine-readable specifications (built in M1)
├── src/                  # Source code (built across milestones)
├── tests/                # Test suites
├── cli/                  # CLI scripts (built in M6)
├── docs/                 # Documentation (built in M6)
└── README.md             # This file
```

## Key Concepts

### Phase Specification

Each phase has:
- **phase_id** - Unique identifier (e.g., PH-1A)
- **objective** - Clear statement of what the phase accomplishes
- **dependencies** - List of phases that must complete first
- **file_scope** - Files/directories the phase can modify
- **pre_flight_checks** - Validations before execution
- **acceptance_tests** - Programmatic tests that verify completion

### Parallel Execution Groups

Phases can execute in parallel when they have:
- No dependencies on each other
- Non-overlapping file scopes
- Same `parallel_group` identifier

Example: PH-1A, PH-1B, PH-1C (GROUP-1) convert three different specs in parallel.

### Validation Layers

1. **Schema Validation** - JSON schema compliance
2. **Guard Rules** - Business logic and anti-patterns (DR-DONT-* rules)
3. **Dependency Validation** - Ensures dependencies are satisfied

### Self-Referential Design

The system uses its own methodology to build itself:
- Each build phase is itself a valid phase spec
- Bootstrap follows the same structure as production phases
- The validation system validates its own components

## Success Criteria

The system is complete when:
- ✅ All 19 phases complete with passing acceptance tests
- ✅ Sample phase plan executes successfully
- ✅ Invalid phase specs rejected before execution (0% false positives)
- ✅ All three tool adapters functional
- ✅ Zero anti-pattern violations in final validation
- ✅ Documentation complete with working examples

## Documentation

- `docs/architecture.md` - Detailed system architecture (built in PH-6C)
- `docs/getting_started.md` - Installation and first steps (built in PH-6C)
- `docs/api_reference.md` - Module documentation (built in PH-6C)
- `docs/phase_specification_guide.md` - How to write phase specs (built in PH-6C)

## Contributing

This is a self-building system. Contributions should:
1. Follow the phase specification format
2. Pass all validation layers
3. Include acceptance tests
4. Stay within declared file scope

## License

[Specify your license here]

## References

- `UNIVERSAL PHASE SPECIFICATION.txt` - Core phase contract
- `PRO_Phase Specification mandatory structure.md` - Phase template
- `DEVELOPMENT RULES DO and DONT.md` - Development guidelines
- `AGENT_OPERATIONS_SPEC version1.0.0` - Technical implementation spec
