#!/usr/bin/env python3
"""
Ground truth verification: observable evidence only

Usage:
    python verify_ground_truth.py --spec verify.json
"""
import argparse
import json
import subprocess
from pathlib import Path
from typing import List, Dict


class GroundTruthVerifier:
    def __init__(self):
        self.results = []
    
    def verify_file_exists(self, path: str) -> bool:
        """Ground truth: file exists on filesystem"""
        exists = Path(path).exists()
        self.results.append({
            'type': 'file_exists',
            'path': path,
            'passed': exists,
            'evidence': f"Path.exists() returned {exists}"
        })
        return exists
    
    def verify_file_size(self, path: str, min_lines: int, max_lines: int) -> bool:
        """Ground truth: file size within expected range"""
        if not Path(path).exists():
            self.results.append({
                'type': 'file_size',
                'path': path,
                'passed': False,
                'evidence': "File does not exist"
            })
            return False
        
        lines = len(Path(path).read_text().splitlines())
        in_range = min_lines <= lines <= max_lines
        
        self.results.append({
            'type': 'file_size',
            'path': path,
            'passed': in_range,
            'evidence': f"{lines} lines (expected {min_lines}-{max_lines})"
        })
        return in_range
    
    def verify_command_exit_code(self, command: str, expected_code: int = 0) -> bool:
        """Ground truth: command exits with expected code"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=60
            )
            passed = result.returncode == expected_code
            
            self.results.append({
                'type': 'command_exit_code',
                'command': command,
                'passed': passed,
                'evidence': f"Exit code: {result.returncode} (expected {expected_code})"
            })
            return passed
        except subprocess.TimeoutExpired:
            self.results.append({
                'type': 'command_exit_code',
                'command': command,
                'passed': False,
                'evidence': "Command timed out (>60s)"
            })
            return False
    
    def verify_output_contains(self, command: str, expected_text: str) -> bool:
        """Ground truth: command output contains expected text"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            passed = expected_text in output
            
            self.results.append({
                'type': 'output_contains',
                'command': command,
                'passed': passed,
                'evidence': f"Output {'contains' if passed else 'missing'}: '{expected_text}'"
            })
            return passed
        except subprocess.TimeoutExpired:
            self.results.append({
                'type': 'output_contains',
                'command': command,
                'passed': False,
                'evidence': "Command timed out"
            })
            return False
    
    def report(self) -> bool:
        """Print verification report and return success status"""
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\n{'='*70}")
        print(f"Ground Truth Verification Report")
        print(f"{'='*70}\n")
        
        for i, r in enumerate(self.results, 1):
            status = "✅ PASS" if r['passed'] else "❌ FAIL"
            print(f"{i}. {status} - {r['type']}")
            
            if 'path' in r:
                print(f"   Path: {r['path']}")
            elif 'command' in r:
                print(f"   Command: {r['command']}")
            
            print(f"   Evidence: {r['evidence']}\n")
        
        print(f"{'='*70}")
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Result: {passed}/{total} checks passed ({success_rate:.1f}%)")
        print(f"{'='*70}\n")
        
        return passed == total


def main():
    parser = argparse.ArgumentParser(description="Verify ground truth with observable evidence")
    parser.add_argument("--spec", required=True, help="Verification spec JSON file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any check fails")
    args = parser.parse_args()
    
    # Load verification spec
    with open(args.spec) as f:
        spec = json.load(f)
    
    verifier = GroundTruthVerifier()
    
    # Execute checks
    for check in spec.get('checks', []):
        check_type = check['type']
        
        if check_type == 'file_exists':
            verifier.verify_file_exists(check['path'])
        
        elif check_type == 'file_size':
            verifier.verify_file_size(
                check['path'],
                check.get('min_lines', 1),
                check.get('max_lines', 999999)
            )
        
        elif check_type == 'command_exit_code':
            verifier.verify_command_exit_code(
                check['command'],
                check.get('expected_code', 0)
            )
        
        elif check_type == 'output_contains':
            verifier.verify_output_contains(
                check['command'],
                check['expected_text']
            )
    
    # Report and exit
    success = verifier.report()
    
    if args.strict and not success:
        exit(1)


if __name__ == "__main__":
    main()
