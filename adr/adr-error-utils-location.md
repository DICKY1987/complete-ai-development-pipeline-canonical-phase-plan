# ADR: Error Utilities Location

## Status
Accepted (2025-11-18)

## Context

During the section-aware repository refactor (WS-12), we must decide where to place shared utilities currently in `src/utils/`:

**Current state**:
- Location: `src/utils/`
- 6 modules: `types.py`, `time.py`, `hashing.py`, `jsonl_manager.py`, `env.py`, `__init__.py`
- 23+ import sites across codebase
- Primary consumers: 21 plugins, error engine, pipeline engine, plugin manager

**Analysis**:
- `types.py`: Error-specific types (PluginIssue, PluginResult, PipelineReport)
- `time.py`: Run ID generation for error pipeline
- `hashing.py`: File hashing for error pipeline cache
- `jsonl_manager.py`: JSONL logging for error pipeline
- `env.py`: Environment variable helpers (potentially reusable)

All utilities are currently used **exclusively by the error subsystem**.

## Decision

**Move utilities to `error/shared/utils/`** for true section isolation.

### Rationale:
1. **Single responsibility**: All current usage is error-pipeline specific
2. **Clear ownership**: Error section owns its utilities
3. **Encapsulation**: No cross-section dependencies currently exist
4. **Future flexibility**: If utilities become truly shared later, can extract to top-level `shared/utils/`

### Migration Strategy:
1. Create `error/shared/utils/` directory structure
2. Move files: `src/utils/*.py` → `error/shared/utils/*.py`
3. Create shim at `src/utils/` re-exporting from new location
4. Update imports in error subsystem (plugins, engines) to use `error.shared.utils`
5. Leave shim in place for backward compatibility during transition

## Consequences

### Positive:
- ✅ Clear section boundaries
- ✅ Error subsystem self-contained
- ✅ Easier to understand ownership
- ✅ Shim provides safe migration path

### Negative:
- ⚠️ 23+ import updates required
- ⚠️ Temporary indirection via shim

### Future considerations:
- If non-error code needs these utilities, extract to top-level `shared/utils/`
- Monitor for cross-section utility needs during future refactors

## Alternatives Considered

### Option A: Keep at top-level `shared/utils/`
- ❌ Implies broader reuse that doesn't exist
- ❌ Less clear ownership
- ❌ Violates section isolation principle

### Option B: Duplicate into each plugin
- ❌ Code duplication
- ❌ Maintenance burden
- ❌ Inconsistent types

## Implementation

See WS-12, WS-13, WS-14 workstreams.
