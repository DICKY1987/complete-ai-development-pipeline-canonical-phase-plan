"""AIM (AI Tools Registry) Bridge Module

This module provides a Python-to-PowerShell bridge for the AIM tool registry system.
It enables capability-based routing, fallback chains, and audit logging for AI tool invocations.

Enhanced with AIM+ features:
- Automatic secret injection via SecretsManager
- Environment validation
- Unified configuration

Contract Version: AIM_PLUS_V1 (backward compatible with AIM_INTEGRATION_V1)
"""
# DOC_ID: DOC-AIM-AIM-BRIDGE-080
# DOC_ID: DOC-AIM-AIM-BRIDGE-075
# DOC_ID: DOC-AIM-AIM-BRIDGE-072
# DOC_ID: DOC-AIM-AIM-BRIDGE-070

import json
import os
import queue
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# AIM+ imports (graceful degradation if not available)
try:
    from modules.aim_environment.m01001B_secrets import get_secrets_manager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False


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
    # Find repository root (where config/ directory lives)
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "aim_config.yaml"

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

    # AIM+: Inject secrets into environment if available
    env_with_secrets = os.environ.copy()
    if SECRETS_AVAILABLE:
        try:
            secrets_manager = get_secrets_manager()
            # Inject common AI tool secrets
            secret_keys = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
                "GITHUB_TOKEN"
            ]
            secrets = secrets_manager.inject_into_env(secret_keys)
            env_with_secrets.update(secrets)
        except Exception:
            # Gracefully degrade if secrets unavailable
            pass

    # Invoke PowerShell adapter via subprocess
    try:
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(adapter_script)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env_with_secrets  # Use environment with secrets
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


# ============================================================================
# Process Pool Implementation (Multi-Instance CLI Control)
# ============================================================================

from aim.pool_interface import ProcessInstance


