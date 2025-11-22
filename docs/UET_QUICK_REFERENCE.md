# UET Integration Quick Reference

**Last Updated**: 2025-11-22  
**Integration Status**: Phase 1 - Foundation (Week 1)  
**Risk Level**: Low (Additive changes only)  

---

## 🚀 Quick Start

### Bootstrap a Project

```bash
# Bootstrap current project
python scripts/bootstrap_uet.py .

# Bootstrap specific project
python scripts/bootstrap_uet.py /path/to/project

# Validate existing artifacts
python scripts/bootstrap_uet.py --validate-only
```

### Generated Files

After bootstrap, you'll have:
- `PROJECT_PROFILE.yaml` - Auto-detected project configuration
- `router_config.json` - Tool routing and capabilities
- `.uet/` directory - UET runtime files

---

## 📚 What's Integrated

### Week 1: Foundation ✅

| Component | Purpose | Status |
|-----------|---------|--------|
| **Bootstrap System** | Auto-project configuration | ✅ Integrated |
| **Resilience Module** | Circuit breakers & retry | ✅ Copied |
| **Progress Tracking** | Real-time monitoring | ✅ Copied |
| **Database Extension** | Workers, events, cost tables | ✅ Migration ready |
| **Schemas** | Project profile, router config | ✅ Added |

### Upcoming Weeks

| Week | Focus | Status |
|------|-------|--------|
| Week 2 | Resilience integration | ⏳ Planned |
| Week 3 | Progress tracking | ⏳ Planned |
| Week 4 | Testing & validation | ⏳ Planned |

---

## 🔧 Module Locations

```
core/
├── bootstrap_uet/              # UET Bootstrap System
│   ├── discovery.py           # Project scanner
│   ├── selector.py            # Profile selector
│   ├── generator.py           # Artifact generator
│   ├── validator.py           # Bootstrap validator
│   └── orchestrator.py        # Bootstrap orchestrator
│
├── engine/
│   ├── resilience/            # UET Resilience Patterns
│   │   ├── circuit_breaker.py # Circuit breaker implementation
│   │   ├── retry.py           # Retry logic with backoff
│   │   └── resilient_executor.py # Main executor
│   │
│   └── monitoring/            # UET Progress Tracking
│       ├── progress_tracker.py # Task progress tracking
│       └── run_monitor.py     # Run-level monitoring
│
schema/
├── project_profile.v1.json    # Project profile schema
├── router_config.v1.json      # Router config schema
└── migrations/
    └── 002_uet_foundation.sql # UET database migration

profiles/
├── software-dev-python/       # Python development profile
├── data-pipeline/             # Data/ML pipeline profile
├── documentation/             # Documentation project profile
├── operations/                # DevOps/SRE profile
└── generic/                   # Fallback profile
```

---

## 📖 Usage Examples

### Bootstrap Integration

```python
from core.bootstrap_uet import bootstrap_project

# Bootstrap with defaults
result = bootstrap_project()

if result['success']:
    print(f"Domain: {result['domain']}")
    print(f"Profile: {result['profile_id']}")
    print(f"Files: {result['generated_files']}")
```

### Resilience (Week 2 - Coming Soon)

```python
from core.engine.resilience import ResilientExecutor

executor = ResilientExecutor()
executor.register_tool("aider", max_retries=3, failure_threshold=5)

def risky_operation():
    # Your tool invocation
    return invoke_aider(...)

result = executor.execute("aider", risky_operation)
```

### Progress Tracking (Week 3 - Coming Soon)

```python
from core.engine.monitoring import ProgressTracker

tracker = ProgressTracker("run-123", total_tasks=10)
tracker.start()

for task in tasks:
    tracker.start_task(task.id)
    # Execute task
    tracker.complete_task(task.id, duration=5.2)

snapshot = tracker.get_snapshot()
print(f"Progress: {snapshot.completion_percent}%")
```

---

## 🗄️ Database Schema Extensions

### New Tables

**workers** - Tool adapter instance tracking
```sql
worker_id (PK) | adapter_type | state | current_task_id | heartbeat_at | spawned_at
```

**events** - Centralized event logging
```sql
id (PK) | event_type | worker_id | task_id | timestamp | payload
```

**cost_tracking** - Token usage and API costs
```sql
id (PK) | step_id | worker_id | input_tokens | output_tokens | cost_usd | timestamp
```

### Apply Migration

```bash
# Apply to main database
sqlite3 .worktrees/pipeline_state.db < schema/migrations/002_uet_foundation.sql

# Verify
sqlite3 .worktrees/pipeline_state.db "SELECT name FROM sqlite_master WHERE type='table';"
```

---

## 🧪 Testing

### Run Integration Tests

```bash
# All UET integration tests
pytest tests/uet_integration/ -v

# Bootstrap tests only
pytest tests/uet_integration/test_bootstrap.py -v

# Verify no regressions
pytest tests/ -v
```

### Manual Testing

```bash
# 1. Bootstrap current project
python scripts/bootstrap_uet.py .

# 2. Check generated files
cat PROJECT_PROFILE.yaml
cat router_config.json

# 3. Validate
python scripts/bootstrap_uet.py --validate-only

# 4. Check database
sqlite3 .worktrees/pipeline_state.db "SELECT * FROM workers LIMIT 5;"
```

---

## 📋 Project Profiles

UET auto-detects your project type and applies appropriate configuration:

### Software Dev (Python)
- **Detects**: `pyproject.toml`, `setup.py`, `.py` files
- **Tools**: pytest, ruff, mypy, aider
- **Constraints**: Tests must pass, patch-only mode

