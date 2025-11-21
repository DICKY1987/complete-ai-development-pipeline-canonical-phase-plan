# AI Development Directory - Systematic Cleanup & Reorganization Strategy

**Date:** 2025-11-20  
**Target Directory:** `C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus`  
**Current State:** Mixed legacy/active files risking AI context contamination

---

## Executive Summary

Your directory contains **three active systems** with significant legacy/reference overlap:

1. **Pipeline Plus** - Production-ready patch-based orchestration (100% complete, 118 tests passed)
2. **AGENTIC_DEV_PROTOTYPE** - Game Board Protocol orchestration (19/19 phases, production ready)
3. **Reference Materials** - Prompt engineering guides, anti-patterns, external resources

**Key Risk:** AI tools may inject outdated context from legacy documents during code generation.

---

## I. ARCHITECTURE ANALYSIS

### Functional Zones Identified

#### Zone 1: CORE PRODUCTION SYSTEMS (Active)
**Location:** `pipeline_plus/AGENTIC_DEV_PROTOTYPE/src/`

**Components:**
- `orchestrator/` - Core orchestration engine (state machine, dependency resolver, parallel executor)
- `validators/` - Schema validation, guard rules engine
- `adapters/` - Aider, Codex, Claude integrations
- `patch_manager.py` - Git patch lifecycle management
- `prompt_renderer.py` - WORKSTREAM_V1.1 template engine
- `task_queue.py` - Priority-based FIFO queue
- `validation_gateway.py` - 3-layer validation pipeline

**Architecture Pattern:** Hexagonal/Ports & Adapters
- **Core Domain:** Orchestration, validation, state management
- **Adapters:** Tool-specific integrations (Aider, Codex, Claude)
- **Ports:** Task queue, patch management, audit logging

**Status:** ✅ Production-ready, tested, documented

---

#### Zone 2: SPECIFICATIONS & CONTRACTS (Active Reference)
**Location:** `pipeline_plus/AGENTIC_DEV_PROTOTYPE/specs/`

**Components:**
- `UNIVERSAL_PHASE_SPEC_V1.md` - Universal phase specification standard
- `PRO_PHASE_SPEC_V1.md` - Professional phase specification
- `DEV_RULES_V1.md` - Development rules and constraints
- Phase specs (`phase_specs/*.json`) - 19 machine-readable phase definitions

**Purpose:** Machine-readable contracts for AI orchestration

**Status:** ✅ Canonical reference, maintain as-is

---

#### Zone 3: OPERATIONAL SPECS (Active)
**Location:** `pipeline_plus/AGENT_OPERATIONS_SPEC version1.0.0`

**Subsystems:**
- `PROMPT_RENDERING_SPEC` - Template rendering, classification inference
- `TASK_ROUTING_SPEC` - Capability-based routing, circuit breakers
- `PATCH_MANAGEMENT_SPEC` - Patch validation, rollback, feature flags
- `COOPERATION_SPEC` - State machine, queue contract, worker behavior

**Status:** ✅ Active operational contract

---

#### Zone 4: REFERENCE & GUIDANCE (Reference - Risk of Confusion)
**Location:** `pipeline_plus/` and `pipeline_plus/AGENTIC_DEV_PROTOTYPE/`

**High-Value References:**
- `IMPLEMENTATION_SUMMARY.md` - Complete implementation summary
- `anthropic_prompt_engineering_guide.md` - Prompt engineering best practices
- `DEVELOPMENT RULES DO and DONT.md` - Anti-patterns and best practices

**Medium-Value References:**
- `Key Innovations for File Passing Between CLI Tools.md`
- `Aider-tuned WORKSTREAM_V1.md`
- Session reports (SESSION_1_FINAL_REPORT.md, etc.)

**Low-Value/Legacy:**
- `A Guide to High-Quality Prompts for Superior AI (1).txt` - External copy
- `The Core of a Good Prompt (1).txt` - Duplicate external resource
- `.txt` copies of external web content

