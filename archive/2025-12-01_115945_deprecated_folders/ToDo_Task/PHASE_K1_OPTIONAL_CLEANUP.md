---
doc_id: DOC-GUIDE-PHASE-K1-OPTIONAL-CLEANUP-1088
---

# Phase K-1 Optional Cleanup Tasks

**Created**: 2025-11-22  
**Priority**: Low (does not block Phase K-2)  
**Estimated Effort**: 2-4 hours  
**Status**: Not started

---

## Overview

Phase K-1 successfully created all core deliverables for documentation navigation and term mapping. However, during the automated analysis, two categories of issues were identified that could be addressed in a future cleanup session.

**Impact if left unaddressed**: Minimal - all core functionality works. AI agents can navigate documentation and find implementations. The cleanup improves polish and completeness but is not blocking.

---

## Issue 1: Broken Documentation Links (74 found)

### Description

The automated link validator in `scripts/generate_doc_index.py` detected **74 broken internal markdown links** across the documentation.

### Root Causes

Most broken links are from:
1. **Past refactors** - Files moved/renamed during Phase E refactor (2025-11)
2. **Deprecated paths** - References to old `src/pipeline/` structure
3. **Missing anchors** - Links to sections that were removed/renamed
4. **Case sensitivity** - Windows-insensitive paths that fail on Linux

### Examples

Common patterns found:
- `[old reference](../src/pipeline/db.md)` → Should be `[new reference](../core/state/db.py)`
- `[config](../config/tool_profiles.yaml#timeout)` → Anchor `#timeout` doesn't exist
- `[ADR](adr/adr-0003.md)` → File was renamed to `adr-0003-xyz.md`

### How to Fix

#### Option 1: Manual Review (Recommended)

```bash
# Run link validator to see full report
python scripts/generate_doc_index.py --fail-on-broken-links

# Review output for broken links
# Fix each link manually based on context
# Common fixes:
#   - Update paths to new locations
#   - Remove links to deleted files
#   - Fix anchor references
#   - Update case sensitivity
```

**Estimated time**: 2-3 hours (3-4 minutes per link)

#### Option 2: Automated Assistance

```python
# Create a script to suggest fixes based on file existence
python scripts/suggest_link_fixes.py  # (Not yet created)

# This could:
# - Find similar filenames for broken paths
# - Suggest alternative anchors
# - Flag links that should be removed
```

**Estimated time**: 1 hour to create script + 1 hour to review suggestions

### Priority Files

Focus cleanup on high-traffic documentation first:

**High Priority** (most referenced):
1. `docs/ARCHITECTURE.md` - Central architecture doc
2. `docs/DIRECTORY_GUIDE.md` - Navigation hub
3. `docs/README.md` files in subdirectories
4. `docs/QUICK_REFERENCE.md` files

**Medium Priority**:
5. Phase completion reports (`*_COMPLETE.md`)
6. Integration guides (`AIM_*.md`, `UET_*.md`)

**Low Priority**:
7. Planning documents (`docs/planning/`)
8. Archive documents (`docs/archive/`)

### Validation

After fixing:
```bash
# Run validator to confirm all links work
python scripts/generate_doc_index.py --fail-on-broken-links

# Should see: "All links valid!"
```

---

## Issue 2: Missing Term Auto-Locations (6 terms)

### Description

The automated implementation mapper couldn't find code locations for **6 specialized terms**:

1. **Spec Patcher** - Specification patching functionality
2. **URI Resolution** - Specification URI resolution
3. **Checkpoint** - State checkpointing
4. **AIM Bridge** - AIM integration bridge
5. **Profile Matching** - Tool profile selection
6. **Compensation Action** - SAGA compensation

### Root Causes

1. **Pattern mismatch** - Search patterns in `generate_implementation_map.py` don't match actual naming
2. **Not yet implemented** - Some features may be planned but not coded
3. **Different naming** - Code uses different terminology than documentation

### How to Fix

