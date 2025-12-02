# DOC_LINK: DOC-SCRIPT-EXECUTE-NEXT-WORKSTREAMS-2025-12-02
"""
Execute Next Workstreams - Automated Execution Runner

This script executes the 5 next-generation workstreams in dependency order.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSTREAMS = [
    {
        "id": "ws-next-001-github-project-integration",
        "name": "GitHub Project Integration",
        "script": None,  # Manual execution required
        "depends_on": [],
        "estimated_hours": 1
    },
    {
        "id": "ws-next-002-fix-reachability-analyzer",
        "name": "Fix Reachability Analyzer",
        "script": "scripts/fix_reachability_analyzer.py",
        "depends_on": [],
        "estimated_hours": 2
    },
    {
        "id": "ws-next-003-test-coverage-improvement",
        "name": "Test Coverage Improvement",
        "script": None,  # Ongoing, manual
        "depends_on": [],
        "estimated_hours": 12  # Over 4 weeks
    },
    {
        "id": "ws-next-004-refactor-2-execution",
        "name": "REFACTOR_2 Execution",
        "script": "scripts/execute_refactor_2.py",
        "depends_on": ["ws-next-001-github-project-integration", "ws-next-002-fix-reachability-analyzer"],
        "estimated_hours": 120
    },
    {
        "id": "ws-next-005-uet-framework-review",
        "name": "UET Framework Review",
        "script": "scripts/review_uet_framework.py",
        "depends_on": [],
        "estimated_hours": 1
    }
]

def load_workstream_status():
    """Load workstream status from tracking file."""
    status_file = Path("state/workstream_status.json")
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return {}

def save_workstream_status(status):
    """Save workstream status to tracking file."""
    status_file = Path("state/workstream_status.json")
    status_file.parent.mkdir(exist_ok=True)
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)

def check_dependencies(ws, status):
    """Check if all dependencies are completed."""
    for dep in ws["depends_on"]:
        if status.get(dep, {}).get("status") != "completed":
            return False, f"Dependency {dep} not completed"
    return True, ""

def execute_workstream(ws, dry_run=False):
    """Execute a single workstream."""
    print(f"\n{'='*80}")
    print(f"Executing: {ws['name']}")
    print(f"ID: {ws['id']}")
    print(f"Estimated: {ws['estimated_hours']} hours")
    print(f"{'='*80}\n")
    
    if ws["script"] is None:
        print(f"⚠️  Manual execution required for {ws['id']}")
        print(f"📋 See workstreams/{ws['id']}.json for instructions")
        return "manual"
    
    if dry_run:
        print(f"[DRY RUN] Would execute: python {ws['script']}")
        return "dry_run"
    
    try:
        result = subprocess.run(
            ["python", ws["script"]],
            capture_output=True,
            text=True,
            timeout=ws["estimated_hours"] * 3600  # Timeout = estimated hours
        )
        
        if result.returncode == 0:
            print(f"✅ {ws['name']} completed successfully")
            print(result.stdout)
            return "completed"
        else:
            print(f"❌ {ws['name']} failed")
            print(result.stderr)
            return "failed"
    except subprocess.TimeoutExpired:
        print(f"⏱️  {ws['name']} timed out")
        return "timeout"
    except Exception as e:
        print(f"💥 {ws['name']} crashed: {e}")
        return "error"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Execute next workstreams")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed")
    parser.add_argument("--workstream", help="Execute specific workstream by ID")
    parser.add_argument("--force", action="store_true", help="Ignore dependency checks")
    args = parser.parse_args()
    
    status = load_workstream_status()
    
    # Filter workstreams if specific one requested
    workstreams = WORKSTREAMS
    if args.workstream:
        workstreams = [ws for ws in WORKSTREAMS if ws["id"] == args.workstream]
        if not workstreams:
            print(f"❌ Workstream {args.workstream} not found")
            sys.exit(1)
    
    print(f"\n🚀 Next Workstreams Execution")
    print(f"{'='*80}")
    print(f"Total workstreams: {len(workstreams)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print(f"{'='*80}\n")
    
    results = {}
    
    for ws in workstreams:
        # Check if already completed
        if status.get(ws["id"], {}).get("status") == "completed" and not args.force:
            print(f"⏭️  Skipping {ws['name']} (already completed)")
            continue
        
        # Check dependencies
        deps_ok, dep_msg = check_dependencies(ws, status)
        if not deps_ok and not args.force:
            print(f"🔒 Skipping {ws['name']}: {dep_msg}")
            results[ws["id"]] = {
                "status": "blocked",
                "message": dep_msg,
                "timestamp": datetime.now().isoformat()
            }
            continue
        
        # Execute
        result_status = execute_workstream(ws, dry_run=args.dry_run)
        
        results[ws["id"]] = {
            "status": result_status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update persistent status
        if not args.dry_run:
            status[ws["id"]] = results[ws["id"]]
            save_workstream_status(status)
        
        # Stop on failure unless force
        if result_status == "failed" and not args.force:
            print(f"\n❌ Stopping execution due to failure in {ws['name']}")
            break
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 EXECUTION SUMMARY")
    print(f"{'='*80}\n")
    
    for ws_id, result in results.items():
        ws_name = next(w["name"] for w in WORKSTREAMS if w["id"] == ws_id)
        status_emoji = {
            "completed": "✅",
            "failed": "❌",
            "manual": "⚠️ ",
            "blocked": "🔒",
            "dry_run": "🔍",
            "timeout": "⏱️ ",
            "error": "💥"
        }.get(result["status"], "❓")
        
        print(f"{status_emoji} {ws_name}: {result['status']}")
    
    print(f"\n{'='*80}\n")
    
    # Exit code
    failed = any(r["status"] == "failed" for r in results.values())
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
