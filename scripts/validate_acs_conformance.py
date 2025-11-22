#!/usr/bin/env python3
"""
Validate ACS (AI Codebase Structure) conformance.

This script validates that:
1. All modules in CODEBASE_INDEX.yaml exist on disk
2. All paths in ai_policies.yaml are valid
3. MODULE.md files cross-reference CODEBASE_INDEX correctly
4. Code graph matches actual module structure
5. All required ACS artifacts are present

Exit codes:
  0 - All validations passed
  1 - Validation failures found
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file with error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except yaml.YAMLError as e:
        print(f"{Colors.RED}✗ Error parsing {path}: {e}{Colors.RESET}")
        return {}


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}✗ Error parsing {path}: {e}{Colors.RESET}")
        return {}


def check_required_artifacts(repo_root: Path) -> Tuple[bool, List[str]]:
    """Check that all required ACS artifacts exist."""
    required = {
        'CODEBASE_INDEX.yaml': repo_root / 'CODEBASE_INDEX.yaml',
        'QUALITY_GATE.yaml': repo_root / 'QUALITY_GATE.yaml',
        'ai_policies.yaml': repo_root / 'ai_policies.yaml',
        '.aiignore': repo_root / '.aiignore',
        '.meta/AI_GUIDANCE.md': repo_root / '.meta' / 'AI_GUIDANCE.md',
        '.meta/ai_context/repo_summary.json': repo_root / '.meta' / 'ai_context' / 'repo_summary.json',
        '.meta/ai_context/code_graph.json': repo_root / '.meta' / 'ai_context' / 'code_graph.json',
    }
    
    missing = []
    for name, path in required.items():
        if not path.exists():
            missing.append(name)
    
    return len(missing) == 0, missing


def validate_module_paths(codebase_index: Dict[str, Any], repo_root: Path) -> Tuple[bool, List[str]]:
    """Validate that all modules in CODEBASE_INDEX exist on disk."""
    modules = codebase_index.get('modules', [])
    invalid = []
    
    for module in modules:
        module_id = module.get('id', 'unknown')
        module_path = module.get('path', '')
        
        if not module_path:
            invalid.append(f"{module_id}: No path specified")
            continue
        
        full_path = repo_root / module_path
        if not full_path.exists():
            invalid.append(f"{module_id}: Path '{module_path}' does not exist")
    
    return len(invalid) == 0, invalid


def validate_policy_paths(ai_policies: Dict[str, Any], repo_root: Path) -> Tuple[bool, List[str]]:
    """Validate that paths in ai_policies.yaml are valid glob patterns."""
    zones = ai_policies.get('zones', {})
    invalid = []
    
    for zone_name, zone_data in zones.items():
        paths = zone_data.get('paths', [])
        for pattern in paths:
            # Basic validation - check if it's a reasonable pattern
            if not pattern:
                invalid.append(f"{zone_name}: Empty path pattern")
                continue
            
            # Check for obvious issues
            if pattern.startswith('/') and not pattern.startswith('//'):
                invalid.append(f"{zone_name}: Absolute path '{pattern}' (should be relative)")
    
    return len(invalid) == 0, invalid


def validate_module_references(repo_root: Path, codebase_index: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check that MODULE.md files exist for key modules."""
    modules = codebase_index.get('modules', [])
    missing_docs = []
    
    # Check for MODULE.md or README.md in each module
    for module in modules:
        module_path = module.get('path', '')
        if not module_path:
            continue
        
        full_path = repo_root / module_path
        if not full_path.exists():
            continue
        
        # Look for MODULE.md or README.md
        has_doc = (full_path / 'MODULE.md').exists() or (full_path / 'README.md').exists()
        
        # Only flag HIGH priority modules without docs
        if not has_doc and module.get('ai_priority') == 'HIGH':
            missing_docs.append(f"{module.get('id')}: No MODULE.md or README.md in {module_path}")
    
    return len(missing_docs) == 0, missing_docs


