#!/usr/bin/env python3
"""
Module ID Assigner - Extends DOC_ID_REGISTRY.yaml with module_id field.

Usage:
    python scripts/module_id_assigner.py --dry-run      # Preview assignments
    python scripts/module_id_assigner.py --apply        # Apply changes
    python scripts/module_id_assigner.py --report-only  # Generate reports only
"""
DOC_ID: DOC-GUIDE-DOC-ID-MODULE-ID-ASSIGNER-451

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Repository root
REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "doc_id" / "specs" / "DOC_ID_REGISTRY.yaml"
REPORTS_DIR = REPO_ROOT / "doc_id" / "reports"
TAXONOMY_PATH = REPO_ROOT / "doc_id" / "specs" / "module_taxonomy.yaml"


class ModuleIDAssigner:
    """Assigns module_id to all docs in DOC_ID_REGISTRY.yaml"""

    def __init__(self):
        self.registry = None
        self.module_stats = defaultdict(list)
        self.unassigned = []

    def load_registry(self) -> Dict:
        """Load DOC_ID_REGISTRY.yaml"""
        if not REGISTRY_PATH.exists():
            raise FileNotFoundError(f"Registry not found: {REGISTRY_PATH}")

        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)

        print(f"==> Loaded registry: {len(self.registry.get('docs', []))} docs")
        return self.registry

    def get_primary_artifact_path(self, doc: Dict) -> Optional[str]:
        """Get primary artifact path from doc entry"""
        artifacts = doc.get("artifacts", [])

        # Prefer doc, spec, or source types
        for artifact in artifacts:
            if artifact.get("type") in ["doc", "spec", "source"]:
                return artifact.get("path", "")

        # Fallback to first artifact
        if artifacts:
            return artifacts[0].get("path", "")

        return None

    def infer_module_id(self, doc: Dict) -> Tuple[str, str]:
        """
        Infer module_id from doc entry.

        Returns:
            (module_id, reason)
        """
        path = self.get_primary_artifact_path(doc)
        category = doc.get("category", "")

        # If no path, try to infer from category
        if not path:
            return self.infer_from_category(doc, category)

        # Normalize path separators
        path = path.replace("\\", "/")

        # Rule 1: Core modules
        if path.startswith("core/engine/") or path.startswith("tests/engine/"):
            return "core.engine", "path_match"

        if path.startswith("core/state/") or path.startswith("tests/state/"):
            return "core.state", "path_match"

        if path.startswith("core/error/") or path.startswith("error/"):
            return "core.error", "path_match"

        if path.startswith("core/"):
            return "core.misc", "path_match"

        # Rule 2: AIM
        if path.startswith("aim/adapters/"):
            return "aim.adapters", "path_match"

        if path.startswith("aim/core/"):
            return "aim.core", "path_match"

        if path.startswith("aim/"):
            return "aim.misc", "path_match"

        # Rule 3: Project Management
        if path.startswith("pm/cli/"):
            return "pm.cli", "path_match"

        if path.startswith("pm/scripts/"):
            return "pm.scripts", "path_match"

        if path.startswith("pm/"):
            return "pm.misc", "path_match"

        # Rule 4: Patterns (UET)
        if "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/" in path:
            if "/specs/" in path:
                return "patterns.specs", "path_match"
            if "/executors/" in path:
                return "patterns.executors", "path_match"
            if "/examples/" in path:
                return "patterns.examples", "path_match"
            return "patterns.misc", "path_match"

        # Rule 5: Documentation/Guides
        if path.startswith("doc_id/") or (
            path.startswith("docs/") and category == "guide"
        ):
            if path.startswith("docs/tooling/"):
                return "docs.tooling", "path_match"
            return "docs.guides", "path_match"

        if path.startswith("docs/"):
            return "docs.guides", "path_match"

        # Rule 6: ADR
        if path.startswith("adr/"):
            return "adr.architecture", "path_match"

        # Rule 7: Configuration
        if path.startswith("config/"):
            return "config.global", "path_match"

        # Rule 8: Infrastructure
        if (
            path.startswith("infra/")
            or path.startswith(".github/")
            or path.startswith("ci/")
        ):
            return "infra.ci", "path_match"

        # Rule 9: Scripts
        if path.startswith("scripts/"):
            return "scripts.automation", "path_match"

        # Rule 10: Tests (inherit from category)
        if path.startswith("tests/"):
            # Try to infer from category
            if category == "core":
                return "core.engine", "test_category_match"
            if category == "error":
                return "core.error", "test_category_match"
            if category == "test":
                return "test.suite", "path_match"
            return "test.suite", "path_match"

        # Rule 11: Legacy/Archive
        if path.startswith("legacy/") or path.startswith("archive/"):
            return "legacy.archived", "path_match"

        # Rule 12: Workstreams/Tasks
        if path.startswith("workstreams/") or path.startswith("ToDo_Task/"):
            return "workstreams.tasks", "path_match"

        # Rule 13: Tool-specific directories
        if (
            path.startswith(".claude/")
            or path.startswith("prompting/")
            or path.startswith("aider/")
        ):
            return "docs.tooling", "path_match"

        if path.startswith("ccpm/"):
            return "pm.cli", "path_match"

        if path.startswith("ai-logs-analyzer/") or path.startswith("AI_SANDBOX/"):
            return "scripts.automation", "path_match"

        # Rule 14: Specifications and schemas
        if (
            path.startswith("specifications/")
            or path.startswith("schema/")
            or path.startswith("openspec/")
        ):
            return "docs.guides", "path_match"

        # Rule 15: Reports and state
        if (
            path.startswith("reports/")
            or path.startswith(".state/")
            or path.startswith("state/")
        ):
            return "infra.ci", "path_match"

        # Rule 16: GUI and abstraction
        if path.startswith("gui/") or path.startswith("abstraction/"):
            return "docs.guides", "path_match"

        # Rule 17: Assets, glossary, examples
        if (
            path.startswith("assets/")
            or path.startswith("glossary/")
            or path.startswith("examples/")
        ):
            return "docs.guides", "path_match"

        # Rule 18: Developer docs and Module-Centric
        if path.startswith("developer/") or path.startswith("Module-Centric/"):
            return "docs.guides", "path_match"

        # Rule 19: Modules registry and tools
        if (
            path.startswith("modules/")
            or path.startswith("registry/")
            or path.startswith("tools/")
        ):
            return "docs.guides", "path_match"

        # Rule 20: Refactor and hidden directories
        if (
            path.startswith("REFACTOR_")
            or path.startswith(".ai")
            or path.startswith(".config")
            or path.startswith(".uet")
            or path.startswith(".execution")
        ):
            return "docs.guides", "path_match"

        # Rule 21: Engine (if not caught by core.engine)
        if path.startswith("engine/"):
            return "core.engine", "path_match"

        # Rule 22: Root-level files - use category
        # Files in the root directory without subdirectory structure
        if "/" not in path or path.count("/") == 0:
            return self.infer_from_category(doc, category)

        # Fallback
        return "unassigned", "no_matching_rule"

    def infer_from_category(self, doc: Dict, category: str) -> Tuple[str, str]:
        """Infer module_id from category when no path is available"""
        # Map category to module_id
        category_mapping = {
            "core": "core.misc",
            "patterns": "patterns.misc",
            "error": "core.error",
            "spec": "docs.guides",
            "arch": "adr.architecture",
            "aim": "aim.misc",
            "pm": "pm.misc",
            "infra": "infra.ci",
            "config": "config.global",
            "script": "scripts.automation",
            "test": "test.suite",
            "guide": "docs.guides",
            "legacy": "legacy.archived",
            "task": "workstreams.tasks",
        }

        module_id = category_mapping.get(category, "unassigned")
        reason = (
            "category_fallback"
            if module_id != "unassigned"
            else "no_artifact_no_category_match"
        )

        return module_id, reason

    def assign_module_ids(self, dry_run: bool = True) -> Dict:
        """
        Assign module_id to all docs.

        Args:
            dry_run: If True, don't modify registry, just collect stats

        Returns:
            Assignment statistics
        """
        if not self.registry:
            self.load_registry()

        docs = self.registry.get("docs", [])
        total = len(docs)
        assigned = 0

        print(
            f"\n{'DRY-RUN' if dry_run else 'APPLYING'}: Assigning module_id to {total} docs..."
        )

        for i, doc in enumerate(docs, 1):
            doc_id = doc.get("doc_id", "UNKNOWN")

            # Skip if already has module_id (unless we're re-assigning)
            if "module_id" in doc and dry_run:
                module_id = doc["module_id"]
                reason = "already_assigned"
            else:
                module_id, reason = self.infer_module_id(doc)

                if not dry_run:
                    # Insert module_id after 'status' field
                    # We need to preserve order, so rebuild dict
                    new_doc = {}
                    for key, value in doc.items():
                        new_doc[key] = value
                        if key == "status":
                            new_doc["module_id"] = module_id

                    # If 'status' wasn't found, add at end
                    if "module_id" not in new_doc:
                        new_doc["module_id"] = module_id

                    # Update doc in place
                    docs[i - 1].clear()
                    docs[i - 1].update(new_doc)

            # Collect stats
            self.module_stats[module_id].append(
                {
                    "doc_id": doc_id,
                    "category": doc.get("category", "unknown"),
                    "path": self.get_primary_artifact_path(doc),
                    "reason": reason,
                }
            )

            if module_id == "unassigned":
                self.unassigned.append(
                    {
                        "doc_id": doc_id,
                        "category": doc.get("category", "unknown"),
                        "candidate_paths": [
                            a.get("path", "") for a in doc.get("artifacts", [])
                        ],
                        "reason": reason,
                    }
                )
            else:
                assigned += 1

            if i % 100 == 0:
                print(f"  Progress: {i}/{total} ({i*100//total}%)")

        stats = {
            "total_docs": total,
            "assigned": assigned,
            "unassigned": len(self.unassigned),
            "modules_count": len(self.module_stats),
            "dry_run": dry_run,
        }

        print(f"\n==> Assignment complete:")
        print(f"   Total docs: {total}")
        print(f"   Assigned: {assigned} ({assigned*100//total}%)")
        print(
            f"   Unassigned: {len(self.unassigned)} ({len(self.unassigned)*100//total}%)"
        )
        print(f"   Modules: {len(self.module_stats)}")

        return stats

    def save_registry(self, backup: bool = True):
        """Save updated registry to disk"""
        if backup:
            backup_path = REGISTRY_PATH.with_suffix(".backup.yaml")
            import shutil

            shutil.copy2(REGISTRY_PATH, backup_path)
            print(f"Backup saved: {backup_path}")

        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            yaml.dump(
                self.registry,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        print(f"Registry saved: {REGISTRY_PATH}")

    def generate_reports(self):
        """Generate assignment reports"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Report 1: Dry-run markdown report
        dry_run_report = REPORTS_DIR / "MODULE_ID_ASSIGNMENT_DRY_RUN.md"
        with open(dry_run_report, "w", encoding="utf-8") as f:
            f.write("# Module ID Assignment Dry-Run Report\n\n")
            f.write(f"**Generated**: {datetime.utcnow().isoformat()}Z\n\n")

            f.write("## Summary\n\n")
            f.write(
                f"- Total docs: {sum(len(docs) for docs in self.module_stats.values())}\n"
            )
            f.write(f"- Modules assigned: {len(self.module_stats)}\n")
            f.write(f"- Unassigned: {len(self.unassigned)}\n\n")

            f.write("## Distribution by Module\n\n")
            for module_id in sorted(self.module_stats.keys()):
                docs = self.module_stats[module_id]
                f.write(f"### {module_id} ({len(docs)} docs)\n\n")

                # Show first 3 examples
                for doc in docs[:3]:
                    f.write(f"- `{doc['doc_id']}` - {doc['path']}\n")

                if len(docs) > 3:
                    f.write(f"- ... and {len(docs) - 3} more\n")
                f.write("\n")

        print(f"Dry-run report: {dry_run_report}")

        # Report 2: Unassigned JSONL
        if self.unassigned:
            unassigned_report = REPORTS_DIR / "MODULE_ID_UNASSIGNED.jsonl"
            with open(unassigned_report, "w", encoding="utf-8") as f:
                for entry in self.unassigned:
                    f.write(json.dumps(entry) + "\n")

            print(f"Unassigned report: {unassigned_report}")

        # Report 3: Final stats JSON
        final_stats = REPORTS_DIR / "MODULE_ID_ASSIGNMENT_FINAL.json"
        stats = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_docs": sum(len(docs) for docs in self.module_stats.values()),
            "modules": {
                module_id: len(docs)
                for module_id, docs in sorted(self.module_stats.items())
            },
            "unassigned_count": len(self.unassigned),
        }

        with open(final_stats, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        print(f"Final stats: {final_stats}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Assign module_id to all docs in registry"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview assignments without modifying registry",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply assignments to registry"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate reports only (requires previous run)",
    )

    args = parser.parse_args()

    if not (args.dry_run or args.apply or args.report_only):
        parser.print_help()
        print("\nError: Must specify one of --dry-run, --apply, or --report-only")
        sys.exit(1)

    assigner = ModuleIDAssigner()

    if args.report_only:
        print("Report-only mode: Loading existing data...")
        # For report-only, we need to load and re-analyze
        assigner.load_registry()
        assigner.assign_module_ids(dry_run=True)
        assigner.generate_reports()
    elif args.dry_run:
        print("DRY-RUN mode: Preview assignments...")
        assigner.load_registry()
        assigner.assign_module_ids(dry_run=True)
        assigner.generate_reports()
    elif args.apply:
        print("APPLY mode: Modifying registry...")
        assigner.load_registry()
        assigner.assign_module_ids(dry_run=False)
        assigner.save_registry(backup=True)
        assigner.generate_reports()
        print("\n==> Module ID assignment complete!")


if __name__ == "__main__":
    main()
