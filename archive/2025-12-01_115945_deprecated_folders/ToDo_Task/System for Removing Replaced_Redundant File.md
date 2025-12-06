---
doc_id: DOC-LEGACY-SYSTEM-FOR-REMOVING-REPLACED-REDUNDANT-007
---


   🗑️ Part 2: System for Removing Replaced/Redundant File

   Based on your existing DEPRECATION_PLAN.md and LEGACY_ARCHIVE_CANDIDATES.md, here's an enhanced automated system:

   Proposed: RESPONSIBILITY_TRACKER.yml

   Create a living document that tracks file purposes and replacements:

     # .meta/RESPONSIBILITY_TRACKER.yml
     version: "1.0"
     last_updated: "2025-11-22"

     categories:
       - state_management
       - orchestration
       - error_handling
       - tool_integration
       - specifications
       - project_management

     responsibilities:
       state_management:
         current_owners:
           - path: "core/state/db.py"
             purpose: "Database initialization and connection management"
             since: "2025-10-15"
             status: "canonical"
             tests: ["tests/unit/test_db.py"]

         deprecated_owners:
           - path: "src/pipeline/db.py"
             purpose: "Database shim (backward compatibility)"
             replaced_by: "core/state/db.py"
             deprecated_date: "2025-11-19"
             removal_date: "2026-11-19"
             status: "phase1_silent"

       orchestration:
         current_owners:
           - path: "core/engine/orchestrator.py"
             purpose: "Workstream orchestration and scheduling"
             since: "2025-10-20"
             status: "canonical"

       specifications:
         current_owners:
           - path: "specifications/tools/indexer/indexer.py"
             purpose: "Generate spec indices and sidecars"
             since: "2025-11-16"
             status: "canonical"

         redundant:
           - path: "Multi-Document Versioning Automation final_spec_docs/"
             purpose: "Planning docs for already-implemented features"
             replaced_by: "specifications/tools/"
             reason: "Over-planned before implementation; functionality exists"
             removed_date: "2025-11-22"
             archived_to: null  # Deleted, not archived

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Automated Cleanup Scripts

   1. Responsibility Scanner

     # scripts/check_responsibility_overlap.py
     """
     Scan codebase for files with overlapping responsibilities.
     Uses RESPONSIBILITY_TRACKER.yml as source of truth.
     """

     import yaml
     from pathlib import Path
     from typing import Dict, List

     def load_tracker() -> dict:
         return yaml.safe_load(Path(".meta/RESPONSIBILITY_TRACKER.yml").read_text())

     def find_duplicate_purposes() -> List[Dict]:
         """Find files claiming same responsibility"""
         tracker = load_tracker()
         duplicates = []

         for category, data in tracker["responsibilities"].items():
             purposes = {}
             for file_info in data.get("current_owners", []):
                 purpose = file_info["purpose"]
                 if purpose in purposes:
                     duplicates.append({
                         "purpose": purpose,
                         "files": [purposes[purpose], file_info["path"]],
                         "category": category
                     })
                 purposes[purpose] = file_info["path"]

         return duplicates

     def suggest_deprecations() -> List[Dict]:
         """Suggest which file should be deprecated based on criteria"""
         # Criteria: older file, fewer tests, less recent commits
         pass

   2. Deprecation Workflow Automation

     # scripts/auto_deprecate.py
     """
     Automatically move file through deprecation phases.
     Triggered by CI cron job or manual command.
     """

     from datetime import datetime, timedelta
     import yaml

     def check_phase_transitions():
         tracker = load_tracker()
         today = datetime.now()

         for category, data in tracker["responsibilities"].items():
             for dep in data.get("deprecated_owners", []):
                 dep_date = datetime.fromisoformat(dep["deprecated_date"])

                 # Phase 1 → Phase 2 (3 months)
                 if (today - dep_date) > timedelta(days=90) and dep["status"] == "phase1_silent":
                     add_deprecation_warnings(dep["path"])
                     update_tracker_status(dep["path"], "phase2_soft_warnings")

                 # Phase 2 → Phase 3 (6 months)
                 elif (today - dep_date) > timedelta(days=180) and dep["status"] == "phase2_soft_warnings":
                     increase_warning_verbosity(dep["path"])
                     update_tracker_status(dep["path"], "phase3_loud_warnings")

                 # Phase 3 → Removal (12 months)
                 elif (today - dep_date) > timedelta(days=365) and dep["status"] == "phase3_loud_warnings":
                     verify_zero_usage(dep["path"])
                     archive_or_delete(dep["path"])
                     update_tracker_status(dep["path"], "removed")

   3. Redundancy Detector

     # scripts/detect_redundant_planning_docs.py
     """
     Find planning documents for features that are already implemented.
     Cross-references docs/ with actual implementation.
     """

     def find_planning_for_implemented_features():
         # Scan docs/ for "PLAN", "ROADMAP", "PRODUCTION_READINESS"
         # Check if implementation exists
         # Suggest archival if >90% complete

         redundant_docs = []

         for doc in Path("docs/").rglob("*PLAN*.md"):
             if "PRODUCTION_READINESS" in doc.name:
                 feature = extract_feature_name(doc)
                 if implementation_exists(feature) and implementation_complete(feature):
                     redundant_docs.append({
                         "doc": doc,
                         "reason": "Feature implemented and complete",
                         "suggest": "archive"
                     })

         return redundant_docs

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Governance Process

   File Lifecycle States

     prototype → active → canonical → deprecated_phase1 → deprecated_phase2
     → deprecated_phase3 → archived/removed

   Decision Matrix

   ┌────────────────────────────────────────────────────────┬───────────────────────────────┐
   │ Condition                                              │ Action                        │
   ├────────────────────────────────────────────────────────┼───────────────────────────────┤
   │ Duplicate responsibility + newer implementation exists │ Deprecate older               │
   ├────────────────────────────────────────────────────────┼───────────────────────────────┤
   │ Planning doc + implementation complete                 │ Archive planning doc          │
   ├────────────────────────────────────────────────────────┼───────────────────────────────┤
   │ Test file + feature removed                            │ Archive test                  │
   ├────────────────────────────────────────────────────────┼───────────────────────────────┤
   │ Script + functionality in core                         │ Integrate or deprecate script │
   ├────────────────────────────────────────────────────────┼───────────────────────────────┤
   │ Documentation + newer docs exist                       │ Consolidate or archive        │
   └────────────────────────────────────────────────────────┴───────────────────────────────┘

   Weekly Automated Tasks

     # .github/workflows/cleanup-governance.yml
     name: Repository Cleanup Governance
     on:
       schedule:
         - cron: '0 0 * * 0'  # Weekly on Sunday

     jobs:
       check-deprecations:
         runs-on: ubuntu-latest
         steps:
           - name: Check deprecation phase transitions
             run: python scripts/auto_deprecate.py --dry-run

           - name: Find redundant planning docs
             run: python scripts/detect_redundant_planning_docs.py

           - name: Scan for duplicate responsibilities
             run: python scripts/check_responsibility_overlap.py

           - name: Create cleanup PR if needed
             if: changes_detected
             run: gh pr create --title "Weekly cleanup: deprecations and redundancies"

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   Immediate Actions

     - Create RESPONSIBILITY_TRACKER.yml - Document current canonical owners
     - Run redundancy scan - Find duplicate Multi-Document... situations
     - Update DEPRECATION_PLAN.md - Add responsibility tracking integration
     - Add to CI - Weekly automated scans for overlaps
     - Document in AGENTS.md - Add "Before adding new file, check RESPONSIBILITY_TRACKER.yml"

   Would you like me to create any of these files or implement the responsibility tracking system?
