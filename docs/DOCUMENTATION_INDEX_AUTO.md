# Documentation Index

**Last Updated**: 2025-11-22  
**Purpose**: Central navigation hub for all pipeline documentation  
**Auto-Generated**: By `scripts/generate_doc_index.py`

> **Quick Links**: [Architecture](#architecture--design) | [Implementation](#implementation-summaries) | [Configuration](#configuration-guides) | [Integrations](#integrations) | [Development](#development-guides)

---

## 📋 Quick Reference

### Common Tasks

| Task | Documentation | Quick Command |
|------|--------------|---------------|
| **Get Started** | [README.md](../README.md) | `pwsh ./scripts/bootstrap.ps1` |
| **Navigate Repository** | [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) | - |
| **Coding Guidelines** | [AGENTS.md](../AGENTS.md) | - |
| **Run Tests** | [scripts/test.ps1](../scripts/test.ps1) | `pwsh ./scripts/test.ps1` |
| **Validate Workstreams** | [scripts/validate_workstreams.py](../scripts/validate_workstreams.py) | `python scripts/validate_workstreams.py` |
| **Find Implementation** | [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md) | - |

### Term Lookup

For specialized term definitions and implementation locations, see:
- **[IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md)** - Every term mapped to file:line
- **[TERM_RELATIONSHIPS.md](TERM_RELATIONSHIPS.md)** (planned K-4) - Term hierarchy and dependencies

---

## Architecture & Design

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Database operations, state persistence, bundle management |
| [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) | Shows the physical organization of the repository after the Phase E refactor. |
| [file-lifecycle-diagram.md](file-lifecycle-diagram.md) | This diagram mirrors the file lifecycle states defined in `core/ui_models.py` and summarizes the ... |
| [FILE_ORGANIZATION_VISUAL.md](FILE_ORGANIZATION_VISUAL.md) | Visual diagrams showing the file organization system |
| [HYBRID_WORKFLOW.md](HYBRID_WORKFLOW.md) | This document describes the integrated workflow combining OpenSpec specification management with ... |
| [prr_project_instructions_architecture_aware_prompting_code_generation.md](prompting/prr_project_instructions_architecture_aware_prompting_code_generation.md) | **Purpose.** Provide a single, machine‑readable set of instructions that every AI task follows to... |
| [state_machine.md](state_machine.md) | This document describes the canonical states and transitions for runs and workstreams in the AI d... |

---

## Implementation Summaries

| Document | Purpose |
|----------|---------|
| [AIM_INTEGRATION_STATUS.md](AIM_INTEGRATION_STATUS.md) | **Date:** 2025-11-22   **Status:** 98% COMPLETE ✅   **Recommendation:** Archive AI_MANGER and AUX... |
| [AIM_PLUS_FINAL_REPORT.md](AIM_PLUS_FINAL_REPORT.md) | **Project**: AIM+ (AI Manager Plus)   **Status**: ✅ COMPLETE & PRODUCTION READY   **Completion Da... |
| [AIM_PLUS_FINAL_SUMMARY.md](AIM_PLUS_FINAL_SUMMARY.md) | **Date**: 2025-11-22   **Status**: ✅ **PRODUCTION READY**   **Total Time**: ~13 hours vs 100 hour... |
| [AIM_PLUS_PHASE_1AB_COMPLETE.md](AIM_PLUS_PHASE_1AB_COMPLETE.md) | **Date**: 2025-11-21   **Phase**: 1A (Project Structure) + 1B (Secrets Management)   **Status**: ... |
| [AIM_PLUS_PHASE_1C_COMPLETE.md](AIM_PLUS_PHASE_1C_COMPLETE.md) | **Date**: 2025-11-21   **Phase**: 1C (Configuration Merge)   **Status**: ✅ COMPLETE   **Time**: ~... |
| [AIM_PLUS_PHASE_2A_COMPLETE.md](AIM_PLUS_PHASE_2A_COMPLETE.md) | **Date**: 2025-11-21   **Phase**: 2A (Health Check System)   **Status**: ✅ COMPLETE   **Time**: ~... |
| [AIM_PLUS_PHASE_2B_COMPLETE.md](AIM_PLUS_PHASE_2B_COMPLETE.md) | **Phase**: 2B - Tool Installer   **Status**: ✅ COMPLETE   **Date**: 2025-11-21   **Time Investmen... |
| [AIM_PLUS_PHASE_3A_COMPLETE.md](AIM_PLUS_PHASE_3A_COMPLETE.md) | **Phase**: 3A - Environment Scanner   **Status**: ✅ COMPLETE   **Date**: 2025-11-21   **Time Inve... |
| [AIM_PLUS_PHASE_3B_COMPLETE.md](AIM_PLUS_PHASE_3B_COMPLETE.md) | **Phase**: 3B - Version Control   **Status**: ✅ COMPLETE   **Date**: 2025-11-21   **Time Investme... |
| [AIM_PLUS_PHASE_4_COMPLETE.md](AIM_PLUS_PHASE_4_COMPLETE.md) | **Phase**: 4 - Integration & Polish   **Status**: ✅ COMPLETE   **Date**: 2025-11-21   **Time Inve... |
| [AIM_PLUS_PROGRESS_SUMMARY.md](AIM_PLUS_PROGRESS_SUMMARY.md) | **Updated**: 2025-11-21   **Current Phase**: 2B Complete   **Next Phase**: 3A - Scanner |
| [COMPLETE_IMPLEMENTATION_SUMMARY.md](COMPLETE_IMPLEMENTATION_SUMMARY.md) | **Implementation Date**: 2025-11-17   **Status**: ✅ COMPLETE   **Total Files Created**: 45 |
| [ENGINE_IMPLEMENTATION_SUMMARY.md](ENGINE_IMPLEMENTATION_SUMMARY.md) | This implementation establishes the **hybrid GUI/Terminal/TUI architecture** foundation for the A... |
| [ENGINE_STATUS.md](ENGINE_STATUS.md) | **Date**: 2025-11-21   **Phase**: 2B - Additional Adapters Complete ✅ |
| [FILE_ORGANIZATION_IMPLEMENTATION_SUMMARY.md](FILE_ORGANIZATION_IMPLEMENTATION_SUMMARY.md) | > **Created**: 2025-11-22   > **Status**: Ready for Implementation   > **Priority**: High - Found... |
| [IMPLEMENTATION_SUMMARY_UI_TOOL_SELECTION.md](IMPLEMENTATION_SUMMARY_UI_TOOL_SELECTION.md) | > "The cli apps and other tools are supposed to run headless but one needs run normally as the pl... |
| [UET_IMPLEMENTATION_COMPLETE.md](UET_IMPLEMENTATION_COMPLETE.md) | **Date**: 2025-11-21   **Status**: ✅ COMPLETE   **Implementation Time**: Single Session   **Git C... |
| [UET_PROGRESS_TRACKER.md](UET_PROGRESS_TRACKER.md) | **Last Updated**: 2025-11-22   **Current Phase**: Week 1 - Foundation   **Overall Status**: 🟡 Not... |
| [UI_IMPLEMENTATION_SUMMARY.md](UI_IMPLEMENTATION_SUMMARY.md) | This implementation provides a complete foundation for building TUI/GUI frontends on top of the A... |

---

## Configuration Guides

| Document | Purpose |
|----------|---------|
| [aider_contract.md](aider_contract.md) | This document specifies how the pipeline integrates with the Aider CLI for EDIT and FIX steps. |
| [AIM_INTEGRATION_CONTRACT.md](AIM_docs/AIM_INTEGRATION_CONTRACT.md) | ** Override default AIM registry location |
| [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) | Project-wide defaults shared by all developers |
| [COORDINATION_GUIDE.md](COORDINATION_GUIDE.md) | This guide explains how Claude Code, Codex CLI, Aider, and other AI coding assistants can coordin... |
| [first place (per-tool headless contract.md](reference/first place (per-tool headless contract.md) | - |
| [SPEC_MANAGEMENT_CONTRACT.md](SPEC_MANAGEMENT_CONTRACT.md) | This document defines the contract for multi‑document versioning and specification management in ... |
| [workstream_authoring_guide.md](workstream_authoring_guide.md) | This guide explains how to author `workstreams/*.json` files, which define discrete units of work... |

---

## Integrations

| Document | Purpose |
|----------|---------|
| [AIM_CAPABILITIES_CATALOG.md](AIM_docs/AIM_CAPABILITIES_CATALOG.md) | ** |
| [AIM_PLUS_INTEGRATION_PLAN.md](AIM_PLUS_INTEGRATION_PLAN.md) | **Status**: Planning   **Priority**: High   **Estimated Duration**: 4 weeks (80-100 hours)   **Cr... |
| [ccpm-github-setup.md](Project_Management_docs/ccpm-github-setup.md) | If these fail, re-run `gh auth login` and confirm the selected repo has issue permissions. |
| [ccpm-openspec-workflow.md](Project_Management_docs/ccpm-openspec-workflow.md) | ** Summarize verbose error reports (80-90% reduction) |
| [ccpm-phase-09-test-plan.md](Project_Management_docs/ccpm-phase-09-test-plan.md) | This document lists existing tests and proposed tests to validate the CCPM integration (install/w... |
| [codex-phase-09-13-evaluation.md](Project_Management_docs/codex-phase-09-13-evaluation.md) | move completed changes |
| [openspec_bridge.md](Project_Management_docs/openspec_bridge.md) | The OpenSpec Bridge connects OpenSpec specification management with the pipeline's workstream exe... |
| [phase-08-completion-summary.md](Project_Management_docs/phase-08-completion-summary.md) | **Date Completed:** 2025-11-16 **Status:** ✅ COMPLETED **Test Results:** 10/10 passing |
| [PHASE-09-2-COMPLETE.md](Project_Management_docs/PHASE-09-2-COMPLETE.md) | **Date:** 2025-11-21 **Status:** ✅ Complete |
| [PHASE-09-3-COMPLETE.md](Project_Management_docs/PHASE-09-3-COMPLETE.md) | **Date:** 2025-11-21   **Status:** ✅ Complete |
| [PHASE-09-CCPM-INTEGRATION-PLAN.md](Project_Management_docs/PHASE-09-CCPM-INTEGRATION-PLAN.md) | **Status:** Draft   **Created:** 2025-11-21   **Last Updated:** 2025-11-21   **Version:** 1.0 |
| [phase-09-ccpm-optimization.md](Project_Management_docs/phase-09-ccpm-optimization.md) | - |
| [PHASE-09-EXISTING-ANALYSIS.md](Project_Management_docs/PHASE-09-EXISTING-ANALYSIS.md) | ** Inventory existing CCPM assets and identify gaps for native implementation |
| [phase-openspec-integration.md](Project_Management_docs/phase-openspec-integration.md) | Phases are small, independently shippable, and keep behavior deterministic. |
| [QUICKSTART_OPENSPEC.md](Project_Management_docs/QUICKSTART_OPENSPEC.md) | Use Claude Code to create an OpenSpec proposal: |
| [tests-openspec-checklist.md](Project_Management_docs/tests-openspec-checklist.md) | This checklist enumerates existing tests and proposed tests to ensure the OpenSpec → Bundle → Wor... |
| [UET_DEVELOPMENT RULES DO and DONT.md](guidelines/UET_DEVELOPMENT RULES DO and DONT.md) | - |
| [UET_INDEX.md](UET_INDEX.md) | **Universal Execution Templates Integration**   **Version**: 1.0   **Last Updated**: 2025-11-21 |
| [UET_INTEGRATION_DESIGN.md](UET_INTEGRATION_DESIGN.md) | **Status**: Active Implementation   **Decision**: Option A - Selective Integration   **Timeline**... |
| [UET_INTEGRATION_PLAN.md](UET_INTEGRATION_PLAN.md) | **Created**: 2025-11-21   **Status**: Draft   **Target**: Phase H (Post Phase G)   **Estimated Du... |
| [UET_INTEGRATION_SUMMARY.md](UET_INTEGRATION_SUMMARY.md) | **Date**: 2025-11-22   **Decision**: Option A - Selective Integration   **Status**: Ready to impl... |
| [UET_QUICK_REFERENCE.md](UET_QUICK_REFERENCE.md) | **Last Updated**: 2025-11-22   **Integration Status**: Phase 1 - Foundation (Week 1)   **Risk Lev... |
| [UET_WEEK1_IMPLEMENTATION.md](UET_WEEK1_IMPLEMENTATION.md) | Add UET framework tables (workers, events, cost_tracking) |

---

## Development Guides

| Document | Purpose |
|----------|---------|
| [ENGINE_QUICK_REFERENCE.md](ENGINE_QUICK_REFERENCE.md) | job_dict = {     "job_id": "job-001",     "run_id": run_id,     "workstream_id": "ws-my-feature",... |
| [GUI_DEVELOPMENT_GUIDE.md](GUI_DEVELOPMENT_GUIDE.md) | This guide shows how to proceed with implementing the GUI layer now that the engine foundation is... |
| [plugin-ecosystem-summary.md](plugin-ecosystem-summary.md) | All plugins are ready for test implementation per `plans/test-specs-plugins.md`: - Tolerant parsi... |
| [plugin-quick-reference.md](plugin-quick-reference.md) | | Plugin ID | Type | Extensions | Category | Requires | Success Codes | |-----------|------|-----... |

---

## Reference Documentation

| Document | Purpose |
|----------|---------|
| [CLI_TOOL_UPDATES.md](reference/CLI_TOOL_UPDATES.md) | This document consolidates guidance from the conversation about configuring and controlling AI-po... |
| [HARDCODED_PATH_INDEXER.md](HARDCODED_PATH_INDEXER.md) | This tool scans the repository to index hardcoded paths, Python imports, and path-like references... |

---

## Planning & Roadmap

| Document | Purpose |
|----------|---------|
| [phase-github-issues-resolution.md](phase-github-issues-resolution.md) | **Phase ID:** `PHASE-GH-ISSUES-2025-11`   **Status:** Draft   **Created:** 2025-11-19   **Owner:*... |
| [PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md](PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md) | **Status**: Planning   **Timeline**: 8-12 days   **Dependencies**: Phase J (Error Detection Integ... |
| [PHASE_PLAN.md](PHASE_PLAN.md) | This document summarizes the PH-01 to PH-03 plan and associated Codex/Claude workstreams at a hig... |
| [PHASE_ROADMAP.md](PHASE_ROADMAP.md) | **Last Updated**: 2025-11-21   **Current Status**: Phase I Complete ✅ |

---

## Migration & Refactoring

| Document | Purpose |
|----------|---------|
| [adr-0005-spec-tooling-consolidation.md](adr/adr-0005-spec-tooling-consolidation.md) | 1. SPEC_MGMT_V1 (sidecars + suite-index): implemented via tools under `tools/spec_*`    (renderer... |
| [ARCHIVE_2025-11-22_SUMMARY.md](ARCHIVE_2025-11-22_SUMMARY.md) | **Operation**: Archive AI_MANGER and AUX_mcp-data folders   **Status**: ✅ COMPLETE   **Duration**... |
| [CI_PATH_STANDARDS.md](CI_PATH_STANDARDS.md) | **Created**: 2025-11-19   **Workflow**: `.github/workflows/path_standards.yml`   **Status**: Active |
| [DEPRECATION_PLAN.md](DEPRECATION_PLAN.md) | **Date Created**: 2025-11-19   **Phase**: F (Post-Refactor Finalization)   **Workstream**: WS-24 ... |
| [id file consolidation checker.md](maintenance/id file consolidation checker.md) | - |
| [LEGACY_ARCHIVE_CANDIDATES.md](LEGACY_ARCHIVE_CANDIDATES.md) | **Date:** 2025-11-21   **Phase:** H3.1 - Identify Legacy/Temporary Folders   **Status:** Complete |
| [PATH_ABSTRACTION_SPEC.md](PATH_ABSTRACTION_SPEC.md) | This document defines the key→path indirection layer used by scripts and tools to avoid hard‑codi... |
| [spec-tooling-consolidation.md](spec-tooling-consolidation.md) | This repository standardizes on OpenSpec for specifications while preserving compatibility with t... |
| [SPEC_CONSOLIDATION_INVENTORY.md](SPEC_CONSOLIDATION_INVENTORY.md) | **Date:** 2025-11-21   **Phase:** H1.1 - Audit Current Spec Folders   **Status:** Complete |
| [SPEC_MIGRATION_GUIDE.md](SPEC_MIGRATION_GUIDE.md) | This migration consolidates `openspec/` and `spec/` into a single unified `specifications/` direc... |
| [wsl-migration.md](windows/wsl-migration.md) | This document centralizes the Windows‑first WSL2 migration guides and scripts to run Codex CLI an... |
| [ZERO_TOUCH_SYNC_DESIGN.md](ZERO_TOUCH_SYNC_DESIGN.md) | **Goal**: User never thinks about sync. Local and remote are always identical, automatically. |

---

## Miscellaneous

| Document | Purpose |
|----------|---------|
| [.gitignore-recommendations.md](.gitignore-recommendations.md) | - |
| [2025- ANTI-PATTERN FORENSICS.md](forensics/2025- ANTI-PATTERN FORENSICS.md) | *Forensic review of historical execution logs against the “Game Board” Non-Negotiables.* |
| [adr-error-utils-location.md](adr/adr-error-utils-location.md) | During the section-aware repository refactor (WS-12), we must decide where to place shared utilit... |
| [agentic_ai_prompting_crafting professional_reference.md](prompting/agentic_ai_prompting_crafting professional_reference.md) | ** |
| [AI_DEV_HYGIENE_GUIDELINES.md](guidelines/AI_DEV_HYGIENE_GUIDELINES.md) | ** Maintain context clarity for AI-assisted development |
| [Anthropic Prompt Guide → structure XML-ish thinking.md](prompting/Anthropic Prompt Guide → structure XML-ish thinking.md) | - |
| [anthropic_prompt_engineering_guide.md](prompting/anthropic_prompt_engineering_guide.md) | - **Use XML format indicators**   - Try: "Write the prose sections of your response in `<smoothly... |
| [apply edits without asking you every time.md](reference/apply edits without asking you every time.md) | copilot help permissions |
| [Background_task.md](planning/Background_task.md) | - |
| [CLAUDE.md](reference/tools/CLAUDE.md) | This file provides guidance to Claude Code (claude.ai/code) when working with code in this reposi... |
| [CORE_DUPLICATE_ANALYSIS.md](CORE_DUPLICATE_ANALYSIS.md) | **Date:** 2025-11-21   **Phase:** H2.1 - Audit Root-Level Core Duplicates   **Status:** Complete |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | ** Central navigation hub for all documentation |
| [FILE_ORGANIZATION_QUICK_REF.md](FILE_ORGANIZATION_QUICK_REF.md) | Quick lookup guide for where files should go |
| [FILE_ORGANIZATION_SYSTEM.md](FILE_ORGANIZATION_SYSTEM.md) | Define a clear separation strategy between development artifacts and production system files to prevent mixing and facilitate clean handover. |
| [GAME_BOARD_CHAT_&_PHASEPLSN.md](planning/GAME_BOARD_CHAT_&_PHASEPLSN.md) | Design blueprint for building a validation system |
| [GEMINI.md](reference/tools/GEMINI.md) | This project is a Python-based AI development pipeline orchestrator. It is designed to automate t... |
| [how to optimized for machine readability.md](prompting/how to optimized for machine readability.md) | - |
| [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md) | Map every specialized term to exact code locations (file:line) |
| [Invoke_POWERSHELLGALLERY.md](reference/tools/Invoke_POWERSHELLGALLERY.md) | This document is designed for **agentic AI** evaluating whether the following three resources pro... |
| [ollama-installation-notes.md](reference/tools/ollama-installation-notes.md) | - |
| [path_standardizer.md](reference/plugins/path_standardizer.md) | Uses CCPM's path validation tools to ensure consistent path usage across the codebase. |
| [plugin-test-suite-summary.md](plugin-test-suite-summary.md) | Test plugin logic without requiring tools installed |
| [Prompt_improve.md](prompting/Prompt_improve.md) | apps:   aider:     roles: [source, target]          # can submit and receive tasks     cmd_templa... |
| [PROPOSED_DIRECTORY_TREE.md](planning/PROPOSED_DIRECTORY_TREE.md) | "Production orchestration engine" |
| [PRR_ai_prompt_engineering_reference.md](prompting/PRR_ai_prompt_engineering_reference.md) | "validate_and_normalize_input_data" |
| [README.md](forensics/README.md) | This directory contains post-mortem analyses and lessons learned from development sessions. |
| [README.md](guidelines/README.md) | This directory contains coding standards, hygiene practices, and development rules. |
| [README.md](maintenance/README.md) | Maintenance scripts, inventories, and operational records |
| [README.md](planning/README.md) | Planning documents, proposals, and design discussions |
| [README.md](prompting/README.md) | This directory contains reference materials and guides for crafting effective prompts for AI syst... |
| [README.md](reference/README.md) | Reference material, patterns, and external resources |
| [README.md](sessions/README.md) | Historical session reports and development summaries |
| [README.md](spec/README.md) | This directory hosts generated and supporting artifacts for the spec index and mapping between do... |
| [spec_index_map.md](spec/spec_index_map.md) | **AI Development Pipeline - Specification to Code Mapping** |
| [test_runner.md](reference/plugins/test_runner.md) | Uses CCPM's `test-and-log.sh` for multi-language test execution. |
| [UI_DATA_REQUIREMENTS.md](UI_DATA_REQUIREMENTS.md) | Single overview of "factory health" |
| [UI_INTERACTIVE_TOOL_SELECTION.md](UI_INTERACTIVE_TOOL_SELECTION.md) | The UI settings system allows you to configure which CLI tool runs in interactive mode (where use... |
| [UI_TOOL_SELECTION_QUICK_REF.md](UI_TOOL_SELECTION_QUICK_REF.md) | A system that lets you configure which CLI tool runs in interactive mode (where you send commands... |
| [USER_PROCESS_UNDERSTANDING_ASSESSMENT.md](USER_PROCESS_UNDERSTANDING_ASSESSMENT.md) | Assessment of user's understanding vs actual codebase capabilities |
| [workstream-style-prompt-structure.md](reference/workstream-style-prompt-structure.md) | files_scope: - <relative/path/to/file1> - <relative/path/to/file2> files_may_create: - <relative/... |

---

## ⚠️ Validation Warnings

The following broken links were detected:

- `ARCHITECTURE.md` → `SECTION_REFACTOR_MAPPING.md`
- `ARCHITECTURE.md` → `SECTION_REFACTOR_MAPPING.md`
- `ARCHITECTURE_DIAGRAMS.md` → `./SECTION_REFACTOR_MAPPING.md`
- `ARCHITECTURE_DIAGRAMS.md` → `./PHASE_F_PLAN.md`
- `CI_PATH_STANDARDS.md` → `SECTION_REFACTOR_MAPPING.md`
- `CI_PATH_STANDARDS.md` → `SECTION_REFACTOR_MAPPING.md`
- `CI_PATH_STANDARDS.md` → `MIGRATION_GUIDE.md`
- `CI_PATH_STANDARDS.md` → `PHASE_F_PLAN.md`
- `CONFIGURATION_GUIDE.md` → `PHASE_G_INVOKE_ADOPTION.md`
- `DEPRECATION_PLAN.md` → `SECTION_REFACTOR_MAPPING.md`
- `DEPRECATION_PLAN.md` → `SECTION_REFACTOR_MAPPING.md`
- `DEPRECATION_PLAN.md` → `PHASE_F_PLAN.md`
- `DEPRECATION_PLAN.md` → `WS-21_COMPLETE.md`
- `DEPRECATION_PLAN.md` → `WS-22_COMPLETE.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `VISUAL_ARCHITECTURE_GUIDE.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `VISUAL_ARCHITECTURE_GUIDE.md`
- `DOCUMENTATION_INDEX.md` → `analysis/Data%20Flow%20Analysis.md`
- `DOCUMENTATION_INDEX.md` → `PHASE_I_COMPLETE.md`
- `DOCUMENTATION_INDEX.md` → `PHASE_G_COMPLETE_REPORT.md`
- `DOCUMENTATION_INDEX.md` → `PHASE_G_FINAL_SUMMARY.md`
- `DOCUMENTATION_INDEX.md` → `PHASE_F_CHECKLIST.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `TERM_RELATIONSHIPS.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `VISUAL_ARCHITECTURE_GUIDE.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `DOCUMENTATION_INDEX.md` → `VISUAL_ARCHITECTURE_GUIDE.md`
- `DOCUMENTATION_INDEX.md` → `../TERMS_SPEC_V1.md`
- `FILE_ORGANIZATION_SYSTEM.md` → `DIRECTORY_GUIDE.md`
- `guidelines\AI_DEV_HYGIENE_GUIDELINES.md` → `./CLEANUP_REORGANIZATION_STRATEGY.md`
- `guidelines\AI_DEV_HYGIENE_GUIDELINES.md` → `./Complete AI Development Pipeline – Canonical Phase Plan/ARCHITECTURE.md`
- `guidelines\AI_DEV_HYGIENE_GUIDELINES.md` → `./Complete AI Development Pipeline – Canonical Phase Plan/pipeline_plus/IMPLEMENTATION_SUMMARY.md`
- `IMPLEMENTATION_LOCATIONS.md` → `TERM_RELATIONSHIPS.md`
- `maintenance\README.md` → `../archive/ROOT_CLEANUP_PLAN.md`
- `planning\PROPOSED_DIRECTORY_TREE.md` → `../CLEANUP_REORGANIZATION_STRATEGY.md`
- `planning\PROPOSED_DIRECTORY_TREE.md` → `../AI_DEV_HYGIENE_GUIDELINES.md`
- `planning\PROPOSED_DIRECTORY_TREE.md` → `./docs/architecture/ARCHITECTURE_OVERVIEW.md`
- `Project_Management_docs\ccpm-openspec-workflow.md` → `../src/pipeline/README.md`
- `Project_Management_docs\ccpm-openspec-workflow.md` → `../src/plugins/README.md`
- `Project_Management_docs\ccpm-openspec-workflow.md` → `../.claude/rules/agent-coordination.md`
- `Project_Management_docs\openspec_bridge.md` → `./workstream_authoring_guide.md`
- `Project_Management_docs\openspec_bridge.md` → `./ARCHITECTURE.md`
- `Project_Management_docs\PHASE-09-CCPM-INTEGRATION-PLAN.md` → `../SECTION_REFACTOR_MAPPING.md`
- `Project_Management_docs\QUICKSTART_OPENSPEC.md` → `./ARCHITECTURE.md`
- `Project_Management_docs\QUICKSTART_OPENSPEC.md` → `./workstream_authoring_guide.md`
- `Project_Management_docs\QUICKSTART_OPENSPEC.md` → `../src/plugins/README.md`
- `reference\tools\CLAUDE.md` → `docs/SECTION_REFACTOR_MAPPING.md`
- `reference\tools\CLAUDE.md` → `docs/SECTION_REFACTOR_MAPPING.md`
- `reference\tools\CLAUDE.md` → `docs/CI_PATH_STANDARDS.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INDEX.md` → `../UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INDEX.md` → `../UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INDEX.md` → `../UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INDEX.md` → `PHASE_I_PLAN.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_INTEGRATION_DESIGN.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_WEEK1_IMPLEMENTATION.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_QUICK_REFERENCE.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_QUICK_REFERENCE.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_INTEGRATION_DESIGN.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_WEEK1_IMPLEMENTATION.md`
- `UET_INTEGRATION_SUMMARY.md` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/README.md`
- `UET_INTEGRATION_SUMMARY.md` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/STATUS.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_WEEK1_IMPLEMENTATION.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_QUICK_REFERENCE.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_WEEK1_IMPLEMENTATION.md`
- `UET_INTEGRATION_SUMMARY.md` → `docs/UET_INTEGRATION_DESIGN.md`
- `UI_INTERACTIVE_TOOL_SELECTION.md` → `../gui/Hybrid%20UI_GUI%20shell_terminal_TUI%20engine.md`

---

## 📊 Documentation Statistics

**Total Documents**: 118  
**Categories**: 9  
**Broken Links**: 74  

- **Architecture & Design**: 7 documents
- **Implementation Summaries**: 19 documents
- **Configuration Guides**: 7 documents
- **Integrations**: 23 documents
- **Development Guides**: 4 documents
- **Reference Documentation**: 2 documents
- **Planning & Roadmap**: 4 documents
- **Migration & Refactoring**: 12 documents
- **Miscellaneous**: 40 documents

---

## 🔄 Maintenance

**Auto-Generated**: This file is automatically generated. Do not edit manually.

**Update Commands**:
```bash
# Regenerate documentation index
python scripts/generate_doc_index.py

# Regenerate with custom output
python scripts/generate_doc_index.py --output docs/DOCUMENTATION_INDEX.md
```

**Update Schedule**:
- **On PR**: Automatically regenerated via CI
- **Manual**: Run script when adding new documentation

---

**Last Generated**: 2025-11-22 12:52:44 UTC  
**Generator**: `scripts/generate_doc_index.py`  
