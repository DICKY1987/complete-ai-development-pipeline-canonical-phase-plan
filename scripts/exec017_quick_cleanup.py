#!/usr/bin/env python3
"""EXEC-017 Quick Cleanup - Archive High-Confidence Orphaned Files"""

import json
import shutil
from datetime import datetime
from pathlib import Path

# Load analysis reports
reports_dir = Path("cleanup_reports")
test_coverage = json.load(open(reports_dir / "test_coverage_archival_report.json"))
reachability = json.load(open(reports_dir / "entry_point_reachability_report.json"))

# Find high-confidence archival candidates (score >= 95)
high_conf_coverage = [
    (module, data) for module, data in test_coverage['test_coverage_scores'].items()
    if data['score'] >= 95
]
high_conf_reachability = {
    module: data for module, data in reachability['reachability_scores'].items()
    if data['score'] == 100  # Completely unreachable
}

print(f"=== EXEC-017 Quick Cleanup Analysis ===\n")
print(f"High-confidence candidates (test coverage score ≥95): {len(high_conf_coverage)}")
print(f"Completely unreachable modules (score 100): {len(high_conf_reachability)}")

# Convert module paths to file paths
def module_to_file(module_path):
    """Convert module path to file path"""
DOC_ID: DOC-SCRIPT-SCRIPTS-EXEC017-QUICK-CLEANUP-713
    # Remove UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK prefix duplicates
    parts = module_path.replace('..', '.').split('.')
    # Convert to file path
    file_path = '/'.join(parts) + '.py'
    return file_path.replace('/', '\\')

# Show top 20 candidates
print(f"\n=== Top 20 High-Confidence Archival Candidates ===")
for i, (module, data) in enumerate(high_conf_coverage[:20], 1):
    score = data['score']
    reasons = data.get('reasons', [])

    print(f"{i:2}. {module[:80]:80} | Score: {score:3}")
    print(f"    Reasons: {', '.join(reasons)}")

# Prepare archival
archive_base = Path("archive") / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_exec017_tier1_automated"

print(f"\n=== Archival Plan ===")
print(f"Archive destination: {archive_base}")
print(f"Files to archive: {len(high_conf_coverage)}")

# Ask for confirmation
print("\nReady to archive these files? (y/n): ", end="")
response = input().strip().lower()

if response == 'y':
    archive_base.mkdir(parents=True, exist_ok=True)
    archived_count = 0

    # Create manifest
    manifest = {
        "date": datetime.now().isoformat(),
        "pattern": "EXEC-017",
        "tier": 1,
        "criteria": "test_coverage_score >= 95",
        "files": []
    }

    for module, data in high_conf_coverage:
        file_path = Path(module_to_file(module))
        if file_path.exists():
            # Create archive subdirectory structure
            archive_path = archive_base / file_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file to archive
            shutil.move(str(file_path), str(archive_path))
            archived_count += 1

            manifest['files'].append({
                "module": module,
                "original": str(file_path),
                "archived": str(archive_path),
                "score": data['score'],
                "reasons": data.get('reasons', [])
            })

            print(f"✓ Archived: {file_path}")

    # Save manifest
    manifest_path = archive_base / "MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== Archival Complete ===")
    print(f"Archived: {archived_count} files")
    print(f"Manifest: {manifest_path}")
    print(f"\nNext steps:")
    print(f"1. Run tests: pytest -q tests/")
    print(f"2. Verify imports: python scripts/validate_archival_safety.py --mode post-archive")
    print(f"3. Commit: git add . && git commit -m 'chore: Archive {archived_count} orphaned files (EXEC-017 Tier 1)'")
else:
    print("Archival cancelled.")
