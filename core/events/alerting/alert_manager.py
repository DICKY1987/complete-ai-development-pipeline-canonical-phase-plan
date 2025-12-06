"""Alert management system for critical events and failures."""
DOC_ID: DOC-CORE-ALERTING-ALERT-MANAGER-870

from __future__ import annotations

import json
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse


class AlertChannel(Enum):
    """Alert delivery channels."""
    SLACK = "slack"
    EMAIL = "email"
    LOG = "log"


@dataclass
class AlertConfig:
    """Configuration for alert manager."""
    
    slack_webhook: Optional[str] = None
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_from: Optional[str] = None
    email_to: Optional[List[str]] = None
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    enabled_channels: List[AlertChannel] = None
    
    def __post_init__(self):
        if self.enabled_channels is None:
            self.enabled_channels = [AlertChannel.LOG]


class AlertManager:
    """Manages alerts for errors, critical events, and failures."""
    
    def __init__(
        self,
        event_bus: Any,
        config: Optional[AlertConfig] = None,
        alert_log: Optional[Path] = None
    ):
        """Initialize alert manager.
        
        Args:
            event_bus: Event bus to subscribe to
            config: Alert configuration
            alert_log: Path to alert log file
        """
        self.event_bus = event_bus
        self.config = config or AlertConfig()
        self.alert_log = alert_log or Path(".state/alerts.jsonl")
        self.alert_log.parent.mkdir(parents=True, exist_ok=True)
        
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to error and critical events."""
        self.event_bus.subscribe('*.ERROR', self.on_error)
        self.event_bus.subscribe('*.CRITICAL', self.on_critical)
        self.event_bus.subscribe('*.FAILED', self.on_failure)
    
    def on_error(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle error events.
        
        Args:
            event_type: Event type
            event_data: Event payload
        """
        component = event_data.get('component', 'unknown') if event_data else 'unknown'
        message = event_data.get('message', 'Error occurred') if event_data else 'Error occurred'
        
        self.send_alert(
            severity='error',
            title=f"⚠️ Error in {component}",
            message=message,
            data=event_data
        )
    
    def on_critical(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle critical events.
        
        Args:
            event_type: Event type
            event_data: Event payload
        """
        message = event_data.get('message', 'Critical event') if event_data else 'Critical event'
        
        self.send_alert(
            severity='critical',
            title=f"🚨 CRITICAL: {message}",
            message=message,
            data=event_data,
            channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.LOG]
        )
    
    def on_failure(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Handle failure events.
        
        Args:
            event_type: Event type
            event_data: Event payload
        """
        task_name = event_data.get('task_name', 'unknown') if event_data else 'unknown'
        error = event_data.get('error', 'No error details') if event_data else 'No error details'
        
        self.send_alert(
            severity='warning',
            title=f"⚠️ Task Failed: {task_name}",
            message=f"Task '{task_name}' failed with error: {error}",
            data=event_data
        )
    
    def send_alert(
        self,
        severity: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> None:
        """Send alert through configured channels.
        
        Args:
            severity: Alert severity (info, warning, error, critical)
            title: Alert title
            message: Alert message
            data: Optional additional data
            channels: Specific channels to use (defaults to all enabled)
        """
        channels = channels or self.config.enabled_channels
        
        alert_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'severity': severity,
            'title': title,
            'message': message,
            'data': data
        }
        
        for channel in channels:
            try:
                if channel == AlertChannel.SLACK and AlertChannel.SLACK in self.config.enabled_channels:
                    self._send_slack(title, message, severity)
                elif channel == AlertChannel.EMAIL and AlertChannel.EMAIL in self.config.enabled_channels:
                    self._send_email(title, message, severity)
                elif channel == AlertChannel.LOG:
                    self._log_alert(alert_record)
            except Exception as e:
                self._log_alert({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'severity': 'error',
                    'title': 'Alert Delivery Failed',
                    'message': f'Failed to send alert via {channel.value}: {str(e)}',
                    'original_alert': alert_record
                })
    
    def _send_slack(self, title: str, message: str, severity: str) -> None:
        """Send alert to Slack webhook.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
        """
        if not self.config.slack_webhook:
            return
        
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }
        
        emoji = emoji_map.get(severity, 'ℹ️')
        
        payload = {
            'text': f"{emoji} {title}",
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*{title}*\n{message}"
                    }
                }
            ]
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.config.slack_webhook,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
    
    def _send_email(self, title: str, message: str, severity: str) -> None:
        """Send alert via email.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
        """
        if not all([
            self.config.email_smtp_host,
            self.config.email_from,
            self.config.email_to
        ]):
            return
        
        msg = MIMEText(f"{message}\n\nSeverity: {severity}\nTimestamp: {datetime.now(timezone.utc).isoformat()}")
        msg['Subject'] = title
        msg['From'] = self.config.email_from
        msg['To'] = ', '.join(self.config.email_to)
        
        with smtplib.SMTP(self.config.email_smtp_host, self.config.email_smtp_port) as server:
            server.starttls()
            if self.config.email_username and self.config.email_password:
                server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
    
    def _log_alert(self, alert_record: Dict[str, Any]) -> None:
        """Log alert to file.
        
        Args:
            alert_record: Alert data to log
        """
        with open(self.alert_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert_record) + '\n')
    
    def get_recent_alerts(
        self,
        limit: int = 100,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent alerts from log.
        
        Args:
            limit: Maximum number of alerts to return
            severity: Optional filter by severity
            
        Returns:
            List of alert records
        """
        if not self.alert_log.exists():
            return []
        
        alerts = []
        with open(self.alert_log, 'r', encoding='utf-8') as f:
            for line in f:
                alert = json.loads(line)
                if severity is None or alert.get('severity') == severity:
                    alerts.append(alert)
                    if len(alerts) >= limit:
                        break
        
        return list(reversed(alerts))  # Most recent first
    
    def generate_daily_summary(self) -> Dict[str, Any]:
        """Generate daily summary of alerts.
        
        Returns:
            Summary statistics
        """
        alerts = self.get_recent_alerts(limit=10000)
        
        by_severity = {}
        by_hour = {}
        
        for alert in alerts:
            severity = alert.get('severity', 'unknown')
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            timestamp = alert.get('timestamp', '')
            hour = timestamp[:13] if timestamp else 'unknown'
            by_hour[hour] = by_hour.get(hour, 0) + 1
        
        return {
            'total_alerts': len(alerts),
            'by_severity': by_severity,
            'by_hour': by_hour,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
