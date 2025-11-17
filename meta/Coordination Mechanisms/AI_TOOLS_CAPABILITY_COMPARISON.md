# AI Tools Capability Comparison

## Overview

This document compares the capabilities of different AI coding assistants for participating in the workstream coordination system.

## Compatibility Matrix

| Capability | Claude Code | Codex CLI | Aider | GitHub Copilot | Gemini 2.0 Flash | Gemini Chat |
|------------|-------------|-----------|-------|----------------|------------------|-------------|
| **Git Worktrees** | ✅ Full | ✅ Full | ✅ Full | ⚠️ IDE-dependent | ⚠️ Environment-dependent | ❌ No |
| **Git Branches** | ✅ Full | ✅ Full | ✅ Full | ⚠️ IDE-dependent | ⚠️ Environment-dependent | ❌ No |
| **Bash Scripts** | ✅ Full | ✅ Full | ✅ Full (via `/run`) | ⚠️ Limited | ✅ Full | ❌ No |
| **Read Coordination Files** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ⚠️ Via copy/paste |
| **Autonomous Commits** | ✅ Full | ✅ Full | ✅ Full (auto or manual) | ❌ No | ⚠️ Limited | ❌ No |
| **Multi-file Editing** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ⚠️ Via copy/paste |
| **Status Checking** | ✅ Full | ✅ Full | ✅ Full (via `/run`) | ⚠️ Manual | ⚠️ If execution enabled | ❌ No |
| **CLI Interface** | ✅ Native | ✅ Native | ✅ Native | ❌ IDE-based | ⚠️ API/web | ⚠️ Web only |

**Legend:**
- ✅ Full support - can use feature autonomously
- ⚠️ Partial/conditional - depends on configuration or requires workarounds
- ❌ Not supported - cannot use this feature

## Detailed Comparison

### 1. Claude Code (Anthropic)

**Coordination Compatibility:** ✅ **EXCELLENT**

**Strengths:**
- Full git workflow support
- Can execute bash scripts directly
- Reads and writes files autonomously
- Creates commits with custom messages
- Can check status of other AI's work

**Limitations:**
- None for this coordination system

**Best For:**
- Complex multi-file workstreams
- Tasks requiring investigation and exploration
- Dependency checking and status monitoring

**Instructions:** `README.md` (this document)

---

### 2. Codex CLI (OpenAI)

**Coordination Compatibility:** ✅ **EXCELLENT**

**Strengths:**
- CLI-native tool designed for git workflows
- Full worktree and branch management
- Executes coordination scripts
- Autonomous file operations

**Limitations:**
- None for this coordination system

**Best For:**
- Code generation tasks
- Schema and configuration file creation
- Structured implementation work

**Instructions:** `CODEX_COORDINATION_INSTRUCTIONS.md`

---

### 3. Aider (Open Source)

**Coordination Compatibility:** ✅ **EXCELLENT**

**Strengths:**
- Designed specifically for git workflows
- `/run` command for bash script execution
- Auto-commit or manual commit options
- Multi-file editing with context awareness
- Excellent for incremental development

**Limitations:**
- Requires exiting/restarting when changing directories
- Manual navigation between worktrees

**Best For:**
- Iterative development
- Refactoring tasks
- Test-driven development
- Tasks requiring conversation context

**Instructions:** `AIDER_COORDINATION_INSTRUCTIONS.md`

---

### 4. GitHub Copilot

**Coordination Compatibility:** ⚠️ **LIMITED**

**Strengths:**
- Excellent inline code suggestions
- Good for implementing well-defined functions
- IDE-integrated (VSCode, JetBrains, etc.)
- Fast autocomplete

**Limitations:**
- ❌ Cannot autonomously manage git worktrees
- ❌ Cannot execute coordination scripts independently
- ❌ Cannot commit autonomously
- ⚠️ Git operations depend on IDE extensions
- ⚠️ Requires human to handle git workflow

**Best For:**
- Code completion within files
- Function implementation
- Assisted development (not autonomous)

**Coordination Approach:**
- **Human-mediated workflow:**
  1. Human reads coordination instructions
  2. Human creates worktree and navigates to it
  3. Human opens files in IDE
  4. Copilot assists with code completion
  5. Human commits changes

**Not Recommended For:**
- Autonomous workstream execution
- Dependency checking
- Multi-file coordination

---

### 5. Gemini 2.0 Flash (Google - Code Execution Mode)

**Coordination Compatibility:** ⚠️ **CONDITIONAL**

**Strengths:**
- Can execute Python and bash commands
- Can read and write files
- Good reasoning capabilities
- Multimodal (can analyze diagrams, screenshots)

**Limitations:**
- ⚠️ Git access depends on execution environment
- ⚠️ May have sandboxed file system
- ⚠️ Worktree support depends on setup
- ⚠️ Not always persistent across sessions

**Best For (if environment supports git):**
- Analysis tasks
- Schema design
- Documentation generation
- Code review

**Coordination Approach:**
- **Test environment first:**
  ```bash
  # Check if git is available
  git --version

  # Check if worktrees work
  git worktree list
  ```
- If git works: Follow similar pattern to Claude Code/Codex
- If git limited: Use for non-git tasks (documentation, analysis)

