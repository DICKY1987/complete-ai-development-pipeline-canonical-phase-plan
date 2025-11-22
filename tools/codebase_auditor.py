#!/usr/bin/env python3
"""
Comprehensive Codebase Auditor

Systematically analyzes repository to identify:
- Deprecated files (legacy shims, old import paths)
- Obsolete files (unused, no references)
- Duplicative files (redundant implementations)
- Outdated documentation (referencing old paths/phases)
- Temporary/backup files that should be archived

Usage:
    python tools/codebase_auditor.py
    python tools/codebase_auditor.py --json
    python tools/codebase_auditor.py --output audit_report.json
    python tools/codebase_auditor.py --category deprecated
"""

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import ast


class CodebaseAuditor:
    """Comprehensive codebase auditor for identifying stale/unnecessary files."""
    
    # Known deprecated directories
    DEPRECATED_DIRS = {
        'src/pipeline/': 'Legacy shims - use core.* instead',
        'MOD_ERROR_PIPELINE/': 'Legacy error shims - use error.* instead',
    }
    
    # Known legacy/archive candidates from docs
    LEGACY_CANDIDATES = {
        'build/': 'Single spec doc - legacy build output',
        'bundles/': 'Misplaced test bundle - should be in workstreams/',
        'pipeline_plus/': 'Archive of previous implementation',
        'state/': 'Only contains DB file - should relocate to .worktrees/',
    }
    
    # Large directories that may be archive candidates
    POTENTIAL_ARCHIVE_DIRS = [
        'AGENTIC_DEV_PROTOTYPE',
        'PROCESS_DEEP_DIVE_OPTOMIZE',
        'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK',
        'Multi-Document Versioning Automation final_spec_docs',
        '.migration_backup_20251120_144334',
        'AI_MANGER',
        'AUX_mcp-data',
        'CMD',
    ]
    
    # File patterns that indicate temporary/backup files
    TEMP_PATTERNS = [
        r'.*\.bak$',
        r'.*\.old$',
        r'.*\.tmp$',
        r'.*~$',
        r'^__tmp_.*',
        r'.*_backup_\d+.*',
        r'^create_backup_.*\.ps1$',
    ]
    
    # Patterns for outdated documentation
    OUTDATED_DOC_PATTERNS = [
        r'from\s+src\.pipeline\.',
        r'from\s+MOD_ERROR_PIPELINE\.',
        r'import\s+src\.pipeline\.',
        r'import\s+MOD_ERROR_PIPELINE\.',
    ]
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules',
        '.venv', 'venv', '.ledger', '.runs', '.tasks', '.worktrees',
        '.migration_backup_20251120_144334', '.claude', 'AUX_mcp-data',
    }
    
    # File extensions to scan for code references
    CODE_EXTENSIONS = {'.py', '.ps1', '.sh', '.bat'}
    DOC_EXTENSIONS = {'.md', '.rst', '.txt'}
    
    def __init__(self, repo_root: Path):
        """Initialize auditor with repository root."""
        self.repo_root = repo_root
        self.findings = defaultdict(list)
        self.file_references = defaultdict(set)
        
    def audit(self) -> Dict:
        """Run comprehensive audit and return findings."""
        print("Starting comprehensive codebase audit...")
        
        # Scan for different categories
        self._scan_deprecated_directories()
        self._scan_legacy_candidates()
        self._scan_potential_archives()
        self._scan_temporary_files()
        self._scan_duplicate_implementations()
        self._scan_outdated_documentation()
        self._scan_obsolete_files()
        self._analyze_file_activity()
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            'audit_date': datetime.now().isoformat(),
            'repository': str(self.repo_root),
            'summary': summary,
            'findings': dict(self.findings),
        }
    
    def _scan_deprecated_directories(self):
        """Scan for files in known deprecated directories."""
        print("Scanning deprecated directories...")
        
        for dep_dir, reason in self.DEPRECATED_DIRS.items():
            dir_path = self.repo_root / dep_dir
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file() and not self._should_exclude(file_path):
                        self.findings['deprecated'].append({
                            'path': str(file_path.relative_to(self.repo_root)),
                            'category': 'deprecated_directory',
                            'reason': reason,
                            'directory': dep_dir,
                            'size': file_path.stat().st_size,
                            'last_modified': datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat(),
                        })
    
    def _scan_legacy_candidates(self):
        """Scan known legacy/archive candidate directories."""
        print("Scanning legacy candidate directories...")
        
        for legacy_dir, reason in self.LEGACY_CANDIDATES.items():
            dir_path = self.repo_root / legacy_dir
            if dir_path.exists():
                files = list(dir_path.rglob('*'))
                file_count = sum(1 for f in files if f.is_file())
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                self.findings['legacy'].append({
                    'path': legacy_dir,
                    'category': 'legacy_directory',
                    'reason': reason,
                    'file_count': file_count,
                    'total_size': total_size,
                    'recommendation': self._get_legacy_recommendation(legacy_dir),
                })
    
    def _scan_potential_archives(self):
        """Scan for large directories that may be archive candidates."""
        print("Scanning potential archive directories...")
        
        for dir_name in self.POTENTIAL_ARCHIVE_DIRS:
            dir_path = self.repo_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                files = list(dir_path.rglob('*'))
                file_count = sum(1 for f in files if f.is_file())
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                # Determine category based on name patterns
                category = 'archive_candidate'
                reason = self._categorize_archive_directory(dir_name)
                
                self.findings['archive_candidates'].append({
                    'path': dir_name,
                    'category': category,
                    'reason': reason,
                    'file_count': file_count,
                    'total_size': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'recommendation': self._get_archive_recommendation(dir_name),
                })
    
    def _scan_temporary_files(self):
        """Scan for temporary and backup files."""
        print("Scanning for temporary/backup files...")
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file() or self._should_exclude(file_path):
                continue
                
            filename = file_path.name
            rel_path = str(file_path.relative_to(self.repo_root))
            
            # Check against temp patterns
            for pattern in self.TEMP_PATTERNS:
                if re.match(pattern, filename):
                    self.findings['temporary'].append({
                        'path': rel_path,
                        'category': 'temporary_file',
                        'pattern': pattern,
                        'size': file_path.stat().st_size,
                        'last_modified': datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                        'recommendation': 'Delete or move to archive',
                    })
                    break
    
    def _scan_duplicate_implementations(self):
        """Scan for potential duplicate implementations."""
        print("Scanning for duplicate implementations...")
        
        # Track files by basename to find potential duplicates
        basename_map = defaultdict(list)
        
        for file_path in self.repo_root.rglob('*.py'):
            if self._should_exclude(file_path):
                continue
            basename_map[file_path.name].append(file_path)
        
        # Report files with same name in different locations
        for basename, paths in basename_map.items():
            if len(paths) > 1:
                # Filter out __init__.py (expected to have duplicates)
                if basename == '__init__.py':
                    continue
                
                # Check if they're in different top-level directories
                top_dirs = set()
                for p in paths:
                    rel_path = p.relative_to(self.repo_root)
                    if len(rel_path.parts) > 0:
                        top_dirs.add(rel_path.parts[0])
                
                if len(top_dirs) > 1:
                    self.findings['duplicative'].append({
                        'basename': basename,
                        'paths': [str(p.relative_to(self.repo_root)) for p in paths],
                        'category': 'duplicate_basename',
                        'top_level_dirs': list(top_dirs),
                        'recommendation': 'Review for consolidation or clarify purpose',
                    })
    
    def _scan_outdated_documentation(self):
        """Scan documentation for outdated references."""
        print("Scanning for outdated documentation...")
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file() or self._should_exclude(file_path):
                continue
            
            if file_path.suffix not in self.DOC_EXTENSIONS:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                outdated_refs = []
                
                for pattern in self.OUTDATED_DOC_PATTERNS:
                    if re.search(pattern, content):
                        outdated_refs.append(pattern)
                
                if outdated_refs:
                    self.findings['outdated_docs'].append({
                        'path': str(file_path.relative_to(self.repo_root)),
                        'category': 'outdated_documentation',
                        'patterns_found': outdated_refs,
                        'recommendation': 'Update to use new import paths',
                    })
            except (UnicodeDecodeError, PermissionError):
                pass
    
    def _scan_obsolete_files(self):
        """Scan for potentially obsolete files (no references)."""
        print("Scanning for obsolete files...")
        
        # Build reference map first
        self._build_reference_map()
        
        # Check Python files with no imports/references
        for file_path in self.repo_root.rglob('*.py'):
            if self._should_exclude(file_path):
                continue
            
            rel_path = str(file_path.relative_to(self.repo_root))
            
            # Skip __init__.py and test files
            if file_path.name in ('__init__.py', 'conftest.py'):
                continue
            if 'test_' in file_path.name or file_path.name.startswith('test_'):
                continue
            
            # Check if file is referenced
            module_path = self._get_module_path(file_path)
            if module_path and module_path not in self.file_references:
                # File might be obsolete - check if it's a script
                is_script = self._is_executable_script(file_path)
                
                if not is_script:
                    self.findings['obsolete'].append({
                        'path': rel_path,
                        'category': 'potentially_obsolete',
                        'reason': 'No import references found',
                        'recommendation': 'Verify if still needed, consider archival',
                    })
    
    def _build_reference_map(self):
        """Build map of which modules are imported/referenced."""
        print("Building reference map...")
        
        for file_path in self.repo_root.rglob('*.py'):
            if self._should_exclude(file_path):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Parse imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self.file_references[alias.name].add(str(file_path))
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self.file_references[node.module].add(str(file_path))
                except SyntaxError:
                    # Try regex fallback for files with syntax errors
                    imports = re.findall(
                        r'(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))',
                        content
                    )
                    for imp in imports:
                        module = imp[0] or imp[1]
                        if module:
                            self.file_references[module].add(str(file_path))
            except (UnicodeDecodeError, PermissionError):
                pass
    
    def _analyze_file_activity(self):
        """Analyze file modification times to find stale files."""
        print("Analyzing file activity...")
        
        # This would use git log to find files not modified in long time
        # For now, we'll use filesystem mtime as proxy
        # This is a placeholder for more sophisticated git-based analysis
        pass
    
    def _get_module_path(self, file_path: Path) -> Optional[str]:
        """Convert file path to Python module path."""
        try:
            rel_path = file_path.relative_to(self.repo_root)
            parts = list(rel_path.parts)
            
            # Remove .py extension
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            
            # Skip __init__
            if parts[-1] == '__init__':
                parts = parts[:-1]
            
            return '.'.join(parts) if parts else None
        except ValueError:
            return None
    
    def _is_executable_script(self, file_path: Path) -> bool:
        """Check if file appears to be an executable script."""
        try:
            content = file_path.read_text(encoding='utf-8')
            # Check for if __name__ == '__main__' or shebang
            return (
                "if __name__ == '__main__':" in content or
                "if __name__ == \"__main__\":" in content or
                content.startswith('#!')
            )
        except:
            return False
    
    def _categorize_archive_directory(self, dir_name: str) -> str:
        """Categorize why a directory might be an archive candidate."""
        if 'PROTOTYPE' in dir_name:
            return 'Prototype/experimental code - may be superseded'
        elif 'backup' in dir_name.lower() or 'migration' in dir_name.lower():
            return 'Backup directory - should be archived'
        elif 'OPTOMIZE' in dir_name or 'DEEP_DIVE' in dir_name:
            return 'Analysis/optimization data - can be archived'
        elif 'FRAMEWORK' in dir_name:
            return 'Framework code - verify if still in use'
        elif 'final_spec_docs' in dir_name:
            return 'Documentation that may be duplicated in specifications/'
        elif dir_name in ('AI_MANGER', 'AUX_mcp-data', 'CMD'):
            return 'Unclear purpose directory - needs review'
        return 'Large directory - review for potential archival'
    
    def _get_archive_recommendation(self, dir_name: str) -> str:
        """Get recommendation for archive candidate directory."""
        recommendations = {
            'AGENTIC_DEV_PROTOTYPE': 'Archive to docs/archive/prototypes/ - appears superseded by current implementation',
            'PROCESS_DEEP_DIVE_OPTOMIZE': 'Archive to docs/archive/analysis/ - process optimization data',
            'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK': 'Review and archive to docs/archive/frameworks/ if not actively used',
            'Multi-Document Versioning Automation final_spec_docs': 'Consolidate into specifications/ or archive',
            '.migration_backup_20251120_144334': 'Delete after verifying migration succeeded',
            'AI_MANGER': 'Review purpose and either integrate or archive',
            'AUX_mcp-data': 'Review purpose and either integrate or archive',
            'CMD': 'Review purpose and either integrate or archive',
        }
        return recommendations.get(dir_name, 'Review for archival or deletion')
    
    def _get_legacy_recommendation(self, legacy_dir: str) -> str:
        """Get recommendation for legacy directory."""
        recommendations = {
            'build/': 'Move to docs/archive/phase-h-legacy/build/',
            'bundles/': 'Move to workstreams/examples/',
            'pipeline_plus/': 'Move to docs/archive/phase-h-legacy/pipeline_plus/',
            'state/': 'Move database to .worktrees/pipeline_state.db',
        }
        return recommendations.get(legacy_dir, 'Review for archival')
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        path_str = str(path)
        
        # Check excluded directories
        for exclude_dir in self.EXCLUDE_DIRS:
            if f'/{exclude_dir}/' in path_str or path_str.startswith(f'{exclude_dir}/'):
                return True
        
        return False
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        return {
            'total_categories': len(self.findings),
            'deprecated_files': len(self.findings['deprecated']),
            'legacy_directories': len(self.findings['legacy']),
            'archive_candidates': len(self.findings.get('archive_candidates', [])),
            'temporary_files': len(self.findings['temporary']),
            'duplicate_files': len(self.findings['duplicative']),
            'outdated_docs': len(self.findings['outdated_docs']),
            'obsolete_files': len(self.findings['obsolete']),
        }


