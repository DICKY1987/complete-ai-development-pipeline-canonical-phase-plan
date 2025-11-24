#!/usr/bin/env python3
"""
Generate documentation index from all markdown files in docs/.

This script scans the docs/ directory, categorizes files, validates links,
and generates an updated DOCUMENTATION_INDEX.md file.

Usage:
    python scripts/generate_doc_index.py [--output DOCS/DOCUMENTATION_INDEX.md]
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


class DocIndexGenerator:
    """Generate documentation index from markdown files."""

    def __init__(self, docs_dir: Path, repo_root: Path):
        self.docs_dir = docs_dir
        self.repo_root = repo_root
        self.all_docs: List[Path] = []
        self.categories: Dict[str, List[Path]] = {}
        self.broken_links: List[Tuple[Path, str]] = []

    def scan_docs(self) -> None:
        """Scan docs/ directory for all markdown files."""
        print(f"Scanning {self.docs_dir}...")
        self.all_docs = sorted(self.docs_dir.rglob("*.md"))
        print(f"Found {len(self.all_docs)} markdown files")

    def categorize_docs(self) -> None:
        """Categorize documentation files by topic."""
        categories = {
            "Architecture & Design": [],
            "Implementation Summaries": [],
            "Configuration Guides": [],
            "Integrations": [],
            "Development Guides": [],
            "Reference Documentation": [],
            "Planning & Roadmap": [],
            "Migration & Refactoring": [],
            "Miscellaneous": []
        }

        # Define patterns for categorization
        patterns = {
            "Architecture & Design": [
                r"ARCHITECTURE", r"DIAGRAM", r"VISUAL", r"state_machine",
                r"HYBRID_WORKFLOW", r"file-lifecycle"
            ],
            "Implementation Summaries": [
                r"IMPLEMENTATION_SUMMARY", r"_COMPLETE\.md$", r"PROGRESS",
                r"STATUS\.md$", r"FINAL_REPORT", r"FINAL_SUMMARY"
            ],
            "Configuration Guides": [
                r"CONFIGURATION_GUIDE", r"COORDINATION_GUIDE",
                r"workstream_authoring", r"CONTRACT\.md$"
            ],
            "Integrations": [
                r"AIM_", r"UET_", r"CCPM", r"openspec", r"aider_contract",
                r"Project_Management_docs"
            ],
            "Development Guides": [
                r"QUICK_REFERENCE", r"DEVELOPMENT_GUIDE", r"GUI_DEVELOPMENT",
                r"plugin-quick-reference", r"plugin-ecosystem"
            ],
            "Reference Documentation": [
                r"reference/", r"HARDCODED_PATH", r"CLI_TOOL",
                r"prompting/", r"guidelines/", r"forensics/"
            ],
            "Planning & Roadmap": [
                r"PHASE_PLAN", r"PHASE_ROADMAP", r"PHASE_K_",
                r"planning/", r"phase-github"
            ],
            "Migration & Refactoring": [
                r"CI_PATH_STANDARDS", r"DEPRECATION", r"MIGRATION",
                r"ARCHIVE_", r"LEGACY", r"REFACTOR", r"CONSOLIDATION",
                r"PATH_ABSTRACTION", r"ZERO_TOUCH"
            ]
        }

        for doc in self.all_docs:
            relative_path = doc.relative_to(self.docs_dir)
            doc_name = str(relative_path)
            categorized = False

            for category, pattern_list in patterns.items():
                if any(re.search(pattern, doc_name, re.IGNORECASE) for pattern in pattern_list):
                    categories[category].append(doc)
                    categorized = True
                    break

            if not categorized:
                categories["Miscellaneous"].append(doc)

        self.categories = {k: v for k, v in categories.items() if v}

    def validate_links(self) -> None:
        """Validate internal markdown links."""
        print("Validating internal links...")
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+\.md[^\)]*)\)')

        for doc in self.all_docs:
            try:
                content = doc.read_text(encoding='utf-8')
                for match in link_pattern.finditer(content):
                    link_text = match.group(1)
                    link_path = match.group(2)

                    # Skip external links
                    if link_path.startswith(('http://', 'https://', 'mailto:')):
                        continue

                    # Remove anchors
                    link_path = link_path.split('#')[0]
                    if not link_path:
                        continue

                    # Resolve relative path
                    target = (doc.parent / link_path).resolve()

                    if not target.exists():
                        self.broken_links.append((doc, link_path))

            except Exception as e:
                print(f"Warning: Could not read {doc}: {e}")

        if self.broken_links:
            print(f"Found {len(self.broken_links)} broken links")
        else:
            print("All links valid!")

    def generate_index(self, output_path: Path) -> None:
        """Generate the documentation index markdown file."""
        print(f"Generating index at {output_path}...")

        lines = [
            "# Documentation Index",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  ",
            "**Purpose**: Central navigation hub for all pipeline documentation  ",
            "**Auto-Generated**: By `scripts/generate_doc_index.py`",
            "",
            "> **Quick Links**: [Architecture](#architecture--design) | "
            "[Implementation](#implementation-summaries) | "
            "[Configuration](#configuration-guides) | "
            "[Integrations](#integrations) | "
            "[Development](#development-guides)",
            "",
            "---",
            "",
            "## 📋 Quick Reference",
            "",
            "### Common Tasks",
            "",
            "| Task | Documentation | Quick Command |",
            "|------|--------------|---------------|",
            "| **Get Started** | [README.md](../README.md) | `pwsh ./scripts/bootstrap.ps1` |",
            "| **Navigate Repository** | [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) | - |",
            "| **Coding Guidelines** | [AGENTS.md](../AGENTS.md) | - |",
            "| **Run Tests** | [scripts/test.ps1](../scripts/test.ps1) | `pwsh ./scripts/test.ps1` |",
            "| **Validate Workstreams** | [scripts/validate_workstreams.py](../scripts/validate_workstreams.py) | `python scripts/validate_workstreams.py` |",
            "| **Find Implementation** | [IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md) | - |",
            "",
            "### Term Lookup",
            "",
            "For specialized term definitions and implementation locations, see:",
            "- **[IMPLEMENTATION_LOCATIONS.md](IMPLEMENTATION_LOCATIONS.md)** - Every term mapped to file:line",
            "- **[TERM_RELATIONSHIPS.md](TERM_RELATIONSHIPS.md)** (planned K-4) - Term hierarchy and dependencies",
            "",
            "---",
            ""
        ]

        # Add categories
        for category, docs in self.categories.items():
            # Convert category name to anchor
            anchor = category.lower().replace(" ", "-").replace("&", "")

            lines.append(f"## {category}")
            lines.append("")

            # Sort docs by name within category
            sorted_docs = sorted(docs, key=lambda d: d.name.lower())

            lines.append("| Document | Purpose |")
            lines.append("|----------|---------|")

            for doc in sorted_docs:
                relative_path = doc.relative_to(self.docs_dir)
                doc_link = str(relative_path).replace('\\', '/')

                # Try to extract purpose from first paragraph
                purpose = self._extract_purpose(doc)

                lines.append(f"| [{doc.name}]({doc_link}) | {purpose} |")

            lines.append("")
            lines.append("---")
            lines.append("")

        # Add validation section
        if self.broken_links:
            lines.append("## ⚠️ Validation Warnings")
            lines.append("")
            lines.append("The following broken links were detected:")
            lines.append("")

            for doc, link in self.broken_links:
                relative_doc = doc.relative_to(self.docs_dir)
                lines.append(f"- `{relative_doc}` → `{link}`")

            lines.append("")
            lines.append("---")
            lines.append("")

        # Add statistics
        lines.append("## 📊 Documentation Statistics")
        lines.append("")
        lines.append(f"**Total Documents**: {len(self.all_docs)}  ")
        lines.append(f"**Categories**: {len(self.categories)}  ")
        lines.append(f"**Broken Links**: {len(self.broken_links)}  ")
        lines.append("")

        for category, docs in self.categories.items():
            lines.append(f"- **{category}**: {len(docs)} documents")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 🔄 Maintenance")
        lines.append("")
        lines.append("**Auto-Generated**: This file is automatically generated. Do not edit manually.")
        lines.append("")
        lines.append("**Update Commands**:")
        lines.append("```bash")
        lines.append("# Regenerate documentation index")
        lines.append("python scripts/generate_doc_index.py")
        lines.append("")
        lines.append("# Regenerate with custom output")
        lines.append("python scripts/generate_doc_index.py --output docs/DOCUMENTATION_INDEX.md")
        lines.append("```")
        lines.append("")
        lines.append("**Update Schedule**:")
        lines.append("- **On PR**: Automatically regenerated via CI")
        lines.append("- **Manual**: Run script when adding new documentation")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**Last Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
        lines.append("**Generator**: `scripts/generate_doc_index.py`  ")
        lines.append("")

        # Write output
        output_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"Index generated successfully: {output_path}")

    def _extract_purpose(self, doc: Path) -> str:
        """Extract purpose from document header or first paragraph."""
        try:
            content = doc.read_text(encoding='utf-8')

            # Look for Purpose: metadata
            purpose_match = re.search(r'[*_]*Purpose[*_]*:\s*(.+)', content, re.IGNORECASE)
            if purpose_match:
                return purpose_match.group(1).strip()

            # Look for first paragraph after H1
            h1_pattern = re.compile(r'^# .+$', re.MULTILINE)
            h1_match = h1_pattern.search(content)
            if h1_match:
                after_h1 = content[h1_match.end():].strip()
                # Get first non-empty paragraph
                paragraphs = [p.strip() for p in after_h1.split('\n\n') if p.strip() and not p.strip().startswith('#')]
                if paragraphs:
                    first_para = paragraphs[0].replace('\n', ' ')
                    # Truncate if too long
                    if len(first_para) > 100:
                        first_para = first_para[:97] + '...'
                    return first_para

            return "-"

        except Exception:
            return "-"

    def run(self, output_path: Path) -> int:
        """Run the full index generation process."""
        self.scan_docs()
        self.categorize_docs()
        self.validate_links()
        self.generate_index(output_path)

        # Return exit code
        return 1 if self.broken_links else 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation index from docs/ directory"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('docs/DOCUMENTATION_INDEX_GENERATED.md'),
        help='Output file path (default: docs/DOCUMENTATION_INDEX_GENERATED.md)'
    )
    parser.add_argument(
        '--docs-dir',
        type=Path,
        default=Path('docs'),
        help='Documentation directory to scan (default: docs/)'
    )
    parser.add_argument(
        '--fail-on-broken-links',
        action='store_true',
        help='Exit with error code if broken links are found'
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent.resolve()
    docs_dir = (repo_root / args.docs_dir).resolve()
    output_path = (repo_root / args.output).resolve()

    if not docs_dir.exists():
        print(f"Error: Documentation directory not found: {docs_dir}")
        return 1

    # Run generator
    generator = DocIndexGenerator(docs_dir, repo_root)
    exit_code = generator.run(output_path)

    print("\n✅ Documentation index generation complete!")
    print(f"Output: {output_path}")

    if generator.broken_links:
        print(f"\n⚠️  Warning: {len(generator.broken_links)} broken links detected")
        if args.fail_on_broken_links:
            return exit_code

    return 0


if __name__ == '__main__':
    exit(main())
