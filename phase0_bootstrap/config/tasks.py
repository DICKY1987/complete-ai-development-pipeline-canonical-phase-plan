"""
Invoke tasks for AI Development Pipeline.

Common automation tasks using Invoke task runner.
Run with: invoke <task-name>
List all tasks: invoke --list

Note: Uses forward slashes for cross-platform compatibility.
"""
# DOC_ID: DOC-CONFIG-CONFIG-TASKS-254
# DOC_ID: DOC-CONFIG-CONFIG-TASKS-253

from invoke import task, Collection


@task
def bootstrap(c):
    """Initialize repository skeleton and dependencies."""
    print("[bootstrap] Initializing repository skeleton...")
    c.run("pwsh ./scripts/bootstrap.ps1", pty=False)


@task
def validate_workstreams(c):
    """Validate all workstream bundle files."""
    print("[validate] Checking workstream bundles...")
    c.run("python scripts/validate_workstreams.py", pty=False)


@task
def validate_imports(c):
    """Check for deprecated import patterns."""
    print("[validate] Checking for deprecated imports...")
    c.run("python scripts/validate_error_imports.py", pty=False)


@task(pre=[validate_workstreams, validate_imports])
def validate(c):
    """Run all validation tasks."""
    print("[validate] ✅ All validations passed")


@task
def test_unit(c):
    """Run unit tests."""
    print("[test] Running unit tests...")
    result = c.run("pytest tests/unit -q", warn=True, pty=False)
    if not result.ok:
        print("[test] ❌ Unit tests failed")
        raise SystemExit(1)
    print("[test] ✅ Unit tests passed")


@task
def test_integration(c):
    """Run integration tests."""
    print("[test] Running integration tests...")
    result = c.run("pytest tests/integration -q", warn=True, pty=False)
    if not result.ok:
        print("[test] ❌ Integration tests failed")
        raise SystemExit(1)
    print("[test] ✅ Integration tests passed")


@task
def test_pipeline(c):
    """Run pipeline tests."""
    print("[test] Running pipeline tests...")
    result = c.run("pytest tests/pipeline -q", warn=True, pty=False)
    if not result.ok:
        print("[test] ❌ Pipeline tests failed")
        raise SystemExit(1)
    print("[test] ✅ Pipeline tests passed")


@task
def test_all(c):
    """Run all test suites."""
    print("[test] Running all tests...")
    result = c.run("pytest tests/ -q", warn=True, pty=False)
    if not result.ok:
        print("[test] ❌ Tests failed")
        raise SystemExit(1)
    print("[test] ✅ All tests passed")


@task(pre=[validate, test_all])
def ci(c):
    """Run full CI validation suite."""
    print("[ci] ✅ CI validation complete")


@task
def run_workstream(c, ws_id, dry_run=False):
    """
    Run a single workstream.
    
    Args:
        ws_id: Workstream ID to execute
        dry_run: Run in dry-run mode (default: False)
    """
    cmd = f"python scripts/run_workstream.py --ws-id {ws_id}"
    if dry_run:
        cmd += " --dry-run"
        print(f"[workstream] Running {ws_id} in DRY-RUN mode...")
    else:
        print(f"[workstream] Running {ws_id}...")
    c.run(cmd, pty=False)


@task
def clean(c):
    """Clean generated files and caches."""
    print("[clean] Removing generated files...")
    c.run('pwsh -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache, __pycache__, .worktrees, state/*.db, logs/*.log"', pty=False)
    print("[clean] ✅ Cleanup complete")


@task
def lint_markdown(c):
    """Lint Markdown files (if markdownlint available)."""
    print("[lint] Linting Markdown files...")
    result = c.run("markdownlint **/*.md", warn=True, pty=False)
    if not result.ok:
        print("[lint] ⚠️  Markdown linting issues found")
    else:
        print("[lint] ✅ Markdown files look good")


@task
def generate_spec_index(c):
    """Generate specification index."""
    print("[generate] Generating spec index...")
    c.run("python scripts/generate_spec_index.py", pty=False)
    print("[generate] ✅ Spec index generated")


@task
def generate_spec_mapping(c):
    """Generate specification mapping."""
    print("[generate] Generating spec mapping...")
    c.run("python scripts/generate_spec_mapping.py", pty=False)
    print("[generate] ✅ Spec mapping generated")


@task(pre=[generate_spec_index, generate_spec_mapping])
def generate_indices(c):
    """Generate all indices and mappings."""
    print("[generate] ✅ All indices generated")


# Create namespace for better organization
ns = Collection()
ns.add_task(bootstrap)
ns.add_task(validate_workstreams, name='validate-workstreams')
ns.add_task(validate_imports, name='validate-imports')
ns.add_task(validate)
ns.add_task(test_unit, name='test-unit')
ns.add_task(test_integration, name='test-integration')
ns.add_task(test_pipeline, name='test-pipeline')
ns.add_task(test_all, name='test-all')
ns.add_task(ci)
ns.add_task(run_workstream, name='run-workstream')
ns.add_task(clean)
ns.add_task(lint_markdown, name='lint-markdown')
ns.add_task(generate_spec_index, name='generate-spec-index')
ns.add_task(generate_spec_mapping, name='generate-spec-mapping')
ns.add_task(generate_indices, name='generate-indices')