class ToolProcessPool:
    """Manage multiple long-lived tool CLI instances.
    
    Spawns N instances of a tool from AIM registry and manages their lifecycle.
    Uses background threads to read stdout/stderr into queues, enabling
    non-blocking interactive communication.
    
    Example:
        pool = ToolProcessPool("aider", count=3)
        pool.send_prompt(0, "/add core/state.py")
        response = pool.read_response(0, timeout=10)
        pool.shutdown()
    
    Thread Safety:
        - send_prompt() and read_response() are thread-safe
        - Each instance has dedicated I/O threads
        - Queue operations are internally synchronized
    
    Resource Management:
        - Always call shutdown() to cleanup processes
    """
    
    def __init__(self, tool_id: str, count: int, registry: Optional[Dict] = None):
        """Initialize process pool.
        
        Args:
            tool_id: Tool from AIM registry (e.g., "aider", "jules", "codex")
            count: Number of instances to spawn (1-10 recommended)
            registry: Optional registry override (for testing)
            
        Raises:
            ValueError: If tool_id not in registry
            RuntimeError: If process spawn fails
        """
        self.tool_id = tool_id
        self.count = count
        self.instances: List[ProcessInstance] = []
        self.registry = registry or load_aim_registry()
        
        # Validate tool exists
        if tool_id not in self.registry.get("tools", {}):
            raise ValueError(f"Tool '{tool_id}' not in AIM registry")
        
        # Spawn instances
        for i in range(count):
            self._spawn_instance(i)
    
    def _spawn_instance(self, index: int) -> ProcessInstance:
        """Spawn a single tool instance with I/O threads."""
        tool_config = self.registry["tools"][self.tool_id]
        
        # Build command from registry
        detect_cmds = tool_config["detectCommands"]
        cmd = detect_cmds[0] if isinstance(detect_cmds[0], list) else [detect_cmds[0]]
        
        # Ensure cmd is a list
        if not isinstance(cmd, list):
            cmd = [cmd]
        
        # Add flags for interactive mode based on tool
        if self.tool_id == "aider" and "--yes-always" not in cmd:
            cmd.append("--yes-always")  # Non-blocking mode
        
        # Spawn process
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )
        
        # Create output queues
        stdout_q = queue.Queue()
        stderr_q = queue.Queue()
        
        # Start reader threads
        threading.Thread(
            target=self._read_stream,
            args=(proc.stdout, stdout_q),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self._read_stream,
            args=(proc.stderr, stderr_q),
            daemon=True
        ).start()
        
        instance = ProcessInstance(
            index=index,
            tool_id=self.tool_id,
            process=proc,
            stdout_queue=stdout_q,
            stderr_queue=stderr_q
        )
        
        self.instances.append(instance)
        return instance
    
    def _read_stream(self, stream, q: queue.Queue):
        """Background thread to read stream into queue."""
        try:
            for line in stream:
                q.put(line.rstrip('\n'))
        except ValueError:
            # Stream closed
            pass
        finally:
            try:
                stream.close()
            except Exception:
                pass
    
    def send_prompt(self, instance_idx: int, prompt: str) -> bool:
        """Send prompt to specific instance.
        
        Args:
            instance_idx: Instance index (0 to count-1)
            prompt: Command/prompt to send
            
        Returns:
            bool: True if sent successfully
        """
        if instance_idx >= len(self.instances):
            return False
        
        instance = self.instances[instance_idx]
        if not instance.alive:
            return False
        
        try:
            instance.process.stdin.write(prompt + "\n")
            instance.process.stdin.flush()
            return True
        except (BrokenPipeError, OSError):
            instance.alive = False
            return False
    
    def read_response(self, instance_idx: int, timeout: float = 5.0) -> Optional[str]:
        """Read response from instance stdout.
        
        Args:
            instance_idx: Instance index
            timeout: Max seconds to wait for response
            
        Returns:
            str: Response line, or None if timeout/error
        """
        if instance_idx >= len(self.instances):
            return None
        
        instance = self.instances[instance_idx]
        
        try:
            line = instance.stdout_queue.get(timeout=timeout)
            return line
        except queue.Empty:
            return None
    
    def get_status(self) -> List[Dict[str, Any]]:
        """Get status of all instances.
        
        Returns:
            List of status dicts with index, alive, return_code
        """
        statuses = []
        for inst in self.instances:
            statuses.append({
                "index": inst.index,
                "alive": inst.alive and inst.process.poll() is None,
                "return_code": inst.process.poll()
            })
        return statuses
    
    def check_health(self) -> Dict[str, Any]:
        """Check health of all instances.
        
        Returns:
            Health report with alive count, dead count, details
        """
        statuses = self.get_status()
        alive_count = sum(1 for s in statuses if s["alive"])
        
        return {
            "total": len(self.instances),
            "alive": alive_count,
            "dead": len(self.instances) - alive_count,
            "instances": statuses
        }
    
    def restart_instance(self, instance_idx: int) -> bool:
        """Restart a dead instance.
        
        Args:
            instance_idx: Instance to restart
            
        Returns:
            bool: True if restarted successfully
        """
        if instance_idx >= len(self.instances):
            return False
        
        old_instance = self.instances[instance_idx]
        
        # Kill old process if still running
        if old_instance.process.poll() is None:
            try:
                old_instance.process.kill()
                old_instance.process.wait()
            except OSError:
                pass
        
        # Spawn new instance
        try:
            new_instance = self._spawn_instance(instance_idx)
            self.instances[instance_idx] = new_instance
            return True
        except Exception:
            return False
    
    def shutdown(self, timeout: float = 5.0):
        """Gracefully shutdown all instances.
        
        Args:
            timeout: Seconds to wait for graceful exit
        """
        for inst in self.instances:
            if inst.process.poll() is None:
                try:
                    inst.process.terminate()
                except OSError:
                    pass
        
        # Wait for all to exit
        start = time.time()
        while time.time() - start < timeout:
            if all(inst.process.poll() is not None for inst in self.instances):
                break
            time.sleep(0.1)
        
        # Force kill stragglers
        for inst in self.instances:
            if inst.process.poll() is None:
                inst.process.kill()
                inst.process.wait()
