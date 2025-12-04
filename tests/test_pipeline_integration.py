# DOC_LINK: DOC-TEST-TESTS-TEST-PIPELINE-INTEGRATION-100
# DOC_LINK: DOC-TEST-TESTS-TEST-PIPELINE-INTEGRATION-061
from core.error_pipeline_service import S_FAILED, S_SUCCESS, run_pipeline


def test_pipeline_success():
    units = ["alpha", "beta"]
    out = run_pipeline(units, max_workers=2)
    assert out["state"] == S_SUCCESS
    assert out["S2"]["failed"] == 0


def test_pipeline_recheck_and_fail():
    units = ["ok-1", "must-fail-2"]
    out = run_pipeline(units, max_workers=2)
    assert out["state"] == S_FAILED
    assert "must-fail-2" in out["failed_units"]
