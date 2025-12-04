"""
GraphRAG query engine over the knowledge graph.
"""

# DOC_ID: DOC-CORE-KNOWLEDGE-QUERY-405

from typing import Dict, List

from core.knowledge.knowledge_graph import KnowledgeGraph
from core.knowledge.relationships import RelationshipType


class QueryEngine:
    """Lightweight query engine for impact analysis."""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def callers_of(self, module_or_symbol: str) -> List[Dict]:
        """Return modules that import the given module/symbol."""
        edges = self.graph.get_edges(RelationshipType.IMPORTS.value)
        nodes = {row["id"]: row for row in self.graph.get_nodes()}
        results = []
        for edge in edges:
            target = nodes.get(edge["target_id"])
            source = nodes.get(edge["source_id"])
            if target and target["name"] == module_or_symbol and source:
                results.append({"caller": source["name"], "target": target["name"]})
        return results

    def dependents_chain(self, module: str, depth: int = 3) -> List[str]:
        """Return dependency chain up to depth using import edges."""
        reverse_edges = self._build_reverse_imports()
        visited = set()
        result = []

        def dfs(current: str, d: int):
            if d > depth or current in visited:
                return
            visited.add(current)
            result.append(current)
            for dep in reverse_edges.get(current, []):
                dfs(dep, d + 1)

        dfs(module, 0)
        return result

    def usages_of(self, symbol_prefix: str) -> List[str]:
        """Return all nodes whose name starts with symbol_prefix."""
        return [
            row["name"]
            for row in self.graph.get_nodes()
            if row["name"].startswith(symbol_prefix)
        ]

    def _build_reverse_imports(self) -> Dict[str, List[str]]:
        reverse_map: Dict[str, List[str]] = {}
        edges = self.graph.get_edges(RelationshipType.IMPORTS.value)
        nodes = {row["id"]: row for row in self.graph.get_nodes()}
        for edge in edges:
            src = nodes.get(edge["source_id"])
            tgt = nodes.get(edge["target_id"])
            if not src or not tgt:
                continue
            reverse_map.setdefault(tgt["name"], []).append(src["name"])
        return reverse_map


__all__ = ["QueryEngine"]
