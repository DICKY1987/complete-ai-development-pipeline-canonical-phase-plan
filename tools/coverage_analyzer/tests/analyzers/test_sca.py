"""Tests for SCA analyzer (Layer 0.5)."""

import pytest
from unittest.mock import Mock, patch

from coverage_analyzer.analyzers.sca import SCAAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, SCAMetrics
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError


class TestSCAAnalyzer:
    """Tests for SCAAnalyzer."""
    
    def test_initialization(self, tmp_path):
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python"
        )
        analyzer = SCAAnalyzer(config)
        assert analyzer.config == config
    
    def test_unsupported_language(self, tmp_path):
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="java"
        )
        analyzer = SCAAnalyzer(config)
        
        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze()
    
    def test_powershell_returns_empty_metrics(self, tmp_path):
        """PowerShell SCA not fully supported yet."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="powershell"
        )
        analyzer = SCAAnalyzer(config)
        
        metrics = analyzer.analyze()
        
        assert isinstance(metrics, SCAMetrics)
        assert metrics.total_dependencies == 0
        assert metrics.security_score == 100.0
        assert metrics.tool_name == "none"
    
    @patch('coverage_analyzer.analyzers.sca.get_registry')
    def test_analyze_python_no_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python"
        )
        
        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry
        
        analyzer = SCAAnalyzer(config)
        
        with pytest.raises(ToolNotAvailableError, match="No Python SCA tools"):
            analyzer.analyze()
    
    @patch('coverage_analyzer.analyzers.sca.get_registry')
    def test_analyze_python_pip_audit(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python"
        )
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_dependencies": 50,
            "vulnerable_dependencies": 3,
            "vulnerabilities": [
                {
                    "package": "django",
                    "installed_version": "2.2.0",
                    "cve": "CVE-2020-13254"
                }
            ],
            "security_score": 85.0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 2,
            "medium_vulnerabilities": 1,
            "low_vulnerabilities": 0,
            "tool_name": "pip-audit"
        }
        
        # Mock registry
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "pip-audit"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry
        
        analyzer = SCAAnalyzer(config)
        metrics = analyzer.analyze()
        
        assert isinstance(metrics, SCAMetrics)
        assert metrics.total_dependencies == 50
        assert metrics.vulnerable_dependencies == 3
        assert metrics.security_score == 85.0
        assert metrics.high_vulnerabilities == 2
        assert metrics.tool_name == "pip-audit"
    
    @patch('coverage_analyzer.analyzers.sca.get_registry')
    def test_analyze_python_safety_fallback(self, mock_get_registry, tmp_path):
        """Test fallback to safety when pip-audit not available."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python"
        )
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_dependencies": 30,
            "vulnerable_dependencies": 1,
            "vulnerabilities": [],
            "security_score": 95.0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 1,
            "low_vulnerabilities": 0,
            "tool_name": "safety"
        }
        
        # Mock registry - only safety available
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "safety"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry
        
        analyzer = SCAAnalyzer(config)
        metrics = analyzer.analyze()
        
        assert metrics.tool_name == "safety"
        assert metrics.security_score == 95.0
    
    @patch('coverage_analyzer.analyzers.sca.logger')
    @patch('coverage_analyzer.analyzers.sca.get_registry')
    def test_log_critical_vulnerabilities(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging when critical vulnerabilities found."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python",
            fail_on_critical_security=True
        )
        
        # Mock adapter with critical vulnerabilities
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_dependencies": 100,
            "vulnerable_dependencies": 5,
            "vulnerabilities": [],
            "security_score": 60.0,
            "critical_vulnerabilities": 2,  # Critical!
            "high_vulnerabilities": 3,
            "medium_vulnerabilities": 0,
            "low_vulnerabilities": 0,
            "tool_name": "pip-audit"
        }
        
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "pip-audit"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry
        
        analyzer = SCAAnalyzer(config)
        metrics = analyzer.analyze()
        
        # Should log errors for critical vulnerabilities
        assert mock_logger.error.called
        assert metrics.critical_vulnerabilities == 2
    
    @patch('coverage_analyzer.analyzers.sca.get_registry')
    def test_tool_execution_failure(self, mock_get_registry, tmp_path):
        """Test handling of tool execution failures."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python"
        )
        
        # Mock adapter that raises exception
        mock_adapter = Mock()
        mock_adapter.execute.side_effect = Exception("Network error")
        
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "pip-audit"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry
        
        analyzer = SCAAnalyzer(config)
        
        with pytest.raises(ToolNotAvailableError, match="SCA scan failed"):
            analyzer.analyze()
