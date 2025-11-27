# Safe Merge Pattern Registry

## Pattern Family: SAFE_MERGE
**Version**: 1.0.0  
**Status**: Active  
**Owner**: richg

---

## Registered Patterns

### Phase 0: Reality Scan & Ground Truth

#### MERGE-001: Safe Merge Environment Scan
- **Status**: ✅ Active
- **Script**: `scripts/merge_env_scan.ps1`
- **Dependencies**: None
- **Output**: `env_scan.safe_merge.json`

#### MERGE-002: Sync Log Summary
- **Status**: ✅ Active
- **Script**: `scripts/sync_log_summary.py`
- **Dependencies**: None
- **Output**: `sync_log_summary.json`

#### MERGE-003: Nested Repo Detector
- **Status**: ✅ Active
- **Script**: `scripts/nested_repo_detector.py`
- **Dependencies**: None
- **Output**: `nested_repos_report.json`

### Phase 2: Multi-Clone / Multi-Tool Safe Sync

#### MERGE-006: Safe Pull and Push
- **Status**: ✅ Active
- **Script**: `scripts/safe_pull_and_push.ps1`
- **Dependencies**: None
- **Output**: `safe_push_events.jsonl`

### Phase 3: Timestamp & File-Class Heuristics

#### MERGE-008: Merge File Classifier
- **Status**: ✅ Active
- **Script**: `scripts/merge_file_classifier.py`
- **Dependencies**: None
- **Output**: `merge_file_classes.json`

---

## Integration with Existing Patterns

```yaml
pattern_relationships:
  EXEC-001:  # Batch File Operations
    used_by: [MERGE-005]
  
  EXEC-002:  # Conditional Workflow
    used_by: [MERGE-004]
  
  EXEC-004:  # Validation + Retry
    used_by: [MERGE-006, MERGE-007]
  
  EXEC-005:  # Parallel Execution
    used_by: [MERGE-008]
```

---

## Anti-Pattern Guards

```yaml
guards_active:
  - no_hallucination: Verify git operations with exit codes
  - no_planning_loops: Max 2 conflict resolution attempts
  - no_incomplete: No TODO/pass in generated code
  - no_silent_failures: Explicit error handling required
  - ground_truth: File exists = success
```

---

## Status Summary

| Pattern | Implementation | Tests | Docs | Status |
|---------|---------------|-------|------|--------|
| MERGE-001 | ✅ | 🔄 | ✅ | Active |
| MERGE-002 | ✅ | 🔄 | ✅ | Active |
| MERGE-003 | ✅ | 🔄 | ✅ | Active |
| MERGE-004 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-005 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-006 | ✅ | 🔄 | ✅ | Active |
| MERGE-007 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-008 | ✅ | 🔄 | ✅ | Active |
| MERGE-009 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-010 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-011 | 🔄 | 🔄 | ✅ | Planned |
| MERGE-012 | 🔄 | 🔄 | ✅ | Planned |

Legend: ✅ Complete | 🔄 In Progress | ❌ Blocked

---

**Last Updated**: 2025-11-27  
**Next Review**: 2025-12-04
