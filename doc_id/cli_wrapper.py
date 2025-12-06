#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DOC_LINK: DOC-SCRIPT-DOC-ID-CLI-WRAPPER-010
"""
DOC_ID CLI Wrapper - Unified Command Interface

PATTERN: EXEC-006 Consolidated Entry Point
Ground Truth: All commands accessible via single CLI

USAGE:
    python doc_id/cli_wrapper.py scan
    python doc_id/cli_wrapper.py cleanup --auto-approve
    python doc_id/cli_wrapper.py sync --auto-sync
    python doc_id/cli_wrapper.py alerts
    python doc_id/cli_wrapper.py report daily
    python doc_id/cli_wrapper.py install-hook
    python doc_id/cli_wrapper.py setup-scheduler
    python doc_id/cli_wrapper.py watch --debounce 600
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOC_ID_DIR = REPO_ROOT / "doc_id"


class DocIDCLI:
    """Unified CLI wrapper for all DOC_ID operations"""
    
    def __init__(self):
        self.scripts = {
            'scan': DOC_ID_DIR / 'doc_id_scanner.py',
            'cleanup': DOC_ID_DIR / 'cleanup_invalid_doc_ids.py',
            'sync': DOC_ID_DIR / 'sync_registries.py',
            'alerts': DOC_ID_DIR / 'alert_monitor.py',
            'report': DOC_ID_DIR / 'scheduled_report_generator.py',
            'install-hook': DOC_ID_DIR / 'install_pre_commit_hook.py',
            'setup-scheduler': DOC_ID_DIR / 'setup_scheduled_tasks.py',
            'watch': DOC_ID_DIR / 'file_watcher.py',
        }
    
    def execute(self, command: str, args: list) -> int:
        """Execute a DOC_ID command"""
        script = self.scripts.get(command)
        
        if not script or not script.exists():
            print(f"❌ Unknown or missing command: {command}")
            print(f"Available: {', '.join(self.scripts.keys())}")
            return 1
        
        # Build command
        cmd = [sys.executable, str(script)] + args
        
        # Execute
        print(f"Executing: {command}")
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        
        return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description='DOC_ID CLI - Unified command interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  scan              Run DOC_ID scanner
  cleanup           Clean up invalid DOC_IDs
  sync              Synchronize registries
  alerts            Check alert thresholds
  report            Generate reports
  install-hook      Install pre-commit hook
  setup-scheduler   Setup scheduled tasks
  watch             Start file watcher

Examples:
  %(prog)s scan
  %(prog)s cleanup --auto-approve
  %(prog)s sync --auto-sync --max-drift 100
  %(prog)s alerts
  %(prog)s report daily
  %(prog)s install-hook
  %(prog)s setup-scheduler
  %(prog)s watch --debounce 300
        """
    )
    
    parser.add_argument('command', 
                       choices=['scan', 'cleanup', 'sync', 'alerts', 'report',
                               'install-hook', 'setup-scheduler', 'watch'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Arguments to pass to command')
    
    parsed_args = parser.parse_args()
    
    cli = DocIDCLI()
    exit_code = cli.execute(parsed_args.command, parsed_args.args)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
