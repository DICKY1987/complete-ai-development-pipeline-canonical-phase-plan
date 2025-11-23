# Patch 005: Development Guidelines Integration Analysis

**Patch ID**: 005-development-guidelines  
**Created**: 2025-11-23T11:23:15.523Z  
**Priority**: HIGH  
**Status**: Ready for Application

---

## Source Files Analyzed

1. **UET_DEVELOPMENT RULES DO and DONT.md** (274 lines)
   - Mandatory practices (8 rules)
   - Anti-patterns catalog (6 patterns)
   - Golden workflow
   - Success metrics

2. **AI_DEV_HYGIENE_GUIDELINES.md** (493 lines)
   - Core principles (3)
   - Directory organization rules
   - File naming standards
   - Context priority levels
   - Quarterly maintenance routine

3. **ANTI_PATTERNS.md** (782 lines)
   - 17 cataloged anti-patterns
   - Examples with BAD/GOOD code
   - Category-specific patterns
   - Historical incidents

4. **TESTING_STRATEGY.md** (447 lines)
   - Section-specific testing patterns
   - Mock & fixture library
   - Test data management
   - Coverage goals

---

## What This Patch Adds

### 1. Development Rules (`/meta/development_rules`)

**Mandatory Practices** (8 rules):
- **Ground Truth Over Vibes**: Verify with CLI, base decisions on observable outputs
- **Atomic Execution**: Small phases (1-3 modules), patch-style diffs
- **Mandatory Phase Structure**: Required fields for every phase
- **Self-Healing Execution**: Detect and fix environment issues autonomously
- **Worktree Isolation**: Every workstream in isolated git worktree
- **Operator Mindset**: Run commands, inspect outputs, proceed autonomously
- **Test-Driven Everything**: Tests required, only "all green" = success
- **Standard Architecture**: Required directories and files

**Golden Workflow**:
```
Pre-Flight Check → Execute Phase → Inspect Reality → 
Self-Heal if Needed → Re-Verify → Mark Complete
```

**Success Criteria**:
- All programmatic tests pass (observable output)
- All required files/dirs exist (CLI verified)
- Git status clean or matches expected
- Patches stored in ledger with metadata
- No files touched outside declared scope

---

### 2. Anti-Patterns Catalog (`/meta/anti_patterns`)

**Forbidden Patterns** (6 high-level):
1. **ANTI-001**: Hallucination of Success
2. **ANTI-002**: Planning Loop Trap
3. **ANTI-003**: Permission Bottlenecks
4. **ANTI-004**: Context Pollution
5. **ANTI-005**: Trusting Tools Without Verification
6. **ANTI-006**: Completing Without Acceptance

**Code Anti-Patterns** (9 technical):
- **AP-CS-01**: Direct file database access (High)
- **AP-CS-02**: Missing database migrations (Critical)
- **AP-CS-03**: Bypassing state machine transitions (Medium)
- **AP-EE-01**: Creating plugin without manifest.json (High)
- **AP-EE-02**: Non-incremental scanning (Medium)
- **AP-SC-01**: Hardcoded absolute paths (Critical)
- **AP-SC-03**: Printing sensitive information (High)
- **AP-TS-01**: Network calls in unit tests (High)
- **AP-TS-02**: Non-deterministic tests (Medium)

---

### 3. AI Development Hygiene (`/meta/ai_development_hygiene`)

**Core Principles**:
- Separation of Concerns: ACTIVE ≠ REFERENCE ≠ ARCHIVE
- Explicit Status Tagging: ACTIVE, REFERENCE, DRAFT, ARCHIVED, EXTERNAL
- Context Boundaries: AI tools see only relevant files

**Directory Rules**:
- Max depth: 4 layers
- Purpose-named directories: specs, docs, reference, _archive
- Isolate archives with `_` prefix
- Forbidden names: stuff, misc, temp, old_versions

**File Naming Convention**:
- Pattern: `[CATEGORY]_[SUBJECT]_[VERSION].[ext]`
- Categories: SPEC_, GUIDE_, REF_, IMPL_, ARCH_, SESSION_

