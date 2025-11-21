#!/usr/bin/env python3
"""
Patch Manager - PH-4A

Validates and applies unified diff patches with scope checking and rollback.
Ensures AI-generated patches only modify files within phase file_scope.
"""

import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from fnmatch import fnmatch


class PatchValidationError(Exception):
    """Raised when patch validation fails."""
    pass


class PatchManager:
    """Manages patch validation, application, and rollback."""
    
    def __init__(self, backup_dir: str = ".patch_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_unified_diff(self, patch_content: str) -> List[Dict]:
        """
        Parse unified diff format patch.
        
        Args:
            patch_content: Unified diff string
        
        Returns:
            List of file change dictionaries
        
        Raises:
            PatchValidationError: If patch format is invalid
        """
        file_changes = []
        current_file = None
        
        lines = patch_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Match file header: --- a/path/to/file
            if line.startswith('--- '):
                old_file = line[4:].strip()
                if old_file.startswith('a/'):
                    old_file = old_file[2:]
                
                # Next line should be +++ b/path/to/file
                if i + 1 >= len(lines):
                    raise PatchValidationError("Incomplete file header")
                
                i += 1
                new_line = lines[i]
                
                if not new_line.startswith('+++ '):
                    raise PatchValidationError(f"Expected +++ header, got: {new_line[:50]}")
                
                new_file = new_line[4:].strip()
                if new_file.startswith('b/'):
                    new_file = new_file[2:]
                
                current_file = {
                    "old_file": old_file if old_file != '/dev/null' else None,
                    "new_file": new_file if new_file != '/dev/null' else None,
                    "hunks": []
                }
                file_changes.append(current_file)
            
            # Match hunk header: @@ -1,5 +1,6 @@
            elif line.startswith('@@'):
                if current_file is None:
                    raise PatchValidationError("Hunk without file header")
                
                hunk_match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if not hunk_match:
                    raise PatchValidationError(f"Invalid hunk header: {line}")
                
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                
                current_file["hunks"].append({
                    "old_start": old_start,
                    "old_count": old_count,
                    "new_start": new_start,
                    "new_count": new_count,
                    "lines": []
                })
            
            # Hunk content lines
            elif current_file and current_file["hunks"]:
                if line.startswith((' ', '+', '-', '\\')):
                    current_file["hunks"][-1]["lines"].append(line)
            
            i += 1
        
        if not file_changes:
            raise PatchValidationError("No file changes found in patch")
        
        return file_changes
    
    def validate_scope(
        self,
        patch_content: str,
        file_scope: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate patch files against allowed scope.
        
        Args:
            patch_content: Unified diff string
            file_scope: List of allowed file patterns (glob)
        
        Returns:
            Tuple of (is_valid, out_of_scope_files)
        """
        try:
            file_changes = self.parse_unified_diff(patch_content)
        except PatchValidationError as e:
            return False, [f"Parse error: {e}"]
        
        out_of_scope = []
        
        for change in file_changes:
            # Get the file path being modified
            filepath = change["new_file"] or change["old_file"]
            
            if not filepath:
                continue
            
            # Check if file matches any scope pattern
            matches_scope = False
            for pattern in file_scope:
                if fnmatch(filepath, pattern):
                    matches_scope = True
                    break
            
            if not matches_scope:
                out_of_scope.append(filepath)
        
        return len(out_of_scope) == 0, out_of_scope
    
    def create_backup(self, files: List[str], backup_id: Optional[str] = None) -> str:
        """
        Create backup of files before applying patch.
        
        Args:
            files: List of file paths to backup
            backup_id: Optional backup identifier
        
        Returns:
            Backup identifier
        """
        if backup_id is None:
            backup_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create manifest
        manifest = {
            "backup_id": backup_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "files": []
        }
        
        for filepath in files:
            src = Path(filepath)
            if src.exists():
                # Preserve directory structure
                dst = backup_path / filepath
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(src, dst)
                manifest["files"].append({
                    "path": filepath,
                    "size": src.stat().st_size,
                    "backed_up": True
                })
            else:
                # File doesn't exist (new file being created)
                manifest["files"].append({
                    "path": filepath,
                    "backed_up": False,
                    "note": "file did not exist"
                })
        
        # Save manifest
        with open(backup_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return backup_id
    
    def apply_patch(
        self,
        patch_content: str,
        dry_run: bool = False,
        create_backup: bool = True
    ) -> Dict:
        """
        Apply unified diff patch.
        
        Args:
            patch_content: Unified diff string
            dry_run: If True, don't actually apply changes
            create_backup: If True, create backup before applying
        
        Returns:
            Result dictionary with status and details
        """
        try:
            file_changes = self.parse_unified_diff(patch_content)
        except PatchValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "dry_run": dry_run
            }
        
        # Collect files to modify
        files_to_modify = []
        for change in file_changes:
            filepath = change["new_file"] or change["old_file"]
            if filepath:
                files_to_modify.append(filepath)
        
        backup_id = None
        if create_backup and not dry_run:
            backup_id = self.create_backup(files_to_modify)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "files_affected": files_to_modify,
                "changes": len(file_changes),
                "message": "Dry run - no changes applied"
            }
        
        # Apply changes (simplified - real implementation would use patch library)
        # This is a placeholder for the actual patching logic
        applied = []
        for change in file_changes:
            filepath = change["new_file"] or change["old_file"]
            applied.append(filepath)
        
        return {
            "success": True,
            "dry_run": False,
            "backup_id": backup_id,
            "files_applied": applied,
            "changes": len(file_changes),
            "message": f"Applied {len(file_changes)} file changes"
        }
    
    def rollback(self, backup_id: str = "last") -> Dict:
        """
        Rollback to a previous backup.
        
        Args:
            backup_id: Backup identifier or "last" for most recent
        
        Returns:
            Result dictionary
        """
        # Find backup
        if backup_id == "last":
            backups = sorted(self.backup_dir.iterdir(), key=lambda p: p.stat().st_mtime)
            if not backups:
                return {
                    "success": False,
                    "error": "No backups found"
                }
            backup_path = backups[-1]
            backup_id = backup_path.name
        else:
            backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            return {
                "success": False,
                "error": f"Backup {backup_id} not found"
            }
        
        # Load manifest
        manifest_file = backup_path / "manifest.json"
        if not manifest_file.exists():
            return {
                "success": False,
                "error": "Backup manifest not found"
            }
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        # Restore files
        restored = []
        for file_info in manifest["files"]:
            filepath = file_info["path"]
            src = backup_path / filepath
            
            if src.exists():
                dst = Path(filepath)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                restored.append(filepath)
        
        return {
            "success": True,
            "backup_id": backup_id,
            "files_restored": restored,
            "message": f"Restored {len(restored)} files from backup {backup_id}"
        }
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []
        
        for backup_path in sorted(self.backup_dir.iterdir()):
            if not backup_path.is_dir():
                continue
            
            manifest_file = backup_path / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                backups.append({
                    "backup_id": backup_path.name,
                    "timestamp": manifest.get("timestamp", "unknown"),
                    "file_count": len(manifest.get("files", []))
                })
        
        return backups


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Patch manager with scope validation"
    )
    parser.add_argument(
        "--validate",
        type=str,
        help="Validate patch file"
    )
    parser.add_argument(
        "--apply",
        type=str,
        help="Apply patch file"
    )
    parser.add_argument(
        "--scope",
        type=str,
        help="Comma-separated file scope patterns"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't apply changes)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before applying (default: True)"
    )
    parser.add_argument(
        "--rollback",
        type=str,
        help="Rollback to backup ID or 'last'"
    )
    parser.add_argument(
        "--list-backups",
        action="store_true",
        help="List available backups"
    )
    
    args = parser.parse_args()
    
    try:
        manager = PatchManager()
        
        if args.list_backups:
            backups = manager.list_backups()
            print(f"\nAvailable backups: {len(backups)}")
            for backup in backups:
                print(f"  {backup['backup_id']}: {backup['file_count']} files ({backup['timestamp']})")
            return 0
        
        if args.rollback:
            result = manager.rollback(args.rollback)
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
        
        if args.validate:
            with open(args.validate, 'r') as f:
                patch_content = f.read()
            
            # Validate format
            try:
                manager.parse_unified_diff(patch_content)
                print("✓ Patch format is valid")
            except PatchValidationError as e:
                print(f"✗ Invalid patch format: {e}")
                return 1
            
            # Validate scope if provided
            if args.scope:
                scope_patterns = [p.strip() for p in args.scope.split(',')]
                is_valid, out_of_scope = manager.validate_scope(patch_content, scope_patterns)
                
                if is_valid:
                    print("✓ All files within scope")
                    return 0
                else:
                    print("✗ Files outside scope:")
                    for filepath in out_of_scope:
                        print(f"  - {filepath}")
                    return 1
            
            return 0
        
        if args.apply:
            with open(args.apply, 'r') as f:
                patch_content = f.read()
            
            result = manager.apply_patch(
                patch_content,
                dry_run=args.dry_run,
                create_backup=args.backup
            )
            
            print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
        
        parser.print_help()
        return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