**Status:** ⚠️ Needs classification and archival

---

#### Zone 5: LEGACY IMPLEMENTATIONS (Archive Candidates)
**Location:** Various duplicate/experimental implementations

**Candidates:**
- `fully-autonomous refactor runner.md` - Experimental concept
- `data and indirection refactor.md` - Exploratory notes
- `orchestration-scripts.md` - Pre-implementation notes
- `mods1.md`, `mods2.md` - Modification logs (pre-final)

**Status:** 🗄️ Archive to `_archive/exploration/`

---

## II. PROPOSED DIRECTORY STRUCTURE

### Clean Architecture-Aware Layout

```
pipeline_plus/
├── core/                                    # CORE PRODUCTION CODE
│   ├── engine/
│   │   ├── orchestrator/                    # Orchestration engine
│   │   │   ├── core.py
│   │   │   ├── state_machine.py
│   │   │   ├── dependency_resolver.py
│   │   │   └── parallel_executor.py
│   │   ├── validators/                      # Validation subsystem
│   │   │   ├── schema_validator.py
│   │   │   └── guard_rules_engine.py
│   │   ├── adapters/                        # Tool adapters (Hexagonal)
│   │   │   ├── base.py
│   │   │   ├── aider_adapter.py
│   │   │   ├── codex_adapter.py
│   │   │   └── claude_adapter.py
│   │   ├── patch_manager.py
│   │   ├── prompt_renderer.py
│   │   ├── task_queue.py
│   │   └── validation_gateway.py
│   ├── state/                               # State management
│   │   ├── .ledger/
│   │   ├── .tasks/
│   │   └── .runs/
│   └── schemas/                             # JSON schemas
│       └── generated/
│
├── specs/                                   # CANONICAL SPECIFICATIONS
│   ├── contracts/                           # Active contracts
│   │   ├── AGENT_OPERATIONS_SPEC_v1.0.0.md
│   │   ├── UNIVERSAL_PHASE_SPEC_V1.md
│   │   ├── PRO_PHASE_SPEC_V1.md
│   │   └── DEV_RULES_V1.md
│   ├── phase_definitions/                   # Machine-readable phases
│   │   └── *.json                           # 19 phase specs
│   └── metadata/
│       ├── ups_index.json
│       ├── pps_index.json
│       └── dr_index.json
│
├── docs/                                    # LIVING DOCUMENTATION
│   ├── architecture/
│   │   ├── ARCHITECTURE_OVERVIEW.md
│   │   ├── HEXAGONAL_PATTERN.md
│   │   └── COMPONENT_RESPONSIBILITIES.md
│   ├── implementation/
│   │   ├── IMPLEMENTATION_SUMMARY.md        # Keep as canonical record
│   │   ├── PHASE_0_EXECUTION_SUMMARY.md
│   │   └── MILESTONE_M1_SUMMARY.md
│   ├── guides/
│   │   ├── WORKSTREAM_AUTHORING.md
│   │   ├── PROMPT_ENGINEERING.md            # Consolidated from multiple sources
│   │   └── DEVELOPMENT_RULES.md
│   └── sessions/                            # Session reports
│       ├── SESSION_1_FINAL_REPORT.md
│       ├── SESSION_2_FINAL_REPORT.md
│       └── SESSION_3_FINAL_REPORT.md
│
├── reference/                               # STABLE REFERENCES
│   ├── prompt_engineering/
│   │   ├── anthropic_guide.md
│   │   ├── workstream_v1_patterns.md
│   │   └── classification_inference.md
│   ├── anti_patterns/
│   │   └── ANTI_PATTERN_FORENSICS.md
│   └── external/                            # Clearly marked external
│       ├── anthropic_prompt_guide.txt       # Tagged: External - Anthropic
│       └── prompt_fundamentals.txt          # Tagged: External
│
├── templates/                               # ACTIVE TEMPLATES
│   └── prompt_template.txt
│
├── tests/                                   # TEST SUITE
│   ├── test_orchestrator.py
│   ├── test_validators.py
│   ├── test_adapters.py
│   └── test_integration.py
│
├── scripts/                                 # OPERATIONAL SCRIPTS
│   ├── bootstrap.ps1
│   ├── validate_phase_spec.py
│   └── collect_development_metrics.py
│
├── analytics/                               # TELEMETRY & METRICS
│   ├── metrics/
│   ├── reports/
│   └── DATA_COLLECTION_SUMMARY.md
│
├── _archive/                                # ARCHIVED CONTENT
│   ├── exploration/                         # Exploratory work
│   │   ├── fully-autonomous_refactor_runner.md
│   │   ├── data_and_indirection_refactor.md
│   │   ├── orchestration_scripts_draft.md
│   │   └── _README_ARCHIVE.md               # Context: Why archived
│   ├── legacy_drafts/                       # Pre-v1 drafts
│   │   ├── mods1.md
│   │   ├── mods2.md
│   │   └── early_workstream_drafts/
│   └── duplicates/                          # Identified duplicates
│       └── _DUPLICATE_LOG.md                # Deduplication log
│
├── config/                                  # CONFIGURATION
│   ├── schema.json
│   └── validation_rules.json
│
├── README.md                                # PROJECT ENTRY POINT
├── IMPLEMENTATION_STATUS.md                 # Current status dashboard
└── ARCHITECTURE.md                          # High-level architecture

```

