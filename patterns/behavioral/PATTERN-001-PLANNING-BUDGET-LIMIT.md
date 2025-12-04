---
doc_id: DOC-PAT-BEHAVIOR-001-894
pattern_id: PATTERN-001
version: 1.0.0
status: active
created: 2025-12-04
category: behavioral
priority: high
---

# PATTERN-001: Planning Budget Limit

## Overview

**Pattern Name**: Planning Budget Limit
**Problem**: Planning loops consuming time without execution (meta-work loops)
**Solution**: Strict limit on planning iterations before forcing execution
**Impact**: Prevents 4 wasted cycles, saves 30-60s per incident

---

## Problem Statement

### Observed Behavior
```
Lines 45-47, 74-76, 108-110, 126-128:
Pattern: update_plan called multiple times without concrete actions
- Planning iteration 1
- Planning iteration 2
- Planning iteration 3
- Planning iteration 4
... still no execution

Result: 2-4 minutes of meta-work, zero progress
```

### Root Cause
Unbounded planning iterations:
- No limit on how many times plan can be updated
- No forcing function to move from planning to execution
- AI agents caught in "thinking about thinking" loops
- No progress tracking (planning vs execution ratio)

### Cost
- **4 incidents** observed (4% of errors)
- **30-60 seconds wasted** per planning loop
- **User frustration** from apparent lack of progress
- **Opportunity cost**: Could have executed and learned faster

---

## Solution Pattern

### Core Principle
**Limit planning iterations to 2, then force execution (fail fast, learn fast)**

### Implementation

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class PlanUpdate:
    """Record of a planning iteration"""
    timestamp: datetime
    description: str
    iteration_number: int


class PlanningBudget:
    """PATTERN-001: Enforce planning budget limit"""

    MAX_PLAN_UPDATES = 2

    def __init__(self):
        self.plan_count = 0
        self.execution_count = 0
        self.plan_history: list[PlanUpdate] = []

    def update_plan(self, plan_description: str) -> None:
        """Update plan with budget enforcement"""
        self.plan_count += 1

        # Record update
        self.plan_history.append(PlanUpdate(
            timestamp=datetime.now(),
            description=plan_description,
            iteration_number=self.plan_count
        ))

        # Enforce budget
        if self.plan_count > self.MAX_PLAN_UPDATES:
            raise RuntimeError(
                f"PLANNING_LOOP: {self.plan_count} plan updates without execution.\n"
                f"Max allowed: {self.MAX_PLAN_UPDATES}\n"
                f"ACTION REQUIRED: Stop planning and start executing.\n"
                f"You can refine the plan AFTER seeing real results."
            )

    def record_execution(self, description: str = "") -> None:
        """Record actual execution (resets planning budget)"""
        self.execution_count += 1
        self.plan_count = 0  # Reset budget on execution
        self.plan_history.clear()

    def get_stats(self) -> dict:
        """Get planning vs execution statistics"""
        total = self.plan_count + self.execution_count
        return {
            "plan_iterations": self.plan_count,
            "executions": self.execution_count,
            "total_actions": total,
            "planning_ratio": self.plan_count / total if total > 0 else 0,
            "current_streak": "planning" if self.plan_count > 0 else "executing"
        }

    def is_planning_heavy(self, threshold: float = 0.5) -> bool:
        """Check if spending too much time planning vs executing"""
        stats = self.get_stats()
        return stats["planning_ratio"] > threshold