#### Option 1: Refine Search Patterns

Edit `scripts/generate_implementation_map.py` to add better patterns:

```python
# Current patterns (examples)
TERM_PATTERNS = {
    "Spec Patcher": ["patcher", "Patcher"],  # Too generic
    "AIM Bridge": ["aim/bridge", "AIMBridge"],  # Too specific
}

# Better patterns
TERM_PATTERNS = {
    "Spec Patcher": ["patch_spec", "SpecPatcher", "apply_patch", "spec.*patch"],
    "AIM Bridge": ["aim.*bridge", "bridge.*aim", "get_tool_info", "route_request"],
}
```

**Estimated time**: 30 minutes to refine patterns + 5 minutes to re-run

#### Option 2: Manual Investigation

For each missing term:
1. Search codebase manually: `grep -r "checkpoint" core/`
2. Identify actual implementation location
3. Either:
   - Add manual entry to `IMPLEMENTATION_LOCATIONS.md`
   - Or update patterns in `generate_implementation_map.py`

**Estimated time**: 10 minutes per term = 1 hour total

#### Option 3: Verify Implementation Status

Some terms may be **planned but not implemented**:

```bash
# Check if these features exist in code
grep -r "Compensation" core/
grep -r "checkpoint" core/state/

# If no results, mark as "Planned" in documentation
```

### Specific Term Investigations

#### 1. Spec Patcher
**Likely location**: `specifications/tools/patcher/`  
**Search**: `grep -r "patch" specifications/`  
**Pattern to add**: `"Spec Patcher": ["patch_spec", "apply_patch", "spec_patcher"]`

#### 2. URI Resolution
**Likely location**: `specifications/tools/resolver/`  
**Search**: `grep -r "resolve_uri\|parse_uri" specifications/`  
**Pattern to add**: `"URI Resolution": ["resolve_uri", "parse_uri", "uri.*resolv"]`

#### 3. Checkpoint
**Likely location**: `core/state/checkpoint.py`  
**Search**: `find . -name "*checkpoint*"`  
**Pattern to add**: `"Checkpoint": ["checkpoint", "save_state", "restore_state"]`

#### 4. AIM Bridge
**Likely location**: `aim/bridge.py`  
**Search**: `grep -r "class.*Bridge\|def.*bridge" aim/`  
**Pattern to add**: `"AIM Bridge": ["class Bridge", "get_tool_info", "aim.*integration"]`

#### 5. Profile Matching
**Likely location**: `core/engine/tools.py`  
**Search**: `grep -r "match.*profile\|select.*profile" core/`  
**Pattern to add**: `"Profile Matching": ["match_profile", "select.*profile", "choose_profile"]`

#### 6. Compensation Action
**Likely location**: `core/engine/saga.py` (if implemented)  
**Search**: `grep -r "compensat\|saga" core/`  
**Pattern to add**: `"Compensation Action": ["compensate", "compensation", "saga.*action"]`

### Validation

After refinement:
```bash
# Re-run implementation mapper
python scripts/generate_implementation_map.py

# Check for warnings
# Should see: "0 terms have no locations" or reduced count
```

---

## Recommended Cleanup Order

### Session 1: Quick Wins (1 hour)

1. **Refine term patterns** (30 min)
   - Update `TERM_PATTERNS` in `generate_implementation_map.py`
   - Re-run mapper and verify improvements
   
2. **Fix high-priority broken links** (30 min)
   - Focus on `ARCHITECTURE.md` and `DIRECTORY_GUIDE.md`
   - Fix 10-15 most critical links

### Session 2: Complete Cleanup (2-3 hours)

1. **Complete link fixing** (2 hours)
   - Run full link validator
   - Fix remaining 60-70 broken links
   - Test all fixes

2. **Verify term locations** (30 min)
   - Investigate remaining missing terms
   - Add manual entries if needed
   - Document any "Planned" features

3. **Final validation** (30 min)
   - Run all validators
   - Regenerate indices
   - Commit and push

