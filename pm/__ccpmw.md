---
doc_id: DOC-PM-CCPMW-025
---

# CCPM + OpenSpec + Pipeline Unified Workflow

## Overview

This document describes the integrated workflow combining:
- **OpenSpec**: Spec-driven development (proposal → tasks → design)
- **CCPM**: Project management and agent coordination
- **Pipeline**: Automated validation and AI-assisted fixes

## Workflow Diagram

```
┌─────────────┐
│  OpenSpec   │  Create change with proposal.md + tasks.md
│   Change    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Generate   │  Parse change → create bundle YAML
│   Bundle    │  python -m src.pipeline.openspec_parser
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Create     │  Track work via GitHub issues
│  CCPM Epic  │  Use /pm commands for status
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Execute    │  Run error pipeline on file scopes
│  Pipeline   │  EDIT → STATIC → RUNTIME → VALIDATE
└──────┬──────┘
       │
       ├─ Success ─→ Archive change + Close epic
       │
       └─ Failure ─→ Quarantine + Create issue
```

## Step-by-Step Guide

### 1. Create OpenSpec Change

```bash
# Create change directory
mkdir -p openspec/changes/<change-id>
cd openspec/changes/<change-id>

# Create proposal
cat > proposal.md <<EOF
---
title: <Feature Title>
author: <Your Name>
date: $(date -I)
---

# Proposal

## Problem
Describe the problem this change solves.

## Solution
High-level solution approach.

## Requirements
- Requirement 1
- Requirement 2
EOF

# Create tasks
cat > tasks.md <<EOF
- [ ] Task 1: Edit file X
- [ ] Task 2: Add test Y
- [ ] Task 3: Update docs
EOF
```

### 2. Generate Pipeline Bundle

```bash
# Generate bundle from OpenSpec change
python -m src.pipeline.openspec_parser \
  --change-id <change-id> \
  --generate-bundle

# Verify bundle created
cat bundles/openspec-<change-id>.yaml
```

### 3. Create CCPM Epic (Optional)

```bash
# Create GitHub issue/epic for tracking
python -m src.pipeline.openspec_parser \
  --change-id <change-id> \
  --create-epic

# Alternative: Use CCPM commands
/pm:issue-start <issue-number>
```

### 4. Implement Changes

```bash
# Edit files as specified in tasks.md
# The pipeline will validate your changes
```

### 5. Run Pipeline Validation

```bash
# Option A: Via orchestrator (recommended)
python -m src.orchestrator.main bundles/openspec-<change-id>.yaml

# Option B: Direct error pipeline
python -m src.pipeline.error_pipeline_cli \
  --workstream ws-<change-id> \
  --files <file1> <file2> ...
```

### 6. Track Progress with CCPM

```bash
# Check current status
/pm:status

# Update issue status
/pm:issue-sync <issue-number>

# View next tasks
/pm:next

# Mark blocked
/pm:blocked "Reason for blockage"
```

### 7. Review Results

**On Success (S_SUCCESS state):**
```bash
# Archive the change
openspec archive <change-id>

# Close CCPM epic
/pm:epic-close <epic-id>
```

**On Failure (S4_QUARANTINE state):**
```bash
# GitHub issue automatically created
# Review error reports in .state/error_pipeline/

# Manual intervention required
# Fix issues and re-run pipeline
```

## Integration Points

### OpenSpec → Bundle Generator
**Tool:** `src/pipeline/openspec_parser.py`

**Function:** Converts OpenSpec changes into pipeline-compatible bundle YAML

**Usage:**
```bash
python -m src.pipeline.openspec_parser --change-id <id> --generate-bundle
```

**Output:** `bundles/openspec-<id>.yaml`

### OpenSpec → CCPM
**Tool:** `src/pipeline/openspec_parser.py`

**Function:** Creates GitHub issues/epics from OpenSpec changes

**Usage:**
```bash
python -m src.pipeline.openspec_parser --change-id <id> --create-epic
```

**Output:** GitHub issue with "openspec" and "epic" labels

### CCPM Agents in Pipeline

#### file-analyzer Agent
**When:** Before AI fix stages (S1/S2/S3)
**Purpose:** Summarize verbose error reports (80-90% reduction)
**Benefit:** Better context for AI agents

#### code-analyzer Agent
**When:** Pre-flight analysis, post-fix validation
**Purpose:** Detect bugs, trace logic, identify patterns
**Benefit:** Catch issues before they enter fix cycle

#### test-runner Agent
**When:** Recheck states (S0/S1/S2/S3_RECHECK)
**Purpose:** Execute tests via test-and-log.sh
**Benefit:** Multi-language test support with smart analysis

#### parallel-worker Agent
**When:** Multi-file workstreams
**Purpose:** Parallel plugin execution on independent files
**Benefit:** 3-5x speedup

### Pipeline → CCPM
**Integration:** Error reports linked to GitHub issues

**Automatic Actions:**
- S4_QUARANTINE → Create GitHub issue
- S_SUCCESS → Close associated epic/issue

## CCPM Commands Reference

