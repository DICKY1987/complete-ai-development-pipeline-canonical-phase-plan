# Patch 009: Sub-Agent Architecture & Slash Commands - Summary

**Created**: 2025-11-23T12:57:11.337Z  
**Status**: ✅ READY TO APPLY  
**Priority**: HIGH

---

## What Was Done

✅ **Analyzed agents and custom commands architecture document**  
✅ **Created patch file**: `009-subagent-architecture-slash-commands.json` (3 operations)  
✅ **Updated apply_patches.py** to include sub-agent patch  
✅ **Defined 20+ sub-agents across 5 categories**  
✅ **Specified 15+ slash commands for user-initiated workflows**

---

## Overview

This patch documents a **three-tier architecture** that decomposes monolithic agent orchestration into specialized, bounded, testable components:

```
User (/command)
    ↓
Tier 1: Orchestrator (AGENT-ORCH-CORE)
    ↓
Tier 2: Sub-Agents (20+ specialized agents)
    ↓
Tier 3: Slash Commands (15+ user workflows)
```

---

## Three-Tier Architecture

### Tier 1: Orchestrator (Top-Level Agent)

**Agent**: `AGENT-ORCH-CORE`

**Responsibilities**:
- Select phase and workstream bundle
- Validate execution requests
- Route tasks to appropriate sub-agents
- Enforce quality gates and FILES_SCOPE
- Coordinate multi-step workflows
- Handle human-facing explanations

**When to Use**:
- High-level phase & workstream design
- Architecture redesign decisions
- Human negotiation and explanation
- Cross-cutting context and tradeoffs
- Freeform exploration

**NOT for**: Bounded, repeatable tasks (use sub-agents instead)

---

### Tier 2: Sub-Agents (Specialized Task Executors)

**Pattern**: Bounded, single-responsibility agents

**Characteristics**:
✅ Well-typed inputs and outputs (spec-governed)  
✅ Narrow scope within Phase + Workstream + FILES_SCOPE  
✅ No high-level planning or coordination  
✅ Deterministic and repeatable  
✅ Easy to test in isolation  
✅ Composable into larger workflows

**Contract**:
- **Input Schema**: Defined per sub-agent
- **Output Schema**: Defined per sub-agent
- **Constraints**: Phase, Workstream, FILES_SCOPE, safety_tier
- **Error Handling**: Return structured errors, never crash orchestrator

---

## 20+ Sub-Agents Defined (5 Categories)

### 1. ACS Sub-Agents (4 agents)

**Purpose**: AI Codebase Structure (PH-ACS) tasks

| Sub-Agent | ID | Task | Output |
|-----------|-----|------|--------|
| **ACS Index Builder** | SUB-ACS-INDEX | Scan modules, map layers, dependencies | CODEBASE_INDEX.yaml |
| **Quality Gate Synthesizer** | SUB-ACS-QUALITY-GATE | Enumerate checks, thresholds, gating rules | QUALITY_GATE.yaml |
| **Policy Deriver** | SUB-ACS-POLICY | Derive safe edit zones, review areas | ai_policies.yaml |
| **Guidance Writer** | SUB-ACS-GUIDANCE | Assemble AI onboarding doc | .meta/AI_GUIDANCE.md |

**Why Sub-Agents**: Deterministic, repeatable, safe to rerun on repo changes

---

### 2. Restructure Sub-Agents (5 agents)

**Purpose**: Restructure/Refactor pipeline tasks

| Sub-Agent | ID | Task | Output |
|-----------|-----|------|--------|
| **Restructure Planner** | SUB-RESTRUCTURE-PLANNER | Plan moves/merges (no edits) | RESTRUCTURE_CODEBASE_V1.yaml |
| **Restructure Simulator** | SUB-RESTRUCTURE-SIMULATOR | Dry-run, predict conflicts | simulation_report |
| **Patch Generator** | SUB-RESTRUCTURE-PATCH-GEN | Implement moves as patches | patch_files |
| **Import Fixer** | SUB-IMPORT-FIXER | Update imports after moves | import_fix_patches |
| **Validation Runner** | SUB-VALIDATION-RUNNER | Run tests on refactored code | validation_results |

