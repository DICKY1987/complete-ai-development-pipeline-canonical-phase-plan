# DOC_LINK: DOC-TEST-MEMORY-TEST-EPISODIC-MEMORY-310
import json
from pathlib import Path

import pytest

from core.memory import EpisodicMemory, PatternLearner


@pytest.fixture()
def temp_memory(tmp_path: Path) -> EpisodicMemory:
    db_path = tmp_path / "episodic_memory.db"
    return EpisodicMemory(db_path=str(db_path))


def test_record_and_get_episode(temp_memory: EpisodicMemory):
    temp_memory.record_episode(
        task_id="task-001",
        task_description="Implement login flow",
        user_prompt="Add login feature",
        files_changed=["core/auth.py", "core/routes.py"],
        edit_accepted=True,
        project_conventions=["use type hints", "prefer dataclasses"],
        metadata={"reviewer": "alice"},
    )

    episode = temp_memory.get_episode("task-001")
    assert episode is not None
    assert episode.task_id == "task-001"
    assert episode.edit_accepted is True
    assert "core/auth.py" in episode.files_changed
    assert "use type hints" in episode.project_conventions
    assert episode.metadata["reviewer"] == "alice"
    assert len(episode.embedding) > 0


def test_recall_similar_tasks_ranks_by_similarity(temp_memory: EpisodicMemory):
    temp_memory.record_episode(
        task_id="t1",
        task_description="Implement login flow",
        user_prompt="Add login",
        files_changed=["core/auth.py"],
        edit_accepted=True,
        project_conventions=[],
    )
    temp_memory.record_episode(
        task_id="t2",
        task_description="Fix login bug",
        user_prompt="Fix auth",
        files_changed=["core/auth.py"],
        edit_accepted=False,
        project_conventions=[],
    )
    temp_memory.record_episode(
        task_id="t3",
        task_description="Write documentation for deployment",
        user_prompt="Docs",
        files_changed=["docs/deploy.md"],
        edit_accepted=True,
        project_conventions=[],
    )

    results = temp_memory.recall_similar_tasks(
        "Improve login flow", top_k=2, min_score=0.05
    )
    task_ids = [item["episode"].task_id for item in results]

    assert "t1" in task_ids and "t2" in task_ids
    assert "t3" not in task_ids
    assert results[0]["score"] >= results[1]["score"]


def test_persistence_across_sessions(tmp_path: Path):
    db_path = tmp_path / "episodic_memory.db"
    with EpisodicMemory(db_path=str(db_path)) as memory:
        memory.record_episode(
            task_id="persist-1",
            task_description="Refactor scheduler",
            user_prompt="Refactor",
            files_changed=["core/scheduler.py"],
            edit_accepted=True,
            project_conventions=["use logging"],
        )

    # New instance reads existing episode
    memory = EpisodicMemory(db_path=str(db_path))
    episodes = memory.list_episodes()
    assert any(ep.task_id == "persist-1" for ep in episodes)


def test_pattern_learner_extracts_conventions(temp_memory: EpisodicMemory):
    temp_memory.record_episode(
        task_id="p1",
        task_description="Add tracing",
        user_prompt="Add tracing",
        files_changed=["core/tracing.py"],
        edit_accepted=True,
        project_conventions=["use structured logging", "add type hints"],
    )
    temp_memory.record_episode(
        task_id="p2",
        task_description="Fix tracing bug",
        user_prompt="Fix tracing",
        files_changed=["core/tracing.py"],
        edit_accepted=False,
        project_conventions=["use structured logging", "prefer dataclasses"],
    )

    learner = PatternLearner(temp_memory)
    patterns = learner.learn_patterns()

    assert "use structured logging" in patterns["conventions"]
    assert 0 <= patterns["success_rate"] <= 1
    assert patterns["recent_examples"], "Should surface recent episodes for context"
