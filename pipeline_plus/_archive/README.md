# Archive Directory - Pipeline Plus

**Created:** 2025-11-20 14:01:20
**Purpose:** Historical preservation - these files are NOT for active development

---

## 📂 Directory Structure

### /exploration (8 files)
Legacy exploratory work and proof-of-concepts that have been superseded by production implementation.

**Files:**
- \ully-autonomous refactor runner.md\ - Early autonomous refactor concepts
- \data and indirection refactor.md\ - Data model exploration notes
- \orchestration-scripts.md\ - Pre-implementation orchestration ideas
- \ollama-code.md\ - Ollama integration notes
- \slim_ASCII-only_render_workstream_prompt_py.md\ - Rendering exploration
- \# ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC_V1.md\ - Superseded router spec
- \CLAUDE.md\ - Duplicate AI tool notes
- \Task-enqueue script (pushes tasks to Aider).md\ - Early task queue concept

**Status:** Superseded by production implementation in AGENTIC_DEV_PROTOTYPE/
**Reuse Value:** Historical context only

### /external_copies (2 files)
External content copied during development (diagnostic outputs, AI responses).

**Files:**
- \2025-11-19-caveat-the-messages-below-were-generated-by-the-u.txt\
- \2025-11-19-command-messageinit-is-analyzing-your-codebase.txt\

**Status:** Temporary diagnostic files
**Reuse Value:** None - can be deleted after 30 days

### /reference (2 files)
Reference documentation for Aider workstream patterns and tool comparisons.

**Files:**
- \Aider-tuned WORKSTREAM_V1.md\ - Aider-specific workstream patterns
- \What DeepSeek-Coder actually adds to your stack.md\ - Tool comparison notes

**Status:** Reference materials (may still be useful)
**Reuse Value:** Medium - consult when working with similar patterns

---

## 🚫 Archival Policy

### AI Exclusion
This directory is EXCLUDED from AI tool indexing via:
- \.aiderignore\ pattern: \_archive/\
- \.aicontext\ exclude pattern: \_archive/**\

### Access Policy
- ✅ Can be referenced via citation in active docs
- ✅ Can be restored if specific content needed
- ❌ Do NOT use as source for new development
- ❌ Do NOT copy content without updating to current patterns

### Retention Policy
- **Exploration files:** Review annually, delete if zero citations after 2 years
- **External copies:** Delete after 30 days (11/20/2025 14:01:20.AddDays(30).ToString('yyyy-MM-dd'))
- **Reference materials:** Keep indefinitely, update if patterns change

---

## 📊 Archive Statistics

- **Total files archived:** 12
- **Total size:** ~2779.1 KB
- **Archived on:** 2025-11-20
- **Archived by:** Automated cleanup Phase 2

---

## 🔍 Finding Archived Content

**If you need content from an archived file:**

1. Check if it's been incorporated into active docs
2. Review the file in place (read-only)
3. If content is still needed, create a new file in active area with updated patterns
4. Cite the archive file as source

**Do NOT:**
- Copy archived content verbatim
- Move files out of archive without review
- Reference archived files in new code

---

## 📞 Questions?

- **Why was my file archived?** See cleanup documentation in \C:\\Users\\richg\\ALL_AI\\CLEANUP_*.md\
- **Can I restore it?** Yes, but review and update to current patterns first
- **Is this safe to delete?** External copies: Yes after 30 days. Others: Check citations first.

---

**Last Updated:** 2025-11-20 14:01:20
**Next Review:** 11/20/2025 14:01:20.AddMonths(3).ToString('yyyy-MM-dd') (Quarterly review)
