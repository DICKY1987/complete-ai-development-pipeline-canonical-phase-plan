"""
Queue CLI - Command-line interface for queue management.

Usage:
    python -m engine.queue submit --job-file JOB.json [--priority PRIORITY]
    python -m engine.queue list [--status STATUS]
    python -m engine.queue cancel JOB_ID
    python -m engine.queue stats
    python -m engine.queue start-workers [--count COUNT]
"""
DOC_ID: DOC-PAT-QUEUE-MAIN-459

import argparse
import asyncio
import json
import sys
from pathlib import Path

from engine.queue.queue_manager import QueueManager


async def cmd_submit(args):
    """Submit a job to the queue."""
    manager = QueueManager(worker_count=0)  # No workers for submit
    
    try:
        job_id = await manager.submit_job(
            job_file=args.job_file,
            priority=args.priority,
            depends_on=args.depends_on
        )
        print(f"✅ Job submitted: {job_id}")
        print(f"   Priority: {args.priority}")
        if args.depends_on:
            print(f"   Dependencies: {', '.join(args.depends_on)}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


async def cmd_list(args):
    """List jobs in queue."""
    manager = QueueManager(worker_count=0)
    
    jobs = manager.list_jobs(status=args.status, limit=args.limit)
    
    if not jobs:
        print("No jobs found")
        return 0
    
    print(f"\n{'Job ID':<40} {'Priority':<10} {'Status':<12} {'Queued At'}")
    print("=" * 100)
    
    for job in jobs:
        print(f"{job['job_id']:<40} {job['priority']:<10} {job['status']:<12} {job['queued_at']}")
    
    print(f"\nTotal: {len(jobs)} jobs")
    return 0


async def cmd_cancel(args):
    """Cancel a job."""
    manager = QueueManager(worker_count=0)
    
    success = await manager.cancel_job(args.job_id)
    
    if success:
        print(f"✅ Job cancelled: {args.job_id}")
        return 0
    else:
        print(f"❌ Could not cancel job: {args.job_id}")
        print("   (Job may be running or already completed)")
        return 1


async def cmd_stats(args):
    """Show queue statistics."""
    manager = QueueManager(worker_count=0)
    
    stats = manager.get_queue_stats()
    
    print("\n📊 Queue Statistics")
    print("=" * 50)
    print(f"Queued:    {stats['queue']['queued']}")
    print(f"Waiting:   {stats['queue']['waiting']}")
    print(f"Running:   {stats['queue']['running']}")
    print(f"Completed: {stats['queue']['completed']}")
    print(f"Failed:    {stats['queue']['failed']}")
    print(f"Total:     {stats['queue']['total']}")
    
    if stats['workers']['running']:
        print(f"\n👷 Workers:")
        print(f"  Active: {stats['workers']['active_workers']}/{stats['workers']['worker_count']}")
    
    return 0


async def cmd_start_workers(args):
    """Start worker pool."""
    print(f"Starting {args.count} workers...")
    
    manager = QueueManager(worker_count=args.count)
    await manager.start()
    
    print(f"✅ Workers started. Press Ctrl+C to stop.")
    
    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
            # Show stats periodically
            if args.verbose:
                stats = manager.get_queue_stats()
                print(f"\rRunning: {stats['queue']['running']} | "
                      f"Queued: {stats['queue']['queued']} | "
                      f"Completed: {stats['queue']['completed']}", end='')
    
    except KeyboardInterrupt:
        print("\n\nStopping workers...")
        await manager.stop(graceful=True)
        print("✅ Workers stopped")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Job Queue Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit a job')
    submit_parser.add_argument('--job-file', required=True, help='Job JSON file')
    submit_parser.add_argument('--priority', default='normal', 
                               choices=['critical', 'high', 'normal', 'low'],
                               help='Job priority')
    submit_parser.add_argument('--depends-on', nargs='*', help='Job dependencies')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=100, help='Max results')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a job')
    cancel_parser.add_argument('job_id', help='Job ID to cancel')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Start workers command
    workers_parser = subparsers.add_parser('start-workers', help='Start worker pool')
    workers_parser.add_argument('--count', type=int, default=3, help='Number of workers')
    workers_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run async command
    if args.command == 'submit':
        return asyncio.run(cmd_submit(args))
    elif args.command == 'list':
        return asyncio.run(cmd_list(args))
    elif args.command == 'cancel':
        return asyncio.run(cmd_cancel(args))
    elif args.command == 'stats':
        return asyncio.run(cmd_stats(args))
    elif args.command == 'start-workers':
        return asyncio.run(cmd_start_workers(args))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