**Required Frontmatter**:
```yaml
status: ACTIVE | REFERENCE | DRAFT | ARCHIVED | EXTERNAL
ai_context_priority: P0 | P1 | P2 | P3 | P4
last_reviewed: YYYY-MM-DD
superseded_by: [path] (if applicable)
source: INTERNAL | EXTERNAL:[Origin]
```

**Context Priority Levels**:
- **P0**: Active specs, contracts (always indexed, review monthly)
- **P1**: Production code (always indexed, review quarterly)
- **P2**: Current guides (index on request, review quarterly)
- **P3**: Reference material (explicit only, review annually)
- **P4**: Archive/legacy (never indexed, delete after 2 years)

**Golden Rules**:
1. Tag Everything
2. Isolate Archives
3. Name Clearly
4. 4 Layers Max
5. No Duplicates

---

### 4. Testing Strategy (`/meta/testing_strategy`)

**Section-Specific Patterns**:
- **Core State**: In-memory DB, test state transitions, verify migrations
- **Core Engine**: Mock tool adapters, test dependency resolution
- **Error Engine**: Use tmp_path, test real tool output, verify error location
- **Specifications**: Test URI parsing, spec resolution, cross-references

**Common Fixtures**:
- `in_memory_db`: Fast SQLite database for tests
- `sample_workstream`: Standard workstream for orchestration tests
- `mock_subprocess_run`: Avoid actual process execution
- `tmp_path`: Pytest fixture for temporary files

**Test Naming Convention**:
```python
test_<function>_<scenario>_<expected>

# Examples:
test_create_workstream_valid_input_success()
test_create_workstream_missing_id_raises_error()
test_transition_workstream_invalid_state_raises_error()
```

**Coverage Goals**:
- Core State: 90%
- Core Engine: 85%
- Error Engine: 80%
- Error Plugins: 70% per plugin
- Specifications Tools: 75%

---

### 5. Validation Gates (`/validation/`)

**Development Hygiene Checks**:
- File status tags present (95%+ target)
- Naming convention compliance
- No duplicate files
- No broken links
- Frontmatter presence

**Anti-Pattern Detection**:
- Direct DB access
- Missing migrations
- Hardcoded paths
- Network calls in tests
- Non-deterministic tests
- Missing plugin manifests
- State machine bypass

**Testing Compliance**:
- Tests required for new code
- Observable test output required
- In-memory DB for tests
- Mocked external calls
- Minimum coverage: 80-90% by section

---

### 6. New Workstreams in Phase 0

**WS-000-008: Development Hygiene Scripts** (2.0 hours)
- TSK-000-008-001: Create directory health check script
- TSK-000-008-002: Create duplicate file detector
- TSK-000-008-003: Create file validation script

**WS-000-009: Anti-Pattern Detection Integration** (1.5 hours)
- TSK-000-009-001: Create anti-pattern linting script
- TSK-000-009-002: Create anti-pattern detection tests

**Phase 0 Duration Updated**: 6.0h → 9.5h

---

## Impact Analysis

### Positive Impacts

1. **Codifies Best Practices**
   - All development rules now machine-readable
   - AI agents can validate compliance automatically
   - Clear success criteria for every phase

2. **Prevents Historical Mistakes**
   - 17 anti-patterns cataloged with fixes
   - Forbidden patterns explicitly listed
   - Historical incidents documented

3. **Improves AI Context Quality**
   - File priority system (P0-P4)
   - Archive isolation reduces confusion
   - Naming conventions make files discoverable

4. **Enables Automated Validation**
   - 3 new validation gate categories
   - Target metrics defined
   - Scripts to enforce hygiene

5. **Testing Standardization**
   - Section-specific patterns defined
   - Common fixtures documented
   - Coverage goals established

### Integration Points

**With Existing Patches**:
- **001-config-integration**: Extends ai_policies with anti-patterns
- **002-documentation-integration**: Complements AI tool configuration
- **003-uet-v2-specifications**: Adds validation for state machines
- **004-planning-reference**: Extends workstream prompt template

**With Quality Gates**:
- Adds 3 new gate categories
- Extends existing CI/CD enforcement
- Provides validation scripts

**With Phases**:
- Extends Phase 0 with 2 new workstreams
- Increases Phase 0 duration by 3.5 hours
- Provides foundation for all future phases

