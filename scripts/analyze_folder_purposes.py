#!/usr/bin/env python3
"""
Folder Purpose Analyzer
=======================
Analyzes duplicate folder names by PURPOSE, not just name matching.

Uses multi-factor scoring:
1. Content similarity (file hashing)
2. Structural similarity (file types, counts)
3. Naming patterns (README presence, file prefixes)
4. Scope analysis (tool-specific vs. global)

Output: Recommendations for RENAME, CONSOLIDATE, or KEEP
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-FOLDER-PURPOSES-186
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-FOLDER-PURPOSES-123

import json
import hashlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Tuple


@dataclass
class FolderProfile:
    """Profile of a folder's purpose and contents."""

    path: str
    file_count: int
    py_count: int
    ps1_count: int
    sh_count: int
    md_count: int
    yaml_count: int
    json_count: int
    has_readme: bool
    file_hashes: Set[str]
    file_names: List[str]
    avg_file_size: int
    total_size: int
    scope: str  # 'global', 'tool-specific', 'module-specific', 'legacy'

    def similarity_score(self, other: "FolderProfile") -> int:
        """Calculate similarity score (0-100) with another folder."""
        score = 0

        # Content hash overlap (most important)
        if self.file_hashes and other.file_hashes:
            overlap = len(self.file_hashes & other.file_hashes)
            union = len(self.file_hashes | other.file_hashes)
            if union > 0:
                score += int((overlap / union) * 40)

        # File type similarity
        type_diff = (
            abs(self.py_count - other.py_count)
            + abs(self.ps1_count - other.ps1_count)
            + abs(self.sh_count - other.sh_count)
        )
        type_similarity = max(0, 30 - (type_diff * 3))
        score += type_similarity

        # Size similarity
        if self.file_count > 0 and other.file_count > 0:
            size_ratio = min(self.file_count, other.file_count) / max(
                self.file_count, other.file_count
            )
            score += int(size_ratio * 20)

        # Name overlap
        name_overlap = len(set(self.file_names) & set(other.file_names))
        if self.file_count > 0:
            score += int((name_overlap / self.file_count) * 10)

        return min(100, score)


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    try:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except:
        return ""


def determine_scope(folder_path: str) -> str:
    """Determine folder scope from path."""
    path_lower = folder_path.lower()

    # Legacy/archived
    if "legacy" in path_lower or "archive" in path_lower or "dicky1987" in path_lower:
        return "legacy"

    # Tool-specific (subdirectory of a known tool)
    if any(
        tool in path_lower
        for tool in ["ai-logs-analyzer", "glossary", "aim", "aider", "ccpm"]
    ):
        return "tool-specific"

    # Module-specific (subdirectory of a module)
    if any(
        mod in path_lower
        for mod in ["universal_execution_templates", "core/", "engine/", "error/"]
    ):
        return "module-specific"

    # Global (top-level)
    if path_lower.count("\\") <= 1 or path_lower.count("/") <= 1:
        return "global"

    return "unknown"


def profile_folder(folder_path: Path, base_path: Path) -> FolderProfile:
    """Create a profile of a folder."""
    files = list(folder_path.glob("*")) if folder_path.exists() else []
    file_items = [f for f in files if f.is_file()]

    # Count file types
    py_count = sum(1 for f in file_items if f.suffix == ".py")
    ps1_count = sum(1 for f in file_items if f.suffix == ".ps1")
    sh_count = sum(1 for f in file_items if f.suffix == ".sh")
    md_count = sum(1 for f in file_items if f.suffix == ".md")
    yaml_count = sum(1 for f in file_items if f.suffix in [".yaml", ".yml"])
    json_count = sum(1 for f in file_items if f.suffix == ".json")

    # Hash files
    file_hashes = set()
    total_size = 0
    for f in file_items:
        file_hash = compute_file_hash(f)
        if file_hash:
            file_hashes.add(file_hash)
        try:
            total_size += f.stat().st_size
        except:
            pass

    avg_size = total_size // len(file_items) if file_items else 0

    rel_path = str(folder_path.relative_to(base_path))

    return FolderProfile(
        path=rel_path,
        file_count=len(file_items),
        py_count=py_count,
        ps1_count=ps1_count,
        sh_count=sh_count,
        md_count=md_count,
        yaml_count=yaml_count,
        json_count=json_count,
        has_readme=(folder_path / "README.md").exists(),
        file_hashes=file_hashes,
        file_names=[f.name for f in file_items],
        avg_file_size=avg_size,
        total_size=total_size,
        scope=determine_scope(rel_path),
    )


