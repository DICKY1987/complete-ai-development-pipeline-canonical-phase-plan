"""
Tests for audit logging module.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone

from aim.environment.audit import (
    AuditLogger,
    AuditEvent,
    EventType,
    EventSeverity,
    get_audit_logger
)


class TestAuditEvent:
    """Test cases for AuditEvent dataclass."""
    
    def test_event_creation(self):
        """Test creating an audit event."""
        event = AuditEvent(
            event_type=EventType.TOOL_INSTALL.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=EventSeverity.INFO.value,
            message="Test event"
        )
        
        assert event.event_type == "tool_install"
        assert event.severity == "info"
        assert event.message == "Test event"
        assert event.details == {}
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = AuditEvent(
            event_type=EventType.SECRET_SET.value,
            timestamp="2025-01-01T00:00:00",
            severity=EventSeverity.INFO.value,
            message="Test",
            details={"key": "value"},
            user="testuser",
            session_id="abc123"
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "secret_set"
        assert event_dict["user"] == "testuser"
        assert event_dict["details"]["key"] == "value"
    
    def test_event_to_jsonl(self):
        """Test converting event to JSON Lines format."""
        event = AuditEvent(
            event_type=EventType.HEALTH_CHECK.value,
            timestamp="2025-01-01T00:00:00",
            severity=EventSeverity.INFO.value,
            message="Health check"
        )
        
        jsonl = event.to_jsonl()
        
        assert isinstance(jsonl, str)
        parsed = json.loads(jsonl)
        assert parsed["event_type"] == "health_check"


class TestAuditLogger:
    """Test cases for AuditLogger class."""
    
    @pytest.fixture
    def temp_log_path(self, tmp_path):
        """Create temporary log path."""
        return tmp_path / "test_audit.jsonl"
    
    @pytest.fixture
    def logger(self, temp_log_path):
        """Create logger instance with temp path."""
        return AuditLogger(log_path=temp_log_path)
    
    def test_logger_initialization(self, logger, temp_log_path):
        """Test logger initializes correctly."""
        assert logger.log_path == temp_log_path
        assert logger.session_id is not None
        assert len(logger.session_id) == 8
        assert logger.user is not None
    
    def test_log_event(self, logger, temp_log_path):
        """Test logging an event."""
        logger.log_event(
            event_type=EventType.TOOL_INSTALL,
            message="Test installation",
            severity=EventSeverity.INFO,
            details={"tool": "test-tool"}
        )
        
        assert temp_log_path.exists()
        
        with open(temp_log_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        event_dict = json.loads(lines[0])
        assert event_dict["event_type"] == "tool_install"
        assert event_dict["message"] == "Test installation"
        assert event_dict["details"]["tool"] == "test-tool"
    
    def test_log_tool_install(self, logger, temp_log_path):
        """Test logging tool installation."""
        logger.log_tool_install("aider-chat", "0.45.0", "pipx", True)
        
        with open(temp_log_path, 'r') as f:
            event_dict = json.loads(f.read())
        
        assert event_dict["event_type"] == "tool_install"
        assert event_dict["details"]["tool"] == "aider-chat"
        assert event_dict["details"]["version"] == "0.45.0"
        assert event_dict["details"]["success"] is True
    
    def test_log_secret_access(self, logger, temp_log_path):
        """Test logging secret access."""
        logger.log_secret_access("set", "API_KEY", True)
        
        with open(temp_log_path, 'r') as f:
            event_dict = json.loads(f.read())
        
        assert event_dict["event_type"] == "secret_set"
        assert event_dict["details"]["key"] == "API_KEY"
        assert event_dict["details"]["action"] == "set"
        # Ensure value is NOT logged
        assert "value" not in event_dict["details"]
    
    def test_log_health_check(self, logger, temp_log_path):
        """Test logging health check."""
        logger.log_health_check("healthy", 5, 0)
        
        with open(temp_log_path, 'r') as f:
            event_dict = json.loads(f.read())
        
        assert event_dict["event_type"] == "health_check"
        assert event_dict["details"]["status"] == "healthy"
        assert event_dict["details"]["passed"] == 5
        assert event_dict["details"]["failed"] == 0
    
    def test_log_multiple_events(self, logger, temp_log_path):
        """Test logging multiple events."""
        logger.log_tool_install("tool1", "1.0", "pipx", True)
        logger.log_tool_install("tool2", "2.0", "npm", True)
        logger.log_health_check("healthy", 5, 0)
        
        with open(temp_log_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
    
    def test_query_events_by_type(self, logger):
        """Test querying events by type."""
        logger.log_tool_install("tool1", "1.0", "pipx", True)
        logger.log_secret_access("set", "KEY", True)
        logger.log_health_check("healthy", 5, 0)
        
        # Query for tool installs only
        events = logger.query_events(event_type=EventType.TOOL_INSTALL)
        
        assert len(events) == 1
        assert events[0].event_type == "tool_install"
    
    def test_query_events_by_severity(self, logger):
        """Test querying events by severity."""
        logger.log_tool_install("tool1", "1.0", "pipx", True)
        logger.log_tool_install("tool2", "2.0", "pipx", False)
        
        # Query for errors only
        events = logger.query_events(severity=EventSeverity.ERROR)
        
        assert len(events) == 1
        assert events[0].severity == "error"
    
    def test_query_events_with_limit(self, logger):
        """Test querying events with limit."""
        for i in range(10):
            logger.log_tool_install(f"tool{i}", "1.0", "pipx", True)
        
        events = logger.query_events(limit=5)
        
        assert len(events) == 5
    
    def test_get_recent_events(self, logger):
        """Test getting recent events."""
        for i in range(5):
            logger.log_tool_install(f"tool{i}", "1.0", "pipx", True)
        
        recent = logger.get_recent_events(count=3)
        
        assert len(recent) == 3
        # Should be in reverse order (newest first)
        assert recent[0].details["tool"] == "tool4"
    
    def test_get_stats(self, logger):
        """Test getting audit log statistics."""
        logger.log_tool_install("tool1", "1.0", "pipx", True)
        logger.log_tool_install("tool2", "2.0", "pipx", False)
        logger.log_secret_access("set", "KEY", True)
        logger.log_health_check("healthy", 5, 0)
        
        stats = logger.get_stats()
        
        assert stats["total_events"] == 4
        assert stats["by_type"]["tool_install"] == 2
        assert stats["by_type"]["secret_set"] == 1
        assert stats["by_severity"]["info"] == 3  # tool1 success, secret set, health check
        assert stats["by_severity"]["error"] == 1  # tool2 failure
        assert stats["log_size_bytes"] > 0
    
    def test_get_stats_empty_log(self, logger):
        """Test getting stats from empty log."""
        stats = logger.get_stats()
        
        assert stats["total_events"] == 0
        assert stats["log_size_bytes"] == 0
    
    def test_session_id_uniqueness(self, temp_log_path):
        """Test that each logger instance has unique session ID."""
        logger1 = AuditLogger(temp_log_path)
        logger2 = AuditLogger(temp_log_path)
        
        assert logger1.session_id != logger2.session_id
    
    def test_log_error(self, logger, temp_log_path):
        """Test logging error event."""
        logger.log_error("test_operation", "Test error message", {"context": "test"})
        
        with open(temp_log_path, 'r') as f:
            event_dict = json.loads(f.read())
        
        assert event_dict["event_type"] == "error"
        assert event_dict["severity"] == "error"
        assert "Test error message" in event_dict["message"]
        assert event_dict["details"]["operation"] == "test_operation"


class TestAuditLoggerFactory:
    """Test cases for audit logger factory function."""
    
    def test_get_audit_logger_singleton(self):
        """Test that get_audit_logger returns singleton instance."""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        
        assert logger1 is logger2
        assert logger1.session_id == logger2.session_id
    
    def test_get_audit_logger_with_path(self, tmp_path):
        """Test getting logger with custom path."""
        log_path = tmp_path / "custom_audit.jsonl"
        logger = get_audit_logger(log_path)
        
        assert logger.log_path == log_path


@pytest.mark.integration
class TestAuditLoggerIntegration:
    """Integration tests for audit logger."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete audit logging workflow."""
        log_path = tmp_path / "workflow_audit.jsonl"
        logger = AuditLogger(log_path)
        
        # Simulate various operations
        logger.log_tool_install("aider-chat", "0.45.0", "pipx", True)
        logger.log_secret_access("set", "ANTHROPIC_API_KEY", True)
        logger.log_health_check("healthy", 5, 0)
        logger.log_version_sync(3, 0)
        logger.log_scan("full", 2, 1)
        
        # Query and verify
        all_events = logger.get_recent_events(count=100)
        assert len(all_events) == 5
        
        # Get stats
        stats = logger.get_stats()
        assert stats["total_events"] == 5
        assert "tool_install" in stats["by_type"]
        assert "secret_set" in stats["by_type"]
        
        # Query specific events
        tool_events = logger.query_events(event_type=EventType.TOOL_INSTALL)
        assert len(tool_events) == 1
        assert tool_events[0].details["tool"] == "aider-chat"
