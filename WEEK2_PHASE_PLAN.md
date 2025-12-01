# Week 2: ClusterManager API - Phase Plan

**Goal**: High-level API for managing process pools with routing strategies  
**Duration**: 5 days  
**Status**: 🚀 Ready to begin

---

## Overview

Week 2 builds on Week 1's `ToolProcessPool` foundation by adding a high-level `ClusterManager` API with intelligent routing, load balancing, and automatic failure recovery.

**Key Addition**: `launch_cluster()` function that abstracts pool management and provides production-ready patterns.

---

## Architecture

```
ClusterManager (Week 2)
├── launch_cluster() - High-level API
├── Routing Strategies:
│   ├── RoundRobinRouter
│   ├── LeastBusyRouter
│   └── StickyRouter
├── Auto-restart on failure
├── Load metrics & monitoring
└── Built on ToolProcessPool (Week 1)
```

---

## Week 2 Schedule

### Day 1: ClusterManager Core (6 hours)

**Deliverables**:
1. `aim/cluster.py` - ClusterManager class
2. `launch_cluster()` API function
3. Basic routing interface

**Tasks**:
- Design ClusterManager interface
- Implement launch_cluster() function
- Add basic round-robin routing
- Create cluster lifecycle management

**Code Structure**:
```python
# aim/cluster.py

from typing import Optional, List, Callable
from aim.bridge import ToolProcessPool


class ClusterManager:
    """High-level manager for tool process pools."""
    
    def __init__(self, tool_id: str, count: int):
        self.pool = ToolProcessPool(tool_id, count)
        self.router = None
        self.metrics = {}
    
    def send(self, prompt: str) -> int:
        """Send prompt using routing strategy.
        
        Returns:
            int: Instance index that received the prompt
        """
        pass
    
    def get_metrics(self) -> dict:
        """Get cluster performance metrics."""
        pass


def launch_cluster(tool_id: str, count: int = 3, 
                   strategy: str = "round-robin") -> ClusterManager:
    """Launch a managed cluster of CLI tools.
    
    Args:
        tool_id: Tool to launch (e.g., "aider", "jules")
        count: Number of instances
        strategy: Routing strategy ("round-robin", "least-busy", "sticky")
    
    Returns:
        ClusterManager: Managed cluster instance
    
    Example:
        cluster = launch_cluster("aider", count=3)
        cluster.send("/add file.py")
        cluster.send("/ask 'refactor this'")
    """
    pass
```

**Validation**:
```bash
python -c "from aim.cluster import launch_cluster; c = launch_cluster('aider', 2); print(c)"
```

---

### Day 2: Routing Strategies (6 hours)

**Deliverables**:
1. `aim/routing.py` - Router implementations
2. Unit tests for each router
3. Router performance benchmarks

**Routers to Implement**:

#### 1. RoundRobinRouter
- Cycles through instances sequentially
- Simple, predictable distribution
- Use case: Evenly distributed workload

#### 2. LeastBusyRouter
- Selects instance with fewest pending tasks
- Tracks task queue per instance
- Use case: Variable task duration

#### 3. StickyRouter
- Routes based on session/context hash
- Maintains affinity to specific instance
- Use case: Stateful workflows

**Code Structure**:
```python
# aim/routing.py

from abc import ABC, abstractmethod
from typing import List


class Router(ABC):
    """Base router interface."""
    
    @abstractmethod
    def select_instance(self, instances: List, context: dict = None) -> int:
        """Select instance index for next task."""
        pass


class RoundRobinRouter(Router):
    def __init__(self):
        self.current = 0
    
    def select_instance(self, instances: List, context: dict = None) -> int:
        idx = self.current
        self.current = (self.current + 1) % len(instances)
        return idx


class LeastBusyRouter(Router):
    def __init__(self):
        self.task_counts = {}
    
    def select_instance(self, instances: List, context: dict = None) -> int:
        # Select instance with minimum pending tasks
        counts = [self.task_counts.get(i, 0) for i in range(len(instances))]
        return counts.index(min(counts))


class StickyRouter(Router):
    def __init__(self):
        self.session_map = {}
    
    def select_instance(self, instances: List, context: dict = None) -> int:
        session_id = context.get("session_id") if context else None
        if session_id and session_id in self.session_map:
            return self.session_map[session_id]
        
        # New session - assign to instance
        idx = len(self.session_map) % len(instances)
        if session_id:
            self.session_map[session_id] = idx
        return idx
```

**Testing**:
```python
# tests/aim/test_routing.py

def test_round_robin_distribution():
    router = RoundRobinRouter()
    instances = [Mock(), Mock(), Mock()]
    
    results = [router.select_instance(instances) for _ in range(9)]
    assert results == [0, 1, 2, 0, 1, 2, 0, 1, 2]

def test_least_busy_prefers_idle():
    router = LeastBusyRouter()
    router.task_counts = {0: 5, 1: 2, 2: 8}
    
    idx = router.select_instance([Mock(), Mock(), Mock()])
    assert idx == 1  # Instance 1 has fewest tasks
```

---

### Day 3: Auto-Restart & Circuit Breaker (6 hours)

**Deliverables**:
1. Automatic crash detection and restart
2. Circuit breaker pattern for failing instances
3. Health-based routing (skip unhealthy instances)

**Features**:

#### Auto-Restart
- Monitor instance health in background thread
- Restart crashed instances automatically
- Exponential backoff on repeated failures

#### Circuit Breaker
- Track failure rate per instance
- Open circuit after N consecutive failures
- Attempt reset after cooldown period

