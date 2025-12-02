---
doc_id: DOC-PAT-README-963
---

# Auto-Approved Patterns

**Purpose**: Pattern specifications that have been automatically approved based on confidence thresholds.

**Status**: Active

---

## Contents

Auto-generated pattern specifications:

- `AUTO-20251127-001.yaml` through `AUTO-20251127-007.yaml`

---

## Auto-Approval Criteria

Patterns are auto-approved when:

1. **Confidence score** > 75%
2. **Similar patterns** detected (3+ occurrences)
3. **No validation errors**
4. **Passes schema validation**

---

## Usage

Auto-approved patterns can be:

1. **Used directly** - Already validated and ready
2. **Promoted** - Move to main `../` directory after review
3. **Modified** - Adjust as needed before promotion

---

## Related

- `../` - Main specs directory
- `../../automation/detectors/` - Pattern detection logic
- `../../registry/PATTERN_INDEX.yaml` - Pattern registry