---

## Operations Summary

| Operation Type | Count | Paths |
|---------------|-------|-------|
| **add** | 20 | `/meta/development_rules`, `/meta/anti_patterns`, `/meta/ai_development_hygiene`, `/meta/testing_strategy`, `/validation/*`, `/phases/PH-000/workstreams/*` |
| **replace** | 1 | `/phases/PH-000/estimated_duration_hours` |
| **Total** | 21 | Across 5 top-level sections |

---

## Validation Checklist

Before applying this patch:

- [x] All source files exist and are complete
- [x] No ULID conflicts with existing patches
- [x] Patch operations are valid RFC 6902 format
- [x] File paths reference existing guideline documents
- [x] New workstreams have unique IDs
- [x] Phase 0 duration correctly updated
- [x] All anti-pattern codes are unique
- [x] Testing patterns reference real modules

After applying this patch:

- [ ] `UET_V2_MASTER_PLAN.json` contains `/meta/development_rules`
- [ ] Anti-pattern catalog accessible at `/meta/anti_patterns`
- [ ] AI hygiene guidelines at `/meta/ai_development_hygiene`
- [ ] Testing strategy at `/meta/testing_strategy`
- [ ] 3 new validation categories exist
- [ ] Phase 0 has 9 workstreams (was 7, +2)
- [ ] Phase 0 estimated duration is 9.5 hours

---

## Expected Outcomes

### Immediate
- **Development rules formalized**: 8 mandatory practices codified
- **Anti-patterns cataloged**: 15 patterns (6 behavioral + 9 technical)
- **Hygiene standards defined**: File naming, directory structure, priority levels
- **Testing patterns established**: 4 section-specific patterns with fixtures

### Near-term
- **Automated validation**: Scripts can check compliance
- **Reduced context pollution**: Priority system filters irrelevant files
- **Fewer test failures**: Standard patterns reduce flakiness
- **Self-documenting codebase**: Files declare status and purpose

### Long-term
- **AI agent quality improvement**: Clear rules reduce hallucinations
- **Faster onboarding**: New developers follow documented patterns
- **Maintainable tests**: Standard fixtures and naming
- **Quality metrics**: Trackable hygiene scores

---

## Relationship to Other Patches

```
001-config-integration
  ├── Provides: ai_policies, quality_gates
  └── Extended by: 005 (anti_patterns)

002-documentation-integration
  ├── Provides: AI tool configuration
  └── Complemented by: 005 (ai_development_hygiene)

003-uet-v2-specifications
  ├── Provides: State machines, component contracts
  └── Validated by: 005 (anti_patterns AP-CS-03)

004-planning-reference
  ├── Provides: Workstream templates, data flows
  └── Enhanced by: 005 (development_rules)

005-development-guidelines ← THIS PATCH
  ├── Extends: All previous patches
  └── Enables: Automated validation in future patches
```

---

## Recommendation

**Status**: ✅ **APPROVED FOR INTEGRATION**

This patch contains critical governance information that should be integrated into the master plan. It:

1. **Codifies tribal knowledge** from 4 comprehensive guideline documents
2. **Prevents regressions** by cataloging historical anti-patterns
3. **Enables automation** with machine-readable validation rules
4. **Improves AI assistance** through context priority system
5. **Standardizes testing** with section-specific patterns

**Priority**: HIGH (should be applied immediately after patches 001-004)

---

## Next Steps After Application

1. **Verify integration**:
   ```powershell
   python apply_patches.py
   # Check for /meta/development_rules in output
   ```

2. **Create hygiene scripts** (WS-000-008):
   - `scripts/directory_health_check.ps1`
   - `scripts/identify_duplicates.ps1`
   - `scripts/validate_new_file.ps1`

3. **Create anti-pattern detector** (WS-000-009):
   - `scripts/detect_anti_patterns.py`
   - `tests/scripts/test_anti_pattern_detection.py`

4. **Update AI tool instructions**:
   - Add development rules to `CLAUDE.md`
   - Add anti-patterns to `AGENTS.md`
   - Reference in `.github/copilot-instructions.md`

---

**Analysis Complete**  
**Patch Ready for Application** ✅
