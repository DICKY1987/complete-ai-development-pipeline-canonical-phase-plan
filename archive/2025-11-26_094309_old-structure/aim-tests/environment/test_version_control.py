"""
Tests for version control module.

Tests version drift detection, syncing, and pinning operations.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.aim_environment.m01001B_version_control import (
    VersionControl,
    VersionReport,
    VersionStatus,
)


@pytest.fixture
def mock_config():
    """Mock configuration with version pins."""
    return {
        "environment": {
            "pipxApps": ["ruff", "black", "pytest"],
            "npmGlobal": ["eslint", "prettier"],
            "versionPins": {
                "pipx": {
                    "ruff": "0.14.1",
                    "black": "25.9.0"
                },
                "npm": {
                    "eslint": "9.39.0"
                }
            }
        }
    }


@pytest.fixture
def mock_installer(mock_config):
    """Mock installer."""
    installer = MagicMock()
    installer.config = mock_config
    return installer


@pytest.fixture
def version_control(mock_config, mock_installer):
    """VersionControl instance with mocks."""
    return VersionControl(mock_config, mock_installer)


class TestVersionStatus:
    """Tests for VersionStatus dataclass."""
    
    def test_has_drift_drift(self):
        """Test has_drift for drift status."""
        status = VersionStatus(
            tool="ruff",
            manager="pipx",
            expected_version="0.14.1",
            actual_version="0.14.0",
            status="drift"
        )
        assert status.has_drift is True
    
    def test_has_drift_missing(self):
        """Test has_drift for missing status."""
        status = VersionStatus(
            tool="ruff",
            manager="pipx",
            expected_version="0.14.1",
            actual_version=None,
            status="missing"
        )
        assert status.has_drift is True
    
    def test_has_drift_ok(self):
        """Test has_drift for ok status."""
        status = VersionStatus(
            tool="ruff",
            manager="pipx",
            expected_version="0.14.1",
            actual_version="0.14.1",
            status="ok"
        )
        assert status.has_drift is False
    
    def test_is_installed_true(self):
        """Test is_installed when tool is installed."""
        status = VersionStatus(
            tool="ruff",
            manager="pipx",
            expected_version="0.14.1",
            actual_version="0.14.1",
            status="ok"
        )
        assert status.is_installed is True
    
    def test_is_installed_false(self):
        """Test is_installed when tool is not installed."""
        status = VersionStatus(
            tool="ruff",
            manager="pipx",
            expected_version="0.14.1",
            actual_version=None,
            status="missing"
        )
        assert status.is_installed is False


class TestVersionReport:
    """Tests for VersionReport dataclass."""
    
    def test_counts(self):
        """Test all count properties."""
        report = VersionReport()
        report.statuses = [
            VersionStatus("tool1", "pipx", "1.0", "1.0", "ok"),
            VersionStatus("tool2", "pipx", "2.0", "2.0", "ok"),
            VersionStatus("tool3", "pipx", "3.0", "3.1", "drift"),
            VersionStatus("tool4", "pipx", "4.0", None, "missing"),
            VersionStatus("tool5", "pipx", None, "5.0", "unexpected"),
        ]
        
        assert report.total_count == 5
        assert report.ok_count == 2
        assert report.drift_count == 1
        assert report.missing_count == 1
        assert report.unexpected_count == 1
    
    def test_has_drift_true(self):
        """Test has_drift when drift exists."""
        report = VersionReport()
        report.statuses = [
            VersionStatus("tool1", "pipx", "1.0", "1.0", "ok"),
            VersionStatus("tool2", "pipx", "2.0", "2.1", "drift"),
        ]
        assert report.has_drift is True
    
    def test_has_drift_false(self):
        """Test has_drift when no drift."""
        report = VersionReport()
        report.statuses = [
            VersionStatus("tool1", "pipx", "1.0", "1.0", "ok"),
            VersionStatus("tool2", "pipx", "2.0", "2.0", "ok"),
        ]
        assert report.has_drift is False


class TestVersionControl:
    """Tests for VersionControl class."""
    
    @pytest.mark.asyncio
    async def test_check_version_ok(self, version_control, mock_installer):
        """Test checking version when it matches."""
        mock_installer._get_installed_version = AsyncMock(return_value="0.14.1")
        
        status = await version_control.check_version("ruff", "pipx", "0.14.1")
        
        assert status.tool == "ruff"
        assert status.manager == "pipx"
        assert status.expected_version == "0.14.1"
        assert status.actual_version == "0.14.1"
        assert status.status == "ok"
    
    @pytest.mark.asyncio
    async def test_check_version_drift(self, version_control, mock_installer):
        """Test checking version when it differs."""
        mock_installer._get_installed_version = AsyncMock(return_value="0.14.0")
        
        status = await version_control.check_version("ruff", "pipx", "0.14.1")
        
        assert status.status == "drift"
        assert status.actual_version == "0.14.0"
        assert status.expected_version == "0.14.1"
    
    @pytest.mark.asyncio
    async def test_check_version_missing(self, version_control, mock_installer):
        """Test checking version when tool not installed."""
        mock_installer._get_installed_version = AsyncMock(return_value=None)
        
        status = await version_control.check_version("ruff", "pipx", "0.14.1")
        
        assert status.status == "missing"
        assert status.actual_version is None
    
    @pytest.mark.asyncio
    async def test_check_version_no_pin(self, version_control, mock_installer):
        """Test checking version when no specific version required."""
        mock_installer._get_installed_version = AsyncMock(return_value="1.0.0")
        
        status = await version_control.check_version("tool", "pipx", None)
        
        assert status.status == "ok"
        assert status.expected_version is None
    
    @pytest.mark.asyncio
    async def test_check_all_pipx(self, version_control, mock_installer):
        """Test checking all pipx tools."""
        async def mock_get_version(manager, package):
            versions = {
                "ruff": "0.14.1",
                "black": "25.9.0",
                "pytest": "8.0.0"
            }
            return versions.get(package)
        
        mock_installer._get_installed_version = mock_get_version
        
        report = await version_control.check_all("pipx")
        
        assert len(report.statuses) == 3
        # All match since pytest has no pin (any version is ok)
        assert report.ok_count == 3
        assert all(s.manager == "pipx" for s in report.statuses)
    
    @pytest.mark.asyncio
    async def test_check_all_managers(self, version_control, mock_installer):
        """Test checking all managers."""
        async def mock_get_version(manager, package):
            return "1.0.0"
        
        mock_installer._get_installed_version = mock_get_version
        
        report = await version_control.check_all()
        
        # Should have both pipx (3) and npm (2) tools
        assert len(report.statuses) == 5
        assert any(s.manager == "pipx" for s in report.statuses)
        assert any(s.manager == "npm" for s in report.statuses)
    
    @pytest.mark.asyncio
    async def test_sync_dry_run(self, version_control, mock_installer):
        """Test sync in dry-run mode."""
        async def mock_get_version(manager, package):
            # Return old version to trigger sync
            return "0.13.0"
        
        mock_installer._get_installed_version = mock_get_version
        
        results = await version_control.sync(dry_run=True)
        
        # Should report what would be done
        assert len(results) > 0
        # Filter out the ones without pins (they show as "Already synced")
        drift_results = [r for r in results if r[0] in ["ruff", "black", "eslint"]]
        assert all("Would" in msg for _, _, msg in drift_results)
    
    @pytest.mark.asyncio
    async def test_sync_already_synced(self, version_control, mock_installer):
        """Test sync when already in sync."""
        async def mock_get_version(manager, package):
            pins = {
                "ruff": "0.14.1",
                "black": "25.9.0",
                "eslint": "9.39.0"
            }
            return pins.get(package, "1.0.0")
        
        mock_installer._get_installed_version = mock_get_version
        
        results = await version_control.sync()
        
        # All should be already synced
        assert all(success for _, success, _ in results)
        assert all("Already synced" in msg for _, _, msg in results)
    
    @pytest.mark.asyncio
    async def test_sync_install_missing(self, version_control, mock_installer):
        """Test sync installs missing tools."""
        from modules.aim_environment.m01001B_installer import InstallResult
        
        async def mock_get_version(manager, package):
            return None  # All missing
        
        async def mock_install_pipx(package, version, force):
            return InstallResult(package, "pipx", True, version or "1.0.0", "OK")
        
        async def mock_install_npm(package, version, force):
            return InstallResult(package, "npm", True, version or "1.0.0", "OK")
        
        mock_installer._get_installed_version = mock_get_version
        mock_installer.install_pipx = mock_install_pipx
        mock_installer.install_npm = mock_install_npm
        
        results = await version_control.sync()
        
        # All should be successfully synced
        assert all(success for _, success, _ in results)
        assert all("Synced to" in msg for _, _, msg in results)
    
    @pytest.mark.asyncio
    async def test_sync_force(self, version_control, mock_installer):
        """Test sync with force flag."""
        from modules.aim_environment.m01001B_installer import InstallResult
        
        async def mock_get_version(manager, package):
            # Return matching version
            return "0.14.1"
        
        async def mock_install_pipx(package, version, force):
            return InstallResult(package, "pipx", True, version, "OK")
        
        async def mock_install_npm(package, version, force):
            return InstallResult(package, "npm", True, version, "OK")
        
        mock_installer._get_installed_version = mock_get_version
        mock_installer.install_pipx = mock_install_pipx
        mock_installer.install_npm = mock_install_npm
        
        results = await version_control.sync(force=True)
        
        # Should reinstall even though versions match
        assert len(results) > 0
        # Should not say "already synced"
        assert not any("Already synced" in msg for _, _, msg in results)
    
    @pytest.mark.asyncio
    async def test_pin_current_versions(self, version_control, mock_installer):
        """Test pinning current versions."""
        async def mock_get_version(manager, package):
            versions = {
                "ruff": "0.14.1",
                "black": "25.9.0",
                "pytest": "8.0.0",
                "eslint": "9.39.0",
                "prettier": "3.0.0"
            }
            return versions.get(package)
        
        mock_installer._get_installed_version = mock_get_version
        
        pins = await version_control.pin_current_versions()
        
        assert "pipx" in pins
        assert "npm" in pins
        assert pins["pipx"]["ruff"] == "0.14.1"
        assert pins["pipx"]["black"] == "25.9.0"
        assert pins["npm"]["eslint"] == "9.39.0"
    
    @pytest.mark.asyncio
    async def test_pin_current_versions_single_manager(self, version_control, mock_installer):
        """Test pinning current versions for single manager."""
        async def mock_get_version(manager, package):
            return "1.0.0"
        
        mock_installer._get_installed_version = mock_get_version
        
        pins = await version_control.pin_current_versions("pipx")
        
        # Should only have pipx pins
        assert pins["pipx"]
        assert not pins["npm"]
    
    def test_update_config_pins(self, version_control):
        """Test updating config with new pins."""
        new_pins = {
            "pipx": {"tool1": "1.0.0", "tool2": "2.0.0"},
            "npm": {"tool3": "3.0.0"}
        }
        
        version_control.update_config_pins(new_pins)
        
        pins = version_control.config["environment"]["versionPins"]
        assert pins["pipx"]["tool1"] == "1.0.0"
        assert pins["npm"]["tool3"] == "3.0.0"
    
    def test_update_config_pins_creates_structure(self):
        """Test updating config creates necessary structure."""
        vc = VersionControl({})
        
        new_pins = {"pipx": {"tool1": "1.0.0"}}
        vc.update_config_pins(new_pins)
        
        assert "environment" in vc.config
        assert "versionPins" in vc.config["environment"]
        assert vc.config["environment"]["versionPins"]["pipx"]["tool1"] == "1.0.0"
