# Phase 12: End-to-end validation and testing

Validate the full workflow from OpenSpec change through pipeline execution,
including success criteria and basic performance checks.

## Objectives

- Demonstrate an end-to-end run using generated OpenSpec bundles.
- Verify each stage produces expected artifacts and final state.
- Establish baseline performance metrics for CI and local runs.
- Update docs with commands and expected outputs.

## Prerequisites

- Phase 09–11 code or equivalents available in the working tree.
- `pytest`, `python` available in the environment.

## Tasks

1. Create a test OpenSpec change under a temp directory.
2. Parse and normalize into a bundle using the Phase 09 CLI.
3. Select unit identifiers (e.g., spec item IDs or file paths).
4. Execute the pipeline using Phase 11 `run_pipeline` stubs.
5. Capture results and compare to success criteria.
6. Record basic timing for performance benchmarks.

## Example: create a test OpenSpec change

```bash
tmp_dir=".e2e-demo"
rm -rf "$tmp_dir" && mkdir -p "$tmp_dir"
cat > "$tmp_dir/demo.yaml" <<'YAML'
bundle-id: demo-e2e-001
version: 1.0
items:
  - id: A
    title: Always pass
  - id: must-fail
    title: Fails in test-runner
YAML

python -m src.pipeline.openspec_parser "$tmp_dir" --out "$tmp_dir/out" --echo
```

Expected output includes normalized YAML and a printed path to the last bundle
file written under `.e2e-demo/out/demo-e2e-001.yaml`.

## Example: execute the pipeline

```bash
python - <<'PY'
from src.pipeline.error_pipeline_service import run_pipeline, S_SUCCESS, S_FAILED

units = ["A", "must-fail"]
result = run_pipeline(units, max_workers=2)
print(result["state"])  # expect S_FAILED
print(result["failed_units"])  # expect ['must-fail']
PY
```

## Success criteria

- Bundle generation succeeds and produces a deterministic YAML file.
- Pipeline returns `S_FAILED` for the provided demo units (as designed).
- Changing `units = ["A"]` yields `S_SUCCESS` with zero failed.

## Performance benchmarking

- Local benchmark (informal):
  - Measure time to parse and emit a bundle with 100 items.
  - Measure pipeline execution with 100 units and `max_workers=8`.
- CI baseline suggestion:
  - Bundle generation: < 1s for 100 items
  - Pipeline run (stubs): < 1s for 100 units

## Documentation updates

- Add a short section to `docs/PHASE_PLAN.md` linking these commands.
- Optionally record timings and environment in `docs/COMPLETE_IMPLEMENTATION_SUMMARY.md`.

## Rollback plan

- Delete any temporary `.e2e-demo` folders created during experimentation.
- Revert doc references if added.

