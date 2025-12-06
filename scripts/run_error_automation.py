#!/usr/bin/env python3
"""Error automation orchestrator CLI

EXECUTION PATTERN: EXEC-001 (Type-Safe Operations)
- All inputs validated
- Clear error messages
- Exit codes indicate success/failure

DOC_ID: DOC-SCRIPTS-RUN-ERROR-AUTO-001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Section-based imports (follows CI_PATH_STANDARDS.md)
from error.automation.patch_applier import PatchApplier


def validate_patch_path(path_str: str) -> Path:
    """Validate patch file exists and is readable.
    
    Pattern: EXEC-001 - Type-safe input validation
    """
    path = Path(path_str)
    if not path.exists():
        raise ValueError(f"Patch file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if path.suffix not in ['.patch', '.diff']:
        raise ValueError(f"Invalid patch file extension: {path.suffix}")
    return path


def cmd_apply_patch(args: argparse.Namespace) -> int:
    """Apply and validate patch with confidence scoring."""
    try:
        patch_path = validate_patch_path(args.patch_path)
        
        applier = PatchApplier(
            repo_path=Path.cwd(),
            auto_merge_threshold=args.auto_merge_threshold,
            pr_threshold=args.pr_threshold
        )
        
        print(f"Validating patch: {patch_path}")
        result = applier.apply_with_validation(patch_path)
        
        # Display results
        print(f"\n{'='*60}")
        print(f"Decision: {result['decision']}")
        print(f"Confidence: {result['confidence']['overall']:.1%}")
        print(f"{'='*60}")
        
        # Detailed breakdown
        conf = result['confidence']
        print(f"\nValidation Breakdown:")
        print(f"  Tests:       {'✅' if conf['tests_passed'] == 1.0 else '❌'} {conf['tests_passed']:.1%}")
        print(f"  Linting:     {'✅' if conf['lint_passed'] == 1.0 else '⚠️'} {conf['lint_passed']:.1%}")
        print(f"  Type Check:  {'✅' if conf['type_check_passed'] == 1.0 else '⚠️'} {conf['type_check_passed']:.1%}")
        print(f"  Security:    {'✅' if conf['security_scan_passed'] == 1.0 else '❌'} {conf['security_scan_passed']:.1%}")
        print(f"  Coverage:    {'✅' if conf['coverage_maintained'] >= 0.7 else '⚠️'} {conf['coverage_maintained']:.1%}")
        
        # Action taken
        action = result['action_taken']
        print(f"\nAction: {action.get('status', 'unknown')}")
        if 'message' in action:
            print(f"  {action['message']}")
        
        # Exit code: 0 = success (merged or queued), 1 = rejected
        return 0 if result['decision'] != 'rejected' else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_process_queue(args: argparse.Namespace) -> int:
    """Process manual review queue."""
    try:
        # Import here to avoid dependency if not used
        from error.automation.queue_processor import ReviewQueueProcessor
        
        processor = ReviewQueueProcessor()
        
        if args.action == 'list':
            pending = processor.list_pending(min_confidence=args.min_confidence or 0.0)
            
            if not pending:
                print("No pending reviews.")
                return 0
            
            print(f"\n{'='*80}")
            print(f"Manual Review Queue ({len(pending)} items)")
            print(f"{'='*80}\n")
            
            for i, entry in enumerate(pending, 1):
                print(f"{i}. Patch: {entry['patch_path']}")
                print(f"   Confidence: {entry['confidence']['overall']:.1%}")
                print(f"   Queued: {entry['queued_at']}")
                print()
            
            return 0
            
        elif args.action == 'approve':
            if not args.patch_id:
                print("Error: --patch-id required for approve action", file=sys.stderr)
                return 1
            
            result = processor.approve(args.patch_id)
            print(f"Approved: {args.patch_id}")
            print(f"Next steps: {result['next_steps']}")
            return 0
            
        elif args.action == 'reject':
            if not args.patch_id:
                print("Error: --patch-id required for reject action", file=sys.stderr)
                return 1
            
            reason = args.reason or "No reason provided"
            result = processor.reject(args.patch_id, reason)
            print(f"Rejected: {args.patch_id}")
            print(f"Reason: {reason}")
            return 0
        
        else:
            print(f"Unknown action: {args.action}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show error automation status and metrics."""
    try:
        # Import here to avoid dependency if not used
        from error.automation.metrics import ErrorAutomationMetrics
        
        metrics = ErrorAutomationMetrics()
        data = metrics.get_metrics(days=args.days)
        
        print(f"\n{'='*80}")
        print(f"Error Automation Status (Last {args.days} Days)")
        print(f"{'='*80}\n")
        
        total = max(data['total_patches'], 1)  # Avoid division by zero
        print(f"Patches Processed: {data['total_patches']}")
        print(f"  ✅ Auto-merged:    {data['auto_merged']} ({data['auto_merged']/total*100:.1f}%)")
        print(f"  🔄 PR created:     {data['pr_created']} ({data['pr_created']/total*100:.1f}%)")
        print(f"  👁️  Manual review:  {data['manual_review']} ({data['manual_review']/total*100:.1f}%)")
        print(f"  ❌ Rejected:       {data['rejected']} ({data['rejected']/total*100:.1f}%)")
        
        print(f"\nAverage Confidence: {data['avg_confidence']:.1%}")
        
        print(f"\n{'='*80}")
        print(f"Manual Review Queue")
        print(f"{'='*80}\n")
        print(f"Pending Reviews: {data['pending_reviews']}")
        
        if data['pending_reviews'] > 0:
            age = data['review_queue_age_hours']
            print(f"Oldest Review: {age:.1f} hours ago")
            
            if age > 72:
                print("⚠️  WARNING: Reviews older than 3 days detected!")
            elif age > 24:
                print("⚠️  NOTICE: Reviews older than 1 day detected")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Error recovery automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply a patch with validation
  %(prog)s apply path/to/fix.patch
  
  # List pending manual reviews
  %(prog)s process-queue --action list
  
  # Approve a patch for merge
  %(prog)s process-queue --action approve --patch-id path/to/fix.patch
  
  # View automation status
  %(prog)s status --days 7
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Apply patch command
    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply and validate patch'
    )
    apply_parser.add_argument(
        'patch_path',
        type=str,
        help='Path to patch file (.patch or .diff)'
    )
    apply_parser.add_argument(
        '--auto-merge-threshold',
        type=float,
        default=0.95,
        help='Confidence threshold for auto-merge (default: 0.95)'
    )
    apply_parser.add_argument(
        '--pr-threshold',
        type=float,
        default=0.80,
        help='Confidence threshold for PR creation (default: 0.80)'
    )
    
    # Process queue command
    queue_parser = subparsers.add_parser(
        'process-queue',
        help='Process manual review queue'
    )
    queue_parser.add_argument(
        '--action',
        choices=['list', 'approve', 'reject'],
        required=True,
        help='Queue action to perform'
    )
    queue_parser.add_argument(
        '--patch-id',
        type=str,
        help='Patch identifier (required for approve/reject)'
    )
    queue_parser.add_argument(
        '--reason',
        type=str,
        help='Rejection reason (optional for reject action)'
    )
    queue_parser.add_argument(
        '--min-confidence',
        type=float,
        help='Minimum confidence to display (list action only)'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show error automation status'
    )
    status_parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to analyze (default: 7)'
    )
    
    args = parser.parse_args()
    
    # Route to command handler
    if args.command == 'apply':
        return cmd_apply_patch(args)
    elif args.command == 'process-queue':
        return cmd_process_queue(args)
    elif args.command == 'status':
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
