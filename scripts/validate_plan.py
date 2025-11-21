#!/usr/bin/env python3
"""Dry-run validator for phase plans.

Analyzes workstream bundles to identify parallel execution opportunities,
detect conflicts, and estimate execution time with different worker configurations.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.state.bundles import load_and_validate_bundles, BundleValidationError
from core.engine.plan_validator import validate_phase_plan, ValidationMode


def main():
    parser = argparse.ArgumentParser(
        description="Validate phase plans and analyze parallelism opportunities"
    )
    parser.add_argument(
        '--workstreams-dir',
        default='workstreams',
        help='Directory containing workstream bundles (default: workstreams)'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--mode',
        choices=['validate', 'execute'],
        default='validate',
        help='Validation mode (default: validate)'
    )
    
    args = parser.parse_args()
    
    # Load bundles
    try:
        workstream_path = Path(args.workstreams_dir)
        if not workstream_path.exists():
            print(f"❌ Workstream directory not found: {workstream_path}", file=sys.stderr)
            return 1
        
        print(f"Loading bundles from: {workstream_path}", file=sys.stderr)
        bundles = load_and_validate_bundles(workstream_path)
        print(f"✅ Loaded {len(bundles)} workstream bundles", file=sys.stderr)
        print("", file=sys.stderr)
    
    except BundleValidationError as e:
        print(f"❌ Bundle validation failed: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"❌ Error loading bundles: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    # Validate plan
    try:
        mode = ValidationMode.EXECUTE if args.mode == 'execute' else ValidationMode.VALIDATE_ONLY
        report = validate_phase_plan(bundles, mode=mode, max_workers=args.max_workers)
        
        # Output report
        if args.output == 'json':
            print(report.to_json())
        else:
            print(report.to_text())
        
        # Exit code based on validity
        return 0 if report.valid else 1
    
    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