---

## Scripts to Create (Optional)

### 1. suggest_link_fixes.py

```python
#!/usr/bin/env python3
"""
Suggest fixes for broken documentation links.

Analyzes broken links and suggests:
- Similar filenames (fuzzy matching)
- Alternative paths in new structure
- Links that should be removed
"""
```

**Value**: Reduces manual effort by 50%  
**Effort**: 1 hour to create

### 2. validate_term_patterns.py

```python
#!/usr/bin/env python3
"""
Validate term search patterns against codebase.

For each term:
- Tests pattern against actual code
- Reports matches and false positives
- Suggests pattern improvements
"""
```

**Value**: Ensures patterns are accurate  
**Effort**: 1 hour to create

---

## Files to Update

### After Link Cleanup

1. `docs/DOCUMENTATION_INDEX.md` - Re-generate to update link validation status
2. `docs/PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md` - Update validation checklist

### After Term Pattern Refinement

1. `scripts/generate_implementation_map.py` - Updated patterns
2. `docs/IMPLEMENTATION_LOCATIONS.md` - Re-generate with new findings
3. `docs/PHASE_K1_COMPLETE.md` - Update statistics

---

## Success Criteria

### Link Cleanup Complete When:
- [ ] `python scripts/generate_doc_index.py --fail-on-broken-links` returns 0 errors
- [ ] All high-priority docs have valid links
- [ ] Remaining broken links are documented as intentional (if any)

### Term Location Complete When:
- [ ] All 47 terms have at least one auto-detected location
- [ ] OR missing terms are documented as "Planned" in IMPLEMENTATION_LOCATIONS.md
- [ ] Pattern refinements reduce false positives

---

## Tracking

### Link Cleanup Progress

| Category | Total | Fixed | Remaining |
|----------|-------|-------|-----------|
| Architecture | ~10 | 0 | 10 |
| Implementation | ~15 | 0 | 15 |
| Configuration | ~8 | 0 | 8 |
| Integrations | ~12 | 0 | 12 |
| Development | ~10 | 0 | 10 |
| Reference | ~8 | 0 | 8 |
| Planning | ~6 | 0 | 6 |
| Migration | ~5 | 0 | 5 |
| **Total** | **74** | **0** | **74** |

### Term Location Progress

| Term | Status | Location Found | Notes |
|------|--------|----------------|-------|
| Spec Patcher | ❌ Not found | - | Check specifications/tools/patcher/ |
| URI Resolution | ❌ Not found | - | Check specifications/tools/resolver/ |
| Checkpoint | ❌ Not found | - | Check core/state/ |
| AIM Bridge | ❌ Not found | - | Check aim/bridge.py |
| Profile Matching | ❌ Not found | - | Check core/engine/tools.py |
| Compensation Action | ❌ Not found | - | May be planned, not implemented |

---

## When to Execute Cleanup

### Good Times:
- During a documentation-focused sprint
- Before a major release
- When onboarding new contributors (makes docs clearer)
- Low-priority downtime work

### Don't Block On:
- Phase K-2 implementation
- Any feature development
- CI/CD improvements

---

## Contact for Questions

- **Link Cleanup**: Review `scripts/generate_doc_index.py` source
- **Term Patterns**: Review `scripts/generate_implementation_map.py` source
- **Documentation Structure**: See `docs/DOCUMENTATION_INDEX.md`

---

## Appendix: Full Broken Link Report

To see the complete list of 74 broken links:

```bash
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
python scripts/generate_doc_index.py --fail-on-broken-links 2>&1 | grep "→"
```

This will output lines like:
```
- docs\ARCHITECTURE.md → ../src/pipeline/db.md
- docs\QUICK_START.md → tools/CLI_REFERENCE.md
```

---

**Last Updated**: 2025-11-22  
**Next Review**: Before Phase L or during low-priority work  
**Estimated Total Effort**: 2-4 hours  
**Priority**: Low - Nice to have, not blocking
