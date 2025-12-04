# DOC_LINK: DOC-TEST-TESTS-TEST-ENTRY-POINT-REACHABILITY-302
from scripts.entry_point_reachability import EntryPointReachabilityAnalyzer


def _write_file(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_find_entry_points_includes_additional_roots(tmp_path):
    """Ensure analyzer seeds entry points from tools, templates, UET, and nested scripts."""
    _write_file(tmp_path / "tools" / "tool_runner.py", "def run():\n    return True\n")
    _write_file(tmp_path / "templates" / "template_script.py", "# template helper\n")
    _write_file(
        tmp_path
        / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"
        / "patterns"
        / "example.py",
        "# uet example\n",
    )
    _write_file(
        tmp_path / "scripts" / "nested" / "helper.py", "def helper():\n    return 1\n"
    )

    analyzer = EntryPointReachabilityAnalyzer(tmp_path)
    entry_points = analyzer.find_entry_points()

    expected = {
        "tools.tool_runner",
        "templates.template_script",
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.patterns.example",
        "scripts.nested.helper",
    }
    assert expected.issubset(entry_points)


def test_cross_validation_flags_string_imports(tmp_path):
    """Cross-validation should warn when unreachable modules are still referenced."""
    _write_file(tmp_path / "core" / "dynamic_module.py", "VALUE = 1\n")
    _write_file(
        tmp_path / "tests" / "test_dynamic.py",
        'import importlib\nimportlib.import_module("core.dynamic_module")\n',
    )

    analyzer = EntryPointReachabilityAnalyzer(tmp_path)
    analyzer.entry_points = analyzer.find_entry_points()
    analyzer.build_import_graph()
    analyzer.compute_reachability()
    warnings = analyzer.cross_validate_orphans()

    assert any("core.dynamic_module" in warning for warning in warnings)
