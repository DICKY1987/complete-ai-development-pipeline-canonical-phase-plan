# DOC_LINK: DOC-TEST-TESTS-TEST-PATH-STANDARDIZER-098
# DOC_LINK: DOC-TEST-TESTS-TEST-PATH-STANDARDIZER-059
from __future__ import annotations

from pathlib import Path
import types

from modules.error_plugin_path_standardizer.m01000D_plugin import validate_paths


class FakeCP:
    def __init__(
        self, returncode=1, stdout="C:/repo/file.txt:12: Found absolute path", stderr=""
    ):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_validate_paths_attaches_file_and_line(monkeypatch, tmp_path: Path):
    # Arrange fake check script
    root = tmp_path
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "check-path-standards.sh").write_text("#!/bin/bash\nexit 1\n")

    calls = []

    def fake_run(args, capture_output=True, text=True):  # noqa: ARG001
        calls.append(args)
        return FakeCP()

    import subprocess

    monkeypatch.setattr(subprocess, "run", fake_run)

    res = validate_paths(["C\\\\repo\\\\file.txt"], str(root), autofix=False)
    assert res["tool"] == "path_standardizer"
    assert res["errors"], "Expected at least one error"
    e = res["errors"][0]
    assert e["file"].endswith("repo/file.txt")
    assert e["line"] == 12
