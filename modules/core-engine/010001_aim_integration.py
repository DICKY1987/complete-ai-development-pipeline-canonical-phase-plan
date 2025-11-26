"""AIM Integration Helper for Orchestrator.

Provides capability-based tool routing with fallback to direct tool invocation.
Enables the orchestrator to use AIM when available while maintaining backward
compatibility with direct tool calls.

AIM+ Features:
- Pre-flight health checks
- Version drift detection
- Audit logging for all operations
"""

from typing import Any, Dict, Optional
import logging
import asyncio

from aim.bridge import route_capability, load_aim_registry
from aim.exceptions import (
    AIMError,
    AIMRegistryNotFoundError,
    AIMCapabilityNotFoundError,
    AIMAllToolsFailedError,
)
from modules.core_engine.010001_tools import ToolResult, run_tool

# AIM+ imports
from modules.aim_environment.01001B_health import HealthMonitor
from modules.aim_environment.01001B_version_control import VersionControl
from modules.aim_environment.01001B_audit import get_audit_logger, EventType, EventSeverity
from modules.aim_environment.01001B_installer import ToolInstaller
from modules.aim_registry.01001C_config_loader import ConfigLoader

logger = logging.getLogger(__name__)


def is_aim_available() -> bool:
    """Check if AIM registry is available.
    
    Returns:
        bool: True if AIM registry can be loaded, False otherwise
    """
    try:
        load_aim_registry()
        return True
    except (AIMRegistryNotFoundError, FileNotFoundError):
        return False


# AIM+ Health Check Integration
_health_monitor = None
_audit_logger = None


def get_health_monitor() -> HealthMonitor:
    """Get singleton health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def get_aim_audit_logger():
    """Get singleton audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = get_audit_logger()
    return _audit_logger


def run_pre_flight_checks(run_id: str, ws_id: str) -> Dict[str, Any]:
    """Run AIM+ pre-flight checks before workstream execution.
    
    Args:
        run_id: Workstream run identifier
        ws_id: Workstream identifier
    
    Returns:
        dict: Pre-flight check results with health, version status
    
    Raises:
        RuntimeError: If system health is unhealthy (critical failures)
    """
    audit = get_aim_audit_logger()
    health_mon = get_health_monitor()
    
    logger.info(f"[{run_id}:{ws_id}] Running AIM+ pre-flight checks")
    
    # Health checks
    health_report = health_mon.generate_report()
    audit.log_health_check(
        health_report["overall_status"],
        health_report["summary"]["pass"],
        health_report["summary"]["fail"]
    )
    
    if health_report["overall_status"] == "unhealthy":
        error_msg = f"Pre-flight health check failed: {health_report['summary']['fail']} failures"
        audit.log_error("pre_flight_check", error_msg)
        raise RuntimeError(error_msg)
    
    # Version drift detection (warning only)
    version_drift = None
    try:
        config = ConfigLoader().load()
        installer = ToolInstaller(config)
        vc = VersionControl(config, installer)
        
        # Run async version check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ver_report = loop.run_until_complete(vc.check_all())
        loop.close()
        
        if ver_report.has_drift:
            version_drift = {
                "drift_count": ver_report.drift_count,
                "missing_count": ver_report.missing_count,
                "total": ver_report.total_count
            }
            logger.warning(
                f"[{run_id}:{ws_id}] Version drift detected: "
                f"{ver_report.drift_count} drifted, {ver_report.missing_count} missing"
            )
    except Exception as e:
        logger.warning(f"[{run_id}:{ws_id}] Version check failed: {e}")
        # Continue execution - version drift is not critical
    
    results = {
        "health_status": health_report["overall_status"],
        "health_summary": health_report["summary"],
        "version_drift": version_drift,
        "pre_flight_passed": True
    }
    
    logger.info(f"[{run_id}:{ws_id}] Pre-flight checks passed")
    return results


