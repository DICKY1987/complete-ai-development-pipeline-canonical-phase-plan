# DOC_LINK: DOC-TEST-TESTS-TEST-PATH-REGISTRY-097
# DOC_LINK: DOC-TEST-TESTS-TEST-PATH-REGISTRY-058
from __future__ import annotations

from pathlib import Path

import pytest

try:
    import yaml  # type: ignore  # noqa: F401

    HAVE_YAML = True
except Exception:
    HAVE_YAML = False


def write_registry(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "paths.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def monkeypatch_registry(monkeypatch, path: Path):
    import src.path_registry as pr

    pr.clear_cache()
    monkeypatch.setattr(pr, "_REGISTRY_PATHS", (path,))
    pr.clear_cache()
    return pr


@pytest.mark.skipif(not HAVE_YAML, reason="PyYAML not installed")
def test_resolve_and_list_paths(tmp_path: Path, monkeypatch):
    registry = write_registry(
        tmp_path,
        """
paths:
  docs:
    arch:
      path: "docs/ARCHITECTURE.md"
      section: "docs"
  core:
    tools:
      path: "core/tools.py"
      section: "core"
        """.strip(),
    )

    pr = monkeypatch_registry(monkeypatch, registry)

    # list_paths without section
    all_paths = pr.list_paths()
    assert all_paths == {
        "docs.arch": str(Path("docs/ARCHITECTURE.md")),
        "core.tools": str(Path("core/tools.py")),
    }

    # list_paths with section filter
    only_docs = pr.list_paths(section="docs")
    assert only_docs == {"docs.arch": str(Path("docs/ARCHITECTURE.md"))}

    # resolve_path
    assert pr.resolve_path("core.tools") == str(Path("core/tools.py"))


@pytest.mark.skipif(not HAVE_YAML, reason="PyYAML not installed")
def test_errors_unknown_and_invalid_keys(tmp_path: Path, monkeypatch):
    registry = write_registry(
        tmp_path,
        """
paths:
  ns:
    item:
      path: "a/b.txt"
      section: "s"
        """.strip(),
    )
    pr = monkeypatch_registry(monkeypatch, registry)

    with pytest.raises(pr.PathRegistryError):
        pr.resolve_path("")
    with pytest.raises(pr.PathRegistryError):
        pr.resolve_path("notdotted")
    with pytest.raises(pr.PathRegistryError):
        pr.resolve_path("ns.missing")


@pytest.mark.skipif(not HAVE_YAML, reason="PyYAML not installed")
def test_missing_path_value(tmp_path: Path, monkeypatch):
    registry = write_registry(
        tmp_path,
        """
paths:
  ns:
    bad:
      section: "x"
        """.strip(),
    )
    pr = monkeypatch_registry(monkeypatch, registry)
    with pytest.raises(pr.PathRegistryError):
        pr.resolve_path("ns.bad")


@pytest.mark.skipif(not HAVE_YAML, reason="PyYAML not installed")
def test_malformed_top_level(tmp_path: Path, monkeypatch):
    # Missing top-level 'paths'
    bad = write_registry(tmp_path, "foo: 1\n")
    import src.path_registry as pr

    pr.clear_cache()
    monkeypatch.setattr(pr, "_REGISTRY_PATHS", (bad,))
    with pytest.raises(ValueError):
        pr.list_paths()


@pytest.mark.skipif(not HAVE_YAML, reason="PyYAML not installed")
def test_missing_registry_file(tmp_path: Path, monkeypatch):
    import src.path_registry as pr

    pr.clear_cache()
    monkeypatch.setattr(pr, "_REGISTRY_PATHS", (tmp_path / "nope.yaml",))
    with pytest.raises(FileNotFoundError):
        pr.list_paths()
