"""
Knowledge graph package.

Provides data structures and builders for semantic code graphs.
"""

# DOC_ID: DOC-CORE-KNOWLEDGE-INIT-401

from .graph_builder import GraphBuilder
from .knowledge_graph import EdgeRecord, KnowledgeGraph, NodeRecord
from .relationships import RelationshipType

__all__ = [
    "KnowledgeGraph",
    "NodeRecord",
    "EdgeRecord",
    "RelationshipType",
    "GraphBuilder",
]