**Why Sub-Agents**: High-impact operations need bounded scope and explicit safety checks

---

### 3. Error Pipeline Sub-Agents (4 agents)

**Purpose**: Error detection and self-healing

| Sub-Agent | ID | Task | Output |
|-----------|-----|------|--------|
| **Error Classifier** | SUB-ERROR-CLASSIFIER | Classify issue, tag severity | error_classification |
| **Fix Draft Generator** | SUB-FIX-DRAFT-GENERATOR | Propose fix patches | fix_patches |
| **Regression Validator** | SUB-REGRESSION-VALIDATOR | Run minimal test subset | validation_results |
| **Rollback Planner** | SUB-ROLLBACK-PLANNER | Create revert plan or PR | rollback_plan |

**Why Sub-Agents**: Classification logic separate from fix generation, clear audit trail

---

### 4. Spec Governance Sub-Agents (3 agents)

**Purpose**: Spec and schema governance

| Sub-Agent | ID | Task | Output |
|-----------|-----|------|--------|
| **Spec Lint Checker** | SUB-SPEC-LINT-CHECK | Validate specs conform to schema | validation_report |
| **Schema Sync Validator** | SUB-SCHEMA-SYNC | Check docs/schemas in sync | sync_report |
| **Change Impact Summarizer** | SUB-CHANGE-IMPACT-SUMMARIZER | Generate impact notes | impact_notes |

**Why Sub-Agents**: Validation runs before execution, separate concern

---

### 5. Repo Hygiene Sub-Agents (2 agents)

**Purpose**: Repo hygiene and staleness management

| Sub-Agent | ID | Task | Output |
|-----------|-----|------|--------|
| **Staleness Scanner** | SUB-STALENESS-SCANNER | Flag outdated/duplicate docs | STALE_CONTENT_REPORT.json |
| **Quarantine Planner** | SUB-QUARANTINE-PLANNER | Propose moves to quarantine/ | quarantine_plan |

**Why Sub-Agents**: Automated analysis without edits, obeys governance

---

### Tier 3: Slash Commands (User-Initiated Workflows)

**Pattern**: Named shortcuts that map to Phase + Workstream + Sub-Agent chains

**Characteristics**:
- Explicit user intent (less ambiguous than natural language)
- Deterministic and auditable (command → known workflow)
- Pre-baked ExecutionRequest templates
- User controls when high-impact operations run

**Structure**:
```json
{
  "command_id": "/acs-init",
  "phase_id": "PH-ACS",
  "workstream_bundle_id": "ACS-INIT-BUNDLE",
  "subagent_chain": ["SUB-ACS-INDEX", "SUB-ACS-QUALITY-GATE", "SUB-ACS-POLICY", "SUB-ACS-GUIDANCE"],
  "parameters": [],
  "validation": "Pre-execution checks"
}
```

---

## 15+ Slash Commands Defined

### ACS Commands (4 commands)

| Command | Description | Sub-Agents | Output |
|---------|-------------|------------|--------|
| `/acs-init` | Initialize ACS artifacts | 4 agents | All ACS files |
| `/acs-refresh-index` | Rebuild CODEBASE_INDEX | 1 agent | CODEBASE_INDEX.yaml |
| `/acs-refresh-policies` | Update ai_policies | 1 agent | ai_policies.yaml |
| `/acs-guidance` | Regenerate AI_GUIDANCE | 1 agent | .meta/AI_GUIDANCE.md |

---

### Restructure Commands (4 commands)

