#!/usr/bin/env python3
# DOC_LINK: DOC-SCRIPT-PATTERN-DISCOVERY-001
"""
Pattern Discovery Tool - Identify Repetitive Work Patterns

PURPOSE: Analyze files to discover reusable patterns for template creation
USAGE:
    python scripts/pattern_discovery.py --analyze core/ error/ aim/
    python scripts/pattern_discovery.py --suggest --min-similarity 0.7

PATTERN: Automatic pattern recognition from existing code/docs
PHASE: Discovery phase automation (EXEC-001 through EXEC-008)
"""

import argparse
import difflib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class PatternDiscoverer:
    """
    Discover repetitive patterns in code/docs automatically.

    Implements discovery phase automation:
    1. Scan files for structural similarity
    2. Extract common patterns
    3. Suggest template opportunities
    4. Estimate time savings
    """

    def __init__(self, paths: List[Path], file_pattern: str = "*"):
        self.paths = paths
        self.file_pattern = file_pattern
        self.files = []
        self.patterns = defaultdict(list)

    def scan_files(self):
        """Scan for files matching pattern."""
        print(f"🔍 Scanning for files matching: {self.file_pattern}")

        for path in self.paths:
            if path.is_file():
                self.files.append(path)
            elif path.is_dir():
                self.files.extend(path.rglob(self.file_pattern))

        print(f"   Found {len(self.files)} files\n")
        return self.files

    def analyze_structure(self, min_similarity: float = 0.7):
        """
        Analyze files for structural similarity.

        Args:
            min_similarity: Minimum similarity ratio (0.0-1.0) to group files
        """
        print(f"📊 Analyzing structural similarity (threshold: {min_similarity})")

        # Group files by extension
        by_extension = defaultdict(list)
        for file in self.files:
            by_extension[file.suffix].append(file)

        # Analyze each extension group
        for ext, files in by_extension.items():
            if len(files) < 2:
                continue

            print(f"\n  Extension: {ext} ({len(files)} files)")

            # Compare files pairwise
            similar_groups = []
            processed = set()

            for i, file1 in enumerate(files):
                if file1 in processed:
                    continue

                group = [file1]
                processed.add(file1)

                content1 = self._read_file_safe(file1)
                if not content1:
                    continue

                for file2 in files[i + 1 :]:
                    if file2 in processed:
                        continue

                    content2 = self._read_file_safe(file2)
                    if not content2:
                        continue

                    similarity = self._calculate_similarity(content1, content2)

                    if similarity >= min_similarity:
                        group.append(file2)
                        processed.add(file2)

                if len(group) >= 2:
                    similar_groups.append((ext, similarity, group))
                    print(f"    Found pattern: {len(group)} similar files")

            self.patterns[ext] = similar_groups

        return self.patterns

    def _read_file_safe(self, path: Path) -> str:
        """Read file with error handling."""
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate structural similarity between two files.

        Uses sequence matching to find common structure.
        """
        # Normalize whitespace
        lines1 = [line.strip() for line in content1.split("\n") if line.strip()]
        lines2 = [line.strip() for line in content2.split("\n") if line.strip()]

        # Use SequenceMatcher for similarity ratio
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()

    def extract_common_structure(self, files: List[Path]) -> Dict:
        """
        Extract common structure from similar files.

        Returns:
            Template with variable markers and invariant sections
        """
        if len(files) < 2:
            return {}

        # Read all files
        contents = [self._read_file_safe(f) for f in files]
        contents = [c for c in contents if c]  # Filter empty

        if not contents:
            return {}

        # Find common lines
        all_lines = [set(c.split("\n")) for c in contents]
        common_lines = set.intersection(*all_lines)

        # Find variable lines (appear in some but not all)
        all_unique_lines = set()
        for lines in all_lines:
            all_unique_lines.update(lines)

        variable_lines = all_unique_lines - common_lines

        # Estimate template structure
        template = {
            "total_lines": len(contents[0].split("\n")),
            "common_lines": len(common_lines),
            "variable_lines": len(variable_lines),
            "stability_ratio": len(common_lines)
            / (len(common_lines) + len(variable_lines)),
            "sample_common": list(common_lines)[:5],
            "sample_variable": list(variable_lines)[:5],
        }

        return template

    def suggest_templates(self, min_files: int = 3) -> List[Dict]:
        """
        Suggest template creation opportunities.

        Args:
            min_files: Minimum number of similar files to suggest template
        """
        suggestions = []

        print(f"\n💡 Template Suggestions (min {min_files} files)")
        print("=" * 70)

        for ext, groups in self.patterns.items():
            for ext_type, similarity, files in groups:
                if len(files) < min_files:
                    continue

                template_struct = self.extract_common_structure(files)

                # Estimate time savings
                manual_time = 30 * len(files)  # 30 min per file
                template_time = 120 + (5 * len(files))  # 2 hours template + 5 min/file
                savings = manual_time - template_time
                savings_pct = (savings / manual_time) * 100

                suggestion = {
                    "pattern": f"{ext}_pattern_{len(suggestions)+1}",
                    "file_type": ext,
                    "num_files": len(files),
                    "similarity": similarity,
                    "files": [str(f) for f in files],
                    "template_structure": template_struct,
                    "time_savings": {
                        "manual_minutes": manual_time,
                        "with_template_minutes": template_time,
                        "savings_minutes": savings,
                        "savings_percent": savings_pct,
                    },
                    "recommended_pattern": self._recommend_pattern(ext, len(files)),
                }

                suggestions.append(suggestion)

                # Print suggestion
                print(f"\n📋 Suggestion #{len(suggestions)}")
                print(f"   File type: {ext}")
                print(f"   Similar files: {len(files)}")
                print(f"   Similarity: {similarity:.1%}")
                print(
                    f"   Stability: {template_struct.get('stability_ratio', 0):.1%} invariant"
                )
                print(f"   Time savings: {savings_pct:.0f}% ({savings} minutes)")
                print(f"   Recommended: {suggestion['recommended_pattern']}")
                print(f"   Files:")
                for f in files[:5]:  # Show first 5
                    print(f"     - {f.name}")
                if len(files) > 5:
                    print(f"     ... and {len(files)-5} more")

        print("=" * 70)

        return suggestions

    def _recommend_pattern(self, file_type: str, num_files: int) -> str:
        """Recommend which EXEC pattern to use."""
        ext_to_pattern = {
            ".py": (
                "EXEC-002 (Code Module Generator)"
                if num_files <= 10
                else "EXEC-001 (Batch File Creator)"
            ),
            ".md": "EXEC-004 (Doc Standardizer)",
            ".yaml": "EXEC-005 (Config Multiplexer)",
            ".yml": "EXEC-005 (Config Multiplexer)",
            ".json": "EXEC-007 (Schema Generator)",
        }

        return ext_to_pattern.get(file_type, "EXEC-001 (Batch File Creator)")

    def generate_template_starter(self, suggestion: Dict, output_path: Path):
        """Generate a starter template from suggestion."""
        files = [Path(f) for f in suggestion["files"]]

        # Read first file as base
        if not files:
            return

        base_content = self._read_file_safe(files[0])

        # Create template with variable markers
        template_content = f"""# TEMPLATE: {suggestion['pattern']}