def execute_with_aim(
    capability: str,
    payload: Dict[str, Any],
    fallback_tool: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
) -> ToolResult:
    """Execute a capability via AIM with optional fallback to direct tool invocation.
    
    This function provides a unified interface for the orchestrator to execute
    capabilities. It tries AIM routing first, and falls back to direct tool
    invocation if AIM is unavailable or fails.
    
    Args:
        capability: Capability to invoke (e.g., "code_generation")
        payload: Capability payload (files, prompt, etc.)
        fallback_tool: Tool ID to use if AIM fails (optional)
        context: Additional context for execution (optional)
        run_id: Run identifier for logging (optional)
        ws_id: Workstream identifier for logging (optional)
    
    Returns:
        ToolResult: Standardized result from tool execution
    
    Raises:
        Exception: If both AIM and fallback fail
    """
    context = context or {}
    
    # Log attempt
    logger.info(
        f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
        f"Executing capability '{capability}' via AIM"
    )
    
    # Try AIM routing first
    aim_result = None
    aim_error = None
    
    try:
        aim_result = route_capability(
            capability=capability,
            payload=payload,
            timeout_sec=payload.get("timeout_ms", 60000) // 1000 if "timeout_ms" in payload else None
        )
        
        # Convert AIM result to ToolResult
        if aim_result.get("success"):
            content = aim_result.get("content", {})
            
            # Determine which tool was actually used (from audit or fallback chain)
            tool_used = content.get("tool_id", "aim_routed")
            
            return ToolResult(
                tool_id=tool_used,
                command_line=f"aim route_capability {capability}",
                exit_code=content.get("exit_code", 0),
                stdout=content.get("stdout", ""),
                stderr=content.get("stderr", ""),
                timed_out=False,
                started_at=content.get("started_at", ""),
                completed_at=content.get("completed_at", ""),
                duration_sec=content.get("duration_sec", 0.0),
                success=True
            )
        else:
            # AIM failed, but we got a result
            aim_error = aim_result.get("message", "AIM routing failed")
            logger.warning(
                f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
                f"AIM routing failed: {aim_error}"
            )
    
    except AIMCapabilityNotFoundError as e:
        aim_error = f"Capability '{capability}' not defined in AIM"
        logger.warning(
            f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
            f"{aim_error}. Available: {e.available_capabilities}"
        )
    
    except AIMAllToolsFailedError as e:
        aim_error = f"All tools failed for capability '{capability}'"
        logger.error(
            f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
            f"{aim_error}. Attempts: {len(e.attempts)}"
        )
    
    except AIMError as e:
        aim_error = f"AIM error: {str(e)}"
        logger.error(
            f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
            f"{aim_error}"
        )
    
    except Exception as e:
        aim_error = f"Unexpected error: {str(e)}"
        logger.exception(
            f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
            f"Unexpected error in AIM routing: {e}"
        )
    
    # Fallback to direct tool invocation if specified
    if fallback_tool and aim_error:
        logger.info(
            f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
            f"Falling back to direct tool invocation: {fallback_tool}"
        )
        
        try:
            # Map capability payload to tool context
            tool_context = {
                "repo_root": context.get("repo_root"),
                "worktree_path": context.get("worktree_path"),
                **payload  # Include all payload fields
            }
            
            return run_tool(
                tool_id=fallback_tool,
                context=tool_context,
                run_id=run_id,
                ws_id=ws_id
            )
        
        except Exception as fallback_error:
            logger.error(
                f"[{run_id or 'N/A'}:{ws_id or 'N/A'}] "
                f"Fallback tool '{fallback_tool}' also failed: {fallback_error}"
            )
            
            # Return failed ToolResult with both errors
            return ToolResult(
                tool_id=fallback_tool,
                command_line=f"fallback to {fallback_tool} after AIM failure",
                exit_code=1,
                stdout="",
                stderr=f"AIM: {aim_error}\nFallback: {str(fallback_error)}",
                timed_out=False,
                started_at="",
                completed_at="",
                duration_sec=0.0,
                success=False
            )
    
    # No fallback, return AIM failure
    if aim_error:
        return ToolResult(
            tool_id="aim",
            command_line=f"aim route_capability {capability}",
            exit_code=1,
            stdout="",
            stderr=aim_error,
            timed_out=False,
            started_at="",
            completed_at="",
            duration_sec=0.0,
            success=False
        )
    
    # Should not reach here, but handle defensive case
    return ToolResult(
        tool_id="aim",
        command_line=f"aim route_capability {capability}",
        exit_code=1,
        stdout="",
        stderr="Unknown error in AIM integration",
        timed_out=False,
        started_at="",
        completed_at="",
        duration_sec=0.0,
        success=False
    )
