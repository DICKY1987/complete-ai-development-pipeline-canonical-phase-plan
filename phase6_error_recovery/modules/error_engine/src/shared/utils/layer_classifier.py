"""5-Layer Error Classification Utility

Maps error categories to infrastructure layers for better prioritization.
Based on 5-Layer Test Coverage Framework.
"""

# DOC_ID: DOC-ERROR-UTILS-LAYER-CLASSIFIER-001

from typing import Dict

# Category to layer mapping
CATEGORY_TO_LAYER: Dict[str, str] = {
    # Layer 1 - Infrastructure
    "file_not_found": "Layer 1 - Infrastructure",
    "resource_exhausted": "Layer 1 - Infrastructure",
    "disk_full": "Layer 1 - Infrastructure",
    # Layer 2 - Dependencies
    "import_error": "Layer 2 - Dependencies",
    "module_not_found": "Layer 2 - Dependencies",
    "version_mismatch": "Layer 2 - Dependencies",
    "dependency_error": "Layer 2 - Dependencies",
    # Layer 3 - Configuration
    "schema_invalid": "Layer 3 - Configuration",
    "config_error": "Layer 3 - Configuration",
    "validation_failed": "Layer 3 - Configuration",
    # Layer 4 - Operational
    "permission_denied": "Layer 4 - Operational",
    "timeout": "Layer 4 - Operational",
    "network_error": "Layer 4 - Operational",
    "test_failure": "Layer 4 - Operational",
    # Layer 5 - Business Logic
    "syntax": "Layer 5 - Business Logic",
    "type": "Layer 5 - Business Logic",
    "style": "Layer 5 - Business Logic",
    "formatting": "Layer 5 - Business Logic",
    "security": "Layer 5 - Business Logic",
    "logic_error": "Layer 5 - Business Logic",
}

# Severity to priority mapping (lower = higher priority)
LAYER_PRIORITY: Dict[str, int] = {
    "Layer 1 - Infrastructure": 1,  # Blocks everything
    "Layer 2 - Dependencies": 2,  # Blocks execution
    "Layer 3 - Configuration": 3,  # Causes runtime errors
    "Layer 4 - Operational": 4,  # Intermittent failures
    "Layer 5 - Business Logic": 5,  # Code quality issues
}


def classify_error_layer(category: str) -> str:
    """
    Classify error category into infrastructure layer.

    Args:
        category: Error category (e.g., "syntax", "import_error")

    Returns:
        Layer classification (e.g., "Layer 5 - Business Logic")
        Defaults to Layer 5 if category unknown.
    """
    return CATEGORY_TO_LAYER.get(category, "Layer 5 - Business Logic")


def get_layer_priority(layer: str) -> int:
    """
    Get priority for a layer (lower = higher priority).

    Args:
        layer: Layer classification

    Returns:
        Priority value (1-5)
    """
    return LAYER_PRIORITY.get(layer, 5)


def is_auto_repairable(category: str, has_fix_method: bool = False) -> bool:
    """
    Determine if an error category is typically auto-repairable.

    Args:
        category: Error category
        has_fix_method: Whether plugin has a fix() method

    Returns:
        True if auto-repairable
    """
    # Layer 5 (code quality) is usually auto-repairable if plugin supports it
    layer = classify_error_layer(category)
    if layer == "Layer 5 - Business Logic" and has_fix_method:
        return True

    # Layer 3 (config) sometimes auto-repairable
    if layer == "Layer 3 - Configuration" and category in ["schema_invalid"]:
        return True

    # Layer 1, 2, 4 typically require human intervention
    return False