---

### 6. Gemini Chat (Google - Web Interface)

**Coordination Compatibility:** ❌ **NOT COMPATIBLE**

**Strengths:**
- Good for planning and discussion
- Can generate code snippets
- Can review and analyze code

**Limitations:**
- ❌ Cannot execute commands
- ❌ Cannot access git
- ❌ Cannot read/write files directly
- ❌ Requires human to copy/paste everything

**Best For:**
- Planning discussions
- Code review (via copy/paste)
- Architecture discussions
- Generating implementation plans

**Coordination Approach:**
- **Human-mediated workflow:**
  1. Human asks Gemini to generate code
  2. Human copies code to files
  3. Human handles all git operations
  4. Gemini provides guidance only

**Not Recommended For:**
- Direct workstream execution

---

## Recommended Tool Assignment

### Tier 1: Fully Autonomous (✅ Can Execute Workstreams Independently)

```
Claude Code → Complex, exploratory, multi-dependency workstreams
Codex CLI   → Structured implementation, schema, config generation
Aider       → Iterative development, refactoring, TDD workflows
```

### Tier 2: Conditionally Autonomous (⚠️ May Work Depending on Setup)

```
Gemini 2.0 Flash → Test git access first, then assign accordingly
```

### Tier 3: Human-Assisted Only (❌ Cannot Work Autonomously)

```
GitHub Copilot → Use for in-IDE assistance during human-led work
Gemini Chat    → Use for planning and discussion only
```

## Workstream Suitability

| Workstream Type | Best Tools | Assisted Tools |
|-----------------|------------|----------------|
| **Schema/Config Creation** | Codex, Aider, Claude Code | Copilot (with human) |
| **Core Logic Implementation** | Claude Code, Aider, Codex | Copilot (with human) |
| **State Machine Design** | Claude Code, Aider | Codex, Gemini (planning) |
| **Documentation** | Aider, Codex, Claude Code | Gemini (generation), Copilot |
| **Test Writing** | Aider (TDD), Claude Code | Codex, Copilot |
| **Refactoring** | Aider, Claude Code | Copilot (with human) |
| **Integration** | Claude Code, Aider | - |
| **Dependency Analysis** | Claude Code | - |

## Coordination File Reference

| Tool | Instruction File |
|------|------------------|
| Claude Code | General coordination guide + this comparison |
| Codex CLI | `CODEX_COORDINATION_INSTRUCTIONS.md` |
| Aider | `AIDER_COORDINATION_INSTRUCTIONS.md` |
| GitHub Copilot | Use human-mediated workflow (see above) |
| Gemini 2.0 Flash | Test environment, then use Claude/Codex instructions |
| Gemini Chat | Planning only - not for execution |

## Multi-Tool Workflow Example

### Scenario: Implementing ws-ph02-db-core

**Step 1: Schema Design (Codex or Aider)**
```bash
# Codex or Aider creates schema.sql
git worktree add .worktrees/ws-ph02-schema -b workstream/ws-ph02-schema main
cd .worktrees/ws-ph02-schema
# ... implement schema ...
git commit -m "feat(ws-ph02-schema): implement schema"
```

**Step 2: Database Core Implementation (Claude Code or Aider)**
```bash
# Claude checks that schema is done
git branch -a | grep ws-ph02-schema  # ✅ exists

# Claude implements db.py
git worktree add .worktrees/ws-ph02-db-core -b workstream/ws-ph02-db-core main
cd .worktrees/ws-ph02-db-core
# ... implement db.py using schema from ws-ph02-schema branch ...
git commit -m "feat(ws-ph02-db-core): implement database core"
```

**Step 3: State Machine (Aider with TDD)**
```bash
# Aider checks dependencies
git branch -a | grep ws-ph02-db-core  # ✅ exists

# Aider uses TDD approach
aider --test-cmd="pytest tests/test_state_machine.py"
# ... iterative development with tests ...
/commit feat(ws-ph02-state-machine): implement state machine
```

**Step 4: Human Review with Copilot**
```bash
# Human opens VSCode
# Copilot assists with:
# - Adding edge case handling
# - Improving error messages
# - Adding docstrings
```

## Status Checking Across Tools

### All Autonomous Tools Can Run:
```bash
# See what's done
git branch -a | grep "workstream/"

# Check detailed status
bash scripts/check_workstream_status.sh

# Verify specific implementation
git show workstream/ws-ph02-schema:schema/schema.sql
```

### Human-Assisted Tools (Copilot, Gemini Chat):
- Human runs status checks manually
- Human reports status to AI for planning
- AI guides human on what to check

## Summary

✅ **Fully Compatible:** Claude Code, Codex CLI, Aider
⚠️ **Conditionally Compatible:** Gemini 2.0 Flash (test first)
❌ **Not Compatible:** GitHub Copilot, Gemini Chat (human-mediated only)

**Best Practice:**
- Use autonomous tools (Claude, Codex, Aider) for workstream execution
- Use assisted tools (Copilot, Gemini) for code completion and planning
- All tools use git as single source of truth
- No conflicts because each uses separate worktrees/branches

🚀 **Ready for multi-tool parallel development!**
