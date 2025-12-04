#!/usr/bin/env python3
"""
Build MODULE_DOC_MAP.yaml from DOC_ID_REGISTRY.yaml

Generates a module-centric view of all documentation.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Repository root
REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "doc_id" / "specs" / "DOC_ID_REGISTRY.yaml"
TAXONOMY_PATH = REPO_ROOT / "doc_id" / "specs" / "module_taxonomy.yaml"
OUTPUT_PATH = REPO_ROOT / "modules" / "MODULE_DOC_MAP.yaml"


def load_yaml_file(path: Path):
    """Load YAML file with proper encoding"""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def infer_doc_kind(doc):
    """Infer document kind from category and artifacts"""
    category = doc.get('category', 'unknown')
    artifacts = doc.get('artifacts', [])

    # Check artifact types
    artifact_types = {a.get('type') for a in artifacts}

    if 'spec' in artifact_types:
        return 'spec'
    if 'source' in artifact_types:
        return 'source'
    if 'doc' in artifact_types:
        return 'doc'
    if 'test' in artifact_types:
        return 'test'

    # Fallback to category
    if category in ['patterns', 'spec']:
        return 'spec'
    if category in ['test']:
        return 'test'
    if category in ['guide', 'arch']:
        return 'doc'
    if category in ['core', 'error', 'aim', 'pm']:
        return 'source'

    return 'doc'


def get_primary_path(doc):
    """Get primary artifact path"""
    artifacts = doc.get('artifacts', [])

    for artifact in artifacts:
        if artifact.get('type') in ['doc', 'spec', 'source']:
            return artifact.get('path', '')

    if artifacts:
        return artifacts[0].get('path', '')

    return None


def get_module_description(module_id, taxonomy):
    """Get module description from taxonomy"""
    if not taxonomy or 'module_taxonomy' not in taxonomy:
        return f"Module: {module_id}"

    module_def = taxonomy['module_taxonomy'].get(module_id, {})
    return module_def.get('description', f"Module: {module_id}")


def build_module_map():
    """Build module map from registry"""
    print("Building MODULE_DOC_MAP.yaml...")

    # Load registry
    print(f"  Loading registry: {REGISTRY_PATH}")
    registry = load_yaml_file(REGISTRY_PATH)

    # Load taxonomy
    taxonomy = None
    if TAXONOMY_PATH.exists():
        print(f"  Loading taxonomy: {TAXONOMY_PATH}")
        taxonomy = load_yaml_file(TAXONOMY_PATH)

    # Group docs by module_id
    print("  Grouping docs by module_id...")
    modules = defaultdict(list)

    for doc in registry.get('docs', []):
        module_id = doc.get('module_id', 'unassigned')

        modules[module_id].append({
            'doc_id': doc['doc_id'],
            'category': doc.get('category', 'unknown'),
            'kind': infer_doc_kind(doc),
            'path': get_primary_path(doc),
            'title': doc.get('title', doc.get('name', '')),
        })

    # Build output structure
    module_map = {
        'metadata': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'source_registry': str(REGISTRY_PATH),
            'total_modules': len(modules),
            'total_docs': len(registry.get('docs', [])),
        },
        'modules': {}
    }

    # Add module descriptions and docs
    print(f"  Building module map for {len(modules)} modules...")
    for module_id in sorted(modules.keys()):
        docs = modules[module_id]

        module_map['modules'][module_id] = {
            'description': get_module_description(module_id, taxonomy),
            'doc_count': len(docs),
            'docs': docs
        }

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Writing output: {OUTPUT_PATH}")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(module_map, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n==> Module map created successfully!")
    print(f"   Modules: {len(modules)}")
    print(f"   Total docs: {len(registry.get('docs', []))}")
    print(f"   Output: {OUTPUT_PATH}")

    # Print summary by module
    print("\n==> Module Summary:")
    for module_id in sorted(modules.keys(), key=lambda x: (-len(modules[x]), x)):
        doc_count = len(modules[module_id])
        print(f"   {module_id:30} {doc_count:4} docs")


def main():
    """Main entry point"""
    try:
        build_module_map()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
