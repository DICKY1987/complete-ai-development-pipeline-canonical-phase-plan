# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/error_context.py
# TargetFunction: ErrorPipelineContext
# Purpose: Validate serialization and mutation helpers on the error pipeline context dataclass
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)


def test_context_serialization_roundtrip():
    ctx = ErrorPipelineContext(
        run_id="r1",
        workstream_id="w1",
        python_files=["a.py"],
        powershell_files=["b.ps1"],
        enable_mechanical_autofix=False,
        enable_aider=False,
        enable_codex=True,
        enable_claude=False,
        strict_mode=False,
        max_attempts_per_agent=3,
        attempt_number=2,
        current_agent="codex",
        mechanical_fix_applied=True,
        last_error_report={"msg": "last"},
        previous_error_report={"msg": "prev"},
        ai_attempts=[{"agent": "codex"}],
        final_status="success",
        quarantine_path=None,
        current_state="S_DONE",
    )

    serialized = ctx.to_json()
    restored = ErrorPipelineContext.from_json(serialized)

    assert restored.run_id == "r1"
    assert restored.workstream_id == "w1"
    assert restored.python_files == ["a.py"]
    assert restored.powershell_files == ["b.ps1"]
    assert restored.enable_mechanical_autofix is False
    assert restored.enable_aider is False
    assert restored.enable_codex is True
    assert restored.enable_claude is False
    assert restored.strict_mode is False
    assert restored.max_attempts_per_agent == 3
    assert restored.attempt_number == 2
    assert restored.current_agent == "codex"
    assert restored.mechanical_fix_applied is True
    assert restored.last_error_report == {"msg": "last"}
    assert restored.previous_error_report == {"msg": "prev"}
    assert restored.ai_attempts == [{"agent": "codex"}]
    assert restored.final_status == "success"
    assert restored.quarantine_path is None
    assert restored.current_state == "S_DONE"


def test_context_mutation_helpers():
    ctx = ErrorPipelineContext(run_id="r2", workstream_id="w2")

    ctx.record_ai_attempt({"agent": "aider", "ok": True})
    assert ctx.ai_attempts == [{"agent": "aider", "ok": True}]

    ctx.update_error_reports({"msg": "first"})
    assert ctx.last_error_report == {"msg": "first"}
    assert ctx.previous_error_report is None

    ctx.update_error_reports({"msg": "second"})
    assert ctx.last_error_report == {"msg": "second"}
    assert ctx.previous_error_report == {"msg": "first"}
