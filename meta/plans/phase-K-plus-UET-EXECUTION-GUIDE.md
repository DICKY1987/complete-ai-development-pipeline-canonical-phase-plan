# Phase K+ Execution Using Universal Execution Templates (UET)

**Created:** 2025-11-22  
**Phase Plan:** `phase-K-plus-decision-context.md`  
**UET Framework:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`  
**Status:** Ready for Execution

---

## Overview

This guide shows how to use the **Universal Execution Templates (UET) Framework** to orchestrate and execute the Phase K+ plan. UET provides autonomous workflow management, parallel execution, resilience patterns, and progress tracking.

### Why Use UET for Phase K+?

- **Automated Orchestration:** Define tasks once, let UET handle execution order
- **Parallel Execution:** Run independent tasks simultaneously (e.g., multiple ADRs)
- **Progress Tracking:** Real-time monitoring of week-by-week progress
- **Resilience:** Automatic retry, circuit breakers, crash recovery
- **Cost Tracking:** Monitor AI tool usage and stay within budgets

---

## Quick Start

### 1. Bootstrap the Project

```bash
# Navigate to UET framework
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"

# Bootstrap the main project
python core/bootstrap/orchestrator.py "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# This generates:
# - PROJECT_PROFILE.yaml (auto-detected: documentation project)
# - router_config.json (tool routing for aider, pytest, etc.)
# - .uet/ directory (runtime state)
```

### 2. Create Phase K+ Workstream Bundle

The Phase K+ plan is already structured as weeks. Convert it to a UET workstream bundle:

```bash
# Use conversion script (to be created)
python scripts/convert_phase_to_workstream.py \
  meta/plans/phase-K-plus-decision-context.md \
  --output workstreams/phase-k-plus-bundle.json
```

Or manually create the bundle (see section below).

### 3. Execute the Plan

```bash
# Run the full Phase K+ workstream
python scripts/run_workstream.py workstreams/phase-k-plus-bundle.json