# File type: {suggestion['file_type']}
# Use case: Create similar {suggestion['file_type']} files
# Similar files found: {suggestion['num_files']}
# Expected time savings: {suggestion['time_savings']['savings_percent']:.0f}%
# Recommended pattern: {suggestion['recommended_pattern']}

# VARIABLES (replace these in each instance):
# - {{variable_1}}: Description
# - {{variable_2}}: Description
# - {{variable_3}}: Description

# STRUCTURAL DECISIONS (made once):
# - Format: {suggestion['file_type']}
# - Length: ~{suggestion['template_structure']['total_lines']} lines
# - Stable sections: {suggestion['template_structure']['common_lines']} lines
# - Variable sections: {suggestion['template_structure']['variable_lines']} lines

---
# TEMPLATE CONTENT (example from {files[0].name}):

{base_content}

---
# USAGE:
# 1. Replace {{variable}} markers with actual values
# 2. Use batch_file_creator.py for bulk generation
# 3. Verify with ground truth (file exists + spot check)
"""

        output_path.write_text(template_content, encoding="utf-8")
        print(f"\n✅ Template starter saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Pattern Discovery Tool - Find repetitive work patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze directories for patterns
  python scripts/pattern_discovery.py --analyze core/ error/ aim/

  # Find Python file patterns
  python scripts/pattern_discovery.py --analyze . --pattern "*.py" --suggest

  # Generate template starters
  python scripts/pattern_discovery.py --analyze docs/ --pattern "*.md" \\
      --suggest --generate-templates templates/

  # Adjust similarity threshold
  python scripts/pattern_discovery.py --analyze . --min-similarity 0.6

Discovery Phase Automation:
  - Scans for similar files
  - Extracts common patterns
  - Suggests template opportunities
  - Estimates time savings
        """,
    )

    parser.add_argument(
        "--analyze",
        nargs="+",
        type=Path,
        help="Paths to analyze (files or directories)",
    )

    parser.add_argument(
        "--pattern", default="*", help="File pattern to match (default: *)"
    )

    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.7,
        help="Minimum similarity ratio 0.0-1.0 (default: 0.7)",
    )

    parser.add_argument(
        "--min-files",
        type=int,
        default=3,
        help="Minimum files needed to suggest template (default: 3)",
    )

    parser.add_argument(
        "--suggest", action="store_true", help="Generate template suggestions"
    )

    parser.add_argument(
        "--generate-templates", type=Path, help="Output directory for template starters"
    )

    parser.add_argument(
        "--report", type=Path, help="Output path for analysis report (JSON)"
    )

    args = parser.parse_args()

    if not args.analyze:
        parser.print_help()
        return 1

    # Discover patterns
    discoverer = PatternDiscoverer(args.analyze, args.pattern)
    discoverer.scan_files()
    discoverer.analyze_structure(args.min_similarity)

    # Generate suggestions
    suggestions = []
    if args.suggest:
        suggestions = discoverer.suggest_templates(args.min_files)

    # Generate template starters
    if args.generate_templates and suggestions:
        args.generate_templates.mkdir(parents=True, exist_ok=True)

        for suggestion in suggestions:
            template_name = f"{suggestion['pattern']}.template{suggestion['file_type']}"
            template_path = args.generate_templates / template_name
            discoverer.generate_template_starter(suggestion, template_path)

    # Generate report
    if args.report:
        report = {
            "analyzed_paths": [str(p) for p in args.analyze],
            "file_pattern": args.pattern,
            "total_files": len(discoverer.files),
            "patterns_found": len(suggestions),
            "suggestions": suggestions,
        }

        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Analysis report saved: {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
