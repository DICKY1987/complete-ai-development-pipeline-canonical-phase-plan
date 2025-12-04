"""
Import Path Analysis - Week 2 Day 1

Analyzes all import statements in Python files to understand:
- Current import patterns
- Module dependencies
- Deprecated imports
- Cross-module references

Usage:
    python scripts/analyze_imports.py
    python scripts/analyze_imports.py --path modules/

Output:
    import_analysis_report.yaml
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-IMPORTS-189
# DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-IMPORTS-126

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import yaml


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import statements."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.imports = []

    def visit_Import(self, node):
        """Handle 'import X' statements."""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Handle 'from X import Y' statements."""
        module = node.module or ''
        for alias in node.names:
            self.imports.append({
                'type': 'from_import',
                'module': module,
                'name': alias.name,
                'alias': alias.asname,
                'line': node.lineno,
                'level': node.level  # For relative imports
            })
        self.generic_visit(node)


def analyze_file(filepath: Path) -> List[Dict]:
    """Analyze imports in a single Python file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))

        analyzer = ImportAnalyzer(filepath)
        analyzer.visit(tree)

        return analyzer.imports
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return []


def categorize_import(import_info: Dict) -> str:
    """Categorize an import based on its module path."""
    module = import_info.get('module', '')

    # Deprecated paths
    if module.startswith('src.'):
        return 'deprecated_src'
    if module.startswith('MOD_ERROR_PIPELINE.'):
        return 'deprecated_mod'

    # Project modules (old structure)
    if module.startswith('core.'):
        return 'project_core'
    if module.startswith('error.'):
        return 'project_error'
    if module.startswith('aim.'):
        return 'project_aim'
    if module.startswith('pm.'):
        return 'project_pm'
    if module.startswith('specifications.'):
        return 'project_specifications'

    # New module structure
    if module.startswith('modules.'):
        return 'migrated_modules'

    # Relative imports
    if import_info.get('level', 0) > 0:
        return 'relative_import'

    # External/stdlib
    if not module or '.' not in module:
        return 'external_stdlib'

    # Check if it's a known third-party
    external_prefixes = ['yaml', 'pytest', 'pathlib', 'typing', 'dataclasses',
                        'click', 'requests', 'jinja2', 'pydantic']
    for prefix in external_prefixes:
        if module.startswith(prefix):
            return 'external_third_party'

    return 'other'


def analyze_directory(directory: Path) -> Dict:
    """Analyze all Python files in a directory."""
    results = {
        'files_analyzed': 0,
        'total_imports': 0,
        'by_category': defaultdict(int),
        'by_module': defaultdict(lambda: defaultdict(int)),
        'deprecated_files': [],
        'import_sources': defaultdict(set),
        'cross_module_refs': []
    }

    # Find all Python files
    py_files = list(directory.rglob("*.py"))

    for py_file in py_files:
        # Skip __pycache__ and .venv
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue

        imports = analyze_file(py_file)

        if not imports:
            continue

        results['files_analyzed'] += 1
        results['total_imports'] += len(imports)

        # Categorize each import
        has_deprecated = False
        for imp in imports:
            category = categorize_import(imp)
            results['by_category'][category] += 1

            module = imp.get('module', '')
            if module:
                results['by_module'][category][module] += 1
                results['import_sources'][module].add(str(py_file))

            if category.startswith('deprecated'):
                has_deprecated = True

            # Track cross-module references (old -> new structure)
            if category in ['project_core', 'project_error', 'project_aim',
                           'project_pm', 'project_specifications']:
                results['cross_module_refs'].append({
                    'file': str(py_file.relative_to(directory)),
                    'import': imp.get('module', ''),
                    'line': imp.get('line', 0)
                })

        if has_deprecated:
            results['deprecated_files'].append(str(py_file.relative_to(directory)))

    # Convert sets to lists for YAML serialization
    results['import_sources'] = {
        module: sorted(list(files))
        for module, files in results['import_sources'].items()
    }

    return results


def generate_conversion_rules(results: Dict) -> List[Dict]:
    """Generate import conversion rules from analysis."""
    rules = []

    # Analyze project imports that need conversion
    for category in ['project_core', 'project_error', 'project_aim',
                     'project_pm', 'project_specifications']:
        modules = results['by_module'].get(category, {})

        for module_path in sorted(modules.keys()):
            # Generate conversion rule
            # Example: core.state.db -> modules.core_state.010003_db

            parts = module_path.split('.')
            if len(parts) >= 2:
                # Determine target module
                section = parts[0]  # core, error, aim, etc.
                submodule = parts[1] if len(parts) > 1 else ''
                file = parts[-1] if len(parts) > 2 else ''

                # Map to module ID format
                module_id = f"{section}-{submodule}".replace('_', '-')

                rule = {
                    'old_pattern': f"from {module_path} import",
                    'old_module': module_path,
                    'target_module_id': module_id,
                    'note': 'ULID and file name to be determined from MODULES_INVENTORY.yaml',
                    'occurrences': modules[module_path]
                }

                rules.append(rule)

    return rules


def main():
    """Main analysis entry point."""
    # Determine directory to analyze
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path(".")

    if not directory.exists():
        print(f"Directory not found: {directory}")
        sys.exit(1)

    print(f"Analyzing imports in: {directory}")
    print(f"Scanning Python files...\n")

    # Analyze
    results = analyze_directory(directory)

    # Print summary
    print(f"Files analyzed: {results['files_analyzed']}")
    print(f"Total imports: {results['total_imports']}\n")

    print("Import categories:")
    for category, count in sorted(results['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")

    print(f"\nFiles with deprecated imports: {len(results['deprecated_files'])}")
    print(f"Cross-module references to rewrite: {len(results['cross_module_refs'])}")

    # Generate conversion rules
    conversion_rules = generate_conversion_rules(results)

    # Save report
    report = {
        'analysis_date': '2025-11-26',
        'directory': str(directory),
        'summary': {
            'files_analyzed': results['files_analyzed'],
            'total_imports': results['total_imports'],
            'deprecated_count': results['by_category']['deprecated_src'] +
                              results['by_category']['deprecated_mod'],
            'cross_module_count': len(results['cross_module_refs'])
        },
        'by_category': dict(results['by_category']),
        'by_module': {k: dict(v) for k, v in results['by_module'].items()},
        'deprecated_files': results['deprecated_files'],
        'cross_module_refs': results['cross_module_refs'][:50],  # First 50 for brevity
        'conversion_rules_needed': len(conversion_rules),
        'sample_conversion_rules': conversion_rules[:10]  # First 10 as examples
    }

    report_path = Path("import_analysis_report.yaml")
    with report_path.open('w', encoding='utf-8') as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    print(f"\nReport saved to: {report_path}")
    print(f"\nNext steps:")
    print(f"  1. Review {report_path}")
    print(f"  2. Create conversion rules from analysis")
    print(f"  3. Run import rewriter")


if __name__ == "__main__":
    main()
