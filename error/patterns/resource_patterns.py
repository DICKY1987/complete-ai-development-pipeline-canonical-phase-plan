"""Resource Exhaustion Patterns.

Systematically check for resource management issues that can
lead to exhaustion, leaks, or system instability.

Resource leak patterns:
- Unclosed file handles
- Database connections not released
- Memory allocations without cleanup
- Thread/process spawning without limits
- Infinite loops or recursion without bounds
- Cache growth without eviction
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .types import (
    PatternCategory,
    PatternFinding,
    PatternSeverity,
    ResourcePattern,
)


# Resource acquisition patterns that need cleanup
RESOURCE_ACQUIRE_PATTERNS = {
    "file": {
        "acquire": ["open(", "Path("],
        "release": [".close()", "with "],
        "context_manager": True,
    },
    "connection": {
        "acquire": [
            "connect(", 
            "create_connection(", 
            "get_connection(",
            "create_engine(",
            "Connection(",
        ],
        "release": [".close()", ".dispose()", "with "],
        "context_manager": True,
    },
    "cursor": {
        "acquire": [".cursor()", "create_cursor("],
        "release": [".close()", "with "],
        "context_manager": True,
    },
    "lock": {
        "acquire": [".acquire()", "Lock()", "RLock()", "Semaphore("],
        "release": [".release()", "with "],
        "context_manager": True,
    },
    "thread": {
        "acquire": ["Thread(", "threading.Thread("],
        "release": [".join()", "daemon=True"],
        "context_manager": False,
    },
    "process": {
        "acquire": ["Process(", "subprocess.Popen("],
        "release": [".wait()", ".kill()", ".terminate()", "with "],
        "context_manager": True,
    },
    "socket": {
        "acquire": ["socket(", "socket.socket("],
        "release": [".close()", "with "],
        "context_manager": True,
    },
    "tempfile": {
        "acquire": ["TemporaryFile(", "NamedTemporaryFile(", "TemporaryDirectory("],
        "release": [".cleanup()", "with "],
        "context_manager": True,
    },
}

# Unbounded resource patterns
UNBOUNDED_PATTERNS = {
    "infinite_loop": {
        "patterns": [
            r"while\s+True\s*:",
            r"while\s+1\s*:",
            r"for\s+\w+\s+in\s+iter\s*\(\s*\w+\s*,\s*None\s*\)",
        ],
        "safe_exits": ["break", "return", "raise", "sys.exit"],
    },
    "unbounded_recursion": {
        "patterns": [
            # Recursive call without base case (heuristic)
        ],
        "safe_exits": ["if", "return"],
    },
    "unbounded_cache": {
        "patterns": [
            r"@cache\b",
            r"@lru_cache\s*\(\s*\)",
            r"@lru_cache\s*\(\s*maxsize\s*=\s*None\s*\)",
            r"_cache\s*=\s*\{\}",
            r"_cache\s*=\s*dict\(\)",
        ],
        "safe_exits": ["maxsize=", "TTLCache", "Cache(maxsize"],
    },
    "unbounded_collection": {
        "patterns": [
            r"\.append\(",
            r"\.add\(",
            r"\.extend\(",
        ],
        "safe_exits": ["max_size", "limit", "[:limit]", "deque(maxlen"],
    },
}


def analyze_resource_patterns(file_path: Path) -> List[PatternFinding]:
    """Analyze a file for resource management issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of findings about resource issues
    """
    findings: List[PatternFinding] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return findings
    
    # Check for resource leaks
    findings.extend(_check_resource_leaks(tree, source, str(file_path)))
    
    # Check for unbounded patterns
    findings.extend(_check_unbounded_patterns(source, str(file_path)))
    
    return findings


def _check_resource_leaks(
    tree: ast.Module,
    source: str,
    file_path: str,
) -> List[PatternFinding]:
    """Check for potential resource leaks."""
    findings: List[PatternFinding] = []
    lines = source.split("\n")
    
    for resource_type, config in RESOURCE_ACQUIRE_PATTERNS.items():
        for acquire_pattern in config["acquire"]:
            for i, line in enumerate(lines, 1):
                if acquire_pattern in line:
                    # Check if it's in a with statement
                    in_with = _is_in_with_statement(lines, i)
                    
                    # Check if corresponding release exists nearby
                    has_release = _has_release_nearby(lines, i, config["release"])
                    
                    if not in_with and not has_release:
                        findings.append(PatternFinding(
                            pattern_category=PatternCategory.RESOURCE_EXHAUSTION,
                            severity=PatternSeverity.MAJOR,
                            file_path=file_path,
                            line=i,
                            code=f"RES-001",
                            message=f"Potential {resource_type} leak: '{acquire_pattern}' without proper cleanup",
                            suggested_fix=_get_resource_fix(resource_type, config),
                            context={
                                "resource_type": resource_type,
                                "pattern": acquire_pattern,
                            },
                        ))
    
    return findings


def _is_in_with_statement(lines: List[str], line_num: int) -> bool:
    """Check if a line is inside a with statement."""
    # Simple heuristic: check if the line or previous lines start with 'with'
    for i in range(max(0, line_num - 5), line_num):
        if lines[i].strip().startswith("with "):
            # Check indentation
            return True
    return False


def _has_release_nearby(lines: List[str], line_num: int, release_patterns: List[str]) -> bool:
    """Check if a release pattern exists near the acquire."""
    # Look within 20 lines for a release
    search_range = lines[line_num:min(len(lines), line_num + 20)]
    
    for line in search_range:
        for pattern in release_patterns:
            if pattern in line:
                return True
    
    return False


def _get_resource_fix(resource_type: str, config: Dict[str, Any]) -> str:
    """Get fix suggestion for a resource leak."""
    if config.get("context_manager"):
        return f"""
