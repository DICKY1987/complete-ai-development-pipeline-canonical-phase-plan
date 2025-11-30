"""Example: Pattern event emission in action.

This example shows how to integrate pattern event emission into
your existing engine/orchestrator code.
"""
DOC_ID: DOC-PAT-PATTERN-EVENT-SYSTEM-PATTERN-EVENTS-805

from core.engine.pattern_events import (
    PatternEvent,
    PatternRun,
    PatternEventEmitter,
    PatternRunAggregator,
    emit_pattern_event,
)


def example_pattern_execution():
    """Simulate a pattern execution with event emission."""
    
    # Initialize emitter
    emitter = PatternEventEmitter()
    aggregator = PatternRunAggregator(emitter)
    
    # Job context
    job_id = "JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ"
    step_id = "STEP-003"
    pattern_id = "PAT-SEMGRP-001"
    
    # Create pattern run
    pattern_run = PatternRun.create(
        pattern_id=pattern_id,
        job_id=job_id,
        operation_kind="semgrep_scan",
        step_id=step_id,
        pattern_version="1.2.0",
    )
    
    print(f"Pattern Run: {pattern_run.pattern_run_id}\n")
    
    # === STEP 1: Pattern Selection ===
    
    event = PatternEvent.create(
        event_type="pattern.selection.started",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "operation_kind": "semgrep_scan",
            "context": {
                "tool": "semgrep",
                "language": "python",
            },
            "candidate_patterns": ["PAT-SEMGRP-001", "PAT-SEMGRP-002"]
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    event = PatternEvent.create(
        event_type="pattern.selection.resolved",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "operation_kind": "semgrep_scan",
            "pattern_id": pattern_id,
            "selection_method": "auto",
            "inputs_preview": {
                "target_paths": ["src/", "tests/"],
                "severity": "medium+",
            }
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    # === STEP 2: Template Expansion ===
    
    event = PatternEvent.create(
        event_type="pattern.template.expanded",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "template_version": "1.2.0",
            "variables_resolved": 12,
            "generated_artifacts": [
                ".worktrees/JOB-.../semgrep.config.yaml",
                ".worktrees/JOB-.../run_semgrep.sh",
            ],
            "command_preview": "semgrep --config auto --severity medium+ ..."
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    # === STEP 3: Validation ===
    
    event = PatternEvent.create(
        event_type="pattern.validation.started",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "validation_type": "preflight",
            "checks": [
                "tool_availability",
                "target_paths_exist",
                "config_file_valid",
            ]
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    event = PatternEvent.create(
        event_type="pattern.validation.completed",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "validation_type": "preflight",
            "checks_passed": 3,
            "checks_failed": 0,
            "warnings": []
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    # === STEP 4: Execution ===
    
    event = PatternEvent.create(
        event_type="pattern.execution.started",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "executor": "subprocess",
            "command": "semgrep --config auto --severity medium+ src/ tests/",
            "working_dir": "/path/to/.worktrees/JOB-...",
            "timeout_seconds": 300
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    # Simulate execution...
    import time
    time.sleep(0.5)
    
    event = PatternEvent.create(
        event_type="pattern.execution.completed",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="success",
        details={
            "exit_code": 0,
            "duration_seconds": 18.74,
            "result_summary": {
                "finding_count": 12,
                "files_scanned": 47,
                "errors": 0,
            },
            "artifacts": [
                "state/reports/semgrep/JOB-.../semgrep_report.json",
                "state/reports/semgrep/JOB-.../semgrep_summary.html",
            ],
            "stdout_lines": 124,
            "stderr_lines": 2,
        },
        step_id=step_id,
    )
    emitter.emit(event, job_scoped=True)
    aggregator.handle_event(event)
    print(f"✓ Emitted: {event.event_type}")
    
    # === Display Results ===
    
    print("\n" + "=" * 60)
    print("Pattern Run Summary")
    print("=" * 60)
    
    final_run = aggregator.get_run(pattern_run.pattern_run_id)
    print(f"Status:          {final_run.status}")
    print(f"Duration:        {final_run.duration_seconds:.2f}s")
    print(f"Events:          {len(final_run.events)}")
    print(f"Artifacts:       {len(final_run.artifacts)}")
    print(f"Finding Count:   {final_run.outputs.get('finding_count', 0)}")
    
    print("\nTo inspect via CLI:")
    print(f"  python -m core.engine.pattern_inspect run {pattern_run.pattern_run_id}")


def example_simple_emission():
    """Simpler example using convenience function."""
    
    job_id = "JOB-TEST-001"
    pattern_run_id = "PRUN-TEST-001"
    
    # Emit event with one function call
    event = emit_pattern_event(
        event_type="pattern.execution.completed",
        job_id=job_id,
        pattern_run_id=pattern_run_id,
        pattern_id="PAT-PYTEST-001",
        status="success",
        details={
            "exit_code": 0,
            "duration_seconds": 5.3,
            "result_summary": {
                "tests_passed": 42,
                "tests_failed": 0,
            }
        },
    )
    
    print(f"✓ Emitted event: {event.event_id}")
    print(f"  Type: {event.event_type}")
    print(f"  Status: {event.status}")


if __name__ == "__main__":
    print("Example 1: Full Pattern Execution Lifecycle")
    print("=" * 60 + "\n")
    example_pattern_execution()
    
    print("\n\n")
    print("Example 2: Simple Event Emission")
    print("=" * 60 + "\n")
    example_simple_emission()