### Data Pipeline
- **Detects**: `dags/`, `pipelines/`, Jupyter notebooks
- **Tools**: pytest, pandas, dbt
- **Constraints**: Data validation, schema checks

### Documentation
- **Detects**: `docs/`, `.md` files, `mkdocs.yml`
- **Tools**: markdownlint, link checker
- **Constraints**: Link validation, format checks

### Operations
- **Detects**: `ansible/`, `terraform/`, `.tf` files
- **Tools**: ansible-lint, terraform validate
- **Constraints**: Dry-run validation, approval gates

### Generic (Fallback)
- **Detects**: Any project
- **Tools**: Universal tools (git, linters)
- **Constraints**: Minimal, project-agnostic

---

## ⚙️ Configuration

### PROJECT_PROFILE.yaml

Auto-generated project configuration:

```yaml
project_id: "my-pipeline"
project_name: "AI Development Pipeline"
domain: "software-dev"
profile_id: "software-dev-python"

available_tools:
  - tool_id: "aider"
    command: "aider"
    capabilities: ["code_edit", "refactor"]
  
  - tool_id: "pytest"
    command: "pytest"
    capabilities: ["testing"]

framework_paths:
  tasks_dir: ".tasks"
  ledger_dir: ".ledger"
  worktrees_dir: ".worktrees"

constraints:
  patch_only: true
  tests_must_pass: true
  max_lines_changed: 500
```

### router_config.json

Tool routing configuration:

```json
{
  "adapters": [
    {
      "adapter_id": "aider",
      "type": "subprocess",
      "command": "aider",
      "capabilities": ["code_edit", "refactor"],
      "timeout": 300
    }
  ],
  "routing_rules": [
    {
      "task_kind": "code_edit",
      "domain": "python",
      "preferred_adapters": ["aider"]
    }
  ]
}
```

---

## 🔍 Troubleshooting

### Bootstrap Fails

**Symptom**: `bootstrap_project()` returns `success: False`

**Solutions**:
1. Check UET framework is accessible:
   ```bash
   ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
   ```

2. Run with verbose output:
   ```bash
   python scripts/bootstrap_uet.py . --verbose
   ```

3. Check project structure:
   ```bash
   # Should have indicators like .git/, pyproject.toml, etc.
   ls -la
   ```

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'core.bootstrap_uet'`

**Solutions**:
1. Verify files copied:
   ```bash
   ls core/bootstrap_uet/
   ```

2. Check Python path:
   ```python
   import sys
   print('\n'.join(sys.path))
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

### Migration Errors

**Symptom**: Migration fails with "table already exists"

**Solutions**:
```sql
-- Check existing tables
SELECT name FROM sqlite_master WHERE type='table';

-- Migration is idempotent (safe to re-run)
-- Uses CREATE TABLE IF NOT EXISTS
```

---

## 📊 Success Metrics

### Week 1 Goals

- [x] UET modules integrated (bootstrap, resilience, monitoring)
- [x] Schemas added (project profile, router config)
- [x] Database extended (workers, events, cost_tracking)
- [x] Bootstrap CLI working
- [x] Tests passing (integration tests green)
- [ ] Zero regressions (all existing tests pass)

### Measurement

```bash
# Check integration completeness
pytest tests/uet_integration/ -v --tb=short

# Verify no regressions
pytest tests/ -v

# Bootstrap success rate
python scripts/bootstrap_uet.py . && echo "✅ Success"
```

---

## 📚 Documentation

### Design Documents
- [UET_INTEGRATION_DESIGN.md](UET_INTEGRATION_DESIGN.md) - Complete design
- [UET_WEEK1_IMPLEMENTATION.md](UET_WEEK1_IMPLEMENTATION.md) - Week 1 plan

### UET Framework Specs
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/README.md` - UET overview
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/STATUS.md` - UET progress
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/UET_BOOTSTRAP_SPEC.md` - Bootstrap spec

### Future Documentation (Coming)
- `docs/UET_BOOTSTRAP_GUIDE.md` - User guide (Week 2)
- `docs/UET_RESILIENCE_CONFIG.md` - Resilience config (Week 2)
- `docs/UET_MONITORING_GUIDE.md` - Monitoring usage (Week 3)

---

## 🚦 Next Steps

### Immediate (Week 1)
1. ✅ Copy UET modules to pipeline
2. ✅ Add schemas and profiles
3. ✅ Create database migration
4. ✅ Test bootstrap on pipeline itself
5. ⏳ Run full test suite

### Week 2: Resilience
1. Wrap tool invocations with `ResilientExecutor`
2. Configure circuit breakers per tool
3. Add health monitoring CLI
4. Test fault tolerance

### Week 3: Progress Tracking
1. Instrument orchestrator with `ProgressTracker`
2. Add progress snapshots
3. Create real-time monitor CLI
4. Gather baseline metrics

### Week 4: Validation
1. Integration tests for all components
2. Performance benchmarking
3. Documentation updates
4. Phase 2 planning (if proceeding)

---

## 🆘 Support

### Questions?
- Check [UET_INTEGRATION_DESIGN.md](UET_INTEGRATION_DESIGN.md) for detailed design
- See [UET_WEEK1_IMPLEMENTATION.md](UET_WEEK1_IMPLEMENTATION.md) for step-by-step guide
- Review UET framework docs in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/`

### Issues?
- Check [Troubleshooting](#troubleshooting) section above
- Review integration tests: `tests/uet_integration/`
- File issue with error details

---

**Current Status**: Week 1 Foundation - Ready to implement  
**Next Milestone**: Week 2 Resilience Integration  
**Integration Risk**: ✅ Low (additive changes only)
