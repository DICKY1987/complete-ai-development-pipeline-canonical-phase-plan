---
doc_id: DOC-GUIDE-TASKS-086
---

# Phase D Tasks - Adapters (Patch-First)

## Feature Flags

- [ ] Add `patch_mode` to `PROJECT_PROFILE.yaml`
- [ ] Implement dual-mode detection
- [ ] Document in `docs/FEATURE_FLAGS.md`

## Base Adapter

- [ ] Modify `core/engine/adapters/base.py`
- [ ] Add `patch_mode` parameter
- [ ] Add task mode support
- [ ] Add `_extract_patch()` helper

## Aider Adapter

- [ ] Modify `core/engine/adapters/aider_adapter.py`
- [ ] Add `--no-auto-commits --output-diff`
- [ ] Implement patch extraction
- [ ] Test dual-mode

## Codex Adapter

- [ ] Modify `core/engine/adapters/codex_adapter.py`
- [ ] Implement patch extraction
- [ ] Test dual-mode

## Claude Adapter

- [ ] Modify `core/engine/adapters/claude_adapter.py`
- [ ] Implement patch extraction
- [ ] Test dual-mode

## Migration Testing

- [ ] Create `tests/migration/` directory
- [ ] Test 20+ workstreams in legacy mode
- [ ] Test 20+ workstreams in patch mode
- [ ] Validate identical outcomes
- [ ] Create migration checklist

## Orchestrator Integration

- [ ] Modify `core/engine/orchestrator.py`
- [ ] Integrate patch capture
- [ ] Add validation before STATIC
- [ ] Store patch metadata
- [ ] Add quarantine on failure
