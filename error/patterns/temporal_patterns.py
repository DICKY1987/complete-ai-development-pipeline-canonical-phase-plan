"""Temporal Bug Patterns.

Time-based bugs are often missed in testing. This module checks
for temporal issues that can cause failures.

Temporal test patterns:
- What happens at midnight?
- What happens across DST boundaries?
- What happens on Feb 29?
- What happens on Dec 31→Jan 1?
- What happens with concurrent requests?
- What happens when X runs while Y is mid-execution?
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
    TemporalPattern,
)


# Temporal vulnerability patterns
TEMPORAL_PATTERNS = {
    "midnight_boundary": {
        "description": "Operations that may fail at midnight",
        "patterns": [
            r"\.today\(\)",
            r"date\.today\(\)",
            r"datetime\.now\(\)\.date\(\)",
        ],
        "severity": PatternSeverity.MINOR,
        "affected_times": ["23:59:59 → 00:00:00"],
    },
    "timezone_naive": {
        "description": "Datetime operations without timezone awareness",
        "patterns": [
            r"datetime\.now\(\)(?!\.astimezone)",
            r"datetime\.utcnow\(\)",  # Deprecated in Python 3.12+
            r"datetime\(.*\)(?!.*tzinfo)",
        ],
        "severity": PatternSeverity.MAJOR,
        "affected_times": ["Any timezone boundary"],
    },
    "dst_boundary": {
        "description": "Operations that may fail during DST transitions",
        "patterns": [
            r"timedelta\(.*hours=1\)",
            r"\.hour\s*[+\-]=?\s*1",
            r"\.replace\(hour=",
        ],
        "severity": PatternSeverity.MINOR,
        "affected_times": ["DST start/end (usually 2am)"],
    },
    "year_boundary": {
        "description": "Operations that may fail at year boundaries",
        "patterns": [
            r"\.year\b",
            r"strftime.*%Y",
            r"year\s*=\s*\d{4}",
        ],
        "severity": PatternSeverity.MINOR,
        "affected_times": ["Dec 31 → Jan 1"],
    },
    "leap_year": {
        "description": "Operations that may fail on Feb 29",
        "patterns": [
            r"month\s*==?\s*2",
            r"february",
            r"\.day\s*==?\s*29",
            r"strftime.*%d.*%m",
        ],
        "severity": PatternSeverity.MINOR,
        "affected_times": ["Feb 29 (leap years)"],
    },
    "time_comparison": {
        "description": "Time comparisons that may have race conditions",
        "patterns": [
            r"datetime\.now\(\)\s*[<>=]+",
            r"time\.time\(\)\s*[<>=]+",
            r"if\s+.*_time\s*[<>=]+",
        ],
        "severity": PatternSeverity.MAJOR,
        "affected_times": ["Concurrent execution"],
    },
    "stale_timestamp": {
        "description": "Timestamps stored and used later may be stale",
        "patterns": [
            r"_timestamp\s*=\s*.*now\(\)",
            r"created_at\s*=\s*.*now\(\)",
            r"last_.*\s*=\s*.*time\(\)",
        ],
        "severity": PatternSeverity.MINOR,
        "affected_times": ["Long-running operations"],
    },
    "timeout_race": {
        "description": "Timeout calculations with race conditions",
        "patterns": [
            r"timeout\s*=\s*.*-\s*.*now\(\)",
            r"remaining\s*=\s*deadline\s*-",
            r"time_left\s*=",
        ],
        "severity": PatternSeverity.MAJOR,
        "affected_times": ["Near-timeout conditions"],
    },
}

# Safe patterns that mitigate temporal issues
SAFE_PATTERNS = {
    "timezone_aware": [
        r"tzinfo",
        r"timezone",
        r"pytz",
        r"zoneinfo",
        r"\.astimezone\(",
        r"datetime\.now\(tz=",
    ],
    "atomic_time": [
        r"monotonic\(\)",
        r"perf_counter\(\)",
        r"time_ns\(\)",
    ],
    "time_mock": [
        r"@freeze_time",
        r"freezegun",
        r"mock.*time",
        r"patch.*datetime",
    ],
}


def analyze_temporal_patterns(file_path: Path) -> List[PatternFinding]:
    """Analyze a file for temporal bug patterns.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of findings about temporal issues
    """
    findings: List[PatternFinding] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError:
        return findings
    
    lines = source.split("\n")
    
    # Check if file has safe patterns that mitigate issues
    has_safe_patterns = _check_safe_patterns(source)
    
    for pattern_name, config in TEMPORAL_PATTERNS.items():
        for pattern in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip if safe patterns exist
                    if _is_mitigated(pattern_name, has_safe_patterns):
                        continue
                    
                    findings.append(PatternFinding(
                        pattern_category=PatternCategory.TEMPORAL,
                        severity=config["severity"],
                        file_path=str(file_path),
                        line=i,
                        code=f"TMP-{_get_temporal_code(pattern_name)}",
                        message=f"Potential temporal issue: {config['description']}",
                        suggested_fix=_get_temporal_fix(pattern_name),
                        context={
                            "pattern_name": pattern_name,
                            "affected_times": config["affected_times"],
                            "matched_pattern": pattern,
                        },
                    ))
    
    return findings


def _check_safe_patterns(source: str) -> Dict[str, bool]:
    """Check which safe patterns exist in the source."""
    results = {}
    
    for safe_name, patterns in SAFE_PATTERNS.items():
        results[safe_name] = any(
            re.search(p, source, re.IGNORECASE) for p in patterns
        )
    
    return results


def _is_mitigated(pattern_name: str, safe_patterns: Dict[str, bool]) -> bool:
    """Check if a temporal pattern is mitigated by safe patterns."""
    mitigation_map = {
        "timezone_naive": "timezone_aware",
        "time_comparison": "atomic_time",
        "timeout_race": "atomic_time",
    }
    
    safe_name = mitigation_map.get(pattern_name)
    if safe_name and safe_patterns.get(safe_name):
        return True
    
    return False


def _get_temporal_code(pattern_name: str) -> str:
    """Get code for temporal pattern type."""
    codes = {
        "midnight_boundary": "001",
        "timezone_naive": "002",
        "dst_boundary": "003",
        "year_boundary": "004",
        "leap_year": "005",
        "time_comparison": "006",
        "stale_timestamp": "007",
        "timeout_race": "008",
    }
    return codes.get(pattern_name, "000")


def _get_temporal_fix(pattern_name: str) -> str:
    """Get fix suggestion for temporal pattern."""
    fixes = {
        "midnight_boundary": """
