"""
Relationship types for knowledge graph edges.
"""

# DOC_ID: DOC-CORE-KNOWLEDGE-RELATIONSHIPS-402

from enum import Enum


class RelationshipType(str, Enum):
    """Supported edge relationship types."""

    CALLS = "calls"
    IMPORTS = "imports"
    INHERITS = "inherits"
    MODIFIES = "modifies"
    USES = "uses"

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Check if value is a valid relationship type."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


__all__ = ["RelationshipType"]
