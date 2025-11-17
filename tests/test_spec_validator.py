from src.plugins.spec_validator import parse_when_then, validate


def test_parse_when_then():
    w, t = parse_when_then("WHEN A THEN B")
    assert w == "A" and t == "B"


def test_validate_flags_malformed():
    issues = validate("U1", ["WHEN only_when"])
    assert any(i.severity == "error" for i in issues)