Use datetime with explicit time handling:
```python
from datetime import datetime, time

# Instead of .today()
start_of_day = datetime.combine(date.today(), time.min)
end_of_day = datetime.combine(date.today(), time.max)
```
""",
        "timezone_naive": """
Always use timezone-aware datetimes:
```python
from datetime import datetime, timezone
# Or: from zoneinfo import ZoneInfo

# Instead of datetime.now()
now = datetime.now(timezone.utc)

# Or with local timezone
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("America/New_York"))
```
""",
        "dst_boundary": """
Use timezone-aware arithmetic:
```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

tz = ZoneInfo("America/New_York")
now = datetime.now(tz)

# Convert to UTC for arithmetic, then back
utc_time = now.astimezone(timezone.utc)
new_time = utc_time + timedelta(hours=1)
local_time = new_time.astimezone(tz)
```
""",
        "year_boundary": """
Handle year transitions explicitly:
```python
from datetime import date

today = date.today()
if today.month == 12 and today.day == 31:
    # Handle year boundary
    next_day = date(today.year + 1, 1, 1)
```
""",
        "leap_year": """
Use calendar module for leap year handling:
```python
import calendar

year = 2024
if calendar.isleap(year):
    feb_days = 29
else:
    feb_days = 28

# Or use try/except for date creation
from datetime import date
try:
    d = date(year, 2, 29)
except ValueError:
    d = date(year, 2, 28)
```
""",
        "time_comparison": """