def generate_markdown_report(audit_results: Dict, output_path: Path):
    """Generate markdown report from audit results."""
    with open(output_path, 'w') as f:
        f.write("# Codebase Audit Report\n\n")
        f.write(f"**Generated:** {audit_results['audit_date']}\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        summary = audit_results['summary']
        f.write(f"- **Deprecated files:** {summary['deprecated_files']}\n")
        f.write(f"- **Legacy directories:** {summary['legacy_directories']}\n")
        f.write(f"- **Archive candidate directories:** {summary.get('archive_candidates', 0)}\n")
        f.write(f"- **Temporary/backup files:** {summary['temporary_files']}\n")
        f.write(f"- **Potential duplicates:** {summary['duplicate_files']}\n")
        f.write(f"- **Outdated documentation:** {summary['outdated_docs']}\n")
        f.write(f"- **Potentially obsolete:** {summary['obsolete_files']}\n\n")
        
        # Deprecated Files
        if audit_results['findings'].get('deprecated'):
            f.write("## Deprecated Files\n\n")
            f.write("Files in legacy directories that should be removed after migration:\n\n")
            for item in audit_results['findings']['deprecated']:
                f.write(f"### `{item['path']}`\n")
                f.write(f"- **Reason:** {item['reason']}\n")
                f.write(f"- **Directory:** {item['directory']}\n")
                f.write(f"- **Size:** {item['size']} bytes\n\n")
        
        # Legacy Directories
        if audit_results['findings'].get('legacy'):
            f.write("## Legacy Directories\n\n")
            for item in audit_results['findings']['legacy']:
                f.write(f"### `{item['path']}`\n")
                f.write(f"- **Reason:** {item['reason']}\n")
                f.write(f"- **Files:** {item['file_count']}\n")
                f.write(f"- **Total size:** {item['total_size']} bytes\n")
                f.write(f"- **Recommendation:** {item['recommendation']}\n\n")
        
        # Archive Candidates
        if audit_results['findings'].get('archive_candidates'):
            f.write("## Archive Candidate Directories\n\n")
            f.write("Large directories that may contain outdated or duplicated content:\n\n")
            for item in audit_results['findings']['archive_candidates']:
                f.write(f"### `{item['path']}`\n")
                f.write(f"- **Reason:** {item['reason']}\n")
                f.write(f"- **Files:** {item['file_count']}\n")
                f.write(f"- **Total size:** {item['size_mb']} MB\n")
                f.write(f"- **Recommendation:** {item['recommendation']}\n\n")
        
        # Temporary Files
        if audit_results['findings'].get('temporary'):
            f.write("## Temporary/Backup Files\n\n")
            for item in audit_results['findings']['temporary']:
                f.write(f"- `{item['path']}` - {item['recommendation']}\n")
            f.write("\n")
        
        # Duplicates
        if audit_results['findings'].get('duplicative'):
            f.write("## Potential Duplicates\n\n")
            for item in audit_results['findings']['duplicative']:
                f.write(f"### `{item['basename']}`\n")
                f.write("Found in:\n")
                for path in item['paths']:
                    f.write(f"- {path}\n")
                f.write(f"\n**Recommendation:** {item['recommendation']}\n\n")
        
        # Outdated Docs
        if audit_results['findings'].get('outdated_docs'):
            f.write("## Outdated Documentation\n\n")
            for item in audit_results['findings']['outdated_docs']:
                f.write(f"- `{item['path']}` - {item['recommendation']}\n")
            f.write("\n")
        
        # Obsolete Files
        if audit_results['findings'].get('obsolete'):
            f.write("## Potentially Obsolete Files\n\n")
            f.write("Files with no apparent references (may be executable scripts or legitimately unused):\n\n")
            for item in audit_results['findings']['obsolete']:
                f.write(f"- `{item['path']}` - {item['reason']}\n")
            f.write("\n")
        
        # Criteria
        f.write("## Audit Criteria\n\n")
        f.write("### Deprecated\n")
        f.write("- Files in `src/pipeline/` (legacy shims)\n")
        f.write("- Files in `MOD_ERROR_PIPELINE/` (legacy error shims)\n\n")
        
        f.write("### Legacy/Archive Candidates\n")
        f.write("- `build/` - Legacy build output\n")
        f.write("- `bundles/` - Misplaced test files\n")
        f.write("- `pipeline_plus/` - Previous implementation\n")
        f.write("- `state/` - Database file location\n\n")
        
        f.write("### Temporary/Backup\n")
        f.write("- Files matching: *.bak, *.old, *.tmp, *~\n")
        f.write("- Files matching: __tmp_*, *_backup_*\n\n")
        
        f.write("### Duplicative\n")
        f.write("- Multiple files with same name in different directories\n\n")
        
        f.write("### Outdated Documentation\n")
        f.write("- Documentation referencing `src.pipeline.*`\n")
        f.write("- Documentation referencing `MOD_ERROR_PIPELINE.*`\n\n")
        
        f.write("### Obsolete\n")
        f.write("- Python files with no import references\n")
        f.write("- Excludes: test files, __init__.py, executable scripts\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        f.write("### Safe Removal Strategy\n\n")
        f.write("1. **Deprecated files**: Remove after Phase 1 grace period (2026-02-19)\n")
        f.write("2. **Legacy directories**: Archive to `docs/archive/phase-h-legacy/`\n")
        f.write("3. **Temporary files**: Delete after backing up\n")
        f.write("4. **Duplicates**: Review and consolidate or document purpose\n")
        f.write("5. **Outdated docs**: Update import references\n")
        f.write("6. **Obsolete files**: Verify unused, then archive or delete\n\n")
        
        f.write("### Archival Process\n\n")
        f.write("```bash\n")
        f.write("# Create archive directory\n")
        f.write("mkdir -p docs/archive/audit-{date}/\n\n")
        f.write("# Move files (don't delete immediately)\n")
        f.write("mv <file> docs/archive/audit-{date}/\n\n")
        f.write("# Document in archive/README.md\n")
        f.write("# Commit with clear message\n")
        f.write("# Wait one sprint before permanent deletion\n")
        f.write("```\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive codebase auditor'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for JSON results (default: codebase_audit.json)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON to stdout'
    )
    parser.add_argument(
        '--markdown',
        type=str,
        help='Generate markdown report at specified path'
    )
    parser.add_argument(
        '--category',
        type=str,
        choices=['deprecated', 'legacy', 'temporary', 'duplicative', 'outdated_docs', 'obsolete'],
        help='Only report specific category'
    )
    
    args = parser.parse_args()
    
    # Find repository root
    repo_root = Path(__file__).parent.parent
    
    # Run audit
    auditor = CodebaseAuditor(repo_root)
    results = auditor.audit()
    
    # Filter by category if specified
    if args.category:
        results['findings'] = {
            args.category: results['findings'].get(args.category, [])
        }
        # Update summary
        for key in results['summary']:
            if key != 'total_categories' and not key.startswith(args.category.replace('_', '')):
                results['summary'][key] = 0
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Audit results written to {output_path}")
    else:
        # Default: write JSON and markdown
        json_path = repo_root / 'codebase_audit.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"JSON results: {json_path}")
        
        md_path = repo_root / 'CODEBASE_AUDIT_REPORT.md'
        generate_markdown_report(results, md_path)
        print(f"Markdown report: {md_path}")
    
    # Generate markdown if requested
    if args.markdown:
        generate_markdown_report(results, Path(args.markdown))
        print(f"Markdown report: {args.markdown}")
    
    print("\nAudit complete!")
    print(f"Found {results['summary']['total_categories']} categories with issues")


if __name__ == '__main__':
    main()
