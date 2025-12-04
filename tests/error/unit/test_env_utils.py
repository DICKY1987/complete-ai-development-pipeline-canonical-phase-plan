# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/shared/utils/env.py
# TargetFunction: scrub_env
# Purpose: Ensure environment scrubbing enforces locale defaults and strips proxy/path variables
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import os

from phase6_error_recovery.modules.error_engine.src.shared.utils import env


def test_scrub_env_removes_proxy_and_pythonpath():
    base_env = {
        "LC_ALL": "en_US",
        "LANG": "en_US",
        "PYTHONPATH": "/tmp/custom",
        "HTTPS_PROXY": "https://proxy",
        "KEEP_ME": "ok",
    }

    sanitized = env.scrub_env(base_env)

    # Locale should be forced to stable C locale.
    assert sanitized["LC_ALL"] == "C"
    assert sanitized["LANG"] == "C"
    # Proxy and PYTHONPATH should be removed.
    assert "HTTPS_PROXY" not in sanitized
    assert "PYTHONPATH" not in sanitized
    # Unrelated keys remain.
    assert sanitized["KEEP_ME"] == "ok"
    # Ensure we returned a copy, not the original mapping.
    assert sanitized is not base_env


def test_scrub_env_uses_os_environ_when_base_not_provided(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://proxy")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.delenv("PYTHONPATH", raising=False)

    sanitized = env.scrub_env()

    assert sanitized["LC_ALL"] == "C"
    assert sanitized["LANG"] == "C"
    assert "HTTP_PROXY" not in sanitized
    # Original os.environ should stay untouched.
    assert os.environ["HTTP_PROXY"] == "http://proxy"
