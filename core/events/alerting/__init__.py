"""Event-driven alerting system for critical events.

DOC_ID: DOC-CORE-ALERTING-INIT-871
"""

from core.events.alerting.alert_manager import AlertManager, AlertChannel

__all__ = ["AlertManager", "AlertChannel"]