---

## III. MULTI-PHASE CLEANUP PLAN

### Phase 1: Inventory & Classification (4 hours)

**Priority:** 🔴 CRITICAL - Do first

**Objectives:**
1. Create master inventory with classification tags
2. Identify duplicate content across folders
3. Tag files by status: ACTIVE | REFERENCE | LEGACY | DUPLICATE | EXTERNAL

**Steps:**

```powershell
# Step 1.1: Generate file inventory with metadata
Get-ChildItem -Path "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus" -Recurse -File | 
  Select-Object FullName, Name, Length, LastWriteTime, Extension |
  Export-Csv -Path ".\file_inventory_raw.csv" -NoTypeInformation

# Step 1.2: Classify by pattern
# Tag files by naming patterns and content signatures
```

**Deliverables:**
- `INVENTORY_MASTER.csv` - Complete file listing with tags
- `DUPLICATION_REPORT.md` - Files with overlapping content
- `CLASSIFICATION_MATRIX.md` - Classification criteria used

**Tags Used:**
- `ACTIVE_CORE` - Production code in active use
- `ACTIVE_SPEC` - Canonical specification files
- `REFERENCE_HIGH` - High-value reference, occasionally consulted
- `REFERENCE_MED` - Medium-value, specific use cases
- `LEGACY_ARCHIVE` - Outdated but contains reusable logic
- `DUPLICATE` - Redundant copy of existing file
- `EXTERNAL_COPY` - Copied from external source (web, docs)

---

### Phase 2: Consolidation of Active Files (6 hours)

**Priority:** 🟠 HIGH - After inventory

**Objectives:**
1. Reorganize production code into clean architecture zones
2. Consolidate specifications into canonical `/specs` directory
3. Merge duplicate documentation

**Steps:**

**2.1 Core Production Code Migration**
```powershell
# Move from AGENTIC_DEV_PROTOTYPE/src to core/engine
New-Item -Path ".\core\engine\orchestrator" -ItemType Directory -Force
Move-Item ".\AGENTIC_DEV_PROTOTYPE\src\orchestrator\*" ".\core\engine\orchestrator\"
```

**2.2 Specifications Consolidation**
```powershell
# Consolidate all specs into single hierarchy
New-Item -Path ".\specs\contracts" -ItemType Directory -Force
Copy-Item ".\AGENT_OPERATIONS_SPEC version1.0.0" ".\specs\contracts\AGENT_OPERATIONS_SPEC_v1.0.0.md"
```

