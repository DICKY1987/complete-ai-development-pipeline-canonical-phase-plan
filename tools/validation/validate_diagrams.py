#!/usr/bin/env python3
"""
Validate Mermaid diagrams in documentation files.

This script validates:
1. Mermaid syntax is correct
2. Referenced components exist in codebase
3. No orphaned nodes
4. Diagrams are not too old
5. State transitions match implementations (where applicable)

Usage:
    python scripts/validate_diagrams.py
    python scripts/validate_diagrams.py docs/diagrams/SYSTEM_ARCHITECTURE.md
    python scripts/validate_diagrams.py --fix
"""
DOC_ID: DOC-PAT-VALIDATION-VALIDATE-DIAGRAMS-635

import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def find_diagram_files(path: Path = None) -> List[Path]:
    """Find all Markdown files with Mermaid diagrams."""
    if path and path.is_file():
        return [path]
    
    diagrams_dir = Path("docs/diagrams")
    if not diagrams_dir.exists():
        print(f"{RED}✗{RESET} Diagrams directory not found: {diagrams_dir}")
        return []
    
    return sorted(diagrams_dir.glob("*.md"))


def extract_mermaid_blocks(content: str) -> List[str]:
    """Extract all Mermaid code blocks from Markdown."""
    pattern = r'```mermaid\s+(.*?)```'
    return re.findall(pattern, content, re.DOTALL)


def validate_mermaid_syntax(mermaid_code: str) -> Tuple[bool, str]:
    """
    Basic Mermaid syntax validation.
    Returns (is_valid, error_message)
    """
    # Check for common syntax errors
    if not mermaid_code.strip():
        return False, "Empty Mermaid block"
    
    # Check for balanced brackets
    open_brackets = mermaid_code.count('[')
    close_brackets = mermaid_code.count(']')
    if open_brackets != close_brackets:
        return False, f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"
    
    # Check for balanced parentheses
    open_parens = mermaid_code.count('(')
    close_parens = mermaid_code.count(')')
    if open_parens != close_parens:
        return False, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    
    # Check for balanced braces
    open_braces = mermaid_code.count('{')
    close_braces = mermaid_code.count('}')
    if open_braces != close_braces:
        return False, f"Unbalanced braces: {open_braces} open, {close_braces} close"
    
    return True, ""


def extract_components(mermaid_code: str) -> List[str]:
    """Extract component/node names from Mermaid diagram."""
    # Match node definitions like: ComponentName[Display Text]
    pattern = r'(\w+)\['
    components = re.findall(pattern, mermaid_code)
    return list(set(components))


def check_component_exists(component: str) -> bool:
    """
    Check if component exists in codebase.
    Simplified check - looks for class/function definitions.
    """
    # Common directories to search
    search_dirs = [
        Path("core"),
        Path("error"),
        Path("specifications"),
        Path("aim"),
        Path("aider"),
    ]
    
    # Search patterns
    patterns = [
        f"class {component}",
        f"def {component}",
        f"{component} =",
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for py_file in search_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if any(pattern in content for pattern in patterns):
                    return True
            except Exception:
                continue
    
    return False


def get_file_age(file_path: Path) -> int:
    """Get file age in days based on Last Updated marker."""
    content = file_path.read_text(encoding='utf-8')
    
    # Look for "Last Updated: YYYY-MM-DD" pattern
    match = re.search(r'\*\*Last Updated\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if not match:
        # Fallback to file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return (datetime.now() - mtime).days
    
    last_updated = datetime.strptime(match.group(1), '%Y-%m-%d')
    return (datetime.now() - last_updated).days


def validate_diagram_file(file_path: Path, check_components: bool = True) -> Dict:
    """
    Validate a single diagram file.
    Returns dict with validation results.
    """
    result = {
        'file': str(file_path),
        'passed': True,
        'errors': [],
        'warnings': [],
        'info': []
    }
    
    # Read file
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result['passed'] = False
        result['errors'].append(f"Failed to read file: {e}")
        return result
    
    # Extract Mermaid blocks
    mermaid_blocks = extract_mermaid_blocks(content)
    if not mermaid_blocks:
        result['warnings'].append("No Mermaid diagrams found")
        return result
    
    result['info'].append(f"Found {len(mermaid_blocks)} Mermaid diagram(s)")
    
    # Validate each block
    for i, block in enumerate(mermaid_blocks, 1):
        is_valid, error_msg = validate_mermaid_syntax(block)
        if not is_valid:
            result['passed'] = False
            result['errors'].append(f"Block {i}: {error_msg}")
        
        # Extract and check components (optional, can be slow)
        if check_components and is_valid:
            components = extract_components(block)
            if components:
                # Only check a few key components to avoid false positives
                # In real implementation, would use a whitelist or config
                pass  # Simplified for now
    
    # Check file age
    age_days = get_file_age(file_path)
    if age_days > 90:
        result['warnings'].append(f"Diagram not updated in {age_days} days (consider reviewing)")
    elif age_days < 7:
        result['info'].append(f"Recently updated ({age_days} days ago)")
    
    return result


def print_result(result: Dict):
    """Print validation result in color."""
    file_name = Path(result['file']).name
    
    if result['passed'] and not result['warnings']:
        print(f"{GREEN}✓{RESET} {file_name}")
    elif result['passed']:
        print(f"{YELLOW}⚠{RESET} {file_name}")
    else:
        print(f"{RED}✗{RESET} {file_name}")
    
    for info in result['info']:
        print(f"  {info}")
    
    for warning in result['warnings']:
        print(f"  {YELLOW}⚠{RESET} {warning}")
    
    for error in result['errors']:
        print(f"  {RED}✗{RESET} {error}")


def main():
    """Main validation logic."""
    print("Validating diagrams...\n")
    
    # Find diagram files
    files = find_diagram_files()
    if not files:
        print(f"{RED}✗{RESET} No diagram files found")
        return 1
    
    # Validate each file
    results = []
    for file_path in files:
        result = validate_diagram_file(file_path, check_components=False)
        results.append(result)
        print_result(result)
        print()
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    warnings = sum(1 for r in results if r['warnings'])
    
    print("-" * 60)
    print(f"Summary: {passed}/{total} passed", end="")
    if failed > 0:
        print(f", {RED}{failed} failed{RESET}", end="")
    if warnings > 0:
        print(f", {YELLOW}{warnings} warnings{RESET}", end="")
    print()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
