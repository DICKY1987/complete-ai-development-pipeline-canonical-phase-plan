---
doc_id: DOC-GUIDE-USER-PROCESS-ASSESSMENT-1195
---

# User Process Understanding Assessment

> **Purpose**: Assessment of user's understanding vs actual codebase capabilities  
> **Date**: 2025-11-22  
> **Status**: Analysis Complete

---

## Executive Summary

This document provides a detailed assessment of the user's understanding of the pipeline process compared to what the actual codebase delivers. The analysis identifies **key alignment areas** and **significant gaps** between expectations and implementation.

**Overall Assessment**: The user has a **partially accurate but simplified** understanding of the pipeline. Several critical components exist in different forms than described, and some expected features are not yet implemented.

---

## User's Understanding Summary

The user describes a two-path process:

### Path 1: New Project/Application
1. User creates PRD (Project Requirements Document)
2. PRD submitted to OpenSpec for formalization
3. Phase plan created via CLI tool (Claude/GitHub Copilot only)
4. Phase plan uploaded to "GetHub" project management
5. Files created from scratch using "GetHub Copilot for Claude code CIL"
6. Files sent through error pipeline
7. Errors fixed via auto-fix or CLI with patch files
8. Complete rewrites only if patches inefficient
9. Error escalation to more powerful applications
10. Files end in GitHub (committed) or quarantine folder

### Path 2: Existing Project/Module
- Same as Path 1 but for existing files
- Patch files created by Claude or GitHub Copilot
- Aider used for modifications (free, no usage constraints)
- Cost optimization through strategic tool selection

---

## Detailed Comparison: User Understanding vs Actual Codebase

### ✅ ALIGNED: Concepts That Match

#### 1. PRD Creation Process
**User's Understanding**: User creates PRD and submits to OpenSpec  
**Actual Implementation**: ✅ **MATCHES**
- `pm/commands/pm/prd-new.md` - PRD creation command exists
- PRDs stored in `.claude/prds/` directory
- Frontmatter-based metadata tracking
- Integration with project management workflow

**Evidence**:
```markdown
# From pm/commands/pm/prd-new.md
/pm:prd-new <feature_name>
# Creates: .claude/prds/$ARGUMENTS.md
```

#### 2. OpenSpec Integration
**User's Understanding**: Collaboration with OpenSpec to formalize documentation  
**Actual Implementation**: ✅ **MATCHES**
- `openspec/` directory contains specifications
- `specifications/` directory manages unified spec content
- OpenSpec bridge converts proposals to workstreams
- `/openspec:proposal` slash command available

**Evidence**:
```python
# From docs/Project_Management_docs/openspec_bridge.md
/openspec:proposal "Your feature description"
python scripts/spec_to_workstream.py --interactive
```

#### 3. Error Pipeline with Escalation
**User's Understanding**: Error detection with escalation to more powerful applications  
**Actual Implementation**: ✅ **STRONGLY MATCHES**
- `error/` directory implements sophisticated error pipeline
- 4-tier AI escalation: Mechanical → Aider → Codex → Claude → Quarantine
- State machine with 11 states (S_INIT → S_SUCCESS/S4_QUARANTINE)
- 21 validation plugins available

**Evidence**:
```
From error/README.md:
S0_MECHANICAL_AUTOFIX → S1_AIDER_FIX → S2_CODEX_FIX → S3_CLAUDE_FIX → S4_QUARANTINE
```

#### 4. Quarantine for Failed Files
**User's Understanding**: Files end in quarantine folder for user review  
**Actual Implementation**: ✅ **MATCHES**
- `S4_QUARANTINE` is a terminal state in error state machine
- Files that fail all escalation tiers go to quarantine
- Manual review required for quarantined files

#### 5. Auto-fix and Patch-based Modifications
**User's Understanding**: Auto-fix feature and patch files for modifications  
**Actual Implementation**: ✅ **MATCHES**
- Mechanical auto-fix plugins: `python_black_fix`, `python_isort_fix`, `js_prettier_fix`, `md_mdformat_fix`
- Patch-based approach through Aider adapter
- `engine/adapters/aider_adapter.py` for modifications

---

