"""
Build a knowledge graph from repository maps and import graphs.
"""
# DOC_ID: DOC-CORE-KNOWLEDGE-GRAPH-BUILDER-404

from pathlib import Path
from typing import Dict, Optional

from core.ast.repository_mapper import RepositoryMapper
from core.knowledge.knowledge_graph import KnowledgeGraph, NodeRecord, EdgeRecord
from core.knowledge.relationships import RelationshipType


class GraphBuilder:
    """Construct a knowledge graph from AST-derived metadata."""

    def __init__(self, root_path: Path, db_path: Path):
        self.root_path = Path(root_path)
        self.db_path = Path(db_path)

    def build(self, repo_map: Optional[Dict] = None) -> Dict[str, int]:
        """
        Build graph from repository map (or generate one on the fly).

        Returns:
            Dict with counts of nodes and edges written.
        """
        if repo_map is None:
            mapper = RepositoryMapper(self.root_path)
            repo_map = mapper.generate_map()

        return self.build_from_repo_map(repo_map)

    def build_from_repo_map(self, repo_map: Dict) -> Dict[str, int]:
        """
        Build graph from a provided repository map.

        Args:
            repo_map: Output from RepositoryMapper.generate_map()

        Returns:
            Dict with counts of nodes and edges written.
        """
        modules = repo_map.get("modules", {})
        import_edges = repo_map.get("import_graph", {}).get("edges", [])

        node_ids: Dict[str, int] = {}
        edge_count = 0

        with KnowledgeGraph(self.db_path) as graph:
            # Insert module nodes
            for module_name, module_info in modules.items():
                node = NodeRecord(
                    name=module_name,
                    type="module",
                    file=module_info.get("file"),
                    line=None,
                    metadata={"kind": "module"},
                )
                node_ids[module_name] = graph.add_node(node)

            # Insert function and class nodes
            for module_name, module_info in modules.items():
                prefix = f"{module_name}."
                for func in module_info.get("functions", []):
                    func_name = prefix + func.get("name", "")
                    node = NodeRecord(
                        name=func_name,
                        type="function",
                        file=module_info.get("file"),
                        line=None,
                        metadata={"module": module_name, "signature": func},
                    )
                    node_ids[func_name] = graph.add_node(node)

                for cls in module_info.get("classes", []):
                    cls_name = prefix + cls.get("name", "")
                    node = NodeRecord(
                        name=cls_name,
                        type="class",
                        file=module_info.get("file"),
                        line=None,
                        metadata={"module": module_name, "signature": cls},
                    )
                    node_ids[cls_name] = graph.add_node(node)

            # Insert import edges
            for edge in import_edges:
                source_module = edge.get("from")
                target_module = edge.get("to")
                if not source_module or not target_module:
                    continue

                source_id = node_ids.get(source_module)
                target_id = node_ids.get(target_module)
                if source_id and target_id:
                    graph.add_edge(
                        EdgeRecord(
                            source_id=source_id,
                            target_id=target_id,
                            type=RelationshipType.IMPORTS.value,
                            metadata={"names": edge.get("names", [])},
                        )
                    )
                    edge_count += 1

            # Insert inheritance edges where possible
            for module_name, module_info in modules.items():
                prefix = f"{module_name}."
                for cls in module_info.get("classes", []):
                    cls_name = prefix + cls.get("name", "")
                    cls_id = node_ids.get(cls_name)
                    if not cls_id:
                        continue
                    for base in cls.get("bases", []):
                        # Try to resolve to fully-qualified name first
                        base_fq = base if base in node_ids else f"{module_name}.{base}"
                        target_id = node_ids.get(base_fq)
                        if target_id:
                            graph.add_edge(
                                EdgeRecord(
                                    source_id=cls_id,
                                    target_id=target_id,
                                    type=RelationshipType.INHERITS.value,
                                    metadata={"base": base},
                                )
                            )
                            edge_count += 1

        return {"nodes": len(node_ids), "edges": edge_count}


__all__ = ["GraphBuilder"]