| Command | Description | Sub-Agents | Safety |
|---------|-------------|------------|--------|
| `/restruct-plan` | Create restructure plan (no edits) | PLANNER | Read-only |
| `/restruct-dryrun` | Simulate, produce report only | SIMULATOR | Read-only |
| `/restruct-apply` | Apply approved plan | PATCH-GEN + FIXER + VALIDATOR | Requires approved spec |
| `/restruct-rollback` | Rollback last restructure | ROLLBACK-PLANNER | Uses ledger |

---

### Error Commands (4 commands)

| Command | Description | Sub-Agents | Output |
|---------|-------------|------------|--------|
| `/err-diagnose` | Classify last error | CLASSIFIER | error_classification |
| `/err-fix` | Generate fix patch | FIX-GENERATOR | fix_patches |
| `/err-verify` | Run minimal validation | VALIDATOR | validation_results |
| `/err-open-pr` | Package fix into PR | ROLLBACK-PLANNER | GitHub PR URL |

---

### Hygiene Commands (3 commands)

| Command | Description | Sub-Agents | Output |
|---------|-------------|------------|--------|
| `/stale-scan` | Scan for stale content | STALENESS-SCANNER | STALE_CONTENT_REPORT.json |
| `/stale-quarantine` | Move to quarantine/ | QUARANTINE-PLANNER | quarantine_patches |
| `/docs-index` | Rebuild docs index | ACS-INDEX | docs_index |

---

### Observability Commands (4 commands)

| Command | Description | Read-Only | Output |
|---------|-------------|-----------|--------|
| `/phase-status` | Show phase status | ✅ | phase_status_report |
| `/ws-status` | Show workstream status | ✅ | workstream_status_report |
| `/ledger-last [n]` | Show last N ledger entries | ✅ | ledger_entries |
| `/graph` | Render dependency graph | ✅ | graph_visualization |

---

## Execution Flow

### Example: `/acs-init`

```
1. User types: /acs-init
2. SlashCommandRouter validates command
3. Orchestrator creates ExecutionRequest from template:
   - phase_id: PH-ACS
   - workstream_bundle_id: ACS-INIT-BUNDLE
   - subagent_chain: [SUB-ACS-INDEX, SUB-ACS-QUALITY-GATE, ...]
4. Orchestrator executes sub-agents in order:
   a. SUB-ACS-INDEX → CODEBASE_INDEX.yaml
   b. SUB-ACS-QUALITY-GATE → QUALITY_GATE.yaml
   c. SUB-ACS-POLICY → ai_policies.yaml
   d. SUB-ACS-GUIDANCE → .meta/AI_GUIDANCE.md
5. Orchestrator aggregates results
6. Ledger records execution
7. Results returned to user
```

---

## Benefits

### Predictability
Each sub-agent has well-defined inputs/outputs, no surprises

### Testability
Sub-agents tested in isolation with mock inputs

### Auditability
Clear logs of which sub-agent ran, inputs, outputs

### Safety
Bounded scope prevents accidental wide-ranging changes

### Reusability
Sub-agents compose into different workflows

### User Control
Slash commands give explicit control over high-impact operations

### Debugging
Easy to identify which sub-agent failed and why

### Parallel Execution
Independent sub-agents can run concurrently

---

## Implementation Roadmap

### Phase 1: Foundation
- Define BaseSubAgent interface (input_schema, output_schema, execute())
- Create SlashCommand registry and router
- Implement orchestrator sub-agent routing logic
- Add sub-agent execution to ledger tracking

### Phase 2: ACS Sub-Agents
- Implement SUB-ACS-INDEX
- Implement SUB-ACS-QUALITY-GATE
- Implement SUB-ACS-POLICY
- Implement SUB-ACS-GUIDANCE
- Wire up /acs-* commands

### Phase 3: Restructure Sub-Agents
- Implement SUB-RESTRUCTURE-PLANNER
- Implement SUB-RESTRUCTURE-SIMULATOR
- Implement SUB-RESTRUCTURE-PATCH-GEN
- Implement SUB-IMPORT-FIXER
- Wire up /restruct-* commands

