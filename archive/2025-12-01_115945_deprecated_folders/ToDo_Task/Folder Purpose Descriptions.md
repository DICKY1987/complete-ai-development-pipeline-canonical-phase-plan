---
doc_id: DOC-GUIDE-FOLDER-PURPOSE-DESCRIPTIONS-1086
---


   Folder Purpose Descriptions

   .config - Repository configuration files including AI policies,
   pytest settings, quality gates, and project profile. No README.

   .github - GitHub-specific configuration including Copilot
   instructions and CI/CD workflows. No README.

   .pytest_cache - Pytest test framework cache directory for test
   discovery and results (auto-generated). Has README.

   engine - Job execution engine with orchestrator, queue
   management, adapters, and state storage for task processing.
   Has README.

   registry - Central registry for tools, plugins, and pipeline
   components. Has README.

   assets - Static resources including diagrams and documentation
   images. Has README.

   examples - Demo scripts showing orchestrator integration and UI
   infrastructure usage patterns. Has README.

   aider - AI-assisted coding tool integration with templates,
   help documentation, and engine configuration. Has README.

   openspec - OpenSpec specification bridge for converting and
   managing project specifications. Has README.

   adr - Architecture Decision Records documenting major design
   choices (workstream model, hybrid architecture, database
   storage). Has README.

   AI_SANDBOX - Template directory for isolated AI experimentation
   environments. No README.

   modules - Modular Python packages organized by domain (core,
   error, aim, pm, specifications). No README.

   scripts - Automation scripts for migration, validation, import
   management, and workflow execution. Has README.

   UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK - UET framework
   containing core templates, patterns, profiles for standardized
   execution workflows. Has README.

   templates - Code generation templates for modules, migrations,
   and tests. No README.

   .claude - Claude AI assistant configuration with commands,
   rules, and local settings. No README.

   docs - Comprehensive documentation including guides,
   architecture decisions, agent instructions, and reference
   materials. No README (has index files).

   schema - Data schemas for jobs, workstreams, modules, and
   database migrations. Has README.

   capabilities - PowerShell capability registry defining
   available tools and resources. No README.

   aim - AI Manager (AIM) for tool registry, environment
   management, and AI service integration. Has README.

   core - Core domain modules including state management,
   orchestration, planning, and AST processing. Has README.

   .worktrees - Git worktrees for parallel development on
   different documentation batches. No README.

   .state - Runtime state storage including orchestrator database,
   health snapshots, and execution indices. No README.

   legacy - Archived deprecated code from pre-UET migration
   (AI_MANGER, prototypes). No README.

   ToDo_Task - Planning documents, integration analysis, and phase
   completion summaries. No README.

   tools - Specialized tooling for spec management, validation,
   pattern extraction, and migration. Has README.

   tests - Comprehensive test suite covering core, engine,
   plugins, and integration scenarios. Has README.

   workstreams_uet - UET-based workstream definitions for phased
   implementation (orchestration, adapters, resilience). No
   README.

   .execution - Execution tracking with anti-patterns,
   checkpoints, telemetry, and worktree coordination. No README.

   glossary - Terminology management system with automated
   updates, proposals, and documentation. Has README.

   config - Application configuration files (YAML, JSON) for
   tools, profiles, routing, and circuit breakers. Has README.

   infra - Infrastructure configuration for CI/CD, data
   management, and sync operations. Has README.

   .ai - AI assistant context including codebase map, common
   patterns, and workflow context. No README.

   cleanup_reports - Automated cleanup analysis reports with safe
   removal scripts and folder version scoring. No README.

   logs - Runtime logs from workstream commits and combined
   execution output. No README.

   workstreams - Legacy JSON workstream definitions for migration
   phases and pipeline enhancements. Has README.

   ccpm - Critical Chain Project Management integration with
   GitHub sync, hooks, and templates. Has README.

   prompting - Prompt engineering resources and best practices for
   AI interactions (Anthropic, Claude guides). Has README.

   doc_id - Document identifier registry system with batch
   processing and parallel execution framework. Has README.

   developer - Developer notes, analysis, planning documents, and
   session archives organized by phase. No README.

   pm - Project management module with CCPM integration, epic/PRD
   management, and GitHub workflows. Has README.

   specifications - Specification content management with indexing
   tools and change tracking. Has README.

   error - Error detection/correction pipeline with pluggable
   analyzers and shared utilities. Has README.

   gui - User interface documentation including hybrid UI design,
   tool selection flows, and visual examples. Has README.

   ai-logs-analyzer - Tool for analyzing, aggregating, and
   exporting AI agent interaction logs. Has README.

   archive - Historical brainstorms, cleanup reports, migration
   logs, and prototype analysis. No README.

 > create a plan and a execution pattern for creating a copy of
   all README files and pput the copies in a folder "READMEALL" in
    this location: "C:\Users\richg\ALL_AI\Complete AI Development
   Pipeline – Canonical Phase Plan\ToDo_Task". put the prefix
   "PROJECTT_" in all file names

     I've categorized all 46 folders into 6 categories with clear
   definitions:

   📦 MODULE (9) - Self-contained domain logic with public APIs
   (core, engine, error, aim, pm, specifications, gui, infra,
   modules)

   🔧 UTILITY (7) - Cross-cutting tools used by modules (scripts,
   tools, templates, ccpm, aider, ai-logs-analyzer, capabilities)

   📋 METADATA (20) - Configuration, documentation, schemas,
   governance (docs, config, schema, adr, workstreams,
   UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK, etc.)

   🗄️ INFRASTRUCTURE (6) - Runtime artifacts, caches, stat
   (.pytest_cache, .state, .worktrees, .execution, logs,
   cleanup_reports)

   🗃️ ARCHIVE (3) - Deprecated/historical content (legacy
   archive, AI_SANDBOX)

   📁 SUB-MODULE (0 top-level) - Found inside MODULE folders
   (core/engine/, error/plugins/, aim/cli/, etc.)
