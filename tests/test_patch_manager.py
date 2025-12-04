"""
Unit tests for Patch Management System
"""

# DOC_ID: DOC-TEST-TESTS-TEST-PATCH-MANAGER-096
# DOC_ID: DOC-TEST-TESTS-TEST-PATCH-MANAGER-057
import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from core.engine.patch_manager import (
    PatchManager,
    PatchArtifact,
    PatchParseResult,
    ApplyResult,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory"""
    yield tmp_path


@pytest.fixture
def git_repo(temp_dir):
    """Create a temporary git repository"""
    repo_path = temp_dir / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )

    # Create initial file
    test_file = repo_path / "test.py"
    test_file.write_text("def hello():\n    print('hello')\n")

    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    yield repo_path


@pytest.fixture
def patch_manager(temp_dir):
    """Create PatchManager instance"""
    ledger = temp_dir / ".ledger" / "patches"
    return PatchManager(ledger_path=str(ledger))


def test_patch_manager_init(patch_manager, temp_dir):
    """Test PatchManager initialization"""
    assert patch_manager.ledger_path.exists()
    assert patch_manager.ledger_path.is_dir()


def test_parse_patch_content(patch_manager):
    """Test parsing patch content"""
    patch_content = """diff --git a/test.py b/test.py
index abc123..def456 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def hello():
     print('hello')
+    return True
"""

    result = patch_manager.parse_patch_content(patch_content)

    assert isinstance(result, PatchParseResult)
    assert "test.py" in result.files_modified
    assert result.hunks == 1
    assert result.additions == 1
    assert result.deletions == 0
    assert result.line_count == 1


def test_parse_patch_content_multiple_files(patch_manager):
    """Test parsing patch with multiple files"""
    patch_content = """diff --git a/file1.py b/file1.py
index abc123..def456 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,2 @@
-old line
+new line
 unchanged
diff --git a/file2.py b/file2.py
index 111222..333444 100644
--- a/file2.py
+++ b/file2.py
@@ -1,1 +1,2 @@
 first line
+second line
"""

    result = patch_manager.parse_patch_content(patch_content)

    assert len(result.files_modified) == 2
    assert "file1.py" in result.files_modified
    assert "file2.py" in result.files_modified
    assert result.hunks == 2
    assert result.additions == 2
    assert result.deletions == 1


def test_capture_patch(patch_manager, git_repo):
    """Test capturing a patch from git worktree"""
    # Modify file
    test_file = git_repo / "test.py"
    test_file.write_text("def hello():\n    print('hello world')\n    return True\n")

    # Capture patch
    artifact = patch_manager.capture_patch(
        run_id="run-123",
        ws_id="ws-1",
        worktree_path=str(git_repo),
        step_name="edit",
        attempt=1,
    )

    assert isinstance(artifact, PatchArtifact)
    assert artifact.patch_id == "ws-1-run-123-edit-1"
    assert artifact.run_id == "run-123"
    assert artifact.ws_id == "ws-1"
    assert artifact.step_name == "edit"
    assert artifact.attempt == 1
    assert len(artifact.diff_hash) == 64  # SHA256
    assert "test.py" in artifact.files_modified
    assert artifact.line_count > 0
    assert artifact.patch_file.exists()


def test_capture_patch_empty_diff(patch_manager, git_repo):
    """Test capturing when there's no diff"""
    # No modifications
    artifact = patch_manager.capture_patch(
        run_id="run-123", ws_id="ws-1", worktree_path=str(git_repo)
    )

    assert artifact.line_count == 0
    assert len(artifact.files_modified) == 0


def test_parse_patch_file(patch_manager, temp_dir):
    """Test parsing a patch file"""
    patch_file = temp_dir / "test.patch"
    patch_file.write_text(
        """diff --git a/test.py b/test.py
index abc..def 100644
--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
 line 1
+line 2
"""
    )

    result = patch_manager.parse_patch(patch_file)

    assert result.files_modified == ["test.py"]
    assert result.additions == 1
    assert result.deletions == 0


def test_apply_patch_success(patch_manager, git_repo, temp_dir):
    """Test successfully applying a patch"""
    # Create a patch file
    patch_file = temp_dir / "test.patch"
    patch_file.write_text(
        """diff --git a/test.py b/test.py
index abc..def 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def hello():
     print('hello')
+    return True
"""
    )

    # Apply patch
    result = patch_manager.apply_patch(patch_file, str(git_repo))

    assert isinstance(result, ApplyResult)
    assert result.success is True
    assert "successfully" in result.message.lower()

    # Verify file was modified
    test_file = git_repo / "test.py"
    content = test_file.read_text()
    assert "return True" in content


def test_apply_patch_dry_run(patch_manager, git_repo, temp_dir):
    """Test dry run patch application"""
    patch_file = temp_dir / "test.patch"
    patch_file.write_text(
        """diff --git a/test.py b/test.py
index abc..def 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def hello():
     print('hello')
+    return True
"""
    )

    # Dry run
    result = patch_manager.apply_patch(patch_file, str(git_repo), dry_run=True)

    assert result.success is True
    assert "dry run" in result.message.lower()

    # Verify file was NOT modified
    test_file = git_repo / "test.py"
    content = test_file.read_text()
    assert "return True" not in content


def test_apply_patch_conflict(patch_manager, git_repo, temp_dir):
    """Test applying a patch that conflicts"""
    # Create conflicting patch
    patch_file = temp_dir / "conflict.patch"
    patch_file.write_text(
        """diff --git a/test.py b/test.py
index abc..def 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,2 @@
-def nonexistent():
+def hello():
     print('world')
"""
    )

    result = patch_manager.apply_patch(patch_file, str(git_repo))

    assert result.success is False
    assert len(result.conflicts) > 0 or "cannot be applied" in result.message.lower()


def test_reverse_patch(patch_manager, git_repo, temp_dir):
    """Test reversing a patch"""
    # Create and apply patch
    patch_file = temp_dir / "test.patch"
    patch_file.write_text(
        """diff --git a/test.py b/test.py
index abc..def 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def hello():
     print('hello')
+    return True
"""
    )

    # Apply
    apply_result = patch_manager.apply_patch(patch_file, str(git_repo))
    assert apply_result.success is True

    # Reverse
    reverse_result = patch_manager.reverse_patch(patch_file, str(git_repo))
    assert reverse_result.success is True

    # Verify file reverted
    test_file = git_repo / "test.py"
    content = test_file.read_text()
    assert "return True" not in content


def test_get_patch_stats(patch_manager, temp_dir):
    """Test getting patch statistics"""
    patch_file = temp_dir / "test.patch"
    patch_content = """diff --git a/file1.py b/file1.py
index abc..def 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
 line 1
 line 2
+line 3
diff --git a/file2.py b/file2.py
index 111..222 100644
--- a/file2.py
+++ b/file2.py
@@ -1,1 +1,1 @@
-old
+new
"""
    patch_file.write_text(patch_content)

    stats = patch_manager.get_patch_stats(patch_file)

    assert stats["file_count"] == 2
    assert "file1.py" in stats["files_modified"]
    assert "file2.py" in stats["files_modified"]
    assert stats["hunks"] == 2
    assert stats["additions"] == 2
    assert stats["deletions"] == 1
    assert stats["line_count"] == 3
    assert len(stats["diff_hash"]) == 64
    assert stats["size_bytes"] > 0


def test_patch_hash_consistency(patch_manager, git_repo):
    """Test that same diff produces same hash"""
    # Make change
    test_file = git_repo / "test.py"
    test_file.write_text("def hello():\n    print('hello world')\n")

    # Capture patch twice
    artifact1 = patch_manager.capture_patch("run-1", "ws-1", str(git_repo))

    # Reset
    subprocess.run(
        ["git", "checkout", "test.py"], cwd=git_repo, check=True, capture_output=True
    )

    # Make same change again
    test_file.write_text("def hello():\n    print('hello world')\n")
    artifact2 = patch_manager.capture_patch("run-2", "ws-1", str(git_repo))

    # Hashes should match
    assert artifact1.diff_hash == artifact2.diff_hash


def test_parse_patch_with_binary_files(patch_manager):
    """Test parsing patch with binary files mentioned"""
    patch_content = """diff --git a/image.png b/image.png
index abc..def 100644
Binary files a/image.png and b/image.png differ
diff --git a/text.py b/text.py
index 111..222 100644
--- a/text.py
+++ b/text.py
@@ -1,1 +1,2 @@
 line 1
+line 2
"""

    result = patch_manager.parse_patch_content(patch_content)

    # Should still parse text file changes
    assert "text.py" in result.files_modified
    assert result.additions == 1


def test_patch_with_spaces_in_filename(patch_manager):
    """Test parsing patch with spaces in filenames"""
    patch_content = """diff --git a/my file.py b/my file.py
index abc..def 100644
--- a/my file.py
+++ b/my file.py
@@ -1,1 +1,2 @@
 line 1
+line 2
"""

    result = patch_manager.parse_patch_content(patch_content)

    assert "my file.py" in result.files_modified
