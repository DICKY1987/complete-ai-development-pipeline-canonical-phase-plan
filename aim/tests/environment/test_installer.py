"""
Tests for the tool installer module.

Tests installation, uninstallation, version checking, and rollback
for pipx, npm, and winget package managers.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aim.environment.installer import InstallResult, ToolInstaller


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
def installer(mock_config):
    """Tool installer instance with mock config."""
    return ToolInstaller(mock_config)


class TestToolInstaller:
    """Tests for ToolInstaller class."""
    
    @pytest.mark.asyncio
    async def test_run_command_success(self, installer):
        """Test successful command execution."""
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(
                return_value=(b"output", b"")
            )
            mock_exec.return_value = mock_proc
            
            returncode, stdout, stderr = await installer._run_command(["echo", "test"])
            
            assert returncode == 0
            assert stdout == "output"
            assert stderr == ""
    
    @pytest.mark.asyncio
    async def test_run_command_failure(self, installer):
        """Test failed command execution."""
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(
                return_value=(b"", b"error message")
            )
            mock_exec.return_value = mock_proc
            
            returncode, stdout, stderr = await installer._run_command(["false"])
            
            assert returncode == 1
            assert stderr == "error message"
    
    @pytest.mark.asyncio
    async def test_run_command_timeout(self, installer):
        """Test command timeout handling."""
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_proc = AsyncMock()
            
            async def slow_communicate():
                await asyncio.sleep(10)
                return (b"", b"")
            
            mock_proc.communicate = slow_communicate
            mock_exec.return_value = mock_proc
            
            returncode, stdout, stderr = await installer._run_command(
                ["sleep", "10"],
                timeout=1
            )
            
            assert returncode == -1
            assert "timed out" in stderr.lower()
    
    @pytest.mark.asyncio
    async def test_get_installed_version_pipx(self, installer):
        """Test getting installed version for pipx package."""
        pipx_list_output = {
            "venvs": {
                "ruff": {
                    "metadata": {
                        "main_package": {
                            "package": "ruff",
                            "package_version": "0.14.1"
                        }
                    }
                }
            }
        }
        
        with patch.object(
            installer,
            "_run_command",
            return_value=(0, json.dumps(pipx_list_output), "")
        ):
            version = await installer._get_installed_version("pipx", "ruff")
            assert version == "0.14.1"
    
    @pytest.mark.asyncio
    async def test_get_installed_version_npm(self, installer):
        """Test getting installed version for npm package."""
        npm_list_output = {
            "dependencies": {
                "eslint": {
                    "version": "9.39.0"
                }
            }
        }
        
        with patch.object(
            installer,
            "_run_command",
            return_value=(0, json.dumps(npm_list_output), "")
        ):
            version = await installer._get_installed_version("npm", "eslint")
            assert version == "9.39.0"
    
    @pytest.mark.asyncio
    async def test_get_installed_version_not_found(self, installer):
        """Test getting version for non-installed package."""
        with patch.object(
            installer,
            "_run_command",
            return_value=(1, "", "not found")
        ):
            version = await installer._get_installed_version("pipx", "nonexistent")
            assert version is None
    
    @pytest.mark.asyncio
    async def test_install_pipx_success(self, installer):
        """Test successful pipx installation."""
        with patch.object(
            installer,
            "_get_installed_version",
            side_effect=[None, "0.14.1"]  # Not installed, then installed
        ), patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully installed", "")
        ):
            result = await installer.install_pipx("ruff", "0.14.1")
            
            assert result.success
            assert result.tool == "ruff"
            assert result.manager == "pipx"
            assert result.version == "0.14.1"
    
    @pytest.mark.asyncio
    async def test_install_pipx_already_installed(self, installer):
        """Test pipx installation when already installed."""
        with patch.object(
            installer,
            "_get_installed_version",
            return_value="0.14.1"
        ):
            result = await installer.install_pipx("ruff", "0.14.1", force=False)
            
            assert result.success
            assert "Already installed" in result.message
            assert result.version == "0.14.1"
    
    @pytest.mark.asyncio
    async def test_install_pipx_with_version_pin(self, installer):
        """Test pipx installation using version pin from config."""
        with patch.object(
            installer,
            "_get_installed_version",
            side_effect=[None, "0.14.1"]
        ), patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully installed", "")
        ) as mock_cmd:
            result = await installer.install_pipx("ruff")  # No version specified
            
            # Should use pinned version
            assert result.success
            mock_cmd.assert_called_once()
            cmd = mock_cmd.call_args[0][0]
            assert "ruff==0.14.1" in cmd
    
    @pytest.mark.asyncio
    async def test_install_pipx_failure(self, installer):
        """Test failed pipx installation."""
        with patch.object(
            installer,
            "_get_installed_version",
            return_value=None
        ), patch.object(
            installer,
            "_run_command",
            return_value=(1, "", "Installation failed")
        ):
            result = await installer.install_pipx("ruff")
            
            assert not result.success
            assert "Installation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_install_npm_success(self, installer):
        """Test successful npm installation."""
        with patch.object(
            installer,
            "_get_installed_version",
            side_effect=[None, "9.39.0"]
        ), patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully installed", "")
        ):
            result = await installer.install_npm("eslint", "9.39.0")
            
            assert result.success
            assert result.tool == "eslint"
            assert result.manager == "npm"
            assert result.version == "9.39.0"
    
    @pytest.mark.asyncio
    async def test_install_npm_with_version_pin(self, installer):
        """Test npm installation using version pin from config."""
        with patch.object(
            installer,
            "_get_installed_version",
            side_effect=[None, "9.39.0"]
        ), patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully installed", "")
        ) as mock_cmd:
            result = await installer.install_npm("eslint")  # No version specified
            
            assert result.success
            mock_cmd.assert_called_once()
            cmd = mock_cmd.call_args[0][0]
            assert "eslint@9.39.0" in cmd
    
    @pytest.mark.asyncio
    async def test_install_winget_success(self, installer):
        """Test successful winget installation."""
        with patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully installed", "")
        ):
            result = await installer.install_winget("Git.Git", "2.42.0")
            
            assert result.success
            assert result.tool == "Git.Git"
            assert result.manager == "winget"
            assert result.version == "2.42.0"
    
    @pytest.mark.asyncio
    async def test_uninstall_pipx(self, installer):
        """Test pipx uninstallation."""
        with patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully uninstalled", "")
        ):
            success = await installer.uninstall_pipx("ruff")
            assert success
    
    @pytest.mark.asyncio
    async def test_uninstall_npm(self, installer):
        """Test npm uninstallation."""
        with patch.object(
            installer,
            "_run_command",
            return_value=(0, "Successfully uninstalled", "")
        ):
            success = await installer.uninstall_npm("eslint")
            assert success
    
    @pytest.mark.asyncio
    async def test_rollback_uninstall(self, installer):
        """Test rollback by uninstalling new package."""
        result = InstallResult(
            tool="ruff",
            manager="pipx",
            success=True,
            version="0.14.1",
            message="Installed",
            rollback_data={"previous_version": None}  # Was not installed before
        )
        
        with patch.object(installer, "uninstall_pipx", return_value=True):
            success = await installer.rollback(result)
            assert success
    
    @pytest.mark.asyncio
    async def test_rollback_reinstall(self, installer):
        """Test rollback by reinstalling previous version."""
        result = InstallResult(
            tool="ruff",
            manager="pipx",
            success=True,
            version="0.14.1",
            message="Installed",
            rollback_data={"previous_version": "0.13.0"}
        )
        
        mock_result = InstallResult(
            tool="ruff",
            manager="pipx",
            success=True,
            version="0.13.0",
            message="Rolled back"
        )
        
        with patch.object(
            installer,
            "install_pipx",
            return_value=mock_result
        ) as mock_install:
            success = await installer.rollback(result)
            assert success
            mock_install.assert_called_once_with("ruff", version="0.13.0", force=True)
    
    @pytest.mark.asyncio
    async def test_install_all_success(self, installer):
        """Test installing multiple tools successfully."""
        tools = [
            {"name": "ruff", "manager": "pipx"},
            {"name": "eslint", "manager": "npm"}
        ]
        
        mock_results = [
            InstallResult("ruff", "pipx", True, "0.14.1", "OK"),
            InstallResult("eslint", "npm", True, "9.39.0", "OK")
        ]
        
        with patch.object(
            installer,
            "install_pipx",
            return_value=mock_results[0]
        ), patch.object(
            installer,
            "install_npm",
            return_value=mock_results[1]
        ):
            results = await installer.install_all(tools, rollback_on_failure=False)
            
            assert len(results) == 2
            assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_install_all_with_rollback(self, installer):
        """Test rollback on failure when installing multiple tools."""
        tools = [
            {"name": "ruff", "manager": "pipx"},
            {"name": "eslint", "manager": "npm"}
        ]
        
        mock_results = [
            InstallResult("ruff", "pipx", True, "0.14.1", "OK"),
            InstallResult("eslint", "npm", False, "", "Failed")
        ]
        
        with patch.object(
            installer,
            "install_pipx",
            return_value=mock_results[0]
        ), patch.object(
            installer,
            "install_npm",
            return_value=mock_results[1]
        ), patch.object(
            installer,
            "rollback",
            return_value=True
        ) as mock_rollback:
            results = await installer.install_all(tools, rollback_on_failure=True)
            
            # Should have rolled back the successful installation
            mock_rollback.assert_called_once()
            assert any(not r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_install_from_config_pipx(self, installer):
        """Test installing all pipx tools from config."""
        mock_result = InstallResult("ruff", "pipx", True, "0.14.1", "OK")
        
        with patch.object(
            installer,
            "install_all",
            return_value=[mock_result, mock_result, mock_result]
        ) as mock_install_all:
            results = await installer.install_from_config("pipx")
            
            # Should create tools list from config
            call_args = mock_install_all.call_args[0][0]
            assert len(call_args) == 3  # ruff, black, pytest
            assert all(t["manager"] == "pipx" for t in call_args)
    
    @pytest.mark.asyncio
    async def test_install_from_config_npm(self, installer):
        """Test installing all npm tools from config."""
        mock_result = InstallResult("eslint", "npm", True, "9.39.0", "OK")
        
        with patch.object(
            installer,
            "install_all",
            return_value=[mock_result, mock_result]
        ) as mock_install_all:
            results = await installer.install_from_config("npm")
            
            call_args = mock_install_all.call_args[0][0]
            assert len(call_args) == 2  # eslint, prettier
            assert all(t["manager"] == "npm" for t in call_args)
    
    @pytest.mark.asyncio
    async def test_install_all_exception_handling(self, installer):
        """Test exception handling during parallel installation."""
        tools = [
            {"name": "ruff", "manager": "pipx"},
            {"name": "eslint", "manager": "npm"}
        ]
        
        with patch.object(
            installer,
            "install_pipx",
            side_effect=Exception("Network error")
        ), patch.object(
            installer,
            "install_npm",
            return_value=InstallResult("eslint", "npm", True, "9.39.0", "OK")
        ):
            results = await installer.install_all(tools, rollback_on_failure=False)
            
            assert len(results) == 2
            assert not results[0].success
            assert "Network error" in results[0].message
            assert results[1].success
