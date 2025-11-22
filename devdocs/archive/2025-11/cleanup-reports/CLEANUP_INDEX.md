# AI Development Directory Cleanup - Document Index

**Project:** Pipeline Plus Directory Reorganization  
**Date Created:** 2025-11-20  
**Status:** Ready for Review & Execution

---

## 📚 Document Library

### 1. **CLEANUP_PROJECT_SUMMARY.md** ⭐ START HERE
**Size:** 17KB | **Read Time:** 15 minutes  
**Audience:** All stakeholders

**Purpose:** Executive overview and quick start guide

**Contents:**
- Current state analysis
- Cleanup scope and metrics
- 4-phase execution roadmap
- Quick start guide
- Success criteria
- Risk mitigation
- Timeline summary

**When to read:** First document - provides project overview

---

### 2. **CLEANUP_REORGANIZATION_STRATEGY.md** 📋 MASTER PLAN
**Size:** 25KB | **Read Time:** 30 minutes  
**Audience:** Project leads, architects

**Purpose:** Complete multi-phase cleanup strategy with detailed steps

**Contents:**
- Architecture analysis (5 functional zones)
- Proposed directory structure (hexagonal/ports & adapters)
- Phase 1: Inventory & Classification (4 hours)
- Phase 2: Consolidation (6 hours)
- Phase 3: Archival Strategy (3 hours)
- Phase 4: Removal & Validation (2 hours)
- AI usability optimization
- Maintenance best practices
- Migration scripts (Appendix)
- Success metrics

**When to read:** Before executing any cleanup phases

---

### 3. **AI_DEV_HYGIENE_GUIDELINES.md** 🧹 DAILY REFERENCE
**Size:** 12KB | **Read Time:** 10 minutes  
**Audience:** All developers

**Purpose:** Quick reference for maintaining clarity during development

**Contents:**
- 5 Golden Rules for AI-friendly organization
- File naming standards (`CATEGORY_SUBJECT_VERSION.ext`)
- Directory organization rules (4-layer max)
- File header frontmatter requirements
- Context priority levels (P0-P4)
- Pre-commit checklist
- Tool-specific practices (Aider, Codex, Claude)
- Deletion policy
- Quarterly maintenance routine

**When to read:** 
- During onboarding
- Before creating new files
- Before committing to core directories

---

### 4. **PROPOSED_DIRECTORY_TREE.md** 🗂️ VISUAL REFERENCE
**Size:** 17KB | **Read Time:** 10 minutes  
**Audience:** All team members

**Purpose:** Visual reference of target directory structure

**Contents:**
- Complete directory tree with annotations
- Purpose and AI priority for each directory
- Color-coded legend
- Directory statistics (before/after)
- Migration mapping examples
- Context optimization config
- Validation checklist
- Quick navigation guide

**When to read:**
- When deciding where to place new files
- During reorganization for reference
- When explaining structure to new team members

---

### 5. **CLEANUP_INDEX.md** 📖 THIS DOCUMENT
**Size:** 6KB | **Read Time:** 5 minutes  
**Audience:** All stakeholders

**Purpose:** Navigation guide for all cleanup documentation

---

## 🎯 Reading Paths by Role

### 👔 Leadership / Decision Makers
**Time Investment:** 20 minutes

1. **CLEANUP_PROJECT_SUMMARY.md**
   - Read: Executive Summary, Cleanup Scope, Timeline Summary
   - Decision: Approve project and allocate resources

**Key Takeaway:** 3-week project to organize 250+ files into clear architecture, reducing AI context confusion. Low risk with backup/rollback plan.

---

### 🏗️ Project Lead / Architect
**Time Investment:** 60 minutes

1. **CLEANUP_PROJECT_SUMMARY.md** (full read)
2. **CLEANUP_REORGANIZATION_STRATEGY.md** (full read)
3. **PROPOSED_DIRECTORY_TREE.md** (review structure)
4. **AI_DEV_HYGIENE_GUIDELINES.md** (skim for reference)

**Key Actions:**
- Review Phase 1-4 detailed plans
- Schedule 3-week sprint
- Create backup and rollback scripts
- Assign phase owners

---

### 👨‍💻 Developer / Contributor
**Time Investment:** 30 minutes

1. **CLEANUP_PROJECT_SUMMARY.md** (Quick Start Guide section)
2. **AI_DEV_HYGIENE_GUIDELINES.md** (full read)
3. **PROPOSED_DIRECTORY_TREE.md** (navigation guide)
4. **CLEANUP_REORGANIZATION_STRATEGY.md** (scripts appendix)

**Key Actions:**
- Learn new naming conventions
- Understand directory purposes
- Bookmark guidelines for daily use
- Practice pre-commit checklist

---

### 🤖 AI Tool User
**Time Investment:** 15 minutes

1. **AI_DEV_HYGIENE_GUIDELINES.md**
   - Read: AI Tool-Specific Practices section
   - Read: Context Priority Levels section
2. **PROPOSED_DIRECTORY_TREE.md**
   - Review: AI Indexing Configuration section