### Status & Tracking
- `/pm:status` - Show current work status
- `/pm:next` - Show next task to work on
- `/pm:in-progress` - List in-progress items
- `/pm:blocked` - Mark/list blocked items

### Issue Management
- `/pm:issue-analyze <number>` - Analyze GitHub issue
- `/pm:issue-start <number>` - Start work on issue
- `/pm:issue-sync <number>` - Sync issue status
- `/pm:issue-close <number>` - Close completed issue

### Epic Management
- `/pm:epic-decompose <number>` - Break epic into issues
- `/pm:epic-start <epic-id>` - Begin epic work
- `/pm:epic-sync <epic-id>` - Sync epic progress
- `/pm:epic-merge <epic-id>` - Merge completed epic
- `/pm:epic-close <epic-id>` - Close epic

## Pipeline States & CCPM Integration

| State | Description | CCPM Action |
|-------|-------------|-------------|
| S_INIT | Initialize context | Log start time |
| S0_BASELINE_CHECK | Run all validators | - |
| S0_MECHANICAL_AUTOFIX | Apply autofixes | Log fix attempts |
| S0_MECHANICAL_RECHECK | Verify fixes | Run test-runner |
| S1_AIDER_FIX | AI fix (tier 1) | Use file-analyzer for context |
| S1_AIDER_RECHECK | Verify Aider fixes | Run test-runner + code-analyzer |
| S2_CODEX_FIX | AI fix (tier 2) | Use file-analyzer for context |
| S2_CODEX_RECHECK | Verify Codex fixes | Run test-runner + code-analyzer |
| S3_CLAUDE_FIX | AI fix (tier 3) | Use file-analyzer for context |
| S3_CLAUDE_RECHECK | Verify Claude fixes | Run test-runner + code-analyzer |
| S_SUCCESS | All validations passed | Close epic, archive change |
| S4_QUARANTINE | All fixes failed | Create GitHub issue |

## Example: End-to-End Workflow

### Scenario: Add Input Validation Feature

**1. Create OpenSpec Change**
```bash
mkdir -p openspec/changes/feature-input-validation

cat > openspec/changes/feature-input-validation/proposal.md <<'EOF'
---
title: Add Input Validation to User Registration
author: Dev Team
date: 2025-11-16
---

# Proposal

## Problem
User registration accepts invalid email formats and weak passwords.

## Solution
Add validation functions for email and password strength.

## Requirements
- Email must match RFC 5322 format
- Password must be 12+ chars with mixed case + numbers + symbols
- Return clear error messages
EOF

cat > openspec/changes/feature-input-validation/tasks.md <<'EOF'
- [ ] Create src/utils/validators.py
- [ ] Add validate_email() function
- [ ] Add validate_password() function
- [ ] Add tests/test_validators.py
- [ ] Verify all linters pass
- [ ] Verify type checking passes
EOF
```

**2. Generate Bundle & Create Epic**
```bash
python -m src.pipeline.openspec_parser \
  --change-id feature-input-validation \
  --generate-bundle \
  --create-epic

# Output: Created GitHub issue #42
```

**3. Implement Functions**
```python
# src/utils/validators.py
import re

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Valid email"
    return False, "Invalid email format"

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    if not (has_upper and has_lower and has_digit and has_symbol):
        return False, "Password must contain uppercase, lowercase, digits, and symbols"

    return True, "Valid password"
```

**4. Run Pipeline**
```bash
python -m src.pipeline.error_pipeline_cli \
  --workstream ws-feature-input-validation \
  --files src/utils/validators.py tests/test_validators.py

# Pipeline progresses:
# S_INIT → S0_BASELINE_CHECK → S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK → S_SUCCESS
```

**5. Track & Close**
```bash
# Update issue status
/pm:issue-sync 42

# Archive change
openspec archive feature-input-validation

# Close epic
/pm:epic-close 42
```

## Benefits

### Traceability
- Every change tracked from spec → implementation → validation
- GitHub issues link to OpenSpec changes
- Pipeline reports reference source requirements

### Context Preservation
- Proposals document the "why"
- Tasks track the "what"
- Pipeline validates the "how"

### Quality Assurance
- Automated validation at every stage
- Multi-tier AI-assisted fixes
- Comprehensive test execution

### Team Coordination
- Clear status visibility via CCPM commands
- Standardized workflow reduces confusion
- Easy onboarding for new team members

## Troubleshooting

### Issue: Bundle generation fails
**Solution:** Verify proposal.md and tasks.md exist and have valid frontmatter

### Issue: Pipeline stuck in recheck loop
**Solution:** Review error reports, may need manual intervention

### Issue: CCPM commands not found
**Solution:** Verify .claude/commands/pm/ directory exists and contains command files

### Issue: Agents not working
**Solution:** Check .claude/agents/ directory has all 4 agent files

## Further Reading

- [Error Pipeline Documentation](../src/pipeline/README.md)
- [Plugin Development Guide](../src/plugins/README.md)
- [CCPM Agent Coordination Rules](../.claude/rules/agent-coordination.md)
- [OpenSpec CLI Documentation](https://github.com/openspec/openspec)

---

**Last Updated:** 2025-11-16
**Maintained By:** Pipeline Team
