---
doc_id: DOC-LEGACY-HIDDEN-PONDERING-TREASURE-023
---

# Phase Plan: Pattern Activity Panel Implementation

**Pattern-Driven Execution with Parallel Worktrees**

---

## Executive Summary

**Goal**: Implement Pattern Activity Panel for UET framework using decision elimination patterns and parallel git worktrees

**Estimated Time**:
- Traditional approach: 16-20 hours
- With execution patterns + worktrees: **4-5 hours** (4x speedup)

**Key Innovation**: Apply EXEC-001 (Batch File Creator), EXEC-002 (Code Module Generator), and EXEC-003 (Test Suite Multiplier) patterns with parallel worktree execution

---

## Pre-Made Decisions (Decision Elimination)

### Structural Decisions (Made Once)

**Database Schema**:
- Format: SQLite with 2 new tables (`pattern_runs`, `pattern_events`)
- Migration file: `schema/migrations/006_add_pattern_tables.sql`
- Indexes: job_id, pattern_id, status, timestamp

**Code Structure**:
- Backend: Python following existing `core/state/`, `core/ui_clients/` patterns
- Frontend: React components (modular panel architecture)
- API: REST endpoints at `/api/patterns/*`, WebSocket at `/jobs/{job_id}/events`

**Event Schema**:
- 15 event types across 5 lifecycle phases
- Unified schema matching existing `run.*`, `step.*`, `tool.*` events
- Correlation IDs: job_id, step_id, pattern_run_id, pattern_id

**File Count**:
- Backend: 8 Python files (~1,200 lines)
- Frontend: 5 React components (~600 lines)
- Tests: 6 test files (~400 lines)
- Documentation: 3 files (already created)
- **Total**: 22 files

---

## Worktree Strategy (4x Parallel Execution)

### Worktree 1: Backend Core (1 hour)
**Branch**: `feature/pattern-panel-backend`
**Path**: `.worktrees/wt-pattern-backend`
**Scope**: Database, state store, event emission

**Files**:
1. `schema/migrations/006_add_pattern_tables.sql` - Schema (EXEC-001: template-driven)
2. `core/state/pattern_state_store.py` - State persistence (~300 lines)
3. `core/events/pattern_events.py` - Event definitions (~100 lines)
4. `patterns/engine/pattern_executor.py` - Add event emission (modify existing ~150 lines)

**Pattern**: EXEC-001 (Batch File Creator) + EXEC-002 (Code Module Generator)

**Ground Truth**:
- Migration runs without errors
- `PatternStateStore` imports successfully
- Events save to database

---

### Worktree 2: API Layer (1 hour)
**Branch**: `feature/pattern-panel-api`
**Path**: `.worktrees/wt-pattern-api`
**Scope**: Client, CLI, REST endpoints

**Files**:
1. `core/ui_clients/pattern_client.py` - Data access client (~150 lines)
2. `core/ui_cli.py` - Add 3 commands (modify existing ~100 lines)
3. `api/routes/patterns.py` - REST endpoints (~100 lines)
4. `api/websocket.py` - Extend WebSocket handler (modify existing ~50 lines)

**Pattern**: EXEC-002 (Code Module Generator) - all follow existing client pattern

**Ground Truth**:
- CLI commands work: `pattern-events`, `pattern-summary`, `pattern-detail`
- REST endpoints return valid JSON
- WebSocket streams pattern events

---

### Worktree 3: Frontend Components (1.5 hours)
**Branch**: `feature/pattern-panel-frontend`
**Path**: `.worktrees/wt-pattern-frontend`
**Scope**: React GUI components

**Files**:
1. `patterns/gui/web/PatternActivityPanel.tsx` - Main panel (~200 lines)
2. `patterns/gui/web/TimelineView.tsx` - Timeline component (~150 lines)
3. `patterns/gui/web/SummaryHeader.tsx` - Summary stats (~100 lines)
4. `patterns/gui/web/DetailDrawer.tsx` - Detail view (~150 lines)
5. `patterns/gui/web/utils.ts` - Utility functions (~100 lines)

**Pattern**: EXEC-002 (Code Module Generator) - React component template

**Ground Truth**:
- Components render without errors
- WebSocket connection establishes
- Timeline updates with live events

---

### Worktree 4: Tests & Integration (1 hour)
**Branch**: `feature/pattern-panel-tests`
**Path**: `.worktrees/wt-pattern-tests`
**Scope**: Test suites and integration

**Files**:
1. `tests/state/test_pattern_state_store.py` - State store tests (~100 lines)
2. `tests/ui_clients/test_pattern_client.py` - Client tests (~80 lines)
3. `tests/api/test_pattern_routes.py` - API endpoint tests (~100 lines)
4. `tests/integration/test_pattern_flow.py` - End-to-end test (~120 lines)
5. `scripts/test_pattern_integration.py` - Integration test script (~100 lines)

