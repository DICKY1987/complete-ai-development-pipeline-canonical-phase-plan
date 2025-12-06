#!/usr/bin/env python3
"""Monitor error automation health (run hourly via cron/CI)

EXECUTION PATTERN: EXEC-001 (Type-Safe Operations)
- Validates inputs and thresholds
- Clear exit codes
- Structured logging

DOC_ID: DOC-SCRIPTS-MONITOR-ERROR-AUTO-001
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from error.automation.queue_processor import ReviewQueueProcessor
from error.automation.alerting import AlertManager


def main() -> int:
    """Monitor queue health and send alerts if needed.

    Returns:
        0 if healthy, 1 if warnings, 2 if critical
    """
    processor = ReviewQueueProcessor()
    alert_manager = AlertManager()

    # Get queue metrics
    metrics = processor.get_queue_metrics()

    # Display status
    print(f"Queue Health: {metrics['health']}")
    print(f"Pending Reviews: {metrics['total_pending']}")
    print(f"Oldest Age: {metrics['oldest_age_hours']:.1f} hours")

    # Alert if unhealthy
    if metrics['health'] in ('warning', 'critical'):
        alert_manager.alert_queue_backlog(
            count=metrics['total_pending'],
            oldest_hours=metrics['oldest_age_hours']
        )

    # Return appropriate exit code
    if metrics['health'] == 'critical':
        return 2
    elif metrics['health'] == 'warning':
        return 1
    else:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
