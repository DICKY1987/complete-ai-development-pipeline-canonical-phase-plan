# Phase 0 – Bootstrap & Initialization

**Purpose**: Detect repo, pick profile, validate baseline, generate project profile/router config.

## Phase Contents

Located in: `phase0_bootstrap/`

- `config/` - Configuration files and profiles
- `schema/` - 17 JSON validation schemas
- `README.md` - This file

## Current Components

### Configuration (`config/`)
- Profile configurations
- Tool profiles
- Quality gates (UTE_QUALITY_GATE.yaml)
- AI policies (UTE_ai_policies.yaml)

### Validation Schemas (`schema/`)
- 17 JSON schemas for data contracts
- Zero dependencies foundation layer

### Implementation (`core/bootstrap/`)
Located in cross-cutting `core/` directory:
- `orchestrator.py` - 4-step bootstrap orchestrator ✅
- `discovery.py` - ProjectScanner (repo detection) ✅
- `selector.py` - Profile selection (5 profiles) ✅
- `generator.py` - Artifact generation ✅
- `validator.py` - Baseline validation ✅

## Main Operations
- Detect repo + environment
- Pick correct project profile (patterns, tools, configs)
- Validate repo against schemas (IDs, patterns, layout)
- Generate `PROJECT_PROFILE.yaml` and `router_config.json`

## Test Coverage
8 passing tests in `tests/bootstrap/`

## Status
✅ Complete (100%)
