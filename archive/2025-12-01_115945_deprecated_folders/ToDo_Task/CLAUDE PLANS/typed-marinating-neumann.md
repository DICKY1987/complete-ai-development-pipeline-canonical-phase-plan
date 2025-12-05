---
doc_id: DOC-GUIDE-TYPED-MARINATING-NEUMANN-1567
---

# Plan: Update Codex Knowledge Files with Execution Patterns

## Executive Summary
Create CODEX.md knowledge file and update Codex Jinja2 template with execution patterns documentation. Claude and Copilot knowledge files are already complete.

## Current State Analysis

### Documentation Already Created (This Session)
1. **Core execution patterns documentation**:
   - `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md` (248 lines)
   - `docs/reference/ai-agents/README.md` (383 lines)
   - `docs/reference/ai-agents/QUICK_REFERENCE_CARD.md` (230 lines)
   - `AI_AGENT_INSTRUCTIONS_UPDATE_SUMMARY.md` (419 lines)
   - `PRMNT_DOCS_ANALYSIS.md` (338 lines)

2. **Existing tool knowledge files already updated**:
   - `.github/copilot-instructions.md` - **ALREADY has Section 0 with execution patterns**
   - `docs/reference/tools/CLAUDE.md` - **ALREADY has Section 0 with execution patterns**

### Codex Integration Point Found
- `aider/templates/prompts/workstream_v1.1_codex.txt.j2` - Jinja2 template for Codex workstream prompts
- This is a **template file** that gets populated with variables at runtime
- Has `[EXECUTION_HINTS]` section that could include pattern references

## Implementation Plan (User Confirmed)

### User Decisions
✅ **Scope**: Just update Codex (Claude and Copilot are complete)
✅ **Format**: Do both - create CODEX.md AND update the Jinja2 template
✅ **Detail Level**: Full Section 0 content (matching CLAUDE.md structure)

### Phase 1: Create docs/reference/tools/CODEX.md

Create new knowledge file with structure matching CLAUDE.md:

**Section 0: MANDATORY Execution Patterns First**
- Pattern-first workflow (ENFORCED)
- The Golden Rule
- Anti-patterns blocked (11 guards)
- Time savings metrics (3x-10x speedup, 255:1 ROI)
- Link to `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`

**Codex-Specific Guidance**:
- Integration with Aider workstream templates
- Template variable context awareness
- File scope constraints
- Validation and acceptance tests
- Git worktree coordination (if applicable)

### Phase 2: Update aider/templates/prompts/workstream_v1.1_codex.txt.j2

Enhance the Jinja2 template with execution patterns:

**Add new [EXECUTION_PATTERNS] section** (after [HEADER], before [OBJECTIVE]):
```jinja2
[EXECUTION_PATTERNS]
MANDATORY: Read docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md first

Pattern Check (30 sec):
  IF N ≥ 3 similar items → Use EXEC-001 to EXEC-006 pattern
  ELSE proceed with single implementation

Anti-Pattern Guards (ENABLED):
  ✅ No hallucination (verify exit codes, not "looks good")
  ✅ No planning loops (max 2 iterations, then execute)
  ✅ No incomplete code (no TODO/pass placeholders)
  ✅ Ground truth only (file.exists() = success)

The Golden Rule: Decide once → Apply N times → Trust ground truth → Move on

Time Savings: 3x-10x faster | 85h waste prevented | ROI: 255:1
Reference: docs/reference/ai-agents/QUICK_REFERENCE_CARD.md
```

**Update [EXECUTION_HINTS] section**:
Add pattern-awareness to existing hints:
- Check execution pattern applicability first (N ≥ 3?)
- Enable anti-pattern guards before starting
- Execute in batches when using patterns (6 files, 4 modules, 8 tests)
- Ground truth verification only (exit codes, file existence)
- [existing hints remain...]

### Phase 3: Validation & Cross-Reference Check
1. Verify CODEX.md references correct paths
2. Ensure template syntax is valid Jinja2
3. Check consistency with CLAUDE.md Section 0 structure
4. Verify all documentation paths exist and are correct

## Files to Create/Modify

### 1. CREATE: docs/reference/tools/CODEX.md
New file with full Section 0 structure matching CLAUDE.md format:
- Mandatory execution patterns section
- Pattern-first workflow
- Anti-pattern guards (all 11)
- Time savings metrics
- Codex-specific guidance for workstream integration

### 2. MODIFY: aider/templates/prompts/workstream_v1.1_codex.txt.j2
Add new [EXECUTION_PATTERNS] section after [HEADER]
Enhance [EXECUTION_HINTS] section with pattern awareness

## Success Criteria

✅ CODEX.md created and matches CLAUDE.md structure
✅ Jinja2 template updated with execution patterns section
✅ All file paths and cross-references validated
✅ Consistent with existing Claude/Copilot knowledge files
✅ Template remains valid Jinja2 syntax

## Critical Files to Reference During Implementation

- `docs/reference/tools/CLAUDE.md` - Template for CODEX.md structure
- `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md` - Core patterns to reference
- `docs/reference/ai-agents/QUICK_REFERENCE_CARD.md` - Quick reference content
- `aider/templates/prompts/workstream_v1.1_codex.txt.j2` - Template to enhance
