#!/usr/bin/env python3
"""
Test Suite for Patch Manager - PH-4A
"""

import json
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patch_manager import PatchManager, PatchValidationError


class TestPatchManager:
    """Test patch manager functionality."""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create PatchManager with temp backup directory."""
        return PatchManager(backup_dir=str(tmp_path / "backups"))
    
    @pytest.fixture
    def simple_patch(self):
        """Create a simple unified diff patch."""
        return """--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def hello():
     print("Hello")
+    return True
"""
    
    @pytest.fixture
    def multi_file_patch(self):
        """Create a patch affecting multiple files."""
        return """--- a/file1.py
+++ b/file1.py
@@ -1 +1,2 @@
 print("file1")
+print("modified")
--- a/file2.py
+++ b/file2.py
@@ -1 +1,2 @@
 print("file2")
+print("also modified")
"""
    
    def test_initialization(self, manager):
        """Test patch manager initialization."""
        assert manager.backup_dir.exists()
    
    def test_parse_simple_patch(self, manager, simple_patch):
        """Test parsing a simple unified diff."""
        changes = manager.parse_unified_diff(simple_patch)
        
        assert len(changes) == 1
        assert changes[0]["old_file"] == "test.py"
        assert changes[0]["new_file"] == "test.py"
        assert len(changes[0]["hunks"]) == 1
    
    def test_parse_multi_file_patch(self, manager, multi_file_patch):
        """Test parsing patch with multiple files."""
        changes = manager.parse_unified_diff(multi_file_patch)
        
        assert len(changes) == 2
        assert changes[0]["old_file"] == "file1.py"
        assert changes[1]["old_file"] == "file2.py"
    
    def test_parse_invalid_patch(self, manager):
        """Test parsing invalid patch format."""
        invalid_patch = "This is not a valid patch"
        
        with pytest.raises(PatchValidationError):
            manager.parse_unified_diff(invalid_patch)
    
    def test_parse_incomplete_header(self, manager):
        """Test parsing patch with incomplete header."""
        incomplete = "--- a/test.py\n"
        
        with pytest.raises(PatchValidationError):
            manager.parse_unified_diff(incomplete)
    
    def test_validate_scope_within_scope(self, manager, simple_patch):
        """Test scope validation when patch is within scope."""
        scope = ["*.py", "src/*.py"]
        is_valid, out_of_scope = manager.validate_scope(simple_patch, scope)
        
        assert is_valid is True
        assert len(out_of_scope) == 0
    
    def test_validate_scope_out_of_scope(self, manager):
        """Test scope validation when patch is out of scope."""
        patch = """--- a/config/settings.conf
+++ b/config/settings.conf
@@ -1 +1,2 @@
 setting=value
+new_setting=new_value
"""
        scope = ["src/*.py"]
        is_valid, out_of_scope = manager.validate_scope(patch, scope)
        
        assert is_valid is False
        assert "config/settings.conf" in out_of_scope
    
    def test_validate_scope_glob_patterns(self, manager):
        """Test scope validation with glob patterns."""
        patch = """--- a/src/validators/test.py
+++ b/src/validators/test.py
@@ -1 +1,2 @@
 pass
+print("test")
"""
        scope = ["src/validators/*"]
        is_valid, out_of_scope = manager.validate_scope(patch, scope)
        
        assert is_valid is True
    
    def test_create_backup(self, manager, tmp_path):
        """Test creating backup of files."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")
        
        backup_id = manager.create_backup([str(test_file)])
        
        # Check backup exists
        backup_path = manager.backup_dir / backup_id
        assert backup_path.exists()
        
        # Check manifest
        manifest_file = backup_path / "manifest.json"
        assert manifest_file.exists()
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        assert manifest["backup_id"] == backup_id
        assert len(manifest["files"]) == 1
    
    def test_create_backup_nonexistent_file(self, manager):
        """Test backup with non-existent file."""
        backup_id = manager.create_backup(["nonexistent.txt"])
        
        backup_path = manager.backup_dir / backup_id
        manifest_file = backup_path / "manifest.json"
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        assert len(manifest["files"]) == 1
        assert manifest["files"][0]["backed_up"] is False
    
    def test_apply_patch_dry_run(self, manager, simple_patch):
        """Test applying patch in dry run mode."""
        result = manager.apply_patch(simple_patch, dry_run=True)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "test.py" in result["files_affected"]
    
    def test_apply_patch_with_backup(self, manager, simple_patch):
        """Test applying patch with backup."""
        result = manager.apply_patch(simple_patch, dry_run=False, create_backup=True)
        
        assert result["success"] is True
        assert "backup_id" in result
        assert result["changes"] == 1
    
    def test_apply_invalid_patch(self, manager):
        """Test applying invalid patch."""
        invalid_patch = "not a valid patch"
        result = manager.apply_patch(invalid_patch)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_rollback_latest(self, manager, tmp_path):
        """Test rolling back to latest backup."""
        # Create test file and backup
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")
        
        backup_id = manager.create_backup([str(test_file)])
        
        # Modify file
        test_file.write_text("modified")
        
        # Rollback
        result = manager.rollback("last")
        
        assert result["success"] is True
        assert str(test_file) in result["files_restored"]
        assert test_file.read_text() == "original"
    
    def test_rollback_specific_backup(self, manager, tmp_path):
        """Test rolling back to specific backup."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")
        
        backup_id = manager.create_backup([str(test_file)], backup_id="test_backup")
        test_file.write_text("modified")
        
        result = manager.rollback("test_backup")
        
        assert result["success"] is True
        assert result["backup_id"] == "test_backup"
    
    def test_rollback_nonexistent_backup(self, manager):
        """Test rollback with non-existent backup."""
        result = manager.rollback("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_list_backups(self, manager, tmp_path):
        """Test listing available backups."""
        # Create multiple backups
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        manager.create_backup([str(test_file)], backup_id="backup1")
        manager.create_backup([str(test_file)], backup_id="backup2")
        
        backups = manager.list_backups()
        
        assert len(backups) == 2
        assert any(b["backup_id"] == "backup1" for b in backups)
        assert any(b["backup_id"] == "backup2" for b in backups)
    
    def test_list_backups_empty(self, manager):
        """Test listing backups when none exist."""
        backups = manager.list_backups()
        assert len(backups) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