class SessionBudget:
    """PATTERN-001: Track planning budget across entire session"""

    MAX_SESSION_PLANNING_RATIO = 0.3  # 30% planning, 70% execution

    def __init__(self):
        self.total_planning_time = 0.0
        self.total_execution_time = 0.0
        self.current_budget = PlanningBudget()

    def start_planning(self) -> None:
        """Start planning timer"""
        self._planning_start = datetime.now()

    def end_planning(self, description: str) -> None:
        """End planning timer and update budget"""
        if hasattr(self, '_planning_start'):
            duration = (datetime.now() - self._planning_start).total_seconds()
            self.total_planning_time += duration
            delattr(self, '_planning_start')

        self.current_budget.update_plan(description)

    def start_execution(self) -> None:
        """Start execution timer"""
        self._execution_start = datetime.now()

    def end_execution(self, description: str = "") -> None:
        """End execution timer and reset budget"""
        if hasattr(self, '_execution_start'):
            duration = (datetime.now() - self._execution_start).total_seconds()
            self.total_execution_time += duration
            delattr(self, '_execution_start')

        self.current_budget.record_execution(description)

    def get_session_stats(self) -> dict:
        """Get overall session statistics"""
        total_time = self.total_planning_time + self.total_execution_time

        return {
            "planning_time": self.total_planning_time,
            "execution_time": self.total_execution_time,
            "total_time": total_time,
            "planning_ratio": self.total_planning_time / total_time if total_time > 0 else 0,
            "execution_ratio": self.total_execution_time / total_time if total_time > 0 else 0,
            "current_budget": self.current_budget.get_stats()
        }

    def check_session_budget(self) -> None:
        """Enforce session-wide planning budget"""
        stats = self.get_session_stats()

        if stats["planning_ratio"] > self.MAX_SESSION_PLANNING_RATIO:
            raise RuntimeError(
                f"SESSION_PLANNING_EXCESSIVE: {stats['planning_ratio']:.1%} of session spent planning.\n"
                f"Max allowed: {self.MAX_SESSION_PLANNING_RATIO:.1%}\n"
                f"Planning time: {stats['planning_time']:.1f}s\n"
                f"Execution time: {stats['execution_time']:.1f}s\n"
                f"ACTION REQUIRED: Execute more, plan less."
            )
```

---

## Usage Examples

### Example 1: Basic Planning Budget

```python
# Initialize budget
budget = PlanningBudget()

# Planning iteration 1
budget.update_plan("Analyze codebase structure")

# Planning iteration 2
budget.update_plan("Refine approach based on analysis")

# Planning iteration 3 (would raise error)
try:
    budget.update_plan("Further refinement")  # PLANNING_LOOP error
except RuntimeError as e:
    print(e)  # Forced to execute

# Execute instead
budget.record_execution("Created module.py")
# Budget reset, can plan again
```

### Example 2: Session Budget Tracking

```python
# Track entire session
session = SessionBudget()

# Planning phase
session.start_planning()
analyze_codebase()
session.end_planning("Analyzed structure")

# Execution phase
session.start_execution()
create_files()
session.end_execution("Created 5 files")

# Check stats
stats = session.get_session_stats()
print(f"Planning ratio: {stats['planning_ratio']:.1%}")
```

### Example 3: Integration with AI Agent

```python
class AIAgent:
    def __init__(self):
        self.budget = PlanningBudget()

    def think(self, task: str):
        """Thinking/planning step"""
        try:
            self.budget.update_plan(f"Planning: {task}")
            # Do planning work...
        except RuntimeError as e:
            # Budget exceeded - force execution
            print(f"Planning budget exceeded: {e}")
            print("Moving to execution phase...")
            return self.execute()

    def execute(self):
        """Execution step"""
        # Do actual work...
        self.budget.record_execution("Executed task")
        # Budget reset, can plan again if needed
```

### Example 4: Pre-Flight Check

```python
def should_execute_now(budget: PlanningBudget) -> bool:
    """Check if should execute instead of planning more"""

    # Check 1: Hit planning limit?
    if budget.plan_count >= PlanningBudget.MAX_PLAN_UPDATES:
        return True

    # Check 2: Planning-heavy session?
    if budget.is_planning_heavy(threshold=0.4):
        return True

    return False

# Usage
if should_execute_now(budget):
    execute_plan()
else:
    continue_planning()
```

---

## Integration Points

### With EXEC-002 (Batch Validation)

```python
from core.patterns.exec002 import BatchExecutor

def execute_with_budget(operations: list, budget: PlanningBudget):
    """Combine planning budget with batch execution"""

    # Allow brief planning
    budget.update_plan("Validating batch operations")

    # Force execution (EXEC-002)
    batch = BatchExecutor()
    for op in operations:
        batch.add(op)

    results = batch.execute_all()

    # Record execution (resets budget)
    budget.record_execution(f"Executed {len(operations)} operations")

    return results
```

### With Agent Loop

```python
def agent_loop(task: str, budget: PlanningBudget):
    """Agent loop with planning budget"""

    max_iterations = 10

    for i in range(max_iterations):
        # Planning phase (budget-limited)
        try:
            if i < 2:  # Allow planning in first 2 iterations
                budget.update_plan(f"Iteration {i}: Analyzing task")
                plan = create_plan(task)
            else:
                # Force execution after 2 planning iterations
                raise RuntimeError("Planning budget exceeded")

        except RuntimeError:
            # Execute
            result = execute_plan(plan)
            budget.record_execution(f"Iteration {i}: Executed")

            if is_complete(result):
                break
