"""Integration tests for ToolProcessPool with real aider.

DOC_ID: DOC-TEST-AIM-AIDER-POOL-INT-001
"""

import shutil
import time

import pytest

from phase4_routing.modules.aim_tools.src.aim.process_pool import ToolProcessPool


def _aider_installed():
    return shutil.which("aider") is not None


pytestmark = pytest.mark.skipif(not _aider_installed(), reason="aider not installed")


@pytest.mark.integration
@pytest.mark.slow
def test_spawn_3_instances():
    pool = ToolProcessPool("aider", count=3)
    try:
        assert len(pool.instances) == 3
        health = pool.check_health()
        assert health["alive"] == 3
    finally:
        pool.shutdown()


@pytest.mark.integration
@pytest.mark.slow
def test_restart():
    pool = ToolProcessPool("aider", count=1)
    try:
        pool.instances[0].process.kill()
        pool.instances[0].process.wait()
        success = pool.restart_instance(0)
        assert success is True
        time.sleep(0.3)
        assert pool.check_health()["alive"] == 1
    finally:
        pool.shutdown()
