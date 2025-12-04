#!/usr/bin/env python3
"""
Batch file creation with parallel execution

Usage:
    python batch_create.py --template templates/my.template --spec batch.json
"""
# DOC_ID: DOC-PAT-SPEED-DEMON-BATCH-CREATE-632
import argparse
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import re


def fill_template(template_content: str, variables: Dict[str, str]) -> str:
    """Replace {{VARIABLE}} placeholders with actual values"""
    result = template_content
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def create_file(template_path: str, output_path: str, variables: Dict[str, str]) -> Dict:
    """Create single file from template"""
    try:
        with open(template_path) as f:
            template = f.read()

        content = fill_template(template, variables)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)

        return {
            'path': output_path,
            'status': 'success',
            'lines': len(content.splitlines())
        }
    except Exception as e:
        return {
            'path': output_path,
            'status': 'error',
            'error': str(e)
        }


def batch_create(template_path: str, batch_spec: Dict) -> List[Dict]:
    """Create multiple files in parallel"""
    specs = batch_spec.get('specs', [])
    max_workers = min(6, len(specs))  # Max 6 parallel operations

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(create_file, template_path, spec['output'], spec['variables'])
            for spec in specs
        ]
        results = [f.result() for f in futures]

    return results


def main():
    parser = argparse.ArgumentParser(description="Batch create files from template")
    parser.add_argument("--template", required=True, help="Template file path")
    parser.add_argument("--spec", required=True, help="Batch specification JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    args = parser.parse_args()

    # Load batch spec
    with open(args.spec) as f:
        batch_spec = json.load(f)

    if args.dry_run:
        print(f"Would create {len(batch_spec['specs'])} files:")
        for spec in batch_spec['specs']:
            print(f"  - {spec['output']}")
        return

    # Execute batch creation
    print(f"Creating {len(batch_spec['specs'])} files from {args.template}...")
    results = batch_create(args.template, batch_spec)

    # Report results
    successes = [r for r in results if r['status'] == 'success']
    failures = [r for r in results if r['status'] == 'error']

    print(f"\n✓ Created {len(successes)}/{len(results)} files successfully:")
    for r in successes:
        print(f"  ✓ {r['path']} ({r['lines']} lines)")

    if failures:
        print(f"\n✗ {len(failures)} failures:")
        for r in failures:
            print(f"  ✗ {r['path']}: {r['error']}")
        exit(1)


if __name__ == "__main__":
    main()
