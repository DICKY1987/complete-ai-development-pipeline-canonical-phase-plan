"""Health monitoring daemon with real-time alerting.

DOC_ID: DOC-PAT-MONITORING-HEALTH-DAEMON-001
"""

import time
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))

try:
    from core.events.event_bus import EventBus, EventSeverity
except ImportError:
    EventBus = None
    EventSeverity = None


def run_health_check():
    try:
        result = subprocess.run(
            ["powershell", "-File", "patterns/automation/monitoring/health_check.ps1", "-Json"],
            capture_output=True, text=True, timeout=60, cwd=repo_root
        )
        return json.loads(result.stdout) if result.stdout else {}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def main():
    print(f"[{datetime.now()}] Health monitor daemon starting...")
    
    check_interval = 300
    failure_count = 0
    
    while True:
        try:
            health = run_health_check()
            status = health.get("status", "UNKNOWN")
            
            if status == "UNHEALTHY":
                failure_count += 1
                print(f"[{datetime.now()}] ❌ UNHEALTHY - Failures: {failure_count}")
            elif status == "HEALTHY":
                if failure_count > 0:
                    print(f"[{datetime.now()}] ✅ RECOVERED after {failure_count} failures")
                failure_count = 0
            else:
                print(f"[{datetime.now()}] Status: {status}")
            
            time.sleep(check_interval)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Daemon stopped")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: {e}")
            time.sleep(check_interval)


if __name__ == "__main__":
    main()
