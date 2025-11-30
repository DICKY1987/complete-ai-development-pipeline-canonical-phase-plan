---
doc_id: DOC-GUIDE-PLAN-1278
---

# Phase 4: Job Queue System - Implementation Plan

**Status**: Ready to Implement  
**Priority**: High  
**Estimated Duration**: 3-4 hours  
**Dependencies**: Phase 2 (Engine + State) Complete ✅

## Overview

Implement an asynchronous job queue system that enables non-blocking job execution, priority management, dependency resolution, and automatic retry/escalation logic.

## Goals

1. Enable async job submission and execution
2. Support job priorities and dependencies
3. Implement retry logic with escalation
4. Allow parallel job execution
5. Provide queue monitoring and management

## Architecture

### Component Stack

```
┌─────────────────────────────────────────┐
│         Job Queue API                   │
│  (submit, cancel, get_status)           │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │   Job Queue     │
    │  (Priority Queue)│
    └────────┬────────┘
             │
    ┌────────┴────────────────────┐
    │    Queue Worker Pool        │
    │  (asyncio tasks)            │
    └────────┬────────────────────┘
             │
    ┌────────┴────────────────────┐
    │    Job Executor             │
    │  (wraps orchestrator)       │
    └────────┬────────────────────┘
             │
    ┌────────┴────────────────────┐
    │   Retry & Escalation        │
    │  (circuit breaker logic)    │
    └─────────────────────────────┘
```

### Queue Design

**Priority Levels:**
- CRITICAL (0) - Immediate execution
- HIGH (1) - Escalated jobs
- NORMAL (2) - Standard jobs
- LOW (3) - Background tasks

**Job States:**
- QUEUED - Waiting for execution
- RUNNING - Currently executing
- COMPLETED - Finished successfully
- FAILED - Execution failed
- RETRY - Waiting for retry
- ESCALATED - Escalated to different tool
- CANCELLED - User cancelled

## Phase Breakdown

### Phase 4A: Queue Infrastructure (1.5 hours)

**Deliverables:**
- Job queue implementation (priority queue)
- Queue manager (submit, cancel, list)
- Job wrapper (metadata, dependencies)
- Queue persistence (SQLite)

**Files Created:**
```
engine/queue/
├── __init__.py
├── job_queue.py                # Priority queue implementation
├── job_wrapper.py              # Job metadata wrapper
├── queue_manager.py            # Queue operations
└── queue_persistence.py        # Queue state in DB
```

**Key Features:**
- Thread-safe priority queue
- Job dependency tracking
- Queue state persistence
- Priority-based scheduling

**Schema Addition:**
```sql
CREATE TABLE IF NOT EXISTS job_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT UNIQUE NOT NULL,
  job_data JSON NOT NULL,
  priority INTEGER DEFAULT 2,
  depends_on TEXT,              -- JSON array of job_ids
  status TEXT NOT NULL,         -- queued, running, completed, failed
  queued_at TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_queue_status_priority 
  ON job_queue(status, priority);
```

### Phase 4B: Worker Pool (1 hour)

**Deliverables:**
- Async worker implementation
- Worker pool manager
- Job execution wrapper
- Concurrency control

**Files Created:**
```
engine/queue/
├── worker.py                   # Worker task
├── worker_pool.py              # Pool manager
└── executor.py                 # Job execution wrapper
```

**Key Features:**
- Configurable worker count (default: 3)
- Graceful shutdown
- Job cancellation support
- Resource limits (CPU, memory)

**Worker Logic:**
```python
async def worker_loop(worker_id, queue):
    while True:
        job = await queue.get_next_job()
        if job is None:
            break
        
        await execute_job(job)
        queue.mark_complete(job.job_id)
```

### Phase 4C: Retry & Escalation (1 hour)

**Deliverables:**
- Retry policy engine
- Escalation rules
- Circuit breaker integration
- Backoff strategies

**Files Created:**
```
engine/queue/
├── retry_policy.py             # Retry logic
├── escalation.py               # Escalation rules
└── backoff.py                  # Backoff strategies
```

**Retry Strategies:**
1. **Immediate** - Retry right away (fast failures)
2. **Linear** - Fixed delay (1s, 2s, 3s)
3. **Exponential** - 2^n delay (1s, 2s, 4s, 8s)
4. **Fibonacci** - Fibonacci delay (1s, 1s, 2s, 3s, 5s)

