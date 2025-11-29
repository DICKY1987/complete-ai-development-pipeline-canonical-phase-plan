---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-AGENT_QUICK_REFERENCE-110
---

# Agent Quick Reference Guide

> **Purpose**: Fast decision guide for which agent to use for your task  
> **Last Updated**: 2025-11-23  
> **Related**: [AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)

---

## "Which Agent Should I Use?"

### Decision Tree

```
┌─────────────────────────────────────┐
│   What are you trying to do?        │
└────────────┬────────────────────────┘
             │
             ├──> 📝 Small code edit or completion (1 function)
             │    ➜ Use: GitHub Copilot
             │    📍 When: In your IDE, typing code
             │
             ├──> 🔧 Well-scoped feature (2-5 files)
             │    ➜ Use: Claude Code
             │    📍 When: You have clear task spec with FILES_SCOPE
             │
             ├──> 🎯 Complete workstream execution
             │    ➜ Use: Codex CLI
             │    📍 When: You have workstream JSON ready
             │
             ├──> 🧪 Validate code quality
             │    ➜ Use: Error Engine
             │    📍 When: Before commit or in CI
             │
             ├──> 🚀 Orchestrate multiple tools
             │    ➜ Use: Job Engine
             │    📍 When: You need tool coordination
             │
             └──> 🤖 Automate repetitive task
                  ➜ Use: Automation Scripts (40+ available)
                  📍 When: Task fits existing script
```

---

## Quick Reference Table

| Task Type | Agent to Use | Command / How to Use | Time to Result |
|-----------|--------------|---------------------|----------------|
| **Code Completion** | GitHub Copilot | (Automatic in IDE) | Instant |
| **Small Bug Fix** | Copilot → Manual | Edit in IDE | < 5 min |
| **Write Unit Test** | Copilot | Type test stub, let it complete | < 10 min |
| **Add Feature (1-5 files)** | Claude Code | Create task spec + delegate | 30-60 min |
| **Run Workstream** | Codex CLI | `python scripts/run_workstream.py --ws-id <id>` | Varies |
| **Check Code Quality** | Error Engine | `python scripts/run_error_engine.py <files>` | 2-5 min |
| **Validate Workstream** | Validation Script | `python scripts/validate_workstreams.py` | 1-2 min |
| **Generate Spec Index** | Generation Script | `python scripts/generate_spec_index.py` | 1-2 min |
| **Migrate Imports** | Migration Script | `python scripts/migrate_imports.py` | 5-10 min |
| **Run Job** | Job Engine | `python -m engine.orchestrator run-job --job-file <file>` | Varies |

---

## Common Scenarios

### Scenario 1: "I need to add a simple function"

**Best approach:**
1. Use **GitHub Copilot** in your IDE
2. Write function signature
3. Let Copilot suggest implementation
4. Review and adjust

**Time**: 5 minutes

---

### Scenario 2: "I need to implement a feature across 3 files with tests"

**Best approach:**
1. Create task specification:
   ```yaml
   Phase: PH-XXX
   Workstream: WS-XXX
   Description: "Clear feature description"
   FILES_SCOPE:
     - "file1.py"
     - "file2.py"
     - "tests/test_file1.py"
   Constraints: ["Specific constraints"]
   Acceptance Criteria: ["Tests pass", "Feature works"]
   ```
2. Delegate to **Claude Code**
3. Review patches
4. Run validation

**Time**: 30-60 minutes

---

### Scenario 3: "I need to check my code before committing"

**Best approach:**
1. Run **Error Engine**:
   ```bash
   python scripts/run_error_engine.py $(git diff --name-only)
   ```
2. Fix any issues reported
3. Commit

**Time**: 2-5 minutes

---

### Scenario 4: "I need to update deprecated import paths"

**Best approach:**
1. Run **Migration Script**:
   ```bash
   python scripts/migrate_imports.py --auto-fix
   ```
2. Review changes
3. Run tests
4. Commit

**Time**: 5-10 minutes

---

### Scenario 5: "I need to create a new workstream"

**Current approach (manual):**
1. Copy example workstream JSON
2. Edit all fields manually
3. Validate with `python scripts/validate_workstreams.py`

**Time**: 20-30 minutes

**Future (with Workstream Generator Agent - RECOMMENDED TO BUILD):**
1. Run generator:
   ```bash
   python scripts/agents/workstream_generator.py \
     --description "Your feature" \
     --files "file1.py,file2.py"
   ```
2. Review and adjust if needed
3. Save

**Time**: 5 minutes (75% time saved)

---

### Scenario 6: "I need to add tests for new code"

**Current approach (manual):**
1. Create test file
2. Write test boilerplate
3. Write test cases
4. Run and debug

**Time**: 30-45 minutes

**Future (with Test Generator Agent - RECOMMENDED TO BUILD):**
1. Run generator:
   ```bash
   python scripts/agents/test_generator.py \
     --module core/engine/executor.py
   ```
