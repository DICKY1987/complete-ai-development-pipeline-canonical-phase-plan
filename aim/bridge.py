"""AIM (AI Tools Registry) Bridge Module

This module provides a Python-to-PowerShell bridge for the AIM tool registry system.
It enables capability-based routing, fallback chains, and audit logging for AI tool invocations.

Contract Version: AIM_INTEGRATION_V1
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def get_aim_registry_path() -> Path:
    """Get the path to the AIM registry directory.

    Resolution order:
    1. AIM_REGISTRY_PATH environment variable
    2. Auto-detect relative to repository root (.AIM_ai-tools-registry)

    Returns:
        Path: Resolved AIM registry directory path

    Raises:
        FileNotFoundError: If AIM registry directory not found
    """
    # Check environment variable first
    env_path = os.getenv("AIM_REGISTRY_PATH")
    if env_path:
        aim_path = Path(env_path)
        if aim_path.exists():
            return aim_path
        raise FileNotFoundError(
            f"[AIM] AIM_REGISTRY_PATH env var set to '{env_path}' but directory not found"
        )

    # Auto-detect relative to aim section or repository root
    repo_root = Path(__file__).parent.parent
    
    # Try aim/.AIM_ai-tools-registry first (new location)
    aim_path = repo_root / "aim" / ".AIM_ai-tools-registry"
    if aim_path.exists():
        return aim_path
    
    # Fallback to root level .AIM_ai-tools-registry (old location)
    aim_path = repo_root / ".AIM_ai-tools-registry"
    if aim_path.exists():
        return aim_path

    raise FileNotFoundError(
        f"[AIM] Registry not found at {aim_path}. "
        f"Set AIM_REGISTRY_PATH environment variable or ensure .AIM_ai-tools-registry exists."
    )


def load_aim_registry() -> Dict[str, Any]:
    """Load the AIM registry JSON file.

    Returns:
        Dict[str, Any]: Parsed AIM registry data

    Raises:
        FileNotFoundError: If AIM_registry.json not found
        json.JSONDecodeError: If JSON is malformed
    """
    aim_path = get_aim_registry_path()
    registry_file = aim_path / "AIM_registry.json"

    if not registry_file.exists():
        raise FileNotFoundError(f"[AIM] Registry file not found: {registry_file}")

    with open(registry_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def load_coordination_rules() -> Dict[str, Any]:
    """Load the AIM coordination rules JSON file.

    Returns:
        Dict[str, Any]: Parsed coordination rules data

    Raises:
        FileNotFoundError: If coordination rules file not found
        json.JSONDecodeError: If JSON is malformed
    """
    aim_path = get_aim_registry_path()
    rules_file = aim_path / "AIM_cross-tool" / "AIM_coordination-rules.json"

    if not rules_file.exists():
        raise FileNotFoundError(f"[AIM] Coordination rules not found: {rules_file}")

    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def _load_aim_config() -> Dict[str, Any]:
    """Load AIM configuration from aim_config.yaml.

    Returns:
        Dict[str, Any]: AIM configuration with defaults
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "aim_config.yaml"

    # Default configuration
    defaults = {
        "enable_aim": True,
        "enable_audit_logging": True,
        "audit_log_retention_days": 30,
        "default_timeout_ms": 30000,
        "registry_path": "auto"
    }

    if not config_path.exists():
        return defaults

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Merge with defaults
    return {**defaults, **config}


def _expand_env_vars(path_str: str, aim_registry_path: Optional[Path] = None) -> str:
    """Expand environment variables in path string (Windows style).

    Args:
        path_str: Path with potential env vars like %USERPROFILE%
        aim_registry_path: Optional AIM registry path for %AIM_REGISTRY_PATH%

    Returns:
        str: Expanded path string
    """
    # Handle Windows environment variables (%VAR%)
    import re

    def replace_var(match):
        var_name = match.group(1)
        # Special handling for AIM_REGISTRY_PATH
        if var_name == "AIM_REGISTRY_PATH" and aim_registry_path:
            return str(aim_registry_path)
        return os.getenv(var_name, match.group(0))

    return re.sub(r'%(\w+)%', replace_var, path_str)


def invoke_adapter(
    tool_id: str,
    capability: str,
    payload: Dict[str, Any],
    timeout_sec: Optional[int] = None
) -> Dict[str, Any]:
    """Invoke a PowerShell adapter for a given tool and capability.

    Args:
        tool_id: Tool identifier from AIM registry (e.g., "aider")
        capability: Capability to invoke (e.g., "code_generation")
        payload: Input data for the capability
        timeout_sec: Subprocess timeout in seconds (default: from config)

    Returns:
        Dict[str, Any]: Result from adapter with keys:
            - success (bool): Whether invocation succeeded
            - message (str): Status message
            - content (Any): Result data

    Raises:
        KeyError: If tool_id not found in registry
        FileNotFoundError: If adapter script not found
    """
    config = _load_aim_config()

    # Get timeout from config if not specified
    if timeout_sec is None:
        timeout_sec = config["default_timeout_ms"] / 1000

    # Load registry and get tool metadata
    registry = load_aim_registry()
    aim_path = get_aim_registry_path()

    if tool_id not in registry.get("tools", {}):
        return {
            "success": False,
            "message": f"Tool '{tool_id}' not found in AIM registry",
            "content": None
        }

    tool = registry["tools"][tool_id]
    adapter_script_path = _expand_env_vars(tool.get("adapterScript", ""), aim_path)
    adapter_script = Path(adapter_script_path)

    if not adapter_script.exists():
        return {
            "success": False,
            "message": f"Adapter script not found: {adapter_script}",
            "content": None
        }

    # Build input JSON
    input_data = {
        "capability": capability,
        "payload": payload
    }
    input_json = json.dumps(input_data)

    # Invoke PowerShell adapter via subprocess
    try:
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(adapter_script)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )

        # Parse JSON output
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"Invalid JSON output from adapter: {e}",
                    "content": {"stdout": result.stdout, "stderr": result.stderr}
                }
        else:
            return {
                "success": False,
                "message": f"Adapter exited with code {result.returncode}: {result.stderr}",
                "content": {"exit_code": result.returncode, "stderr": result.stderr}
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": f"Adapter timed out after {timeout_sec}s",
            "content": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Subprocess error: {e}",
            "content": None
        }


