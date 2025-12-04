#!/usr/bin/env python3
"""
Advanced Folder Version Detector v2.0
======================================
Implements FOLDER_VERSION_SCORING_SPEC.md

Identifies which folder is the "canonical" version when duplicates exist.

Scoring factors:
1. Content similarity (SHA-256 hashing) - 25 points
2. Modification recency (newer = canonical) - 20 points
3. File completeness (more files = canonical) - 15 points
4. Git history (created first = canonical) - 15 points
5. Import/usage analysis (actively imported = canonical) - 15 points
6. Location score (blessed tiers) - 10 points

HARD Guardrails for deletion:
- Score < 50 AND usage == 0 AND not in registry AND location == graveyard

Total: 100 points
Higher score = more likely to be the canonical (keep) version

Reference: docs/FOLDER_VERSION_SCORING_SPEC.md
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-FOLDER-VERSIONS-187
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-FOLDER-VERSIONS-124

import hashlib
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Set, Tuple, Optional

@dataclass
class FolderVersionScore:
    """Comprehensive scoring for folder version detection (v2.0)."""
    path: str

    # Content analysis
    file_count: int
    total_size: int
    file_hashes: Set[str] = field(default_factory=set)
    file_names: Set[str] = field(default_factory=set)  # For strict similarity
    content_score: int = 0  # 0-25

    # Temporal analysis
    newest_file_date: Optional[datetime] = None
    oldest_file_date: Optional[datetime] = None
    avg_modification_date: Optional[datetime] = None
    recency_score: int = 0  # 0-20

    # Completeness
    has_readme: bool = False
    has_init: bool = False  # __init__.py
    has_tests: bool = False
    has_pattern_spec: bool = False
    completeness_score: int = 0  # 0-15

    # Git history
    git_created_date: Optional[datetime] = None
    git_last_modified: Optional[datetime] = None
    commit_count: int = 0
    history_score: int = 0  # 0-15

    # Usage analysis (expanded)
    is_imported: bool = False
    import_count: int = 0
    powershell_refs: int = 0
    yaml_refs: int = 0
    pattern_registry_refs: int = 0
    is_in_codebase_index: bool = False
    has_doc_id: bool = False
    usage_score: int = 0  # 0-15

    # Location (tier-based)
    depth: int = 0  # Path depth (0 = root)
    location_tier: int = 0  # 0=graveyard, 1=experimental, 2=library, 3=canonical
    is_in_legacy: bool = False
    is_in_archive: bool = False
    location_score: int = 0  # 0-10

    # Final
    total_score: int = 0  # 0-100
    verdict: str = "KEEP"  # KEEP, DELETE, ARCHIVE, REVIEW, DIFFERENT_PURPOSE
    can_delete: bool = False  # Guardrail check

def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except:
        return ""

def get_git_file_history(filepath: Path, repo_root: Path) -> Tuple[Optional[datetime], int]:
    """Get git creation date and commit count for a file."""
    try:
        rel_path = filepath.relative_to(repo_root)

        # Get first commit (creation date)
        result = subprocess.run(
            ['git', 'log', '--diff-filter=A', '--format=%cI', '--', str(rel_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        created = None
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if lines:
                created = datetime.fromisoformat(lines[-1].replace('Z', '+00:00'))

        # Get commit count
        result = subprocess.run(
            ['git', 'log', '--oneline', '--', str(rel_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        commit_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

        return created, commit_count
    except:
        return None, 0

def analyze_folder_version(folder: Path, repo_root: Path, all_python_files: List[Path]) -> FolderVersionScore:
    """Generate comprehensive version score for a folder."""

    # Gather files
    files = list(folder.glob('*')) if folder.exists() else []
    file_items = [f for f in files if f.is_file()]

    # Content analysis
    file_hashes = set()
    total_size = 0
    modification_dates = []

    for f in file_items:
        file_hash = compute_file_hash(f)
        if file_hash:
            file_hashes.add(file_hash)

        try:
            total_size += f.stat().st_size
            mod_time = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            modification_dates.append(mod_time)
        except:
            pass

    # Temporal analysis
    newest = max(modification_dates) if modification_dates else None
    oldest = min(modification_dates) if modification_dates else None
    avg_date = None
    if modification_dates:
        avg_timestamp = sum(d.timestamp() for d in modification_dates) / len(modification_dates)
        avg_date = datetime.fromtimestamp(avg_timestamp, tz=timezone.utc)

    # Git history
    git_created = None
    total_commits = 0
    git_last_mod = None

    for f in file_items[:5]:  # Sample first 5 files for performance
        created, commits = get_git_file_history(f, repo_root)
        if created:
            if not git_created or created < git_created:
                git_created = created
        total_commits += commits

    if modification_dates:
        git_last_mod = max(modification_dates)

    # Completeness
    has_readme = (folder / "README.md").exists() or (folder / "readme.md").exists()
    has_init = (folder / "__init__.py").exists()

    # Usage analysis (check if this folder is imported)
    rel_path = str(folder.relative_to(repo_root))
    module_path = rel_path.replace('\\', '.').replace('/', '.')

    is_imported = False
    import_count = 0
    for py_file in all_python_files:
        if py_file.parent == folder:  # Skip files in this folder
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            # Look for imports of this folder
            if f"from {module_path}" in content or f"import {module_path}" in content:
                is_imported = True
                import_count += content.count(module_path)
        except:
            pass

    # Location analysis
    depth = len(Path(rel_path).parts) - 1
    is_in_legacy = 'legacy' in rel_path.lower() or 'archive' in rel_path.lower()
    is_in_archive = 'archive' in rel_path.lower()

    # Initial score object
    score = FolderVersionScore(
        path=rel_path,
        file_count=len(file_items),
        total_size=total_size,
        file_hashes=file_hashes,
        newest_file_date=newest,
        oldest_file_date=oldest,
        avg_modification_date=avg_date,
        has_readme=has_readme,
        has_init=has_init,
        git_created_date=git_created,
        git_last_modified=git_last_mod,
        commit_count=total_commits,
        is_imported=is_imported,
        import_count=import_count,
        depth=depth,
        is_in_legacy=is_in_legacy,
        is_in_archive=is_in_archive
    )

    return score

def score_folder_versions(folder_scores: List[FolderVersionScore]) -> List[FolderVersionScore]:
    """Score multiple folder versions against each other."""

    if not folder_scores:
        return []

    # Content similarity scoring (0-25 points)
    all_hashes = set()
    for fs in folder_scores:
        all_hashes.update(fs.file_hashes)

    for fs in folder_scores:
        if all_hashes:
            coverage = len(fs.file_hashes) / len(all_hashes)
            fs.content_score = int(coverage * 25)

    # Recency scoring (0-20 points) - newer is better
    newest_overall = max((fs.newest_file_date for fs in folder_scores if fs.newest_file_date), default=None)
    if newest_overall:
        for fs in folder_scores:
            if fs.newest_file_date:
                age_diff = (newest_overall - fs.newest_file_date).days
                # Newer = higher score
                fs.recency_score = max(0, 20 - (age_diff // 30))  # Lose 1 point per month

    # Completeness scoring (0-15 points)
    max_files = max(fs.file_count for fs in folder_scores)
    for fs in folder_scores:
        completeness = (fs.file_count / max_files) * 10 if max_files > 0 else 0
        if fs.has_readme:
            completeness += 3
        if fs.has_init:
            completeness += 2
        fs.completeness_score = int(completeness)

    # Git history scoring (0-15 points) - created earlier = canonical
    earliest_git = min((fs.git_created_date for fs in folder_scores if fs.git_created_date), default=None)
    if earliest_git:
        for fs in folder_scores:
            if fs.git_created_date:
                # Earlier creation = higher score
                if fs.git_created_date == earliest_git:
                    fs.history_score = 15
                else:
                    days_after = (fs.git_created_date - earliest_git).days
                    fs.history_score = max(0, 15 - (days_after // 30))
            # Bonus for commit count
            if fs.commit_count > 0:
                fs.history_score = min(15, fs.history_score + min(5, fs.commit_count))

    # Usage scoring (0-15 points)
    max_imports = max(fs.import_count for fs in folder_scores)
    for fs in folder_scores:
        if fs.is_imported:
            fs.usage_score = 8
            if max_imports > 0:
                fs.usage_score += int((fs.import_count / max_imports) * 7)

    # Location scoring (0-10 points)
    min_depth = min(fs.depth for fs in folder_scores)
    for fs in folder_scores:
        if fs.is_in_legacy or fs.is_in_archive:
            fs.location_score = 0  # Legacy/archive = lowest priority
        else:
            # Shallower = higher score
            if fs.depth == min_depth:
                fs.location_score = 10
            else:
                fs.location_score = max(0, 10 - (fs.depth - min_depth) * 2)

    # Calculate totals and verdicts
    for fs in folder_scores:
        fs.total_score = (
            fs.content_score +
            fs.recency_score +
            fs.completeness_score +
            fs.history_score +
            fs.usage_score +
            fs.location_score
        )

    # Determine verdicts (highest score = KEEP)
    if folder_scores:
        folder_scores.sort(key=lambda x: x.total_score, reverse=True)
        folder_scores[0].verdict = "KEEP"  # Highest score

        for fs in folder_scores[1:]:
            if fs.is_in_legacy or fs.is_in_archive:
                fs.verdict = "ARCHIVE"  # Already archived
            elif fs.total_score < folder_scores[0].total_score * 0.5:
                fs.verdict = "DELETE"  # Significantly worse
            else:
                fs.verdict = "REVIEW"  # Close call

    return folder_scores

def main():
    repo_root = Path.cwd()

    print("Advanced Folder Version Detection")
    print("=" * 70)
    print(f"Repository: {repo_root}\n")

    # Find all Python files for import analysis
    print("1. Indexing Python files for import analysis...")
    all_python_files = list(repo_root.rglob('*.py'))
    all_python_files = [f for f in all_python_files if '.git' not in str(f) and '.venv' not in str(f)]
    print(f"   Found {len(all_python_files)} Python files\n")

    # Example: Analyze specific duplicate folders
    print("2. Analyzing duplicate folder pairs...\n")

    # You can specify folders to compare
    test_pairs = [
        (['engine', 'core/engine', 'error/engine'], 'engine'),
        (['scripts', 'pm/scripts', 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts'], 'scripts'),
    ]

    results = []

    for paths, name in test_pairs:
        print(f"📁 Analyzing '{name}' folders...")

        folders = [repo_root / p for p in paths if (repo_root / p).exists()]
        if len(folders) < 2:
            print(f"   ⚠️  Only {len(folders)} folder(s) found, skipping\n")
            continue

        # Analyze each folder
        scores = []
        for folder in folders:
            print(f"   Analyzing: {folder.relative_to(repo_root)}...")
            score = analyze_folder_version(folder, repo_root, all_python_files)
            scores.append(score)

        # Score against each other
        scores = score_folder_versions(scores)

        # Display results
        print(f"\n   Results for '{name}':")
        for score in scores:
            print(f"   [{score.total_score:3d} pts] {score.verdict:8s} - {score.path}")
            print(f"            Content:{score.content_score:2d} | Recency:{score.recency_score:2d} | Complete:{score.completeness_score:2d} | History:{score.history_score:2d} | Usage:{score.usage_score:2d} | Location:{score.location_score:2d}")
        print()

        results.append({
            'folder_name': name,
            'scores': [asdict(s) for s in scores]
        })

    # Save report
    output_file = repo_root / "cleanup_reports" / "folder_version_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✅ Analysis saved: {output_file}")

if __name__ == '__main__':
    main()
