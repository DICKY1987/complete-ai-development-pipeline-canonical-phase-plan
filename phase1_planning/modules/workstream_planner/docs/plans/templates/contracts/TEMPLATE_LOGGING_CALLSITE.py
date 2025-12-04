# DOC_LINK: DOC-CORE-CONTRACTS-TEMPLATE-LOGGING-CALLSITE-205
# TEMPLATE: Logging Callsite
# Purpose: Standard pattern for logging events using LogEventV1 contract
# Usage: Copy these snippets wherever you need to log events

"""
Standard logging patterns using LogEventV1 contract.
"""

from datetime import datetime, timezone
from modules.logging_shared import append_event
from modules.shared_types import LogEventV1


# ============================================================================
# TEMPLATE: Log Phase Completed
# ============================================================================

def log_phase_completed(run_id: str, ws_id: str, phase_id: str, details: dict = None) -> None:
    """Log successful phase completion."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "phase.completed",
        "run_id": run_id,
        "ws_id": ws_id,
        "phase_id": phase_id,
        "doc_ids": [],  # Add relevant doc_ids if available
        "summary": f"Phase {phase_id} completed successfully",
        "details": details or {},
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Log Task Failed
# ============================================================================

def log_task_failed(
    run_id: str,
    ws_id: str,
    phase_id: str,
    error_msg: str,
    details: dict = None
) -> None:
    """Log task failure."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "task.failed",
        "run_id": run_id,
        "ws_id": ws_id,
        "phase_id": phase_id,
        "doc_ids": [],
        "summary": f"Task failed: {error_msg}",
        "details": {
            "error_message": error_msg,
            **(details or {})
        },
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Log Error Detected
# ============================================================================

def log_error_detected(
    run_id: str,
    error_id: str,
    error_kind: str,
    message: str,
    details: dict = None
) -> None:
    """Log error detection."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "error.detected",
        "run_id": run_id,
        "ws_id": "",  # Fill if available
        "phase_id": "",  # Fill if available
        "doc_ids": [],
        "summary": f"{error_kind}: {message}",
        "details": {
            "error_id": error_id,
            "error_kind": error_kind,
            **(details or {})
        },
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Log Pattern Execution
# ============================================================================

def log_pattern_execution(
    run_id: str,
    pattern_id: str,
    operation_kind: str,
    success: bool,
    files_touched: list = None,
    details: dict = None
) -> None:
    """Log pattern execution."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "pattern.executed" if success else "pattern.failed",
        "run_id": run_id,
        "ws_id": "",
        "phase_id": "",
        "doc_ids": [],
        "summary": f"Pattern {pattern_id} {'succeeded' if success else 'failed'}",
        "details": {
            "pattern_id": pattern_id,
            "operation_kind": operation_kind,
            "files_touched": files_touched or [],
            **(details or {})
        },
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Log Validation Result
# ============================================================================

def log_validation_result(
    run_id: str,
    validation_type: str,
    passed: bool,
    issues_found: int = 0,
    details: dict = None
) -> None:
    """Log validation result."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "validation.completed",
        "run_id": run_id,
        "ws_id": "",
        "phase_id": "",
        "doc_ids": [],
        "summary": f"{validation_type} validation {'passed' if passed else 'failed'} ({issues_found} issues)",
        "details": {
            "validation_type": validation_type,
            "passed": passed,
            "issues_found": issues_found,
            **(details or {})
        },
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Log File Operation
# ============================================================================

def log_file_operation(
    run_id: str,
    operation: str,  # "created" | "modified" | "deleted"
    file_path: str,
    # DOC_ID: str = None,
    details: dict = None
) -> None:
    """Log file operation."""
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": f"file.{operation}",
        "run_id": run_id,
        "ws_id": "",
        "phase_id": "",
        "doc_ids": [doc_id] if doc_id else [],
        "summary": f"File {operation}: {file_path}",
        "details": {
            "file_path": file_path,
            "operation": operation,
            **(details or {})
        },
    }
    append_event(event)


# ============================================================================
# TEMPLATE: Generic Event Logger (when you need custom events)
# ============================================================================

def log_custom_event(
    event_type: str,
    summary: str,
    run_id: str = "",
    ws_id: str = "",
    phase_id: str = "",
    doc_ids: list = None,
    details: dict = None
) -> None:
    """
    Log custom event following LogEventV1 contract.

    Use this when none of the specific templates above fit.
    """
    event: LogEventV1 = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "run_id": run_id,
        "ws_id": ws_id,
        "phase_id": phase_id,
        "doc_ids": doc_ids or [],
        "summary": summary,
        "details": details or {},
    }
    append_event(event)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # Example 1: Log phase completion
    log_phase_completed(
        run_id="RUN-001",
        ws_id="WS-01",
        phase_id="PH-01A",
        details={"files_created": 3, "tests_passed": 12}
    )

    # Example 2: Log task failure
    log_task_failed(
        run_id="RUN-001",
        ws_id="WS-01",
        phase_id="PH-01A",
        error_msg="Import error: module not found",
        details={"module": "missing_module", "file": "core/state/db.py"}
    )

    # Example 3: Log error detection
    log_error_detected(
        run_id="RUN-001",
        error_id="ERR-001",
        error_kind="execution_failure",
        message="Pytest failed with 2 failures",
        details={"failed_tests": ["test_a", "test_b"]}
    )

    # Example 4: Log pattern execution
    log_pattern_execution(
        run_id="RUN-001",
        pattern_id="PAT-EXEC-ATOMIC-CREATE-001",
        operation_kind="EXEC-ATOMIC-CREATE",
        success=True,
        files_touched=["core/state/new_file.py"]
    )
