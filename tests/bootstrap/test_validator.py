"""Tests for Bootstrap Validation Engine - WS-02-03A"""

import json
import yaml
import pytest

pytest.importorskip("jsonschema")
import sys
from pathlib import Path

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.bootstrap.validator import BootstrapValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def setup_fixtures(tmp_path):
    """Create test fixtures"""
    # DOC_ID: DOC-TEST-BOOTSTRAP-TEST-VALIDATOR-171
    # Valid PROJECT_PROFILE.yaml
    valid_profile = {
        "project_id": "PRJ-TEST",
        "project_name": "Test Project",
        "project_root": str(tmp_path),
        "domain": "software-dev",
        "profile_id": "generic",
        "profile_version": "1.0.0",
        "resource_types": {"files": {"root": ".", "tracked_by": "git"}},
        "available_tools": [
            {"tool_id": "tool1", "command": "tool1", "capabilities": ["test"]},
            {"tool_id": "tool2", "command": "tool2", "capabilities": ["build"]},
        ],
        "framework_paths": {
            "tasks_dir": ".tasks/",
            "ledger_dir": ".ledger/",
            "worktrees_dir": ".worktrees/",
            "quarantine_dir": ".quarantine/",
            "registry_file": "registry/project.registry.yaml",
        },
        "constraints": {"patch_only": True, "max_lines_changed": 500},
    }

    # Valid router_config.json
    valid_router = {
        "version": "1.0.0",
        "apps": {
            "tool1": {
                "kind": "tool",
                "command": "tool1",
                "capabilities": {"task_kinds": ["test"], "domains": ["software-dev"]},
            }
        },
        "routing": {"rules": []},
        "defaults": {"max_attempts": 3, "timeout_seconds": 600},
    }

    profile_path = tmp_path / "PROJECT_PROFILE.yaml"
    router_path = tmp_path / "router_config.json"

    with open(profile_path, "w", encoding="utf-8") as f:
        yaml.dump(valid_profile, f)

    with open(router_path, "w", encoding="utf-8") as f:
        json.dump(valid_router, f, indent=2)

    return {
        "profile_path": profile_path,
        "router_path": router_path,
        "profile_data": valid_profile,
        "router_data": valid_router,
        "tmp_path": tmp_path,
    }


def test_valid_artifacts(setup_fixtures):
    """Test that valid artifacts pass all validations"""
    fixtures = setup_fixtures

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    # Debug: print result if invalid
    if not result["valid"]:
        print(f"\nErrors: {result['errors']}")
        print(f"Warnings: {result['warnings']}")
        print(f"Needs human: {result['needs_human']}")

    assert result["valid"] is True
    assert len(result["errors"]) == 0
    assert len(result["needs_human"]) == 0


def test_invalid_schema(setup_fixtures):
    """Test that invalid schema is caught"""
    fixtures = setup_fixtures

    # Create invalid profile (missing required field)
    invalid_profile = fixtures["profile_data"].copy()
    del invalid_profile["project_id"]

    with open(fixtures["profile_path"], "w", encoding="utf-8") as f:
        yaml.dump(invalid_profile, f)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any(e["type"] == "schema_validation" for e in result["errors"])


def test_relaxed_constraint(setup_fixtures):
    """Test that relaxed constraints are flagged"""
    fixtures = setup_fixtures

    # Relax max_lines_changed constraint
    relaxed_profile = fixtures["profile_data"].copy()
    relaxed_profile["constraints"]["max_lines_changed"] = 1000

    with open(fixtures["profile_path"], "w", encoding="utf-8") as f:
        yaml.dump(relaxed_profile, f)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert result["valid"] is False
    assert len(result["needs_human"]) > 0
    assert any(
        nh["type"] == "relaxed_constraint" and nh["constraint"] == "max_lines_changed"
        for nh in result["needs_human"]
    )


def test_missing_tool_warning(setup_fixtures):
    """Test that tools in router not in available_tools generate warnings"""
    fixtures = setup_fixtures

    # Add tool to router that's not in available_tools
    router_with_extra = fixtures["router_data"].copy()
    router_with_extra["apps"]["tool3"] = {
        "kind": "tool",
        "command": "tool3",
        "capabilities": {"task_kinds": ["test"], "domains": ["software-dev"]},
    }

    with open(fixtures["router_path"], "w", encoding="utf-8") as f:
        json.dump(router_with_extra, f, indent=2)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert len(result["warnings"]) > 0
    assert any(w["type"] == "tool_mismatch" for w in result["warnings"])


def test_path_normalization(setup_fixtures):
    """Test that Windows paths are auto-fixed"""
    fixtures = setup_fixtures

    # Use Windows-style backslashes
    windows_profile = fixtures["profile_data"].copy()
    windows_profile["framework_paths"] = {
        "tasks_dir": ".tasks\\",
        "ledger_dir": ".ledger\\",
        "worktrees_dir": ".worktrees\\",
        "quarantine_dir": ".quarantine\\",
        "registry_file": "registry\\project.registry.yaml",
    }

    with open(fixtures["profile_path"], "w", encoding="utf-8") as f:
        yaml.dump(windows_profile, f)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert len(result["auto_fixed"]) > 0
    assert any(af["type"] == "path_normalization" for af in result["auto_fixed"])

    # Verify paths were actually fixed
    with open(fixtures["profile_path"], "r", encoding="utf-8") as f:
        fixed_profile = yaml.safe_load(f)

    assert "\\" not in str(fixed_profile["framework_paths"])


def test_missing_defaults_autofix(setup_fixtures):
    """Test that missing defaults are auto-added"""
    fixtures = setup_fixtures

    # Remove constraints
    no_defaults_profile = fixtures["profile_data"].copy()
    del no_defaults_profile["constraints"]

    with open(fixtures["profile_path"], "w", encoding="utf-8") as f:
        yaml.dump(no_defaults_profile, f)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert any(af["type"] == "missing_defaults" for af in result["auto_fixed"])

    # Verify defaults were added
    with open(fixtures["profile_path"], "r", encoding="utf-8") as f:
        fixed_profile = yaml.safe_load(f)

    assert "constraints" in fixed_profile
    assert fixed_profile["constraints"]["patch_only"] is True
    assert fixed_profile["constraints"]["max_lines_changed"] == 500


def test_profile_id_mismatch(setup_fixtures):
    """Test that profile_id mismatch is caught"""
    fixtures = setup_fixtures

    validator = BootstrapValidator(
        str(fixtures["profile_path"]),
        str(fixtures["router_path"]),
        "different-profile",  # Doesn't match "generic" in the fixture
    )

    result = validator.validate_all()

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any(e["type"] == "consistency_error" for e in result["errors"])


def test_patch_only_disabled(setup_fixtures):
    """Test that disabling patch_only is flagged"""
    fixtures = setup_fixtures

    unsafe_profile = fixtures["profile_data"].copy()
    unsafe_profile["constraints"]["patch_only"] = False

    with open(fixtures["profile_path"], "w", encoding="utf-8") as f:
        yaml.dump(unsafe_profile, f)

    validator = BootstrapValidator(
        str(fixtures["profile_path"]), str(fixtures["router_path"]), "generic"
    )

    result = validator.validate_all()

    assert result["valid"] is False
    assert len(result["needs_human"]) > 0
    assert any(
        nh["type"] == "relaxed_constraint" and nh["constraint"] == "patch_only"
        for nh in result["needs_human"]
    )
