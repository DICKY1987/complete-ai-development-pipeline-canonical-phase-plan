---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-MODULE-CENTRIC-ARCHITECTURE-OVERVIEW-850
---

# Module-Centric Architecture Overview

## Purpose
This overview captures the starting point for the module-centric refactor. It
records the canonical module kinds, points to the authoritative inventory, and
explains how the initial classification script maps legacy sections to module
ownership without moving any files.

## Inputs referenced
- DATA_FLOWS.md for pipeline boundaries and hand-offs.
- reports/paths_summary.txt and reports/paths_clusters.json for path usage
  signals.
- modules/MODULES_INVENTORY.yaml for module identifiers, kinds, and legacy
  path hints.

## Module kinds (enum)
PIPELINE_STAGE_MODULE, FEATURE_SERVICE_MODULE, INTEGRATION_BRIDGE_MODULE,
INTERFACE_MODULE, REGISTRY_METADATA_MODULE, INFRA_PLATFORM_MODULE,
OBSERVABILITY_REPORTING_MODULE, GOVERNANCE_KNOWLEDGE_MODULE,
SANDBOX_EXPERIMENTAL_MODULE, ARCHIVE_LEGACY_BUCKET.

## Inventory snapshot
- Inventory lives at modules/MODULES_INVENTORY.yaml with module_kind, ULID
  prefix, and legacy_paths for AIM, core, error, PM, and specifications
  modules.
- Legacy paths stay recorded so registry rows can be backfilled before any
  physical moves.
- Error plugins share the PIPELINE_STAGE_MODULE kind to align with the error
  detection data flow.
- registry backfill planner: scripts/generate_registry_backfill_plan.py scans
  the tree (skipping archive/sandbox) and emits
  reports/registry_backfill_plan.json with inferred module_id/module_kind and
  artifact_kind per file.

## Classification workflow
- Script: scripts/classify_module_registry.py reads the inventory and
  reports/paths_clusters.json, applies the enum-based heuristics from the
  module refactor plan, and writes reports/module_classification_report.json.
- The script prefers inventory legacy_paths when selecting a module_id, and
  otherwise falls back to section-based module_kind inference.
- No files are relocated; the output is a report to drive registry updates and
  migration sequencing.
