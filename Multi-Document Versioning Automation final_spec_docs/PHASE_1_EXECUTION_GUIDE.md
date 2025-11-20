# Phase 1 Execution Guide

**Phase:** Foundation & Testing  
**Duration:** 3-4 days  
**Prerequisites:** Current module with 5 working tools  
**Outcome:** Test coverage ≥85%, README complete, CI enhanced

---

## Day 1: Documentation Foundation

### Morning: README.md (2-3 hours)

Create `README.md` with these sections:

```markdown
# Multi-Document Versioning Automation

> Contract-driven documentation-as-code with versioning and traceability

## Features
- Deterministic identity using ULIDs + stable human keys
- Paragraph-level fingerprinting with SHA-256 MFIDs
- Microkernel + plugins architecture
- CI-ready validation with 6-layer gates
- Immutable audit trail (Cards → Ledger → Registry)

## Quick Start

### Installation
```bash
# Clone repository
git clone <repo-url>
cd multi-doc-versioning

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Generate sidecars for your markdown docs
python -m tools.spec_indexer.indexer docs/source

# Validate suite integrity
python -m tools.spec_guard.guard

# Resolve a specification URI
python -m tools.spec_resolver.resolver "spec://ARCH/1#p-3"

# Render complete specification
python -m tools.spec_renderer.renderer --output build/spec.md
```

## Architecture
- **Microkernel:** Core validation and identity management
- **Plugins:** Extensible document processing pipeline
- **Sidecar Pattern:** Metadata separated from content
- **Event Sourcing:** Immutable ledger of all changes

See [Architecture Guide](docs/architecture-guide.md) for details.

## Tools

| Tool | Purpose | Entry Point |
|------|---------|-------------|
| `spec_indexer` | Generate/update sidecars | `tools.spec_indexer.indexer` |
| `spec_guard` | Validate suite integrity | `tools.spec_guard.guard` |
| `spec_resolver` | Resolve spec URIs | `tools.spec_resolver.resolver` |
| `spec_patcher` | Surgical paragraph edits | `tools.spec_patcher.patcher` |
| `spec_renderer` | Render documentation | `tools.spec_renderer.renderer` |

## Development

### Running Tests
```bash
pytest -v --cov=tools --cov-report=html
```

### Code Quality
```bash
black tools/ tests/
ruff check tools/ tests/
mypy tools/
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
MIT License - see [LICENSE](LICENSE)
```

### Afternoon: Dependencies & Supporting Docs (2 hours)

**Create `requirements.txt`:**
```txt
# Core dependencies
pyyaml>=6.0.1,<7.0
jsonschema>=4.19.0,<5.0
jinja2>=3.1.2,<4.0

# Testing
pytest>=7.4.0,<8.0
pytest-cov>=4.1.0,<5.0

# BDD testing (Phase 2)
pytest-bdd>=6.1.1,<7.0

# Development tools
black>=23.0.0,<24.0
ruff>=0.1.0,<0.2.0
mypy>=1.7.0,<2.0
```

**Create `CHANGELOG.md`:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20

### Added
- Initial release with 5 core tools
- Specification suite with 28 documents
- Sidecar metadata system with MFIDs
- Suite index and validation framework
- CI/CD workflow with GitHub Actions

### Architecture
- Microkernel + plugins design
- Contract-first interfaces
- Immutable identity (ULID + human keys)
- Cards → Ledger → Registry pattern

### Tools
- `spec_indexer`: Sidecar generation
- `spec_guard`: Integrity validation
- `spec_resolver`: URI resolution (spec:// and specid://)
- `spec_patcher`: Paragraph-level editing
- `spec_renderer`: Documentation rendering
```

**Choose and add LICENSE file (MIT recommended):**
```
MIT License

Copyright (c) 2025 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
[Complete MIT text]
```

### Verification
- [ ] `README.md` has all sections, links work
- [ ] `requirements.txt` complete and formatted
- [ ] `CHANGELOG.md` follows Keep a Changelog format
- [ ] `LICENSE` file added

---

## Day 2: Unit Tests - Indexer & Guard

### Morning: test_indexer.py (3 hours)

Create `tests/unit/test_indexer.py`:

