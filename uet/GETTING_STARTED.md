---
doc_id: DOC-GUIDE-GETTING-STARTED-749
---

# Getting Started with UET

Quick navigation guide for common tasks. Choose your path below.

## I want to...

### 🚀 Bootstrap a new project

**Quick start:**
```bash
python core/bootstrap/orchestrator.py /path/to/project
```

**With specific profile:**
```bash
python core/bootstrap/orchestrator.py /path/to/project --profile software-dev-python
```

**Learn more:**
- Read: `specs/UET_BOOTSTRAP_SPEC.md`
- See: `core/bootstrap/README.md`
- Example: `profiles/software-dev-python/`

---

### 🏗️ Understand the architecture

**Entry points:**
- Read: `ARCHITECTURE.md` - System overview and mental model
- See: `DEPENDENCIES.md` - Dependency graph and layers
- Check: `README.md` - Feature overview

**Deep dive:**
- Specs: `specs/UET_PHASE_SPEC_MASTER.md`
- Status: `specs/STATUS.md`

---

### 🔧 Add a new tool adapter

**Steps:**
1. Read: `core/adapters/README.md`
2. Copy template: `core/adapters/subprocess_adapter.py`
3. Implement: `execute()` method
4. Register: Add to `router_config.json`
5. Test: Add tests in `tests/adapters/`

**Example:**
```python
from core.adapters.base import ToolAdapter

class MyToolAdapter(ToolAdapter):
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        # Your implementation
        pass
```

---

### 📋 Create a custom profile

**Steps:**
1. Read: `profiles/README.md`
2. Copy template: `profiles/generic/`
3. Create: `profiles/my-profile/`
4. Define: `profile.json` and `router_config.json`
5. Document: Add `README.md`

**Profile structure:**
```
profiles/my-profile/
├── profile.json           # Metadata
├── router_config.json     # Tool routing
├── phases/               # Phase definitions
└── README.md             # Usage guide
```

**Learn more:**
- Examples: `profiles/software-dev-python/`
- Schema: `schema/profile.v1.json`

---

### ✅ Run tests

**All tests:**
```bash
pytest tests/ -v
```

**Specific module:**
```bash
pytest tests/bootstrap/ -v
pytest tests/engine/ -v
pytest tests/adapters/ -v
```

**With coverage:**
```bash
pytest tests/ --cov=core --cov-report=html
open htmlcov/index.html
```

**Single test:**
```bash
pytest tests/engine/test_scheduler.py::test_topological_sort -v
```

---

### 🔍 Explore the codebase

**Directory guide:**
```
core/                    # Implementation
├── bootstrap/          # Project discovery
├── engine/            # Orchestration
│   ├── monitoring/    # Progress tracking
│   └── resilience/    # Fault tolerance
├── adapters/          # Tool integration
└── state/             # State management

specs/                  # Documentation
schema/                 # JSON schemas
profiles/              # Project templates
tests/                 # Test suites
```

**Key files:**
- `core/bootstrap/orchestrator.py` - Main entry point
- `core/engine/scheduler.py` - Task scheduling
- `core/engine/resilience/executor.py` - Resilient execution
- `core/adapters/registry.py` - Adapter registry

---

### 📊 Monitor execution progress

**Programmatic:**
```python
from core.engine.monitoring import ProgressTracker

tracker = ProgressTracker("run-123", total_tasks=10)
tracker.start()

# During execution
tracker.start_task("task-1")
tracker.update_task_progress(50.0)
tracker.complete_task("task-1", duration=5.2)

# Get snapshot
snapshot = tracker.get_snapshot()
print(f"Progress: {snapshot.completion_percent}%")
print(f"ETA: {snapshot.estimated_completion}")
```

**Learn more:**
- See: `core/engine/monitoring/README.md`
- API: `core/engine/monitoring/progress.py`

---

### 🛠️ Debug execution issues

**Check run state:**
```python
from core.state import RunManager

manager = RunManager()
run = manager.get_run("run-123")
print(f"Status: {run.status}")
print(f"Tasks: {run.completed_tasks}/{run.total_tasks}")
```

**View audit trail:**
```bash
# Audit logs stored in JSONL format
cat logs/run-123.jsonl | jq .
```

**Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Learn more:**
- State: `core/state/README.md`
- Resilience: `core/engine/resilience/README.md`

---

### 📚 Understand schemas

