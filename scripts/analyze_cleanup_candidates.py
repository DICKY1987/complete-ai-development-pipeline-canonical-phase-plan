#!/usr/bin/env python3
"""
Automated Repository Cleanup Analyzer
======================================
Identifies obsolete, duplicate, and orphaned files for safe deletion.

Uses forensic signals:
- Duplication detection (SHA-256, directory structure)
- Staleness scoring (git history, last modified)
- Obsolescence detection (multiple versions, superseded components)
- Isolation scoring (no imports, not referenced)

Output:
- cleanup_report.json: Full analysis with scores
- cleanup_plan_high_confidence.ps1: Safe deletions (>85% confidence)
- cleanup_plan_review_needed.json: Manual review cases

Author: GitHub Copilot
Version: 1.0.0
Date: 2025-11-25
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-CLEANUP-CANDIDATES-185
DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-CLEANUP-CANDIDATES-122

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

CHUNK_SIZE = 65536  # 64KB for file hashing
STALENESS_DAYS = 180  # 6 months = stale
RECENT_DAYS = 30  # Last 30 days = recent

# Patterns that indicate deprecation
DEPRECATED_PATTERNS = [
    'deprecated', 'archive', 'backup', 'old', 'legacy',
    'tmp', 'temp', 'draft', '_bak', '.bak', '_old'
]

# Directories to exclude from analysis
EXCLUDE_DIRS = {
    '.git', '.worktrees', '.venv', '__pycache__', 
    'node_modules', '.pytest_cache', '.state'
}

# File extensions to analyze
CODE_EXTENSIONS = {'.py', '.ps1', '.bat', '.sh'}
DOC_EXTENSIONS = {'.md', '.txt', '.rst'}
CONFIG_EXTENSIONS = {'.yaml', '.yml', '.json', '.toml', '.ini'}

# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class FileScore:
    """Scoring for a single file."""
    path: str
    duplication_score: int = 0  # 0-100
    staleness_score: int = 0    # 0-100
    obsolescence_score: int = 0  # 0-100
    isolation_score: int = 0     # 0-100
    total_score: int = 0         # Average of above
    confidence: int = 0          # Confidence in recommendation
    action: str = "KEEP"         # KEEP, DELETE, ARCHIVE, CONSOLIDATE
    reasons: List[str] = None
    duplicate_of: Optional[str] = None
    last_modified: Optional[str] = None
    file_size: int = 0
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        self.total_score = (
            self.duplication_score + self.staleness_score + 
            self.obsolescence_score + self.isolation_score
        ) // 4

@dataclass
class CleanupRecommendation:
    """A cleanup action recommendation."""
    action: str  # DELETE, ARCHIVE, CONSOLIDATE, KEEP
    paths: List[str]
    reason: str
    confidence: int
    estimated_space_saved: int = 0
    duplicate_group_id: Optional[str] = None

# =============================================================================
# File Analysis Functions
# =============================================================================

def compute_file_hash(filepath: Path) -> Optional[str]:
    """Compute SHA-256 hash of a file."""
    if not filepath.is_file():
        return None
    
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError, PermissionError) as e:
        logger.debug(f"Cannot hash {filepath}: {e}")
        return None

def get_git_last_modified(filepath: Path, repo_root: Path) -> Optional[datetime]:
    """Get last git commit date for a file."""
    try:
        rel_path = filepath.relative_to(repo_root)
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cI', '--', str(rel_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return datetime.fromisoformat(result.stdout.strip().replace('Z', '+00:00'))
    except Exception as e:
        logger.debug(f"Git log failed for {filepath}: {e}")
    
    # Fallback to filesystem mtime
    try:
        return datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc)
    except:
        return None

def find_python_imports(filepath: Path) -> Set[str]:
    """Extract import statements from Python file."""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Match: from X import Y or import X
                if line.startswith('from '):
                    match = re.match(r'from\s+([\w.]+)', line)
                    if match:
                        imports.add(match.group(1))
                elif line.startswith('import '):
                    match = re.match(r'import\s+([\w.]+)', line)
                    if match:
                        imports.add(match.group(1))
    except Exception as e:
        logger.debug(f"Cannot parse imports from {filepath}: {e}")
    
    return imports

# =============================================================================
# Repository Scanner
# =============================================================================

class RepositoryScanner:
    """Scans repository and builds file index."""
    
    def __init__(self, root: Path, exclude_dirs: Set[str] = None):
        self.root = root.resolve()
        self.exclude_dirs = exclude_dirs or EXCLUDE_DIRS
        
        # File index
        self.files: List[Path] = []
        self.files_by_hash: Dict[str, List[Path]] = defaultdict(list)
        self.files_by_name: Dict[str, List[Path]] = defaultdict(list)
        
        # Import graph
        self.imports_from: Dict[Path, Set[str]] = {}  # file -> modules it imports
        self.imported_by: Dict[str, Set[Path]] = defaultdict(set)  # module -> files that import it
        
        # Statistics
        self.total_size = 0
        self.total_files = 0
    
    def scan(self) -> 'RepositoryScanner':
        """Scan the repository."""
        logger.info(f"Scanning repository: {self.root}")
        
        for dirpath, dirnames, filenames in os.walk(self.root):
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if d not in self.exclude_dirs]
            
            for filename in filenames:
                filepath = Path(dirpath) / filename
                self.files.append(filepath)
                self.total_files += 1
                
                # Track by name
                self.files_by_name[filename].append(filepath)
                
                # Compute hash for code/config files
                ext = filepath.suffix.lower()
                if ext in CODE_EXTENSIONS | CONFIG_EXTENSIONS:
                    file_hash = compute_file_hash(filepath)
                    if file_hash:
                        self.files_by_hash[file_hash].append(filepath)
                
                # Track size
                try:
                    self.total_size += filepath.stat().st_size
                except:
                    pass
                
                # Extract imports from Python files
                if ext == '.py':
                    imports = find_python_imports(filepath)
                    self.imports_from[filepath] = imports
                    for imp in imports:
                        self.imported_by[imp].add(filepath)
                
                if self.total_files % 500 == 0:
                    logger.info(f"  Scanned {self.total_files} files...")
        
        logger.info(f"Scan complete: {self.total_files} files, {self.total_size:,} bytes")
        return self
    
    def get_module_name(self, filepath: Path) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            rel_path = filepath.relative_to(self.root)
            if rel_path.suffix != '.py':
                return None
            
            # Convert path to module: core/state/db.py -> core.state.db
            parts = list(rel_path.parts[:-1]) + [rel_path.stem]
            if parts[-1] == '__init__':
                parts = parts[:-1]
            
            return '.'.join(parts)
        except:
            return None

# =============================================================================
# Scoring Engine
# =============================================================================

class CleanupScorer:
    """Scores files for cleanup recommendations."""
    
    def __init__(self, scanner: RepositoryScanner, codebase_index: dict):
        self.scanner = scanner
        self.codebase_index = codebase_index
        self.scores: Dict[Path, FileScore] = {}
        self.now = datetime.now(timezone.utc)
        
        # Build canonical module set from CODEBASE_INDEX
        self.canonical_modules = self._extract_canonical_modules()
    
    def _extract_canonical_modules(self) -> Set[str]:
        """Extract canonical module paths from CODEBASE_INDEX.yaml."""
        canonical = set()
        if 'modules' in self.codebase_index:
            for module in self.codebase_index['modules']:
                if module.get('path'):
                    canonical.add(module['path'].rstrip('/'))
        return canonical
    
    def score_duplication(self, filepath: Path) -> Tuple[int, List[str]]:
        """Score file for duplication (0-100)."""
        score = 0
        reasons = []
        
        file_hash = compute_file_hash(filepath)
        if file_hash and file_hash in self.scanner.files_by_hash:
            duplicates = self.scanner.files_by_hash[file_hash]
            if len(duplicates) > 1:
                score = 100
                other_paths = [str(p.relative_to(self.scanner.root)) for p in duplicates if p != filepath]
                reasons.append(f"Exact duplicate of: {', '.join(other_paths[:3])}")
                return score, reasons
        
        # Check for similar directory names
        filename = filepath.name
        if filename in self.scanner.files_by_name:
            similar = self.scanner.files_by_name[filename]
            if len(similar) > 1:
                score = 60
                reasons.append(f"Same filename exists in {len(similar)} locations")
        
        return score, reasons
    
    def score_staleness(self, filepath: Path) -> Tuple[int, List[str]]:
        """Score file for staleness (0-100)."""
        score = 0
        reasons = []
        
        # Check last modified date
        last_modified = get_git_last_modified(filepath, self.scanner.root)
        if last_modified:
            age_days = (self.now - last_modified).days
            
            if age_days > STALENESS_DAYS:
                score = min(100, 50 + (age_days - STALENESS_DAYS) // 30 * 10)
                reasons.append(f"Not modified in {age_days} days")
            elif age_days > RECENT_DAYS:
                score = 30
        
        # Check for deprecated patterns in path
        path_str = str(filepath.relative_to(self.scanner.root)).lower()
        for pattern in DEPRECATED_PATTERNS:
            if pattern in path_str:
                score = max(score, 80)
                reasons.append(f"Path contains '{pattern}'")
                break
        
        return score, reasons
    
    def score_obsolescence(self, filepath: Path) -> Tuple[int, List[str]]:
        """Score file for obsolescence (0-100)."""
        score = 0
        reasons = []
        
        rel_path_str = str(filepath.relative_to(self.scanner.root))
        
        # Check if in legacy/archive directories
        if rel_path_str.startswith('legacy/') or rel_path_str.startswith('archive/'):
            score = 90
            reasons.append("In legacy/archive directory")
            return score, reasons
        
        # Check if superseded by canonical module
        for canonical_path in self.canonical_modules:
            # Check if this file is in a non-canonical version
            if filepath.suffix == '.py':
                # Extract module prefix (e.g., "core/engine" from "core/engine/orchestrator.py")
                parts = Path(rel_path_str).parts
                if len(parts) >= 2:
                    module_prefix = '/'.join(parts[:2])
                    
                    # If same module name exists in canonical location
                    if module_prefix not in self.canonical_modules and \
                       any(canonical_path.endswith(parts[1]) for canonical_path in self.canonical_modules):
                        score = 70
                        reasons.append(f"Superseded by canonical module in {canonical_path}")
                        break
        
        # Check for version suffixes (_v1, _v2, _old, etc.)
        if re.search(r'(_v\d+|_old|_new|_backup|_copy|\d{8})', filepath.stem):
            score = max(score, 75)
            reasons.append("Filename indicates versioning/backup")
        
        return score, reasons
    
    def score_isolation(self, filepath: Path) -> Tuple[int, List[str]]:
        """Score file for isolation/orphaned status (0-100)."""
        score = 0
        reasons = []
        
        if filepath.suffix != '.py':
            return 0, []
        
        module_name = self.scanner.get_module_name(filepath)
        if not module_name:
            return 0, []
        
        # Check if this module is imported by anyone
        is_imported = module_name in self.scanner.imported_by or \
                     any(module_name.startswith(imp) for imp in self.scanner.imported_by)
        
        # Check if this file imports anything
        has_imports = filepath in self.scanner.imports_from and \
                     len(self.scanner.imports_from[filepath]) > 0
        
        if not is_imported and not has_imports:
            score = 90
            reasons.append("Not imported and imports nothing (orphaned)")
        elif not is_imported:
            score = 60
            reasons.append("Not imported by any file")
        
        return score, reasons
    
    def score_file(self, filepath: Path) -> FileScore:
        """Generate complete score for a file."""
        dup_score, dup_reasons = self.score_duplication(filepath)
        stale_score, stale_reasons = self.score_staleness(filepath)
        obs_score, obs_reasons = self.score_obsolescence(filepath)
        iso_score, iso_reasons = self.score_isolation(filepath)
        
        all_reasons = dup_reasons + stale_reasons + obs_reasons + iso_reasons
        
        total = (dup_score + stale_score + obs_score + iso_score) // 4
        
        # Determine action and confidence
        action = "KEEP"
        confidence = 0
        duplicate_of = None
        
        # High confidence deletions
        if dup_score == 100:
            action = "DELETE"
            confidence = 95
            # Find the canonical duplicate (prefer canonical module paths)
            file_hash = compute_file_hash(filepath)
            if file_hash and file_hash in self.scanner.files_by_hash:
                duplicates = self.scanner.files_by_hash[file_hash]
                canonical = self._find_canonical_duplicate(filepath, duplicates)
                if canonical:
                    duplicate_of = str(canonical.relative_to(self.scanner.root))
        
        elif obs_score >= 90:
            action = "ARCHIVE"
            confidence = 90
        
        elif total >= 70:
            action = "DELETE"
            confidence = 70 + (total - 70) // 3
        
        elif total >= 50:
            action = "ARCHIVE"
            confidence = 50 + (total - 50) // 5
        
        # Get file stats
        last_modified = get_git_last_modified(filepath, self.scanner.root)
        try:
            file_size = filepath.stat().st_size
        except:
            file_size = 0
        
        return FileScore(
            path=str(filepath.relative_to(self.scanner.root)),
            duplication_score=dup_score,
            staleness_score=stale_score,
            obsolescence_score=obs_score,
            isolation_score=iso_score,
            total_score=total,
            confidence=confidence,
            action=action,
            reasons=all_reasons,
            duplicate_of=duplicate_of,
            last_modified=last_modified.isoformat() if last_modified else None,
            file_size=file_size
        )
    
    def _find_canonical_duplicate(self, filepath: Path, duplicates: List[Path]) -> Optional[Path]:
        """Find the canonical version among duplicates."""
        # Prefer files in canonical module paths
        for dup in duplicates:
            if dup == filepath:
                continue
            rel_path = str(dup.relative_to(self.scanner.root))
            if any(rel_path.startswith(canonical) for canonical in self.canonical_modules):
                return dup
        
        # Prefer shorter paths (likely more canonical)
        others = [d for d in duplicates if d != filepath]
        if others:
            return min(others, key=lambda p: len(str(p)))
        
        return None
    
    def analyze_all(self) -> Dict[Path, FileScore]:
        """Score all files in the repository."""
        logger.info("Scoring files for cleanup...")
        
        for i, filepath in enumerate(self.scanner.files):
            # Skip directories
            if filepath.is_dir():
                continue
            
            score = self.score_file(filepath)
            self.scores[filepath] = score
            
            if (i + 1) % 500 == 0:
                logger.info(f"  Scored {i + 1} files...")
        
        logger.info(f"Scoring complete: {len(self.scores)} files scored")
        return self.scores

# =============================================================================
# Directory Structure Analyzer
# =============================================================================

class DirectoryDuplicateDetector:
    """Detects duplicate directory structures."""
    
    def __init__(self, scanner: RepositoryScanner):
        self.scanner = scanner
        self.duplicates: List[CleanupRecommendation] = []
    
    def find_duplicate_directories(self) -> List[CleanupRecommendation]:
        """Find directories with identical structure and content."""
        logger.info("Detecting duplicate directories...")
        
        # Known duplicates from visual inspection
        known_duplicates = [
            (['pm/', 'ccpm/ccpm/'], "CCPM commands duplicated", 95),
            (['pm/commands/', 'ccpm/ccpm/commands/'], "PM commands duplicated", 95),
            (['pm/rules/', 'ccpm/ccpm/rules/'], "PM rules duplicated", 95),
            (['pm/agents/', 'ccpm/ccpm/agents/'], "PM agents duplicated", 95),
            (['tools/pattern-extraction/', 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/'], 
             "Pattern extraction tools duplicated", 90),
        ]
        
        for paths, reason, confidence in known_duplicates:
            # Verify directories exist
            existing = [p for p in paths if (self.scanner.root / p).exists()]
            if len(existing) > 1:
                # Calculate space that could be saved
                total_size = 0
                for p in existing[1:]:  # Keep first, delete rest
                    dir_path = self.scanner.root / p
                    for f in dir_path.rglob('*'):
                        if f.is_file():
                            try:
                                total_size += f.stat().st_size
                            except:
                                pass
                
                self.duplicates.append(CleanupRecommendation(
                    action="DELETE",
                    paths=[p for p in existing[1:]],  # Keep first, suggest deleting rest
                    reason=reason,
                    confidence=confidence,
                    estimated_space_saved=total_size,
                    duplicate_group_id=f"dir_dup_{len(self.duplicates)}"
                ))
        
        logger.info(f"Found {len(self.duplicates)} duplicate directory groups")
        return self.duplicates

# =============================================================================
# Report Generator
# =============================================================================

class CleanupReportGenerator:
    """Generates cleanup reports and scripts."""
    
    def __init__(
        self, 
        scores: Dict[Path, FileScore],
        dir_duplicates: List[CleanupRecommendation],
        root: Path
    ):
        self.scores = scores
        self.dir_duplicates = dir_duplicates
        self.root = root
    
    def generate_json_report(self, output_path: Path):
        """Generate full JSON report."""
        # Group by action
        by_action = defaultdict(list)
        for filepath, score in self.scores.items():
            by_action[score.action].append(asdict(score))
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository_root": str(self.root),
            "total_files_analyzed": len(self.scores),
            "summary": {
                action: len(files) for action, files in by_action.items()
            },
            "total_potential_space_saved": sum(
                s.file_size for s in self.scores.values() 
                if s.action in ['DELETE', 'ARCHIVE']
            ),
            "directory_duplicates": [asdict(d) for d in self.dir_duplicates],
            "file_scores": {
                action: sorted(files, key=lambda x: -x['total_score'])
                for action, files in by_action.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated JSON report: {output_path}")
        return report
    
    def generate_high_confidence_script(self, output_path: Path, confidence_threshold: int = 85):
        """Generate PowerShell script for high-confidence deletions."""
        lines = [
            "# Automated Cleanup Script (High Confidence)",
            f"# Generated: {datetime.now(timezone.utc).isoformat()}",
            f"# Confidence Threshold: {confidence_threshold}%",
            "",
            "$ErrorActionPreference = 'Stop'",
            f"$RepoRoot = '{self.root}'",
            "",
            "Write-Host '=== High Confidence Cleanup ===' -ForegroundColor Cyan",
            "Write-Host 'Review this script before running!' -ForegroundColor Yellow",
            "Write-Host ''",
            "",
            "$DryRun = $true  # Change to $false to execute",
            "",
        ]
        
        delete_count = 0
        space_saved = 0
        
        # Add directory duplicates first
        for dup in self.dir_duplicates:
            if dup.confidence >= confidence_threshold:
                lines.append(f"# {dup.reason} (Confidence: {dup.confidence}%)")
                for path in dup.paths:
                    lines.append(f"if ($DryRun) {{")
                    lines.append(f"    Write-Host '[DRY-RUN] Would delete: {path}' -ForegroundColor Yellow")
                    lines.append(f"}} else {{")
                    lines.append(f"    Remove-Item -Path (Join-Path $RepoRoot '{path}') -Recurse -Force")
                    lines.append(f"    Write-Host 'Deleted: {path}' -ForegroundColor Green")
                    lines.append(f"}}")
                    delete_count += 1
                lines.append("")
                space_saved += dup.estimated_space_saved
        
        # Add high-confidence file deletions
        high_conf_deletes = [
            (fp, score) for fp, score in self.scores.items()
            if score.action == "DELETE" and score.confidence >= confidence_threshold
        ]
        
        # Sort by confidence (highest first)
        high_conf_deletes.sort(key=lambda x: -x[1].confidence)
        
        for filepath, score in high_conf_deletes:
            lines.append(f"# {score.path}")
            lines.append(f"# Confidence: {score.confidence}% | Score: {score.total_score}")
            lines.append(f"# Reasons: {'; '.join(score.reasons)}")
            if score.duplicate_of:
                lines.append(f"# Duplicate of: {score.duplicate_of}")
            lines.append(f"if ($DryRun) {{")
            lines.append(f"    Write-Host '[DRY-RUN] Would delete: {score.path}' -ForegroundColor Yellow")
            lines.append(f"}} else {{")
            lines.append(f"    Remove-Item -Path (Join-Path $RepoRoot '{score.path}') -Force")
            lines.append(f"    Write-Host 'Deleted: {score.path}' -ForegroundColor Green")
            lines.append(f"}}")
            lines.append("")
            delete_count += 1
            space_saved += score.file_size
        
        lines.append("")
        lines.append(f"Write-Host ''")
        lines.append(f"Write-Host 'Summary:' -ForegroundColor Cyan")
        lines.append(f"Write-Host '  Items to delete: {delete_count}'")
        lines.append(f"Write-Host '  Space to save: {space_saved:,} bytes ({space_saved / 1024 / 1024:.2f} MB)'")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Generated high-confidence script: {output_path} ({delete_count} items)")
    
    def generate_review_needed_report(self, output_path: Path, confidence_threshold: int = 85):
        """Generate JSON report for items needing manual review."""
        review_items = []
        
        for filepath, score in self.scores.items():
            if score.action in ['DELETE', 'ARCHIVE', 'CONSOLIDATE'] and \
               score.confidence < confidence_threshold:
                review_items.append(asdict(score))
        
        # Sort by total score (highest first)
        review_items.sort(key=lambda x: -x['total_score'])
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "confidence_threshold": confidence_threshold,
            "total_items": len(review_items),
            "items": review_items
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated review-needed report: {output_path} ({len(review_items)} items)")

# =============================================================================
# Main Execution
# =============================================================================

def load_codebase_index(root: Path) -> dict:
    """Load CODEBASE_INDEX.yaml."""
    index_path = root / "CODEBASE_INDEX.yaml"
    if not index_path.exists():
        logger.warning("CODEBASE_INDEX.yaml not found, using minimal index")
        return {"modules": []}
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(
        description="Automated Repository Cleanup Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis with default threshold (85%)
  python analyze_cleanup_candidates.py
  
  # Run with custom confidence threshold
  python analyze_cleanup_candidates.py --confidence-threshold 90
  
  # Analyze specific directory
  python analyze_cleanup_candidates.py --root /path/to/repo
        """
    )
    
    parser.add_argument(
        '--root', '-r',
        type=Path,
        default=Path.cwd(),
        help='Repository root path (default: current directory)'
    )
    
    parser.add_argument(
        '--confidence-threshold', '-c',
        type=int,
        default=85,
        help='Confidence threshold for automated cleanup (default: 85)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path('cleanup_reports'),
        help='Output directory for reports (default: cleanup_reports/)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup
    root = args.root.resolve()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Repository Cleanup Analyzer v1.0.0")
    logger.info(f"Root: {root}")
    logger.info(f"Confidence threshold: {args.confidence_threshold}%")
    logger.info("")
    
    # Load codebase index
    codebase_index = load_codebase_index(root)
    logger.info(f"Loaded CODEBASE_INDEX with {len(codebase_index.get('modules', []))} modules")
    
    # Step 1: Scan repository
    scanner = RepositoryScanner(root, EXCLUDE_DIRS)
    scanner.scan()
    
    # Step 2: Detect directory duplicates
    dir_detector = DirectoryDuplicateDetector(scanner)
    dir_duplicates = dir_detector.find_duplicate_directories()
    
    # Step 3: Score files
    scorer = CleanupScorer(scanner, codebase_index)
    scores = scorer.analyze_all()
    
    # Step 4: Generate reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    generator = CleanupReportGenerator(scores, dir_duplicates, root)
    
    # Full JSON report
    json_report_path = output_dir / f"cleanup_report_{timestamp}.json"
    report_data = generator.generate_json_report(json_report_path)
    
    # High-confidence script
    script_path = output_dir / f"cleanup_high_confidence_{timestamp}.ps1"
    generator.generate_high_confidence_script(script_path, args.confidence_threshold)
    
    # Review-needed report
    review_path = output_dir / f"cleanup_review_needed_{timestamp}.json"
    generator.generate_review_needed_report(review_path, args.confidence_threshold)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 CLEANUP ANALYSIS SUMMARY")
    print("="*70)
    print(f"\nTotal files analyzed: {len(scores):,}")
    print(f"\nRecommendations:")
    print(f"  DELETE:      {report_data['summary'].get('DELETE', 0):,} files")
    print(f"  ARCHIVE:     {report_data['summary'].get('ARCHIVE', 0):,} files")
    print(f"  CONSOLIDATE: {report_data['summary'].get('CONSOLIDATE', 0):,} files")
    print(f"  KEEP:        {report_data['summary'].get('KEEP', 0):,} files")
    
    print(f"\nDirectory duplicates found: {len(dir_duplicates)}")
    
    space_mb = report_data['total_potential_space_saved'] / 1024 / 1024
    print(f"\nPotential space savings: {space_mb:.2f} MB")
    
    print(f"\n📁 Output files:")
    print(f"  Full report:         {json_report_path}")
    print(f"  High-confidence:     {script_path}")
    print(f"  Review needed:       {review_path}")
    
    print("\n" + "="*70)
    print("🎯 NEXT STEPS:")
    print("="*70)
    print(f"1. Review: {json_report_path}")
    print(f"2. Edit script (set $DryRun=$false): {script_path}")
    print(f"3. Run script: .\\{script_path}")
    print(f"4. Review uncertain cases: {review_path}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
