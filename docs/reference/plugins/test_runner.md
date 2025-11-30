---
doc_id: DOC-GUIDE-TEST-RUNNER-1370
---

# Test Runner Plugin

Uses CCPM's `test-and-log.sh` for multi-language test execution.

## Supported Frameworks
- Python: pytest, unittest
- JavaScript/TypeScript: jest, mocha, vitest
- Java: junit
- Go: go test
- Rust: cargo test

## Configuration
None required - auto-detects test framework.

## Output
Captures test logs to `tests/logs/` with automatic rotation.