**Schema catalog:**
- See: `schema/README.md`
- Validate: `python -m jsonschema -i data.json schema/task_spec.v1.json`

**Key schemas:**
- `task_spec.v1.json` - Task definitions
- `phase_spec.v1.json` - Phase structure
- `execution_request.v1.json` - Tool execution
- `profile.v1.json` - Project profiles

---

### 🔄 Work with state and checkpoints

**Checkpoints:**
```python
from core.state import CheckpointManager

manager = CheckpointManager()

# Create checkpoint
checkpoint_id = manager.create_checkpoint(run_id, state_data)

# Restore from checkpoint
state = manager.restore_checkpoint(checkpoint_id)
```

**State transitions:**
- See: `ARCHITECTURE.md` (State Management section)
- Spec: `specs/UET_PHASE_SPEC_MASTER.md`

---

### 🧪 Validate workstreams

**Run validation:**
```bash
python scripts/validate_workstreams.py
```

**Check ACS conformance:**
```bash
python scripts/validate_acs_conformance.py
```

**Check import paths (CI gate):**
```bash
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

---

### 🤝 Understand multi-agent coordination

**Cooperation spec:**
- Read: `specs/UET_COOPERATION_SPEC.md`
- Learn: How multiple AI agents coordinate
- See: Boss program pattern

---

### 📖 Read full documentation

**Specifications (in order):**
1. `specs/UET_BOOTSTRAP_SPEC.md` - Start here
2. `specs/UET_TASK_ROUTING_SPEC.md` - Task routing
3. `specs/UET_PHASE_SPEC_MASTER.md` - Phase structure
4. `specs/UET_WORKSTREAM_SPEC.md` - Workstreams
5. `specs/UET_COOPERATION_SPEC.md` - Multi-agent
6. `specs/UET_PATCH_MANAGEMENT_SPEC.md` - Patch handling
7. `specs/UET_PROMPT_RENDERING_SPEC.md` - Prompt generation

**Progress:**
- Current status: `specs/STATUS.md`
- Phase 3 completion: `specs/PHASE_3_COMPLETION_REPORT.md`
- Phase 4 plan: `specs/PHASE_4_AI_ENHANCEMENT_PLAN.md`

---

## Quick Reference Commands

```bash
# Bootstrap
python core/bootstrap/orchestrator.py /path/to/project

# Tests
pytest tests/ -v
pytest tests/engine/ -k scheduler

# Coverage
pytest tests/ --cov=core --cov-report=html

# Validation
python scripts/validate_workstreams.py
python scripts/validate_acs_conformance.py

# Path check (CI)
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Schema validation
python -m jsonschema -i data.json schema/task_spec.v1.json
```

---

## Common Patterns

### Pattern: Execute a workflow
```python
from core import BootstrapOrchestrator, ExecutionScheduler, ResilientExecutor

# 1. Bootstrap project
bootstrap = BootstrapOrchestrator("/path/to/project")
profile = bootstrap.run()

# 2. Define tasks
tasks = [
    Task('analyze', 'analysis'),
    Task('implement', 'code_edit', depends_on=['analyze']),
    Task('test', 'testing', depends_on=['implement'])
]

# 3. Schedule
scheduler = ExecutionScheduler()
scheduler.add_tasks(tasks)
order = scheduler.get_execution_order()

# 4. Execute with resilience
executor = ResilientExecutor()
executor.register_tool("aider", max_retries=3)
for task in order:
    result = executor.execute(task.tool, lambda: task.run())
```

### Pattern: Add custom tool
```python
# 1. Implement adapter
class MyToolAdapter(ToolAdapter):
    def execute(self, request):
        # Tool execution logic
        return ExecutionResult(...)

# 2. Register in router_config.json
{
    "tools": {
        "my_tool": {
            "adapter_type": "custom",
            "adapter_class": "MyToolAdapter",
            "capabilities": {
                "domains": ["python"],
                "actions": ["analyze"]
            }
        }
    }
}

# 3. Use in workflow
adapter = registry.get('my_tool')
result = adapter.execute(request)
```

---

## Help & Support

- **Questions**: Check `specs/` directory first
- **Issues**: Review `specs/STATUS.md` for known issues
- **Architecture**: See `ARCHITECTURE.md`
- **Dependencies**: See `DEPENDENCIES.md`

---

**Built with Python 3.8+ • Production-ready orchestration • 196/196 tests passing**
