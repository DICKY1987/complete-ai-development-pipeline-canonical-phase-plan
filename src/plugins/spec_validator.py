from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ValidationIssue:
    unit_id: str
    severity: str  # info|warn|error
    message: str


def parse_when_then(text: str) -> Tuple[str, str]:
    # Format: "WHEN <...> THEN <...>"; tolerant of case and spacing.
    s = text.strip()
    up = s.upper()
    if "WHEN " in up and " THEN " in up:
        w = up.index("WHEN ")
        t = up.index(" THEN ")
        when = s[w + 5 : t].strip()
        then = s[t + 6 :].strip()
        return when, then
    # fallback: return as-is if not strictly matched
    return s, ""


def validate(unit_id: str, clauses: List[str]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not clauses:
        issues.append(ValidationIssue(unit_id, "warn", "No WHEN/THEN clauses"))
        return issues
    for raw in clauses:
        when, then = parse_when_then(raw)
        if not when or not then:
            issues.append(ValidationIssue(unit_id, "error", f"Malformed clause: {raw}"))
    return issues

