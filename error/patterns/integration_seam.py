"""Integration Seam Analysis.

Every boundary between modules/services is a potential failure point.
This module identifies integration points and checks for proper
failure handling.

For each integration seam, check:
- Network failure handling
- Timeout handling
- Retry logic
- Circuit breakers
- Data validation at boundary
- Version mismatch handling
"""
DOC_ID: DOC-ERROR-PATTERNS-INTEGRATION-SEAM-050
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .types import (
    IntegrationSeam,
    PatternCategory,
    PatternFinding,
    PatternSeverity,
)


# Integration seam detection patterns
SEAM_PATTERNS = {
    "api": {
        "markers": ["requests", "httpx", "aiohttp", "urllib", "http.client"],
        "required_checks": [
            "network_failure_handling",
            "timeout_handling",
            "retry_logic",
            "data_validation",
        ],
    },
    "database": {
        "markers": ["sqlite3", "psycopg2", "mysql", "sqlalchemy", "pymongo", "redis"],
        "required_checks": [
            "network_failure_handling",
            "timeout_handling",
            "retry_logic",
            "data_validation",
        ],
    },
    "file": {
        "markers": ["open", "Path", "shutil", "os.path"],
        "required_checks": [
            "network_failure_handling",  # For network files
            "data_validation",
        ],
    },
    "external_service": {
        "markers": ["boto3", "google.cloud", "azure", "twilio", "stripe"],
        "required_checks": [
            "network_failure_handling",
            "timeout_handling",
            "retry_logic",
            "circuit_breaker",
            "data_validation",
        ],
    },
    "message_queue": {
        "markers": ["pika", "kafka", "celery", "kombu", "aiokafka"],
        "required_checks": [
            "network_failure_handling",
            "timeout_handling",
            "retry_logic",
            "data_validation",
        ],
    },
}

# Patterns indicating specific failure handling
HANDLING_PATTERNS = {
    "network_failure_handling": [
        r"ConnectionError",
        r"NetworkError",
        r"ConnectionRefusedError",
        r"socket\.error",
        r"requests\.exceptions\.",
        r"httpx\..*Error",
    ],
    "timeout_handling": [
        r"TimeoutError",
        r"Timeout",
        r"timeout=",
        r"read_timeout",
        r"connect_timeout",
        r"socket\.timeout",
    ],
    "retry_logic": [
        r"@retry",
        r"retries=",
        r"max_retries",
        r"retry_count",
        r"tenacity",
        r"backoff",
        r"for .* in range.*:.*try:",
        r"while.*try:",
    ],
    "circuit_breaker": [
        r"circuit_?breaker",
        r"CircuitBreaker",
        r"@circuit",
        r"pybreaker",
        r"is_?open",
        r"half_?open",
    ],
    "data_validation": [
        r"\.validate\(",
        r"pydantic",
        r"marshmallow",
        r"jsonschema",
        r"isinstance\(",
        r"assert\s+",
        r"Schema\(",
        r"validator",
    ],
    "version_mismatch_handling": [
        r"version",
        r"api_version",
        r"schema_version",
        r"compatibility",
        r"deprecated",
    ],
}

# Pre-compile regex patterns for efficiency
_COMPILED_HANDLING_PATTERNS: Dict[str, List[re.Pattern]] = {}


def _get_compiled_patterns() -> Dict[str, List[re.Pattern]]:
    """Get compiled regex patterns (cached for efficiency).
    
    Compiles patterns once on first call for better performance
    when checking multiple files or seams.
    """
    global _COMPILED_HANDLING_PATTERNS
    if not _COMPILED_HANDLING_PATTERNS:
        for check_name, patterns in HANDLING_PATTERNS.items():
            _COMPILED_HANDLING_PATTERNS[check_name] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ]
    return _COMPILED_HANDLING_PATTERNS


def identify_integration_seams(file_path: Path) -> List[IntegrationSeam]:
    """Identify integration points in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of identified integration seams
    """
    seams: List[IntegrationSeam] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return seams
    
    # Check imports to determine what integrations exist
    imports = _extract_imports(tree)
    
    # Identify seams based on imports and code patterns
    for seam_type, config in SEAM_PATTERNS.items():
        for marker in config["markers"]:
            if any(marker in imp for imp in imports):
                seam = IntegrationSeam(
                    name=f"{seam_type}_{marker}",
                    seam_type=seam_type,
                    location=str(file_path),
                    checks={},
                )
                
                # Check what handling exists
                for check_name in config["required_checks"]:
                    has_handling = _check_handling_exists(source, check_name)
                    seam.checks[check_name] = has_handling
                
                seams.append(seam)
                break  # One seam per type per file
    
    return seams


