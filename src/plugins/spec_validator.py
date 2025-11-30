# DOC_LINK: DOC-PAT-PLUGINS-SPEC-VALIDATOR-617
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class Issue:
    severity: str
    message: str
    unit_id: str | None = None


def parse_when_then(text: str) -> Tuple[str, str]:
    match = re.match(r"\s*WHEN\s+(.*?)\s+THEN\s+(.*)", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid WHEN/THEN clause: {text}")
    return match.group(1).strip(), match.group(2).strip()


def validate(unit_id: str, when_then_clauses: Iterable[str]) -> List[Issue]:
    issues: List[Issue] = []
    for clause in when_then_clauses:
        try:
            parse_when_then(clause)
        except ValueError as exc:
            issues.append(Issue(severity="error", message=str(exc), unit_id=unit_id))
    return issues


__all__ = ["parse_when_then", "validate", "Issue"]