def route_capability(
    capability: str,
    payload: Dict[str, Any],
    timeout_sec: Optional[int] = None
) -> Dict[str, Any]:
    """Route a capability request to the appropriate tool with fallback chain.

    Uses coordination rules to select primary tool, then tries fallbacks if primary fails.
    All attempts are logged to audit log.

    Args:
        capability: Capability to invoke (e.g., "code_generation")
        payload: Input data for the capability
        timeout_sec: Subprocess timeout in seconds (default: from config)

    Returns:
        Dict[str, Any]: Result from first successful tool

    Raises:
        KeyError: If capability not defined in coordination rules
    """
    config = _load_aim_config()

    # Load coordination rules
    try:
        rules = load_coordination_rules()
    except FileNotFoundError as e:
        return {
            "success": False,
            "message": f"Coordination rules not found: {e}",
            "content": None
        }

    if capability not in rules.get("capabilities", {}):
        return {
            "success": False,
            "message": f"Capability '{capability}' not defined in coordination rules",
            "content": None
        }

    cap_rules = rules["capabilities"][capability]
    primary_tool = cap_rules.get("primary")
    fallback_tools = cap_rules.get("fallback", [])

    # Try primary tool
    all_attempts = []

    if primary_tool:
        result = invoke_adapter(primary_tool, capability, payload, timeout_sec)

        # Record audit log
        if config["enable_audit_logging"]:
            record_audit_log(primary_tool, capability, payload, result)

        all_attempts.append((primary_tool, result))

        if result.get("success"):
            return result

    # Try fallback tools in order
    for fallback_tool in fallback_tools:
        result = invoke_adapter(fallback_tool, capability, payload, timeout_sec)

        # Record audit log
        if config["enable_audit_logging"]:
            record_audit_log(fallback_tool, capability, payload, result)

        all_attempts.append((fallback_tool, result))

        if result.get("success"):
            return result

    # All tools failed - return aggregated error
    failure_messages = [
        f"{tool}: {res.get('message', 'Unknown error')}"
        for tool, res in all_attempts
    ]

    return {
        "success": False,
        "message": f"All tools failed for capability '{capability}': {'; '.join(failure_messages)}",
        "content": {"attempts": all_attempts}
    }


def detect_tool(tool_id: str) -> bool:
    """Detect if a tool is installed by running its detection commands.

    Args:
        tool_id: Tool identifier from AIM registry

    Returns:
        bool: True if any detect command succeeds (exit code 0), False otherwise
    """
    try:
        registry = load_aim_registry()
    except (FileNotFoundError, json.JSONDecodeError):
        return False

    if tool_id not in registry.get("tools", {}):
        return False

    tool = registry["tools"][tool_id]
    detect_commands = tool.get("detectCommands", [])

    # Try each detect command
    for cmd in detect_commands:
        try:
            # Handle both string commands and list of args
            if isinstance(cmd, str):
                cmd_args = [cmd]
            else:
                cmd_args = cmd

            result = subprocess.run(
                cmd_args,
                capture_output=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    return False


def get_tool_version(tool_id: str) -> Optional[str]:
    """Get the version of an installed tool.

    Args:
        tool_id: Tool identifier from AIM registry

    Returns:
        str: Version string if command succeeds, None otherwise
    """
    try:
        registry = load_aim_registry()
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    if tool_id not in registry.get("tools", {}):
        return None

    tool = registry["tools"][tool_id]
    version_command = tool.get("versionCommand", [])

    if not version_command:
        return None

    try:
        result = subprocess.run(
            version_command,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def record_audit_log(
    tool_id: str,
    capability: str,
    payload: Dict[str, Any],
    result: Dict[str, Any]
) -> None:
    """Record an audit log entry for a tool invocation.

    Audit logs are written to: .AIM_ai-tools-registry/AIM_audit/<YYYY-MM-DD>/<timestamp>_<tool>_<capability>.json

    Args:
        tool_id: Tool that was invoked
        capability: Capability that was requested
        payload: Input data sent to adapter
        result: Output data from adapter
    """
    try:
        aim_path = get_aim_registry_path()
    except FileNotFoundError:
        # Cannot record audit log if registry not found
        return

    # Create audit directory structure
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    audit_dir = aim_path / "AIM_audit" / date_str

    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # Log warning but don't crash
        print(f"[AIM] Warning: Could not create audit directory: {e}")
        return

    # Build audit entry
    timestamp = now.isoformat() + "Z"
    timestamp_safe = now.strftime("%Y-%m-%dT%H-%M-%S-%f")  # Filename-safe
    filename = f"{timestamp_safe}_{tool_id}_{capability}.json"

    entry = {
        "timestamp": timestamp,
        "actor": "pipeline",
        "tool_id": tool_id,
        "capability": capability,
        "payload": payload,
        "result": result
    }

    # Write audit log
    audit_file = audit_dir / filename
    try:
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
    except OSError as e:
        # Log warning but don't crash
        print(f"[AIM] Warning: Could not write audit log: {e}")
