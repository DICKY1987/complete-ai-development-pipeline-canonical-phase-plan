"""Duplicate File Detector - EXEC-014 Implementation

Detects exact file duplicates using SHA256 hashing with canonical file ranking.
Supports discovery, analysis, and verification phases.

Usage:
    python duplicate_detector.py --scan-paths . --report duplicates.json
    python duplicate_detector.py --verify  # Verify no duplicates remain
"""
DOC_ID: DOC-PAT-DETECTORS-DUPLICATE-DETECTOR-879

from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Set

import yaml


@dataclass
class DuplicateGroup:
    """Group of files with identical content."""
    hash: str
    file_count: int
    total_size_bytes: int
    files: List[str]
    canonical: str | None = None
    canonical_score: int | None = None


@dataclass
class DetectionResult:
    """Result of duplicate detection."""
    duplicate_groups: List[DuplicateGroup]
    total_duplicates: int
    potential_savings_bytes: int
    scan_summary: Dict[str, int]


class DuplicateDetector:
    """Detect exact file duplicates via SHA256 hashing."""

    # Location tier weights (higher = more canonical)
    LOCATION_TIERS = {
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/": 100,
        "modules/": 70,
        "core/": 50,
        "error/": 50,
        "engine/": 30,
        "archive/": 10,
        "": 20  # Default for unknown paths
    }

    def __init__(self, config_path: str = "config/cleanup_automation_config.yaml"):
        """Initialize detector with configuration."""
        self.config = self._load_config(config_path)
        self.hash_cache: Dict[str, str] = {}

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self) -> dict:
        """Default configuration if file not found."""
        return {
            "global": {
                "scan_paths": ["."],
                "exclusions": {
                    "directories": [".git/", "__pycache__/", "node_modules/"],
                    "file_patterns": ["*.pyc", "*.pyo", "*.log"]
                }
            },
            "patterns": {
                "EXEC-014": {
                    "hash_algorithm": "SHA256",
                    "min_file_size_bytes": 1024,
                    "scoring": {
                        "location_tier": 40,
                        "recency": 30,
                        "import_count": 20,
                        "path_depth": 10
                    }
                }
            }
        }

    def compute_file_hash(self, file_path: Path, algorithm: str = "SHA256") -> str:
        """Compute hash of file content."""
        if str(file_path) in self.hash_cache:
            return self.hash_cache[str(file_path)]

        hasher = hashlib.sha256() if algorithm == "SHA256" else hashlib.md5()

        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()
            self.hash_cache[str(file_path)] = file_hash
            return file_hash

        except (IOError, PermissionError) as e:
            print(f"Warning: Could not hash {file_path}: {e}", file=sys.stderr)
            return ""

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        path_str = str(path)
        exclusions = self.config.get("global", {}).get("exclusions", {})

        # Check directory exclusions
        for excl_dir in exclusions.get("directories", []):
            if excl_dir in path_str:
                return True

        # Check file pattern exclusions
        for pattern in exclusions.get("file_patterns", []):
            if path.match(pattern):
                return True

        return False

    def scan_for_duplicates(self, scan_paths: List[str]) -> DetectionResult:
        """Scan paths and detect duplicate files."""
        hash_groups: Dict[str, List[Path]] = defaultdict(list)
        min_size = self.config.get("patterns", {}).get("EXEC-014", {}).get("min_file_size_bytes", 1024)

        scanned_count = 0
        excluded_count = 0

        for scan_path in scan_paths:
            root = Path(scan_path)
            if not root.exists():
                print(f"Warning: Path does not exist: {scan_path}", file=sys.stderr)
                continue

            for file_path in root.rglob("*"):
                if not file_path.is_file():
                    continue

                if self.should_exclude(file_path):
                    excluded_count += 1
                    continue

                if file_path.stat().st_size < min_size:
                    continue

                scanned_count += 1
                file_hash = self.compute_file_hash(file_path)

                if file_hash:
                    hash_groups[file_hash].append(file_path)

        # Filter to only groups with 2+ files (duplicates)
        duplicate_groups = []
        total_duplicates = 0
        potential_savings = 0

        for file_hash, files in hash_groups.items():
            if len(files) < 2:
                continue

            file_size = files[0].stat().st_size
            group = DuplicateGroup(
                hash=file_hash,
                file_count=len(files),
                total_size_bytes=file_size * len(files),
                files=[str(f) for f in files]
            )

            # Rank files to determine canonical
            canonical, score = self._rank_canonical(files)
            group.canonical = str(canonical)
            group.canonical_score = score

            duplicate_groups.append(group)
            total_duplicates += len(files) - 1  # Don't count canonical
            potential_savings += file_size * (len(files) - 1)

        return DetectionResult(
            duplicate_groups=duplicate_groups,
            total_duplicates=total_duplicates,
            potential_savings_bytes=potential_savings,
            scan_summary={
                "scanned_files": scanned_count,
                "excluded_files": excluded_count,
                "duplicate_groups": len(duplicate_groups)
            }
        )

    def _rank_canonical(self, files: List[Path]) -> tuple[Path, int]:
        """Rank files to determine canonical version."""
        scoring = self.config.get("patterns", {}).get("EXEC-014", {}).get("scoring", {})

        best_file = files[0]
        best_score = 0

        for file_path in files:
            score = 0

            # Location tier scoring
            location_score = self._get_location_score(file_path)
            score += location_score * (scoring.get("location_tier", 40) / 100)

            # Recency scoring
            mtime = file_path.stat().st_mtime
            recency_score = min(mtime / 1e9, 1.0) * 100  # Normalize to 0-100
            score += recency_score * (scoring.get("recency", 30) / 100)

            # Path depth scoring (shallower = better)
            depth = len(file_path.parts)
            depth_score = max(0, 100 - (depth * 10))  # Penalty for deep paths
            score += depth_score * (scoring.get("path_depth", 10) / 100)

            # Import count scoring (placeholder - would need import graph analysis)
            # For now, use simple heuristic: files in canonical locations get bonus
            if "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" in str(file_path):
                score += 20  # Bonus for UETF location

            if score > best_score:
                best_score = score
                best_file = file_path

        return best_file, int(best_score)

    def _get_location_score(self, file_path: Path) -> int:
        """Get location tier score for file path."""
        path_str = str(file_path)

        for tier_prefix, score in self.LOCATION_TIERS.items():
            if tier_prefix and tier_prefix in path_str:
                return score

        return self.LOCATION_TIERS[""]  # Default score

    def verify_no_duplicates(self, scan_paths: List[str]) -> bool:
        """Verify no duplicates remain after cleanup."""
        result = self.scan_for_duplicates(scan_paths)
        return result.total_duplicates == 0

    def export_report(self, result: DetectionResult, output_path: str) -> None:
        """Export detection result to JSON file."""
        output_data = {
            "duplicate_groups": [asdict(group) for group in result.duplicate_groups],
            "total_duplicates": result.total_duplicates,
            "potential_savings_bytes": result.potential_savings_bytes,
            "potential_savings_mb": round(result.potential_savings_bytes / (1024 * 1024), 2),
            "scan_summary": result.scan_summary
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Report exported to: {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect duplicate files")
    parser.add_argument("--scan-paths", nargs="+", default=["."], help="Paths to scan")
    parser.add_argument("--config", default="config/cleanup_automation_config.yaml", help="Config file")
    parser.add_argument("--report", help="Export report to JSON file")
    parser.add_argument("--verify", action="store_true", help="Verify no duplicates (exit 1 if found)")
    parser.add_argument("--check-staged", action="store_true", help="Check only staged git files")
    parser.add_argument("--fail-on-duplicate", action="store_true", help="Exit 1 if duplicates found")

    args = parser.parse_args()

    detector = DuplicateDetector(config_path=args.config)

    if args.verify or args.fail_on_duplicate:
        is_clean = detector.verify_no_duplicates(args.scan_paths)

        if is_clean:
            print("✓ No duplicates detected")
            sys.exit(0)
        else:
            print("✗ Duplicates detected", file=sys.stderr)
            sys.exit(1)

    result = detector.scan_for_duplicates(args.scan_paths)

    # Print summary
    print(f"\nDuplicate Detection Results:")
    print(f"  Total duplicate groups: {len(result.duplicate_groups)}")
    print(f"  Total duplicate files: {result.total_duplicates}")
    print(f"  Potential space savings: {result.potential_savings_bytes / (1024 * 1024):.2f} MB")
    print(f"  Files scanned: {result.scan_summary['scanned_files']}")

    # Print top 5 duplicate groups
    if result.duplicate_groups:
        print(f"\nTop 5 Duplicate Groups:")
        for i, group in enumerate(sorted(result.duplicate_groups, key=lambda g: g.total_size_bytes, reverse=True)[:5], 1):
            print(f"\n{i}. Hash: {group.hash[:16]}... ({group.file_count} files, {group.total_size_bytes / 1024:.1f} KB)")
            print(f"   Canonical: {group.canonical} (score: {group.canonical_score})")
            for file in group.files:
                if file != group.canonical:
                    print(f"   Duplicate: {file}")

    if args.report:
        detector.export_report(result, args.report)


if __name__ == "__main__":
    main()
