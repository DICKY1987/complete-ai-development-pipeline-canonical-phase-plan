# DOC_LINK: DOC-CORE-CONTRACTS-TEMPLATE-ERROR-PLUGIN-202
# TEMPLATE: Error Detection Plugin
# Purpose: Implements ErrorEventV1 contract for error handling
# Location: modules/error_plugins/{name}_plugin.py

"""
{Plugin Name} Error Plugin

Detects and handles {error_type} errors following UET contract.
"""

from typing import Optional, List, Dict, Any
from modules.error_shared import ErrorEventV1
from modules.logging_shared import log_event, append_event
from modules.shared_types import ExecutionRequestV1, ExecutionResultV1


def handle_error(error: ErrorEventV1) -> None:
    """
    Handle error event according to ErrorEventV1 contract.

    REQUIRED CONTRACT:
    - Pure function from ErrorEventV1 → side effects (logs, suggestions)
    - MUST NOT modify code directly; only suggest or log
    - MUST NOT raise exceptions

    Args:
        error: ErrorEventV1 containing error details
    """
    try:
        # 1. Extract error details
        error_id = error["error_id"]
        kind = error["kind"]
        message = error["message"]
        details = error["details"]

        # 2. Check if this plugin handles this error kind
        if not _should_handle(kind):
            return

        # 3. Analyze error and generate suggestions
        suggestions = _analyze_error(error)

        # 4. Log plugin processing
        log_event({
            "event_type": "error.plugin.processed",
            "run_id": error.get("run_id"),
            "summary": f"Processed {kind} error with {len(suggestions)} suggestions",
            "details": {
                "plugin": "{plugin_name}",
                "error_id": error_id,
                "suggestions_count": len(suggestions),
            }
        })

        # 5. Record suggestions for later review
        if suggestions:
            _record_suggestions(error_id, suggestions)

    except Exception as exc:
        # Plugin failures MUST NOT break error handling pipeline
        log_event({
            "event_type": "error.plugin.failed",
            "summary": f"Plugin {'{plugin_name}'} failed: {str(exc)}",
            "details": {
                "plugin": "{plugin_name}",
                "error_id": error.get("error_id"),
                "exception": str(exc),
            }
        })


def detect_errors(
    request: ExecutionRequestV1,
    result: ExecutionResultV1
) -> List[ErrorEventV1]:
    """
    Detect errors from execution result.

    Optional: Implement if plugin does proactive error detection.

    Args:
        request: Original execution request
        result: Execution result to analyze

    Returns:
        List of detected ErrorEventV1 events
    """
    errors = []

    # TODO: Implement error detection logic
    # Example:
    # - Parse stdout/stderr for error patterns
    # - Check exit codes
    # - Validate outputs against schema

    return errors


def suggest_fix(error: ErrorEventV1) -> Optional[Dict[str, Any]]:
    """
    Suggest automated fix for error.

    Optional: Implement if plugin can suggest fixes.

    Args:
        error: Error to analyze

    Returns:
        Fix suggestion dict or None if no fix available
    """
    # TODO: Implement fix suggestion logic
    # Return format:
    # {
    #     "fix_type": "automated" | "manual",
    #     "description": "...",
    #     "actions": [...],
    #     "confidence": 0.0-1.0,
    # }
    return None


# Internal helpers (prefix with _)

def _should_handle(error_kind: str) -> bool:
    """
    Check if this plugin handles the given error kind.

    Args:
        error_kind: Error kind from ErrorEventV1

    Returns:
        True if this plugin handles this error type
    """
    # TODO: Define which error kinds this plugin handles
    handled_kinds = [
        "execution_failure",
        "validation_failure",
        # Add more kinds as needed
    ]
    return error_kind in handled_kinds


def _analyze_error(error: ErrorEventV1) -> List[Dict[str, Any]]:
    """
    Analyze error and generate suggestions.

    Args:
        error: Error to analyze

    Returns:
        List of suggestion dicts
    """
    suggestions = []

    # TODO: Implement analysis logic
    # Example:
    # - Pattern matching on error message
    # - Lookup in knowledge base
    # - Query similar errors from history

    return suggestions


def _record_suggestions(error_id: str, suggestions: List[Dict[str, Any]]) -> None:
    """
    Record suggestions for later review.

    Args:
        error_id: Error identifier
        suggestions: List of suggestions to record
    """
    # TODO: Implement suggestion recording
    # Could write to:
    # - JSONL log
    # - Database table
    # - Suggestion queue
    pass
