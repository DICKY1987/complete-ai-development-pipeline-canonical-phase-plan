#!/usr/bin/env python3
"""
Validation Gateway - PH-2C

Unified validation gateway that orchestrates all validation layers:
- Schema validation (structural integrity)
- Guard rules (business logic and anti-patterns)
- Dependency validation (execution readiness)

Gates all phase execution to ensure quality and consistency.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Import validators
sys.path.insert(0, str(Path(__file__).parent / "validators"))
from schema_validator import SchemaValidator
from guard_rules_engine import GuardRulesEngine


class ValidationLayer(Enum):
    """Validation layers."""
    SCHEMA = "schema"
    GUARD_RULES = "guard_rules"
    DEPENDENCIES = "dependencies"


class ValidationResult:
    """Result from validation gateway."""
    
    def __init__(self):
        self.passed = True
        self.layers = {}
        self.errors = []
        self.warnings = []
    
    def add_layer_result(
        self,
        layer: ValidationLayer,
        passed: bool,
        messages: List[str]
    ):
        """Add result from a validation layer."""
        self.layers[layer.value] = {
            "passed": passed,
            "messages": messages
        }
        
        if not passed:
            self.passed = False
            self.errors.extend(messages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "overall_passed": self.passed,
            "layers": self.layers,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


class ValidationGateway:
    """Unified validation gateway for phase specifications."""
    
    def __init__(self):
        self.schema_validator = SchemaValidator()
        self.guard_engine = GuardRulesEngine()
    
    def validate_phase_spec(
        self,
        spec_data: Dict[str, Any],
        verbose: bool = False
    ) -> ValidationResult:
        """
        Run all validation layers on a phase specification.
        
        Args:
            spec_data: Phase specification as dictionary
            verbose: Include detailed messages
        
        Returns:
            ValidationResult with results from all layers
        """
        result = ValidationResult()
        
        # Layer 1: Schema Validation
        schema_valid, schema_errors = self.schema_validator.validate_phase_spec(
            spec_data,
            verbose=verbose
        )
        result.add_layer_result(
            ValidationLayer.SCHEMA,
            schema_valid,
            schema_errors
        )
        
        # Layer 2: Guard Rules
        guard_results = self.guard_engine.check_all_rules(spec_data)
        
        all_guard_violations = []
        all_guards_pass = True
        
        for rule_name, (is_valid, violations) in guard_results.items():
            if not is_valid:
                all_guards_pass = False
                all_guard_violations.extend(violations)
        
        result.add_layer_result(
            ValidationLayer.GUARD_RULES,
            all_guards_pass,
            all_guard_violations
        )
        
        # Layer 3: Dependency Format Check
        dep_valid, dep_errors = self.guard_engine.check_dependencies_valid(spec_data)
        result.add_layer_result(
            ValidationLayer.DEPENDENCIES,
            dep_valid,
            dep_errors
        )
        
        return result
    
    def validate_file(
        self,
        file_path: str,
        verbose: bool = False
    ) -> ValidationResult:
        """
        Validate a phase spec file through all layers.
        
        Args:
            file_path: Path to JSON file (or '-' for stdin)
            verbose: Include detailed messages
        
        Returns:
            ValidationResult
        """
        try:
            if file_path == '-':
                spec_data = json.load(sys.stdin)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    spec_data = json.load(f)
            
            return self.validate_phase_spec(spec_data, verbose)
        
        except json.JSONDecodeError as e:
            result = ValidationResult()
            result.passed = False
            result.errors.append(f"Invalid JSON: {e.msg}")
            return result
        except FileNotFoundError:
            result = ValidationResult()
            result.passed = False
            result.errors.append(f"File not found: {file_path}")
            return result
        except Exception as e:
            result = ValidationResult()
            result.passed = False
            result.errors.append(f"Error: {str(e)}")
            return result
    
    def validate_phase_plan(
        self,
        plan_file: str,
        verbose: bool = False
    ) -> Dict[str, ValidationResult]:
        """
        Validate an entire phase plan with all dependencies.
        
        Args:
            plan_file: Path to master phase plan JSON
            verbose: Include detailed messages
        
        Returns:
            Dictionary mapping phase IDs to ValidationResults
        """
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            results = {}
            
            # Get all phase specs
            for phase_entry in plan_data.get("phases", []):
                spec_file = phase_entry.get("spec_file", "")
                phase_id = phase_entry.get("phase_id", "UNKNOWN")
                
                if not spec_file:
                    continue
                
                spec_path = Path(spec_file)
                if not spec_path.exists():
                    result = ValidationResult()
                    result.passed = False
                    result.errors.append(f"Spec file not found: {spec_file}")
                    results[phase_id] = result
                    continue
                
                # Validate the spec
                result = self.validate_file(str(spec_path), verbose)
                results[phase_id] = result
            
            # Additional: Check for circular dependencies across all phases
            all_specs = {}
            for phase_entry in plan_data.get("phases", []):
                spec_file = phase_entry.get("spec_file", "")
                if spec_file and Path(spec_file).exists():
                    with open(spec_file, 'r') as f:
                        spec = json.load(f)
                        phase_id = spec.get("phase_id")
                        if phase_id:
                            all_specs[phase_id] = spec
            
            # Check cycles
            no_cycles, cycle_messages = self.guard_engine.detect_cycles_in_directory(
                "phase_specs"
            )
            
            if not no_cycles:
                # Add cycle errors to results
                for phase_id in results:
                    for msg in cycle_messages:
                        if phase_id in msg:
                            results[phase_id].errors.extend(cycle_messages)
                            results[phase_id].passed = False
            
            return results
        
        except Exception as e:
            return {"ERROR": self._error_result(str(e))}
    
    def pre_execution_check(
        self,
        spec_file: str
    ) -> Tuple[bool, List[str]]:
        """
        Pre-execution validation check.
        Verifies phase is ready to execute (dependencies satisfied, scope clear).
        
        Args:
            spec_file: Path to phase spec file
        
        Returns:
            Tuple of (ready_to_execute, blocking_issues)
        """
        result = self.validate_file(spec_file, verbose=True)
        
        if not result.passed:
            return False, result.errors
        
        # Additional pre-execution checks can go here
        # (e.g., check if dependencies are completed, workspace is clean)
        
        return True, []
    
    def _error_result(self, message: str) -> ValidationResult:
        """Create error result."""
        result = ValidationResult()
        result.passed = False
        result.errors.append(message)
        return result


def main():
    """CLI entry point for validation gateway."""
    parser = argparse.ArgumentParser(
        description="Unified validation gateway for phase specifications"
    )
    parser.add_argument(
        "--validate",
        type=str,
        help="Path to phase spec file to validate"
    )
    parser.add_argument(
        "--validate-plan",
        type=str,
        help="Path to master phase plan to validate"
    )
    parser.add_argument(
        "--pre-exec",
        type=str,
        help="Pre-execution check for phase spec"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation messages"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    if not args.validate and not args.validate_plan and not args.pre_exec:
        parser.error("One of --validate, --validate-plan, or --pre-exec must be specified")
    
    try:
        gateway = ValidationGateway()
        
        if args.validate:
            result = gateway.validate_file(args.validate, args.verbose)
            
            if args.output_format == "json":
                print(json.dumps(result.to_dict(), indent=2))
                return 0 if result.passed else 1
            else:
                if result.passed:
                    print(f"✓ All validation layers passed: {args.validate}")
                    return 0
                else:
                    print(f"✗ Validation failed: {args.validate}\n")
                    for layer, layer_result in result.layers.items():
                        status = "✓" if layer_result["passed"] else "✗"
                        print(f"{status} Layer: {layer}")
                        if not layer_result["passed"] and args.verbose:
                            for msg in layer_result["messages"]:
                                print(f"    - {msg}")
                    return 1
        
        elif args.validate_plan:
            results = gateway.validate_phase_plan(args.validate_plan, args.verbose)
            
            valid_count = sum(1 for r in results.values() if r.passed)
            total_count = len(results)
            
            print(f"\nPhase Plan Validation: {valid_count}/{total_count} phases valid\n")
            
            for phase_id, result in sorted(results.items()):
                status = "✓" if result.passed else "✗"
                print(f"{status} {phase_id}")
                
                if not result.passed and args.verbose:
                    for error in result.errors[:3]:  # Limit to first 3 errors
                        print(f"    - {error}")
            
            return 0 if valid_count == total_count else 1
        
        elif args.pre_exec:
            ready, issues = gateway.pre_execution_check(args.pre_exec)
            
            if ready:
                print(f"✓ Phase ready for execution: {args.pre_exec}")
                return 0
            else:
                print(f"✗ Phase not ready for execution: {args.pre_exec}\n")
                print("Blocking issues:")
                for issue in issues:
                    print(f"  - {issue}")
                return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
