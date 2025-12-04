from pathlib import Path

from core.knowledge.knowledge_graph import EdgeRecord, KnowledgeGraph, NodeRecord
from core.knowledge.query_engine import QueryEngine
from core.knowledge.relationships import RelationshipType


def build_graph(tmp_path):
    kg = KnowledgeGraph(tmp_path / "kg.db")
    a = kg.add_node(NodeRecord(name="pkg.a", type="module"))
    b = kg.add_node(NodeRecord(name="pkg.b", type="module"))
    c = kg.add_node(NodeRecord(name="pkg.c", type="module"))
    kg.add_edge(
        EdgeRecord(source_id=b, target_id=a, type=RelationshipType.IMPORTS.value)
    )
    kg.add_edge(
        EdgeRecord(source_id=c, target_id=b, type=RelationshipType.IMPORTS.value)
    )
    return kg


def test_callers(tmp_path):
    kg = build_graph(tmp_path)
    qe = QueryEngine(kg)
    callers = qe.callers_of("pkg.a")
    assert callers and callers[0]["caller"] == "pkg.b"


def test_dependents_chain(tmp_path):
    kg = build_graph(tmp_path)
    qe = QueryEngine(kg)
    chain = qe.dependents_chain("pkg.a", depth=5)
    assert "pkg.a" in chain
    assert "pkg.b" in chain
    assert "pkg.c" in chain


def test_usages(tmp_path):
    kg = build_graph(tmp_path)
    qe = QueryEngine(kg)
    usages = qe.usages_of("pkg.")
    assert len(usages) == 3