**Key Actions:**
- Configure `.aiderignore`, `.aicontext` files
- Understand priority levels (P0-P4)
- Use explicit file scope in prompts

---

### 🆕 New Team Member (Onboarding)
**Time Investment:** 45 minutes

**Day 1:**
1. **CLEANUP_PROJECT_SUMMARY.md** (Overview)
2. **PROPOSED_DIRECTORY_TREE.md** (Quick Navigation Guide)

**Week 1:**
3. **AI_DEV_HYGIENE_GUIDELINES.md** (full read)
4. **CLEANUP_REORGANIZATION_STRATEGY.md** (Sections I-III)

**Key Actions:**
- Navigate directory structure confidently
- Follow naming conventions
- Use pre-commit checklist
- Ask questions about unclear areas

---

## 🚀 Execution Quick Reference

### Phase 1: Inventory (Week 1)
**Lead Document:** CLEANUP_REORGANIZATION_STRATEGY.md - Section III.1  
**Scripts:** Appendix A (generate_inventory.ps1), Appendix B (identify_duplicates.ps1)  
**Deliverable:** `INVENTORY_MASTER.csv`, `DUPLICATION_REPORT.md`

---

### Phase 2: Consolidation (Week 2)
**Lead Document:** CLEANUP_REORGANIZATION_STRATEGY.md - Section III.2  
**Reference:** PROPOSED_DIRECTORY_TREE.md (target structure)  
**Deliverable:** Reorganized `/core`, `/specs`, `/docs`

---

### Phase 3: Archival (Week 2-3)
**Lead Document:** CLEANUP_REORGANIZATION_STRATEGY.md - Section III.3  
**Deliverable:** `_archive/` with READMEs and exclusion patterns

---

### Phase 4: Removal (Week 3)
**Lead Document:** CLEANUP_REORGANIZATION_STRATEGY.md - Section III.4  
**Scripts:** Appendix C (validate_links.ps1)  
**Deliverable:** `DELETION_LOG.md`, `RENAME_LOG.md`, updated README

---

## 📊 Document Dependencies

```
CLEANUP_INDEX.md (You are here)
    ↓
CLEANUP_PROJECT_SUMMARY.md ← START HERE
    ↓
    ├─→ CLEANUP_REORGANIZATION_STRATEGY.md (Master Plan)
    │       ├─→ Scripts (Appendix X)
    │       └─→ Best Practices (Section V)
    │
    ├─→ AI_DEV_HYGIENE_GUIDELINES.md (Daily Reference)
    │       └─→ Pre-commit Checklist
    │
    └─→ PROPOSED_DIRECTORY_TREE.md (Visual Reference)
            └─→ Migration Mapping
```

---

## 🔍 Quick Finder

**"How do I...?"**

| Task | Document | Section |
|------|----------|---------|
| Understand the project scope | CLEANUP_PROJECT_SUMMARY.md | Executive Summary |
| Execute Phase 1 inventory | CLEANUP_REORGANIZATION_STRATEGY.md | Section III.1 |
| Learn file naming rules | AI_DEV_HYGIENE_GUIDELINES.md | File Naming Standards |
| Find where to place a new file | PROPOSED_DIRECTORY_TREE.md | Quick Navigation Guide |
| Configure AI tool exclusions | AI_DEV_HYGIENE_GUIDELINES.md | AI Tool-Specific Practices |
| Create backup before migration | CLEANUP_REORGANIZATION_STRATEGY.md | Section XI (Rollback Plan) |
| Run duplicate detection | CLEANUP_REORGANIZATION_STRATEGY.md | Appendix B |
| Validate links after changes | CLEANUP_REORGANIZATION_STRATEGY.md | Appendix C |
| Understand directory purposes | PROPOSED_DIRECTORY_TREE.md | Directory Tree (annotations) |
| Learn quarterly maintenance | AI_DEV_HYGIENE_GUIDELINES.md | Quarterly Maintenance Routine |

---

## ✅ Pre-Execution Checklist

Before starting cleanup:

- [ ] Read CLEANUP_PROJECT_SUMMARY.md (Executive Summary)
- [ ] Review CLEANUP_REORGANIZATION_STRATEGY.md (Phases 1-4)
- [ ] Understand PROPOSED_DIRECTORY_TREE.md (target structure)
- [ ] Create backup of `pipeline_plus` directory
- [ ] Document current state (tree output, test results)
- [ ] Generate rollback script
- [ ] Schedule 3-week sprint
- [ ] Assign phase owners
- [ ] Communicate to stakeholders

---

## 📅 Timeline at a Glance

| Week | Phase | Document Reference | Deliverables |
|------|-------|-------------------|--------------|
| **1** | Inventory | CLEANUP_REORGANIZATION_STRATEGY.md III.1 | Inventory, duplicates report |
| **2** | Consolidation | CLEANUP_REORGANIZATION_STRATEGY.md III.2 | Reorganized core/specs/docs |
| **2-3** | Archival | CLEANUP_REORGANIZATION_STRATEGY.md III.3 | Archive with exclusions |
| **3** | Removal | CLEANUP_REORGANIZATION_STRATEGY.md III.4 | Clean structure, validated |