Use monotonic time for comparisons:
```python
import time

# For duration measurement
start = time.monotonic()
# ... work ...
elapsed = time.monotonic() - start

# For timeouts
deadline = time.monotonic() + timeout
while time.monotonic() < deadline:
    # ... work ...
```
""",
        "stale_timestamp": """
Refresh timestamps when needed:
```python
from datetime import datetime, timezone

def get_current_time():
    return datetime.now(timezone.utc)

# Refresh before comparison
current = get_current_time()
if stored_time < current - timedelta(hours=1):
    # Handle stale data
```
""",
        "timeout_race": """
Use monotonic time for timeout calculations:
```python
import time

deadline = time.monotonic() + timeout_seconds
while True:
    remaining = max(0, deadline - time.monotonic())
    if remaining == 0:
        raise TimeoutError()
    # Wait with remaining time
    result = wait_with_timeout(remaining)
```
""",
    }
    return fixes.get(pattern_name, f"Review temporal handling for {pattern_name}")


def identify_temporal_patterns(file_path: Path) -> List[TemporalPattern]:
    """Identify temporal patterns in a file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of identified temporal patterns
    """
    patterns: List[TemporalPattern] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
    except OSError:
        return patterns
    
    lines = source.split("\n")
    
    for pattern_name, config in TEMPORAL_PATTERNS.items():
        for regex in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(regex, line, re.IGNORECASE):
                    patterns.append(TemporalPattern(
                        pattern_type=pattern_name,
                        file_path=str(file_path),
                        line=i,
                        issue_description=config["description"],
                        affected_dates=config["affected_times"],
                    ))
    
    return patterns


def generate_temporal_test_cases(pattern: TemporalPattern) -> List[str]:
    """Generate test cases for a temporal pattern.
    
    Args:
        pattern: The temporal pattern to generate tests for
        
    Returns:
        List of test case code snippets
    """
    test_templates = {
        "midnight_boundary": [
            """
@freeze_time("2024-01-15 23:59:59")
def test_just_before_midnight():
    result = function_under_test()
    # Verify behavior
    
@freeze_time("2024-01-16 00:00:00")
def test_at_midnight():
    result = function_under_test()
    # Verify same behavior
""",
        ],
        "timezone_naive": [
            """
@freeze_time("2024-06-15 12:00:00", tz_offset=0)
def test_utc_time():
    result = function_under_test()
    # Verify

@freeze_time("2024-06-15 12:00:00", tz_offset=-5)
def test_eastern_time():
    result = function_under_test()
    # Should produce same result
""",
        ],
        "dst_boundary": [
            """
@freeze_time("2024-03-10 01:59:59", tz_offset=-5)  # Before DST
def test_before_dst_start():
    result = function_under_test()

@freeze_time("2024-03-10 03:00:00", tz_offset=-4)  # After DST
def test_after_dst_start():
    result = function_under_test()
""",
        ],
        "leap_year": [
            """
@freeze_time("2024-02-28")
def test_feb_28_leap_year():
    result = function_under_test()

@freeze_time("2024-02-29")
def test_feb_29_leap_year():
    result = function_under_test()

@freeze_time("2023-02-28")
def test_feb_28_non_leap_year():
    result = function_under_test()
""",
        ],
        "year_boundary": [
            """
@freeze_time("2024-12-31 23:59:59")
def test_last_second_of_year():
    result = function_under_test()

@freeze_time("2025-01-01 00:00:00")
def test_first_second_of_year():
    result = function_under_test()
""",
        ],
    }
    
    return test_templates.get(pattern.pattern_type, [])


def scan_file_for_temporal_issues(file_path: Path) -> List[PatternFinding]:
    """Scan a file for temporal bug issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of temporal-related findings
    """
    return analyze_temporal_patterns(file_path)
