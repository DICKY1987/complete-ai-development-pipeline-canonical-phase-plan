#!/usr/bin/env python3
"""
Tests for codebase_auditor.py

Validates the audit tool's ability to detect deprecated, obsolete,
duplicative, and outdated files.
"""

import json
import tempfile
from pathlib import Path
import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.codebase_auditor import CodebaseAuditor


class TestCodebaseAuditor:
    """Tests for CodebaseAuditor class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            
            # Create deprecated directory
            (repo / 'src' / 'pipeline').mkdir(parents=True)
            (repo / 'src' / 'pipeline' / 'db.py').write_text('# Legacy shim')
            
            # Create legacy directory
            (repo / 'build').mkdir()
            (repo / 'build' / 'spec.md').write_text('# Old spec')
            
            # Create temporary files
            (repo / 'backup.bak').write_text('backup')
            (repo / '__tmp_test.py').write_text('temp file')
            
            # Create duplicate files
            (repo / 'core').mkdir()
            (repo / 'core' / 'utils.py').write_text('# Core utils')
            (repo / 'engine').mkdir()
            (repo / 'engine' / 'utils.py').write_text('# Engine utils')
            
            # Create outdated documentation
            (repo / 'docs').mkdir()
            (repo / 'docs' / 'guide.md').write_text(
                'from src.pipeline.db import init_db'
            )
            
            # Create potentially obsolete file
            (repo / 'unused.py').write_text('# Not imported anywhere')
            
            # Create referenced file
            (repo / 'main.py').write_text('import unused')
            
            yield repo
    
    def test_scan_deprecated_directories(self, temp_repo):
        """Should detect files in deprecated directories."""
        auditor = CodebaseAuditor(temp_repo)
        auditor._scan_deprecated_directories()
        
        assert 'deprecated' in auditor.findings
        deprecated = auditor.findings['deprecated']
        assert len(deprecated) > 0
        
        # Check that src/pipeline/db.py was found
        paths = [item['path'] for item in deprecated]
        assert any('src/pipeline/db.py' in p or 'src\\pipeline\\db.py' in p for p in paths)
    
    def test_scan_legacy_candidates(self, temp_repo):
        """Should detect legacy candidate directories."""
        auditor = CodebaseAuditor(temp_repo)
        auditor._scan_legacy_candidates()
        
        assert 'legacy' in auditor.findings
        legacy = auditor.findings['legacy']
        
        # Check that build/ was found
        paths = [item['path'] for item in legacy]
        assert 'build/' in paths
    
    def test_scan_temporary_files(self, temp_repo):
        """Should detect temporary and backup files."""
        auditor = CodebaseAuditor(temp_repo)
        auditor._scan_temporary_files()
        
        assert 'temporary' in auditor.findings
        temp_files = auditor.findings['temporary']
        assert len(temp_files) >= 2  # backup.bak and __tmp_test.py
        
        paths = [item['path'] for item in temp_files]
        assert any('backup.bak' in p for p in paths)
        assert any('__tmp_test.py' in p for p in paths)
    
    def test_scan_duplicate_implementations(self, temp_repo):
        """Should detect files with same name in different directories."""
        auditor = CodebaseAuditor(temp_repo)
        auditor._scan_duplicate_implementations()
        
        assert 'duplicative' in auditor.findings
        duplicates = auditor.findings['duplicative']
        
        # Should find utils.py in both core/ and engine/
        basenames = [item['basename'] for item in duplicates]
        assert 'utils.py' in basenames
    
    def test_scan_outdated_documentation(self, temp_repo):
        """Should detect docs with outdated import references."""
        auditor = CodebaseAuditor(temp_repo)
        auditor._scan_outdated_documentation()
        
        assert 'outdated_docs' in auditor.findings
        outdated = auditor.findings['outdated_docs']
        
        # Should find docs/guide.md with old import
        paths = [item['path'] for item in outdated]
        assert any('guide.md' in p for p in paths)
    
    def test_should_exclude(self, temp_repo):
        """Should exclude specified directories."""
        auditor = CodebaseAuditor(temp_repo)
        
        # Create .git directory
        git_dir = temp_repo / '.git'
        git_dir.mkdir()
        git_file = git_dir / 'config'
        git_file.write_text('git config')
        
        assert auditor._should_exclude(git_file)
        assert not auditor._should_exclude(temp_repo / 'main.py')
    
    def test_get_module_path(self, temp_repo):
        """Should convert file path to module path."""
        auditor = CodebaseAuditor(temp_repo)
        
        file_path = temp_repo / 'core' / 'utils.py'
        module_path = auditor._get_module_path(file_path)
        assert module_path == 'core.utils'
        
        file_path = temp_repo / 'main.py'
        module_path = auditor._get_module_path(file_path)
        assert module_path == 'main'
    
    def test_is_executable_script(self, temp_repo):
        """Should detect executable scripts."""
        auditor = CodebaseAuditor(temp_repo)
        
        # Create script with main block
        script = temp_repo / 'script.py'
        script.write_text("if __name__ == '__main__':\n    print('hello')")
        
        assert auditor._is_executable_script(script)
        
        # Non-script file
        non_script = temp_repo / 'module.py'
        non_script.write_text('def func():\n    pass')
        
        assert not auditor._is_executable_script(non_script)
    
    def test_full_audit(self, temp_repo):
        """Should run complete audit and generate summary."""
        auditor = CodebaseAuditor(temp_repo)
        results = auditor.audit()
        
        # Check structure
        assert 'audit_date' in results
        assert 'repository' in results
        assert 'summary' in results
        assert 'findings' in results
        
        # Check summary
        summary = results['summary']
        assert 'total_categories' in summary
        assert 'deprecated_files' in summary
        assert 'temporary_files' in summary
        
        # Should have found issues
        assert summary['deprecated_files'] > 0
        assert summary['temporary_files'] > 0


class TestAuditCriteria:
    """Tests for audit criteria and detection patterns."""
    
    def test_deprecated_dir_patterns(self):
        """Should recognize all deprecated directory patterns."""
        auditor = CodebaseAuditor(Path('.'))
        
        assert 'src/pipeline/' in auditor.DEPRECATED_DIRS
        assert 'MOD_ERROR_PIPELINE/' in auditor.DEPRECATED_DIRS
    
    def test_temp_file_patterns(self):
        """Should recognize all temporary file patterns."""
        auditor = CodebaseAuditor(Path('.'))
        
        import re
        patterns = auditor.TEMP_PATTERNS
        
        # Test various file names
        assert any(re.match(p, 'file.bak') for p in patterns)
        assert any(re.match(p, 'file.old') for p in patterns)
        assert any(re.match(p, '__tmp_test.py') for p in patterns)
        assert any(re.match(p, 'create_backup_20251120.ps1') for p in patterns)
    
    def test_outdated_doc_patterns(self):
        """Should recognize outdated import patterns in docs."""
        auditor = CodebaseAuditor(Path('.'))
        
        import re
        patterns = auditor.OUTDATED_DOC_PATTERNS
        
        # Test various outdated imports
        old_imports = [
            'from src.pipeline.db import init_db',
            'from MOD_ERROR_PIPELINE.error_engine import ErrorEngine',
            'import src.pipeline.crud',
            'import MOD_ERROR_PIPELINE.plugin_manager',
        ]
        
        for old_import in old_imports:
            assert any(re.search(p, old_import) for p in patterns), \
                f"Pattern should match: {old_import}"


class TestReportGeneration:
    """Tests for report generation."""
    
    def test_json_output_structure(self):
        """Should generate valid JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / 'test.bak').write_text('backup')
            
            auditor = CodebaseAuditor(repo)
            results = auditor.audit()
            
            # Should be JSON serializable
            json_str = json.dumps(results)
            parsed = json.loads(json_str)
            
            assert parsed['audit_date']
            assert parsed['repository']
            assert isinstance(parsed['findings'], dict)
    
    def test_markdown_generation(self):
        """Should generate markdown report."""
        from tools.codebase_auditor import generate_markdown_report
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / 'test.bak').write_text('backup')
            
            auditor = CodebaseAuditor(repo)
            results = auditor.audit()
            
            md_path = Path(tmpdir) / 'report.md'
            generate_markdown_report(results, md_path)
            
            assert md_path.exists()
            content = md_path.read_text()
            
            # Check key sections
            assert '# Codebase Audit Report' in content
            assert '## Summary' in content
            assert '## Audit Criteria' in content
            assert '## Recommendations' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
