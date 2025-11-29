# Abstraction Layer - Remaining Implementation Guide

**Created**: 2025-11-29 17:18 UTC  
**Status**: Wave 1 (67% complete) + Wave 2 (0% started)  
**Remaining**: 4 workstreams (1 in Wave 1, 3 in Wave 2)

---

## 🎯 Current Status Summary

### ✅ Completed (2/12)
- **WS-ABS-003**: ProcessExecutor (11 tests passing)
- **WS-ABS-002**: StateStore (15 tests passing)

### 🔄 In Progress
- **Wave 1**: 2/3 complete (67%)
- **Overall**: 2/12 complete (17%)

---

## 📋 Remaining Wave 1: WS-ABS-001 (ToolAdapter)

**Priority**: P0-CRITICAL  
**Duration**: Est. 3 days → Projected < 1 hour  
**Dependencies**: WS-ABS-003 (ProcessExecutor) ✅ SATISFIED

### Implementation Checklist

#### Files to Create
- [ ] `core/interfaces/tool_adapter.py` - Protocol definition
- [ ] `core/adapters/__init__.py` - Package init
- [ ] `core/adapters/base.py` - Base adapter implementation  
- [ ] `core/adapters/registry.py` - ToolRegistry for discovery
- [ ] `tests/interfaces/test_tool_adapter.py` - Test suite

#### Files to Reference (for migration pattern)
- `engine/adapters/aider_adapter.py`
- `engine/adapters/codex_adapter.py`
- `engine/adapters/tests_adapter.py`
- `engine/adapters/git_adapter.py`

### Protocol Design

```python
@runtime_checkable
class ToolAdapter(Protocol):
    """Protocol for tool adapters."""
    
    def supports(self, capabilities: set[str]) -> bool:
        """Check if adapter supports given capabilities."""
        ...
    
    def prepare_job(self, job_spec: dict[str, Any]) -> dict[str, Any]:
        """Prepare job for execution."""
        ...
    
    def run(
        self, 
        job: dict[str, Any],
        *,
        executor: ProcessExecutor,
    ) -> ProcessResult:
        """Execute job using process executor."""
        ...
    
    def normalize_result(self, result: ProcessResult) -> dict[str, Any]:
        """Normalize process result to standard format."""
        ...
```

### Ground Truth Verification
```bash
test -f core/interfaces/tool_adapter.py && \
python -c "from core.adapters.registry import ToolRegistry" && \
pytest tests/interfaces/test_tool_adapter.py -q && \
echo "✅ WS-ABS-001 COMPLETE"
```

---

## 📋 Wave 2 Workstreams (P1 - Config & Events)

### WS-ABS-004: ConfigManager

**Duration**: Est. 2 days → Projected < 45 min  
**Dependencies**: WS-ABS-002 (StateStore) ✅ SATISFIED

#### Files to Create
- [ ] `core/interfaces/config_manager.py` - Protocol
- [ ] `core/config/__init__.py` - Package init
- [ ] `core/config/yaml_config_manager.py` - YAML implementation
- [ ] `core/config/schemas.py` - Pydantic schemas
- [ ] `tests/interfaces/test_config_manager.py` - Tests

#### Protocol Design
```python
@runtime_checkable  
class ConfigManager(Protocol):
    """Protocol for configuration management."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        ...
    
    def get_tool_profile(self, tool: str) -> dict[str, Any]:
        """Get tool-specific configuration."""
        ...
    
    def validate_all(self) -> list[str]:
        """Validate all configs, return errors."""
        ...
    
    def reload(self) -> None:
        """Hot-reload configs from disk."""
        ...
```

---

### WS-ABS-005: EventBus & Logger

**Duration**: Est. 3 days → Projected < 1 hour  
**Dependencies**: None (independent)