**Pattern**: EXEC-003 (Test Suite Multiplier) - test template

**Ground Truth**:
- All tests pass: `pytest tests/ -q`
- Integration script completes successfully
- No import errors

---

## Execution Templates (Pre-Compiled)

### Template 1: Python State Store Module

```python
# TEMPLATE: PatternStateStore
# Pattern: EXEC-002 (Code Module Generator)
# Variables: {table_name}, {methods}

"""
{module_name}

DOC_ID: DOC-CORE-PATTERN-STATE-STORE-001
PURPOSE: Pattern execution data persistence
"""

from typing import Optional, List, Dict
import sqlite3
import json
from pathlib import Path

class PatternStateStore:
    """State persistence for pattern execution data."""

    def __init__(self, db_path: str = ".worktrees/pipeline_state.db"):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Load schema from migration file
            migration = Path("schema/migrations/006_add_pattern_tables.sql").read_text()
            conn.executescript(migration)

    def save_run(self, record: dict) -> None:
        """Persist pattern run record."""
        # Implementation from design doc Section 5.2
        pass

    def save_event(self, event: dict) -> None:
        """Persist pattern event."""
        # Implementation from design doc Section 5.2
        pass

    def get_events_for_job(self, job_id: str, after_event_id: Optional[str] = None) -> List[dict]:
        """Query events for a job."""
        # Implementation from design doc Section 5.2
        pass
```

**Decision Elimination**:
- ✅ Database type (SQLite)
- ✅ Connection pattern (context manager)
- ✅ Method signatures (from alignment doc)
- ✅ Error handling (standard try/except)

---

### Template 2: React Panel Component

```typescript
// TEMPLATE: PatternActivityPanel
// Pattern: EXEC-002 (Code Module Generator)
// Variables: {jobId}, {event_types}

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface PatternActivityPanelProps {
  jobId: string;
}

export const PatternActivityPanel: React.FC<PatternActivityPanelProps> = ({ jobId }) => {
  const [events, setEvents] = useState<PatternEvent[]>([]);
  const [summary, setSummary] = useState<PatternSummary | null>(null);
  const ws = useWebSocket(`ws://localhost:8080/jobs/${jobId}/events`);

  useEffect(() => {
    // Fetch initial data
    fetchEvents();
    fetchSummary();
  }, [jobId]);

  useEffect(() => {
    if (!ws) return;
    ws.onmessage = (message) => {
      const event = JSON.parse(message.data);
      if (event.event_type.startsWith("pattern.")) {
        setEvents(prev => [...prev, event]);
      }
    };
  }, [ws]);

  // Implementation from design doc Section 5.5

  return (
    <div className="pattern-activity-panel">
      <SummaryHeader summary={summary} />
      <TimelineView events={events} />
    </div>
  );
};
```

**Decision Elimination**:
- ✅ Component structure (hooks-based functional component)
- ✅ State management (useState for local state)
- ✅ Real-time updates (WebSocket)
- ✅ Layout (summary header + timeline view)

---

### Template 3: Test Suite

```python
# TEMPLATE: Pattern Panel Test
# Pattern: EXEC-003 (Test Suite Multiplier)
# Variables: {test_class}, {methods_to_test}

import pytest
from core.state.pattern_state_store import PatternStateStore
from core.ui_clients import PatternClient

class TestPatternStateStore:
    """Tests for PatternStateStore."""

    @pytest.fixture
    def store(self, tmp_path):
        """Fixture for test database."""
        db_path = tmp_path / "test.db"
        return PatternStateStore(str(db_path))

    def test_save_run(self, store):
        """Test saving pattern run record."""
        record = {
            "pattern_run_id": "PRUN-TEST",
            "pattern_id": "PAT-001",
            "job_id": "JOB-001",
            "status": "success"
        }
        store.save_run(record)

        # Verify saved
        result = store.get_run_detail("PRUN-TEST")
        assert result is not None
        assert result["status"] == "success"

    def test_get_events_for_job(self, store):
        """Test querying events by job."""
        # Test implementation
        pass
```

**Decision Elimination**:
- ✅ Test framework (pytest)
- ✅ Fixture pattern (tmp_path for isolated DB)
- ✅ Assertion style (assert)
- ✅ Test naming (test_<method_name>)

---

## Anti-Pattern Guards

### Guard 1: Hallucination of Success Prevention

**Problem**: AI may report "all files created" when only skeletons exist

**Solution**: Ground truth verification at each phase

```bash
# After Backend Core (Worktree 1)
python -c "from core.state.pattern_state_store import PatternStateStore; print('✓ Import success')"
sqlite3 .worktrees/pipeline_state.db "SELECT name FROM sqlite_master WHERE type='table' AND name='pattern_runs';"
# Expected: pattern_runs

