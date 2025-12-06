"""Event-driven pattern execution launcher.

DOC_ID: DOC-PAT-LIFECYCLE-EVENT-LAUNCHER-001

Listens for pattern_approved events and automatically triggers execution.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Setup imports
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))

from core.events.event_bus import EventBus


def launch_pattern_execution(pattern_id: str, confidence: float):
    """Launch pattern execution via CLI."""
    import subprocess
    
    cli_path = Path(__file__).parent.parent.parent / "cli" / "pattern_orchestrate.py"
    
    cmd = [
        "python",
        str(cli_path),
        "execute",
        "--pattern-id", pattern_id,
        "--timeout", "600"
    ]
    
    print(f"[{datetime.now()}] Launching pattern execution: {pattern_id} (confidence: {confidence:.0%})")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=660)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Pattern executed successfully: {pattern_id}")
        else:
            print(f"[{datetime.now()}] ❌ Pattern execution failed: {pattern_id}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] ⏱️  Pattern execution timeout: {pattern_id}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Execution error: {e}")


def main():
    """Run event-driven pattern launcher daemon."""
    print(f"[{datetime.now()}] Event-driven pattern launcher starting...")
    
    event_bus = EventBus()
    
    # Subscribe to pattern approval events
    def on_pattern_approved(event):
        pattern_id = event.data.get('pattern_id')
        confidence = event.data.get('confidence', 0.0)
        
        if pattern_id:
            launch_pattern_execution(pattern_id, confidence)
    
    try:
        event_bus.subscribe("pattern_approved", on_pattern_approved)
        print(f"[{datetime.now()}] Subscribed to pattern_approved events")
        
        # Keep daemon running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Launcher daemon stopped")
    except Exception as e:
        print(f"[{datetime.now()}] Daemon error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
