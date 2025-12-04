"""
Knowledge graph package.

Provides data structures and builders for semantic code graphs.
"""
# DOC_ID: DOC-CORE-KNOWLEDGE-INIT-401

from .knowledge_graph import KnowledgeGraph, NodeRecord, EdgeRecord
from .relationships import RelationshipType
from .graph_builder import GraphBuilder

__all__ = [
    "KnowledgeGraph",
    "NodeRecord",
    "EdgeRecord",
    "RelationshipType",
    "GraphBuilder",
]
