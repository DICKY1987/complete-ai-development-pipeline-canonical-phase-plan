# Phase 4 – Tool Routing & Adapter Selection

**Purpose**: Match tasks to tool profiles and select adapters (Aider/Codex/Custom).

## Current Components
- See `tools/` for tool implementations
- See `aider/` for Aider adapter
- See `aim/` for AIM environment manager
- See `config/tool_profiles.json`

## Main Operations
- Match tasks by language, task type, environment
- Select best tool adapter with fallbacks
- Validate adapter configuration (commands, paths, env, timeouts)
- Manage multi-instance pools for Aider/Codex

## Related Code
- `core/engine/tools.py`
- Adapter implementations
- ToolProcessPool + ClusterManager
