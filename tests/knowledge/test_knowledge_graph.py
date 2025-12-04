import sqlite3
from pathlib import Path

from core.knowledge.graph_builder import GraphBuilder
from core.knowledge.knowledge_graph import EdgeRecord, KnowledgeGraph, NodeRecord
from core.knowledge.relationships import RelationshipType


def test_add_node_and_edge(tmp_path):
    db_path = tmp_path / "kg.db"
    with KnowledgeGraph(db_path) as graph:
        module_id = graph.add_node(NodeRecord(name="pkg.mod", type="module"))
        other_id = graph.add_node(NodeRecord(name="pkg.other", type="module"))

        edge_id = graph.add_edge(
            EdgeRecord(
                source_id=module_id,
                target_id=other_id,
                type=RelationshipType.IMPORTS.value,
                metadata={"names": ["other"]},
            )
        )

        assert isinstance(edge_id, int)
        assert len(graph.get_nodes()) == 2
        assert len(graph.get_edges()) == 1


def test_graph_builder_ingests_repo_map(tmp_path):
    repo_map = {
        "modules": {
            "pkg.mod": {
                "file": "pkg/mod.py",
                "functions": [
                    {
                        "name": "foo",
                        "params": [],
                        "return_type": None,
                        "is_async": False,
                        "decorators": [],
                    }
                ],
                "classes": [
                    {
                        "name": "Bar",
                        "bases": ["BaseClass"],
                        "methods": [],
                        "decorators": [],
                    },
                    {"name": "BaseClass", "bases": [], "methods": [], "decorators": []},
                ],
            },
            "pkg.other": {
                "file": "pkg/other.py",
                "functions": [],
                "classes": [],
            },
        },
        "import_graph": {
            "edges": [
                {"from": "pkg.mod", "to": "pkg.other", "names": ["other"]},
            ]
        },
    }

    db_path = tmp_path / "kg_builder.db"
    builder = GraphBuilder(root_path=Path("."), db_path=db_path)
    summary = builder.build_from_repo_map(repo_map)

    assert summary["nodes"] == 5  # 2 modules + 1 function + 2 classes
    assert summary["edges"] >= 2  # import + inheritance

    with KnowledgeGraph(db_path) as graph:
        imports = graph.get_edges(RelationshipType.IMPORTS.value)
        inherits = graph.get_edges(RelationshipType.INHERITS.value)

        assert len(imports) == 1
        assert len(inherits) == 1
        assert graph.get_node("pkg.mod", "module") is not None
        assert graph.get_node("pkg.mod.foo", "function") is not None
        assert graph.get_node("pkg.mod.Bar", "class") is not None
        assert graph.get_node("pkg.mod.BaseClass", "class") is not None
