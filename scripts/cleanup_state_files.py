#!/usr/bin/env python3
"""
State File Cleanup Automation

Automatically archives and compresses old state files.

Strategy:
- Preserve critical: current.json, *.db, health.json
- Archive files older than retention period (default 30 days)
- Compress archived files with gzip
- Clean up temporary files

Usage:
    python scripts/cleanup_state_files.py --dry-run
    python scripts/cleanup_state_files.py --days 60
"""

import argparse
import gzip
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set

STATE_DIR = Path(__file__).parent.parent / ".state"
ARCHIVE_DIR = STATE_DIR / "archive"

CRITICAL_FILES = {"current.json", "health.json", "orchestration.db", "orchestrator.db"}
ARCHIVABLE_PATTERNS = ["pipeline_results_*.json", "*_inventory.jsonl", "*_scan*.json"]
TEMP_PATTERNS = ["*.tmp", "*.lock", "*_temp_*.json"]


class StateFileCleanup:
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.cutoff_date = datetime.now() - timedelta(days=retention_days)
        self.stats = {"archived": 0, "compressed": 0, "deleted": 0, "preserved": 0}

    def cleanup_all(self, dry_run: bool = False) -> bool:
        """Run complete cleanup workflow."""
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")

        if not STATE_DIR.exists():
            print(f"❌ State directory not found: {STATE_DIR}")
            return False

        self._archive_old_files(dry_run)
        self._compress_archived_files(dry_run)
        self._cleanup_temp_files(dry_run)
        self._print_summary()
        return True

    def _archive_old_files(self, dry_run: bool):
        """Archive files older than retention period."""
        print(f"📦 Archiving files older than {self.retention_days} days...")

        if not dry_run:
            ARCHIVE_DIR.mkdir(exist_ok=True)

        for file_path in STATE_DIR.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.parent == ARCHIVE_DIR:
                continue
            if file_path.name in CRITICAL_FILES:
                self.stats["preserved"] += 1
                continue

            if self._is_old_file(file_path):
                if self._matches_archivable_pattern(file_path):
                    self._archive_file(file_path, dry_run)

    def _compress_archived_files(self, dry_run: bool):
        """Compress archived files with gzip."""
        print(f"\n🗜️  Compressing archived files...")

        if not ARCHIVE_DIR.exists():
            return

        for file_path in ARCHIVE_DIR.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix == ".gz":
                continue

            self._compress_file(file_path, dry_run)

    def _cleanup_temp_files(self, dry_run: bool):
        """Remove temporary files."""
        print(f"\n🧹 Cleaning up temporary files...")

        for pattern in TEMP_PATTERNS:
            for file_path in STATE_DIR.rglob(pattern):
                if file_path.is_file():
                    action = "[DRY RUN] Would delete" if dry_run else "Deleting"
                    print(f"  {action}: {file_path.name}")
                    if not dry_run:
                        file_path.unlink()
                    self.stats["deleted"] += 1

    def _is_old_file(self, file_path: Path) -> bool:
        """Check if file is older than cutoff date."""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return mtime < self.cutoff_date
        except Exception:
            return False

    def _matches_archivable_pattern(self, file_path: Path) -> bool:
        """Check if file matches archivable patterns."""
        from fnmatch import fnmatch

        return any(fnmatch(file_path.name, pattern) for pattern in ARCHIVABLE_PATTERNS)

    def _archive_file(self, file_path: Path, dry_run: bool):
        """Move file to archive directory."""
        try:
            archive_path = ARCHIVE_DIR / file_path.name
            action = "[DRY RUN] Would archive" if dry_run else "Archiving"
            print(f"  {action}: {file_path.name}")

            if not dry_run:
                shutil.move(str(file_path), str(archive_path))
            self.stats["archived"] += 1
        except Exception as e:
            print(f"  ⚠️  Error archiving {file_path.name}: {e}")

    def _compress_file(self, file_path: Path, dry_run: bool):
        """Compress file with gzip."""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
            action = "[DRY RUN] Would compress" if dry_run else "Compressing"
            print(f"  {action}: {file_path.name}")

            if not dry_run:
                with open(file_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                file_path.unlink()
            self.stats["compressed"] += 1
        except Exception as e:
            print(f"  ⚠️  Error compressing {file_path.name}: {e}")

    def _print_summary(self):
        """Print cleanup summary."""
        print("\n" + "=" * 60)
        print("📊 CLEANUP SUMMARY")
        print("=" * 60)
        print(f"  Files archived:   {self.stats['archived']}")
        print(f"  Files compressed: {self.stats['compressed']}")
        print(f"  Temp files deleted: {self.stats['deleted']}")
        print(f"  Critical files preserved: {self.stats['preserved']}")
        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up old state files with archival and compression"
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Retention period in days (default: 30)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    args = parser.parse_args()

    cleanup = StateFileCleanup(args.days)
    success = cleanup.cleanup_all(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
