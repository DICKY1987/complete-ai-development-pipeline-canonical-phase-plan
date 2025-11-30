---
doc_id: DOC-GUIDE-PROPOSED-DIRECTORY-TREE-1250
---

# Proposed Directory Structure - Visual Reference

**Project:** Pipeline Plus AI Development System  
**Date:** 2025-11-20  
**Status:** PROPOSAL (Execute after inventory phase)

---

## 🎯 Design Philosophy

**Key Principles:**
1. **Hexagonal Architecture** - Core domain isolated from adapters
2. **Context Clarity** - AI tools see only relevant files
3. **4-Layer Maximum** - Prevent deep nesting
4. **Clear Separation** - Code / Specs / Docs / Reference / Archive

---

## 📂 Complete Directory Tree

```
pipeline_plus/
│
├── 📁 core/                                    # PRODUCTION CODE (P1)
│   ├── engine/                                 # Orchestration engine
│   │   ├── orchestrator/                       # Core orchestration logic
│   │   │   ├── core.py                         # Main orchestrator
│   │   │   ├── state_machine.py                # State transitions
│   │   │   ├── dependency_resolver.py          # Dependency graph
│   │   │   ├── parallel_executor.py            # Parallel execution
│   │   │   └── __init__.py
│   │   │
│   │   ├── validators/                         # Validation subsystem
│   │   │   ├── schema_validator.py             # JSON schema validation
│   │   │   ├── guard_rules_engine.py           # Guard rules
│   │   │   └── __init__.py
│   │   │
│   │   ├── adapters/                           # Tool adapters (Ports)
│   │   │   ├── base.py                         # Abstract base adapter
│   │   │   ├── aider_adapter.py                # Aider integration
│   │   │   ├── codex_adapter.py                # Codex CLI integration
│   │   │   ├── claude_adapter.py               # Claude Code integration
│   │   │   └── __init__.py
│   │   │
│   │   ├── patch_manager.py                    # Patch lifecycle manager
│   │   ├── prompt_renderer.py                  # WORKSTREAM_V1.1 renderer
│   │   ├── task_queue.py                       # Priority FIFO queue
│   │   ├── validation_gateway.py               # 3-layer validation
│   │   ├── schema_generator.py                 # Schema generation
│   │   ├── spec_renderer.py                    # Spec rendering
│   │   └── spec_resolver.py                    # Spec resolution
│   │
│   ├── state/                                  # State management
│   │   ├── .ledger/                            # Execution ledger
│   │   │   ├── PH-00.json
│   │   │   ├── PH-1A.json
│   │   │   └── ...
│   │   ├── .tasks/                             # Task queue storage
│   │   │   ├── queued/
│   │   │   ├── running/
│   │   │   ├── complete/
│   │   │   └── failed/
│   │   ├── .runs/                              # Execution runs
│   │   └── .patch_backups/                     # Patch backups
│   │
│   └── schemas/                                # JSON Schemas
│       ├── generated/
│       │   ├── phase_spec.schema.json
│       │   ├── validation_rules.schema.json
│       │   └── workstream.schema.json
│       └── README.md
│
├── 📁 specs/                                   # CANONICAL SPECS (P0)
│   ├── contracts/                              # Active contracts
│   │   ├── AGENT_OPERATIONS_SPEC_V1.0.0.md     # Agent operations contract
│   │   ├── UNIVERSAL_PHASE_SPEC_V1.md          # Universal phase spec
│   │   ├── PRO_PHASE_SPEC_V1.md                # Professional phase spec
│   │   ├── DEV_RULES_V1.md                     # Development rules
│   │   ├── PROMPT_RENDERING_SPEC.md            # Prompt rendering contract
│   │   ├── TASK_ROUTING_SPEC.md                # Task routing contract
│   │   ├── PATCH_MANAGEMENT_SPEC.md            # Patch management contract
│   │   └── COOPERATION_SPEC.md                 # Multi-agent cooperation
│   │
│   ├── phase_definitions/                      # Machine-readable phases
│   │   ├── phase_0_bootstrap.json
│   │   ├── phase_1a_universal_spec.json
│   │   ├── phase_1b_pro_spec.json
│   │   ├── phase_1c_dev_rules.json
│   │   ├── phase_1d_cross_reference.json
│   │   ├── phase_1e_schema_generator.json
│   │   ├── phase_1f_spec_renderer.json
│   │   ├── phase_2a_schema_validator.json
│   │   ├── phase_2b_guard_rules.json
│   │   ├── phase_2c_validation_gateway.json
│   │   ├── phase_3a_prompt_renderer.json
│   │   ├── phase_3b_orchestrator_core.json
│   │   ├── phase_3c_dependency_executor.json
│   │   ├── phase_4a_patch_manager.json
│   │   ├── phase_4b_task_queue.json
│   │   ├── phase_5a_aider_adapter.json
│   │   ├── phase_5b_codex_adapter.json
│   │   ├── phase_5c_claude_adapter.json
│   │   ├── phase_6a_integration_tests.json
│   │   ├── phase_6b_cli_scripts.json
│   │   └── phase_6c_documentation.json
│   │
│   ├── metadata/                               # Spec indices
│   │   ├── ups_index.json                      # UPS index
│   │   ├── pps_index.json                      # PPS index
│   │   └── dr_index.json                       # Dev rules index
│   │
│   └── README.md                               # Spec catalog
│
├── 📁 docs/                                    # LIVING DOCUMENTATION (P2)
│   ├── architecture/                           # Architecture docs
│   │   ├── ARCHITECTURE_OVERVIEW.md            # High-level architecture
│   │   ├── HEXAGONAL_PATTERN.md                # Hexagonal architecture
│   │   ├── COMPONENT_RESPONSIBILITIES.md       # Component contracts
│   │   ├── DATA_FLOW.md                        # Data flow diagrams
│   │   └── BOUNDED_CONTEXTS.md                 # Domain boundaries
│   │
│   ├── implementation/                         # Implementation records
│   │   ├── IMPLEMENTATION_SUMMARY.md           # Complete summary
│   │   ├── PHASE_0_EXECUTION_SUMMARY.md        # Phase 0 record
│   │   ├── MILESTONE_M1_SUMMARY.md             # Milestone 1
│   │   ├── MILESTONE_M2_SUMMARY.md             # Milestone 2
│   │   └── ...
│   │
│   ├── guides/                                 # How-to guides
│   │   ├── GUIDE_WORKSTREAM_AUTHORING.md       # Writing workstreams
│   │   ├── GUIDE_PROMPT_ENGINEERING.md         # Prompt engineering
│   │   ├── GUIDE_PHASE_EXECUTION.md            # Executing phases
│   │   ├── GUIDE_TESTING.md                    # Testing guide
│   │   └── GUIDE_DEVELOPMENT_WORKFLOW.md       # Dev workflow
│   │
│   ├── sessions/                               # Session reports
│   │   ├── SESSION_1_FINAL_REPORT.md
│   │   ├── SESSION_2_FINAL_REPORT.md
│   │   ├── SESSION_3_FINAL_REPORT.md
│   │   └── SESSION_INDEX.md                    # Session index
│   │
│   └── api/                                    # API documentation
│       ├── orchestrator_api.md
│       ├── adapter_api.md
│       └── validator_api.md
│
├── 📁 reference/                               # STABLE REFERENCES (P3)
│   ├── prompt_engineering/                     # Prompt patterns
│   │   ├── REF_ANTHROPIC_GUIDE.md              # Anthropic best practices
│   │   ├── REF_WORKSTREAM_V1_PATTERNS.md       # Workstream patterns
│   │   ├── REF_CLASSIFICATION_INFERENCE.md     # Classification logic
│   │   └── REF_CHAIN_OF_THOUGHT.md             # CoT patterns
│   │
│   ├── anti_patterns/                          # Anti-patterns
│   │   ├── ANTI_PATTERN_FORENSICS.md           # Known anti-patterns
│   │   └── LESSONS_LEARNED.md                  # Lessons learned
│   │
│   ├── tools/                                  # Tool-specific refs
│   │   ├── REF_AIDER_BEST_PRACTICES.md
│   │   ├── REF_CODEX_PATTERNS.md
│   │   └── REF_CLAUDE_CODE_USAGE.md
│   │
│   └── external/                               # External resources
│       ├── _EXTERNAL_SOURCES.md                # Source index
│       ├── anthropic_prompts_2025-01.md        # Tagged: External
│       ├── openai_best_practices_2025-01.md    # Tagged: External
│       └── README.md                           # Usage guidelines
│
├── 📁 templates/                               # ACTIVE TEMPLATES (P1)
│   ├── prompts/
│   │   ├── workstream_v1.1_universal.txt.j2
│   │   ├── workstream_v1.1_aider.txt.j2
│   │   └── workstream_v1.1_codex.txt.j2
│   ├── phase_spec_template.json
│   └── session_report_template.md
│
├── 📁 tests/                                   # TEST SUITE (P1)
│   ├── unit/
│   │   ├── test_orchestrator.py
│   │   ├── test_state_machine.py
│   │   ├── test_validators.py
│   │   ├── test_adapters.py
│   │   ├── test_patch_manager.py
│   │   ├── test_prompt_renderer.py
│   │   └── test_task_queue.py
│   │
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   ├── test_phase_execution.py
│   │   └── test_multi_tool.py
│   │
│   ├── fixtures/
│   │   ├── sample_phase_spec.json
│   │   ├── sample_workstream.json
│   │   └── mock_adapters.py
│   │
│   └── conftest.py
│
├── 📁 scripts/                                 # OPERATIONAL SCRIPTS (P1)
│   ├── bootstrap.ps1                           # Initial setup
│   ├── validate_phase_spec.py                  # Spec validation
│   ├── collect_development_metrics.py          # Metrics collection
│   ├── generate_inventory.ps1                  # File inventory
│   ├── identify_duplicates.ps1                 # Duplicate detection
│   ├── validate_links.ps1                      # Link validation
│   ├── directory_health_check.ps1              # Health check
│   └── reorganize_structure.ps1                # Migration script
│
├── 📁 analytics/                               # TELEMETRY (P2)
│   ├── metrics/
│   │   ├── latest_metrics.json
│   │   └── metrics_YYYYMMDD_HHMMSS.json
│   │
│   ├── reports/
│   │   └── METRICS_SUMMARY_YYYYMMDD.md
│   │
│   ├── raw_data/
│   │   ├── git_logs/
│   │   ├── terminal_transcripts/
│   │   └── test_outputs/
│   │
│   ├── snapshots/
│   │   └── YYYY-MM-DD/
│   │
│   ├── visualizations/
│   │
│   └── DATA_COLLECTION_SUMMARY.md
│
├── 📁 config/                                  # CONFIGURATION (P1)
│   ├── schema.json                             # Core schema
│   ├── validation_rules.json                   # Validation rules
│   ├── router.config.yaml                      # Router config
│   ├── adapters.config.yaml                    # Adapter configs
│   └── .aicontext                              # AI context hints
│
├── 📁 cli/                                     # CLI INTERFACE (P1)
│   └── commands/
│       ├── execute_phase.py
│       ├── validate_spec.py
│       └── render_prompt.py
│
├── 📁 examples/                                # USAGE EXAMPLES (P2)
│   ├── simple_phase/
│   │   ├── phase_spec.json
│   │   └── README.md
│   ├── complex_workstream/
│   │   ├── workstream_bundle.json
│   │   └── README.md
│   └── multi_tool_coordination/
│       ├── example.json
│       └── README.md
│
├── 📁 _archive/                                # ARCHIVED CONTENT (P4 - EXCLUDED)
│   ├── exploration/                            # Early explorations
│   │   ├── fully_autonomous_refactor_runner.md
│   │   ├── data_and_indirection_refactor.md
│   │   ├── orchestration_scripts_draft.md
│   │   └── _README_ARCHIVE.md                  # Archive context
│   │
│   ├── legacy_drafts/                          # Pre-v1 drafts
│   │   ├── mods1.md
│   │   ├── mods2.md
│   │   ├── early_workstream_v0.9/
│   │   └── _README_LEGACY.md
│   │
│   ├── duplicates/                             # Deduped files
│   │   └── _DUPLICATE_LOG.md                   # Dedup record
│   │
│   └── sessions_historical/                    # Old session reports
│       └── 2024/
│
├── 📄 README.md                                # PROJECT ENTRY POINT
├── 📄 ARCHITECTURE.md                          # Architecture overview
├── 📄 IMPLEMENTATION_STATUS.md                 # Current status
├── 📄 CHANGELOG.md                             # Version history
├── 📄 CONTRIBUTING.md                          # Contribution guide
├── 📄 LICENSE                                  # License
│
├── 📄 .gitignore                               # Git ignore patterns
├── 📄 .aiderignore                             # Aider exclusions
├── 📄 .aicontext                               # AI context config
├── 📄 master_phase_plan.json                   # Master plan
│
└── 📄 requirements.txt                         # Python dependencies

```