### Phase 4: Error Sub-Agents
- Implement SUB-ERROR-CLASSIFIER
- Implement SUB-FIX-DRAFT-GENERATOR
- Implement SUB-REGRESSION-VALIDATOR
- Wire up /err-* commands

---

## Design Philosophy

### Separation of Concerns
Each sub-agent handles one well-defined task with clear inputs/outputs

### Deterministic Workflows
Sub-agents produce predictable results, easy to test and audit

### User Control
Slash commands give explicit control over when high-impact operations run

### Orchestration Over Autonomy
Top-level orchestrator routes tasks, sub-agents execute within constraints

---

## Integration with Existing Systems

### With Tool Adapters (Patch 007)
Sub-agents use tool adapters for external tool execution:
```python
# SUB-ACS-INDEX uses tool adapters
def execute(self, input_data):
    adapter = registry.get("ruff")
    result = adapter.execute(scan_request)
    # Process result to build CODEBASE_INDEX.yaml
```

### With Resilience Patterns (Patch 008)
Sub-agents wrapped with resilient executor:
```python
# Orchestrator wraps sub-agent calls
executor = ResilientExecutor()
executor.register_tool("SUB-ACS-INDEX", failure_threshold=3)

result = executor.execute(
    "SUB-ACS-INDEX",
    lambda: subagent.execute(input_data)
)
```

### With Workstream Execution
Sub-agents map to workstream tasks:
```yaml
workstream:
  tasks:
    - task_id: "build-acs-index"
      subagent: "SUB-ACS-INDEX"
      input_from: "repo_root"
      output_to: "CODEBASE_INDEX.yaml"
```

---

## Statistics

| Metric | Value |
|--------|-------|
| **Sub-Agents Defined** | 20+ |
| **Slash Commands** | 15+ |
| **Categories** | 5 (ACS, Restructure, Error, Governance, Hygiene) |
| **Phases Covered** | 6 (PH-ACS, PH-RESTRUCTURE, PH-ERROR, etc.) |
| **Implementation Status** | Planned (0% complete) |
| **Priority** | HIGH |

---

## Updated Patch Summary

After adding Patch 009:

| Patch | Operations | What It Adds |
|-------|------------|--------------|
| **001** | 22 | Config files, architecture, Phase 7 |
| **002** | 15 | AI tool config, sandbox, docs |
| **003** | 25 | State machines, contracts, DAG |
| **004** | 18 | Complete plan, prompts, errors |
| **005** | 11 | ADRs, design principles |
| **007** | 3 | Tool Adapter pattern |
| **008** | 2 | Resilience patterns |
| **009** | 3 | **Sub-Agent architecture, slash commands** |
| **TOTAL** | **99** | **Complete UET V2 Foundation + Agent Architecture** |

---

## How to Apply

```bash
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\PATCH_PLAN_JSON"

# Apply all 8 patches
python apply_patches.py
```

---

## Validation

```python
import json
plan = json.loads(open("UET_V2_MASTER_PLAN.json").read())

# Check subagent_architecture added
assert "subagent_architecture" in plan["meta"]

# Check tiers documented
arch = plan["meta"]["subagent_architecture"]["architecture_tiers"]
assert "tier_1_orchestrator" in arch
assert "tier_2_subagents" in arch
assert "tier_3_slash_commands" in arch

# Check sub-agents defined
categories = arch["tier_2_subagents"]["categories"]
assert "acs_subagents" in categories
assert "restructure_subagents" in categories
assert "error_pipeline_subagents" in categories

# Check slash commands
commands = arch["tier_3_slash_commands"]["command_registry"]
assert "acs_commands" in commands
assert len(commands["acs_commands"]) >= 4
```

---

**Status**: ✅ **READY TO APPLY**

Patch 009 adds the architectural blueprint for decomposing monolithic orchestration into specialized, testable sub-agents with user-friendly slash commands! 🎯
