# DOC_LINK: DOC-TEST-PLUGINS-TEST-PATH-STANDARDIZER-PLUGIN-312
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/plugins/path_standardizer/src/path_standardizer/plugin.py
# TargetFunction: validate_paths|normalize_path|parse_violations
# Purpose: Validate path normalization, violation parsing, and autofix handling in the path standardizer plugin
# OptimizationPattern: Mock-Heavy
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from phase6_error_recovery.modules.plugins.path_standardizer.src.path_standardizer.plugin import (
    normalize_path,
    parse_violations,
    validate_paths,
)


def test_normalize_path_cleans_drive_and_slashes():
    windows_input = r"C:\repo\subdir\\file.txt"
    unix_input = "/repo//subdir/./file.txt"

    assert normalize_path(windows_input) == "repo/subdir/file.txt"
    assert normalize_path(unix_input) == "repo/subdir/./file.txt"


def test_parse_violations_extracts_details():
    output = (
        "C:/repo/file.txt:42: bad thing\nrelative/path - missing prefix\njust-a-message"
    )
    violations = parse_violations(output, default_file="C:/repo/default.txt")

    assert violations[0]["file"] == "repo/file.txt"
    assert violations[0]["line"] == 42
    assert violations[0]["message"] == "bad thing"

    assert violations[1]["file"] == "relative/path"
    assert violations[1]["line"] == 0
    assert violations[1]["message"] == "missing prefix"

    assert violations[2]["file"] == "repo/default.txt"
    assert violations[2]["line"] == 0
    assert violations[2]["message"] == "just-a-message"


def test_validate_paths_missing_scripts_returns_empty(tmp_path):
    result = validate_paths(["sample.py"], str(tmp_path))

    assert result["tool"] == "path_standardizer"
    assert result["errors"] == []


def test_validate_paths_collects_errors(monkeypatch, tmp_path):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    check_script = scripts_dir / "check-path-standards.sh"
    check_script.write_text("#!/bin/bash\necho")

    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        return SimpleNamespace(
            returncode=1,
            stdout="C:/repo/main.py:12: bad slash\nrelative/path - missing prefix\n",
        )

    monkeypatch.setattr(
        "phase6_error_recovery.modules.plugins.path_standardizer.src.path_standardizer.plugin.subprocess.run",
        fake_run,
    )

    result = validate_paths(["C:/repo/main.py"], str(tmp_path), autofix=False)

    assert len(calls) == 1
    assert [e["file"] for e in result["errors"]] == ["repo/main.py", "relative/path"]
    assert result["errors"][0]["line"] == 12
    assert result["errors"][1]["message"] == "missing prefix"


def test_validate_paths_autofix_skips_errors_when_fix_succeeds(monkeypatch, tmp_path):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    check_script = scripts_dir / "check-path-standards.sh"
    fix_script = scripts_dir / "fix-path-standards.sh"
    check_script.write_text("echo")
    fix_script.write_text("echo")

    responses = iter(
        [
            SimpleNamespace(returncode=1, stdout="file.py:1: issue"),
            SimpleNamespace(returncode=0, stdout="fixed"),
        ]
    )

    def fake_run(cmd, capture_output, text):
        return next(responses)

    monkeypatch.setattr(
        "phase6_error_recovery.modules.plugins.path_standardizer.src.path_standardizer.plugin.subprocess.run",
        fake_run,
    )

    result = validate_paths(["file.py"], str(tmp_path), autofix=True)

    assert result["errors"] == []