def _extract_imports(tree: ast.Module) -> Set[str]:
    """Extract all import names from an AST."""
    imports: Set[str] = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
                for alias in node.names:
                    imports.add(f"{node.module}.{alias.name}")
    
    return imports


def _check_handling_exists(source: str, check_name: str) -> bool:
    """Check if a specific type of handling exists in the source.
    
    Uses pre-compiled patterns for efficiency when checking multiple files.
    """
    compiled = _get_compiled_patterns()
    patterns = compiled.get(check_name, [])
    
    for pattern in patterns:
        if pattern.search(source):
            return True
    
    return False


def analyze_integration_seams(file_path: Path) -> List[PatternFinding]:
    """Analyze integration seams for missing failure handling.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of findings about missing integration handling
    """
    findings: List[PatternFinding] = []
    seams = identify_integration_seams(file_path)
    
    for seam in seams:
        missing = seam.missing_checks
        
        for check in missing:
            severity = _get_severity_for_seam_check(check, seam.seam_type)
            
            findings.append(PatternFinding(
                pattern_category=PatternCategory.INTEGRATION_SEAM,
                severity=severity,
                file_path=str(file_path),
                code=f"ISA-{_get_code_for_seam_check(check)}",
                message=f"Missing {check} for {seam.seam_type} integration '{seam.name}'",
                suggested_fix=_get_seam_fix_suggestion(check, seam.seam_type),
                context={
                    "seam_name": seam.name,
                    "seam_type": seam.seam_type,
                    "check": check,
                    "existing_checks": {k: v for k, v in seam.checks.items() if v},
                },
            ))
    
    return findings


def _get_severity_for_seam_check(check: str, seam_type: str) -> PatternSeverity:
    """Determine severity for a missing seam check."""
    # External services need more robust handling
    if seam_type == "external_service":
        if check in ["circuit_breaker", "retry_logic"]:
            return PatternSeverity.CRITICAL
    
    severity_map = {
        "network_failure_handling": PatternSeverity.CRITICAL,
        "timeout_handling": PatternSeverity.MAJOR,
        "retry_logic": PatternSeverity.MAJOR,
        "circuit_breaker": PatternSeverity.MAJOR,
        "data_validation": PatternSeverity.MAJOR,
        "version_mismatch_handling": PatternSeverity.MINOR,
    }
    return severity_map.get(check, PatternSeverity.MINOR)


def _get_code_for_seam_check(check: str) -> str:
    """Get pattern code for a seam check."""
    code_map = {
        "network_failure_handling": "001",
        "timeout_handling": "002",
        "retry_logic": "003",
        "circuit_breaker": "004",
        "data_validation": "005",
        "version_mismatch_handling": "006",
    }
    return code_map.get(check, "000")


def _get_seam_fix_suggestion(check: str, seam_type: str) -> str:
    """Get fix suggestion for a missing seam check."""
    suggestions = {
        "network_failure_handling": f"""
Add try/except blocks to catch network-related exceptions:
```python
try:
    response = client.call()
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Network error: {{e}}")
    return fallback_value
```
""",
        "timeout_handling": f"""
Add timeout configuration to {seam_type} calls:
```python
response = client.request(timeout=30)  # Set appropriate timeout
```
""",
        "retry_logic": f"""
Add retry logic for transient failures:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def make_request():
    return client.call()
```
""",
        "circuit_breaker": f"""
Add circuit breaker for {seam_type} integration:
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

@breaker
def make_external_call():
    return external_service.call()
```
""",
        "data_validation": f"""
Add data validation at the integration boundary:
```python
from pydantic import BaseModel, ValidationError

class ResponseModel(BaseModel):
    field1: str
    field2: int

try:
    validated = ResponseModel(**response_data)
except ValidationError as e:
    logger.error(f"Invalid response: {{e}}")
    raise
```
""",
        "version_mismatch_handling": f"""
Add version checking for {seam_type} integration:
```python
API_VERSION = "v2"
if response.get("api_version") != API_VERSION:
    logger.warning("API version mismatch")
```
""",
    }
    return suggestions.get(check, f"Add {check} handling for {seam_type} integration")


def generate_seam_matrix(seams: List[IntegrationSeam]) -> Dict[str, Dict[str, bool]]:
    """Generate a matrix of seams vs checks for reporting.
    
    Args:
        seams: List of identified integration seams
        
    Returns:
        Dict[seam_name][check_name] = is_implemented
    """
    matrix: Dict[str, Dict[str, bool]] = {}
    
    for seam in seams:
        matrix[seam.name] = seam.checks.copy()
    
    return matrix


def scan_file_for_integration_issues(file_path: Path) -> List[PatternFinding]:
    """Scan a file for integration seam issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of integration-related findings
    """
    return analyze_integration_seams(file_path)
