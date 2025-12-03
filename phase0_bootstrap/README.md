# Phase 0 – Bootstrap & Initialization

**Purpose**: Detect repo, pick profile, validate baseline, generate project profile/router config.

## Current Components
- See `config/` for configuration files
- See `schema/` for validation schemas

## Main Operations
- Detect repo + environment
- Pick correct project profile (patterns, tools, configs)
- Validate repo against schemas (IDs, patterns, layout)
- Generate `PROJECT_PROFILE.yaml` and `router_config.json`

## Related Code
- `core/bootstrap/` (if exists)
- Configuration and schema validation logic
