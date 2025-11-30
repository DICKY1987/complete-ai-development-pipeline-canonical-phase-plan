# EXACT IMPORT MAPPINGS FOR ENGINE MIGRATION
Generated: 2025-11-30 06:02:18

## Summary
- **58 files** currently import from engine modules
- **3 engine locations** with different architectures
- **Recommended**: Keep root engine/, migrate others to it OR UET

---

## CRITICAL DECISION NEEDED

You have TWO viable engines with DIFFERENT architectures:

### Option A: Use ROOT engine/ (Job Queue Architecture)
**Pros**: 
  ✅ Already in production
  ✅ Async job queue with workers
  ✅ CLI ready: python -m engine.orchestrator run-job
  ✅ StateInterface abstraction
  ✅ Priority queue, retry, dependencies

**Cons**:
  ❌ Fewer features than UET version
  ❌ No circuit breakers, resilience patterns
  ❌ No test gates, patch ledger

### Option B: Use UET engine/ (State Machine Architecture) 
**Pros**:
  ✅ Full-featured: resilience, monitoring, test gates
  ✅ State machine-based (Run/Step lifecycle)
  ✅ Circuit breakers, retry with backoff
  ✅ Patch ledger, cost tracking
  ✅ Better for complex workflows

**Cons**:
  ❌ Different architecture (not job queue)
  ❌ Requires more refactoring
  ❌ More complex

---

## IMPORT MAPPING: If Choosing ROOT engine/

### From core.engine → engine
```python
# OLD (core/engine/)
from core.engine.parallel_orchestrator import ParallelOrchestrator
from core.engine.patch_manager import PatchManager
from core.engine.adapters import ToolAdapter, ExecutionResult

# NEW (engine/)
from engine.orchestrator.orchestrator import Orchestrator
from engine.state_store.job_state_store import JobStateStore
from engine.adapters.aider_adapter import run_aider_job
from engine.types import Job, JobResult
```

### From UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine → engine
```python
# OLD (UET)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.resilience import CircuitBreaker
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.executor import Executor
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator import Orchestrator

# NEW (engine/) - REQUIRES ADDING THESE FEATURES
# Not directly mappable - UET has more features
# Would need to port: resilience/, monitoring/, test_gate, etc.
```

---

## IMPORT MAPPING: If Choosing UET engine/

### Move UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine → core/engine
```python
# Current UET tests already use:
from core.engine.resilience import CircuitBreaker, ResilientExecutor
from core.engine.monitoring import RunMonitor, ProgressTracker
from core.engine.state_machine import RunStateMachine
from core.engine.executor import Executor
from core.engine.orchestrator import Orchestrator

# These would become the canonical imports
# Root engine/ would be archived
```

---

## DETAILED FILE-BY-FILE MAPPING

### Category 1: ROOT engine/ Internal (17 files)
**Action**: No change needed - keep using engine.*

Files:
  - engine/adapters/*.py (uses engine.types, engine.interfaces)
  - engine/orchestrator/*.py (uses engine.types, engine.state_store)
  - engine/queue/*.py (uses engine.types, engine.interfaces)
  - engine/state_store/*.py (self-contained)

---

### Category 2: modules/core-engine/ Shims (11 files)
**Current**:
```python
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.{module} import *
```

**Option A** (Use root engine/):
```python
# Most don't have equivalents in root engine/
# Would need to port or remove
```

**Option B** (Use UET):
```python
# Change shims to point to core.engine instead of UET
from core.engine.{module} import *
```

---

### Category 3: Tests Using core.engine (6 files)

#### tests/test_adapters.py
**Current**:
```python
from core.engine.adapters import ToolAdapter, ExecutionResult, AiderAdapter
```
**Option A**: 
```python
from engine.adapters.aider_adapter import run_aider_job
from engine.types import JobResult
```

#### tests/test_patch_manager.py  
**Current**:
```python
from core.engine.patch_manager import PatchManager
```
**Option A**: No equivalent - archive test or port PatchManager to engine/
**Option B**: Keep as-is if moving UET to core/

---

### Category 4: UET Tests (11 files)
**Current**: All use `from core.engine.*`
```python
from core.engine.resilience import CircuitBreaker
from core.engine.monitoring import RunMonitor
from core.engine.state_machine import RunStateMachine
```

**Option A**: Port features to root engine/ or archive these tests
**Option B**: Move UET engine to core/, keep tests as-is

---

### Category 5: Scripts (4 files)

#### scripts/test_adapters.py, scripts/test_state_store.py
**Current**:
```python  
from engine.orchestrator.orchestrator import Orchestrator
```
**Action**: No change (already using root engine/)

#### scripts/uet_execute_workstreams.py
**Current**:
```python
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.dag_builder import DAGBuilder
```
**Option A**: Port DAGBuilder to engine/ or archive script
**Option B**: Change to `from core.engine.dag_builder import DAGBuilder`

---

## RECOMMENDED STRATEGY

### PHASE 1: Clarify Which Engine is Canonical

**Question to answer**: Do you want:
- **Simpler, production-ready job queue** (root engine/)
- **Full-featured execution framework** (UET engine/)

### PHASE 2A: If ROOT engine/ is canonical

1. **Keep**: root engine/ as-is
2. **Port**: UET features you need to root engine/ (circuit breakers, etc.)
3. **Archive**: 
   - core/engine/ → archive/
   - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/ → archive/
4. **Update imports**:
   - modules/core-engine/* → Delete shims or point to engine/
   - UET tests → Port needed tests to root tests/
5. **Create compatibility shim** in core/engine/__init__.py

### PHASE 2B: If UET engine/ is canonical

1. **Move**: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/ → core/engine/
2. **Archive**: 
   - Old core/engine/ → archive/
   - root engine/ → archive/ OR keep for job queue features
3. **Update imports**:
   - modules/core-engine/* shims → Point to core.engine
   - Root tests → Update to use core.engine
4. **Port**: Job queue features from root engine/ if needed

---

## NEXT STEP: YOU DECIDE

**Which architecture do you want as your canonical engine?**

A. ROOT engine/ (job queue, simpler, production-ready)
B. UET engine/ (full-featured, state machine, complex)
C. Hybrid (merge features from both)

I'll create the exact migration script once you decide.
