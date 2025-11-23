#!/usr/bin/env python3
"""
Speed Demon Batch Creator
Parallel file generation using templates

Usage:
    # Extract template from examples
    python batch_create.py --extract --examples file1 file2 --output template.json
    
    # Batch create from template
    python batch_create.py --template template.json --spec batch.json --batch-size 6
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import concurrent.futures


def extract_template(example_files: List[str], output: str) -> None:
    """Extract common template from example files"""
    print(f"📝 Extracting template from {len(example_files)} examples...")
    
    # Read all examples
    examples = []
    for file_path in example_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            examples.append(f.read())
    
    # Identify common structure (simplified - would need actual diff logic)
    template = {
        "structure": "extracted",
        "variables": [],
        "examples_used": example_files
    }
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Template saved to {output}")


def create_file_from_template(template: Dict[str, Any], item: Dict[str, Any], output_path: str) -> bool:
    """Create single file from template and variables"""
    try:
        # Apply template variables to structure
        content = render_template(template, item)
        
        # Write file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"❌ Failed to create {output_path}: {e}")
        return False


def render_template(template: Dict[str, Any], variables: Dict[str, Any]) -> str:
    """Render template with variables (simplified)"""
    # In production, use Jinja2 or similar
    content = str(template)
    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content


def batch_create(template_file: str, spec_file: str, batch_size: int = 6) -> None:
    """Create files in parallel batches"""
    print(f"🚀 Starting batch creation (batch size: {batch_size})...")
    
    # Load template and spec
    with open(template_file, 'r') as f:
        template = json.load(f)
    
    with open(spec_file, 'r') as f:
        spec = json.load(f)
    
    items = spec.get('items', [])
    print(f"📋 Total items to create: {len(items)}")
    
    # Process in batches
    successes = 0
    failures = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        print(f"\n⚡ Processing batch {i//batch_size + 1} ({len(batch)} items)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            for item in batch:
                output = item.get('output_path', f"output/{item.get('name', 'file')}")
                future = executor.submit(create_file_from_template, template, item, output)
                futures.append((future, output))
            
            for future, output in futures:
                if future.result():
                    print(f"  ✓ {output}")
                    successes += 1
                else:
                    print(f"  ✗ {output}")
                    failures += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successes: {successes}")
    print(f"❌ Failures: {failures}")
    print(f"📊 Success rate: {successes/(successes+failures)*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='Speed Demon Batch Creator')
    parser.add_argument('--extract', action='store_true', help='Extract template mode')
    parser.add_argument('--examples', nargs='+', help='Example files for extraction')
    parser.add_argument('--output', help='Output template file')
    parser.add_argument('--template', help='Template file for batch creation')
    parser.add_argument('--spec', help='Batch specification file')
    parser.add_argument('--batch-size', type=int, default=6, help='Batch size (default: 6)')
    
    args = parser.parse_args()
    
    if args.extract:
        if not args.examples or not args.output:
            parser.error('--extract requires --examples and --output')
        extract_template(args.examples, args.output)
    
    elif args.template and args.spec:
        batch_create(args.template, args.spec, args.batch_size)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