def analyze_duplicate_folders(repo_root: Path) -> Dict:
    """Analyze all duplicate folder names."""
    # Find all folders
    all_folders = defaultdict(list)

    for folder in repo_root.rglob("*"):
        if not folder.is_dir():
            continue

        # Skip excluded directories
        if any(
            excl in str(folder)
            for excl in [".git", ".worktrees", ".venv", "__pycache__", "node_modules"]
        ):
            continue

        # Normalize folder name (remove leading dots)
        norm_name = folder.name.lstrip(".")
        all_folders[norm_name].append(folder)

    # Analyze duplicates
    results = {
        "total_folder_names": len(all_folders),
        "duplicate_names": 0,
        "analysis": [],
    }

    for name, folders in all_folders.items():
        if len(folders) <= 1:
            continue

        results["duplicate_names"] += 1

        # Profile each folder
        profiles = [profile_folder(f, repo_root) for f in folders]

        # Calculate similarity matrix
        similarities = []
        for i, p1 in enumerate(profiles):
            for j, p2 in enumerate(profiles[i + 1 :], start=i + 1):
                sim_score = p1.similarity_score(p2)
                if sim_score > 50:  # Only report if >50% similar
                    similarities.append(
                        {
                            "folder1": p1.path,
                            "folder2": p2.path,
                            "similarity": sim_score,
                        }
                    )

        # Determine recommendation
        recommendation = "KEEP"  # Default: keep all
        reason = []

        # Check for true duplicates (>80% similar)
        high_similarity = [s for s in similarities if s["similarity"] > 80]
        if high_similarity:
            recommendation = "CONSOLIDATE"
            reason.append(f"{len(high_similarity)} pairs with >80% similarity")

        # Check for different scopes (global vs tool-specific)
        scopes = set(p.scope for p in profiles)
        if scopes == {"global", "tool-specific"} or scopes == {
            "global",
            "module-specific",
        }:
            recommendation = "RENAME"
            reason.append("Mixed scopes - rename for clarity")

        # Check for legacy folders
        if "legacy" in scopes:
            recommendation = "ARCHIVE"
            reason.append("Contains legacy folders")

        results["analysis"].append(
            {
                "folder_name": name,
                "occurrences": len(folders),
                "profiles": [asdict(p) for p in profiles],
                "similarities": similarities,
                "recommendation": recommendation,
                "reason": "; ".join(reason) if reason else "Different purposes",
            }
        )

    return results


def main():
    repo_root = Path.cwd()

    print("Analyzing duplicate folder names by PURPOSE...")
    print(f"Repository: {repo_root}\n")

    results = analyze_duplicate_folders(repo_root)

    # Save full report
    output_file = repo_root / "cleanup_reports" / "folder_purpose_analysis.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✅ Analysis complete!")
    print(f"   Total folder names: {results['total_folder_names']}")
    print(f"   Duplicate names: {results['duplicate_names']}")
    print(f"\n📊 Summary by recommendation:")

    # Group by recommendation
    by_rec = defaultdict(list)
    for item in results["analysis"]:
        by_rec[item["recommendation"]].append(item["folder_name"])

    for rec, names in sorted(by_rec.items()):
        print(f"   {rec}: {len(names)} folders")
        for name in names[:5]:
            print(f"      - {name}")
        if len(names) > 5:
            print(f"      ... and {len(names) - 5} more")

    print(f"\n📁 Full report: {output_file}")


if __name__ == "__main__":
    main()