# After API Layer (Worktree 2)
python -m core.ui_cli pattern-events --job-id test --json
# Expected: Valid JSON output (even if empty list)

# After Frontend (Worktree 3)
npm run build
# Expected: Exit code 0

# After Tests (Worktree 4)
pytest tests/state/test_pattern_state_store.py -q
# Expected: All tests pass
```

---

### Guard 2: Partial Success Amnesia Prevention

**Problem**: Losing track of what's completed when switching contexts

**Solution**: Checkpoint tracking file

**File**: `.worktrees/pattern-panel-progress.yaml`

```yaml
phase_status:
  backend_core:
    status: completed | in_progress | pending
    files_created: [list]
    ground_truth_passed: true | false
    timestamp: "2025-11-26T10:30:00Z"

  api_layer:
    status: pending
    # ...

  frontend:
    status: pending
    # ...

  tests:
    status: pending
    # ...
```

Update after each worktree completes.

---

### Guard 3: Planning Loop Trap Prevention

**Problem**: Spending too much time planning vs executing

**Solution**: 2-hour time box, decision cap

**Rules**:
- ❌ No planning sessions >30 min
- ❌ No architecture debates
- ❌ No "should we use X or Y?" questions
- ✅ Use templates as-is
- ✅ Trust existing patterns (StateClient, ToolsClient)
- ✅ Start coding after reading design docs

---

### Guard 4: Scope Creep Prevention

**Problem**: Adding features not in original spec

**Solution**: Strict file manifest

**Allowed Files** (22 total):
- Backend: 4 files
- API: 4 files
- Frontend: 5 files
- Tests: 6 files
- Docs: 3 files (already done)

**Forbidden**:
- ❌ New optimization layers
- ❌ Additional caching mechanisms
- ❌ Extra analytics features
- ❌ Alternative UI frameworks

If not in the manifest → defer to Phase 2.

---

## Execution Workflow

### Setup Phase (10 minutes)

```bash
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"

# Create worktree directory
mkdir -p .worktrees

# Create 4 parallel worktrees
git worktree add .worktrees/wt-pattern-backend feature/pattern-panel-backend
git worktree add .worktrees/wt-pattern-api feature/pattern-panel-api
git worktree add .worktrees/wt-pattern-frontend feature/pattern-panel-frontend
git worktree add .worktrees/wt-pattern-tests feature/pattern-panel-tests

# Verify
git worktree list

# Initialize progress tracker
cat > .worktrees/pattern-panel-progress.yaml << EOF
phase_status:
  backend_core: {status: pending}
  api_layer: {status: pending}
  frontend: {status: pending}
  tests: {status: pending}
EOF
```

---

### Parallel Execution Phase (4 hours)

**Open 4 terminal sessions** (or use tmux/screen):

#### Session 1: Backend Core
```bash
cd .worktrees/wt-pattern-backend

# Create migration (5 min) - EXEC-001 pattern
cat > ../../schema/migrations/006_add_pattern_tables.sql << 'EOF'
-- Copy from PATTERN_PANEL_INTEGRATION_CHECKLIST.md Step 1
EOF

# Create state store (30 min) - EXEC-002 pattern
# Use template, fill implementation from design doc Section 5.2

# Add event emission (15 min)
# Modify patterns/engine/pattern_executor.py

# Ground truth verification
python -c "from core.state.pattern_state_store import PatternStateStore; print('✓')"

# Commit
git add .
git commit -m "feat: pattern panel backend core"

# Update progress
# Edit .worktrees/pattern-panel-progress.yaml: backend_core.status = completed
```

#### Session 2: API Layer
```bash
cd .worktrees/wt-pattern-api

# Create client (30 min) - EXEC-002 pattern
# Use PatternClient template

# Add CLI commands (15 min)
# Modify core/ui_cli.py

# Create REST endpoints (15 min) - EXEC-002 pattern
# Copy from alignment doc Section 6

# Ground truth verification
python -m core.ui_cli pattern-events --job-id test --json

# Commit
git add .
git commit -m "feat: pattern panel API layer"
```

#### Session 3: Frontend
```bash
cd .worktrees/wt-pattern-frontend

# Create components (1.5 hours) - EXEC-002 pattern
# Use React component template for each:
# - PatternActivityPanel.tsx
# - TimelineView.tsx
# - SummaryHeader.tsx
# - DetailDrawer.tsx
# - utils.ts

# Ground truth verification
npm run build

# Commit
git add .
git commit -m "feat: pattern panel frontend components"
```

#### Session 4: Tests
```bash
cd .worktrees/wt-pattern-tests

# Create test files (1 hour) - EXEC-003 pattern
# Use test template for:
# - test_pattern_state_store.py
# - test_pattern_client.py
# - test_pattern_routes.py
# - test_pattern_flow.py

# Ground truth verification
pytest tests/ -q