def validate_dependency_references(codebase_index: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that all dependency references are valid module IDs."""
    modules = codebase_index.get('modules', [])
    module_ids = {m['id'] for m in modules}
    invalid = []
    
    for module in modules:
        module_id = module.get('id', 'unknown')
        depends_on = module.get('depends_on', [])
        
        for dep_id in depends_on:
            if dep_id not in module_ids:
                invalid.append(f"{module_id}: Unknown dependency '{dep_id}'")
    
    return len(invalid) == 0, invalid


def validate_code_graph(code_graph: Dict[str, Any], codebase_index: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate code graph consistency with CODEBASE_INDEX."""
    issues = []
    
    # Check metadata
    metadata = code_graph.get('metadata', {})
    if not metadata.get('validation', {}).get('acyclic', False):
        issues.append("Code graph is not acyclic (contains cycles)")
    
    # Check node count matches modules
    graph = code_graph.get('graph', {})
    nodes = graph.get('nodes', [])
    modules = codebase_index.get('modules', [])
    
    if len(nodes) != len(modules):
        issues.append(f"Node count mismatch: {len(nodes)} nodes vs {len(modules)} modules")
    
    # Check all module IDs present in graph
    node_ids = {n['id'] for n in nodes}
    module_ids = {m['id'] for m in modules}
    
    missing = module_ids - node_ids
    if missing:
        issues.append(f"Modules missing from graph: {', '.join(missing)}")
    
    extra = node_ids - module_ids
    if extra:
        issues.append(f"Extra nodes in graph: {', '.join(extra)}")
    
    return len(issues) == 0, issues


def validate_invariants(ai_policies: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check that invariants are well-defined."""
    invariants = ai_policies.get('invariants', [])
    issues = []
    
    required_fields = ['id', 'name', 'description', 'enforcement']
    
    for inv in invariants:
        inv_id = inv.get('id', 'unknown')
        
        for field in required_fields:
            if field not in inv:
                issues.append(f"Invariant {inv_id}: Missing field '{field}'")
    
    return len(issues) == 0, issues


def print_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_result(passed: bool, message: str, details: List[str] = None):
    """Print a validation result."""
    if passed:
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
        if details:
            for detail in details:
                print(f"  {Colors.YELLOW}→{Colors.RESET} {detail}")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print(f"\n{Colors.BOLD}ACS Conformance Validator{Colors.RESET}")
    print(f"Repository: {repo_root}")
    
    # Track overall status
    all_passed = True
    
    # 1. Check required artifacts
    print_section("1. Required Artifacts")
    passed, missing = check_required_artifacts(repo_root)
    print_result(passed, "All required ACS artifacts present", missing if not passed else None)
    all_passed &= passed
    
    # Load artifacts
    codebase_index = load_yaml(repo_root / 'CODEBASE_INDEX.yaml')
    ai_policies = load_yaml(repo_root / 'ai_policies.yaml')
    code_graph = load_json(repo_root / '.meta' / 'ai_context' / 'code_graph.json')
    
    if not codebase_index:
        print(f"\n{Colors.RED}✗ Cannot proceed without CODEBASE_INDEX.yaml{Colors.RESET}")
        sys.exit(1)
    
    # 2. Validate module paths
    print_section("2. Module Paths")
    passed, invalid = validate_module_paths(codebase_index, repo_root)
    print_result(passed, f"All {len(codebase_index.get('modules', []))} module paths valid", invalid if not passed else None)
    all_passed &= passed
    
    # 3. Validate policy paths
    print_section("3. Policy Paths")
    if ai_policies:
        passed, invalid = validate_policy_paths(ai_policies, repo_root)
        print_result(passed, "All policy paths are valid patterns", invalid if not passed else None)
        all_passed &= passed
    else:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} ai_policies.yaml not found (skipping)")
    
    # 4. Validate module documentation
    print_section("4. Module Documentation")
    passed, missing = validate_module_references(repo_root, codebase_index)
    print_result(passed, "All HIGH priority modules have documentation", missing if not passed else None)
    all_passed &= passed
    
    # 5. Validate dependency references
    print_section("5. Dependency References")
    passed, invalid = validate_dependency_references(codebase_index)
    print_result(passed, "All dependency references are valid", invalid if not passed else None)
    all_passed &= passed
    
    # 6. Validate code graph
    print_section("6. Code Graph Consistency")
    if code_graph:
        passed, issues = validate_code_graph(code_graph, codebase_index)
        print_result(passed, "Code graph consistent with CODEBASE_INDEX", issues if not passed else None)
        all_passed &= passed
    else:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} code_graph.json not found (skipping)")
    
    # 7. Validate invariants
    print_section("7. Invariant Definitions")
    if ai_policies:
        passed, issues = validate_invariants(ai_policies)
        print_result(passed, f"All {len(ai_policies.get('invariants', []))} invariants well-defined", issues if not passed else None)
        all_passed &= passed
    
    # Summary
    print_section("Summary")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All ACS conformance checks passed{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some ACS conformance checks failed{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Review the issues above and fix them.{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
