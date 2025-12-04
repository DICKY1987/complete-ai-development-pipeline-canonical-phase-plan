#!/usr/bin/env python3
"""
EXEC-015: Stale File Archiver - Staleness Scorer
Analyzes files to determine staleness score for archival candidates.

Scoring Criteria (total = 100 points):
- Last modified days (30 points): ≥180 days = max points
- Last commit days (20 points): ≥365 days = max points
- Reference count (20 points): 0 references = max points (inverted)
- Location tier (10 points): archive/ = max points (inverted)
- File size (10 points): Smaller = higher points
- Test coverage (10 points): 0% coverage = max points (inverted)

Files with ≥70 points are marked as stale and recommended for archival.
"""
# DOC_ID: DOC-PAT-DETECTORS-STALENESS-SCORER-886

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class StalenessScorer:
    """Calculate staleness scores for files to identify archival candidates."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize staleness scorer.

        Args:
            config: Optional configuration dict with scoring weights
        """
        self.config = config or self._load_default_config()

        # Scoring weights
        self.weights = {
            'last_modified_days': 30,
            'last_commit_days': 20,
            'reference_count': 20,
            'location_tier': 10,
            'file_size': 10,
            'test_coverage': 10
        }

        # Location tier scoring (inverted: archive = high score)
        self.location_tiers = {
            'archive/': 100,
            'legacy/': 90,
            'deprecated/': 80,
            'ToDo_Task/': 70,
            'REFACTOR_2/': 60,
            'modules/': 30,
            'core/': 10,
            'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/': 0
        }

        # Thresholds
        self.stale_threshold = 70  # Files ≥70 points are stale
        self.old_modified_days = 180  # 6 months
        self.old_commit_days = 365  # 1 year
        self.large_file_bytes = 1024 * 1024  # 1 MB

    def _load_default_config(self) -> Dict:
        """Load default configuration."""
        config_path = Path('config/cleanup_automation_config.yaml')
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    return data.get('patterns', {}).get('EXEC-015', {})
            except:
                pass
        return {}

    def score_file(self, file_path: str) -> Dict:
        """
        Calculate staleness score for a file.

        Args:
            file_path: Path to file to score

        Returns:
            Dict with score components and total score
        """
        if not os.path.exists(file_path):
            return {'error': 'File not found', 'total_score': 0}

        scores = {
            'file_path': file_path,
            'components': {},
            'total_score': 0,
            'is_stale': False,
            'recommendation': 'keep'
        }

        # Component 1: Last modified days
        modified_score = self._score_last_modified(file_path)
        scores['components']['last_modified'] = modified_score

        # Component 2: Last commit days
        commit_score = self._score_last_commit(file_path)
        scores['components']['last_commit'] = commit_score

        # Component 3: Reference count (imports/usage)
        reference_score = self._score_references(file_path)
        scores['components']['references'] = reference_score

        # Component 4: Location tier
        location_score = self._score_location(file_path)
        scores['components']['location'] = location_score

        # Component 5: File size
        size_score = self._score_file_size(file_path)
        scores['components']['file_size'] = size_score

        # Component 6: Test coverage
        coverage_score = self._score_test_coverage(file_path)
        scores['components']['test_coverage'] = coverage_score

        # Calculate total score
        total = (
            modified_score['score'] +
            commit_score['score'] +
            reference_score['score'] +
            location_score['score'] +
            size_score['score'] +
            coverage_score['score']
        )

        scores['total_score'] = total
        scores['is_stale'] = total >= self.stale_threshold

        if scores['is_stale']:
            scores['recommendation'] = 'archive'
        else:
            scores['recommendation'] = 'keep'

        return scores

    def _score_last_modified(self, file_path: str) -> Dict:
        """Score based on last modification time."""
        try:
            mtime = os.path.getmtime(file_path)
            days_old = (time.time() - mtime) / (24 * 3600)

            # Linear scaling: 0 days = 0 points, 180+ days = 30 points
            raw_score = min(days_old / self.old_modified_days, 1.0)
            score = int(raw_score * self.weights['last_modified_days'])

            return {
                'score': score,
                'max_score': self.weights['last_modified_days'],
                'days_old': int(days_old),
                'threshold': self.old_modified_days
            }
        except Exception as e:
            return {
                'score': 0,
                'max_score': self.weights['last_modified_days'],
                'error': str(e)
            }

    def _score_last_commit(self, file_path: str) -> Dict:
        """Score based on last git commit date."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ct', '--', file_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                commit_time = int(result.stdout.strip())
                days_old = (time.time() - commit_time) / (24 * 3600)

                # Linear scaling: 0 days = 0 points, 365+ days = 20 points
                raw_score = min(days_old / self.old_commit_days, 1.0)
                score = int(raw_score * self.weights['last_commit_days'])

                return {
                    'score': score,
                    'max_score': self.weights['last_commit_days'],
                    'days_old': int(days_old),
                    'threshold': self.old_commit_days
                }
            else:
                # No commits = very stale
                return {
                    'score': self.weights['last_commit_days'],
                    'max_score': self.weights['last_commit_days'],
                    'days_old': 999,
                    'note': 'No git history'
                }
        except Exception as e:
            return {
                'score': 0,
                'max_score': self.weights['last_commit_days'],
                'error': str(e)
            }

    def _score_references(self, file_path: str) -> Dict:
        """Score based on number of references (imports/usage)."""
        try:
            # Search for references using ripgrep (fast)
            filename = Path(file_path).name
            base_name = Path(file_path).stem

            # Count imports and references
            ref_count = 0

            # Try ripgrep first
            try:
                result = subprocess.run(
                    ['rg', '-c', f'{base_name}', '.', '--type', 'py'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    ref_count = sum(int(line.split(':')[-1]) for line in lines if ':' in line)
            except:
                # Fallback to simple grep
                try:
                    result = subprocess.run(
                        ['git', 'grep', '-c', base_name],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        ref_count = len(lines)
                except:
                    pass

            # Inverted scoring: 0 refs = max points, 10+ refs = 0 points
            if ref_count == 0:
                score = self.weights['reference_count']
            else:
                raw_score = max(0, 1 - (ref_count / 10))
                score = int(raw_score * self.weights['reference_count'])

            return {
                'score': score,
                'max_score': self.weights['reference_count'],
                'reference_count': ref_count
            }
        except Exception as e:
            return {
                'score': 0,
                'max_score': self.weights['reference_count'],
                'error': str(e)
            }

    def _score_location(self, file_path: str) -> Dict:
        """Score based on file location (archive/ = high score)."""
        normalized_path = file_path.replace('\\', '/')

        # Find matching tier
        for tier_prefix, tier_score in self.location_tiers.items():
            if normalized_path.startswith(tier_prefix) or f'/{tier_prefix}' in normalized_path:
                # Scale to max weight
                raw_score = tier_score / 100
                score = int(raw_score * self.weights['location_tier'])

                return {
                    'score': score,
                    'max_score': self.weights['location_tier'],
                    'tier': tier_prefix,
                    'tier_score': tier_score
                }

        # Default: no archival tier found
        return {
            'score': 0,
            'max_score': self.weights['location_tier'],
            'tier': 'active',
            'tier_score': 0
        }

    def _score_file_size(self, file_path: str) -> Dict:
        """Score based on file size (smaller = higher score)."""
        try:
            size_bytes = os.path.getsize(file_path)

            # Inverted scoring: 0 bytes = max points, 1MB+ = 0 points
            if size_bytes == 0:
                score = self.weights['file_size']
            else:
                raw_score = max(0, 1 - (size_bytes / self.large_file_bytes))
                score = int(raw_score * self.weights['file_size'])

            return {
                'score': score,
                'max_score': self.weights['file_size'],
                'size_bytes': size_bytes,
                'size_kb': round(size_bytes / 1024, 2)
            }
        except Exception as e:
            return {
                'score': 0,
                'max_score': self.weights['file_size'],
                'error': str(e)
            }

    def _score_test_coverage(self, file_path: str) -> Dict:
        """Score based on test coverage (0% = high score)."""
        # Simplified: Check if test file exists
        if not file_path.endswith('.py'):
            return {
                'score': 0,
                'max_score': self.weights['test_coverage'],
                'note': 'Non-Python file'
            }

        # Look for corresponding test file
        path = Path(file_path)
        test_patterns = [
            f'test_{path.stem}.py',
            f'{path.stem}_test.py',
            f'tests/**/test_{path.stem}.py',
            f'tests/**/{path.stem}_test.py'
        ]

        has_tests = False
        for pattern in test_patterns:
            if list(Path('.').glob(pattern)):
                has_tests = True
                break

        # Inverted: no tests = max points
        if has_tests:
            score = 0
        else:
            score = self.weights['test_coverage']

        return {
            'score': score,
            'max_score': self.weights['test_coverage'],
            'has_tests': has_tests
        }

    def scan_directory(self, directory: str, exclude_patterns: List[str] = None) -> List[Dict]:
        """
        Scan directory and score all files.

        Args:
            directory: Directory to scan
            exclude_patterns: Patterns to exclude

        Returns:
            List of score dicts sorted by staleness (highest first)
        """
        if exclude_patterns is None:
            exclude_patterns = [
                '__pycache__',
                '.git',
                'node_modules',
                '.venv',
                'venv',
                '.cleanup_backups',
                '.pyc',
                '.db',
                '.log'
            ]

        scores = []

        for root, dirs, files in os.walk(directory):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]

            for file in files:
                # Skip excluded patterns
                if any(ex in file for ex in exclude_patterns):
                    continue

                file_path = os.path.join(root, file)
                score = self.score_file(file_path)
                scores.append(score)

        # Sort by total score (highest = most stale)
        scores.sort(key=lambda x: x['total_score'], reverse=True)

        return scores


def main():
    """CLI for staleness scorer."""
    parser = argparse.ArgumentParser(
        description='EXEC-015 Stale File Archiver - Staleness Scorer'
    )
    parser.add_argument(
        '--scan-paths',
        nargs='+',
        default=['.'],
        help='Directories to scan for stale files'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=70,
        help='Staleness threshold (0-100, default: 70)'
    )
    parser.add_argument(
        '--report',
        default='staleness_report.json',
        help='Output report file (JSON)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=50,
        help='Show top N stale files (default: 50)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    print("\nEXEC-015: Stale File Analysis")
    print("=" * 80)
    print(f"Threshold: {args.threshold} points (>={args.threshold} = stale)")
    print(f"Scan paths: {', '.join(args.scan_paths)}\n")

    scorer = StalenessScorer()
    scorer.stale_threshold = args.threshold

    all_scores = []

    for scan_path in args.scan_paths:
        if not os.path.exists(scan_path):
            print(f"⚠️  Path not found: {scan_path}")
            continue

        print(f"Scanning: {scan_path}...")

        if os.path.isfile(scan_path):
            score = scorer.score_file(scan_path)
            all_scores.append(score)
        else:
            scores = scorer.scan_directory(scan_path)
            all_scores.extend(scores)

    # Sort by staleness
    all_scores.sort(key=lambda x: x['total_score'], reverse=True)

    # Filter stale files
    stale_files = [s for s in all_scores if s['is_stale']]

    print(f"\nAnalysis Results:")
    print(f"  Total files scanned: {len(all_scores)}")
    print(f"  Stale files found: {len(stale_files)} (>={args.threshold} points)")
    print(f"  Active files: {len(all_scores) - len(stale_files)}\n")

    # Show top N stale files
    print(f"Top {min(args.top, len(stale_files))} Stale Files:\n")

    for i, score in enumerate(stale_files[:args.top], 1):
        print(f"{i}. {score['file_path']} (Score: {score['total_score']})")

        if args.verbose:
            comps = score['components']
            print(f"   - Last modified: {comps['last_modified']['days_old']} days ago")
            print(f"   - Last commit: {comps['last_commit'].get('days_old', 'N/A')} days ago")
            print(f"   - References: {comps['references'].get('reference_count', 0)}")
            print(f"   - Location: {comps['location'].get('tier', 'N/A')}")
            print(f"   - Size: {comps['file_size'].get('size_kb', 0)} KB")
            print()

    # Export report
    report = {
        'scan_date': datetime.now().isoformat(),
        'threshold': args.threshold,
        'total_files': len(all_scores),
        'stale_files': len(stale_files),
        'active_files': len(all_scores) - len(stale_files),
        'stale_file_details': stale_files,
        'all_scores': all_scores[:100]  # Limit to top 100 for file size
    }

    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport exported to: {args.report}")
    print(f"\nRecommendation: Archive {len(stale_files)} stale files")

    return 0


if __name__ == '__main__':
    sys.exit(main())
