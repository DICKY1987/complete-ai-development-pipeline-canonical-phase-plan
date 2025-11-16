# CCPM Setup and Usage Instructions for AI Assistants

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initialization](#initialization)
- [Understanding CCPM Architecture](#understanding-ccpm-architecture)
- [Workflow Guide](#workflow-guide)
- [Command Reference](#command-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Claude Code Project Management (CCPM)** is a spec-driven development system that enables:
- **Context preservation** across sessions using structured documentation
- **Parallel execution** with multiple AI agents working simultaneously
- **Full traceability** from PRD → Epic → Task → Issue → Code
- **GitHub integration** for team collaboration and progress tracking

### Core Principle: No Vibe Coding
Every line of code must trace back to a specification. Follow the 5-phase discipline:
1. **Brainstorm** - Think deeply about requirements
2. **Document** - Write comprehensive specs
3. **Plan** - Make explicit technical decisions
4. **Execute** - Build exactly what was specified
5. **Track** - Maintain transparent progress

---

## Prerequisites

Before starting, verify:

### 1. Git Repository
```bash
# Check if current directory is a git repository
git status

# If not initialized, create one:
git init
```

### 2. GitHub CLI (gh)
```bash
# Check if gh is installed
gh --version

# If not installed, install it:
# Windows (PowerShell):
winget install --id GitHub.cli

# macOS:
brew install gh

# Linux:
# See: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
```

### 3. GitHub Authentication
```bash
# Authenticate with GitHub
gh auth login

# Verify authentication
gh auth status
```

---

## Installation

### Step 1: Navigate to Project Directory
```bash
cd /path/to/your/project
```

### Step 2: Choose Installation Method

#### Method A: Direct Clone (Recommended)
```bash
# Clone CCPM repository to a temporary location
git clone https://github.com/automazeio/ccpm.git ccpm-temp

# Copy the .claude directory to your project
cp -r ccpm-temp/ccpm .claude

# Remove temporary clone
rm -rf ccpm-temp
```

#### Method B: Install Script (Unix/Linux/macOS)
```bash
curl -sSL https://automaze.io/ccpm/install | bash
# OR
wget -qO- https://automaze.io/ccpm/install | bash
```

#### Method C: Install Script (Windows PowerShell)
```powershell
iwr -useb https://automaze.io/ccpm/install | iex
```

**Note:** If you already have a `.claude` directory, manually merge the contents rather than overwriting.

### Step 3: Verify Installation
```bash
# Check that .claude directory exists
ls -la .claude

# Should see these directories:
# - agents/
# - commands/
# - context/
# - epics/
# - prds/
# - rules/
# - scripts/
```

---

## Initialization

### Step 1: Run Initialization Script

#### Using Slash Command (if available)
```bash
/pm:init
```

#### Manual Execution
```bash
# Unix/Linux/macOS
bash .claude/scripts/pm/init.sh

# Windows (Git Bash)
bash .claude/scripts/pm/init.sh
```

### Step 2: Verify Initialization

The init script should:
- ✅ Verify GitHub CLI is installed
- ✅ Verify GitHub authentication
- ✅ Install gh-sub-issue extension
- ✅ Create required directories
- ✅ Create initial CLAUDE.md file
- ✅ Update .gitignore

### Step 3: Configure Git Remote (if needed)
```bash
# Check current remotes
git remote -v

# Add remote if not configured
git remote add origin https://github.com/username/repo.git
```

### Step 4: Create Initial Context

#### Using Slash Command
```bash
/context:create
```

#### What This Does
Creates comprehensive context files in `.claude/context/`:
- `progress.md` - Current project status
- `project-structure.md` - Directory organization
- `tech-context.md` - Dependencies and technologies
- `system-patterns.md` - Architectural patterns
- `product-context.md` - Product requirements
- `project-brief.md` - Project scope and goals
- `project-overview.md` - Features and capabilities
- `project-vision.md` - Long-term vision
- `project-style-guide.md` - Coding standards

### Step 5: Update .gitignore

Ensure `.gitignore` includes:
```
.claude/epics/
.claude/context/
.claude/prds/
*.local.json
```

**Rationale:**
- `epics/` and `prds/` are local planning artifacts
- Context files may contain sensitive information
- Local config should not be committed

---

## Understanding CCPM Architecture

### Directory Structure
```
.claude/
├── CLAUDE.md              # Always-on instructions
├── agents/                # Task-oriented agents
├── commands/              # Command definitions
│   ├── context/          # Context management
│   ├── pm/               # Project management commands
│   └── testing/          # Test commands
├── context/              # Project-wide context (gitignored)
├── epics/                # Local workspace (gitignored)
│   └── [epic-name]/
│       ├── epic.md       # Implementation plan
│       ├── [#].md        # Task files (named by issue number)
│       └── updates/      # Work-in-progress updates
├── prds/                 # Product Requirements (gitignored)
├── rules/                # Rule files
├── scripts/              # Executable scripts
└── settings.local.json   # Local configuration
```

### File Lifecycle

1. **PRD Creation** → `.claude/prds/feature-name.md`
2. **Epic Planning** → `.claude/epics/feature-name/epic.md`
3. **Task Decomposition** → `.claude/epics/feature-name/001.md`, `002.md`, etc.
4. **GitHub Sync** → Tasks become GitHub issues
5. **File Renaming** → `001.md` → `1234.md` (issue number)
6. **Execution** → Agents work in git worktrees or main branch
7. **Updates** → Progress tracked in `updates/` directory
8. **Completion** → Issues closed, epic marked complete

---

## Workflow Guide

### Phase 1: Product Requirements Document (PRD)

#### Create New PRD
```bash
/pm:prd-new feature-name
```

**What to Include:**
- **Vision**: What problem does this solve?
- **User Stories**: Who benefits and how?
- **Success Criteria**: How do we measure success?
- **Constraints**: Technical limitations, timeline, resources
- **Edge Cases**: What could go wrong?

#### List All PRDs
```bash
/pm:prd-list
```

#### Edit Existing PRD
```bash
/pm:prd-edit feature-name
```

#### Check PRD Status
```bash
/pm:prd-status feature-name
```

---

### Phase 2: Epic Planning

#### Parse PRD to Epic
```bash
/pm:prd-parse feature-name
```

**This Creates:** `.claude/epics/feature-name/epic.md`

**Epic Should Include:**
- **Technical Approach**: Architecture decisions
- **Dependencies**: What needs to exist first
- **Risk Assessment**: Potential blockers
- **Implementation Strategy**: High-level steps

#### View Epic
```bash
/pm:epic-show feature-name
```

#### Edit Epic
```bash
/pm:epic-edit feature-name
```

---

### Phase 3: Task Decomposition

#### Decompose Epic into Tasks
```bash
/pm:epic-decompose feature-name
```

**This Creates:** Individual task files (`001.md`, `002.md`, etc.)

**Each Task Should Have:**
- **Title**: Clear, actionable description
- **Description**: Detailed implementation notes
- **Acceptance Criteria**: How to know it's done
- **Dependencies**: What must be completed first
- **Effort Estimate**: Complexity assessment
- **Parallel Flag**: Can this run simultaneously with others?

#### Task File Example
```markdown
---
title: Implement user authentication service
epic: user-auth
dependencies: []
effort: medium
parallel: true
---

## Description
Create authentication service with JWT token generation and validation.

## Acceptance Criteria
- [ ] User can login with email/password
- [ ] JWT token generated on successful login
- [ ] Token validation middleware created
- [ ] Password hashing implemented
- [ ] Unit tests cover all authentication flows

## Technical Notes
- Use bcrypt for password hashing
- JWT secret from environment variable
- Token expiry: 24 hours
- Refresh token support for future iteration

## Dependencies
- Database schema for users table
- Environment configuration setup
```

---

### Phase 4: GitHub Synchronization

#### One-Shot: Decompose and Sync
```bash
/pm:epic-oneshot feature-name
```

This combines decomposition and sync into one command.

#### Manual Sync
```bash
# First decompose
/pm:epic-decompose feature-name

# Then sync to GitHub
/pm:epic-sync feature-name
```

**What Happens:**
1. Creates parent epic issue on GitHub
2. Creates sub-issues for each task
3. Establishes parent-child relationships (using gh-sub-issue)
4. Adds appropriate labels (`epic:feature-name`, `task:feature-name`)
5. Renames local files from `001.md` → `1234.md` (issue number)

#### Verify on GitHub
```bash
# View epic issue
gh issue view [epic-number]

# List all issues for epic
gh issue list --label "epic:feature-name"
```

---

### Phase 5: Execution

#### Start Work on an Issue
```bash
/pm:issue-start 1234
```

**What This Does:**
- Loads specialized agent for the task type
- Reads task requirements from `.claude/epics/feature-name/1234.md`
- Reads project context from `.claude/context/`
- Begins implementation with full context

#### Check Issue Status
```bash
/pm:issue-status 1234
```

#### View Issue Details
```bash
/pm:issue-show 1234
```

#### Update Progress
As you work, document progress in update files:
```bash
# Agent should create/update:
.claude/epics/feature-name/updates/1234-progress.md
```

#### Sync Progress to GitHub
```bash
/pm:issue-sync 1234
```

This posts progress updates as GitHub issue comments.

#### Complete Issue
```bash
/pm:issue-close 1234
```

#### Reopen Issue (if needed)
```bash
/pm:issue-reopen 1234
```

---

### Phase 6: Parallel Execution

#### Understanding Parallel Work

Traditional approach:
- 1 epic = 3 issues
- Sequential execution
- 1 agent at a time

**CCPM approach:**
- 1 epic = 3 issues
- Each issue can spawn multiple parallel agents
- 12+ agents working simultaneously

#### Analyze Parallelization Opportunities
```bash
/pm:issue-analyze 1234
```

#### Start Epic with All Parallel Tasks
```bash
/pm:epic-start feature-name
```

**What This Does:**
- Identifies all tasks marked `parallel: true`
- Launches specialized agents for each
- Creates git worktrees for isolation (optional)
- Coordinates through commits

#### Work in Worktrees (Advanced)
```bash
# Create worktree for epic
/pm:epic-start-worktree feature-name

# This creates:
../epic-feature-name/  # Separate working directory
```

**Benefits:**
- Complete isolation from main branch
- Multiple agents can't conflict
- Easy to discard if needed
- Clean merge when complete

#### Merge Epic Worktree
```bash
/pm:epic-merge feature-name
```

---

### Phase 7: Progress Tracking

#### Get Next Priority Task
```bash
/pm:next
```

**This Shows:**
- Highest priority unassigned task
- Epic context
- Dependencies that must be completed first

#### View Overall Status
```bash
/pm:status
```

**Displays:**
- Active epics
- Issues in progress
- Blocked tasks
- Completion percentage

#### Daily Standup Report
```bash
/pm:standup
```

**Generates:**
- What was completed yesterday
- What's in progress today
- Blockers and risks

#### View Blocked Tasks
```bash
/pm:blocked
```

#### View In-Progress Work
```bash
/pm:in-progress
```

---

### Phase 8: Synchronization

#### Full Bidirectional Sync
```bash
/pm:sync
```

**What This Does:**
- Pulls latest issue updates from GitHub
- Pushes local progress updates
- Reconciles any conflicts
- Updates local task files with GitHub state

#### Import Existing GitHub Issues
```bash
/pm:import
```

Use this to bring existing GitHub issues into CCPM workflow.

---

### Phase 9: Maintenance

#### Validate System Integrity
```bash
/pm:validate
```

**Checks:**
- All epic files have corresponding issues
- All task files are properly linked
- No orphaned files
- Dependency chains are valid

#### Clean Completed Work
```bash
/pm:clean
```

**This:**
- Archives completed epics
- Removes old update files
- Cleans up temporary worktrees

#### Search Content
```bash
/pm:search "search term"
```

Searches across:
- PRDs
- Epics
- Task files
- Context files

#### Close Epic
```bash
/pm:epic-close feature-name
```

Marks epic and all tasks as complete.

---

## Command Reference

### Quick Command Summary

#### Setup
```bash
/pm:init                    # Initialize CCPM system
/context:create             # Create initial context files
/context:update             # Update existing context
/context:prime              # Load context in new session
```

#### PRD Management
```bash
/pm:prd-new <name>          # Create new PRD
/pm:prd-list                # List all PRDs
/pm:prd-edit <name>         # Edit existing PRD
/pm:prd-status <name>       # Show PRD status
/pm:prd-parse <name>        # Convert PRD to epic
```

#### Epic Management
```bash
/pm:epic-decompose <name>   # Break epic into tasks
/pm:epic-sync <name>        # Push to GitHub
/pm:epic-oneshot <name>     # Decompose + sync
/pm:epic-list               # List all epics
/pm:epic-show <name>        # Display epic details
/pm:epic-status <name>      # Show epic progress
/pm:epic-edit <name>        # Edit epic
/pm:epic-close <name>       # Mark epic complete
/pm:epic-refresh <name>     # Update from tasks
/pm:epic-start <name>       # Start parallel execution
/pm:epic-merge <name>       # Merge worktree
```

#### Issue Management
```bash
/pm:issue-show <number>     # Display issue
/pm:issue-status <number>   # Check status
/pm:issue-start <number>    # Begin work
/pm:issue-sync <number>     # Push updates
/pm:issue-close <number>    # Complete issue
/pm:issue-reopen <number>   # Reopen issue
/pm:issue-edit <number>     # Edit issue
/pm:issue-analyze <number>  # Find parallelization
```

#### Workflow
```bash
/pm:next                    # Get next task
/pm:status                  # Project dashboard
/pm:standup                 # Daily report
/pm:blocked                 # Show blockers
/pm:in-progress             # List WIP
```

#### Sync & Maintenance
```bash
/pm:sync                    # Full sync with GitHub
/pm:import                  # Import GitHub issues
/pm:validate                # Check integrity
/pm:clean                   # Archive completed
/pm:search <term>           # Search all content
```

#### Help
```bash
/pm:help                    # Show command summary
```

---

## Best Practices

### 1. Context Management

#### Always Prime Context
When starting a new session:
```bash
/context:prime
```

This loads all context files into the conversation.

#### Update Context Regularly
After significant changes:
```bash
/context:update
```

#### Keep Context Files Current
- Update `progress.md` after completing tasks
- Update `tech-context.md` when dependencies change
- Update `system-patterns.md` when architecture evolves

### 2. PRD Quality

**Good PRD Characteristics:**
- ✅ Specific user stories with clear value
- ✅ Measurable success criteria
- ✅ Identified edge cases and failure modes
- ✅ Explicit constraints and assumptions
- ✅ Technical considerations noted

**Poor PRD Characteristics:**
- ❌ Vague requirements ("make it better")
- ❌ No success criteria
- ❌ Missing edge cases
- ❌ Assumptions not documented

### 3. Task Decomposition

**Optimal Task Size:**
- 2-8 hours of focused work
- Single responsibility
- Clear acceptance criteria
- Minimal dependencies

**Task Parallelization:**
Mark as `parallel: true` only if:
- No file conflicts with other tasks
- No dependency on other task completion
- Can be tested independently

**Example:**
```markdown
# Good for parallel
✅ Task 1: Create database schema
✅ Task 2: Create API endpoints
✅ Task 3: Create UI components

# Not good for parallel (sequential dependencies)
❌ Task 1: Design API
❌ Task 2: Implement API (depends on Task 1)
❌ Task 3: Test API (depends on Task 2)
```

### 4. Commit Strategy

#### Atomic Commits
Each task should result in focused commits:
```bash
git commit -m "feat(auth): implement JWT token generation

- Add JWT library dependency
- Create token generation function
- Add token validation middleware
- Include unit tests

Closes #1234"
```

#### Reference Issues
Always include issue number in commits:
```bash
git commit -m "fix(auth): handle expired tokens (#1235)"
```

### 5. Progress Updates

#### Update Frequency
- Sync progress at natural checkpoints
- Don't sync every tiny change
- Do sync before taking breaks
- Always sync before switching tasks

#### Update Quality
```markdown
## Progress Update - 2025-11-16

### Completed
- ✅ Implemented JWT token generation
- ✅ Added token validation middleware
- ✅ Created unit tests for happy path

### In Progress
- 🔄 Implementing refresh token logic
- 🔄 Adding integration tests

### Blockers
- ⚠️ Need clarification on token expiry policy
- ⚠️ Waiting for security review

### Next Steps
- Complete refresh token implementation
- Add error handling for edge cases
- Update API documentation
```

### 6. GitHub Integration

#### Issue Labels
Use consistent labeling:
- `epic:feature-name` - Epic parent issues
- `task:feature-name` - Individual tasks
- `parallel` - Can be worked on simultaneously
- `blocked` - Waiting on dependency
- `priority:high` - Urgent work

#### Issue Comments
Post meaningful updates:
```markdown
## Update - 2025-11-16 14:30 UTC

Made significant progress on authentication service:

**Completed:**
- JWT token generation with configurable expiry
- Password hashing using bcrypt
- Basic unit test coverage

**Code Changes:**
- `src/auth/token.js` - Token generation and validation
- `src/auth/hash.js` - Password hashing utilities
- `tests/auth.test.js` - Unit tests

**Next:**
- Implement refresh token mechanism
- Add integration tests
- Update API documentation

**Questions:**
- Should we support social auth in this iteration?
```

### 7. Agent Specialization

#### Use Appropriate Agents
CCPM includes specialized agents:
- **UI Agent** - React/Vue components
- **API Agent** - Backend endpoints
- **Database Agent** - Schema and migrations
- **Test Agent** - Test suites
- **Doc Agent** - Documentation

#### Agent Context
Each agent should:
- Read task requirements
- Load relevant context files
- Focus on single responsibility
- Update progress in `updates/` directory

### 8. Error Handling

#### When Tasks Fail
```bash
# Document the issue
echo "## Blocker - $(date -u +%Y-%m-%dT%H:%M:%SZ)

Issue #1234 blocked due to missing dependency.

**Problem:**
Cannot implement feature X without library Y being upgraded.

**Impact:**
Blocks tasks #1235, #1236

**Resolution:**
Need to upgrade library Y to v2.0+

**Workaround:**
Can implement partial feature with current version.
" >> .claude/epics/feature-name/updates/1234-blocker.md

# Mark issue as blocked
gh issue edit 1234 --add-label blocked

# Create blocking issue if needed
gh issue create --title "Upgrade library Y to v2.0" \
  --body "Required for #1234" \
  --label dependency
```

### 9. Context Preservation

#### Before Long Breaks
```bash
# Update all context
/context:update

# Sync all progress
/pm:sync

# Document current state
/pm:status > status-$(date +%Y%m%d).md
```

#### After Long Breaks
```bash
# Prime context
/context:prime

# Review status
/pm:status

# Check for updates
/pm:sync

# Get next task
/pm:next
```

### 10. Code Quality

#### Before Closing Issues
Verify:
- ✅ All acceptance criteria met
- ✅ Tests passing
- ✅ Code reviewed (if applicable)
- ✅ Documentation updated
- ✅ No console errors/warnings
- ✅ Linting passes
- ✅ Committed and pushed

#### Quality Checklist
```markdown
## Pre-Close Checklist for Issue #1234

- [x] All acceptance criteria completed
- [x] Unit tests written and passing
- [x] Integration tests written and passing
- [x] Code follows style guide
- [x] No linting errors
- [x] Documentation updated
- [x] Peer review completed (if required)
- [x] Manually tested edge cases
- [x] Performance acceptable
- [x] Security review done (if applicable)
- [x] Changes committed to feature branch
- [x] PR created and linked to issue
```

---

## Troubleshooting

### Command Not Found

**Problem:** Slash commands not recognized
```bash
Unknown slash command: pm:init
```

**Solutions:**
1. Verify `.claude/commands/` directory exists
2. Check that command files are present
3. Restart Claude Code session
4. Manually execute scripts:
   ```bash
   bash .claude/scripts/pm/init.sh
   ```

### GitHub Authentication Failed

**Problem:** `gh` not authenticated
```bash
To get started with GitHub CLI, please run:  gh auth login
```

**Solution:**
```bash
gh auth login
# Follow prompts to authenticate
gh auth status
```

### Missing gh-sub-issue Extension

**Problem:** Parent-child relationships not created
```bash
extension "gh-sub-issue" is not installed
```

**Solution:**
```bash
gh extension install yahsan2/gh-sub-issue
gh extension list
```

### File Permission Errors

**Problem:** Cannot create files
```bash
Permission denied: .claude/context/
```

**Solutions:**
```bash
# Check permissions
ls -la .claude

# Fix permissions (Unix/Linux/macOS)
chmod -R 755 .claude

# Windows: Right-click → Properties → Security
```

### Git Not Initialized

**Problem:** Not a git repository
```bash
fatal: not a git repository
```

**Solution:**
```bash
git init
git add .
git commit -m "Initial commit"
```

### Missing Remote

**Problem:** Cannot push to GitHub
```bash
fatal: No configured push destination
```

**Solution:**
```bash
# Add remote
git remote add origin https://github.com/username/repo.git

# Verify
git remote -v
```

### Context Files Missing

**Problem:** Context not found
```bash
No context files in .claude/context/
```

**Solution:**
```bash
/context:create
# Or manually:
# Read .claude/commands/context/create.md for instructions
```

### Issue Sync Failures

**Problem:** Cannot sync to GitHub
```bash
Error: Issue not found
```

**Solutions:**
1. Verify issue exists:
   ```bash
   gh issue view 1234
   ```

2. Check GitHub connectivity:
   ```bash
   gh auth status
   gh repo view
   ```

3. Re-sync epic:
   ```bash
   /pm:epic-sync feature-name
   ```

### Task File Name Mismatch

**Problem:** Task file doesn't match issue number
```bash
Expected: 1234.md, Found: 001.md
```

**Solution:**
Task files are numbered `001.md`, `002.md` before GitHub sync.
After sync, they're renamed to issue numbers.

```bash
# Re-sync to fix naming
/pm:epic-sync feature-name
```

### Merge Conflicts in Worktrees

**Problem:** Conflict when merging worktree
```bash
CONFLICT (content): Merge conflict in src/file.js
```

**Solution:**
```bash
# Navigate to worktree
cd ../epic-feature-name

# Resolve conflicts manually
git status
# Edit conflicted files
git add .
git commit

# Complete merge
cd ../main-project
/pm:epic-merge feature-name
```

### Orphaned Issues

**Problem:** GitHub issue without local task file
```bash
Warning: Issue #1234 has no local task file
```

**Solution:**
```bash
# Import from GitHub
/pm:import

# Or create task file manually
# .claude/epics/feature-name/1234.md
```

### Context Too Large

**Problem:** Context files consuming too much token budget
```bash
Warning: Context files exceed recommended size
```

**Solutions:**
1. Split large context files into focused sections
2. Use `/context:prime` selectively (only load needed files)
3. Archive old/irrelevant context
4. Keep context current, remove obsolete information

---

## Advanced Patterns

### 1. Multi-Epic Projects

For large projects with multiple epics:

```bash
# Structure
.claude/epics/
  ├── auth-system/
  ├── payment-integration/
  ├── notification-service/
  └── admin-dashboard/

# Work on multiple epics in parallel
/pm:epic-start auth-system
/pm:epic-start payment-integration

# Track overall project status
/pm:status
```

### 2. Emergency Hotfixes

For urgent fixes outside epic workflow:

```bash
# Create hotfix branch
git checkout -b hotfix/critical-bug

# Create minimal task file
cat > .claude/epics/hotfixes/urgent-fix.md << 'EOF'
---
title: Fix critical authentication bug
type: hotfix
priority: critical
---

## Problem
Users cannot login due to token validation error.

## Solution
Update token validation logic to handle edge case.

## Testing
- Manual testing on staging
- Verify fix resolves reported issues
EOF

# Implement and commit
# Push directly without full CCPM workflow
git push origin hotfix/critical-bug

# Create PR
gh pr create --title "Hotfix: Critical auth bug" \
  --body "Fixes #urgent-issue"
```

### 3. Dependency Management

Track external dependencies:

```bash
# .claude/context/dependencies.md
## Current Dependencies

### Critical Path
- Issue #1234 blocks #1235, #1236
- Library upgrade required for #1240

### External Dependencies
- Waiting on API provider for webhook documentation (#1250)
- Design team finalizing UI mockups (#1260)

### Technical Debt
- Refactor auth layer (#1270) - improves future work
- Update test framework (#1280) - unblocks parallel testing
```

### 4. Context Versioning

Version context for major milestones:

```bash
# Before major release
cp -r .claude/context .claude/context-v1.0.0

# After significant architecture change
cp -r .claude/context .claude/context-post-refactor

# Track in git (if desired)
git add .claude/context-v*.0.0
git commit -m "docs: archive context for v1.0.0"
```

---

## Integration with Other Tools

### CI/CD Integration

```yaml
# .github/workflows/ccpm-sync.yml
name: CCPM Sync

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup GitHub CLI
        run: |
          gh extension install yahsan2/gh-sub-issue
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Validate CCPM Structure
        run: |
          bash .claude/scripts/pm/validate.sh

      - name: Sync with GitHub
        run: |
          bash .claude/scripts/pm/sync.sh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### VS Code Integration

Create tasks in `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "CCPM: Status",
      "type": "shell",
      "command": "bash .claude/scripts/pm/status.sh",
      "problemMatcher": []
    },
    {
      "label": "CCPM: Next Task",
      "type": "shell",
      "command": "bash .claude/scripts/pm/next.sh",
      "problemMatcher": []
    }
  ]
}
```

### Slack Notifications

```bash
# Add to .claude/hooks/post-sync.sh
#!/bin/bash
# Notify team on issue completion

if [ "$ISSUE_STATUS" = "closed" ]; then
  curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{
      \"text\": \"✅ Issue #$ISSUE_NUMBER completed: $ISSUE_TITLE\",
      \"username\": \"CCPM Bot\"
    }"
fi
```

---

## Summary Checklist

### Initial Setup
- [ ] Git repository initialized
- [ ] GitHub CLI installed and authenticated
- [ ] CCPM installed (`.claude/` directory present)
- [ ] Initialization script run (`/pm:init`)
- [ ] Initial context created (`/context:create`)
- [ ] `.gitignore` updated

### For Each Feature
- [ ] PRD created with comprehensive requirements
- [ ] Epic planned with technical approach
- [ ] Tasks decomposed with clear acceptance criteria
- [ ] Epic synced to GitHub
- [ ] Parallel tasks identified
- [ ] Work executed with progress updates
- [ ] All issues closed
- [ ] Epic marked complete

### Ongoing Maintenance
- [ ] Context updated regularly
- [ ] Progress synced to GitHub
- [ ] Status reviewed weekly
- [ ] Blocked tasks addressed
- [ ] Completed work archived
- [ ] System validated periodically

---

## Conclusion

CCPM transforms AI-assisted development from ad-hoc coding to systematic software engineering. By following this guide, you'll:

✅ Maintain complete context across sessions
✅ Work on multiple tasks in parallel
✅ Track every decision from idea to code
✅ Collaborate effectively with teams
✅ Ship features faster with fewer bugs

**Key Takeaway:** Discipline in planning and documentation pays off exponentially in execution quality and velocity.

For support and updates:
- GitHub: https://github.com/automazeio/ccpm
- Documentation: README.md and docs/
- Issues: https://github.com/automazeio/ccpm/issues

---

*Generated: 2025-11-16*
*Version: 1.0.0*
*For: AI Assistants using Claude Code*
