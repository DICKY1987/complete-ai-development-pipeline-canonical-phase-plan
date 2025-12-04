# DOC_LINK: DOC-TEST-AUTONOMOUS-TEST-REFLEXION-304
from pathlib import Path

from core.autonomous import ErrorAnalyzer, FixGenerator, ReflexionLoop
from core.memory import EpisodicMemory


def test_error_analyzer_parses_file_and_line():
    stderr = "core/module.py:42: ValueError: boom"
    parsed = ErrorAnalyzer.parse(stderr)
    assert parsed[0].file == "core/module.py"
    assert parsed[0].line == 42
    assert "boom" in parsed[0].message


def test_reflexion_succeeds_on_first_attempt(tmp_path: Path):
    memory = EpisodicMemory(db_path=str(tmp_path / "mem.db"))

    run_calls = []

    def run_fn():
        run_calls.append("run")
        return {"result": "ok"}

    def validate_fn(output):
        assert output["result"] == "ok"
        return {"success": True}

    loop = ReflexionLoop(run_fn=run_fn, validate_fn=validate_fn, memory=memory)
    result = loop.run(
        task_id="task-success",
        task_description="Do thing",
        user_prompt="Do it",
        files_changed=["a.py"],
    )

    assert result.success is True
    assert result.escalated is False
    assert len(result.attempts) == 1
    assert result.attempts[0].success is True
    # Memory captured
    assert memory.get_episode("task-success") is not None


def test_reflexion_retries_and_escalates_after_cap(tmp_path: Path):
    memory = EpisodicMemory(db_path=str(tmp_path / "mem.db"))
    attempts = []

    def run_fn():
        attempts.append("run")
        return {"result": "fail"}

    def validate_fn(_):
        return {"success": False, "stderr": "core/foo.py:10: NameError"}

    loop = ReflexionLoop(
        run_fn=run_fn,
        validate_fn=validate_fn,
        fix_generator=FixGenerator(),
        max_iterations=2,
        memory=memory,
    )

    result = loop.run(
        task_id="task-fail",
        task_description="Failing task",
        user_prompt="Try it",
        files_changed=["foo.py"],
    )

    assert result.success is False
    assert result.escalated is True
    assert len(result.attempts) == 2
    assert result.attempts[-1].errors, "Should capture parsed errors"
    # Failure recorded to memory
    ep = memory.get_episode("task-fail")
    assert ep is not None
    assert ep.edit_accepted is False


def test_fix_generator_custom_callable_used():
    called = []

    def custom_fix(errors, attempt):
        called.append((errors, attempt))
        return {"summary": "custom", "patch": "fix"}

    gen = FixGenerator(fix_fn=custom_fix)
    out = gen.generate([], 1)
    assert out["summary"] == "custom"
    assert called, "Custom fix function should be invoked"