# Or use UET orchestrator directly
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
python core/engine/orchestrator.py ../workstreams/phase-k-plus-bundle.json
```

---

## Phase K+ as UET Workstream Bundle

Here's how the Phase K+ plan maps to UET structure:

### Bundle Structure

```json
{
  "bundle_id": "phase-k-plus",
  "bundle_name": "Phase K+: Decision Context Enhancement",
  "description": "Add critical decision-making context to documentation",
  "version": "1.0.0",
  "estimated_duration_hours": 32,
  "max_cost_usd": 50.0,
  "workstreams": [
    {
      "ws_id": "WS-K0-FOUNDATION",
      "name": "Week 0: Phase K Foundation Completion (Optional)",
      "kind": "docs",
      "priority": "background",
      "parallel_ok": true,
      "estimated_context_tokens": 5000,
      "max_cost_usd": 5.0,
      "steps": [...]
    },
    {
      "ws_id": "WS-K1-CRITICAL",
      "name": "Week 1: Critical Foundations",
      "kind": "docs",
      "priority": "foreground",
      "parallel_ok": true,
      "steps": [...]
    },
    {
      "ws_id": "WS-K2-RUNTIME",
      "name": "Week 2: Runtime & Testing",
      "depends_on": ["WS-K1-CRITICAL"],
      "steps": [...]
    },
    {
      "ws_id": "WS-K3-DEPENDENCIES",
      "name": "Week 3: Dependencies & Errors",
      "depends_on": ["WS-K2-RUNTIME"],
      "steps": [...]
    },
    {
      "ws_id": "WS-K4-PERFORMANCE",
      "name": "Week 4: Performance & State",
      "depends_on": ["WS-K3-DEPENDENCIES"],
      "steps": [...]
    }
  ]
}
```

### Week 0 Workstream (Optional)

```json
{
  "ws_id": "WS-K0-FOUNDATION",
  "name": "Week 0: Phase K Foundation Completion (Optional)",
  "description": "K-1 cleanup and K-4 cross-references",
  "kind": "docs",
  "priority": "background",
  "parallel_ok": true,
  "estimated_context_tokens": 5000,
  "max_cost_usd": 5.0,
  "steps": [
    {
      "step_id": "k0-01-fix-links",
      "name": "Fix 74 Broken Documentation Links",
      "tool_profile_id": "aider",
      "context": {
        "files": [
          "docs/ARCHITECTURE.md",
          "docs/DIRECTORY_GUIDE.md",
          "docs/README.md"
        ],
        "instruction": "Fix broken internal markdown links identified by link validator. Update src/pipeline/ references to core/, fix case sensitivity, remove links to deleted files."
      },
      "validation": {
        "test_command": "python scripts/generate_doc_index.py --fail-on-broken-links",
        "expected_exit_code": 0
      }
    },
    {
      "step_id": "k0-02-find-terms",
      "name": "Find 6 Missing Term Locations",
      "tool_profile_id": "aider",
      "context": {
        "files": [
          "scripts/generate_implementation_map.py",
          "docs/IMPLEMENTATION_LOCATIONS.md"
        ],
        "instruction": "Refine search patterns to locate: Spec Patcher, URI Resolution, Checkpoint, AIM Bridge, Profile Matching, Compensation Action. Check specifications/tools/, core/state/, aim/bridge.py"
      }
    },
    {
      "step_id": "k0-03-term-graph",
      "name": "Create Term Relationships Graph",
      "tool_profile_id": "aider",
      "depends_on": ["k0-02-find-terms"],
      "context": {
        "files": [],
        "create_files": [
          "docs/TERM_RELATIONSHIPS.md",
          "scripts/generate_term_graph.py"
        ],
        "instruction": "Build hierarchical graph of 47 terms with parent-child and dependency relationships. Use NetworkX for graph analysis."
      }
    },
    {
      "step_id": "k0-04-cross-refs",
      "name": "Generate Cross-Reference Index",
      "tool_profile_id": "aider",
      "depends_on": ["k0-03-term-graph"],
      "context": {
        "create_files": [
          "docs/CROSS_REFERENCE_INDEX.md",
          "scripts/generate_cross_references.py"
        ],
        "instruction": "Create bi-directional reference map. For each term: 'Used by', 'Uses', 'Related to'. Include code references (file:line) and doc links."
      }
    }
  ],
  "completion_criteria": [
    "All high-priority documentation links valid",
    "All 47 terms have at least one auto-detected location",
    "Term relationships graph complete",
    "Cross-reference index generated"
  ]
}
```

### Week 1 Workstream (Critical)

```json
{
  "ws_id": "WS-K1-CRITICAL",
  "name": "Week 1: Critical Foundations",
  "description": "ADRs, Change Impact Matrix, Anti-Patterns",
  "kind": "docs",
  "priority": "foreground",
  "parallel_ok": true,
  "depends_on": [],
  "estimated_context_tokens": 8000,
  "max_cost_usd": 10.0,
  "steps": [
    {
      "step_id": "k1-01-adr-structure",
      "name": "Create ADR Directory and Template",
      "tool_profile_id": "aider",
      "context": {
        "create_files": [
          "docs/adr/README.md",
          "docs/adr/template.md"
        ],
        "instruction": "Create docs/adr/ with template following format in phase plan. Include Status, Date, Deciders, Context, Decision, Rationale, Consequences, Alternatives, Related Decisions sections."
      }
    },
    {
      "step_id": "k1-02-adr-workstream",
      "name": "ADR-0001: Workstream Model Choice",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "context": {
        "create_files": ["docs/adr/0001-workstream-model-choice.md"],
        "instruction": "Document why workstream over task graph. Reference core/engine/orchestrator.py, schema/workstream.schema.json. Include alternatives: task DAG, event-driven, imperative scripts."
      }
    },
    {
      "step_id": "k1-03-adr-hybrid",
      "name": "ADR-0002: Hybrid Architecture",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0002-hybrid-architecture.md"],
        "instruction": "Document GUI/Terminal/TUI decision. Reference engine/README.md, gui/ design docs. Explain job-based execution pattern."
      }
    },
    {
      "step_id": "k1-04-adr-sqlite",
      "name": "ADR-0003: SQLite State Storage",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0003-sqlite-state-storage.md"],
        "instruction": "Document why SQLite vs PostgreSQL/Redis. Reference .worktrees/pipeline_state.db, core/state/db.py. Include tradeoffs: simplicity vs scaling."
      }
    },
    {
      "step_id": "k1-05-adr-sections",
      "name": "ADR-0004: Section-Based Organization",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0004-section-based-organization.md"],
        "instruction": "Document why core/, error/, aim/ structure. Reference docs/SECTION_REFACTOR_MAPPING.md. Explain migration from src/pipeline/."
      }
    },
    {
      "step_id": "k1-06-adr-python",
      "name": "ADR-0005: Python Primary Language",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0005-python-primary-language.md"],
        "instruction": "Document Python + PowerShell strategy. Reference scripts/, AGENTS.md. Include reasoning: ecosystem, AI tooling, Windows-first."
      }
    },
    {
      "step_id": "k1-07-adr-specs",
      "name": "ADR-0006: Specifications Unified Management",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0006-specifications-unified-management.md"],
        "instruction": "Document spec system design. Reference specifications/tools/, openspec/. Explain consolidation from scattered spec files."
      }
    },
    {
      "step_id": "k1-08-adr-plugins",
      "name": "ADR-0007: Error Plugin Architecture",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0007-error-plugin-architecture.md"],
        "instruction": "Document plugin vs monolith. Reference error/plugins/, error/engine/. Include plugin discovery, manifest.json pattern."
      }
    },
    {
      "step_id": "k1-09-adr-db-location",
      "name": "ADR-0008: Database Location Worktree",
      "tool_profile_id": "aider",
      "depends_on": ["k1-01-adr-structure"],
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/adr/0008-database-location-worktree.md"],
        "instruction": "Document why .worktrees/pipeline_state.db. Reference PIPELINE_DB_PATH env var. Include reasoning: git-ignored, per-worktree isolation."
      }
    },
    {
      "step_id": "k1-10-impact-matrix",
      "name": "Create Change Impact Matrix",
      "tool_profile_id": "aider",
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/reference/CHANGE_IMPACT_MATRIX.md"],
        "instruction": "Document critical dependencies: Schema changes → regenerate indices; core/state/db.py → update tests/migrations; schema/ → validate workstreams; error/plugins/ → update manifest/docs; specifications/tools/ → update spec index. Include validation commands for each."
      }
    },
    {
      "step_id": "k1-11-anti-patterns",
      "name": "Create Anti-Patterns Catalog",
      "tool_profile_id": "aider",
      "parallel_ok": true,
      "context": {
        "create_files": ["docs/guidelines/ANTI_PATTERNS.md"],
        "instruction": "Document anti-patterns by section: Core State (direct file DB access, missing migrations), Error Engine (skip plugin manifest, non-incremental scans), Specifications (circular deps, missing URI resolution), Scripts (hardcoded paths, no error handling), Testing (network calls, non-deterministic assertions). Include BAD/GOOD code examples."
      }
    },
    {
      "step_id": "k1-12-update-index",
      "name": "Update Documentation Index",
      "tool_profile_id": "aider",
      "depends_on": ["k1-02-adr-workstream", "k1-10-impact-matrix", "k1-11-anti-patterns"],
      "context": {
        "files": ["docs/DOCUMENTATION_INDEX.md"],
        "instruction": "Add links to new docs/adr/ section, CHANGE_IMPACT_MATRIX.md, ANTI_PATTERNS.md. Regenerate index if needed."
      },
      "validation": {
        "test_command": "python scripts/generate_doc_index.py",
        "expected_exit_code": 0
      }
    }
  ],
  "test_gates": [
    {
      "type": "GATE_DOCS",
      "required": true,
      "blocking": true,
      "command": "python scripts/generate_doc_index.py --fail-on-broken-links"
    }
  ],
  "completion_criteria": [
    "8 ADRs created and linked from index",
    "Change impact matrix covers 20+ dependencies",
    "Anti-patterns catalog has 15+ examples",
    "All documentation links valid"
  ]
}
```

### Week 2-4 Workstreams

Similar structure for:
- **WS-K2-RUNTIME:** Execution traces (5 workflows), Testing strategy guide
- **WS-K3-DEPENDENCIES:** Dependency graphs, Error catalog (20+ errors), Data flows
- **WS-K4-PERFORMANCE:** Performance profiles, State machines, Automation, Final integration

---

## Execution Patterns

### Sequential Execution (Default)

```bash
# Execute workstreams in dependency order: K0 → K1 → K2 → K3 → K4
python core/engine/orchestrator.py ../workstreams/phase-k-plus-bundle.json
```

### Parallel Step Execution

Within each week, independent steps run in parallel:

```python
# Week 1: ADRs 0001-0008 run in parallel (all depend on k1-01-adr-structure)
# UET automatically:
# 1. Runs k1-01-adr-structure first
# 2. Spawns 8 parallel workers for ADRs 0001-0008
# 3. Waits for all to complete before k1-12-update-index
```

### Skip Optional Week 0

```bash
# Execute only critical path (Weeks 1-4)
python core/engine/orchestrator.py ../workstreams/phase-k-plus-bundle.json \
  --skip-workstream WS-K0-FOUNDATION