**2.3 Documentation Merge**
- Merge `anthropic_prompt_engineering_guide.md` + `Anthropic Prompt Guide...md` → `docs/guides/PROMPT_ENGINEERING.md`
- Consolidate session reports → `docs/sessions/`
- Tag all external copies clearly

**Deliverables:**
- Reorganized `/core`, `/specs`, `/docs` directories
- `CONSOLIDATION_LOG.md` - Record of moves and merges
- `MERGE_DECISIONS.md` - Which files merged and why

---

### Phase 3: Archival Strategy (3 hours)

**Priority:** 🟡 MEDIUM - After consolidation

**Objectives:**
1. Archive legacy exploration documents
2. Preserve historical context without polluting active workspace
3. Create clear archival metadata

**Steps:**

**3.1 Create Archive Structure**
```powershell
New-Item -Path ".\_archive\exploration" -ItemType Directory -Force
New-Item -Path ".\_archive\legacy_drafts" -ItemType Directory -Force
New-Item -Path ".\_archive\duplicates" -ItemType Directory -Force
```

**3.2 Archive with Context**
```powershell
# Move legacy files with README explaining why archived
Move-Item "fully-autonomous refactor runner.md" ".\_archive\exploration\"
```

**3.3 Create Archive Index**
Create `_archive/_README_ARCHIVE.md`:

```markdown
# Archive Directory - Context Preservation

## Purpose
This directory contains historical artifacts preserved for reference but not part of active development.

## Categories

### /exploration
Early-stage exploratory work, proof-of-concepts, experimental designs.
**Status:** Superseded by production implementation.
**Reuse Value:** Conceptual ideas may inform future work.

### /legacy_drafts
Pre-v1.0 drafts and modification logs.
**Status:** Obsolete - replaced by canonical specs.
**Reuse Value:** Low - historical record only.

### /duplicates
Duplicate copies of files retained elsewhere.
**Status:** Redundant.
**Reuse Value:** None - kept for audit trail.

## Archival Policy
- Files moved here are NOT indexed by AI tools.
- To reference archived content, cite specific file in active docs.
- Review annually; delete if zero citations after 2 years.
```

**Deliverables:**
- Populated `_archive/` with clear categorization
- `_README_ARCHIVE.md` - Archive policy and index
- `.aiexclude` or `.gitignore` patterns to exclude from AI context

---

### Phase 4: Removal of Redundant Materials (2 hours)

**Priority:** 🟢 LOW - Final cleanup

**Objectives:**
1. Delete confirmed duplicates after archival
2. Remove obsolete temporary files
3. Clean up naming inconsistencies

**Steps:**

**4.1 Delete Safe Targets**
- `.txt` external copies already consolidated into `/reference/external`
- `(1).txt` duplicates after deduplication
- Temporary files (if any)

**4.2 Rename for Clarity**
```powershell
# Remove special characters that cause path issues
Rename-Item "# ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC_V1.md" "ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC_V1.md"
```

**4.3 Update All Internal References**
- Update import paths in Python code
- Update relative links in Markdown docs
- Verify no broken links

**Deliverables:**
- `DELETION_LOG.md` - Record of all deleted files with SHA256 hashes
- `RENAME_LOG.md` - Old → New name mappings
- Updated README with new structure

---

## IV. AI USABILITY OPTIMIZATION

### Context Clarity Gates

**Goal:** Prevent AI tools from using outdated context during code generation.

#### Strategy 1: File Header Annotations

Add to all reference files:

```markdown
---
status: REFERENCE_ONLY | ARCHIVED | ACTIVE_SPEC
last_reviewed: 2025-11-20
superseded_by: [path/to/newer/file.md]  # If applicable
ai_context_priority: HIGH | MEDIUM | LOW | EXCLUDE
---
```

#### Strategy 2: Directory-Level `.aicontext` Files

Create `.aicontext` in each directory:

```yaml
# .aicontext - AI tool context hints
directory_purpose: "Core production orchestration engine"
ai_indexing: PRIORITY  # PRIORITY | STANDARD | LOW | EXCLUDE
context_scope: ACTIVE_CODE
review_frequency: monthly
```

#### Strategy 3: Explicit Exclusion Patterns

**For Aider:**
Create `.aiderignore`:
```
_archive/
reference/external/
*.txt
**/duplicates/
```

**For Codex:**
Codex respects `.gitignore` - add:
```gitignore
_archive/
reference/external/
```

**For Claude Code:**
Use `.claude_context.yaml`:
```yaml
exclude_patterns:
  - "_archive/**"
  - "reference/external/**"
  - "**/*.txt"
```

---

## V. MAINTENANCE BEST PRACTICES

### 1. Documentation Gates

**Rule:** Before committing new files to `/docs` or `/reference`:

✅ **Checklist:**
- [ ] File has clear purpose statement in first paragraph
- [ ] Status tag present (ACTIVE | REFERENCE | DRAFT)
- [ ] Supersession chain documented if replacing existing doc
- [ ] No duplicate content (checked via grep/search)
- [ ] Filename follows convention: `CATEGORY_SUBJECT_VERSION.md`

**Example:** `SPEC_PROMPT_RENDERING_V1.1.md`

---

### 2. Reference Tagging System

**Tag Format:** `[SOURCE:type:origin:date]`

**Examples:**
- `[SOURCE:EXTERNAL:Anthropic:2025-01]` - External source, Anthropic docs, Jan 2025
- `[SOURCE:INTERNAL:SESSION:2025-11-19]` - Internal session output
- `[SOURCE:LEGACY:v0.9:2025-10]` - Legacy version 0.9

**Usage in Docs:**
```markdown
## Prompt Engineering Principles

> [SOURCE:EXTERNAL:Anthropic:2025-01]
> The following guidelines are adapted from Anthropic's official documentation.

1. Be specific and clear...
```

---

### 3. Periodic Review Cycles

**Quarterly Review (Every 3 months):**
- Review `/reference` for outdated content
- Check for new duplicates
- Update status tags
- Archive files with zero citations

**Annual Review (Every 12 months):**
- Delete archived files with zero active references
- Consolidate similar reference materials
- Update architecture documentation
- Regenerate dependency graphs

---

### 4. Naming Conventions

**File Naming Standard:**

```
[CATEGORY]_[SUBJECT]_[VERSION].[ext]

Categories:
- SPEC_    : Specifications and contracts
- GUIDE_   : How-to guides and tutorials
- REF_     : Reference materials
- ARCH_    : Architecture documentation
- SESSION_ : Session reports
- IMPL_    : Implementation summaries
```

**Examples:**
- `SPEC_AGENT_OPERATIONS_V1.0.0.md`
- `GUIDE_WORKSTREAM_AUTHORING_V1.md`
- `REF_ANTHROPIC_PROMPTS_2025-01.md`
- `ARCH_HEXAGONAL_PATTERN.md`
- `SESSION_FINAL_REPORT_2025-11-19.md`

---

### 5. AI Context Priority System

**Priority Levels:**

| Level | Usage | Indexing | Examples |
|-------|-------|----------|----------|
| **P0 - CRITICAL** | Active specs and contracts | Always indexed | `AGENT_OPERATIONS_SPEC_v1.0.0.md` |
| **P1 - HIGH** | Production code | Always indexed | `core/engine/**/*.py` |
| **P2 - MEDIUM** | Current guides | Indexed on request | `docs/guides/*.md` |
| **P3 - LOW** | Reference material | Indexed explicitly only | `reference/**` |
| **P4 - EXCLUDE** | Archive/legacy | Never indexed | `_archive/**` |

**Implementation:**
Add to file frontmatter:
```markdown
---
ai_context_priority: P0
---
```

---