**Code Structure**:
```python
# aim/cluster.py (additions)

class ClusterManager:
    def __init__(self, tool_id: str, count: int, 
                 auto_restart: bool = True):
        self.pool = ToolProcessPool(tool_id, count)
        self.auto_restart = auto_restart
        self.circuit_breakers = {}
        
        if auto_restart:
            self._start_health_monitor()
    
    def _start_health_monitor(self):
        """Start background thread to monitor and restart instances."""
        import threading
        
        def monitor():
            while self.running:
                health = self.pool.check_health()
                
                for inst in health['instances']:
                    if not inst['alive']:
                        self._handle_dead_instance(inst['index'])
                
                time.sleep(5.0)  # Check every 5 seconds
        
        self.monitor_thread = threading.Thread(
            target=monitor, 
            daemon=True
        )
        self.monitor_thread.start()
    
    def _handle_dead_instance(self, idx: int):
        """Handle a dead instance with circuit breaker logic."""
        cb = self.circuit_breakers.get(idx)
        
        if cb and cb.is_open():
            # Circuit open, don't restart yet
            return
        
        # Attempt restart
        if self.pool.restart_instance(idx):
            print(f"Restarted instance {idx}")
        else:
            # Restart failed, open circuit
            if idx not in self.circuit_breakers:
                self.circuit_breakers[idx] = CircuitBreaker()
            self.circuit_breakers[idx].record_failure()
```

---

### Day 4: Metrics & Monitoring (6 hours)

**Deliverables**:
1. Performance metrics tracking
2. Real-time monitoring API
3. Metrics export (JSON/dict format)

**Metrics to Track**:
- Prompts sent per instance
- Response time per instance
- Success/failure rate
- Instance uptime
- Restart count
- Current load (pending tasks)

**Code Structure**:
```python
# aim/metrics.py

from dataclasses import dataclass
from typing import Dict
import time


@dataclass
class InstanceMetrics:
    instance_id: int
    prompts_sent: int = 0
    responses_received: int = 0
    failures: int = 0
    total_response_time: float = 0.0
    restart_count: int = 0
    start_time: float = time.time()
    
    @property
    def avg_response_time(self) -> float:
        if self.responses_received == 0:
            return 0.0
        return self.total_response_time / self.responses_received
    
    @property
    def uptime(self) -> float:
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        total = self.prompts_sent
        if total == 0:
            return 1.0
        return (total - self.failures) / total


class MetricsCollector:
    def __init__(self, instance_count: int):
        self.instances = {
            i: InstanceMetrics(instance_id=i)
            for i in range(instance_count)
        }
    
    def record_prompt(self, instance_id: int):
        self.instances[instance_id].prompts_sent += 1
    
    def record_response(self, instance_id: int, elapsed: float):
        m = self.instances[instance_id]
        m.responses_received += 1
        m.total_response_time += elapsed
    
    def get_summary(self) -> Dict:
        return {
            "total_prompts": sum(m.prompts_sent for m in self.instances.values()),
            "avg_response_time": sum(m.avg_response_time for m in self.instances.values()) / len(self.instances),
            "overall_success_rate": sum(m.success_rate for m in self.instances.values()) / len(self.instances),
            "instances": {i: m.__dict__ for i, m in self.instances.items()}
        }
```

---

### Day 5: Integration & Documentation (6 hours)

**Deliverables**:
1. Complete integration tests
2. API documentation
3. Usage examples
4. Performance benchmarks

**Integration Tests**:
```python
# tests/aim/integration/test_cluster_manager.py

def test_cluster_with_routing():
    cluster = launch_cluster("aider", count=3, strategy="round-robin")
    
    # Send 9 prompts
    for i in range(9):
        cluster.send(f"/help {i}")
    
    # Verify round-robin distribution
    metrics = cluster.get_metrics()
    assert metrics['instances'][0]['prompts_sent'] == 3
    assert metrics['instances'][1]['prompts_sent'] == 3
    assert metrics['instances'][2]['prompts_sent'] == 3


def test_auto_restart_on_crash():
    cluster = launch_cluster("aider", count=2, auto_restart=True)
    
    # Kill an instance
    cluster.pool.instances[0].process.kill()
    
    # Wait for auto-restart
    time.sleep(6.0)
    
    # Verify restarted
    health = cluster.pool.check_health()
    assert health['alive'] == 2
```

**Documentation**:
- Complete API reference for ClusterManager
- Routing strategy guide
- Metrics interpretation
- Production deployment guide

---

## Success Criteria

### Week 2 Complete When:
- ✅ `launch_cluster()` API functional
- ✅ 3 routing strategies implemented
- ✅ Auto-restart working
- ✅ Metrics tracking operational
- ✅ All tests passing (target: 20+ new tests)
- ✅ Documentation complete

### Performance Targets:
- **Throughput**: 50+ prompts/minute with 5 instances
- **Failover time**: <10 seconds for auto-restart
- **Routing overhead**: <10ms per selection

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Routing complexity | Start with simple round-robin, iterate |
| Thread safety | Use queue.Queue for metrics, test concurrency |
| Monitor overhead | 5-second poll interval, daemon threads |
| Memory leaks | Proper cleanup in shutdown, test long runs |

---

## Dependencies

- ✅ Week 1: ToolProcessPool (complete)
- ✅ Python 3.8+ (threading, dataclasses)
- ✅ pytest for testing
- ⚠️ Optional: prometheus_client for metrics export (future)

---

## Estimated Timeline

| Task | Hours | Dependencies |
|------|-------|--------------|
| Day 1: ClusterManager core | 6 | Week 1 complete |
| Day 2: Routing strategies | 6 | Day 1 |
| Day 3: Auto-restart | 6 | Day 1 |
| Day 4: Metrics | 6 | Day 1-3 |
| Day 5: Integration & docs | 6 | Day 1-4 |
| **Total** | **30** | |

---

**Status**: Ready to begin Day 1  
**Next**: Implement ClusterManager core in `aim/cluster.py`
