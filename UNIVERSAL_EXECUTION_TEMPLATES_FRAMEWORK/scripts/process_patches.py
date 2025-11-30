#!/usr/bin/env python3
"""
Patch Lifecycle Management Script
Implements PAT-PATCH-001: Check, Apply, Archive patches

Usage:
    python scripts/process_patches.py                    # Process all patches
    python scripts/process_patches.py --check FILE       # Check specific patch
    python scripts/process_patches.py --apply FILE       # Apply specific patch
    python scripts/process_patches.py --dry-run          # Show what would happen
    python scripts/process_patches.py --validate         # Validate no pending patches
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-PROCESS-PATCHES-275

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import shutil


class PatchManager:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.patches_dir = self.repo_path / "patches"
        self.active_dir = self.patches_dir / "active"
        self.archive_dir = self.patches_dir / "archive"
        self.failed_dir = self.patches_dir / "failed"
        
        # Create directories if they don't exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
    
    def is_patch_applied(self, patch_file: Path) -> bool:
        """Check if a patch has been applied by attempting reverse dry-run."""
        result = subprocess.run(
            ["git", "apply", "--check", "--reverse", str(patch_file)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        # Exit code 0 = patch IS applied (reverse succeeds)
        return result.returncode == 0
    
    def apply_patch(self, patch_file: Path) -> Dict[str, any]:
        """Apply a patch file with 3-way merge support."""
        if self.is_patch_applied(patch_file):
            return {
                "success": True,
                "patch": str(patch_file),
                "message": "Already applied",
                "output": ""
            }
        
        result = subprocess.run(
            ["git", "apply", "--3way", str(patch_file)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "patch": str(patch_file),
            "message": "Applied successfully" if result.returncode == 0 else "Failed to apply",
            "output": result.stdout + result.stderr
        }
    
    def archive_patch(self, patch_file: Path) -> Path:
        """Move patch to dated archive folder."""
        date_folder = datetime.now().strftime("%Y-%m-%d")
        archive_path = self.archive_dir / date_folder
        archive_path.mkdir(parents=True, exist_ok=True)
        
        dest = archive_path / patch_file.name
        shutil.move(str(patch_file), str(dest))
        return dest
    
    def move_to_failed(self, patch_file: Path) -> Path:
        """Move failed patch to failed directory."""
        dest = self.failed_dir / patch_file.name
        shutil.move(str(patch_file), str(dest))
        return dest
    
    def discover_all_patches(self) -> List[Path]:
        """Recursively find all .patch files in repository."""
        patch_files = []
        
        def search_recursive(current_path: Path):
            try:
                for item in current_path.iterdir():
                    # Skip common directories
                    if item.name in {'.git', '.venv', '__pycache__', 'node_modules', 
                                   '.pytest_cache', '.worktrees', 'archive', 'failed'}:
                        continue
                    
                    if item.is_dir():
                        search_recursive(item)
                    elif item.is_file() and item.suffix == '.patch':
                        patch_files.append(item)
            except PermissionError:
                pass
        
        search_recursive(self.repo_path)
        return sorted(patch_files)
    
    def process_all_patches(self, dry_run: bool = False) -> Dict[str, List]:
        """Process all patches found recursively in repository."""
        results = {
            "applied": [],
            "already_applied": [],
            "failed": [],
            "archived": []
        }
        
        # Recursively discover all .patch files
        patch_files = self.discover_all_patches()
        
        if not patch_files:
            print("No .patch files found in repository (searched recursively)")
            return results
        
        print(f"Discovered {len(patch_files)} patch files across all subdirectories\n")
        
        for patch_file in patch_files:
            print(f"\nProcessing: {patch_file.name}")
            
            # Check status
            already_applied = self.is_patch_applied(patch_file)
            
            if already_applied:
                print(f"  ○ Already applied")
                results["already_applied"].append(str(patch_file))
                
                if not dry_run:
                    archived = self.archive_patch(patch_file)
                    results["archived"].append(str(archived))
                    print(f"  → Archived to {archived}")
                else:
                    print(f"  [DRY RUN] Would archive to archive/{datetime.now().strftime('%Y-%m-%d')}/")
                continue
            
            # Apply patch
            if not dry_run:
                apply_result = self.apply_patch(patch_file)
                
                if apply_result["success"]:
                    print(f"  ✓ Applied successfully")
                    results["applied"].append(str(patch_file))
                    
                    archived = self.archive_patch(patch_file)
                    results["archived"].append(str(archived))
                    print(f"  → Archived to {archived}")
                else:
                    print(f"  ✗ Failed to apply")
                    print(f"  Error: {apply_result['output']}")
                    results["failed"].append({
                        "patch": str(patch_file),
                        "error": apply_result["output"]
                    })
                    
                    failed_path = self.move_to_failed(patch_file)
                    print(f"  → Moved to {failed_path}")
            else:
                print(f"  [DRY RUN] Would attempt to apply")
        
        return results
    
    def print_summary(self, results: Dict[str, List]):
        """Print formatted summary of patch processing."""
        print("\n" + "="*60)
        print("Patch Processing Summary")
        print("="*60)
        
        print(f"\n✓ Applied: {len(results['applied'])}")
        for patch in results["applied"]:
            print(f"  • {Path(patch).name}")
        
        print(f"\n○ Already Applied: {len(results['already_applied'])}")
        for patch in results["already_applied"]:
            print(f"  • {Path(patch).name}")
        
        print(f"\n✗ Failed: {len(results['failed'])}")
        for item in results["failed"]:
            print(f"  • {Path(item['patch']).name}")
        
        print(f"\n→ Archived: {len(results['archived'])}")
        for patch in results["archived"]:
            print(f"  • {patch}")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Patch Lifecycle Management (PAT-PATCH-001)"
    )
    parser.add_argument(
        "--check",
        metavar="FILE",
        help="Check if specific patch is applied"
    )
    parser.add_argument(
        "--apply",
        metavar="FILE",
        help="Apply specific patch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate no pending patches (for CI/CD)"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)"
    )
    
    args = parser.parse_args()
    
    manager = PatchManager(args.repo)
    
    # Handle specific operations
    if args.check:
        patch_file = Path(args.check)
        if not patch_file.exists():
            print(f"Error: Patch file not found: {patch_file}")
            sys.exit(1)
        
        is_applied = manager.is_patch_applied(patch_file)
        if is_applied:
            print(f"✓ Patch is APPLIED: {patch_file.name}")
            sys.exit(0)
        else:
            print(f"○ Patch is NOT applied: {patch_file.name}")
            sys.exit(1)
    
    elif args.apply:
        patch_file = Path(args.apply)
        if not patch_file.exists():
            print(f"Error: Patch file not found: {patch_file}")
            sys.exit(1)
        
        result = manager.apply_patch(patch_file)
        print(result["message"])
        if result["output"]:
            print(result["output"])
        
        sys.exit(0 if result["success"] else 1)
    
    elif args.validate:
        # Check for any pending patches
        patch_files = list(manager.active_dir.glob("*.patch"))
        patch_files.extend(manager.patches_dir.glob("*.patch"))
        
        if patch_files:
            print(f"✗ Validation failed: {len(patch_files)} pending patches found")
            for pf in patch_files:
                print(f"  • {pf.name}")
            sys.exit(1)
        else:
            print("✓ Validation passed: No pending patches")
            sys.exit(0)
    
    else:
        # Process all patches
        print("Processing all patches...")
        if args.dry_run:
            print("[DRY RUN MODE - No changes will be made]\n")
        
        results = manager.process_all_patches(dry_run=args.dry_run)
        manager.print_summary(results)
        
        # Exit with error if any patches failed
        sys.exit(1 if results["failed"] else 0)


if __name__ == "__main__":
    main()