## VI. STEP-BY-STEP EXECUTION GUIDE

### Week 1: Inventory & Planning

**Day 1-2: Inventory**
```powershell
# Run inventory scripts
.\scripts\generate_inventory.ps1
.\scripts\identify_duplicates.ps1
```

**Day 3-4: Classification**
- Manual review of 50 key files
- Tag with status and priority
- Document classification decisions

**Day 5: Review & Approval**
- Review `INVENTORY_MASTER.csv`
- Approve archival candidates
- Identify merge candidates

---

### Week 2: Consolidation

**Day 1-2: Core Code Reorganization**
```powershell
# Execute consolidation script
.\scripts\reorganize_core.ps1 -DryRun
# Review changes
.\scripts\reorganize_core.ps1 -Execute
```

**Day 3-4: Specifications & Docs**
```powershell
.\scripts\consolidate_specs.ps1
.\scripts\merge_docs.ps1
```

**Day 5: Validation**
- Run all tests
- Verify import paths
- Check for broken links

---

### Week 3: Archival & Cleanup

**Day 1-2: Archive Migration**
```powershell
.\scripts\archive_legacy.ps1
# Create archive README
# Add exclusion patterns
```

**Day 3-4: Deletion & Renaming**
```powershell
.\scripts\safe_delete.ps1  # Logs SHA256 before delete
.\scripts\rename_normalize.ps1
```

**Day 5: Final Validation**
- AI context test (run sample prompts)
- Documentation review
- Update README and ARCHITECTURE.md

---

## VII. SUCCESS METRICS

### Quantitative Targets

| Metric | Before | Target | Method |
|--------|--------|--------|--------|
| Total files | ~250 | ~120 | Inventory script |
| Duplicate files | ~45 | 0 | Deduplication report |
| Avg file age (active) | Mixed | <30 days | File metadata |
| Broken links | Unknown | 0 | Link checker |
| AI context confusion rate | High | <5% | Test prompts |
| Directory depth | 7 levels | 4 levels | Tree analysis |

### Qualitative Goals

✅ **Clarity:** Any developer can understand directory purpose in <5 minutes  
✅ **AI Safety:** AI tools reference only current, relevant context  
✅ **Maintainability:** New files follow clear conventions  
✅ **Discoverability:** README provides complete navigation  

---

## VIII. ROLLBACK PLAN

**Before any destructive operations:**

```powershell
# 1. Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path ".\pipeline_plus" -Destination ".\pipeline_plus_BACKUP_$timestamp" -Recurse

# 2. Create restoration script
@"
# Rollback script generated: $timestamp
Remove-Item ".\pipeline_plus" -Recurse -Force
Rename-Item ".\pipeline_plus_BACKUP_$timestamp" "pipeline_plus"
"@ | Out-File ".\rollback_$timestamp.ps1"
```

**Restoration:**
```powershell
.\rollback_20251120_143022.ps1
```

---

## IX. ONGOING GOVERNANCE

### Change Control Board (CCB)

**For directory structure changes:**
1. Propose change in `meta/proposals/DIR_CHANGE_PROPOSAL_NNN.md`
2. Document impact analysis
3. Get approval before execution
4. Update this strategy doc

### Quarterly Health Check

**Automation:**
```powershell
# Run quarterly
.\scripts\directory_health_check.ps1
```

**Outputs:**
- Duplicate detection report
- Orphaned files (no inbound links)
- Outdated files (>6 months since edit)
- AI context pollution risk score

---

## X. APPENDIX: TOOLS & SCRIPTS

### A. Inventory Generator

**File:** `scripts/generate_inventory.ps1`

