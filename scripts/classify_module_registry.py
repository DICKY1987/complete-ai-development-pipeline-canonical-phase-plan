"""Classify path sections into module kinds and module ids without moving files.

Inputs:
- modules/MODULES_INVENTORY.yaml for module_id, module_kind, legacy_paths.
- reports/paths_clusters.json for path usage counts.

Output:
- reports/module_classification_report.json summarizing inferred module_kind and
  module_id per section to guide registry backfill before moves.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-CLASSIFY-MODULE-REGISTRY-197
DOC_ID: DOC-SCRIPT-SCRIPTS-CLASSIFY-MODULE-REGISTRY-134

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml


MODULE_KIND_ENUM = [
    "PIPELINE_STAGE_MODULE",
    "FEATURE_SERVICE_MODULE",
    "INTEGRATION_BRIDGE_MODULE",
    "INTERFACE_MODULE",
    "REGISTRY_METADATA_MODULE",
    "INFRA_PLATFORM_MODULE",
    "OBSERVABILITY_REPORTING_MODULE",
    "GOVERNANCE_KNOWLEDGE_MODULE",
    "SANDBOX_EXPERIMENTAL_MODULE",
    "ARCHIVE_LEGACY_BUCKET",
]


def load_inventory(inventory_path: Path) -> List[Dict]:
    data = yaml.safe_load(inventory_path.read_text())
    modules: List[Dict] = []
    for entry in data.get("modules", []):
        module_id = entry.get("module_id") or entry.get("id")
        if not module_id:
            continue
        entry = dict(entry)
        entry["module_id"] = module_id
        entry.setdefault("legacy_paths", [])
        modules.append(entry)
    return modules


def normalize(value: str) -> str:
    return value.replace("\\", "/").lower()


def infer_kind(section: str) -> Optional[str]:
    key = normalize(section)
    if key.startswith(("core", "engine", "workstreams", "pipeline", "state")):
        return "PIPELINE_STAGE_MODULE"
    if key.startswith(("aim", "universal_execution_templates_framework")):
        return "FEATURE_SERVICE_MODULE"
    if key.startswith(("openspec", "ccpm", "pm")):
        return "INTEGRATION_BRIDGE_MODULE"
    if key.startswith(("gui", "tui_app", "tui")):
        return "INTERFACE_MODULE"
    if key.startswith(("registry", "doc_id")):
        return "REGISTRY_METADATA_MODULE"
    if key.startswith(("reports", "cleanup_reports", "logs", "ai-logs-analyzer")):
        return "OBSERVABILITY_REPORTING_MODULE"
    if key.startswith(("docs", "adr", "glossary", "capabilities")):
        return "GOVERNANCE_KNOWLEDGE_MODULE"
    if key.startswith(("ai_sandbox", "sandbox")):
        return "SANDBOX_EXPERIMENTAL_MODULE"
    if key.startswith("archive"):
        return "ARCHIVE_LEGACY_BUCKET"
    if key.startswith(("scripts", "infra", ".ai", ".claude", ".execution", ".state")):
        return "INFRA_PLATFORM_MODULE"
    return None


def match_module(section: str, modules: List[Dict]) -> Optional[Dict]:
    normalized_section = normalize(section).strip("/")
    for module in modules:
        for legacy in module.get("legacy_paths", []):
            normalized_legacy = normalize(legacy).strip("/")
            if not normalized_legacy:
                continue
            if normalized_section.startswith(normalized_legacy) or normalized_legacy.startswith(
                normalized_section
            ):
                return module
    return None


def build_report(clusters_path: Path, inventory_path: Path) -> Dict:
    modules = load_inventory(inventory_path)
    clusters = json.loads(clusters_path.read_text())
    entries = []
    kind_counter: Counter = Counter()

    for section_info in clusters.get("top_sections", []):
        section = section_info.get("section", "")
        module_kind = infer_kind(section)
        module = match_module(section, modules)
        if module_kind:
            kind_counter[module_kind] += 1
        entry = {
            "section": section,
            "total": section_info.get("total"),
            "by_kind": section_info.get("by_kind", {}),
            "module_kind_guess": module_kind,
            "module_id_guess": module["module_id"] if module else None,
            "legacy_match": module.get("legacy_paths", []) if module else [],
            "inventory_module_kind": module.get("module_kind") if module else None,
        }
        entries.append(entry)

    summary = {
        "counts_by_inferred_module_kind": dict(kind_counter),
        "inventory_entries_loaded": len(modules),
        "sections_classified": len(entries),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "paths_clusters": str(clusters_path),
            "inventory": str(inventory_path),
        },
        "module_kind_enum": MODULE_KIND_ENUM,
        "sections": entries,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify path sections into module kinds to prep registry backfill."
    )
    parser.add_argument(
        "--paths-clusters",
        default=Path("reports") / "paths_clusters.json",
        type=Path,
        help="Path to paths_clusters.json",
    )
    parser.add_argument(
        "--inventory",
        default=Path("modules") / "MODULES_INVENTORY.yaml",
        type=Path,
        help="Path to modules inventory YAML",
    )
    parser.add_argument(
        "--output",
        default=Path("reports") / "module_classification_report.json",
        type=Path,
        help="Where to write the classification report",
    )
    args = parser.parse_args()

    report = build_report(args.paths_clusters, args.inventory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
