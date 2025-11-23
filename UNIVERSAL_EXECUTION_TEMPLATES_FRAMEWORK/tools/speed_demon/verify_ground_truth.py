#!/usr/bin/env python3
"""
Speed Demon Ground Truth Verifier
Observable evidence-based validation

Usage:
    python verify_ground_truth.py --spec batch.json --check file_exists
    python verify_ground_truth.py --spec test_results.json --check exit_code
"""

import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def verify_file_exists(spec: Dict[str, Any]) -> bool:
    """Verify files exist (most basic ground truth)"""
    print("📁 Verifying file existence...")
    
    items = spec.get('items', [])
    successes = 0
    failures = []
    
    for item in items:
        path = item.get('output_path') or item.get('path')
        if not path:
            continue
            
        if Path(path).exists():
            print(f"  ✓ {path}")
            successes += 1
        else:
            print(f"  ✗ {path} MISSING")
            failures.append(path)
    
    total = len(items)
    print(f"\n{'='*60}")
    print(f"✅ Found: {successes}/{total}")
    print(f"❌ Missing: {len(failures)}/{total}")
    
    if failures:
        print("\nMissing files:")
        for f in failures:
            print(f"  - {f}")
        return False
    
    return True


def verify_exit_code(spec: Dict[str, Any]) -> bool:
    """Verify commands exit with code 0"""
    print("🔍 Verifying exit codes...")
    
    commands = spec.get('commands', [])
    successes = 0
    failures = []
    
    for cmd_spec in commands:
        cmd = cmd_spec.get('command')
        expected = cmd_spec.get('expected_exit_code', 0)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == expected:
                print(f"  ✓ {cmd} (exit {result.returncode})")
                successes += 1
            else:
                print(f"  ✗ {cmd} (exit {result.returncode}, expected {expected})")
                failures.append({
                    'command': cmd,
                    'actual': result.returncode,
                    'expected': expected
                })
        
        except subprocess.TimeoutExpired:
            print(f"  ✗ {cmd} (timeout)")
            failures.append({'command': cmd, 'error': 'timeout'})
        
        except Exception as e:
            print(f"  ✗ {cmd} (error: {e})")
            failures.append({'command': cmd, 'error': str(e)})
    
    total = len(commands)
    print(f"\n{'='*60}")
    print(f"✅ Passed: {successes}/{total}")
    print(f"❌ Failed: {len(failures)}/{total}")
    
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        return False
    
    return True


def verify_file_size(spec: Dict[str, Any]) -> bool:
    """Verify files are non-empty (reasonable size)"""
    print("📏 Verifying file sizes...")
    
    items = spec.get('items', [])
    min_size = spec.get('min_size_bytes', 100)
    
    successes = 0
    failures = []
    
    for item in items:
        path = item.get('output_path') or item.get('path')
        if not path or not Path(path).exists():
            continue
        
        size = Path(path).stat().st_size
        if size >= min_size:
            print(f"  ✓ {path} ({size} bytes)")
            successes += 1
        else:
            print(f"  ✗ {path} ({size} bytes, < {min_size})")
            failures.append({'path': path, 'size': size})
    
    total = len(items)
    print(f"\n{'='*60}")
    print(f"✅ Valid: {successes}/{total}")
    print(f"❌ Too small: {len(failures)}/{total}")
    
    return len(failures) == 0


def main():
    parser = argparse.ArgumentParser(description='Ground Truth Verifier')
    parser.add_argument('--spec', required=True, help='Specification file')
    parser.add_argument('--check', required=True, 
                       choices=['file_exists', 'exit_code', 'file_size'],
                       help='Verification type')
    
    args = parser.parse_args()
    
    with open(args.spec, 'r') as f:
        spec = json.load(f)
    
    if args.check == 'file_exists':
        success = verify_file_exists(spec)
    elif args.check == 'exit_code':
        success = verify_exit_code(spec)
    elif args.check == 'file_size':
        success = verify_file_size(spec)
    else:
        print(f"❌ Unknown check type: {args.check}")
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
