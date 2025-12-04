"""
Template: Tool Adapter Template
Purpose: Subprocess-based CLI tool adapter template for UET Framework
Version: 1.0.0
Dependencies: core.adapters.base, core.engine.resilience
Last Updated: 2025-11-23

Usage:
    1. Copy: cp tool-adapter-template.py my_tool_adapter.py
    2. Implement the three required methods:
       - detect_capabilities()
       - execute()
       - validate_result()
    3. Register in router_config.json
    4. Test: pytest tests/adapters/test_my_tool_adapter.py

Placeholders:
    {{TOOL_NAME}}       - Name of the CLI tool (e.g., "mytool")
    {{CAPABILITIES}}    - List of capabilities (e.g., ["linting", "formatting"])
    {{VERSION_CMD}}     - Command to check version (e.g., ["mytool", "--version"])
"""
# DOC_ID: DOC-PAT-SUBPROCESS-TOOL-ADAPTER-TEMPLATE-970

import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Framework imports
# from core.adapters.base import ToolAdapter, ExecutionRequest, ExecutionResult, ValidationResult
# from core.engine.resilience import retry_with_backoff

logger = logging.getLogger(__name__)


class {{TOOL_NAME}}Adapter:  # Implement ToolAdapter interface
    """
    Adapter for {{TOOL_NAME}} CLI tool.

    This adapter wraps the {{TOOL_NAME}} command-line tool and provides
    integration with the UET Framework execution engine.

    Capabilities:
        - {{CAPABILITIES[0]}}
        - {{CAPABILITIES[1]}}
        # Add more capabilities as needed

    Example:
        adapter = {{TOOL_NAME}}Adapter()
        capabilities = adapter.detect_capabilities()

        request = ExecutionRequest(
            task_id="task-001",
            work_dir="/path/to/project"
        )
        result = adapter.execute(request)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter.

        Args:
            config: Optional configuration dictionary
                   - tool_path: Path to tool executable
                   - default_args: Default arguments to pass
                   - timeout: Default timeout in seconds
        """
        self.tool_name = "{{TOOL_NAME}}"
        self.config = config or {}
        self.tool_path = self.config.get('tool_path', self.tool_name)
        self.default_args = self.config.get('default_args', [])
        self.default_timeout = self.config.get('timeout', 300)

        logger.info(f"Initialized {self.tool_name} adapter")

    def detect_capabilities(self) -> Dict[str, Any]:
        """
        Detect if tool is available and what capabilities it provides.

        Returns:
            Dict containing:
                - available: bool - Is tool installed/accessible
                - version: str - Tool version
                - capabilities: List[str] - What the tool can do
                - path: str - Path to tool executable

        Example:
            {
                "available": True,
                "version": "1.2.3",
                "capabilities": ["linting", "formatting"],
                "path": "/usr/local/bin/mytool"
            }
        """
        try:
            # Check if tool is available
            result = subprocess.run(
                {{VERSION_CMD}},  # e.g., ["mytool", "--version"]
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                return {
                    "available": True,
                    "version": version,
                    "capabilities": {{CAPABILITIES}},
                    "path": self.tool_path
                }
            else:
                logger.warning(f"{self.tool_name} found but returned error: {result.stderr}")
                return {
                    "available": False,
                    "version": None,
                    "capabilities": [],
                    "path": None
                }

        except FileNotFoundError:
            logger.error(f"{self.tool_name} not found in PATH")
            return {
                "available": False,
                "version": None,
                "capabilities": [],
                "path": None
            }
        except subprocess.TimeoutExpired:
            logger.error(f"{self.tool_name} version check timed out")
            return {
                "available": False,
                "version": None,
                "capabilities": [],
                "path": None
            }

    # @retry_with_backoff(max_retries=3, base_delay=1.0)
    def execute(self, request) -> Dict[str, Any]:  # ExecutionRequest -> ExecutionResult
        """
        Execute the tool with given request.

        Args:
            request: ExecutionRequest with:
                - task_id: str - Task identifier
                - work_dir: str - Working directory
                - parameters: Dict - Tool-specific parameters
                - timeout: Optional[int] - Timeout override

        Returns:
            ExecutionResult with:
                - status: str - "success", "failed", or "timeout"
                - output: str - Tool stdout
                - errors: str - Tool stderr
                - exit_code: int - Process exit code
                - duration: float - Execution time in seconds

        Raises:
            Exception: If execution fails unexpectedly
        """
        logger.info(f"Executing {self.tool_name} for task {request.task_id}")

        # Build command
        cmd = self._build_command(request)
        timeout = request.timeout or self.default_timeout
        work_dir = Path(request.work_dir) if request.work_dir else None

        try:
            import time
            start_time = time.time()

            # Execute tool
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir
            )

            duration = time.time() - start_time

            # Determine status
            status = "success" if result.returncode == 0 else "failed"

            logger.info(f"{self.tool_name} completed with status: {status} (took {duration:.2f}s)")

            return {
                "status": status,
                "output": result.stdout,
                "errors": result.stderr,
                "exit_code": result.returncode,
                "duration": duration
            }

        except subprocess.TimeoutExpired:
            logger.error(f"{self.tool_name} execution timed out after {timeout}s")
            return {
                "status": "timeout",
                "output": "",
                "errors": f"Execution timed out after {timeout} seconds",
                "exit_code": -1,
                "duration": timeout
            }
        except Exception as e:
            logger.error(f"{self.tool_name} execution failed: {str(e)}")
            return {
                "status": "failed",
                "output": "",
                "errors": str(e),
                "exit_code": -1,
                "duration": 0
            }

    def validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool execution result.

        Args:
            result: ExecutionResult from execute()

        Returns:
            ValidationResult with:
                - valid: bool - Is result valid
                - errors: List[str] - Validation errors if any
                - warnings: List[str] - Validation warnings

        Example:
            {
                "valid": True,
                "errors": [],
                "warnings": ["Output format could be improved"]
            }
        """
        errors = []
        warnings = []

        # Check if execution succeeded
        if result['status'] != 'success':
            errors.append(f"Execution status: {result['status']}")

        # Check for error patterns in output
        if result['errors']:
            # Parse stderr for known error patterns
            error_output = result['errors'].lower()
            if 'error' in error_output:
                errors.append("Tool reported errors in stderr")
            elif 'warning' in error_output:
                warnings.append("Tool reported warnings")

        # Validate output format (customize based on tool)
        if result['output']:
            # Example: Check if output is non-empty
            pass
        else:
            warnings.append("No output generated")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _build_command(self, request) -> List[str]:
        """
        Build command line from request.

        Args:
            request: ExecutionRequest

        Returns:
            List of command parts

        Example:
            ["mytool", "check", "--fix", "src/"]
        """
        cmd = [self.tool_path]

        # Add default arguments
        cmd.extend(self.default_args)

        # Add request-specific arguments
        if hasattr(request, 'parameters') and request.parameters:
            # Parse parameters into CLI arguments
            for key, value in request.parameters.items():
                if isinstance(value, bool) and value:
                    cmd.append(f"--{key}")
                elif value is not None:
                    cmd.extend([f"--{key}", str(value)])

        return cmd


# Example usage
if __name__ == "__main__":
    # Test adapter
    adapter = {{TOOL_NAME}}Adapter()

    # Check capabilities
    caps = adapter.detect_capabilities()
    print(f"Capabilities: {caps}")

    # Example execution (would need real ExecutionRequest)
    # request = ExecutionRequest(
    #     task_id="test-001",
    #     work_dir=".",
    #     parameters={"check": True}
    # )
    # result = adapter.execute(request)
    # validation = adapter.validate_result(result)
    # print(f"Result: {result}")
    # print(f"Validation: {validation}")
