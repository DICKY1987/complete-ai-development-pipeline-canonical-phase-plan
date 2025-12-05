"""Event-driven alerting system for critical events."""

from core.events.alerting.alert_manager import AlertManager, AlertChannel

__all__ = ["AlertManager", "AlertChannel"]