# Commit
git add .
git commit -m "feat: pattern panel test suite"
```

---

### Merge Phase (15 minutes)

```bash
# Return to main checkout
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"

# Merge all branches (sequential to handle any conflicts)
git merge feature/pattern-panel-backend
git merge feature/pattern-panel-api
git merge feature/pattern-panel-frontend
git merge feature/pattern-panel-tests

# Run final validation
pytest tests/ -q
python -m core.ui_cli pattern-summary --job-id test --json

# Clean up worktrees
git worktree remove .worktrees/wt-pattern-backend
git worktree remove .worktrees/wt-pattern-api
git worktree remove .worktrees/wt-pattern-frontend
git worktree remove .worktrees/wt-pattern-tests

# Delete branches (optional)
git branch -d feature/pattern-panel-backend
git branch -d feature/pattern-panel-api
git branch -d feature/pattern-panel-frontend
git branch -d feature/pattern-panel-tests
```

---

## Success Metrics (Ground Truth)

### Phase 1: Backend Core ✅
- [ ] Migration file exists and runs without errors
- [ ] `PatternStateStore` class imports successfully
- [ ] Can save pattern run to database
- [ ] Can save pattern event to database
- [ ] Pattern events emitted from executor

### Phase 2: API Layer ✅
- [ ] `PatternClient` class imports successfully
- [ ] CLI commands return valid output
- [ ] REST endpoints return 200 status
- [ ] WebSocket connection establishes
- [ ] Pattern events streamed via WebSocket

### Phase 3: Frontend ✅
- [ ] All components render without errors
- [ ] WebSocket connection works from browser
- [ ] Timeline displays events
- [ ] Summary header shows statistics
- [ ] Detail drawer opens and shows data

### Phase 4: Tests ✅
- [ ] All unit tests pass
- [ ] Integration test completes successfully
- [ ] No import errors
- [ ] Coverage >70%

### Final Integration ✅
- [ ] All 4 worktree branches merged successfully
- [ ] Full test suite passes: `pytest tests/ -q`
- [ ] Pattern panel visible in GUI
- [ ] Live updates work end-to-end
- [ ] No performance issues with 100+ events

---

## Time Breakdown

### Traditional Approach (16-20 hours)
```
Planning: 2 hours
Backend development: 4 hours
API development: 3 hours
Frontend development: 5 hours
Testing: 4 hours
Integration: 2 hours
Total: 20 hours
```

### Pattern-Driven + Parallel (4-5 hours)
```
Setup (worktrees): 10 min
Parallel execution (4 sessions): 1.5 hours (longest worktree)
Merge & validation: 15 min
Buffer for issues: 2 hours
Total: 4-5 hours
```

**Speedup**: 4x faster

**ROI**:
- Template creation (one-time): Already done (design docs)
- Execution: 4-5 hours vs 20 hours = 15 hours saved
- Reusability: Templates work for future panel additions

---

## Critical Files Reference

From design documents:
1. `PATTERN_EXECUTION_VISUALIZATION_DESIGN.md` - Complete technical spec
2. `PATTERN_PANEL_GUI_ALIGNMENT.md` - Architecture alignment
3. `PATTERN_PANEL_INTEGRATION_CHECKLIST.md` - Step-by-step guide

From codebase:
1. `core/ui_clients/state_client.py` - Client pattern reference
2. `core/ui_cli.py` - CLI command pattern reference
3. `api/routes/*.py` - REST endpoint pattern reference
4. `core/state/db.py` - Database pattern reference

From PRMNT DOCS:
1. `EXECUTION_PATTERNS_LIBRARY.md` - Pattern templates
2. `PARALLEL_EXECUTION_STRATEGY.md` - Worktree strategy
3. `UTE_decision-elimination-playbook.md` - Decision elimination principles

---

## Decision Elimination Checklist

Before starting:
- [x] All structural decisions made (in templates)
- [x] File manifest defined (22 files)
- [x] Ground truth criteria established
- [x] Anti-pattern guards in place
- [x] Parallel execution strategy defined

During execution:
- [ ] No mid-flight architecture changes
- [ ] Trust templates as-is
- [ ] Verify with ground truth only
- [ ] Commit frequently (every 10-15 min)
- [ ] Update progress tracker after each worktree

After completion:
- [ ] All ground truth checks pass
- [ ] All worktrees merged
- [ ] Full test suite passes
- [ ] Pattern panel works end-to-end

---

## Next Steps After Completion

Phase 2 enhancements (defer to after Phase 1):
- Pattern analytics dashboard
- Pattern recommendations engine
- Pattern template editor UI
- Historical pattern performance tracking

**The Golden Rule**: Decide once → Apply N times → Trust ground truth → Move on

---

**END OF PLAN**

**Estimated total time**: 4-5 hours with 4x speedup via parallel worktrees and execution patterns