---

## 🎨 Color Coding Legend

| Icon | Purpose | AI Priority | Examples |
|------|---------|-------------|----------|
| 📁 | Directory | - | All folders |
| 📄 | File | Varies | README, specs |
| 🔴 | Critical (P0) | Always indexed | Specs, contracts |
| 🟠 | High (P1) | Always indexed | Core code, tests |
| 🟡 | Medium (P2) | Index on request | Docs, guides |
| 🔵 | Low (P3) | Explicit only | References |
| ⚫ | Excluded (P4) | Never indexed | Archives |

---

## 📊 Directory Statistics (Post-Cleanup Target)

| Category | Count | Total Size | Avg File Age |
|----------|-------|------------|--------------|
| Core Code | ~25 files | ~500 KB | <30 days |
| Specs | ~30 files | ~2 MB | <60 days |
| Docs | ~35 files | ~3 MB | <90 days |
| Reference | ~15 files | ~1 MB | Stable |
| Tests | ~20 files | ~400 KB | <30 days |
| Scripts | ~10 files | ~100 KB | <90 days |
| Templates | ~5 files | ~50 KB | Stable |
| Archive | ~45 files | ~5 MB | >180 days |
| **TOTAL** | **~185** | **~12 MB** | - |

**Reduction:** ~65 files removed (duplicates, externals, obsolete)

