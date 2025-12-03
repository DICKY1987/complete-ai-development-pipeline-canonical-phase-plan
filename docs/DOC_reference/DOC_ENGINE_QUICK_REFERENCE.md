---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-ENGINE_QUICK_REFERENCE-083
---

# Engine Quick Reference

## Running Jobs

### Execute a Job
```bash
# Basic execution
python -m engine.orchestrator run-job --job-file path/to/job.json

# Example with Aider
python -m engine.orchestrator run-job --job-file schema/jobs/aider_job.example.json
```

### Job File Format
```json
{
  "job_id": "job-2025-11-21-001",
  "run_id": "run-2025-11-21",
  "workstream_id": "ws-my-feature",
  "tool": "aider",
  "command": {
    "exe": "aider",
    "args": ["--message", "Fix the bug"]
  },
  "env": {
    "OLLAMA_API_BASE": "http://127.0.0.1:11434"
  },
  "paths": {
    "repo_root": ".",
    "working_dir": ".",
    "log_file": "logs/job.log",
    "error_report": "logs/job.error.json"
  },
  "metadata": {
    "timeout_seconds": 600,
    "retry_policy": "escalate_to_codex"
  }
}
```

## Testing

### Validate Engine
```bash
# Set Python path (Windows)
$env:PYTHONPATH = (Get-Location).Path

# Run validation (7 tests)
python scripts/validate_engine.py
```

### Test State Store
```bash
# Run integration tests (6 tests)
python scripts/test_state_store.py
```

## Using State Store Programmatically

### Basic Operations
```python
from engine.state_store.job_state_store import JobStateStore

# Initialize
store = JobStateStore()

# Create run
run_id = store.create_run("ws-my-feature", metadata={"version": "1.0"})

# Get run
run = store.get_run(run_id)
print(run["status"])  # "pending"

# Update run status
store.update_run_status(run_id, "running")

# List recent runs
recent = store.list_recent_runs(limit=10)
```

### Job Tracking
```python
from engine.types import JobResult

# After job execution, update state
result = JobResult(
    exit_code=0,
    error_report_path="logs/error.json",
    duration_s=45.2,
    success=True
)

job_dict = {
    "job_id": "job-001",
    "run_id": run_id,
    "workstream_id": "ws-my-feature",
    "tool": "aider",
    # ... rest of job spec
}

store.update_job_result(job_dict, result)

# Query job status
status = store.get_job_status("job-001")  # "completed"
```

### List Jobs
```python
# Get all jobs for a run
jobs = store.list_jobs(run_id)

for job in jobs:
    print(f"{job['job_id']}: {job['status']}")
```

## Using Orchestrator Programmatically

### Basic Usage
```python
from engine.orchestrator.orchestrator import Orchestrator
from engine.state_store.job_state_store import JobStateStore

# Initialize with state store
store = JobStateStore()
orch = Orchestrator(state_store=store)

# Run job from file
result = orch.run_job("path/to/job.json")

print(f"Exit code: {result.exit_code}")
print(f"Success: {result.success}")
print(f"Duration: {result.duration_s}s")
```

### Custom State Store
```python
# Use test database
test_store = JobStateStore(db_path="state/test.db")
orch = Orchestrator(state_store=test_store)

# Jobs will be tracked in test database
result = orch.run_job("test_job.json")
```

## Creating Adapters

### Adapter Template
```python
"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: <tool_name>
VERSION: 0.1.0
"""

from engine.types import JobResult

class MyToolAdapter:
    def run_job(self, job: dict) -> JobResult:
        """Execute job and return result."""
        # 1. Build command from job spec
        command = self._build_command(job)
        
        # 2. Execute in subprocess
        result = subprocess.run(...)
        
        # 3. Return JobResult
        return JobResult(
            exit_code=result.returncode,
            error_report_path=job["paths"]["error_report"],
            duration_s=duration,
            success=(result.returncode == 0)
        )
    
    def validate_job(self, job: dict) -> bool:
        """Validate job has required fields."""
        return job.get("tool") == "mytool"
    
    def get_tool_info(self) -> dict:
        """Return tool metadata."""
        return {
            "tool": "mytool",
            "capabilities": ["capability1", "capability2"]
        }

def run_mytool_job(job: dict) -> JobResult:
    """Convenience function for orchestrator."""
    return MyToolAdapter().run_job(job)
```

