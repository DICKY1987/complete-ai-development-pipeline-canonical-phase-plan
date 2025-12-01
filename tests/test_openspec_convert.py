# DOC_LINK: DOC-TEST-TESTS-TEST-OPENSPEC-CONVERT-090
# DOC_LINK: DOC-TEST-TESTS-TEST-OPENSPEC-CONVERT-051
from pathlib import Path
import json

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.openspec_parser import load_bundle_from_change
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.openspec_convert import bundle_to_workstream
from modules.core_state import m010003_bundles as ws_bundles


def _write_change(tmp: Path, change_id: str) -> Path:
    ch = tmp / "openspec" / "changes" / change_id
    ch.mkdir(parents=True, exist_ok=True)
    (ch / "proposal.md").write_text(
        """
---
title: Demo Change
---

# Proposal

Add a tiny feature.
""".strip()
    )
    (ch / "tasks.md").write_text(
        """
- [ ] Update src/pipeline/openspec_parser.py
- [ ] Add tests
""".strip()
    )
    return ch


def test_change_to_workstream_roundtrip(tmp_path: Path, monkeypatch):
    # Prepare a fake repo layout with .git marker so schema resolution works
    (tmp_path / ".git").mkdir()
    # Copy schema into tmp repo so validation can resolve it
    real_schema = Path.cwd() / "schema" / "workstream.schema.json"
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_text = real_schema.read_text(encoding="utf-8")
    (schema_dir / "workstream.schema.json").write_text(schema_text, encoding="utf-8")
    change_id = "demo-001"
    chdir = _write_change(tmp_path, change_id)

    # Run in the temp repo context
    monkeypatch.chdir(tmp_path)

    bundle = load_bundle_from_change(change_id)
    assert bundle.bundle_id == f"openspec-{change_id}"

    # Provide explicit files_scope to satisfy schema (inference may vary)
    ws = bundle_to_workstream(
        bundle,
        change_id=change_id,
        files_scope=["src/pipeline/openspec_parser.py"],
        tool="aider",
        gate=1,
        ccpm_issue="TBD",
    )

    # Validate using existing schema logic
    ws_bundles.validate_bundle_data(ws, schema=None)

    # Ensure key fields set
    assert ws["id"] == f"ws-{change_id}"
    assert ws["openspec_change"] == change_id
    assert ws["files_scope"] == ["src/pipeline/openspec_parser.py"]