#### Files to Create
- [ ] `core/interfaces/event_bus.py` - EventBus protocol
- [ ] `core/interfaces/logger.py` - Logger protocol  
- [ ] `core/events/__init__.py` - Package init
- [ ] `core/events/simple_event_bus.py` - In-memory implementation
- [ ] `core/logging/__init__.py` - Package init
- [ ] `core/logging/structured_logger.py` - JSON logger
- [ ] `tests/interfaces/test_event_bus.py` - EventBus tests
- [ ] `tests/interfaces/test_logger.py` - Logger tests

#### Protocol Designs
```python
@runtime_checkable
class EventBus(Protocol):
    """Protocol for event pub/sub."""
    
    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        """Emit an event."""
        ...
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[dict], None]
    ) -> str:
        """Subscribe to events, return subscription ID."""
        ...
    
    def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from events."""
        ...

@runtime_checkable
class Logger(Protocol):
    """Protocol for structured logging."""
    
    def info(self, msg: str, **context) -> None:
        """Log info message."""
        ...
    
    def error(self, msg: str, **context) -> None:
        """Log error message."""
        ...
    
    def job_event(
        self, 
        job_id: str, 
        event: str, 
        **data
    ) -> None:
        """Log job-specific event."""
        ...
```

---

### WS-ABS-006: WorkstreamService

**Duration**: Est. 3 days → Projected < 1 hour  
**Dependencies**: WS-ABS-001 (ToolAdapter), WS-ABS-002 (StateStore) ✅ SATISFIED

#### Files to Create
- [ ] `core/interfaces/workstream_service.py` - Protocol
- [ ] `core/workstreams/__init__.py` - Package init
- [ ] `core/workstreams/workstream_service_impl.py` - Implementation
- [ ] `core/workstreams/lifecycle_hooks.py` - Hook system
- [ ] `tests/interfaces/test_workstream_service.py` - Tests

#### Protocol Design
```python
@runtime_checkable
class WorkstreamService(Protocol):
    """Protocol for workstream lifecycle management."""
    
    def create(self, spec: dict[str, Any]) -> str:
        """Create new workstream, return ID."""
        ...
    
    def load(self, ws_id: str) -> dict[str, Any]:
        """Load workstream by ID."""
        ...
    
    def execute(
        self, 
        ws_id: str,
        *,
        dry_run: bool = False
    ) -> str:
        """Execute workstream, return run ID."""
        ...
    
    def get_status(self, ws_id: str) -> dict[str, Any]:
        """Get workstream status."""
        ...
    
    def archive(self, ws_id: str) -> None:
        """Archive completed workstream."""
        ...
```

---

## 🎯 Implementation Strategy

### Pattern: EXEC-002 (Module Generator)
1. Create protocol with minimal methods (3-5)
2. Implement concrete class using dependencies
3. Write comprehensive tests (aim for 10-15 tests)
4. Verify ground truth
5. Commit immediately

### Time Estimates (Based on Current Velocity)
- WS-ABS-001: 45-60 minutes
- WS-ABS-004: 30-45 minutes
- WS-ABS-005: 45-60 minutes (2 protocols)
- WS-ABS-006: 45-60 minutes

**Total Projected Time**: ~3 hours for all 4 workstreams

### Execution Order
1. ✅ WS-ABS-001 (ToolAdapter) - Complete Wave 1
2. ✅ WS-ABS-004 (ConfigManager) - Start Wave 2
3. ✅ WS-ABS-005 (EventBus & Logger) - Independent
4. ✅ WS-ABS-006 (WorkstreamService) - Depends on 001, 002

---

## 📊 Success Criteria

### Per Workstream
- [ ] Protocol file created with `@runtime_checkable`
- [ ] At least one concrete implementation
- [ ] 10+ tests passing
- [ ] Ground truth verification passed
- [ ] No mypy errors
- [ ] Committed to main branch