2. Fill in assertion logic
3. Run and debug

**Time**: 10-15 minutes (67% time saved)

---

## Agent Capabilities Matrix

| Capability | Copilot | Claude Code | Codex CLI | Error Engine | Job Engine | Scripts |
|------------|---------|-------------|-----------|--------------|------------|---------|
| Code Completion | ✅✅✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Small Edits | ✅✅✅ | ✅✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-file Changes | ❌ | ✅✅✅ | ✅✅ | ❌ | ❌ | ❌ |
| Task Coordination | ❌ | ✅ | ✅✅✅ | ❌ | ✅✅✅ | ✅ |
| Code Validation | ❌ | ✅ | ✅ | ✅✅✅ | ❌ | ✅✅ |
| Auto-fix Issues | ❌ | ✅ | ✅ | ✅✅ | ❌ | ✅ |
| Test Generation | ✅✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Documentation | ✅ | ✅✅ | ✅ | ❌ | ❌ | ✅✅ |
| Orchestration | ❌ | ❌ | ✅✅✅ | ❌ | ✅✅✅ | ✅ |

**Legend**: ✅✅✅ Excellent | ✅✅ Good | ✅ Fair | ❌ Not supported

---

## When NOT to Use Agents

### Don't use agents for:

1. **Architectural decisions**
   - Use: Human judgment, team discussion
   - Why: Requires business context and long-term vision

2. **Security-sensitive changes**
   - Use: Manual review + security expert review
   - Why: High risk of vulnerabilities

3. **Database migrations**
   - Use: Manual implementation with review
   - Why: Data loss risk, requires careful planning

4. **Breaking changes to public APIs**
   - Use: Manual planning with deprecation strategy
   - Why: Affects downstream consumers

5. **Complex multi-phase refactors**
   - Use: Human-led incremental approach
   - Why: Requires strategic planning and coordination

---

## Tips for Success

### 1. Match Task Size to Agent

- **Tiny (1 function)**: Copilot
- **Small (1-5 files)**: Claude Code
- **Medium (workstream)**: Codex CLI + Claude Code
- **Large (multi-workstream)**: Human coordination + agents

### 2. Always Validate

After any agent work:
```bash
# Run tests
pytest -q

# Check code quality
python scripts/run_error_engine.py <files>

# Validate structure
python scripts/validate_workstreams.py
```

### 3. Use the Right Level of Automation

```
Manual ←─────────────────────────────→ Fully Automated
  │                    │                       │
  │                    │                       │
Architecture      Feature Impl         Code Quality
Decisions          (Claude Code)      (Error Engine)
```

### 4. Combine Agents Effectively

**Example workflow:**
1. Human defines architecture
2. **Claude Code** implements features
3. **Copilot** helps with test completion
4. **Error Engine** validates quality
5. **Scripts** regenerate indices
6. Human reviews and merges

---

## Emergency: "Something Went Wrong"

### Agent produced bad code

1. **Stop**: Don't commit
2. **Review**: Check the changes manually
3. **Revert**: Use `git checkout <file>` if needed
4. **Adjust**: Refine task specification
5. **Retry**: With clearer instructions

### CI failing after agent changes

1. **Check errors**: Review CI output
2. **Run locally**: `pytest -q` and validation scripts
3. **Fix issues**: Either manually or with agent
4. **Verify**: Run full test suite before pushing

### Agent seems confused

1. **Simplify**: Break task into smaller pieces
2. **Clarify**: Provide more specific constraints
3. **Examples**: Show example input/output
4. **Manual**: Consider doing it manually if too complex

---

## Quick Start Checklist

- [ ] Read [AGENTS.md](../AGENTS.md) for conventions
- [ ] Configure Copilot in your IDE
- [ ] Bookmark [CLAUDE.md](../CLAUDE.md) for task specs
- [ ] Try running `python scripts/validate_workstreams.py`
- [ ] Test Error Engine: `python scripts/run_error_engine.py <file>`
- [ ] Review automation scripts in `scripts/`
- [ ] Read full analysis: [AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)

---

## Resources

### Documentation
- [Full Agent Analysis](AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)
- [AGENTS.md](../AGENTS.md) - Repository guidelines
- [CLAUDE.md](../CLAUDE.md) - Claude Code instructions
- [.github/copilot-instructions.md](../.github/copilot-instructions.md)

### Scripts Directory
- [scripts/README.md](../scripts/README.md) - All automation scripts
- [scripts/validate_workstreams.py](../scripts/validate_workstreams.py)
- [scripts/run_error_engine.py](../scripts/run_error_engine.py)

### Quality Gates
- [QUALITY_GATE.yaml](../QUALITY_GATE.yaml) - Validation commands
- [ai_policies.yaml](../ai_policies.yaml) - AI tool policies

---

**Last Updated**: 2025-11-23  
**Questions?** Open an issue or ask in team chat  
**Feedback?** Update this document with your learnings
