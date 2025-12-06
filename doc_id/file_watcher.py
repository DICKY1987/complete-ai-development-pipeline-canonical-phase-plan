#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DOC_LINK: DOC-SCRIPT-DOC-ID-FILE-WATCHER-009
"""
DOC_ID File Watcher - Automatic Scan Trigger

PATTERN: EXEC-003 Tool Availability Guards
Ground Truth: Watcher process running, scan triggered on changes

USAGE:
    python doc_id/file_watcher.py
    python doc_id/file_watcher.py --debounce 600
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# PATTERN: Tool availability guard
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog not installed")
    print("Run: pip install watchdog")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
SCANNER_SCRIPT = REPO_ROOT / "doc_id" / "doc_id_scanner.py"
ELIGIBLE_EXTENSIONS = {'.py', '.md', '.yaml', '.yml', '.json', '.ps1', '.sh', '.txt'}
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache'}


class DocIDEventHandler(FileSystemEventHandler):
    """Handle file system events for DOC_ID scanning"""
    
    def __init__(self, debounce_seconds=300):
        self.last_scan = datetime.min
        self.debounce = timedelta(seconds=debounce_seconds)
        self.pending_scan = False
        self.modified_files = set()
    
    def should_process(self, path: Path) -> bool:
        """Check if file should trigger scan"""
        # Skip directories
        if path.is_dir():
            return False
        
        # Check extension
        if path.suffix not in ELIGIBLE_EXTENSIONS:
            return False
        
        # Check excluded directories
        if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
            return False
        
        return True
    
    def on_modified(self, event):
        """Trigger scan on file modification"""
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        if not self.should_process(path):
            return
        
        # Track modified file
        self.modified_files.add(str(path.relative_to(REPO_ROOT)))
        
        # Debounce
        now = datetime.now()
        if now - self.last_scan < self.debounce:
            self.pending_scan = True
            return
        
        # Trigger scan
        self.trigger_scan()
    
    def on_created(self, event):
        """Handle new files"""
        self.on_modified(event)
    
    def trigger_scan(self):
        """Execute scanner"""
        if not self.modified_files:
            return
        
        print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Files changed: {len(self.modified_files)}")
        print(f"Triggering scan...")
        
        result = subprocess.run(
            [sys.executable, str(SCANNER_SCRIPT), 'scan'],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT
        )
        
        if result.returncode == 0:
            print("✅ Scan completed successfully")
            # Parse and display coverage
            if 'Coverage:' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'Coverage:' in line or 'Scanned:' in line:
                        print(f"   {line.strip()}")
        else:
            print(f"❌ Scan failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
        
        self.last_scan = datetime.now()
        self.modified_files.clear()
        self.pending_scan = False


def main():
    parser = argparse.ArgumentParser(description="DOC_ID File Watcher")
    parser.add_argument('--debounce', type=int, default=300,
                       help='Debounce interval in seconds (default: 300)')
    args = parser.parse_args()
    
    print("═══════════════════════════════════════════════════════════════")
    print("   DOC_ID FILE WATCHER")
    print("═══════════════════════════════════════════════════════════════")
    print(f"Watching: {REPO_ROOT}")
    print(f"Scanner: {SCANNER_SCRIPT}")
    print(f"Debounce: {args.debounce} seconds")
    print("Press Ctrl+C to stop")
    print("═══════════════════════════════════════════════════════════════\n")
    
    # Verify scanner exists
    if not SCANNER_SCRIPT.exists():
        print(f"❌ Scanner not found: {SCANNER_SCRIPT}")
        sys.exit(1)
    
    # Create handler and observer
    handler = DocIDEventHandler(debounce_seconds=args.debounce)
    observer = Observer()
    observer.schedule(handler, str(REPO_ROOT), recursive=True)
    observer.start()
    
    print("✅ Watcher started - monitoring for changes...\n")
    
    try:
        while True:
            time.sleep(1)
            # Check for pending scans
            if handler.pending_scan:
                now = datetime.now()
                if now - handler.last_scan >= handler.debounce:
                    handler.trigger_scan()
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped")
    sys.exit(0)


if __name__ == '__main__':
    main()
