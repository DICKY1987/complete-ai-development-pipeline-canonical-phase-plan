---
doc_id: DOC-GUIDE-DEV-GITIGNORE-RECOMMENDATIONS-345
---

# .gitignore Recommendations for File Organization System
# Add these entries to your .gitignore file

# ============================================================================
# RUNTIME ARTIFACTS (Never Commit)
# ============================================================================

# Worktree folders (per-workstream working directories)
.worktrees/

# Execution runs and records
.runs/

# Task queue storage
.tasks/

# Execution ledger
.ledger/

# Application logs
logs/
*.log

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Test cache
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.venv/
venv/
.env.local

# OS
.DS_Store
Thumbs.db

# ============================================================================
# DEVELOPMENT WORKSPACE (Optional - For Local Drafts)
# ============================================================================

# Uncomment these if you want to keep drafts/scratch notes locally
# devdocs/scratch/
# devdocs/.drafts/
# *.draft.md
# *.tmp.md

# ============================================================================
# NOTES ON devdocs/
# ============================================================================

# The devdocs/ directory itself is NOT gitignored!
# Development artifacts (phase plans, session logs, etc.) ARE committed
# for continuity across sessions and team collaboration.
#
# Only exclude devdocs/ content that is truly personal/temporary:
# - Local scratch notes
# - Draft documents before finalization
# - Temporary analysis files
#
# The general rule: If it documents the development process and would be
# useful to future you or other developers, commit it to devdocs/.

# ============================================================================
# EXISTING ENTRIES (Keep These)
# ============================================================================
# Your existing .gitignore entries should be preserved above these additions