---

## 🔀 Migration Mapping

### Key Moves (Examples)

```
BEFORE → AFTER

AGENTIC_DEV_PROTOTYPE/src/orchestrator/core.py
  → core/engine/orchestrator/core.py

AGENT_OPERATIONS_SPEC version1.0.0
  → specs/contracts/AGENT_OPERATIONS_SPEC_V1.0.0.md

anthropic_prompt_engineering_guide.md
  → reference/prompt_engineering/REF_ANTHROPIC_GUIDE.md

A Guide to High-Quality Prompts for Superior AI (1).txt
  → reference/external/anthropic_prompts_2025-01.md  [Tagged: External]

fully-autonomous refactor runner.md
  → _archive/exploration/fully_autonomous_refactor_runner.md

The Core of a Good Prompt (1).txt
  → [DELETED - Duplicate of reference/external/anthropic_prompts_2025-01.md]

mods1.md, mods2.md
  → _archive/legacy_drafts/
```

---

## 🎯 Context Optimization

### AI Indexing Configuration

**Create `.aicontext` in each directory:**

```yaml
# core/.aicontext
directory_purpose: "Production orchestration engine"
ai_indexing: PRIORITY
context_scope: ACTIVE_CODE
exclude_subdirs: []
```

```yaml
# _archive/.aicontext
directory_purpose: "Historical artifacts - DO NOT USE IN ACTIVE DEVELOPMENT"
ai_indexing: EXCLUDE
context_scope: ARCHIVE
exclude_subdirs: ["*"]  # Exclude all
```

