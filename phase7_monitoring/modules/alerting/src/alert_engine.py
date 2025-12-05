"""Alert Engine - Multi-channel alerting for monitoring events.

GAP-002 Implementation: Automated alerting and escalation
Pattern: EXEC-002 (Batch Validation) + Plugin architecture
"""
# DOC_ID: DOC-PHASE7-ALERT-ENGINE-003

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import yaml


@dataclass
class AlertRule:
    """Alert routing rule."""
    name: str
    event_types: List[str]
    severity: str
    channels: List[str]
    throttle_minutes: int


class AlertEngine:
    """Routes events to notification channels based on rules.
    
    Implements:
    - Rule-based alert routing
    - Throttling and deduplication
    - Multi-channel delivery
    """
    
    def __init__(self, config_path: str):
        """Initialize alert engine.
        
        Args:
            config_path: Path to alerts.yaml configuration
        """
        self.config_path = config_path
        self.rules: List[AlertRule] = []
        self.channels: Dict[str, 'AlertChannel'] = {}
        self.throttle_cache: Dict[str, datetime] = {}
        
        self._load_config()
    
    def _load_config(self):
        """Load alert configuration from YAML."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            print(f"[AlertEngine] WARNING: Config not found: {self.config_path}")
            print("[AlertEngine] Using default configuration")
            self._use_defaults()
            return
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            # Load rules
            self.rules = [
                AlertRule(**rule_data)
                for rule_data in config.get('alert_rules', [])
            ]
            
            # Initialize channels
            self.channels = self._init_channels(config.get('channels', {}))
            
            print(f"[AlertEngine] Loaded {len(self.rules)} rules, {len(self.channels)} channels")
            
        except Exception as e:
            print(f"[AlertEngine] ERROR loading config: {e}")
            self._use_defaults()
    
    def _use_defaults(self):
        """Use default alert configuration."""
        # Default rule: alert on all failures
        self.rules = [
            AlertRule(
                name="default_failure",
                event_types=["run_failed", "archival_failed", "run_stalled"],
                severity="critical",
                channels=["console"],
                throttle_minutes=15
            )
        ]
        
        # Console-only channel
        self.channels = {"console": ConsoleChannel()}
    
    def _init_channels(self, channel_config: dict) -> Dict[str, 'AlertChannel']:
        """Initialize notification channels from config.
        
        Args:
            channel_config: Channel configuration dict
            
        Returns:
            Dictionary of channel name to channel instance
        """
        channels = {}
        
        # Always include console channel
        channels['console'] = ConsoleChannel()
        
        # Slack channel (if configured)
        if 'slack' in channel_config:
            slack_config = channel_config['slack']
            webhook_url = os.getenv('SLACK_WEBHOOK_URL', slack_config.get('webhook_url', ''))
            
            if webhook_url and webhook_url != '${SLACK_WEBHOOK_URL}':
                channels['slack'] = SlackChannel(
                    webhook_url=webhook_url,
                    default_channel=slack_config.get('default_channel', '#pipeline-alerts')
                )
                print("[AlertEngine] Slack channel enabled")
            else:
                print("[AlertEngine] Slack channel disabled (no webhook URL)")
        
        # Email channel (if configured)
        if 'email' in channel_config:
            email_config = channel_config['email']
            smtp_host = os.getenv('SMTP_HOST', email_config.get('smtp_host', ''))
            
            if smtp_host and smtp_host != '${SMTP_HOST}':
                channels['email'] = EmailChannel(
                    smtp_host=smtp_host,
                    smtp_port=email_config.get('smtp_port', 587),
                    from_addr=os.getenv('ALERT_EMAIL_FROM', email_config.get('from_address', '')),
                    to_addrs=os.getenv('ALERT_EMAIL_TO', '').split(',') or email_config.get('to_addresses', [])
                )
                print("[AlertEngine] Email channel enabled")
            else:
                print("[AlertEngine] Email channel disabled (no SMTP host)")
        
        return channels
    
    def process_event(self, event_type: str, run_id: str, data: dict):
        """Process event and send alerts if rules match.
        
        Args:
            event_type: Event type (e.g., "run_failed")
            run_id: Run ID
            data: Event data dictionary
        """
        # Find matching rules
        matching_rules = [
            rule for rule in self.rules
            if event_type in rule.event_types
        ]
        
        if not matching_rules:
            return
        
        # Process each matching rule
        for rule in matching_rules:
            # Check throttling
            throttle_key = f"{rule.name}:{run_id}"
            
            if self._is_throttled(throttle_key, rule.throttle_minutes):
                print(f"[AlertEngine] Throttled: {rule.name} for {run_id}")
                continue
            
            # Send to configured channels
            for channel_name in rule.channels:
                channel = self.channels.get(channel_name)
                
                if channel:
                    try:
                        channel.send_alert(rule, event_type, run_id, data)
                    except Exception as e:
                        print(f"[AlertEngine] ERROR: {channel_name} failed: {e}")
                else:
                    print(f"[AlertEngine] WARNING: Channel {channel_name} not found")
            
            # Update throttle cache
            self.throttle_cache[throttle_key] = datetime.utcnow()
    
    def _is_throttled(self, key: str, minutes: int) -> bool:
        """Check if alert is throttled.
        
        Args:
            key: Throttle key
            minutes: Throttle window in minutes
            
        Returns:
            True if alert should be throttled
        """
        if key not in self.throttle_cache:
            return False
        
        last_sent = self.throttle_cache[key]
        elapsed = datetime.utcnow() - last_sent
        
        return elapsed < timedelta(minutes=minutes)


# Alert Channel Implementations

class ConsoleChannel:
    """Console/stdout alert channel."""
    
    def send_alert(self, rule: AlertRule, event_type: str, run_id: str, data: dict):
        """Send alert to console.
        
        Args:
            rule: Alert rule
            event_type: Event type
            run_id: Run ID
            data: Event data
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity_prefix = {
            "critical": "🔴 CRITICAL",
            "high": "🟠 HIGH",
            "medium": "🟡 MEDIUM",
            "low": "🟢 LOW"
        }
        
        prefix = severity_prefix.get(rule.severity, "ℹ️ INFO")
        
        print(f"\n[ALERT] {timestamp} - {prefix}")
        print(f"  Event: {event_type}")
        print(f"  Run ID: {run_id}")
        
        if 'error' in data:
            print(f"  Error: {data['error']}")
        
        if 'metrics' in data:
            metrics = data['metrics']
            print(f"  Steps: {metrics.get('completed_steps', 0)}/{metrics.get('total_steps', 0)} completed")
        
        print()


