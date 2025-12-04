"""Bootstrap Discovery - WS-02-01A"""

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


class ProjectScanner:
    """Scans project and detects characteristics."""

    # DOC_ID: DOC-CORE-BOOTSTRAP-DISCOVERY-138

    LANGUAGE_EXTENSIONS = {
        "python": [".py"],
        "javascript": [".js"],
        "markdown": [".md"],
        "yaml": [".yaml", ".yml"],
        "json": [".json"],
    }

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

    def scan(self):
        """Perform complete project scan."""
        languages = self._detect_languages()
        domain, confidence = self._classify_domain(languages)

        return {
            "project_root": str(self.project_root),
            "project_name": self.project_root.name,
            "domain": domain,
            "domain_confidence": confidence,
            "languages": languages,
            "frameworks": [],
            "resource_types": ["files"],
            "available_tools": [],
            "existing_ci": self._detect_ci(),
            "vcs": "git" if (self.project_root / ".git").exists() else None,
            "inferred_constraints": {},
            "directory_structure": self._analyze_structure(),
            "discovery_timestamp": datetime.now(UTC).isoformat() + "Z",
        }

    def _detect_languages(self):
        """Detect languages by file extensions."""
        counts = Counter()
        for lang, exts in self.LANGUAGE_EXTENSIONS.items():
            for ext in exts:
                counts[lang] += len(list(self.project_root.rglob(f"*{ext}")))

        total = sum(counts.values())
        if total == 0:
            return []

        return [
            {
                "language": lang,
                "percentage": round((count / total) * 100, 1),
                "file_count": count,
            }
            for lang, count in counts.most_common()
            if count > 0
        ]

    def _detect_ci(self):
        """Detect CI system."""
        if (self.project_root / ".github" / "workflows").exists():
            return "github-actions"
        return None

    def _analyze_structure(self):
        """Analyze directory structure."""
        return {
            "src_dirs": [
                d.name
                for d in self.project_root.iterdir()
                if d.is_dir() and "src" in d.name.lower()
            ],
            "test_dirs": [
                d.name
                for d in self.project_root.iterdir()
                if d.is_dir() and "test" in d.name.lower()
            ],
            "doc_dirs": [
                d.name
                for d in self.project_root.iterdir()
                if d.is_dir() and "doc" in d.name.lower()
            ],
        }

    def _classify_domain(self, languages):
        """Classify project domain."""
        if not languages:
            return "mixed", 0.5

        top_lang = languages[0]["language"]
        top_pct = languages[0]["percentage"]

        if top_lang == "python" and top_pct > 50:
            return "software-dev", 0.8
        elif top_lang == "markdown" and top_pct > 70:
            return "documentation", 0.9
        else:
            return "mixed", 0.6


if __name__ == "__main__":
    import sys

    scanner = ProjectScanner(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(json.dumps(scanner.scan(), indent=2))
