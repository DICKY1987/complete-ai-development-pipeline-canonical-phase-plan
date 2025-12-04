# DOC_LINK: DOC-TEST-INTEGRATION-TEST-PHASE4-E2E-307
from core.autonomous import ReflexionLoop
from core.memory import EpisodicMemory
from core.search import HyDESearch, InMemoryVectorStore
from core.terminal import capture_state


def test_phase4_e2e_minimal_flow(tmp_path):
    # Set up memory and reflexion loop that succeeds immediately.
    memory = EpisodicMemory(db_path=str(tmp_path / "mem.db"))

    def run_fn():
        return {"result": "ok"}

    def validate_fn(output):
        return {"success": output["result"] == "ok"}

    loop = ReflexionLoop(run_fn=run_fn, validate_fn=validate_fn, memory=memory)
    reflexion_result = loop.run(
        task_id="e2e-task",
        task_description="Minimal end-to-end",
        user_prompt="run",
        files_changed=["example.py"],
    )

    assert reflexion_result.success is True
    assert memory.get_episode("e2e-task") is not None

    # HyDE search over a tiny corpus.
    store = InMemoryVectorStore()
    store.add_documents([("doc1", "def minimal_end_to_end(): pass", {})])
    hyde = HyDESearch(vector_store=store)
    hyde_results = hyde.search("minimal end to end", top_k=1)
    assert hyde_results and hyde_results[0].doc_id == "doc1"

    # Terminal capture stub
    state = capture_state(stdout="ok\n", stderr="", exit_code=0, tail_lines=5)
    assert state.stdout_tail == ["ok"]
    assert state.exit_code == 0