```

### Resume After Failure

```bash
# UET automatically saves state to .uet/runs/<run_id>/
# Resume from checkpoint:
python core/engine/orchestrator.py ../workstreams/phase-k-plus-bundle.json \
  --resume <run_id>
```

---

## Monitoring Progress

### Real-Time Progress Tracking

```python
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.monitoring import RunMonitor

# Monitor active run
monitor = RunMonitor(run_id="phase-k-plus-20251122")
status = monitor.get_status()

print(f"Progress: {status.progress_pct}%")
print(f"Current Step: {status.current_step}")
print(f"Completed: {status.completed_count}/{status.total_count}")
print(f"Cost: ${status.total_cost_usd:.2f}")
```

### Progress Output

```
=== Phase K+ Execution ===
Week 0: Foundation [OPTIONAL] ........................ ⏭️  SKIPPED
Week 1: Critical Foundations ......................... 🔄 IN PROGRESS (8/12 steps)
  ✅ k1-01-adr-structure
  ✅ k1-02-adr-workstream
  ✅ k1-03-adr-hybrid
  ✅ k1-04-adr-sqlite
  ✅ k1-05-adr-sections
  ✅ k1-06-adr-python
  ✅ k1-07-adr-specs
  ✅ k1-08-adr-plugins
  🔄 k1-09-adr-db-location (Running)
  ⏳ k1-10-impact-matrix (Waiting)
  ⏳ k1-11-anti-patterns (Waiting)
  ⏳ k1-12-update-index (Blocked on previous)

