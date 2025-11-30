"""Generate a registry backfill plan using module inventory and path heuristics.

Inputs:
- modules/MODULES_INVENTORY.yaml (module_id, module_kind, legacy_paths)
- repository file tree (excluding archive/sandbox areas)

Output:
- reports/registry_backfill_plan.json containing inferred module ownership and
  artifact_kind per file to drive registry population before moving files.
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-GENERATE-REGISTRY-BACKFILL-PLAN-211
# DOC_ID: DOC-SCRIPT-SCRIPTS-GENERATE-REGISTRY-BACKFILL-PLAN-148

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

SKIP_DIRS = {
    ".git",
    ".venv",
    ".worktrees",
    "archive",
    "AI_SANDBOX",
    "sandbox_repos",
    ".aider",
    ".ai",
}

MODULE_KIND_ENUM = {
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
}


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").lower()


def load_inventory(inventory_path: Path) -> List[Dict]:
    data = yaml.safe_load(inventory_path.read_text())
    modules: List[Dict] = []
    for entry in data.get("modules", []):
        module_id = entry.get("module_id") or entry.get("id")
        if not module_id:
            continue
        entry = dict(entry)
        entry["module_id"] = module_id
        entry.setdefault("module_kind", entry.get("moduleKind"))
        entry.setdefault("legacy_paths", entry.get("legacy_paths", []))
        modules.append(entry)
    return modules


def best_module_for_path(path_str: str, modules: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    normalized = normalize_path(path_str)
    best_len = -1
    best_module: Optional[Dict] = None
    for module in modules:
        for legacy in module.get("legacy_paths", []):
            legacy_norm = normalize_path(legacy).rstrip("/")
            if not legacy_norm:
                continue
            if normalized.startswith(legacy_norm):
                if len(legacy_norm) > best_len:
                    best_len = len(legacy_norm)
                    best_module = module
    if best_module:
        module_kind = best_module.get("module_kind")
        if module_kind and module_kind not in MODULE_KIND_ENUM:
            module_kind = None
        return best_module["module_id"], module_kind
    return None, None


def infer_artifact_kind(path: Path) -> str:
    path_str = normalize_path(str(path))
    name = path.name.lower()
    suffix = path.suffix.lower()

    if "/tests/" in path_str or name.startswith("test_"):
        return "unit_test"
    if "schema" in path_str or suffix in {".schema.json", ".json"} and "schema" in path_str:
        return "schema"
    if "config" in path_str or suffix in {".yaml", ".yml", ".json"}:
        return "config"
    if suffix in {".md", ".txt"}:
        return "spec_doc"
    if suffix in {".py", ".ps1", ".sh", ".bat"}:
        return "code_module"
    return "other"


def iter_files(root: Path, skips: Iterable[str]) -> Iterable[Path]:
    skip_norm = {normalize_path(s) for s in skips}
    for path in root.rglob("*"):
        if path.is_dir():
            # Skip entire directory trees early when possible
            parts_norm = {normalize_path(part) for part in path.parts}
            if parts_norm & skip_norm:
                continue
        if not path.is_file():
            continue
        normalized = normalize_path(str(path))
        if any(seg in normalized.split("/") for seg in skip_norm):
            continue
        yield path


def build_plan(root: Path, inventory: Path, limit: Optional[int]) -> Dict:
    modules = load_inventory(inventory)
    records: List[Dict] = []
    counts_by_module: Counter = Counter()
    counts_by_kind: Counter = Counter()

    for idx, path in enumerate(iter_files(root, SKIP_DIRS)):
        if limit is not None and idx >= limit:
            break
        module_id, module_kind = best_module_for_path(str(path), modules)
        artifact_kind = infer_artifact_kind(path)
        record = {
            "path": str(path).replace("\\", "/"),
            "module_id": module_id,
            "module_kind": module_kind,
            "artifact_kind": artifact_kind,
        }
        records.append(record)
        if module_id:
            counts_by_module[module_id] += 1
        if module_kind:
            counts_by_kind[module_kind] += 1

    summary = {
        "total_records": len(records),
        "by_module_id": counts_by_module,
        "by_module_kind": counts_by_kind,
        "unassigned": sum(1 for r in records if not r["module_id"]),
    }
    # Convert Counters to plain dicts for JSON output
    summary["by_module_id"] = dict(summary["by_module_id"])
    summary["by_module_kind"] = dict(summary["by_module_kind"])

    return {"records": records, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate registry backfill plan from inventory and file tree.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to scan.")
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("modules") / "MODULES_INVENTORY.yaml",
        help="Path to modules inventory YAML.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "registry_backfill_plan.json",
        help="Where to write the plan JSON.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of files to process (for quick runs).",
    )
    args = parser.parse_args()

    plan = build_plan(args.root, args.inventory, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
