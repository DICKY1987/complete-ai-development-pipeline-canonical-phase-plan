import hashlib
from pathlib import Path
from typing import Dict, List
import yaml
from datetime import datetime, timezone


class DuplicateFinder:
    def __init__(self, root: Path):
        self.root = root
        self.file_hashes: Dict[str, List[Path]] = {}

    def scan_duplicates(self, exclude_patterns: List[str]) -> Dict:
        """Find duplicate files by content hash."""
        duplicates = {}

        print("?? Scanning for duplicate Python files...")

        for py_file in self.root.rglob("*.py"):
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            file_hash = self._hash_file(py_file)

            if file_hash not in self.file_hashes:
                self.file_hashes[file_hash] = []
            self.file_hashes[file_hash].append(py_file)

        for file_hash, paths in self.file_hashes.items():
            if len(paths) > 1:
                duplicates[file_hash] = {
                    "count": len(paths),
                    "locations": [str(p.relative_to(self.root)) for p in paths],
                    "canonical": self._select_canonical(paths),
                    "file_size": paths[0].stat().st_size,
                }

        return duplicates

    def _hash_file(self, path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

    def _select_canonical(self, paths: List[Path]) -> str:
        """Select canonical version (prefer UET, then modules, then active)."""
        priorities = [
            "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK",
            "modules",
            "core",
            "error",
            "aim",
            "pm",
            "specifications",
        ]

        for priority in priorities:
            for path in paths:
                if priority in str(path):
                    return str(path.relative_to(self.root))

        newest = max(paths, key=lambda p: p.stat().st_mtime)
        return str(newest.relative_to(self.root))


if __name__ == "__main__":
    root = Path(".")
    finder = DuplicateFinder(root)

    exclude = [
        "__pycache__",
        ".venv",
        "archive/legacy",
        "tests/",
        "test_",
    ]

    duplicates = finder.scan_duplicates(exclude)

    registry = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "total_duplicates": len(duplicates),
        "total_duplicate_files": sum(d["count"] for d in duplicates.values()),
        "duplicates": duplicates,
    }

    output_path = Path(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml"
    )
    output_path.write_text(yaml.dump(registry, default_flow_style=False))

    print("\n? Scan complete:")
    print(f"   - Found {registry['total_duplicates']} unique files with duplicates")
    print(f"   - Total duplicate instances: {registry['total_duplicate_files']}")
    print(f"   - Registry saved to: {output_path}")