Week 2: Runtime & Testing ............................ ⏳ PENDING
Week 3: Dependencies & Errors ........................ ⏳ PENDING
Week 4: Performance & State .......................... ⏳ PENDING

Progress: 22% | Cost: $4.25 | ETA: 3.2 hours
```

---

## Resilience Features

### Automatic Retry

```json
{
  "step_id": "k1-02-adr-workstream",
  "tool_profile_id": "aider",
  "resilience": {
    "max_retries": 3,
    "backoff_strategy": "exponential",
    "retry_on": ["timeout", "rate_limit", "transient_error"]
  }
}
```

### Circuit Breaker

```json
{
  "workstream": {
    "circuit_breaker": {
      "failure_threshold": 5,
      "timeout_seconds": 300,
      "half_open_after": 60
    }
  }
}
```

### Cost Budget Enforcement

```json
{
  "workstream": {
    "max_cost_usd": 10.0,
    "on_budget_exceeded": "pause_and_notify"
  }
}
```

---

## Tool Routing

UET automatically routes tasks to appropriate tools based on `router_config.json`:

```json
{
  "routes": [
    {
      "task_kind": "docs",
      "file_patterns": ["*.md", "docs/**"],
      "tools": ["aider"],
      "priority": "high"
    },
    {
      "task_kind": "code_edit",
      "file_patterns": ["*.py"],
      "tools": ["aider", "cursor"],
      "priority": "high"
    },
    {
      "task_kind": "testing",
      "tools": ["pytest"],
      "priority": "critical"
    }
  ]
}
```

---

## Validation Gates

Each workstream can define test gates:

```json
{
  "test_gates": [
    {
      "type": "GATE_LINT",
      "required": false,
      "blocking": false,
      "command": "markdownlint docs/**/*.md"
    },
    {
      "type": "GATE_DOCS",
      "required": true,
      "blocking": true,
      "command": "python scripts/generate_doc_index.py --fail-on-broken-links"
    }
  ]
}
```

Gates run automatically after workstream completion.

---

## Creating the Workstream Bundle

### Option 1: Manual Creation

Create `workstreams/phase-k-plus-bundle.json` using the examples above.

### Option 2: Conversion Script (Recommended)

```bash
# Create conversion utility
cat > scripts/convert_phase_to_workstream.py << 'EOF'
#!/usr/bin/env python3
"""Convert Phase K+ markdown plan to UET workstream bundle."""

import json
import re
from pathlib import Path