---

## 🎓 Training Materials

### For Team Onboarding

**Self-Paced Learning Path:**
1. Read CLEANUP_PROJECT_SUMMARY.md (15 min)
2. Explore PROPOSED_DIRECTORY_TREE.md (10 min)
3. Study AI_DEV_HYGIENE_GUIDELINES.md (10 min)
4. Practice: Create a test file following conventions (15 min)
5. Review: Pre-commit checklist (5 min)

**Total Time:** ~55 minutes

---

### Workshop Outline (90 minutes)

**Session 1: Overview (30 min)**
- Present: CLEANUP_PROJECT_SUMMARY.md
- Q&A: Scope and timeline

**Session 2: New Structure (30 min)**
- Walkthrough: PROPOSED_DIRECTORY_TREE.md
- Demo: Navigate new structure

**Session 3: Best Practices (30 min)**
- Review: AI_DEV_HYGIENE_GUIDELINES.md
- Hands-on: Create sample files
- Practice: Pre-commit checklist

---

## 🔗 External References

**Architecture Patterns:**
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

**AI Context Management:**
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [GitHub Codex Best Practices](https://github.com/features/copilot)

**Project Management:**
- [Agile Sprint Planning](https://www.atlassian.com/agile/scrum/sprint-planning)

---

## 📞 Support & Feedback

### Questions About Documents

**This Index:**
- Contact: Project Lead

**Strategy & Execution:**
- See: CLEANUP_REORGANIZATION_STRATEGY.md
- Contact: Architect / Project Lead

**Daily Practices:**
- See: AI_DEV_HYGIENE_GUIDELINES.md
- Contact: Senior Developer

**Directory Structure:**
- See: PROPOSED_DIRECTORY_TREE.md
- Contact: Architect

---

## 🔄 Document Maintenance

### Review Cycle

**Monthly (During Cleanup):**
- Update CLEANUP_PROJECT_SUMMARY.md with progress
- Add lessons learned to CLEANUP_REORGANIZATION_STRATEGY.md

**Quarterly (Post-Cleanup):**
- Review AI_DEV_HYGIENE_GUIDELINES.md for new patterns
- Update PROPOSED_DIRECTORY_TREE.md if structure changes

**Annually:**
- Archive old versions
- Consolidate lessons learned
- Update based on team feedback

---

## 📈 Success Metrics

Track these after cleanup:

| Metric | Document Source | Target |
|--------|-----------------|--------|
| Files with status tags | AI_DEV_HYGIENE_GUIDELINES.md | 95%+ |
| Duplicate files | CLEANUP_REORGANIZATION_STRATEGY.md | 0 |
| AI context clarity | CLEANUP_PROJECT_SUMMARY.md | >95% |
| Team understanding | Survey post-onboarding | >90% |
| Directory depth | PROPOSED_DIRECTORY_TREE.md | ≤4 levels |

---

## 🎯 Next Steps

1. **Read** CLEANUP_PROJECT_SUMMARY.md (START HERE)
2. **Review** CLEANUP_REORGANIZATION_STRATEGY.md (Master Plan)
3. **Reference** AI_DEV_HYGIENE_GUIDELINES.md (Daily Use)
4. **Consult** PROPOSED_DIRECTORY_TREE.md (Visual Guide)
5. **Execute** Phase 1: Inventory

---

## ✨ Document Highlights

**Best Sections by Use Case:**

| Use Case | Document | Section |
|----------|----------|---------|
| **Quick project overview** | CLEANUP_PROJECT_SUMMARY.md | Executive Summary |
| **Detailed execution steps** | CLEANUP_REORGANIZATION_STRATEGY.md | Section III (Phases 1-4) |
| **File naming rules** | AI_DEV_HYGIENE_GUIDELINES.md | File Naming Standards |
| **Where to put files** | PROPOSED_DIRECTORY_TREE.md | Quick Navigation Guide |
| **AI tool configuration** | AI_DEV_HYGIENE_GUIDELINES.md | AI Tool-Specific Practices |
| **Scripts for automation** | CLEANUP_REORGANIZATION_STRATEGY.md | Appendix X |
| **Pre-commit checks** | AI_DEV_HYGIENE_GUIDELINES.md | Pre-Commit Checklist |
| **Quarterly maintenance** | AI_DEV_HYGIENE_GUIDELINES.md | Quarterly Routine |

---

## 🏆 Project Goals Recap

1. **Eliminate** AI context contamination from legacy/outdated files
2. **Organize** ~250 files into clear architecture-aligned structure
3. **Establish** maintainable governance with quarterly reviews
4. **Improve** developer velocity with clear navigation
5. **Enable** accurate AI assistance with context priority system

---

**All documents ready for review and execution. Good luck with the cleanup! 🚀**

---

**END OF INDEX**
