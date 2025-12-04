---
doc_id: DOC-GUIDE-QUICK-START-393
---

# Quick Start Guide

> **Purpose**: Fast entry points for common tasks
> **Last Updated**: 2025-11-22
> **Audience**: New contributors and AI tools

---

## 🚀 First-Time Setup

### Prerequisites
- Python 3.8+ installed
- PowerShell (`pwsh`) for Windows users
- Git configured

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan.git
cd complete-ai-development-pipeline-canonical-phase-plan

# 2. Create virtual environment (recommended)
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Bootstrap environment
pwsh ./scripts/bootstrap.ps1  # Windows
# OR
bash ./scripts/bootstrap.sh   # Linux/Mac (if available)

# 5. Run tests to verify setup
pytest -q
```

---

## 📖 I Want To...

### Understand the Repository

**Read these in order**:
1. [README.md](README.md) - Overview and status
2. [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) - Navigation and structure
3. [AGENTS.md](AGENTS.md) - Coding conventions
4. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

**For AI tools**: Start with [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) to understand section priorities.

### Run Tests

```bash
# All tests
pytest -q

# Specific test file
pytest tests/pipeline/test_orchestrator_single.py -v

# With coverage
pytest --cov=core --cov=engine --cov=error

# CI-friendly run
pwsh ./scripts/test.ps1
```

### Work with Workstreams

#### Validate Workstreams
```bash
python ./scripts/validate_workstreams.py
python ./scripts/validate_workstreams_authoring.py
```

#### Run a Workstream
```bash
python ./scripts/run_workstream.py --ws-id ws-001
```

#### Create from OpenSpec
```bash
# Interactive mode
python scripts/spec_to_workstream.py --interactive

# Direct conversion
python scripts/spec_to_workstream.py --change-id <id>
```

**Learn more**: [workstreams/README.md](workstreams/README.md)

### Work with the Engine

#### Validate Engine
```bash
python scripts/validate_engine.py
```

#### Run a Job
```bash
python -m engine.orchestrator run-job --job-file schema/jobs/aider_job.example.json
```

**Learn more**: [engine/README.md](engine/README.md)

### Run Error Detection

```bash
python ./scripts/run_error_engine.py
```

**Learn more**: [error/README.md](error/README.md)

### Generate Indices

After changing specifications:

```bash
python ./scripts/generate_spec_index.py
python ./scripts/generate_spec_mapping.py
```

### Add New Code

#### Where to Add It

| What You're Adding | Where It Goes | Example Import |
|-------------------|---------------|----------------|
| State management | `core/state/` | `from core.state.db import init_db` |
| Orchestration logic | `core/engine/` | `from core.engine.orchestrator import Orchestrator` |
| Error detection | `error/engine/` | `from error.engine.error_engine import ErrorEngine` |
| Detection plugin | `error/plugins/<name>/` | `from error.plugins.python_ruff.plugin import parse` |
| Spec content | `specifications/content/` | - |
| Tests | `tests/` | - |
| Scripts | `scripts/` | - |
| Documentation | `docs/` | - |

**Learn more**: [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md#finding-what-you-need)

#### Coding Conventions

- **Python**: 4-space indent, Black/PEP8, snake_case
- **Markdown**: One H1, sentence-case headings, ~100 char wrap
- **YAML/JSON**: 2-space indent, kebab-case keys
- **Files**: Descriptive, scope-first names

**Learn more**: [AGENTS.md](AGENTS.md)

### Contribute

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes** following conventions in [AGENTS.md](AGENTS.md)
4. **Write tests** in appropriate `tests/` subdirectory
5. **Run tests**: `pytest -q`
6. **Validate**: Run applicable validation scripts
7. **Commit**: Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
8. **Push**: `git push origin feature/my-feature`
9. **Create Pull Request** with clear description

**PR Checklist**:
- [ ] Tests pass
- [ ] Code follows conventions
- [ ] Documentation updated
- [ ] No deprecated imports (CI will check)
- [ ] Changelog entry (if applicable)

---

## 🎯 Common Tasks by Role

### For Developers

**Adding a feature**:
1. Check [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) for where it belongs
2. Read section README (e.g., [core/README.md](core/README.md))
3. Write tests first (`tests/`)
4. Implement feature
5. Run tests: `pytest -q`
6. Commit with conventional commits

**Fixing a bug**:
1. Write failing test
2. Fix the bug
3. Verify test passes
4. Check for regressions: `pytest -q`
5. Commit fix

### For Documentation Writers

**Adding documentation**:
1. Choose appropriate location:
   - Architecture → `docs/`
   - Section-specific → `<section>/README.md`
   - Guides → `docs/guides/` (if exists)
2. Follow markdown conventions (see [AGENTS.md](AGENTS.md))
3. Add metadata header (purpose, last updated, related docs)
4. Cross-reference with [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md)

**Updating existing docs**:
1. Update content
2. Update "Last Updated" date
3. Check internal links
4. Regenerate indices if needed

### For AI Tools

**Understanding the codebase**:
1. Start with [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md)
2. Check `.aicontext` files in each directory
3. Focus on HIGH priority sections:
   - `core/` - Core business logic
   - `engine/` - Alternative execution
   - `error/` - Error detection
   - `specifications/` - Specs
   - `tests/` - Behavior validation

**Making changes**:
1. Use section-based imports (see [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md#import-path-rules))
2. Follow conventions in [AGENTS.md](AGENTS.md)
3. Exclude runtime artifacts (see `.gitignore`)
4. Reference `.aicontext` for section guidance

**Validating changes**:
1. Run applicable tests
2. Run validation scripts
3. Check for deprecated imports (CI enforced)

---

## 📚 Documentation Index

### Essential Reading
- [README.md](README.md) - Main overview
- [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) - Navigation
- [AGENTS.md](AGENTS.md) - Conventions

### Architecture
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md) - Import paths
- [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) - CI enforcement

### Section Guides
- [core/README.md](core/README.md) - Core pipeline
- [engine/README.md](engine/README.md) - Job engine
- [error/README.md](error/README.md) - Error detection
- [specifications/README.md](specifications/README.md) - Specs
- [scripts/README.md](scripts/README.md) - Scripts
- [schema/README.md](schema/README.md) - Schemas
- [workstreams/README.md](workstreams/README.md) - Workstreams

### Workflow Guides
- [docs/QUICKSTART_OPENSPEC.md](docs/QUICKSTART_OPENSPEC.md) - OpenSpec workflow
- [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md) - Configuration
- [docs/COORDINATION_GUIDE.md](docs/COORDINATION_GUIDE.md) - Multi-agent coordination

---

## 🆘 Troubleshooting

### Tests Failing

**Module not found errors**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Import errors**:
- Check you're using section-based imports (not deprecated paths)
- See [docs/SECTION_REFACTOR_MAPPING.md](docs/SECTION_REFACTOR_MAPPING.md)

### Script Not Running

**PowerShell execution policy** (Windows):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Permission denied** (Linux/Mac):
```bash
chmod +x ./scripts/script_name.sh
```

### CI Failures

**Deprecated import paths**:
- See error message for specific violations
- Update to section-based imports
- See [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md)

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Repository** | [GitHub](https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan) |
| **Issues** | [GitHub Issues](https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan/issues) |
| **CI Status** | [Actions](https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan/actions) |

---

**Last Updated**: 2025-11-22
**For Questions**: See [AGENTS.md](AGENTS.md) for contribution guidelines
