"""Unit tests for StructuredLogger."""

import pytest
import sys
import json
from io import StringIO
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '..')

from structured_logger import StructuredLogger


class TestStructuredLogger:
    """Test StructuredLogger functionality."""

    def test_logger_creation(self):
        """Logger can be created with a name."""
        logger = StructuredLogger(name="test-logger")
        assert logger.name == "test-logger"

    def test_info_logging(self, capsys):
        """Info messages are logged correctly."""
        logger = StructuredLogger(name="test")
        logger.info("Test info message", key="value", count=42)
        
        captured = capsys.readouterr()
        log_line = captured.err.strip()
        
        # Parse JSON log
        log_data = json.loads(log_line)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test"
        assert log_data["message"] == "Test info message"
        assert log_data["data"]["key"] == "value"
        assert log_data["data"]["count"] == 42

    def test_error_logging(self, capsys):
        """Error messages are logged correctly."""
        logger = StructuredLogger(name="test")
        logger.error("Error occurred", error_code="ERR-001", severity="high")
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Error occurred"
        assert log_data["data"]["error_code"] == "ERR-001"

    def test_warning_logging(self, capsys):
        """Warning messages are logged correctly."""
        logger = StructuredLogger(name="test")
        logger.warning("Warning message", threshold=80, current=95)
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        assert log_data["level"] == "WARNING"
        assert log_data["data"]["threshold"] == 80

    def test_debug_logging(self, capsys):
        """Debug messages are logged correctly."""
        logger = StructuredLogger(name="test")
        logger.debug("Debug info", variable="value")
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        assert log_data["level"] == "DEBUG"

    def test_job_event_logging(self, capsys):
        """Job events are logged correctly."""
        logger = StructuredLogger(name="test")
        logger.job_event(job_id="job-123", event="started", worker="worker-01")
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        assert log_data["level"] == "JOB"
        assert log_data["message"] == "job_event:job-123:started"
        assert log_data["data"]["job_id"] == "job-123"
        assert log_data["data"]["event"] == "started"
        assert log_data["data"]["worker"] == "worker-01"

    def test_timestamp_format(self, capsys):
        """Timestamps are in ISO 8601 format with UTC timezone."""
        logger = StructuredLogger(name="test")
        logger.info("Test timestamp")
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        timestamp = log_data["timestamp"]
        # Should be ISO 8601 format
        assert "T" in timestamp
        # Should have timezone info
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp[-6:]

    def test_empty_context(self, capsys):
        """Logging without context data works."""
        logger = StructuredLogger(name="test")
        logger.info("Simple message")
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        # Should not have 'data' key if no context provided
        assert "data" not in log_data or log_data["data"] == {}

    def test_multiple_loggers(self, capsys):
        """Multiple logger instances maintain separate names."""
        logger1 = StructuredLogger(name="logger-1")
        logger2 = StructuredLogger(name="logger-2")
        
        logger1.info("Message from logger 1")
        logger2.info("Message from logger 2")
        
        captured = capsys.readouterr()
        lines = captured.err.strip().split('\n')
        
        log1 = json.loads(lines[0])
        log2 = json.loads(lines[1])
        
        assert log1["logger"] == "logger-1"
        assert log2["logger"] == "logger-2"

    def test_complex_data_types(self, capsys):
        """Complex data types are serialized correctly."""
        logger = StructuredLogger(name="test")
        logger.info("Complex data", 
                   nested={"key": "value", "count": 42},
                   list_data=[1, 2, 3],
                   bool_flag=True,
                   none_value=None)
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.err.strip())
        
        assert log_data["data"]["nested"]["key"] == "value"
        assert log_data["data"]["list_data"] == [1, 2, 3]
        assert log_data["data"]["bool_flag"] is True
        assert log_data["data"]["none_value"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
