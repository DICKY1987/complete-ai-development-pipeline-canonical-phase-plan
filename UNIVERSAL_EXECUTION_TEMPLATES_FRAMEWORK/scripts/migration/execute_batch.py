"""
Execute a migration batch defined in .migration/migration_plan.yaml.

By default this runs in dry-run mode and only reports what would be staged.
Use --apply to copy source files into the staging area under
.migration/stage/<batch_id>/ without touching originals.
"""

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATION_DIR = REPO_ROOT / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" / ".migration"
PLAN_PATH = MIGRATION_DIR / "migration_plan.yaml"
LOG_PATH = MIGRATION_DIR / "migration_log.yaml"
STAGE_DIR = MIGRATION_DIR / "stage"


def load_plan() -> Dict[str, Any]:
    if not PLAN_PATH.exists():
        raise FileNotFoundError(f"Migration plan not found: {PLAN_PATH}")
    return yaml.safe_load(PLAN_PATH.read_text())


def find_batch(plan: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
    for batch in plan.get("batches", []):
        if batch.get("batch_id") == batch_id:
            return batch
    raise ValueError(f"Batch {batch_id} not found in plan.")


def append_log(entry: Dict[str, Any]) -> None:
    existing: List[Dict[str, Any]] = []
    if LOG_PATH.exists():
        loaded = yaml.safe_load(LOG_PATH.read_text())
        if isinstance(loaded, list):
            existing = loaded
    existing.append(entry)
    LOG_PATH.write_text(yaml.safe_dump(existing, default_flow_style=False))


def stage_files(batch: Dict[str, Any], apply: bool) -> Dict[str, Any]:
    staged = []
    missing = []

    for rel_path in batch.get("files", []):
        src = REPO_ROOT / rel_path
        dest = STAGE_DIR / batch["batch_id"] / rel_path

        if not src.exists():
            missing.append(str(src))
            continue

        staged.append({"source": str(src), "staged_to": str(dest)})

        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    return {
        "staged": staged,
        "missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute a migration batch (staged copy only; originals untouched)."
    )
    parser.add_argument("batch_id", help="Batch ID from migration_plan.yaml (e.g., WS-005)")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy files into .migration/stage/<batch_id>/ (default is dry-run).",
    )
    args = parser.parse_args()

    plan = load_plan()
    batch = find_batch(plan, args.batch_id)

    print(f"== Executing {args.batch_id} ({batch.get('component')})")
    if batch.get("dependencies"):
        print(f"Dependencies: {', '.join(batch['dependencies'])}")
    print(f"Files in batch: {batch.get('file_count', len(batch.get('files', [])))}")

    result = stage_files(batch, apply=args.apply)

    if result["staged"]:
        action_word = "Staged" if args.apply else "Would stage"
        print(f"\n{action_word} {len(result['staged'])} file(s) to {STAGE_DIR / args.batch_id}")
        for item in result["staged"]:
            print(f" - {item['source']} -> {item['staged_to']}")
    else:
        print("\nNo files staged.")

    if result["missing"]:
        print(f"\nMissing {len(result['missing'])} file(s):")
        for missing_path in result["missing"]:
            print(f" - {missing_path}")

    append_log(
        {
            "batch_id": args.batch_id,
            "component": batch.get("component"),
            "mode": "apply" if args.apply else "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "staged_count": len(result["staged"]),
            "missing_count": len(result["missing"]),
            "staged": result["staged"],
            "missing": result["missing"],
        }
    )

    print("\nLog updated:", LOG_PATH)
    if not args.apply:
        print("Dry-run only. Re-run with --apply to copy into staging.")


if __name__ == "__main__":
    main()
