"""Process Pool Interface Definitions

Defines the contracts and interfaces for multi-instance tool process management.
Supports launching multiple CLI tool instances and managing interactive stdin/stdout.

Contract Version: POOL_V1
"""
# DOC_ID: DOC-AIM-POOL-INTERFACE-001

from dataclasses import dataclass
from typing import Protocol, Dict, Any, List, Optional
import subprocess
import queue


@dataclass
class ProcessInstance:
    """Represents a single tool process instance.
    
    Attributes:
        index: Unique index within the pool (0 to count-1)
        tool_id: Tool identifier from AIM registry
        process: Subprocess.Popen instance
        stdout_queue: Queue for buffered stdout lines
        stderr_queue: Queue for buffered stderr lines
        alive: Whether process is responsive
    """
    index: int
    tool_id: str
    process: subprocess.Popen
    stdout_queue: queue.Queue
    stderr_queue: queue.Queue
    alive: bool = True


class ProcessPoolInterface(Protocol):
    """Protocol for process pool implementations.
    
    Defines the contract for managing multiple long-lived CLI tool processes.
    Implementations must support:
    - Spawning N instances of a tool
    - Sending interactive prompts to specific instances
    - Reading responses from stdout queues
    - Health monitoring and graceful shutdown
    """
    
    def send_prompt(self, instance_idx: int, prompt: str) -> bool:
        """Send prompt to specific instance via stdin.
        
        Args:
            instance_idx: Instance index (0 to count-1)
            prompt: Command/prompt to send (newline appended automatically)
            
        Returns:
            bool: True if sent successfully, False if instance dead/invalid
        """
        ...
    
    def read_response(self, instance_idx: int, timeout: float = 5.0) -> Optional[str]:
        """Read response from instance stdout queue.
        
        Args:
            instance_idx: Instance index
            timeout: Max seconds to wait for response
            
        Returns:
            str: Response line (without trailing newline), or None if timeout/error
        """
        ...
    
    def get_status(self) -> List[Dict[str, Any]]:
        """Get status of all instances.
        
        Returns:
            List of status dicts with keys:
                - index: Instance index
                - alive: Whether instance is running
                - return_code: Exit code if terminated, None if still running
        """
        ...
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """Gracefully shutdown all instances.
        
        Args:
            timeout: Seconds to wait for graceful exit before force kill
        """
        ...


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
        - Use context manager for automatic cleanup (if implemented)
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
        ...
    
    def send_prompt(self, instance_idx: int, prompt: str) -> bool:
        """Send prompt to specific instance."""
        ...
    
    def read_response(self, instance_idx: int, timeout: float = 5.0) -> Optional[str]:
        """Read response from instance stdout."""
        ...
    
    def get_status(self) -> List[Dict[str, Any]]:
        """Get status of all instances."""
        ...
    
    def check_health(self) -> Dict[str, Any]:
        """Check health of all instances.
        
        Returns:
            Health report with keys:
                - total: Total instance count
                - alive: Number of alive instances
                - dead: Number of dead instances
                - instances: List of per-instance status
        """
        ...
    
    def restart_instance(self, instance_idx: int) -> bool:
        """Restart a dead instance.
        
        Args:
            instance_idx: Instance to restart
            
        Returns:
            bool: True if restarted successfully
        """
        ...
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """Gracefully shutdown all instances."""
        ...


# Protocol expectations for tool stdin/stdout
TOOL_PROTOCOL_EXPECTATIONS = {
    "aider": {
        "prompt_ready": ">",  # Aider uses ">" as prompt
        "needs_flags": ["--yes-always"],  # Prevent blocking confirmations
        "completion_markers": ["Commit", "Applied"],
        "error_markers": ["Error:", "error:", "failed"]
    },
    "jules": {
        "prompt_ready": "jules>",
        "needs_flags": [],
        "completion_markers": ["Done", "Complete"],
        "error_markers": ["Error", "Failed"]
    },
    "codex": {
        "prompt_ready": "codex>",
        "needs_flags": [],
        "completion_markers": ["✓", "Success"],
        "error_markers": ["✗", "Error"]
    }
}