### ⚠️ PARTIALLY ALIGNED: Concepts with Differences

#### 6. Phase Plan Creation
**User's Understanding**: Phase plan created using CLI tool; only Claude or GitHub Copilot can generate  
**Actual Implementation**: ⚠️ **PARTIALLY DIFFERENT**

**What Actually Exists**:
- Workstream-based execution (not "phase plan" per se)
- Workstreams defined in JSON format in `workstreams/` directory
- `scripts/spec_to_workstream.py` converts OpenSpec to workstreams
- Phase plans exist as documentation in `meta/PHASE_DEV_DOCS/` but are development guides, not runtime artifacts

**Gap**: 
- No specific CLI tool that generates "phase plans" for upload to project management
- "Phase plans" in the repo are development documentation, not project execution plans
- Workstreams serve similar purpose but different format/approach

**Evidence**:
```json
// Workstream format (not phase plan):
{
  "id": "ws-001",
  "openspec_change": "OS-042",
  "tasks": [...],
  "files_scope": [...],
  "acceptance_tests": [...]
}
```

#### 7. GitHub/GetHub Project Management Upload
**User's Understanding**: Phase plan uploaded to "GetHub project management" for tracking  
**Actual Implementation**: ⚠️ **NOT CLEARLY IMPLEMENTED**

**What Actually Exists**:
- Project management tooling in `pm/` directory
- CCPM (Critical Chain Project Management) integration mentioned
- PRD and epic management commands
- **However**: No clear mechanism to "upload" workstreams/plans to GitHub Projects

**Gap**:
- No GitHub Projects API integration found
- No upload/sync mechanism visible
- PM tools appear to be local CLI commands, not GitHub integration
- User wrote "GetHub" (possibly meant "GitHub") - unclear if typo or different system

**Note**: The term "GetHub" appears to be a misspelling of "GitHub" throughout the user's description.

#### 8. File Creation Tools Restriction
**User's Understanding**: "Only GetHub Copilot for Claude code CIL can create new files"  
**Actual Implementation**: ⚠️ **SIGNIFICANTLY DIFFERENT**

**What Actually Exists**:
- Multiple adapters can create files:
  - `engine/adapters/aider_adapter.py` - Aider (can create files)
  - `engine/adapters/codex_adapter.py` - GitHub Copilot CLI
  - No "Claude code CIL" adapter found
- Aider explicitly supports file creation, not just modification
- No restriction preventing Aider from creating files

**Gap**:
- User believes only Copilot/Claude can create files - **NOT TRUE**
- Aider is fully capable of file creation
- "Claude code CIL" terminology not found in codebase (should be "Claude Code CLI" or similar)

**Evidence**:
```python
# From engine/adapters/aider_adapter.py
# Aider can create files with --yes flag and file specifications
```

#### 9. Cost Optimization Strategy
**User's Understanding**: Aider used for patches because it's "free and without usage constraints"; premium tools only for new files  
**Actual Implementation**: ⚠️ **PHILOSOPHY PARTIALLY SUPPORTED**

**What Actually Exists**:
- Multiple tool adapters with different capabilities
- Error pipeline does prioritize mechanical fixes (free) before AI escalation
- Strategic tool selection logic exists in error state machine

**Gap**:
- No explicit "cost optimization" configuration
- No hard rules about when to use which tool based on cost
- Escalation is based on **error severity and fix success**, not cost
- Aider isn't necessarily "free" (depends on AI model used: GPT-4, Claude, etc.)

---

### ❌ MISALIGNED: Significant Gaps

#### 10. Two Distinct Entry Points
**User's Understanding**: "Two entry points: new module/app vs existing module/app"  
**Actual Implementation**: ❌ **NOT EXPLICITLY SEPARATED**

**What Actually Exists**:
- Workstream execution is **unified** - no separate "new project" vs "existing project" entry points
- Same orchestrator handles both scenarios
- Differentiation happens in workstream JSON via `files_create` vs `files_scope` fields

**Gap**:
- No separate CLI commands for "new project" vs "existing project"
- User's mental model suggests two different workflows; actual implementation is one workflow with configuration

**Evidence**:
```json
// Same workstream format for both cases:
{
  "files_scope": ["existing/file.py"],      // Existing files
  "files_create": ["new/module/file.py"]    // New files
}
```