Use a context manager to ensure {resource_type} cleanup:
```python
with resource as r:
    # Use resource
    ...
# Resource automatically cleaned up
```
"""
    else:
        release = config["release"][0] if config["release"] else ".close()"
        return f"""
Ensure {resource_type} is properly released:
```python
resource = acquire_{resource_type}()
try:
    # Use resource
    ...
finally:
    resource{release}
```
"""


def _check_unbounded_patterns(source: str, file_path: str) -> List[PatternFinding]:
    """Check for unbounded resource patterns."""
    findings: List[PatternFinding] = []
    lines = source.split("\n")
    
    for pattern_name, config in UNBOUNDED_PATTERNS.items():
        for pattern in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Check if safe exits exist
                    has_safe = _has_safe_exit(lines, i, config["safe_exits"])
                    
                    if not has_safe:
                        severity = PatternSeverity.MAJOR
                        if pattern_name == "infinite_loop":
                            severity = PatternSeverity.CRITICAL
                        
                        findings.append(PatternFinding(
                            pattern_category=PatternCategory.RESOURCE_EXHAUSTION,
                            severity=severity,
                            file_path=file_path,
                            line=i,
                            code=f"RES-{_get_unbounded_code(pattern_name)}",
                            message=f"Potentially unbounded {pattern_name.replace('_', ' ')}",
                            suggested_fix=_get_unbounded_fix(pattern_name),
                            context={
                                "pattern_name": pattern_name,
                                "matched": pattern,
                            },
                        ))
    
    return findings


def _has_safe_exit(lines: List[str], line_num: int, safe_patterns: List[str]) -> bool:
    """Check if safe exit patterns exist in the context."""
    # Look in the next 30 lines for safe exits
    search_range = lines[line_num:min(len(lines), line_num + 30)]
    
    for line in search_range:
        for pattern in safe_patterns:
            if pattern in line:
                return True
    
    return False


def _get_unbounded_code(pattern_name: str) -> str:
    """Get code for unbounded pattern type."""
    codes = {
        "infinite_loop": "002",
        "unbounded_recursion": "003",
        "unbounded_cache": "004",
        "unbounded_collection": "005",
    }
    return codes.get(pattern_name, "000")


def _get_unbounded_fix(pattern_name: str) -> str:
    """Get fix suggestion for unbounded pattern."""
    fixes = {
        "infinite_loop": """
Add a termination condition or maximum iterations:
```python
max_iterations = 1000
for i in range(max_iterations):
    if condition_met():
        break
    # Process...
else:
    raise RuntimeError("Max iterations exceeded")
```
""",
        "unbounded_recursion": """
Add a depth limit or convert to iteration:
```python
def recursive_func(data, depth=0, max_depth=100):
    if depth >= max_depth:
        raise RecursionError("Max depth exceeded")
    if base_case(data):
        return result
    return recursive_func(process(data), depth + 1)
```
""",
        "unbounded_cache": """
Add a size limit to the cache:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)  # Set appropriate limit
def cached_function(arg):
    return expensive_computation(arg)
```
""",
        "unbounded_collection": """
Add size limits to growing collections:
```python
from collections import deque

# Use deque with maxlen for bounded collections
items = deque(maxlen=1000)
items.append(new_item)  # Automatically removes oldest

# Or manually limit
if len(items) < MAX_SIZE:
    items.append(new_item)
```
""",
    }
    return fixes.get(pattern_name, f"Add bounds to {pattern_name}")


def identify_resource_patterns(file_path: Path) -> List[ResourcePattern]:
    """Identify resource usage patterns in a file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of identified resource patterns
    """
    patterns: List[ResourcePattern] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
    except (OSError, SyntaxError):
        return patterns
    
    lines = source.split("\n")
    
    for resource_type, config in RESOURCE_ACQUIRE_PATTERNS.items():
        for acquire_pattern in config["acquire"]:
            for i, line in enumerate(lines, 1):
                if acquire_pattern in line:
                    in_with = _is_in_with_statement(lines, i)
                    has_release = _has_release_nearby(lines, i, config["release"])
                    
                    patterns.append(ResourcePattern(
                        resource_type=resource_type,
                        pattern_name=acquire_pattern,
                        file_path=str(file_path),
                        line=i,
                        is_leak=not (in_with or has_release),
                        context=line.strip(),
                    ))
    
    return patterns


def scan_file_for_resource_issues(file_path: Path) -> List[PatternFinding]:
    """Scan a file for resource exhaustion issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of resource-related findings
    """
    return analyze_resource_patterns(file_path)
