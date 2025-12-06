---
doc_id: DOC-GUIDE-WORKSTREAM-MULTI-CLI-FILE-MAP-242
---

# Core Files for Workstreams & Multi-Parallel CLI Execution

**Generated**: 2025-12-05 03:59

---

## 📍 SPECIFICATIONS (Core Concepts)

Location: `phase1_planning\modules\spec_parser\docs\specifications\specs\`

### Primary Specs:
1. **UET_WORKSTREAM_SPEC.md** - Complete workstream specification
2. **UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md** - Parallel execution strategy
3. **MULTI_CLI_WORKTREES_EXECUTION_SPEC.md** - Multi-CLI control via worktrees
4. **UET_CLI_TOOL_EXECUTION_SPEC.md** - CLI tool execution framework

---

## 🏗️ CORE IMPLEMENTATION

### Workstream State Management
- `core\state\worktree.py` - Worktree state tracking
- `core\state\db_unified.py` - Unified database for workstream state
- `core\state\dag_utils.py` - DAG utilities for workstream dependencies
- `core\state\bundles.py` - Workstream bundle management

### Engine Components
- `core\engine\orchestrator.py` - Main orchestrator (workstream coordination)
- `core\engine\scheduler.py` - Workstream scheduling
- `core\engine\executor.py` - Workstream execution
- `core\engine\dag_builder.py` - DAG construction for parallel execution
- `core\engine\parallel_orchestrator.py` - Parallel orchestration (ARCHIVED version exists)

### Planning & Parallelism Detection
- `core\planning\planner.py` - Workstream planner
- `core\planning\ccpm_integration.py` - Critical Chain Project Management

---

## 📋 WORKSTREAM DEFINITIONS

Location: `phase1_planning\modules\workstream_planner\docs\plans\workstreams\`

### Active Workstreams:
- ws-next-001 through ws-next-005 (Next iteration workstreams)
- ws-abs-001 through ws-abs-012 (Abstract/foundation workstreams)
- ws-10 through ws-30 (Pipeline integration workstreams)

### Workstream Templates:
- `phase1_planning\modules\workstream_planner\docs\plans\templates\workstreams\`

### Example Workstreams:
- `02_parallel_execution.json` - Example of parallel execution pattern

---

## 🔧 TOOLS & VALIDATION

### Workstream Tools:
- `phase4_routing\modules\tool_adapters\src\tools\workstream_validator.py`
- `phase4_routing\modules\tool_adapters\src\tools\workstream_converter.py`
- `phase4_routing\modules\tool_adapters\src\tools\validation\validate_workstreams.py`
- `phase4_routing\modules\tool_adapters\src\tools\validation\validate_workstreams_authoring.py`

### Workstream Generation:
- `phase4_routing\modules\tool_adapters\src\tools\generation\generate_workstreams.py`
- `phase4_routing\modules\tool_adapters\src\tools\generation\generate_workstreams_from_openspec.py`

### Scripts:
- `scripts\run_workstream.py` - Main workstream executor
- `scripts\execute_next_workstreams.py` - Execute next planned workstreams
- `scripts\multi_agent_orchestrator.py` - Multi-agent coordination
- `scripts\monitor_parallel.py` - Monitor parallel execution
- `scripts\worktree_manager.py` - Git worktree management

---

## 📚 DOCUMENTATION & GUIDES

### Operational Guides:
- `docs\DOC_operations\PARALLEL_EXECUTION_STRATEGY.md` ⭐ **Key Guide**
- `docs\DOC_operations\MULTI_AGENT_ORCHESTRATION_GUIDE.md` ⭐ **Key Guide**
- `docs\DOC_operations\WORKSTREAM_SYNC_GUIDE.md`
- `docs\DOC_operations\DOC_WORKSTREAM_PROMPT_STRUCTURE.md`

### Execution Patterns:
- `patterns\EXECUTION_PATTERNS_LIBRARY.md` ⭐ **Pattern Catalog**
- `docs\DOC_reference\ai-agents\EXECUTION_PATTERNS_MANDATORY.md` ⭐ **Mandatory Reading**
- `patterns\EXECUTION_ACCELERATION_ANALYSIS.md`

### Multi-CLI Control:
- `core\MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md` ⭐ **3-Week Implementation Plan**

### Quick References:
- `core\NEXT_WORKSTREAMS_QUICKSTART.md`
- `core\MULTI_AGENT_CONSOLIDATION_QUICKREF.md`
- `phase1_planning\modules\workstream_planner\docs\plans\WORKSTREAM_SYNC_QUICKREF.md`

---

## 🧪 TESTS

### Workstream Tests:
- `tests\pipeline\test_workstream_authoring.py`
- `tests\pipeline\test_bundles.py`
- `tests\planning\test_planner.py`

### Parallel Execution Tests:
- `tests\test_parallel_orchestrator.py`
- `tests\test_parallel_dependencies.py`
- `tests\test_parallelism_detection.py`
- `tests\engine\test_scheduling.py`
- `tests\engine\test_dag_builder.py`

---

## 🎯 EXECUTION PATTERN SPECS

Location: `patterns\specs\`

- `multi_workstream_doc_suite_generation.pattern.yaml` - Multi-workstream pattern
- `multi_agent_orchestration.pattern.md` - Multi-agent coordination
- `GH_SYNC_PHASE_V1.pattern.yaml` - GitHub sync pattern

Pattern Executors:
- `patterns\executors\multi_workstream_doc_suite_gen_001_executor.ps1`
- `patterns\executors\lib\parallel.ps1`

---

## 📊 SCHEMAS & REGISTRIES

### Workstream Schemas:
- `_ARCHIVE\phase0_bootstrap_orchestrator_duplicate_20251204_143704\bootstrap_orchestrator\schemas\schema\workstream_spec.v1.json`
- `_ARCHIVE\phase0_bootstrap_orchestrator_duplicate_20251204_143704\bootstrap_orchestrator\schemas\schema\workstream.schema.json`

### Pattern Schemas:
- `patterns\schemas\multi_workstream_doc_suite_gen_001.schema.json`

### Registries:
- `patterns\registry\PATTERN_INDEX.yaml` - All execution patterns indexed
- `patterns\registry\OPERATION_KIND_REGISTRY.yaml`

---

## 🔍 YOUR DOWNLOADED FILES vs SYSTEM FILES

### Your Downloaded Files:
1. `C:\Users\richg\Downloads\PRMNT DOCS\DOC_MULTI_CLI_WORKTREES_EXECUTION_SPEC.md.md`
   - **System Location**: `phase1_planning\modules\spec_parser\docs\specifications\specs\MULTI_CLI_WORKTREES_EXECUTION_SPEC.md`

2. `C:\Users\richg\Downloads\PRMNT DOCS\agentworknow\COE_MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md`
   - **System Location**: `core\MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md`

3. `C:\Users\richg\Downloads\UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`
   - **System Location**: `phase1_planning\modules\spec_parser\docs\specifications\specs\UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`

4. `C:\Users\richg\Downloads\UET_WORKSTREAM_SPEC.md`
   - **System Location**: `phase1_planning\modules\spec_parser\docs\specifications\specs\UET_WORKSTREAM_SPEC.md`

---

## 🚀 QUICK START - WHERE TO BEGIN

### 1. Read These First (15 minutes):
   - `docs\DOC_reference\ai-agents\EXECUTION_PATTERNS_MANDATORY.md`
   - `core\NEXT_WORKSTREAMS_QUICKSTART.md`

### 2. Understand Specs (30 minutes):
   - `phase1_planning\modules\spec_parser\docs\specifications\specs\UET_WORKSTREAM_SPEC.md`
   - `phase1_planning\modules\spec_parser\docs\specifications\specs\UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`

### 3. Review Implementation (20 minutes):
   - `core\engine\orchestrator.py`
   - `core\state\worktree.py`
   - `scripts\run_workstream.py`

### 4. Study Patterns (20 minutes):
   - `patterns\EXECUTION_PATTERNS_LIBRARY.md`
   - `docs\DOC_operations\PARALLEL_EXECUTION_STRATEGY.md`

### 5. See Examples (15 minutes):
   - `phase1_planning\modules\workstream_planner\docs\plans\workstreams\examples\02_parallel_execution.json`
   - `patterns\examples\multi_workstream_doc_suite_gen_001\`

---

## 💡 KEY CONCEPTS TO UNDERSTAND

### Workstreams
A **workstream** is a unit of coordinated work that can contain multiple tasks, execute in parallel with other workstreams, and track dependencies.

**Files**: `UET_WORKSTREAM_SPEC.md`, `core\state\worktree.py`

### Multi-CLI Execution
The ability to run **multiple CLI tool instances** (aider, codex, claude) simultaneously in separate processes or git worktrees.

**Files**: `MULTI_CLI_WORKTREES_EXECUTION_SPEC.md`, `core\MULTI_INSTANCE_CLI_CONTROL_PHASE_PLAN.md`

### Parallel Execution Strategy
Using **git worktrees + parallel processes** to achieve 3x-10x speedup on batch tasks.

**Files**: `UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md`, `docs\DOC_operations\PARALLEL_EXECUTION_STRATEGY.md`

### Execution Patterns
Reusable **templates for common tasks** (EXEC-001 through EXEC-009) that eliminate decision overhead.

**Files**: `patterns\EXECUTION_PATTERNS_LIBRARY.md`, `docs\DOC_reference\ai-agents\EXECUTION_PATTERNS_MANDATORY.md`

---

## 📞 SUPPORT DOCS

### Architecture:
- `docs\DOC_reference\CODEBASE_INDEX.yaml` - Full system structure
- `docs\DOC_reference\DOC_ARCHITECTURE.md` - Architecture overview

### Diagrams:
- `docs\DOC_diagrams\DOC_VISUAL_ARCHITECTURE_GUIDE.md`
- `docs\DOC_diagrams\data-flow-workstream.mmd`

### State Machines:
- `docs\DOC_state_machines\workstream_lifecycle.yaml`
- `docs\DOC_state_machines\STATE_MACHINES.md`

---

**END OF SUMMARY**
