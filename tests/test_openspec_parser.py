# DOC_LINK: DOC-TEST-TESTS-TEST-OPENSPEC-PARSER-091
# DOC_LINK: DOC-TEST-TESTS-TEST-OPENSPEC-PARSER-052
from pathlib import Path
from core.openspec_parser import load_bundle_from_yaml, write_bundle


def test_load_and_roundtrip(tmp_path: Path):
    src = tmp_path / "demo.yaml"
    src.write_text(
        (
            "bundle-id: demo-001\n"
            "version: 1.0\n"
            "items:\n"
            "  - id: S-1\n"
            "    title: Login succeeds\n"
            "    when-then:\n"
            "      - when: user submits valid credentials\n"
            "        then: session is created\n"
        ),
        encoding="utf-8",
    )
    b = load_bundle_from_yaml(src)
    assert b.bundle_id == "demo-001"
    out = write_bundle(b, tmp_path)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "bundle-id: \"demo-001\"" in text or "bundle-id: demo-001" in text
