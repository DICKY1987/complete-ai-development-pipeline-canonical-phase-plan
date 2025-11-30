#!/usr/bin/env python3
"""
Documentation Move Plan Applicator
Implements DOC-ORG-040 through DOC-ORG-043a
"""
DOC_ID: DOC-PAT-TOOLS-APPLY-DOC-MOVE-PLAN-657
import argparse
import json
import subprocess
import sys
from pathlib import Path


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_git_status(path: Path) -> str | None:
    """Get git status of a file (None if untracked, 'clean', 'modified')."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", str(path)],
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            # Check if file is tracked
            result2 = subprocess.run(
                ["git", "ls-files", str(path)],
                capture_output=True, text=True
            )
            return "clean" if result2.stdout.strip() else None
        return "modified"
    except subprocess.CalledProcessError:
        return None


def apply_move_plan(plan_path: Path, dry_run: bool = True) -> dict:
    """Apply document move plan."""
    moves = []
    conflicts = []
    
    # Read and parse plan
    with plan_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("target_dir"):
                moves.append(record)
    
    repo_root = Path.cwd()
    use_git = is_git_repo()
    successful = 0
    
    for record in moves:
        src_path = repo_root / record["path"]
        target_dir = repo_root / record["target_dir"]
        dst_path = target_dir / Path(record["path"]).name
        
        # Check for conflicts
        if dst_path.exists() and dst_path != src_path:
            git_status = get_git_status(dst_path) if use_git else None
            if git_status == "modified":
                conflicts.append({
                    "source": record["path"],
                    "destination": str(dst_path.relative_to(repo_root)),
                    "reason": "destination_modified",
                    "git_status": git_status
                })
                print(f"[CONFLICT] {dst_path} is modified, skipping")
                continue
        
        if dry_run:
            print(f"[DRY-RUN] {record['path']} -> {record['target_dir']}")
            successful += 1
        else:
            try:
                # Create target directory
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Move file
                if use_git and src_path.exists():
                    subprocess.run(
                        ["git", "mv", str(src_path), str(dst_path)],
                        check=True, capture_output=True
                    )
                else:
                    src_path.rename(dst_path)
                
                print(f"[MOVED] {record['path']} -> {record['target_dir']}")
                successful += 1
            except Exception as e:
                print(f"[ERROR] {record['path']}: {e}", file=sys.stderr)
    
    # Log conflicts
    if conflicts and not dry_run:
        conflict_log = repo_root / ".state/docs/move_conflicts.jsonl"
        conflict_log.parent.mkdir(parents=True, exist_ok=True)
        with conflict_log.open("a", encoding="utf-8") as f:
            for conflict in conflicts:
                f.write(json.dumps(conflict) + "\n")
    
    return {
        "total": len(moves),
        "successful": successful,
        "conflicts": len(conflicts),
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(description="Apply documentation move plan")
    parser.add_argument("--plan", default=".state/docs/doc_move_plan.jsonl",
                       help="Move plan JSONL file")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Print planned moves without executing (default)")
    parser.add_argument("--apply", action="store_true",
                       help="Actually execute file moves")
    
    args = parser.parse_args()
    
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"[ERROR] Plan file not found: {plan_path}", file=sys.stderr)
        return 1
    
    dry_run = not args.apply
    
    print(f"{'DRY RUN' if dry_run else 'APPLYING'} move plan: {plan_path}")
    print("=" * 60)
    
    result = apply_move_plan(plan_path, dry_run=dry_run)
    
    print("=" * 60)
    print(f"Total moves: {result['total']}")
    print(f"Successful: {result['successful']}")
    print(f"Conflicts: {result['conflicts']}")
    
    if result['conflicts'] > 0:
        print(f"\n[WARNING] {result['conflicts']} conflicts detected")
        if not dry_run:
            print("See .state/docs/move_conflicts.jsonl for details")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