class SlackChannel:
    """Slack webhook alert channel."""
    
    def __init__(self, webhook_url: str, default_channel: str):
        """Initialize Slack channel.
        
        Args:
            webhook_url: Slack webhook URL
            default_channel: Default channel (e.g., "#pipeline-alerts")
        """
        self.webhook_url = webhook_url
        self.default_channel = default_channel
    
    def send_alert(self, rule: AlertRule, event_type: str, run_id: str, data: dict):
        """Send alert to Slack.
        
        Args:
            rule: Alert rule
            event_type: Event type
            run_id: Run ID
            data: Event data
        """
        import requests
        
        message = self._format_message(rule, event_type, run_id, data)
        
        payload = {
            "channel": self.default_channel,
            "text": message,
            "username": "Pipeline Monitor",
            "icon_emoji": ":rotating_light:"
        }
        
        response = requests.post(self.webhook_url, json=payload, timeout=5)
        response.raise_for_status()
    
    def _format_message(self, rule: AlertRule, event_type: str, run_id: str, data: dict) -> str:
        """Format alert message for Slack.
        
        Args:
            rule: Alert rule
            event_type: Event type
            run_id: Run ID
            data: Event data
            
        Returns:
            Formatted message string
        """
        severity_emoji = {
            "critical": ":red_circle:",
            "high": ":warning:",
            "medium": ":large_orange_diamond:",
            "low": ":large_blue_circle:"
        }
        
        emoji = severity_emoji.get(rule.severity, ":information_source:")
        
        message = f"{emoji} *{rule.severity.upper()}*: {event_type}\n"
        message += f"Run ID: `{run_id}`\n"
        
        if 'error' in data:
            message += f"Error: {data['error']}\n"
        
        if 'metrics' in data:
            metrics = data['metrics']
            message += f"Progress: {metrics.get('completed_steps', 0)}/{metrics.get('total_steps', 0)} steps\n"
        
        return message


class EmailChannel:
    """Email alert channel."""
    
    def __init__(self, smtp_host: str, smtp_port: int, from_addr: str, to_addrs: List[str]):
        """Initialize email channel.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            from_addr: From email address
            to_addrs: List of recipient addresses
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.to_addrs = [addr.strip() for addr in to_addrs if addr.strip()]
    
    def send_alert(self, rule: AlertRule, event_type: str, run_id: str, data: dict):
        """Send alert via email.
        
        Args:
            rule: Alert rule
            event_type: Event type
            run_id: Run ID
            data: Event data
        """
        import smtplib
        from email.mime.text import MIMEText
        
        subject = f"[{rule.severity.upper()}] Pipeline Alert: {event_type}"
        body = self._format_message(rule, event_type, run_id, data)
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(self.to_addrs)
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.send_message(msg)
    
    def _format_message(self, rule: AlertRule, event_type: str, run_id: str, data: dict) -> str:
        """Format alert message for email.
        
        Args:
            rule: Alert rule
            event_type: Event type
            run_id: Run ID
            data: Event data
            
        Returns:
            Formatted message body
        """
        message = f"Pipeline Alert\n\n"
        message += f"Severity: {rule.severity.upper()}\n"
        message += f"Event: {event_type}\n"
        message += f"Run ID: {run_id}\n"
        message += f"Time: {datetime.utcnow().isoformat()}Z\n\n"
        
        if 'error' in data:
            message += f"Error:\n{data['error']}\n\n"
        
        if 'metrics' in data:
            metrics = data['metrics']
            message += f"Metrics:\n"
            message += f"  Steps: {metrics.get('completed_steps', 0)}/{metrics.get('total_steps', 0)}\n"
            message += f"  Events: {metrics.get('total_events', 0)} ({metrics.get('error_events', 0)} errors)\n"
        
        return message