---

## 🚀 Migration Execution Order

### Phase 1: Prepare
1. Create new directory structure (empty folders)
2. Create `.aicontext` files in each directory
3. Create `_archive/_README_ARCHIVE.md`

### Phase 2: Move Production Code
1. Move `core/engine/` contents
2. Move `core/state/` contents
3. Update import paths in Python files
4. Run tests to verify

### Phase 3: Reorganize Specs
1. Move specs to `specs/contracts/`
2. Move phase definitions to `specs/phase_definitions/`
3. Update references in docs

### Phase 4: Consolidate Docs
1. Move implementation summaries to `docs/implementation/`
2. Move guides to `docs/guides/`
3. Move session reports to `docs/sessions/`
4. Merge duplicate content

### Phase 5: Archive Legacy
1. Move exploration docs to `_archive/exploration/`
2. Move legacy drafts to `_archive/legacy_drafts/`
3. Create archive READMEs

### Phase 6: Final Cleanup
1. Delete confirmed duplicates
2. Rename files to follow conventions
3. Validate all links
4. Update root README

---

## ✅ Validation Checklist

After migration:

- [ ] All tests pass
- [ ] No broken imports in Python code
- [ ] No broken links in Markdown files
- [ ] All files have frontmatter (where applicable)
- [ ] `.aicontext` files in all directories
- [ ] Archive has exclusion patterns
- [ ] README reflects new structure
- [ ] ARCHITECTURE.md updated

---

## 📞 Quick Navigation Guide

**"Where do I find...?"**

| Looking for... | Go to... |
|---------------|----------|
| Production code | `/core/engine/` |
| Active specifications | `/specs/contracts/` |
| Phase definitions | `/specs/phase_definitions/` |
| Architecture docs | `/docs/architecture/` |
| Implementation history | `/docs/implementation/` |
| How-to guides | `/docs/guides/` |
| Reference patterns | `/reference/prompt_engineering/` |
| External resources | `/reference/external/` |
| Test suite | `/tests/` |
| Operational scripts | `/scripts/` |
| Historical artifacts | `/_archive/` (but don't use for new work) |

---

## 🔗 Related Documents

- [Full Cleanup Strategy](../CLEANUP_REORGANIZATION_STRATEGY.md)
- [AI Dev Hygiene Guidelines](../AI_DEV_HYGIENE_GUIDELINES.md)
- [Architecture Overview](./docs/architecture/ARCHITECTURE_OVERVIEW.md)

---

**Last Updated:** 2025-11-20  
**Version:** 1.0  
**Status:** PROPOSAL - Execute after Phase 1 inventory

---

**END OF DIRECTORY TREE PROPOSAL**
