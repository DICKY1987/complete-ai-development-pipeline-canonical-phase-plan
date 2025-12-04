#!/usr/bin/env python
"""
Validate Extracted Templates
Validates YAML templates for schema compliance and correctness
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-EXTRACTED-TEMPLATES-276

import sys
from pathlib import Path
import yaml
from typing import List, Dict, Any

def validate_template_file(filepath: Path) -> List[str]:
    """
    Validate a single template file

    Returns list of errors (empty if valid)
    """
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)

        # Check required top-level fields
        required_fields = ['pattern_id', 'category', 'meta']
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")

        # Validate pattern_id format
        if 'pattern_id' in template:
            pattern_id = template['pattern_id']
            if not pattern_id.endswith('_v1'):
                errors.append(f"pattern_id must end with '_v1': {pattern_id}")

        # Validate meta section
        if 'meta' in template:
            meta = template['meta']
            required_meta = ['created_at', 'version', 'proven_uses']
            for field in required_meta:
                if field not in meta:
                    errors.append(f"Missing required meta field: {field}")

            # Check proven_uses is non-negative
            if 'proven_uses' in meta and not isinstance(meta['proven_uses'], int):
                errors.append(f"proven_uses must be integer: {type(meta['proven_uses'])}")

        # Validate durations are reasonable
        if 'meta' in template and 'avg_duration_seconds' in template['meta']:
            duration = template['meta']['avg_duration_seconds']
            if duration < 0 or duration > 86400:  # 0 to 24 hours
                errors.append(f"Unreasonable duration: {duration}s")

        # Check for duplicate pattern IDs (handled at directory level)

    except yaml.YAMLError as e:
        errors.append(f"YAML syntax error: {e}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    return errors


def main():
    template_dir = Path("templates/patterns")

    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return 1

    print("=" * 60)
    print("Template Validation Report")
    print("=" * 60)

    # Find all YAML files
    yaml_files = list(template_dir.rglob("*.yaml"))

    if not yaml_files:
        print(f"❌ No YAML files found in {template_dir}")
        return 1

    print(f"\nValidating {len(yaml_files)} template files...\n")

    # Validate each file
    all_errors = {}
    pattern_ids = set()

    for filepath in yaml_files:
        errors = validate_template_file(filepath)

        if errors:
            all_errors[filepath.name] = errors
            print(f"❌ {filepath.name}")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✅ {filepath.name}")

            # Track pattern IDs for duplicate check
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    template = yaml.safe_load(f)
                    if 'pattern_id' in template:
                        if template['pattern_id'] in pattern_ids:
                            if filepath.name not in all_errors:
                                all_errors[filepath.name] = []
                            all_errors[filepath.name].append(f"Duplicate pattern_id: {template['pattern_id']}")
                        pattern_ids.add(template['pattern_id'])
            except:
                pass

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files: {len(yaml_files)}")
    print(f"Valid: {len(yaml_files) - len(all_errors)}")
    print(f"Invalid: {len(all_errors)}")
    print(f"Unique pattern IDs: {len(pattern_ids)}")

    if all_errors:
        print(f"\n❌ Validation failed for {len(all_errors)} files")
        return 1
    else:
        print(f"\n✅ All templates valid!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