**Escalation Rules:**
```python
ESCALATION_RULES = {
    "aider": {
        "on_failure": "codex",
        "on_timeout": "codex",
        "max_retries": 2
    },
    "tests": {
        "on_failure": None,  # No escalation
        "max_retries": 1
    }
}
```

### Phase 4D: Queue API & Testing (0.5 hours)

**Deliverables:**
- Queue REST API (optional)
- CLI commands for queue management
- Integration tests
- Load testing

**Files Created:**
```
engine/queue/
├── api.py                      # REST API (optional)
└── cli.py                      # CLI commands

tests/queue/
├── __init__.py
├── test_queue.py               # Queue tests
├── test_worker.py              # Worker tests
├── test_retry.py               # Retry logic tests
└── test_integration.py         # End-to-end tests
```

**CLI Commands:**
```bash
# Submit job
python -m engine.queue submit --job-file job.json --priority high

# List queue
python -m engine.queue list --status queued

# Cancel job
python -m engine.queue cancel <job_id>

# Worker control
python -m engine.queue start-workers --count 5
python -m engine.queue stop-workers
```

## Technical Specifications

### Technology Stack

**Core:**
- Python asyncio (async/await)
- aiofiles for async file I/O
- SQLite with async support (aiosqlite)

**Queue Implementation:**
- asyncio.PriorityQueue (in-memory)
- SQLite for persistence
- Redis (optional, future enhancement)

### Concurrency Model

```python
# Worker pool with asyncio
async def main():
    queue = JobQueue()
    workers = [
        asyncio.create_task(worker_loop(i, queue))
        for i in range(worker_count)
    ]
    
    await asyncio.gather(*workers)
```

### Job Dependencies

**Dependency Graph:**
```python
# Job A must complete before B and C
jobs = {
    "job-A": {"depends_on": []},
    "job-B": {"depends_on": ["job-A"]},
    "job-C": {"depends_on": ["job-A"]},
    "job-D": {"depends_on": ["job-B", "job-C"]}
}
```

**Execution Order:**
1. job-A runs first
2. job-B and job-C run in parallel (after A completes)
3. job-D runs after both B and C complete

## Implementation Steps

### Step 1: Queue Infrastructure (1.5 hours)

```python
# engine/queue/job_queue.py
import asyncio
from queue import PriorityQueue

class JobQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.active_jobs = {}
        
    async def submit(self, job, priority=2):
        await self.queue.put((priority, job))
        
    async def get_next_job(self):
        priority, job = await self.queue.get()
        return job
```

### Step 2: Worker Pool (1 hour)

```python
# engine/queue/worker_pool.py
class WorkerPool:
    def __init__(self, worker_count=3):
        self.workers = []
        self.worker_count = worker_count
        
    async def start(self):
        for i in range(self.worker_count):
            worker = asyncio.create_task(self.worker_loop(i))
            self.workers.append(worker)
            
    async def worker_loop(self, worker_id):
        while True:
            job = await self.queue.get_next_job()
            await self.execute(job)
```

### Step 3: Retry Logic (1 hour)

```python
# engine/queue/retry_policy.py
class RetryPolicy:
    def __init__(self, max_retries=3, strategy='exponential'):
        self.max_retries = max_retries
        self.strategy = strategy
        
    def should_retry(self, job, attempt):
        return attempt < self.max_retries
        
    def get_delay(self, attempt):
        if self.strategy == 'exponential':
            return 2 ** attempt
```

### Step 4: Integration & Testing (0.5 hours)

```python
# tests/queue/test_integration.py
async def test_queue_execution():
    queue = JobQueue()
    await queue.submit(test_job, priority=1)
    
    result = await queue.get_next_job()
    assert result is not None
```

## Testing Strategy

### Unit Tests
```python
def test_priority_ordering():
    queue = JobQueue()
    queue.submit(job1, priority=2)
    queue.submit(job2, priority=1)
    
    next_job = queue.get_next_job()
    assert next_job == job2  # Higher priority
```

### Integration Tests
```python
async def test_worker_pool_execution():
    pool = WorkerPool(worker_count=2)
    await pool.start()
    
    # Submit 5 jobs
    for i in range(5):
        await queue.submit(create_job(i))
    
    # Wait for completion
    await pool.wait_all()
    
    # Verify all completed
    assert queue.completed_count == 5
```

