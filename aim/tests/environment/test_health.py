"""Unit tests for HealthMonitor."""

import pytest
from pathlib import Path

from aim.environment.health import HealthMonitor, HealthCheck, check_health


class TestHealthCheck:
    """Test HealthCheck dataclass."""
    
    def test_creation(self):
        """Test creating a HealthCheck."""
        check = HealthCheck(
            name="test",
            status="pass",
            message="Test message",
            details={"key": "value"},
            timestamp="2025-01-01T00:00:00Z"
        )
        
        assert check.name == "test"
        assert check.status == "pass"
        assert check.message == "Test message"
        assert check.details == {"key": "value"}
        assert check.timestamp == "2025-01-01T00:00:00Z"
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        check = HealthCheck(
            name="test",
            status="pass",
            message="Test message"
        )
        
        d = check.to_dict()
        assert d["name"] == "test"
        assert d["status"] == "pass"
        assert d["message"] == "Test message"


class TestHealthMonitor:
    """Test suite for HealthMonitor."""
    
    def test_initialization(self):
        """Test HealthMonitor initialization."""
        monitor = HealthMonitor()
        assert monitor._config is None
    
    def test_check_python(self):
        """Test Python version check."""
        monitor = HealthMonitor()
        result = monitor.check_python()
        
        assert result.name == "python"
        assert result.status in ["pass", "warn", "fail"]
        assert "Python" in result.message
        assert result.details is not None
        assert "version" in result.details
    
    def test_check_required_commands(self):
        """Test required commands check."""
        monitor = HealthMonitor()
        result = monitor.check_required_commands()
        
        assert result.name == "required_commands"
        assert result.status in ["pass", "warn", "fail"]
        assert result.details is not None
    
    def test_check_ai_tools(self):
        """Test AI tools detection."""
        monitor = HealthMonitor()
        result = monitor.check_ai_tools()
        
        assert result.name == "ai_tools"
        assert result.status in ["pass", "warn", "fail"]
        # Should have details about detected/not detected tools
        if result.status != "fail":
            assert result.details is not None
    
    def test_check_secrets_vault(self):
        """Test secrets vault check."""
        monitor = HealthMonitor()
        result = monitor.check_secrets_vault()
        
        assert result.name == "secrets_vault"
        assert result.status in ["pass", "warn", "fail"]
    
    def test_check_config(self):
        """Test configuration check."""
        monitor = HealthMonitor()
        result = monitor.check_config()
        
        assert result.name == "config"
        assert result.status in ["pass", "warn", "fail"]
    
    def test_check_all(self):
        """Test running all checks."""
        monitor = HealthMonitor()
        checks = monitor.check_all()
        
        assert len(checks) >= 5  # At least 5 checks
        assert all(isinstance(c, HealthCheck) for c in checks)
        
        # Verify all checks have required fields
        for check in checks:
            assert check.name
            assert check.status in ["pass", "warn", "fail"]
            assert check.message
            assert check.timestamp
    
    def test_generate_report(self):
        """Test report generation."""
        monitor = HealthMonitor()
        report = monitor.generate_report()
        
        assert "timestamp" in report
        assert "overall_status" in report
        assert report["overall_status"] in ["healthy", "degraded", "unhealthy"]
        assert "summary" in report
        assert "checks" in report
        
        # Verify summary counts
        summary = report["summary"]
        assert "pass" in summary
        assert "warn" in summary
        assert "fail" in summary
    
    def test_generate_report_with_checks(self):
        """Test report generation with provided checks."""
        monitor = HealthMonitor()
        
        checks = [
            HealthCheck("test1", "pass", "Test 1 passed"),
            HealthCheck("test2", "warn", "Test 2 warning"),
            HealthCheck("test3", "fail", "Test 3 failed"),
        ]
        
        report = monitor.generate_report(checks)
        
        assert report["overall_status"] == "unhealthy"  # Has failures
        assert report["summary"]["pass"] == 1
        assert report["summary"]["warn"] == 1
        assert report["summary"]["fail"] == 1
        assert len(report["checks"]) == 3
    
    def test_overall_status_healthy(self):
        """Test overall status when all checks pass."""
        monitor = HealthMonitor()
        
        checks = [
            HealthCheck("test1", "pass", "Test 1"),
            HealthCheck("test2", "pass", "Test 2"),
        ]
        
        report = monitor.generate_report(checks)
        assert report["overall_status"] == "healthy"
    
    def test_overall_status_degraded(self):
        """Test overall status with warnings but no failures."""
        monitor = HealthMonitor()
        
        checks = [
            HealthCheck("test1", "pass", "Test 1"),
            HealthCheck("test2", "warn", "Test 2"),
        ]
        
        report = monitor.generate_report(checks)
        assert report["overall_status"] == "degraded"
    
    def test_overall_status_unhealthy(self):
        """Test overall status with failures."""
        monitor = HealthMonitor()
        
        checks = [
            HealthCheck("test1", "pass", "Test 1"),
            HealthCheck("test2", "fail", "Test 2"),
        ]
        
        report = monitor.generate_report(checks)
        assert report["overall_status"] == "unhealthy"


class TestHealthConvenienceFunction:
    """Test convenience function."""
    
    def test_check_health(self):
        """Test check_health convenience function."""
        report = check_health()
        
        assert isinstance(report, dict)
        assert "overall_status" in report
        assert "checks" in report
        assert len(report["checks"]) >= 5


class TestHealthCheckEdgeCases:
    """Edge case tests."""
    
    def test_check_with_no_details(self):
        """Test HealthCheck without details."""
        check = HealthCheck("test", "pass", "Message")
        d = check.to_dict()
        
        assert "name" in d
        assert "status" in d
        assert "message" in d
        # details and timestamp should be omitted if None
        assert d.get("details") is None
    
    def test_empty_report(self):
        """Test generating report with no checks."""
        monitor = HealthMonitor()
        report = monitor.generate_report([])
        
        assert report["overall_status"] == "healthy"  # No failures = healthy
        assert report["summary"]["pass"] == 0
        assert len(report["checks"]) == 0
