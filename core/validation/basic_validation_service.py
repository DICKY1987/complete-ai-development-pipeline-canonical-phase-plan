# DOC_LINK: DOC-CORE-VALIDATION-BASIC-VALIDATION-SERVICE-113
from __future__ import annotations
from typing import Any

class BasicValidationService:
    def validate(self, data: dict[str, Any], schema: str) -> list[str]:
        errors = []
        if schema == 'workstream':
            errors.extend(self.validate_workstream(data))
        return errors
    
    def validate_workstream(self, ws: dict[str, Any]) -> list[str]:
        errors = []
        if 'id' not in ws:
            errors.append("Missing required field: id")
        if 'status' not in ws:
            errors.append("Missing required field: status")
        return errors