```powershell
# Generate comprehensive file inventory with classification
param(
    [string]$RootPath = ".\pipeline_plus",
    [string]$OutputCsv = ".\INVENTORY_MASTER.csv"
)

Get-ChildItem -Path $RootPath -Recurse -File |
    Select-Object @{N='Path';E={$_.FullName}}, 
                  @{N='Name';E={$_.Name}},
                  @{N='Size';E={$_.Length}},
                  @{N='Modified';E={$_.LastWriteTime}},
                  @{N='Extension';E={$_.Extension}},
                  @{N='Category';E={
                      if ($_.DirectoryName -like "*\src\*") {"ACTIVE_CORE"}
                      elseif ($_.DirectoryName -like "*\specs\*") {"ACTIVE_SPEC"}
                      elseif ($_.Name -like "*.txt") {"EXTERNAL_COPY"}
                      else {"UNCLASSIFIED"}
                  }} |
    Export-Csv -Path $OutputCsv -NoTypeInformation

Write-Host "Inventory generated: $OutputCsv"
```

---

### B. Duplicate Detector

**File:** `scripts/identify_duplicates.ps1`

```powershell
# Find duplicate files by content hash
param(
    [string]$RootPath = ".\pipeline_plus",
    [string]$OutputFile = ".\DUPLICATION_REPORT.md"
)

$hashes = @{}
$duplicates = @()

Get-ChildItem -Path $RootPath -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    
    if ($hashes.ContainsKey($hash)) {
        $duplicates += [PSCustomObject]@{
            Hash = $hash
            Original = $hashes[$hash]
            Duplicate = $_.FullName
        }
    } else {
        $hashes[$hash] = $_.FullName
    }
}

$duplicates | ConvertTo-Markdown | Out-File $OutputFile
Write-Host "Found $($duplicates.Count) duplicates. Report: $OutputFile"
```

---

### C. Link Validator

**File:** `scripts/validate_links.ps1`

```powershell
# Check for broken internal links in Markdown files
param(
    [string]$RootPath = ".\pipeline_plus"
)

$brokenLinks = @()

Get-ChildItem -Path $RootPath -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $links = [regex]::Matches($content, '\[.*?\]\((.*?)\)')
    
    foreach ($link in $links) {
        $target = $link.Groups[1].Value
        if ($target -notmatch '^http' -and $target -notmatch '^#') {
            $fullPath = Join-Path (Split-Path $_.FullName) $target
            if (-not (Test-Path $fullPath)) {
                $brokenLinks += [PSCustomObject]@{
                    File = $_.FullName
                    BrokenLink = $target
                }
            }
        }
    }
}

$brokenLinks | Format-Table -AutoSize
```

---

## XI. MIGRATION CHECKLIST

### Pre-Migration

- [ ] Create complete backup
- [ ] Run inventory script
- [ ] Review classification results
- [ ] Get stakeholder approval
- [ ] Document current state (screenshots, tree output)

### During Migration

- [ ] Phase 1: Inventory complete
- [ ] Phase 2: Core code reorganized
- [ ] Phase 2: Specs consolidated
- [ ] Phase 2: Docs merged
- [ ] Phase 3: Legacy archived
- [ ] Phase 4: Duplicates removed
- [ ] Phase 4: Files renamed

### Post-Migration Validation

- [ ] All tests pass
- [ ] No broken import statements
- [ ] No broken documentation links
- [ ] AI context test: Run 10 sample prompts
- [ ] README updated
- [ ] ARCHITECTURE.md updated
- [ ] Team walkthrough completed

### Ongoing

- [ ] Add to quarterly review calendar
- [ ] Update contribution guidelines
- [ ] Train team on new structure
- [ ] Monitor AI tool behavior for 2 weeks

---

## XII. CONTACT & GOVERNANCE

**Strategy Owner:** AI Systems Architect  
**Last Updated:** 2025-11-20  
**Next Review:** 2026-02-20 (Quarterly)  
**Version:** 1.0

**Approval Required For:**
- Directory structure changes
- Archival of active files
- Deletion of any `.py` or `.json` files
- Changes to core specifications

**Emergency Rollback Contact:** Execute `rollback_[timestamp].ps1`

---

**END OF STRATEGY DOCUMENT**