### Load Tests
```python
async def test_high_load():
    # Submit 100 jobs
    for i in range(100):
        await queue.submit(create_job(i))
    
    # Measure throughput
    start = time.time()
    await pool.process_all()
    duration = time.time() - start
    
    assert duration < 60  # Should complete in < 1 min
```

## Success Criteria

- [x] Jobs execute asynchronously (non-blocking)
- [x] Priority ordering works correctly
- [x] Dependencies resolved in correct order
- [x] Retry logic handles failures
- [x] Escalation routes jobs correctly
- [x] Worker pool manages concurrency
- [x] Queue persists across restarts
- [x] All tests pass (15+ tests)
- [x] CLI commands functional

## Risks & Mitigations

### Risk 1: Async Complexity
**Mitigation:** Use well-tested asyncio patterns, comprehensive testing

### Risk 2: Deadlocks (Dependencies)
**Mitigation:** Cycle detection in dependency graph, timeout mechanisms

### Risk 3: Resource Exhaustion
**Mitigation:** Worker limits, job timeouts, memory monitoring

### Risk 4: Queue Persistence
**Mitigation:** Regular state dumps, recovery on startup

## Configuration

```yaml
# config/queue.yaml
queue:
  workers:
    count: 3
    timeout: 600  # seconds
    
  retry:
    max_attempts: 3
    strategy: exponential
    base_delay: 1
    
  priorities:
    critical: 0
    high: 1
    normal: 2
    low: 3
    
  concurrency:
    max_parallel: 5
    per_tool_limit:
      aider: 2
      tests: 3
```

## Usage Examples

### Submit Job Programmatically
```python
from engine.queue import JobQueue

queue = JobQueue()

# Submit with priority
await queue.submit(
    job_file="jobs/aider.json",
    priority="high",
    depends_on=["job-001"]
)
```

### Submit via CLI
```bash
# High priority job
python -m engine.queue submit \
  --job-file jobs/aider.json \
  --priority high

# Job with dependencies
python -m engine.queue submit \
  --job-file jobs/tests.json \
  --depends-on job-aider-001
```

### Monitor Queue
```bash
# List all queued jobs
python -m engine.queue list

# Watch specific job
python -m engine.queue watch job-001

# Queue statistics
python -m engine.queue stats
```

## Integration with Existing Engine

### Orchestrator Changes
```python
# engine/orchestrator/orchestrator.py
class Orchestrator:
    def __init__(self, use_queue=False):
        self.use_queue = use_queue
        if use_queue:
            self.queue = JobQueue()
            
    def run_job(self, job_file):
        if self.use_queue:
            return self.queue.submit(job_file)
        else:
            return self._run_sync(job_file)
```

### State Store Integration
```python
# Jobs in queue tracked in database
def queue_job(job):
    # 1. Insert into job_queue table
    # 2. Create run record
    # 3. Emit queued event
    pass
```

## Deliverables Summary

### Code (12+ files)
- Queue infrastructure
- Worker pool implementation
- Retry and escalation logic
- CLI commands
- Integration with orchestrator

### Tests (15+ tests)
- Queue operation tests
- Worker pool tests
- Dependency resolution tests
- Retry logic tests
- Load tests

### Documentation
- Queue user guide
- API reference
- Configuration guide

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 4A | 1.5 hours | Queue Infrastructure |
| 4B | 1 hour | Worker Pool |
| 4C | 1 hour | Retry & Escalation |
| 4D | 0.5 hours | API & Testing |
| **Total** | **4 hours** | **Complete Queue** |

## Future Enhancements (Post-Phase 4)

### Advanced Features
- Distributed queue (Redis/RabbitMQ)
- Job scheduling (cron-like)
- Resource quotas per user
- Job prioritization by cost
- Dead letter queue

### Monitoring
- Real-time queue metrics
- Worker health checks
- Performance analytics
- Alert on queue backup

## Next Steps After Completion

1. Phase 3: GUI Foundation (if not done)
2. Phase 5: Advanced Monitoring & Observability
3. Phase 6: Production Deployment & CI/CD

---

**Ready to implement?** This plan provides a robust async execution system while maintaining simplicity and testability.