#### 11. Complete File Rewrite Decision Process
**User's Understanding**: "Complete file rewrite only if patch process becomes inefficient"  
**Actual Implementation**: ❌ **NO EXPLICIT LOGIC FOUND**

**What Exists**:
- Patch-based editing is default for Aider
- No automatic detection of "patch inefficiency"
- No automatic switch to "complete rewrite" mode
- Decision appears to be manual/implicit

**Gap**:
- No metrics or thresholds for patch vs rewrite
- No automatic escalation from patch to rewrite
- This decision logic is not implemented

#### 12. Files Committed to GitHub Automatically
**User's Understanding**: "File corrected and sent to GitHub, committed, and saved"  
**Actual Implementation**: ❌ **SEMI-AUTOMATIC**

**What Exists**:
- `engine/adapters/git_adapter.py` exists for git operations
- Error pipeline can fix files
- **However**: Automatic git commit/push not evident in error pipeline flow
- Git operations appear to be manual or separate from error pipeline

**Gap**:
- Error pipeline doesn't automatically commit fixed files
- Git integration exists but not as automatic success outcome
- User expects: Error fixed → Auto-commit → GitHub; Reality: Error fixed → Success state (commit separate)

#### 13. Handling Pipeline/Application Errors
**User's Understanding**: "Possibility that an error within the pipeline or with one of the applications occurs and file does not end up in GitHub or quarantine"  
**Actual Implementation**: ❌ **NOT EXPLICITLY HANDLED**

**What Exists**:
- Error state machine is comprehensive
- State transitions are well-defined
- Plugin execution has error handling

**Gap**:
- No explicit "pipeline failure" state beyond terminal states (SUCCESS/QUARANTINE)
- No clear documentation of what happens if the error pipeline itself fails
- No explicit recovery for infrastructure/tool failures
- User identifies a real concern that doesn't appear to have a documented solution

---

## Key Terminology Discrepancies

| User's Term | Actual Codebase Term | Notes |
|-------------|---------------------|-------|
| "GetHub" | GitHub | Likely typo; appears 4 times |
| "Phase Plan" | Workstream | Different structure and purpose |
| "CIL" / "code CIL" | CLI / Code CLI | Typo; should be "CLI" (Command Line Interface) |
| "GetHub Copilot for Claude code CIL" | GitHub Copilot CLI / Claude Code CLI | Confusing phrasing; two separate tools |
| "Air pipeline tool" | Aider | Likely autocorrect error for "Aider" |
| "Eight" (for patches) | Aider | Likely speech-to-text error |

---

## Missing or Unclear Components

### 1. GitHub Projects Integration
- **User Expects**: Upload phase plan to GitHub Projects for tracking
- **Reality**: No GitHub Projects API integration visible
- **Impact**: Manual project management required

### 2. Automatic Git Operations
- **User Expects**: Fixed files automatically committed to GitHub
- **Reality**: Git operations exist but not automatically triggered by error pipeline
- **Impact**: Manual git workflow required after fixes

### 3. New vs Existing Project Workflows
- **User Expects**: Two distinct entry points with different behaviors
- **Reality**: Single unified workstream workflow
- **Impact**: Mental model mismatch; actual system is more flexible

### 4. Phase Plan Generator CLI
- **User Expects**: CLI tool to generate phase plans compatible with GitHub Projects
- **Reality**: Spec-to-workstream converter exists but different format
- **Impact**: User may be looking for a feature that doesn't exist as described

### 5. Cost-Based Tool Selection
- **User Expects**: Explicit rules about when to use free vs paid tools
- **Reality**: Escalation based on error severity, not cost
- **Impact**: No cost optimization enforcement in code

---

## What Works Well (Matches User Understanding)

1. ✅ **PRD Creation**: Well-implemented with PM commands
2. ✅ **OpenSpec Integration**: Bridge exists and works as described
3. ✅ **Error Pipeline**: Sophisticated, matches escalation concept
4. ✅ **Quarantine System**: Terminal state for unfixable files
5. ✅ **Auto-fix Plugins**: Mechanical fixes before AI escalation
6. ✅ **Patch-Based Editing**: Aider adapter supports this
7. ✅ **Multiple AI Tiers**: Aider, Codex, Claude progression

