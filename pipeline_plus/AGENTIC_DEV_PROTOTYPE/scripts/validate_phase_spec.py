#!/usr/bin/env python3
"""
Validation script for phase specifications.
Checks phase spec files against schema and business rules before execution.

Usage:
    python validate_phase_spec.py phase_specs/phase_0_bootstrap.json
    python validate_phase_spec.py --all phase_specs/
    python validate_phase_spec.py --plan master_phase_plan.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class PhaseSpecValidator:
    """Validates phase specifications against schema and business rules"""
    
    def __init__(self, schema_path: Path = None):
        self.schema_path = schema_path or Path("config/schema.json")
        self.schema = self._load_schema()
        self.errors = []
        self.warnings = []
        
    def _load_schema(self) -> Dict:
        """Load JSON schema for validation"""
        if not self.schema_path.exists():
            print(f"{Colors.YELLOW}Warning: Schema file not found at {self.schema_path}{Colors.RESET}")
            return {}
        
        with open(self.schema_path) as f:
            return json.load(f)
    
    def validate_file(self, spec_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a single phase spec file.
        Returns: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check file exists
        if not spec_path.exists():
            self.errors.append(f"File not found: {spec_path}")
            return False, self.errors, self.warnings
        
        # Load JSON
        try:
            with open(spec_path) as f:
                spec = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        
        # Validate against schema
        self._validate_schema(spec)
        
        # Validate business rules
        self._validate_business_rules(spec)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_schema(self, spec: Dict):
        """Validate spec against JSON schema"""
        required_fields = self.schema.get('required', [])
        
        # Check required fields
        for field in required_fields:
            if field not in spec:
                self.errors.append(f"Missing required field: '{field}'")
        
        # Validate phase_id format
        if 'phase_id' in spec:
            if not re.match(r'^PH-[0-9A-Z]+$', spec['phase_id']):
                self.errors.append(f"Invalid phase_id format: '{spec['phase_id']}' (must match PH-XX)")
        
        # Validate file_scope is not empty
        if 'file_scope' in spec:
            if not isinstance(spec['file_scope'], list) or len(spec['file_scope']) == 0:
                self.errors.append("file_scope must be a non-empty array")
        
        # Validate acceptance_tests structure
        if 'acceptance_tests' in spec:
            if not isinstance(spec['acceptance_tests'], list):
                self.errors.append("acceptance_tests must be an array")
            elif len(spec['acceptance_tests']) == 0:
                self.errors.append("acceptance_tests must contain at least one test")
            else:
                for i, test in enumerate(spec['acceptance_tests']):
                    required_test_fields = ['test_id', 'description', 'command', 'expected']
                    for field in required_test_fields:
                        if field not in test:
                            self.errors.append(f"acceptance_tests[{i}] missing field: '{field}'")
    
    def _validate_business_rules(self, spec: Dict):
        """Validate business rules and best practices"""
        
        # Rule: Objective should be meaningful (not too short)
        if 'objective' in spec:
            if len(spec['objective']) < 10:
                self.warnings.append("Objective seems too short (< 10 chars)")
        
        # Rule: Dependencies should reference valid phase IDs
        if 'dependencies' in spec:
            for dep in spec['dependencies']:
                if not re.match(r'^PH-[0-9A-Z]+$', dep):
                    self.errors.append(f"Invalid dependency format: '{dep}'")
        
        # Rule: Acceptance tests should have CLI commands
        if 'acceptance_tests' in spec:
            for i, test in enumerate(spec['acceptance_tests']):
                if 'command' in test and not test['command'].strip():
                    self.errors.append(f"acceptance_tests[{i}] has empty command")
        
        # Rule: Pre-flight checks should be present for phases with dependencies
        if spec.get('dependencies') and not spec.get('pre_flight_checks'):
            self.warnings.append("Phase has dependencies but no pre_flight_checks")
        
        # Rule: Estimated effort should be reasonable
        if 'estimated_effort_hours' in spec:
            hours = spec['estimated_effort_hours']
            if hours > 40:
                self.warnings.append(f"Estimated effort seems high ({hours} hours)")
            elif hours < 1:
                self.warnings.append(f"Estimated effort seems low ({hours} hours)")


def validate_phase_plan(plan_path: Path) -> bool:
    """Validate master phase plan structure and dependencies"""
    try:
        with open(plan_path) as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}✗ Invalid JSON in plan: {e}{Colors.RESET}")
        return False
    
    errors = []
    
    # Check required plan fields
    required_fields = ['plan_name', 'phases', 'execution_order']
    for field in required_fields:
        if field not in plan:
            errors.append(f"Missing required field: '{field}'")
    
    # Build phase ID set
    phase_ids = {p['phase_id'] for p in plan.get('phases', [])}
    
    # Validate dependencies reference existing phases
    for phase in plan.get('phases', []):
        for dep in phase.get('dependencies', []):
            if dep not in phase_ids:
                errors.append(f"Phase {phase['phase_id']} references non-existent dependency: {dep}")
    
    # Check for circular dependencies (simple check)
    # TODO: Implement full cycle detection
    
    if errors:
        print(f"{Colors.RED}✗ Plan validation failed:{Colors.RESET}")
        for error in errors:
            print(f"  • {error}")
        return False
    
    print(f"{Colors.GREEN}✓ Plan validation passed{Colors.RESET}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Validate phase specification files')
    parser.add_argument('path', help='Path to phase spec file or directory')
    parser.add_argument('--all', action='store_true', help='Validate all specs in directory')
    parser.add_argument('--plan', action='store_true', help='Validate master phase plan')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    path = Path(args.path)
    
    # Validate plan
    if args.plan:
        success = validate_phase_plan(path)
        sys.exit(0 if success else 1)
    
    # Validate all specs in directory
    if args.all:
        if not path.is_dir():
            print(f"{Colors.RED}✗ Path is not a directory: {path}{Colors.RESET}")
            sys.exit(1)
        
        spec_files = list(path.glob('*.json'))
        if not spec_files:
            print(f"{Colors.YELLOW}No JSON files found in {path}{Colors.RESET}")
            sys.exit(1)
        
        print(f"{Colors.CYAN}Validating {len(spec_files)} phase specs...{Colors.RESET}\n")
        
        validator = PhaseSpecValidator()
        total_valid = 0
        total_invalid = 0
        
        for spec_file in sorted(spec_files):
            is_valid, errors, warnings = validator.validate_file(spec_file)
            
            if is_valid:
                print(f"{Colors.GREEN}✓{Colors.RESET} {spec_file.name}")
                total_valid += 1
                
                if warnings and args.verbose:
                    for warning in warnings:
                        print(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
            else:
                print(f"{Colors.RED}✗{Colors.RESET} {spec_file.name}")
                total_invalid += 1
                
                for error in errors:
                    print(f"  {Colors.RED}•{Colors.RESET} {error}")
                
                if warnings:
                    for warning in warnings:
                        print(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        
        print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  Valid: {Colors.GREEN}{total_valid}{Colors.RESET}")
        print(f"  Invalid: {Colors.RED}{total_invalid}{Colors.RESET}")
        
        sys.exit(0 if total_invalid == 0 else 1)
    
    # Validate single spec file
    if not path.is_file():
        print(f"{Colors.RED}✗ File not found: {path}{Colors.RESET}")
        sys.exit(1)
    
    validator = PhaseSpecValidator()
    is_valid, errors, warnings = validator.validate_file(path)
    
    if is_valid:
        print(f"{Colors.GREEN}✓ Phase spec is valid: {path.name}{Colors.RESET}")
        
        if warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.RESET}")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        
        sys.exit(0)
    else:
        print(f"{Colors.RED}✗ Phase spec is invalid: {path.name}{Colors.RESET}\n")
        print(f"{Colors.RED}Errors:{Colors.RESET}")
        for error in errors:
            print(f"  • {error}")
        
        if warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.RESET}")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        
        sys.exit(1)


if __name__ == '__main__':
    main()
