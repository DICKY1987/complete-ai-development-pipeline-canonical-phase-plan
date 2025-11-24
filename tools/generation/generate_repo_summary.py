#!/usr/bin/env python3
"""
Generate AI-friendly repository summary artifacts.

This script generates:
1. .meta/ai_context/repo_summary.md - Human-readable summary
2. .meta/ai_context/repo_summary.json - Machine-readable metadata

Inputs:
- CODEBASE_INDEX.yaml
- PROJECT_PROFILE.yaml
- docs/ARCHITECTURE.md
- DIRECTORY_GUIDE.md

Output:
- .meta/ai_context/repo_summary.{md,json}
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file with error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: {path} not found, skipping")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing {path}: {e}")
        sys.exit(1)


def load_markdown(path: Path) -> str:
    """Load markdown file content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {path} not found, skipping")
        return ""


def extract_architecture_summary(arch_md: str) -> str:
    """Extract key points from ARCHITECTURE.md."""
    lines = arch_md.split('\n')
    summary_lines = []
    
    # Extract first paragraph after header
    in_summary = False
    for line in lines:
        if line.startswith('## High-Level Architecture'):
            in_summary = True
            continue
        if in_summary:
            if line.startswith('##'):
                break
            if line.strip():
                summary_lines.append(line.strip())
    
    return ' '.join(summary_lines[:3]) if summary_lines else "Multi-phase AI development pipeline with section-based organization."


def generate_summary(
    codebase_index: Dict[str, Any],
    project_profile: Dict[str, Any],
    arch_md: str,
    directory_guide: str
) -> Dict[str, Any]:
    """Generate repository summary data structure."""
    
    metadata = codebase_index.get('metadata', {})
    modules = codebase_index.get('modules', [])
    layers = codebase_index.get('layers', [])
    
    # Build module statistics
    module_count = len(modules)
    layer_distribution = {}
    for layer in layers:
        layer_id = layer['id']
        layer_distribution[layer_id] = len([m for m in modules if m.get('layer') == layer_id])
    
    # Extract key modules (HIGH priority)
    key_modules = [
        {
            'id': m['id'],
            'name': m['name'],
            'path': m['path'],
            'purpose': m.get('purpose', ''),
            'layer': m.get('layer', '')
        }
        for m in modules
        if m.get('ai_priority') == 'HIGH'
    ]
    
    # Build dependency graph stats
    total_dependencies = sum(len(m.get('depends_on', [])) for m in modules)
    
    # Extract architecture summary
    arch_summary = extract_architecture_summary(arch_md)
    
    return {
        'repository': {
            'name': metadata.get('repository', project_profile.get('project_name', 'Unknown')),
            'version': metadata.get('version', project_profile.get('profile_version', '1.0.0')),
            'root': project_profile.get('project_root', '.'),
            'description': arch_summary
        },
        'architecture': {
            'style': 'section-based',
            'layers': [
                {
                    'id': layer['id'],
                    'name': layer['name'],
                    'description': layer.get('description', ''),
                    'module_count': layer_distribution.get(layer['id'], 0)
                }
                for layer in layers
            ]
        },
        'modules': {
            'total': module_count,
            'by_layer': layer_distribution,
            'key_modules': key_modules
        },
        'dependencies': {
            'total_edges': total_dependencies,
            'average_per_module': round(total_dependencies / module_count, 2) if module_count > 0 else 0
        },
        'quality': {
            'test_framework': 'pytest',
            'ci_enforced': True,
            'path_standards': 'section-based imports',
            'validation_scripts': [
                'scripts/validate_workstreams.py',
                'scripts/validate_workstreams_authoring.py',
                'scripts/test.ps1'
            ]
        },
        'documentation': {
            'architecture': 'docs/ARCHITECTURE.md',
            'directory_guide': 'DIRECTORY_GUIDE.md',
            'codebase_index': 'CODEBASE_INDEX.yaml',
            'agents_guide': 'AGENTS.md',
            'documentation_index': 'docs/DOCUMENTATION_INDEX.md'
        },
        'generated': {
            'timestamp': '2025-11-22T20:54:48Z',
            'generator': 'scripts/generate_repo_summary.py',
            'version': '1.0.0'
        }
    }


def generate_markdown(summary: Dict[str, Any]) -> str:
    """Generate human-readable markdown summary."""
    repo = summary['repository']
    arch = summary['architecture']
    modules = summary['modules']
    deps = summary['dependencies']
    quality = summary['quality']
    docs = summary['documentation']
    
    md = f"""# Repository Summary

**Repository**: {repo['name']}  
**Version**: {repo['version']}  
**Generated**: {summary['generated']['timestamp']}

## Overview

{repo['description']}

## Architecture

**Style**: {arch['style']}  
**Layers**: {len(arch['layers'])}

"""
    
    for layer in arch['layers']:
        md += f"- **{layer['name']}** (`{layer['id']}`): {layer['description']} ({layer['module_count']} modules)\n"
    
    md += f"""

## Modules

**Total Modules**: {modules['total']}  
**Module Distribution**:

"""
    
    for layer_id, count in modules['by_layer'].items():
        md += f"- {layer_id}: {count} modules\n"
    
    md += "\n### Key Modules (HIGH Priority)\n\n"
    
    for mod in modules['key_modules']:
        md += f"- **{mod['name']}** (`{mod['id']}`)\n"
        md += f"  - Path: `{mod['path']}`\n"
        md += f"  - Layer: `{mod['layer']}`\n"
        md += f"  - Purpose: {mod['purpose']}\n\n"
    
    md += f"""## Dependencies

**Total Dependency Edges**: {deps['total_edges']}  
**Average Dependencies per Module**: {deps['average_per_module']}

## Quality & Testing

- **Test Framework**: {quality['test_framework']}
- **CI Enforcement**: {'Yes' if quality['ci_enforced'] else 'No'}
- **Path Standards**: {quality['path_standards']}

**Validation Scripts**:
"""
    
    for script in quality['validation_scripts']:
        md += f"- `{script}`\n"
    
    md += "\n## Documentation\n\n"
    
    for doc_name, doc_path in docs.items():
        md += f"- **{doc_name.replace('_', ' ').title()}**: `{doc_path}`\n"
    
    md += f"""

---

*Generated by `{summary['generated']['generator']}` v{summary['generated']['version']}*
"""
    
    return md


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("Loading repository data...")
    
    # Load source files
    codebase_index = load_yaml(repo_root / 'CODEBASE_INDEX.yaml')
    project_profile = load_yaml(repo_root / 'PROJECT_PROFILE.yaml')
    arch_md = load_markdown(repo_root / 'docs' / 'ARCHITECTURE.md')
    directory_guide = load_markdown(repo_root / 'DIRECTORY_GUIDE.md')
    
    if not codebase_index:
        print("Error: CODEBASE_INDEX.yaml is required")
        sys.exit(1)
    
    print("Generating summary data...")
    summary = generate_summary(codebase_index, project_profile, arch_md, directory_guide)
    
    # Ensure output directory exists
    output_dir = repo_root / '.meta' / 'ai_context'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    json_path = output_dir / 'repo_summary.json'
    print(f"Writing {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Write Markdown
    md_path = output_dir / 'repo_summary.md'
    print(f"Writing {md_path}...")
    markdown = generate_markdown(summary)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✓ Repository summary generated successfully")
    print(f"  - JSON: {json_path}")
    print(f"  - Markdown: {md_path}")
    print(f"\nSummary: {summary['modules']['total']} modules, {summary['dependencies']['total_edges']} dependencies")


if __name__ == '__main__':
    main()
