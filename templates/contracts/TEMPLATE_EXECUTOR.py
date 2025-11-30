# TEMPLATE: Executor Module
# Purpose: Implements ExecutionRequestV1/ExecutionResultV1 contract
# Location: modules/executors/{name}_executor.py

"""
{Executor Name} Executor

Executes {operation_kind} operations following the UET contract.
"""

from typing import Dict, Any
from modules.shared_types import ExecutionRequestV1, ExecutionResultV1
from modules.logging_shared import log_event
from modules.error_shared import build_error

def run(request: ExecutionRequestV1) -> ExecutionResultV1:
    """
    Execute operation according to ExecutionRequestV1 contract.
    
    REQUIRED CONTRACT:
    - Accepts ExecutionRequestV1
    - Returns ExecutionResultV1
    - Never raises unhandled exceptions
    - All errors captured in result.error
    
    Args:
        request: ExecutionRequestV1 containing operation details
        
    Returns:
        ExecutionResultV1 with success status and outputs
    """
    try:
        # 1. Extract inputs from request
        operation_kind = request["operation_kind"]
        workspace = request["workspace"]
        file_scope = request["file_scope"]
        inputs = request["inputs"]
        context = request["context"]
        
        # 2. Perform the actual work
        # TODO: Implement executor-specific logic here
        # Example:
        # - CLI calls
        # - File edits
        # - AST transformations
        # - API calls
        
        files_touched = []  # Track all modified files
        patch_path = None   # Optional: path to generated patch
        
        # 3. Build successful result
        result: ExecutionResultV1 = {
            "success": True,
            "stdout": "",  # Capture command output
            "stderr": "",
            "files_touched": files_touched,
            "patch_path": patch_path,
            "error": None,
        }
        
        # 4. Log successful execution
        log_event({
            "event_type": "execution.completed",
            "run_id": context.get("run_id"),
            "operation_kind": operation_kind,
            "summary": f"Successfully executed {operation_kind}",
            "details": {
                "files_touched": len(files_touched),
                "workspace": workspace,
            }
        })
        
        return result
        
    except Exception as exc:
        # 5. Handle errors without propagating exceptions
        error = build_error(
            kind="execution_failure",
            message=str(exc),
            details={
                "exception_type": type(exc).__name__,
                "operation_kind": request.get("operation_kind"),
            },
            context={
                "request": request,
                "workspace": request.get("workspace"),
            },
        )
        
        # 6. Log error event
        log_event({
            "event_type": "execution.failed",
            "run_id": request.get("context", {}).get("run_id"),
            "summary": f"Execution failed: {str(exc)}",
            "details": error,
        })
        
        # 7. Return error result (never raise)
        return {
            "success": False,
            "stdout": "",
            "stderr": str(exc),
            "files_touched": [],
            "patch_path": None,
            "error": error,
        }


def validate_request(request: ExecutionRequestV1) -> bool:
    """
    Validate that request conforms to contract.
    
    Optional helper - implement if you need pre-execution validation.
    
    Args:
        request: Request to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["operation_kind", "workspace", "file_scope", "inputs"]
    return all(field in request for field in required_fields)


# Internal helpers below (prefix with _)

def _perform_operation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal operation implementation.
    
    This is private - external callers must use run().
    """
    # TODO: Implement specific operation logic
    pass
