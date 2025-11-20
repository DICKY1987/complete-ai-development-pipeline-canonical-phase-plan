"""Test suite for all core framework schemas."""
import json, pytest
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_DIR = Path(__file__).parent.parent.parent / "schema"
SCHEMAS = ["doc-meta.v1.json", "run_record.v1.json", "step_attempt.v1.json", "run_event.v1.json", "patch_artifact.v1.json", "patch_ledger_entry.v1.json", "patch_policy.v1.json", "prompt_instance.v1.json", "execution_request.v1.json", "phase_spec.v1.json", "workstream_spec.v1.json", "task_spec.v1.json", "router_config.v1.json", "project_profile.v1.json", "profile_extension.v1.json", "bootstrap_discovery.v1.json", "bootstrap_report.v1.json"]

@pytest.mark.parametrize("schema_name", SCHEMAS)
def test_schema_is_valid(schema_name):
    with open(SCHEMA_DIR / schema_name, "r") as f:
        Draft7Validator.check_schema(json.load(f))

def test_all_schemas_exist():
    for s in SCHEMAS: assert (SCHEMA_DIR / s).exists()

def test_schema_count():
    assert len(list(SCHEMA_DIR.glob("*.json"))) == 17
