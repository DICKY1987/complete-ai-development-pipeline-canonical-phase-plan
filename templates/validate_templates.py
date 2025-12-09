# Template Validation Script
# Validates templates against standards defined in TEMPLATE_STANDARDS.md

import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

def validate_frontmatter(template_path: Path) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter in template"""
    errors = []
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for frontmatter
    if not content.startswith('---'):
        errors.append("Missing YAML frontmatter")
        return False, errors
    
    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter format")
        return False, errors
    
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return False, errors
    
    # Check required fields
    required_fields = ['doc_id', 'version', 'created', 'last_updated', 
                      'status', 'template_type', 'target_extension']
    
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    # Validate doc_id format
    if 'doc_id' in frontmatter:
        doc_id = frontmatter['doc_id']
        if not doc_id.startswith('DOC-'):
            errors.append(f"doc_id must start with 'DOC-': {doc_id}")
    
    # Validate version format
    if 'version' in frontmatter:
        version = str(frontmatter['version'])
        parts = version.split('.')
        if len(parts) != 3:
            errors.append(f"version must be semver (x.y.z): {version}")
    
    # Validate status
    if 'status' in frontmatter:
        valid_statuses = ['active', 'deprecated', 'draft']
        if frontmatter['status'] not in valid_statuses:
            errors.append(f"status must be one of {valid_statuses}")
    
    return len(errors) == 0, errors

def validate_naming(template_path: Path) -> Tuple[bool, List[str]]:
    """Validate file naming convention"""
    errors = []
    name = template_path.name
    
    # Check for .template extension
    if not name.endswith('.template'):
        errors.append("File must end with '.template'")
        return False, errors
    
    # Check for category prefix
    valid_prefixes = ['doc_', 'code_', 'test_', 'spec_', 'plan_', 'config_']
    has_prefix = any(name.startswith(p) for p in valid_prefixes)
    
    if not has_prefix:
        errors.append(f"File must start with one of: {valid_prefixes}")
    
    return len(errors) == 0, errors

def validate_template(template_path: Path) -> Dict:
    """Validate a single template"""
    result = {
        'path': str(template_path),
        'valid': True,
        'errors': []
    }
    
    # Validate naming
    naming_valid, naming_errors = validate_naming(template_path)
    result['errors'].extend(naming_errors)
    
    # Validate frontmatter
    fm_valid, fm_errors = validate_frontmatter(template_path)
    result['errors'].extend(fm_errors)
    
    result['valid'] = naming_valid and fm_valid
    return result

def main():
    """Validate all templates"""
    templates_dir = Path(__file__).parent
    
    print("🔍 Validating Templates...\n")
    
    results = []
    for template_path in templates_dir.rglob('*.template'):
        result = validate_template(template_path)
        results.append(result)
        
        status = "✅" if result['valid'] else "❌"
        print(f"{status} {result['path']}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"   ⚠️  {error}")
            print()
    
    # Summary
    valid_count = sum(1 for r in results if r['valid'])
    total_count = len(results)
    
    print(f"\n{'='*60}")
    print(f"Summary: {valid_count}/{total_count} templates valid")
    print(f"{'='*60}")
    
    return 0 if valid_count == total_count else 1

if __name__ == '__main__':
    exit(main())
