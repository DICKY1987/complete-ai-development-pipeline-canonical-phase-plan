"""
Tests for the environment scanner module.

Tests scanning for duplicates, misplaced caches, and cleanup operations.
"""
DOC_ID: DOC-PAT-ENVIRONMENT-TEST-SCANNER-426

import tempfile
from pathlib import Path

import pytest

from modules.aim_environment.m01001B_scanner import (
    DuplicateGroup,
    EnvironmentScanner,
    MisplacedCache,
    ScanReport,
)


@pytest.fixture
def temp_scan_dir(tmp_path):
    """Create temporary directory structure for testing."""
    # Create some duplicate files
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    
    # Create identical files
    content = b"test content" * 1000  # ~12KB
    (tmp_path / "dir1" / "file1.txt").write_bytes(content)
    (tmp_path / "dir2" / "file1.txt").write_bytes(content)
    
    # Create different file
    (tmp_path / "dir1" / "file2.txt").write_bytes(b"different")
    
    # Create cache directories
    (tmp_path / "dir1" / "__pycache__").mkdir()
    (tmp_path / "dir1" / "__pycache__" / "test.pyc").write_bytes(b"cache")
    
    (tmp_path / "dir2" / ".mypy_cache").mkdir()
    (tmp_path / "dir2" / ".mypy_cache" / "data.json").write_bytes(b"cache data")
    
    return tmp_path


@pytest.fixture
def scanner():
    """Scanner instance with default settings."""
    return EnvironmentScanner()


class TestDuplicateGroup:
    """Tests for DuplicateGroup dataclass."""
    
    def test_size_mb(self):
        """Test MB size calculation."""
        group = DuplicateGroup(
            file_hash="abc123",
            files=["file1.txt", "file2.txt"],
            size_bytes=1024 * 1024  # 1MB
        )
        assert group.size_mb == 1.0
    
    def test_wasted_bytes(self):
        """Test wasted bytes calculation."""
        group = DuplicateGroup(
            file_hash="abc123",
            files=["f1", "f2", "f3"],
            size_bytes=1000
        )
        # 3 files, wasted = 1000 * (3-1) = 2000
        assert group.wasted_bytes == 2000
    
    def test_wasted_mb(self):
        """Test wasted MB calculation."""
        group = DuplicateGroup(
            file_hash="abc123",
            files=["f1", "f2"],
            size_bytes=1024 * 1024  # 1MB
        )
        # 2 files, wasted = 1MB
        assert group.wasted_mb == 1.0


class TestMisplacedCache:
    """Tests for MisplacedCache dataclass."""
    
    def test_size_mb(self):
        """Test MB size calculation."""
        cache = MisplacedCache(
            path="/tmp/cache",
            pattern="__pycache__",
            size_bytes=2 * 1024 * 1024,  # 2MB
            file_count=10
        )
        assert cache.size_mb == 2.0


class TestScanReport:
    """Tests for ScanReport dataclass."""
    
    def test_total_wasted_mb(self):
        """Test total wasted MB calculation."""
        report = ScanReport()
        report.duplicates = [
            DuplicateGroup("hash1", ["f1", "f2"], 1024 * 1024),  # 1MB wasted
            DuplicateGroup("hash2", ["f3", "f4", "f5"], 2 * 1024 * 1024),  # 4MB wasted
        ]
        assert report.total_wasted_mb == 5.0
    
    def test_total_cache_mb(self):
        """Test total cache MB calculation."""
        report = ScanReport()
        report.misplaced_caches = [
            MisplacedCache("/c1", "__pycache__", 1024 * 1024, 5),  # 1MB
            MisplacedCache("/c2", ".mypy_cache", 2 * 1024 * 1024, 10),  # 2MB
        ]
        assert report.total_cache_mb == 3.0


