# Anti-Patterns Directory

**Purpose**: Forensic analysis of execution failures and anti-patterns to avoid.

---

## Contents

### 1. SPEED_PATTERNS_EXTRACTED.md
**Source**: PH-011 execution analysis  
**Key Learnings**:
- 80/20 ruthless prioritization (4+ hours saved)
- Ground truth verification (80 min saved)
- Batch similar operations (30 min saved)
- Decision elimination through templates

**Achievement**: 60% of value in 20% of time (95 min vs 6 hours)

---

### 2. UET_2025- ANTI-PATTERN FORENSICS.md
**Source**: Historical execution log analysis  
**Key Failures Documented**:
- **Hallucination of Success**: Claiming "complete" without test output
- **Planning Loop Trap**: 80k+ tokens planning, zero execution
- **Incomplete Implementation**: TODO/pass placeholders in production
- **Silent Failures**: Missing error handling

**Critical Insight**: These patterns burned 85+ hours across multiple sessions.

---

## How to Use This Directory

### When Planning New Work
1. Read **SPEED_PATTERNS_EXTRACTED.md** → Apply proven techniques
2. Read **UET_2025- ANTI-PATTERN FORENSICS.md** → Avoid documented failures

### When Reviewing AI Execution
Check for anti-patterns:
- ❌ "Looks complete" without test output
- ❌ Multiple planning iterations without atomic execution
- ❌ TODO/pass in submitted code
- ❌ Missing exit code verification

### ROI of This Directory
**Time saved by avoiding documented anti-patterns**: 85+ hours  
**Time to read both files**: 15 minutes  
**ROI**: 340:1

---

## Integration with Main Patterns

These anti-patterns informed the design of:
- **EXEC-009**: Meta-execution techniques (ground truth, no approval loops)
- **Execution guards** in main pattern library
- **Verification requirements** in all EXEC-001 through EXEC-008

**Relationship**: Anti-patterns are the "why" behind pattern design decisions.

---

## Contributing

When adding new anti-pattern analysis:
1. Include **evidence** (logs, timestamps, token counts)
2. Quantify **time wasted**
3. Propose **pattern guard** to prevent recurrence
4. Link to related **positive pattern** that solves it

**Template**: See existing files for structure.