def parse_phase_plan(md_path):
    """Parse Phase K+ markdown and extract weeks/tasks."""
    # Read markdown
    content = Path(md_path).read_text()
    
    # Extract weeks using regex
    weeks = re.findall(r'### (Week \d+).*?\n\n(.*?)(?=###|$)', content, re.DOTALL)
    
    workstreams = []
    for i, (week_title, week_content) in enumerate(weeks):
        # Parse tasks from deliverables
        tasks = re.findall(r'- \[ \] (.+)', week_content)
        
        steps = []
        for j, task in enumerate(tasks):
            steps.append({
                "step_id": f"k{i}-{j:02d}",
                "name": task,
                "tool_profile_id": "aider",
                "context": {
                    "instruction": f"Implement: {task}"
                }
            })
        
        workstreams.append({
            "ws_id": f"WS-K{i}",
            "name": week_title,
            "kind": "docs",
            "priority": "foreground" if i > 0 else "background",
            "steps": steps
        })
    
    return {
        "bundle_id": "phase-k-plus",
        "bundle_name": "Phase K+: Decision Context Enhancement",
        "workstreams": workstreams
    }

if __name__ == "__main__":
    import sys
    plan = parse_phase_plan(sys.argv[1])
    print(json.dumps(plan, indent=2))
EOF

chmod +x scripts/convert_phase_to_workstream.py

# Generate bundle
python scripts/convert_phase_to_workstream.py \
  meta/plans/phase-K-plus-decision-context.md \
  > workstreams/phase-k-plus-bundle.json
```

---

## Advanced: Custom Adapters

Create custom tool adapters for specialized tasks:

```python
# scripts/uet_custom_adapter.py
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.adapters.base import ToolAdapter

class DocumentationGeneratorAdapter(ToolAdapter):
    """Custom adapter for ADR generation."""
    
    def execute(self, context):
        template = Path("docs/adr/template.md").read_text()
        # Custom logic to fill template
        return {"status": "success", "files_created": [...]}
```

Register in `router_config.json`:

```json
{
  "custom_adapters": {
    "adr_generator": {
      "module": "scripts.uet_custom_adapter",
      "class": "DocumentationGeneratorAdapter"
    }
  }
}
```

---

## Troubleshooting

### UET Not Found

```bash
# Ensure PYTHONPATH includes UET framework
export PYTHONPATH="C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK:$PYTHONPATH"

# Or run from UET directory
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
python core/engine/orchestrator.py ../workstreams/phase-k-plus-bundle.json
```

### Resume Failed Run

```bash
# List recent runs
ls .uet/runs/

# Resume specific run
python core/engine/orchestrator.py workstreams/phase-k-plus-bundle.json \
  --resume phase-k-plus-20251122-143022
```

### Debug Mode

```bash
# Enable verbose logging
export UET_LOG_LEVEL=DEBUG
python core/engine/orchestrator.py workstreams/phase-k-plus-bundle.json
```

---

## Next Steps

1. **Create the workstream bundle:** Use conversion script or manual JSON
2. **Bootstrap the project:** Run UET bootstrap to generate config
3. **Execute Week 0 (Optional):** Test UET with optional cleanup tasks
4. **Execute Week 1:** Run critical ADR/impact matrix work
5. **Monitor progress:** Use `RunMonitor` for real-time tracking
6. **Iterate weeks 2-4:** Sequential execution with parallel steps

---

## References

- **UET Framework:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/README.md`
- **UET Status:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/STATUS.md` (78% complete, 196 tests passing)
- **UET Integration Plan:** `docs/UET_INTEGRATION_PLAN.md`
- **UET Quick Reference:** `docs/UET_QUICK_REFERENCE.md`
- **Phase K+ Plan:** `meta/plans/phase-K-plus-decision-context.md`
- **Bootstrap Spec:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/UET_BOOTSTRAP_SPEC.md`
- **Task Routing Spec:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/UET_TASK_ROUTING_SPEC.md`

---

## Summary

UET transforms Phase K+ from a manual checklist into an orchestrated, resilient, monitored workflow:

| Feature | Without UET | With UET |
|---------|-------------|----------|
| **Execution** | Manual, sequential | Automated, parallel |
| **Progress** | Manual tracking | Real-time monitoring |
| **Errors** | Manual retry | Auto-retry, circuit breakers |
| **Cost** | Unknown until done | Tracked, budget-enforced |
| **Resume** | Start from scratch | Resume from checkpoint |
| **Validation** | Manual checks | Automated test gates |

**Estimated Time Savings:** 30-40% through parallelism and automation  
**Error Reduction:** 50%+ through validation gates and resilience patterns