```python
"""Unit tests for spec_indexer tool."""

import hashlib
from pathlib import Path
import yaml
import pytest
from tools.spec_indexer.indexer import (
    compute_mfid,
    compute_paragraphs,
    generate_sidecar,
)


@pytest.fixture
def sample_markdown(tmp_path):
    """Create sample markdown file."""
    md_file = tmp_path / "sample.md"
    content = """# Sample Doc

This is paragraph one.

This is paragraph two.
It spans multiple lines.

Final paragraph."""
    md_file.write_text(content, encoding="utf-8")
    return md_file


def test_compute_mfid_deterministic():
    """MFID computation is deterministic."""
    data = b"test content"
    mfid1 = compute_mfid(data)
    mfid2 = compute_mfid(data)
    assert mfid1 == mfid2
    assert len(mfid1) == 64  # SHA-256 hex


def test_compute_mfid_changes_with_content():
    """MFID changes when content changes."""
    mfid1 = compute_mfid(b"content A")
    mfid2 = compute_mfid(b"content B")
    assert mfid1 != mfid2


def test_compute_paragraphs_basic(sample_markdown):
    """Paragraph detection works correctly."""
    content = sample_markdown.read_text(encoding="utf-8")
    paragraphs = compute_paragraphs(content)
    
    assert len(paragraphs) == 4
    # Check first paragraph
    start, end, text = paragraphs[0]
    assert start == 1
    assert "# Sample Doc" in text


def test_compute_paragraphs_empty_file(tmp_path):
    """Empty file produces no paragraphs."""
    empty = tmp_path / "empty.md"
    empty.write_text("", encoding="utf-8")
    paragraphs = compute_paragraphs(empty.read_text())
    assert len(paragraphs) == 0


def test_generate_sidecar_creates_file(sample_markdown):
    """Sidecar file is created with correct structure."""
    generate_sidecar(str(sample_markdown))
    
    sidecar_path = Path(str(sample_markdown) + ".sidecar.yaml")
    assert sidecar_path.exists()
    
    with open(sidecar_path, "r", encoding="utf-8") as f:
        sidecar = yaml.safe_load(f)
    
    assert sidecar["file"] == str(sample_markdown)
    assert "mfid" in sidecar
    assert len(sidecar["paragraphs"]) == 4
    
    # Check first paragraph structure
    p1 = sidecar["paragraphs"][0]
    assert p1["anchor"] == "p-1"
    assert p1["start_line"] == 1
    assert "mfid" in p1


def test_generate_sidecar_preserves_ids(sample_markdown):
    """Existing paragraph IDs are preserved."""
    # Generate initial sidecar
    generate_sidecar(str(sample_markdown))
    
    sidecar_path = Path(str(sample_markdown) + ".sidecar.yaml")
    with open(sidecar_path, "r", encoding="utf-8") as f:
        sidecar = yaml.safe_load(f)
    
    # Manually add IDs
    for i, p in enumerate(sidecar["paragraphs"]):
        p["id"] = f"TEST-ID-{i}"
    
    with open(sidecar_path, "w", encoding="utf-8") as f:
        yaml.dump(sidecar, f)
    
    # Regenerate
    generate_sidecar(str(sample_markdown))
    
    with open(sidecar_path, "r", encoding="utf-8") as f:
        new_sidecar = yaml.safe_load(f)
    
    # IDs should be preserved
    for i, p in enumerate(new_sidecar["paragraphs"]):
        assert p["id"] == f"TEST-ID-{i}"


# Add more tests:
# - test_unicode_handling
# - test_malformed_sidecar_recovery
# - test_line_number_accuracy
# - test_mfid_updates_on_change
```

### Afternoon: test_guard.py (3 hours)

Create `tests/unit/test_guard.py`:

```python
"""Unit tests for spec_guard tool."""

import yaml
from pathlib import Path
import pytest
from tools.spec_guard.guard import validate_suite


@pytest.fixture
def valid_suite(tmp_path):
    """Create a minimal valid suite."""
    # Create docs directory
    docs_dir = tmp_path / "docs" / "source"
    docs_dir.mkdir(parents=True)
    
    # Create index directory
    index_dir = tmp_path / "docs" / ".index"
    index_dir.mkdir(parents=True)
    
    # Create sample markdown
    md_file = docs_dir / "test.md"
    content = "# Test\n\nParagraph one."
    md_file.write_text(content, encoding="utf-8")
    
    # Compute hash
    import hashlib
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    para_hash = hashlib.sha256("Paragraph one.".encode("utf-8")).hexdigest()
    
    # Create sidecar
    sidecar = {
        "file": str(md_file),
        "mfid": file_hash,
        "paragraphs": [{
            "anchor": "p-1",
            "start_line": 3,
            "end_line": 3,
            "mfid": para_hash,
            "id": "TEST-ID-001"
        }]
    }
    
    sidecar_path = md_file.with_suffix(md_file.suffix + ".sidecar.yaml")
    with open(sidecar_path, "w") as f:
        yaml.dump(sidecar, f)
    
    # Create suite index
    suite_index = {
        "suite": {
            "suite_id": "TEST-SUITE",
            "volumes": [{
                "id": "VOL-001",
                "key": "TEST",
                "sections": [{
                    "id": "SEC-001",
                    "key": "1",
                    "file": str(md_file),
                    "mfid": file_hash,
                    "paragraphs": [{
                        "id": "TEST-ID-001",
                        "anchor": "p-1",
                        "mfid": para_hash
                    }]
                }]
            }]
        }
    }
    
    index_path = index_dir / "suite-index.yaml"
    with open(index_path, "w") as f:
        yaml.dump(suite_index, f)
    
    return index_path


def test_valid_suite_passes(valid_suite, monkeypatch):
    """Valid suite produces no errors."""
    monkeypatch.chdir(valid_suite.parent.parent.parent)
    errors = validate_suite(valid_suite)
    assert len(errors) == 0


def test_missing_file_detected(valid_suite, monkeypatch):
    """Missing markdown file is detected."""
    monkeypatch.chdir(valid_suite.parent.parent.parent)
    
    # Load index and point to non-existent file
    with open(valid_suite, "r") as f:
        index = yaml.safe_load(f)
    
    index["suite"]["volumes"][0]["sections"][0]["file"] = "nonexistent.md"
    
    with open(valid_suite, "w") as f:
        yaml.dump(index, f)
    
    errors = validate_suite(valid_suite)
    assert any("missing" in err.lower() for err in errors)


def test_mfid_mismatch_detected(valid_suite, monkeypatch):
    """MFID mismatch is detected."""
    monkeypatch.chdir(valid_suite.parent.parent.parent)
    
    # Modify markdown without updating index
    with open(valid_suite, "r") as f:
        index = yaml.safe_load(f)
    
    md_path = Path(index["suite"]["volumes"][0]["sections"][0]["file"])
    md_path.write_text("# Modified content\n\nChanged.", encoding="utf-8")
    
    errors = validate_suite(valid_suite)
    assert any("mfid mismatch" in err.lower() for err in errors)


# Add more tests:
# - test_duplicate_id_detected
# - test_missing_sidecar_detected
# - test_anchor_ordering_error_detected
# - test_paragraph_count_mismatch_detected
```