```

---

## Decision Tree

```
Need to Update Plan?
  │
  ├─ Have you executed the current plan yet?
  │   NO → Execute first, refine later
  │   YES ↓
  │
  ├─ Plan update count < 2?
  │   YES → Update plan
  │   NO  ↓
  │
  ├─ Have new information from execution?
  │   YES → Record execution, reset budget, update plan
  │   NO  → STOP PLANNING, START EXECUTING
  │
  └─ Session planning ratio > 30%?
      YES → Reduce planning, increase execution
      NO  → Continue normally
```

---

## Metrics

### Prevents
- **Planning loops**: 100% elimination
- **Meta-work waste**: 30-60s saved per incident (4 incidents)
- **Execution delays**: Forces action after 2 iterations

### Performance
- **Overhead**: <1ms per plan update (counter increment)
- **Savings**: 30-60s per prevented loop
- **ROI**: 30,000:1 (1ms overhead vs 30s saved)

---

## Anti-Patterns (Don't Do This)

### ❌ Anti-Pattern 1: Unbounded Planning
```python
# BAD: Can plan forever
while not perfect_plan:
    refine_plan()  # Never perfect, infinite loop
```

### ❌ Anti-Pattern 2: Planning Without Validation
```python
# BAD: Planning without execution to validate assumptions
plan_v1 = create_plan()
plan_v2 = refine_plan(plan_v1)  # No execution to test plan_v1
plan_v3 = refine_plan(plan_v2)  # No data, just speculation
```

### ✅ Correct Pattern: Plan-Execute-Learn Loop
```python
# GOOD: Short planning, execute, learn, repeat
budget = PlanningBudget()

for iteration in range(5):
    # Brief planning (max 2 updates)
    budget.update_plan(f"Plan iteration {iteration}")

    # Execute
    result = execute()
    budget.record_execution()

    # Learn from results
    if is_complete(result):
        break
```

---

## Testing Strategy

```python
import pytest

def test_planning_budget_limit():
    """Test PATTERN-001: Planning budget enforced"""
    budget = PlanningBudget()

    # First two updates allowed
    budget.update_plan("Plan v1")
    budget.update_plan("Plan v2")

    # Third update raises error
    with pytest.raises(RuntimeError, match="PLANNING_LOOP"):
        budget.update_plan("Plan v3")

def test_budget_reset_on_execution():
    """Test PATTERN-001: Budget resets after execution"""
    budget = PlanningBudget()

    # Use budget
    budget.update_plan("Plan v1")
    budget.update_plan("Plan v2")

    # Execute (resets budget)
    budget.record_execution("Executed")

    # Can plan again
    budget.update_plan("Plan v3")  # Should not raise

def test_planning_ratio():
    """Test PATTERN-001: Planning ratio calculation"""
    budget = PlanningBudget()

    budget.update_plan("Plan v1")
    budget.record_execution("Execute 1")
    budget.record_execution("Execute 2")
    budget.record_execution("Execute 3")

    stats = budget.get_stats()
    assert stats["planning_ratio"] == 0.0  # Reset on execution
    assert stats["executions"] == 3
```

---

## Implementation Checklist

- [ ] Implement PlanningBudget class with limit enforcement
- [ ] Implement SessionBudget for session-wide tracking
- [ ] Add planning time vs execution time tracking
- [ ] Add statistics and reporting methods
- [ ] Integrate with agent loop
- [ ] Add unit tests for budget enforcement
- [ ] Add unit tests for reset logic
- [ ] Document recommended planning/execution ratios
- [ ] Add metrics dashboard (planning vs execution over time)

---

## Recommended Ratios

### Per-Task Budget
- **Planning iterations**: Max 2 before execution
- **Planning time**: Max 30% of task time
- **Execution time**: Min 70% of task time

### Session Budget
- **Planning time**: Max 30% of session
- **Execution time**: Min 70% of session
- **Plan-execute cycles**: 3-5 cycles preferred over 1 long planning phase

### Recovery Actions
If planning budget exceeded:
1. **Execute current plan** (even if imperfect)
2. **Observe results** (gather real data)
3. **Refine plan** based on observations (budget reset)
4. **Repeat** (plan-execute-learn loop)

---

## References

- **Source**: `codex_log_analysis_report.md` Section 1.4
- **Related Patterns**: All execution patterns (forces action)
- **Implementation**: `core/patterns/pattern001.py`
- **Tests**: `tests/patterns/test_pattern001.py`

---

**Status**: ✅ Ready for Implementation
**Priority**: High (prevents meta-work waste)
**Effort**: Low (2-3 hours)