### Wave 1 Completion
- [ ] All 3 workstreams complete (001, 002, 003)
- [ ] Run: `pytest tests/interfaces/ -v`
- [ ] Run: `mypy core/interfaces/ --strict`
- [ ] Create Wave 1 final report
- [ ] Git tag: `v0.1.0-wave1-complete`

### Wave 2 Completion  
- [ ] All 3 workstreams complete (004, 005, 006)
- [ ] All tests passing (Wave 1 + Wave 2)
- [ ] Integration tests pass
- [ ] Create Wave 2 final report
- [ ] Git tag: `v0.2.0-wave2-complete`

---

## 🚀 Next Commands

### To Continue Implementation

```bash
# Navigate to project
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Verify current status
git status
git log --oneline -5

# Check tests are still passing
pytest tests/interfaces/test_process_executor.py -q
pytest tests/interfaces/test_state_store.py -q

# Start WS-ABS-001 implementation
# (AI agent will create protocol, implementation, tests)
```

### Ground Truth Verification Commands

```bash
# WS-ABS-001 (ToolAdapter)
test -f core/interfaces/tool_adapter.py && \
pytest tests/interfaces/test_tool_adapter.py -q && \
echo "✅ WS-ABS-001 COMPLETE"

# WS-ABS-004 (ConfigManager)
test -f core/interfaces/config_manager.py && \
pytest tests/interfaces/test_config_manager.py -q && \
echo "✅ WS-ABS-004 COMPLETE"

# WS-ABS-005 (EventBus & Logger)
test -f core/interfaces/event_bus.py && \
test -f core/interfaces/logger.py && \
pytest tests/interfaces/test_event_bus.py tests/interfaces/test_logger.py -q && \
echo "✅ WS-ABS-005 COMPLETE"

# WS-ABS-006 (WorkstreamService)
test -f core/interfaces/workstream_service.py && \
pytest tests/interfaces/test_workstream_service.py -q && \
echo "✅ WS-ABS-006 COMPLETE"

# Wave 1 + Wave 2 Complete
pytest tests/interfaces/ -v --cov=core/interfaces --cov-report=term-missing && \
mypy core/interfaces/ --strict && \
echo "✅ WAVE 1 + WAVE 2 COMPLETE"
```

---

## 📈 Progress Tracking

### Completion Checklist

**Wave 1 (P0 - Foundation)**:
- [x] WS-ABS-003: ProcessExecutor
- [x] WS-ABS-002: StateStore  
- [ ] WS-ABS-001: ToolAdapter

**Wave 2 (P1 - Config & Events)**:
- [ ] WS-ABS-004: ConfigManager
- [ ] WS-ABS-005: EventBus & Logger
- [ ] WS-ABS-006: WorkstreamService

**Overall Progress**: 2/12 (17%) → Target: 6/12 (50%)

---

## 🎯 Anti-Pattern Guards (Maintain for All)

For each workstream, ensure:
- ✅ Ground truth verification (file exists + imports + tests pass)
- ✅ No TODO/pass in production code
- ✅ Explicit error types defined
- ✅ Type hints enforced via mypy
- ✅ Protocol marked `@runtime_checkable`
- ✅ Tests cover all protocol methods
- ✅ Immediate commit after verification

---

## 📚 Reference Documents

- **Phase Plan**: `abstraction/ABSTRACTION_PHASE_PLAN.md`
- **Quick Reference**: `abstraction/QUICK_REFERENCE.md`
- **Wave 1 Report**: `abstraction/WAVE_1_COMPLETION_REPORT.md`
- **Workstream Specs**: `abstraction/workstream_specs.json`
- **Execution Patterns**: `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`

---

**Ready to Continue**: This guide provides complete specifications for the remaining 4 workstreams. Follow the pattern established in WS-ABS-002 and WS-ABS-003 for consistent, high-quality implementations.

**Estimated Completion**: Wave 1 + Wave 2 complete in ~3 hours total.

**Current Status**: Ready to implement WS-ABS-001 (ToolAdapter)

---

**End of Guide**