### Verification
```bash
pytest tests/unit/test_indexer.py -v
pytest tests/unit/test_guard.py -v
pytest tests/unit/ --cov=tools.spec_indexer --cov=tools.spec_guard
# Target: ≥90% coverage for both modules
```

---

## Day 3: Unit Tests - Resolver, Patcher, Renderer + Infrastructure

### Morning: test_resolver.py & test_patcher.py (3 hours)

Similar pattern to Day 2 tests. Focus on:
- **Resolver:** URI parsing, lookup logic, error cases
- **Patcher:** File modification, MFID recalculation, index updates

### Afternoon: Test Infrastructure (2-3 hours)

**Create `pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=tools --cov-report=html --cov-report=term-missing --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    bdd: Behavior-driven tests
    performance: Performance benchmarks
```

**Create `tests/conftest.py`:**
```python
"""Shared test fixtures."""

import pytest
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with standard structure."""
    docs = tmp_path / "docs" / "source"
    docs.mkdir(parents=True)
    
    index_dir = tmp_path / "docs" / ".index"
    index_dir.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def sample_suite_index():
    """Return minimal suite index structure."""
    return {
        "suite": {
            "suite_id": "TEST-SUITE-001",
            "title": "Test Suite",
            "version": "1.0.0",
            "volumes": []
        }
    }
```

**Create `tests/fixtures/`:** Add sample markdown, YAML files

### Verification
```bash
pytest tests/unit/ -v --cov=tools --cov-report=term-missing
# Target: ≥85% overall coverage
```

---

## Day 4: CI Enhancement

### Update `.github/workflows/spec-ci.yml`

```yaml
name: Specification CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=tools --cov-report=xml --cov-report=term-missing --cov-fail-under=85
          
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
          
      - name: Generate sidecars
        run: |
          python -m tools.spec_indexer.indexer docs/source
          
      - name: Validate specification
        run: |
          python -m tools.spec_guard.guard
          
      - name: Render specification
        run: |
          mkdir -p build
          python -m tools.spec_renderer.renderer --output build/spec.md
          
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: specification-build
          path: build/
```

### Verification
- [ ] CI runs successfully on push
- [ ] Coverage report generated
- [ ] Build artifacts uploaded

---

## Phase 1 Gate Checklist

Before proceeding to Phase 2, verify:

- [ ] README.md complete with all sections
- [ ] requirements.txt has all dependencies
- [ ] CHANGELOG.md and LICENSE added
- [ ] test_indexer.py: ≥90% coverage, all pass
- [ ] test_guard.py: ≥90% coverage, all pass
- [ ] test_resolver.py: ≥85% coverage, all pass
- [ ] test_patcher.py: ≥85% coverage, all pass
- [ ] test_renderer.py: ≥85% coverage, all pass
- [ ] pytest.ini configured correctly
- [ ] tests/conftest.py has shared fixtures
- [ ] CI workflow updated and passing
- [ ] Overall coverage ≥85%

**Command to verify:**
```bash
pytest tests/unit/ -v --cov=tools --cov-report=term-missing --cov-fail-under=85
```

**Expected output:** All tests pass, coverage ≥85%

---

## Troubleshooting

### Coverage too low
- Add tests for error paths
- Test edge cases (empty files, malformed YAML)
- Test all public functions

### Tests failing
- Check fixture setup
- Verify temp directory cleanup
- Check monkeypatch usage

### CI failing
- Verify requirements.txt complete
- Check Python version (3.10+)
- Review GitHub Actions logs

---

## Next Steps

Once Phase 1 gate is passed:
1. Review Phase 2 plan in PRODUCTION_READINESS_PLAN.md
2. Begin BDD test implementation
3. Create example artifacts

**Phase 2 Start:** Day 5
