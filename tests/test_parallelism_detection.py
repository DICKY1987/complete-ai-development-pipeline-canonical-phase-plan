"""Tests for parallelism detection module."""

import pytest
from modules.core_state.m010003_bundles import WorkstreamBundle
from modules.core_planning.m010002_parallelism_detector import (
    detect_parallel_opportunities,
    detect_conflict_groups,
)


def test_simple_parallel_detection():
    """Test detection of simple parallel opportunities."""
# DOC_ID: DOC-TEST-TESTS-TEST-PARALLELISM-DETECTION-093
# DOC_ID: DOC-TEST-TESTS-TEST-PARALLELISM-DETECTION-054
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file1.py",),
            tasks=("Task A",),
            tool="aider",
            parallel_ok=True,
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file2.py",),
            tasks=("Task B",),
            tool="aider",
            parallel_ok=True,
        ),
    ]

    profile = detect_parallel_opportunities(bundles, max_workers=4)

    assert len(profile.waves) == 1  # Both can run in same wave
    assert len(profile.waves[0]) == 2  # Both workstreams in wave
    assert profile.max_parallelism == 2
    assert profile.estimated_speedup == 2.0  # 2 sequential / 1 wave


def test_file_scope_conflict():
    """Test that file scope conflicts prevent parallelism."""
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file.py",),
            tasks=("Task A",),
            tool="aider",
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file.py",),  # Same file
            tasks=("Task B",),
            tool="aider",
        ),
    ]

    profile = detect_parallel_opportunities(bundles, max_workers=4)

    assert len(profile.waves) == 2  # Must run in separate waves
    assert len(profile.conflicts) > 0  # Conflict detected


def test_conflict_group_serialization():
    """Test that conflict_group enforces serialization."""
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file1.py",),
            tasks=("Task A",),
            tool="aider",
            conflict_group="database",
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file2.py",),
            tasks=("Task B",),
            tool="aider",
            conflict_group="database",  # Same group
        ),
    ]

    profile = detect_parallel_opportunities(bundles, max_workers=4)

    assert len(profile.waves) == 2  # Must run in separate waves


def test_dependency_levels():
    """Test that dependencies create proper execution levels."""
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file1.py",),
            tasks=("Task A",),
            tool="aider",
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file2.py",),
            tasks=("Task B",),
            tool="aider",
            depends_on=("ws-a",),  # Depends on A
        ),
    ]

    profile = detect_parallel_opportunities(bundles, max_workers=4)

    assert len(profile.waves) >= 2  # At least 2 waves (A, then B)
    # ws-a must come before ws-b
    a_wave = next(i for i, w in enumerate(profile.waves) if "ws-a" in w)
    b_wave = next(i for i, w in enumerate(profile.waves) if "ws-b" in w)
    assert a_wave < b_wave


def test_parallel_ok_false():
    """Test that parallel_ok=False forces serialization."""
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file1.py",),
            tasks=("Task A",),
            tool="aider",
            parallel_ok=False,  # Cannot run in parallel
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file2.py",),
            tasks=("Task B",),
            tool="aider",
        ),
    ]

    profile = detect_parallel_opportunities(bundles, max_workers=4)

    # ws-a should run alone in its wave
    a_wave = next(w for w in profile.waves if "ws-a" in w)
    assert len(a_wave) == 1


def test_detect_conflict_groups():
    """Test conflict group detection."""
    bundles = [
        WorkstreamBundle(
            id="ws-a",
            openspec_change="TEST-1",
            ccpm_issue="1",
            gate=1,
            files_scope=("file1.py",),
            tasks=("Task A",),
            tool="aider",
            conflict_group="database",
        ),
        WorkstreamBundle(
            id="ws-b",
            openspec_change="TEST-2",
            ccpm_issue="2",
            gate=1,
            files_scope=("file2.py",),
            tasks=("Task B",),
            tool="aider",
            conflict_group="database",
        ),
        WorkstreamBundle(
            id="ws-c",
            openspec_change="TEST-3",
            ccpm_issue="3",
            gate=1,
            files_scope=("file3.py",),
            tasks=("Task C",),
            tool="aider",
            conflict_group="api",
        ),
    ]

    groups = detect_conflict_groups(bundles)

    assert "database" in groups
    assert len(groups["database"]) == 2
    assert "api" in groups
    assert len(groups["api"]) == 1
