# core/engine/monitoring

**Purpose**: Real-time progress tracking and execution metrics.

## Overview

Provides monitoring capabilities:
- **Progress Tracking** - Task and run-level progress
- **Metrics Collection** - Performance statistics
- **ETA Calculation** - Estimated completion time
- **Snapshots** - Real-time state snapshots

## Key Files

- **progress.py** - ProgressTracker implementation
- **metrics.py** - MetricsCollector for statistics
- **snapshot.py** - State snapshot generation

## Dependencies

**Depends on:**
- core/state/ - For run/task state

**Used by:**
- core/engine/ - For execution monitoring

## Progress Tracker

Tracks execution progress in real-time.

### Usage
```python
from core.engine.monitoring import ProgressTracker

tracker = ProgressTracker("run-123", total_tasks=10)
tracker.start()

# Track task progress
tracker.start_task("task-1")
tracker.update_task_progress(50.0)  # 50% complete
tracker.complete_task("task-1", duration=5.2)

# Get snapshot
snapshot = tracker.get_snapshot()
print(f"Progress: {snapshot.completion_percent}%")
print(f"ETA: {snapshot.estimated_completion}")
```

## Metrics Collector

Collects and aggregates execution metrics.

### Usage
```python
from core.engine.monitoring import MetricsCollector

collector = MetricsCollector("run-123")

# Collect metrics
metrics = collector.collect()

print(f"Duration: {metrics.duration}s")
print(f"Success rate: {metrics.success_rate}%")
print(f"Avg task duration: {metrics.avg_task_duration}s")
```

## References

- **Engine**: core/engine/README.md
- **State**: core/state/README.md
