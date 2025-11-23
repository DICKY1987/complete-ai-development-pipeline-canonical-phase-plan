# Phase D: Adapters - Patch-First Refactoring

**Change ID**: uet-001-phase-d-adapters  
**Parent**: uet-001-complete-implementation  
**Depends On**: uet-001-phase-b-patch-system  
**Type**: BREAKING CHANGE  
**Priority**: HIGH  
**Estimated Duration**: 3-4 weeks  
**Effort**: 42 hours

---

## Problem Statement

**CRITICAL**: This is a **BREAKING CHANGE** to all adapters. Current adapters directly edit files - this prevents:

- Full audit trails (no patch artifacts)
- Validation before application
- Easy rollback
- Multi-tool compatibility

**Risk Level**: HIGH - Requires dual-mode support to prevent breaking existing workstreams.

---

## Requirements

**Dual-Mode Support**:
- MUST implement `patch_mode: true/false` feature flag
- MUST maintain backward compatibility for 3 months
- SHALL NOT break existing workstreams

**Patch-First Mode**:
- SHALL output unified diffs (not direct edits)
- SHALL support task modes: prompt, patch_review, patch_apply_validate
- SHALL create PatchArtifact for all changes
- SHALL validate patches before application

---

## Implementation Strategy

### Feature Flag Infrastructure

```yaml
# PROJECT_PROFILE.yaml
execution:
  patch_mode: false  # Default: legacy mode
  adapters:
    aider:
      patch_mode: true  # Opt-in per adapter
```

### Adapter Refactoring

**Before (Direct Edit)**:
```python
def execute(self, task):
    subprocess.run(['aider', '--yes', '--auto-commits'])
```

**After (Patch-First)**:
```python
def execute(self, task):
    if self.config.get('patch_mode', False):
        result = subprocess.run(['aider', '--no-auto-commits', '--output-diff'])
        patch = self._extract_patch(result.stdout)
        return {'patch': patch}
    else:
        # Legacy mode
        subprocess.run(['aider', '--yes', '--auto-commits'])
```

---

## Success Criteria

- ✅ All adapters support dual-mode
- ✅ 20+ workstreams tested in migration suite
- ✅ No regressions in legacy mode
- ✅ Patch mode creates valid artifacts

---

## Dependencies

**Requires**: Phase B (patch system)  
**Blocks**: Phase E (resilience needs adapters)

---

## Files Modified

- `core/engine/adapters/base.py`
- `core/engine/adapters/aider_adapter.py`
- `core/engine/adapters/codex_adapter.py`
- `core/engine/adapters/claude_adapter.py`
- `core/engine/orchestrator.py`

## Files Created

- `docs/FEATURE_FLAGS.md`
- `docs/PATCH_FIRST_MIGRATION.md`
- `tests/migration/` (full test suite)