---

## What Doesn't Match User Understanding

1. ❌ **Two Entry Points**: No separate new/existing workflows
2. ❌ **Phase Plan Upload**: No GitHub Projects integration
3. ❌ **File Creation Restrictions**: Aider CAN create files
4. ❌ **Auto-commit**: Error fixes don't auto-commit to GitHub
5. ❌ **Cost-Based Selection**: Escalation is error-driven, not cost-driven
6. ❌ **Rewrite Detection**: No automatic patch-to-rewrite escalation
7. ❌ **Pipeline Error Handling**: Infrastructure failures not explicitly handled
8. ❌ **Phase Plan Format**: Workstreams != Phase Plans

---

## Recommendations for Alignment

### For Documentation
1. **Clarify terminology**: "Workstreams" not "Phase Plans"
2. **Document actual workflow**: Show unified approach with file scope configuration
3. **Explain tool capabilities**: Aider can create files; no restrictions
4. **Git integration**: Document manual vs automatic commit steps
5. **Cost considerations**: Explain escalation is error-based, not cost-based

### For User Education
1. **Correct misconceptions**:
   - Aider is not restricted to patches only
   - No automatic GitHub Projects upload exists
   - Single workflow handles both new and existing projects
   
2. **Highlight actual capabilities**:
   - Error pipeline is more sophisticated than user realizes
   - 21 validation plugins available
   - State machine provides robust error handling
   
3. **Set realistic expectations**:
   - Git operations require manual steps or separate automation
   - Phase plan generation doesn't exist in described form
   - GitHub Projects integration is not implemented

### For Future Development
If user expectations should become reality:

1. **Implement GitHub Projects API integration**
   - Create workstream-to-project sync
   - Auto-create issues/tasks from workstreams
   
2. **Add auto-commit on success**
   - Extend error pipeline to commit fixed files
   - Add git operations to success state
   
3. **Create phase plan generator**
   - Convert workstreams to GitHub Projects format
   - Support upload/sync to GitHub
   
4. **Add cost-based tool selection**
   - Configuration for tool costs
   - Smart routing based on budget/limits
   
5. **Implement patch inefficiency detection**
   - Metrics for patch success/efficiency
   - Auto-escalate to rewrite when needed
   
6. **Add pipeline error recovery**
   - Handle infrastructure failures
   - Implement retry/recovery for tool failures

---

## Conclusion

The user has a **reasonable conceptual understanding** of the pipeline's purpose and flow, but several **critical implementation details differ** from their expectations:

### Strong Alignment (70%)
- Error pipeline with escalation ✅
- OpenSpec integration ✅
- PRD workflow ✅
- Quarantine system ✅
- Auto-fix capabilities ✅

### Weak Alignment (30%)
- GitHub Projects integration ❌
- Tool capability restrictions ❌
- Automatic git operations ❌
- Two separate entry points ❌
- Cost-based tool selection ❌

### User's Mental Model
The user envisions a **more automated, GitHub-centric workflow** with stricter tool boundaries than actually exists.

### Actual Implementation
The codebase provides a **flexible, workstream-based pipeline** with sophisticated error handling but requires more manual project management integration than user expects.

### Primary Gap
The biggest disconnect is **GitHub Projects integration** - the user believes phase plans are uploaded to GitHub Projects for tracking, but this feature doesn't exist. Project management appears to be local CLI-based, not GitHub-integrated.

---

## Action Items

### Immediate
1. ✅ **Document created**: This assessment
2. ⬜ Clarify terminology in main README
3. ⬜ Add "actual workflow" guide
4. ⬜ Document git integration steps

### Short-term
1. ⬜ Create user-facing workflow guide
2. ⬜ Add tool capability matrix
3. ⬜ Document manual vs automatic steps

### Long-term
1. ⬜ Consider GitHub Projects integration
2. ⬜ Evaluate auto-commit on success
3. ⬜ Implement cost-aware tool selection

---

**Assessment Date**: 2025-11-22  
**Reviewer**: AI Development Pipeline Analysis  
**Version**: 1.0