class TestEnvironmentScanner:
    """Tests for EnvironmentScanner class."""
    
    def test_hash_file(self, scanner, tmp_path):
        """Test file hashing."""
        file1 = tmp_path / "file1.txt"
        file1.write_bytes(b"test content")
        
        hash1 = scanner._hash_file(file1)
        assert hash1
        assert len(hash1) == 64  # SHA256 hex digest
        
        # Same content should have same hash
        file2 = tmp_path / "file2.txt"
        file2.write_bytes(b"test content")
        hash2 = scanner._hash_file(file2)
        
        assert hash1 == hash2
    
    def test_hash_file_different_content(self, scanner, tmp_path):
        """Test different content produces different hash."""
        file1 = tmp_path / "file1.txt"
        file1.write_bytes(b"content1")
        
        file2 = tmp_path / "file2.txt"
        file2.write_bytes(b"content2")
        
        hash1 = scanner._hash_file(file1)
        hash2 = scanner._hash_file(file2)
        
        assert hash1 != hash2
    
    def test_hash_file_nonexistent(self, scanner, tmp_path):
        """Test hashing nonexistent file returns empty string."""
        result = scanner._hash_file(tmp_path / "nonexistent.txt")
        assert result == ""
    
    def test_dir_size(self, scanner, tmp_path):
        """Test directory size calculation."""
        (tmp_path / "file1.txt").write_bytes(b"x" * 100)
        (tmp_path / "file2.txt").write_bytes(b"y" * 200)
        
        total_bytes, file_count = scanner._dir_size(tmp_path)
        
        assert total_bytes == 300
        assert file_count == 2
    
    def test_dir_size_nested(self, scanner, tmp_path):
        """Test directory size with nested directories."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.txt").write_bytes(b"x" * 100)
        (tmp_path / "subdir" / "file2.txt").write_bytes(b"y" * 200)
        
        total_bytes, file_count = scanner._dir_size(tmp_path)
        
        assert total_bytes == 300
        assert file_count == 2
    
    def test_find_duplicates(self, scanner, temp_scan_dir):
        """Test finding duplicate files."""
        duplicates = scanner.find_duplicates([temp_scan_dir], min_size_kb=1)
        
        # Should find the duplicate file1.txt in dir1 and dir2
        assert len(duplicates) == 1
        assert len(duplicates[0].files) == 2
        assert duplicates[0].size_bytes == 12000
    
    def test_find_duplicates_min_size(self, scanner, temp_scan_dir):
        """Test minimum size filter for duplicates."""
        # Set min size higher than any file
        duplicates = scanner.find_duplicates([temp_scan_dir], min_size_kb=1000)
        
        assert len(duplicates) == 0
    
    def test_find_duplicates_extension_filter(self, scanner, tmp_path):
        """Test extension filter for duplicates."""
        # Create duplicate .txt files
        content = b"test" * 100
        (tmp_path / "file1.txt").write_bytes(content)
        (tmp_path / "file2.txt").write_bytes(content)
        
        # Create duplicate .py files
        (tmp_path / "file1.py").write_bytes(content)
        (tmp_path / "file2.py").write_bytes(content)
        
        # Find only .txt duplicates
        duplicates = scanner.find_duplicates(
            [tmp_path],
            min_size_kb=0,
            extensions=[".txt"]
        )
        
        assert len(duplicates) == 1
        assert all(".txt" in f for f in duplicates[0].files)
    
    def test_find_misplaced_caches(self, scanner, temp_scan_dir):
        """Test finding misplaced cache directories."""
        caches = scanner.find_misplaced_caches([temp_scan_dir])
        
        # Should find __pycache__ and .mypy_cache
        assert len(caches) >= 2
        
        patterns = [c.pattern for c in caches]
        assert "__pycache__" in patterns
        assert ".mypy_cache" in patterns
    
    def test_find_misplaced_caches_central_exclusion(self, scanner, tmp_path):
        """Test that central cache location is excluded."""
        # Create cache in central location
        central = tmp_path / "central_cache"
        central.mkdir()
        (central / "__pycache__").mkdir()
        (central / "__pycache__" / "file.pyc").write_bytes(b"cache")
        
        # Create cache outside central location
        other = tmp_path / "other"
        other.mkdir()
        (other / "__pycache__").mkdir()
        (other / "__pycache__" / "file.pyc").write_bytes(b"cache")
        
        caches = scanner.find_misplaced_caches([tmp_path], central_cache=central)
        
        # Should only find cache outside central location
        assert len(caches) == 1
        assert str(other) in caches[0].path
    
    def test_scan_complete(self, scanner, temp_scan_dir):
        """Test complete scan."""
        report = scanner.scan([temp_scan_dir], min_duplicate_size_kb=1)
        
        # Should have duplicates and caches
        assert len(report.duplicates) > 0
        assert len(report.misplaced_caches) > 0
        assert report.total_scanned_files > 0
        assert report.total_scanned_bytes > 0
    
    def test_cleanup_cache(self, scanner, tmp_path):
        """Test cache cleanup."""
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "file.pyc").write_bytes(b"cache")
        
        assert cache_dir.exists()
        
        success = scanner.cleanup_cache(cache_dir)
        
        assert success
        assert not cache_dir.exists()
    
    def test_cleanup_cache_nonexistent(self, scanner, tmp_path):
        """Test cleanup of nonexistent cache."""
        result = scanner.cleanup_cache(tmp_path / "nonexistent")
        assert result is False
    
    def test_remove_duplicates(self, scanner, tmp_path):
        """Test removing duplicate files."""
        # Create duplicates
        content = b"test" * 100
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        file3.write_bytes(content)
        
        group = DuplicateGroup(
            file_hash="abc123",
            files=[str(file1), str(file2), str(file3)],
            size_bytes=len(content)
        )
        
        # Remove duplicates, keeping first file
        removed = scanner.remove_duplicates(group, keep_index=0)
        
        assert len(removed) == 2
        assert file1.exists()
        assert not file2.exists()
        assert not file3.exists()
    
    def test_remove_duplicates_keep_different_index(self, scanner, tmp_path):
        """Test removing duplicates while keeping specific file."""
        content = b"test" * 100
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        
        group = DuplicateGroup(
            file_hash="abc123",
            files=[str(file1), str(file2)],
            size_bytes=len(content)
        )
        
        # Keep second file
        removed = scanner.remove_duplicates(group, keep_index=1)
        
        assert len(removed) == 1
        assert not file1.exists()
        assert file2.exists()
    
    def test_custom_cache_patterns(self, tmp_path):
        """Test scanner with custom cache patterns."""
        custom_patterns = [".custom_cache", ".test_cache"]
        scanner = EnvironmentScanner(cache_patterns=custom_patterns)
        
        # Create caches matching custom patterns
        (tmp_path / ".custom_cache").mkdir()
        (tmp_path / ".custom_cache" / "file").write_bytes(b"data")
        
        caches = scanner.find_misplaced_caches([tmp_path])
        
        assert len(caches) >= 1
        assert any(c.pattern == ".custom_cache" for c in caches)
    
    def test_find_duplicates_sorted_by_waste(self, scanner, tmp_path):
        """Test that duplicates are sorted by wasted space."""
        # Create small duplicates
        small = b"x" * 100
        (tmp_path / "small1.txt").write_bytes(small)
        (tmp_path / "small2.txt").write_bytes(small)
        
        # Create large duplicates
        large = b"y" * 10000
        (tmp_path / "large1.txt").write_bytes(large)
        (tmp_path / "large2.txt").write_bytes(large)
        (tmp_path / "large3.txt").write_bytes(large)  # 3 copies = more waste
        
        duplicates = scanner.find_duplicates([tmp_path], min_size_kb=0)
        
        # Larger waste should come first
        assert duplicates[0].wasted_bytes > duplicates[1].wasted_bytes
    
    def test_find_caches_sorted_by_size(self, scanner, tmp_path):
        """Test that caches are sorted by size."""
        # Create small cache
        small_cache = tmp_path / ".small_cache"
        small_cache.mkdir()
        (small_cache / "file").write_bytes(b"x" * 100)
        
        # Create large cache
        large_cache = tmp_path / ".large_cache"
        large_cache.mkdir()
        (large_cache / "file").write_bytes(b"y" * 10000)
        
        scanner = EnvironmentScanner(cache_patterns=[".small_cache", ".large_cache"])
        caches = scanner.find_misplaced_caches([tmp_path])
        
        # Larger cache should come first
        assert caches[0].size_bytes > caches[1].size_bytes
