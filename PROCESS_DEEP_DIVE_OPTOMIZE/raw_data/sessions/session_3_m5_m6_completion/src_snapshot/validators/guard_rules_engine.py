#!/usr/bin/env python3
"""
Guard Rules Engine - PH-2B

Enforces semantic validation rules and anti-patterns from DEV_RULES specification.
Provides business logic validation beyond schema checking.
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple


class GuardRulesEngine:
    """Enforce development rules and detect anti-patterns."""
    
    def __init__(
        self,
        dr_spec_path: str = "specs/DEV_RULES_V1.md",
        dr_index_path: str = "specs/metadata/dr_index.json"
    ):
        self.dr_spec_path = Path(dr_spec_path)
        self.dr_index_path = Path(dr_index_path)
        self.dr_index = self._load_dr_index()
        self.rules = self._load_rules()
    
    def _load_dr_index(self) -> Dict[str, Any]:
        """Load Development Rules index."""
        if not self.dr_index_path.exists():
            return {}
        
        with open(self.dr_index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load and parse guard rules from DR index."""
        rules = {}
        
        for section in self.dr_index.get("sections", []):
            section_id = section.get("section_id", "")
            
            # Extract rule metadata
            if section_id.startswith("DR-DO-"):
                rule_type = "MUST_DO"
                severity = "ERROR"
            elif section_id.startswith("DR-DONT-"):
                rule_type = "MUST_NOT_DO"
                severity = "ERROR"
            elif section_id.startswith("DR-GOLD-"):
                rule_type = "BEST_PRACTICE"
                severity = "WARNING"
            else:
                continue
            
            rules[section_id] = {
                "rule_id": section_id,
                "rule_type": rule_type,
                "severity": severity,
                "title": section.get("title", ""),
                "keywords": section.get("keywords", [])
            }
        
        return rules
    
    def check_acceptance_tests_present(
        self,
        spec_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check DR-DONT-002: Must not declare complete without acceptance tests.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        acceptance_tests = spec_data.get("acceptance_tests", [])
        
        if not acceptance_tests or len(acceptance_tests) < 3:
            violations.append(
                "DR-DONT-002 violation: Phase must have at least 3 programmatic acceptance tests"
            )
            return False, violations
        
        # Check that each test has required fields
        for i, test in enumerate(acceptance_tests):
            if not isinstance(test, dict):
                violations.append(f"Acceptance test {i+1} is not a valid object")
                continue
            
            if "command" not in test:
                violations.append(
                    f"DR-DO-001 violation: Acceptance test {i+1} missing 'command' field (CLI-first execution)"
                )
        
        return len(violations) == 0, violations
    
    def check_file_scope_valid(
        self,
        spec_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check DR-DONT-005: File scope must be within phase boundaries.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        file_scope = spec_data.get("file_scope", [])
        
        if not file_scope:
            violations.append("DR-DO-003: Phase must declare file_scope")
            return False, violations
        
        # Check for overly broad scopes
        dangerous_scopes = [".", "/", "*", "**/*"]
        for scope in file_scope:
            if scope in dangerous_scopes:
                violations.append(
                    f"DR-DONT-005 violation: File scope '{scope}' is too broad"
                )
        
        return len(violations) == 0, violations
    
    def check_dependencies_valid(
        self,
        spec_data: Dict[str, Any],
        all_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Check for circular dependencies and valid phase IDs.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        phase_id = spec_data.get("phase_id", "UNKNOWN")
        dependencies = spec_data.get("dependencies", [])
        
        # Check for self-dependency
        if phase_id in dependencies:
            violations.append(
                f"Circular dependency: Phase {phase_id} depends on itself"
            )
        
        # Validate dependency format
        for dep in dependencies:
            if not re.match(r'^PH-[0-9A-Z]+$', dep):
                violations.append(
                    f"Invalid dependency format: '{dep}' (should match PH-XX pattern)"
                )
        
        # If all specs provided, check for circular dependencies
        if all_specs:
            visited = set()
            path = []
            
            def has_cycle(node):
                if node in path:
                    cycle = " -> ".join(path[path.index(node):] + [node])
                    violations.append(f"Circular dependency detected: {cycle}")
                    return True
                
                if node in visited:
                    return False
                
                visited.add(node)
                path.append(node)
                
                node_spec = all_specs.get(node, {})
                for dep in node_spec.get("dependencies", []):
                    if has_cycle(dep):
                        return True
                
                path.pop()
                return False
            
            has_cycle(phase_id)
        
        return len(violations) == 0, violations
    
    def check_cli_first_execution(
        self,
        spec_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check DR-DO-001: CLI-first execution (all tests have commands).
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        pre_flight_checks = spec_data.get("pre_flight_checks", [])
        acceptance_tests = spec_data.get("acceptance_tests", [])
        
        # Check pre-flight checks
        for i, check in enumerate(pre_flight_checks):
            if "command" not in check:
                violations.append(
                    f"DR-DO-001 violation: Pre-flight check {i+1} missing 'command' field"
                )
        
        # Check acceptance tests
        for i, test in enumerate(acceptance_tests):
            if "command" not in test:
                violations.append(
                    f"DR-DO-001 violation: Acceptance test {i+1} missing 'command' field"
                )
        
        return len(violations) == 0, violations
    
    def check_phase_id_format(
        self,
        spec_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check phase_id follows standard format.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        phase_id = spec_data.get("phase_id", "")
        
        if not phase_id:
            violations.append("Missing required field: phase_id")
            return False, violations
        
        if not re.match(r'^PH-[0-9A-Z]+$', phase_id):
            violations.append(
                f"Invalid phase_id format: '{phase_id}' (should match PH-XX pattern)"
            )
        
        return len(violations) == 0, violations
    
    def check_all_rules(
        self,
        spec_data: Dict[str, Any],
        all_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Run all guard rule checks.
        
        Returns:
            Dictionary mapping rule names to (is_valid, violations) tuples
        """
        results = {}
        
        results["phase_id_format"] = self.check_phase_id_format(spec_data)
        results["acceptance_tests"] = self.check_acceptance_tests_present(spec_data)
        results["file_scope"] = self.check_file_scope_valid(spec_data)
        results["cli_first"] = self.check_cli_first_execution(spec_data)
        results["dependencies"] = self.check_dependencies_valid(spec_data, all_specs)
        
        return results
    
    def validate_file(
        self,
        file_path: str,
        enforce_scope: bool = False,
        require_cli_tests: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a phase spec file against guard rules.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        try:
            if file_path == '-':
                spec_data = json.load(sys.stdin)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    spec_data = json.load(f)
            
            results = self.check_all_rules(spec_data)
            
            all_violations = []
            all_valid = True
            
            for rule_name, (is_valid, violations) in results.items():
                if not is_valid:
                    all_valid = False
                    all_violations.extend(violations)
            
            return all_valid, all_violations
        
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e.msg}"]
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except Exception as e:
            return False, [f"Error: {str(e)}"]
    
    def detect_cycles_in_directory(
        self,
        directory: str
    ) -> Tuple[bool, List[str]]:
        """
        Detect circular dependencies across all specs in directory.
        
        Returns:
            Tuple of (no_cycles, cycle_descriptions)
        """
        dir_path = Path(directory)
        all_specs = {}
        
        # Load all specs
        for file_path in dir_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    spec = json.load(f)
                    phase_id = spec.get("phase_id")
                    if phase_id:
                        all_specs[phase_id] = spec
            except:
                continue
        
        # Check each for cycles
        all_violations = []
        for phase_id, spec in all_specs.items():
            _, violations = self.check_dependencies_valid(spec, all_specs)
            all_violations.extend(violations)
        
        return len(all_violations) == 0, all_violations


def main():
    """CLI entry point for guard rules validation."""
    parser = argparse.ArgumentParser(
        description="Enforce development rules and detect anti-patterns"
    )
    parser.add_argument(
        "--check",
        type=str,
        help="Path to phase spec file to check (or '-' for stdin)"
    )
    parser.add_argument(
        "--check-deps",
        type=str,
        help="Directory to check for circular dependencies"
    )
    parser.add_argument(
        "--enforce-scope",
        action="store_true",
        help="Enforce file scope validation"
    )
    parser.add_argument(
        "--require-cli-tests",
        action="store_true",
        help="Require CLI commands in all tests"
    )
    parser.add_argument(
        "--detect-cycles",
        action="store_true",
        help="Detect circular dependencies"
    )
    parser.add_argument(
        "--load-rules",
        type=str,
        help="Load custom guard rules from JSON file"
    )
    
    args = parser.parse_args()
    
    if not args.check and not args.check_deps:
        parser.error("Either --check or --check-deps must be specified")
    
    try:
        engine = GuardRulesEngine()
        
        if args.check:
            is_valid, violations = engine.validate_file(
                args.check,
                args.enforce_scope,
                args.require_cli_tests
            )
            
            if is_valid:
                print(f"✓ All guard rules passed: {args.check}")
                return 0
            else:
                print(f"✗ Guard rule violations in: {args.check}")
                for violation in violations:
                    print(f"  - {violation}")
                return 1
        
        elif args.check_deps:
            no_cycles, violations = engine.detect_cycles_in_directory(args.check_deps)
            
            if no_cycles:
                print(f"✓ No circular dependencies detected in: {args.check_deps}")
                return 0
            else:
                print(f"✗ Circular dependencies detected:")
                for violation in violations:
                    print(f"  - {violation}")
                return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
