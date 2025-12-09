# PAT-PYTEST-CORE-001: Core Pytest Execution

## Purpose
Execute the pytest test suite and collect results.

## Implementation
1. Run pytest with configured args from `config/tool_profiles.json`.
2. Capture stdout and stderr.
3. Parse test results.
4. Extract failure details if any.

## Command Template
```bash
pytest ${test_paths} -q --tb=short
```

## Success Criteria
- Exit code 0.
- Output contains "passed".
- Output does not contain "failed" or "error".

## Failure Handling
- Collect failure details.
- Extract stack traces.
- Log to error collection.
- Continue execution (NO STOP MODE).