### Register Adapter
```python
# In orchestrator.py
from engine.adapters.mytool_adapter import run_mytool_job

TOOL_RUNNERS = {
    "aider": run_aider_job,
    "mytool": run_mytool_job,  # Add here
}
```

## Database Schema

### Tables Used
- **runs**: Overall run tracking
- **workstreams**: Workstream management
- **step_attempts**: Job execution records (with job_id in result_json)
- **events**: Job lifecycle events
- **errors**: Error tracking

### Job Storage
Jobs are stored as `step_attempts`:
- `step_name` = tool name (e.g., "aider")
- `status` = job status (running/completed/failed/timeout)
- `result_json` = Full JobResult with job_id

### Querying Jobs
```sql
-- Find job by job_id
SELECT * FROM step_attempts 
WHERE json_extract(result_json, '$.job_id') = 'job-001';

-- List all jobs for run
SELECT * FROM step_attempts 
WHERE run_id = 'run-2025-11-21'
ORDER BY started_at DESC;
```

## File Structure

```
engine/
├── interfaces/           # Protocol definitions
├── adapters/            # Tool wrappers
│   └── aider_adapter.py
├── orchestrator/        # Job coordinator
│   ├── orchestrator.py
│   └── __main__.py
├── state_store/         # State persistence
│   └── job_state_store.py
└── types.py            # Shared types

schema/jobs/              # Job specifications
├── job.schema.json
└── aider_job.example.json

scripts/                 # Validation & testing
├── validate_engine.py
└── test_state_store.py
```

## Common Tasks

### Create a Job File
1. Copy `schema/jobs/aider_job.example.json`
2. Update job_id, run_id, workstream_id
3. Update command and args for your task
4. Set appropriate paths for logs/errors
5. Run: `python -m engine.orchestrator run-job --job-file yourjob.json`

### Debug Job Execution
1. Check orchestrator output for errors
2. View log file at `job["paths"]["log_file"]`
3. Check error report at `job["paths"]["error_report"]` if failed
4. Query state: `store.get_job(job_id)`

### Test an Adapter
1. Create minimal job JSON for your tool
2. Call adapter directly:
   ```python
   from engine.adapters.mytool_adapter import MyToolAdapter
   adapter = MyToolAdapter()
   result = adapter.run_job(job_dict)
   ```
3. Check result.exit_code and result.success
4. Validate against AdapterInterface

## Environment Setup

### Required
```bash
# Python 3.12+
python --version

# Set PYTHONPATH (Windows PowerShell)
$env:PYTHONPATH = (Get-Location).Path

# Or (bash/zsh)
export PYTHONPATH=$(pwd)
```

### Optional
```bash
# Custom database path
$env:PIPELINE_DB_PATH = "custom/path/pipeline.db"

# Ollama for AI tools
$env:OLLAMA_API_BASE = "http://127.0.0.1:11434"
```

## Troubleshooting

### "No module named 'engine'"
- Ensure PYTHONPATH includes repository root
- Run from repository root directory

### "FOREIGN KEY constraint failed"
- Ensure run and workstream exist before creating job
- Use `store.create_run()` first
- Workstreams may need manual creation in DB

### Job status shows "not_found"
- Job hasn't been updated in state store yet
- Check if job_id is correct
- Verify orchestrator completed execution

### Import errors
- Check all dependencies installed: `pip install -r requirements.txt`
- Verify Python version: 3.12+
- Run validation: `python scripts/validate_engine.py`

## Documentation

- **Architecture**: `docs/ENGINE_IMPLEMENTATION_SUMMARY.md`
- **State Integration**: `docs/PHASE_2A_COMPLETE.md`
- **GUI Development**: `docs/GUI_DEVELOPMENT_GUIDE.md`
- **Status**: `docs/ENGINE_STATUS.md`
- **Usage**: `engine/README.md`

## Support

For issues or questions:
1. Run validation scripts to verify setup
2. Check documentation in `docs/`
3. Review test files for usage examples
4. Examine existing adapters for patterns
