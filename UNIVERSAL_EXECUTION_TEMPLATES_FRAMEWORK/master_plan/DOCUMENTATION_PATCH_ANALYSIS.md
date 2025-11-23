# Documentation Patch Analysis

**Generated**: 2025-11-23T11:07:25Z  
**Purpose**: Analyze documentation files for master plan patches  
**Status**: HIGH PRIORITY - Critical AI tooling and execution patterns identified

---

## Executive Summary

**6 documentation files analyzed** - **4 contain CRITICAL information** for master plan:

| File | Priority | Impact | Patches |
|------|----------|--------|---------|
| **tools-instructions-config.md** | CRITICAL | Multi-tool instruction patterns | 8 patches |
| **soft-sandbox-pattern.md** | HIGH | Sandbox isolation strategy | 6 patches |
| **ai-development-techniques.md** | MEDIUM | Advanced AI patterns | 3 patches |
| **DOCUMENTATION_INDEX.md** | HIGH | Documentation structure | 5 patches |
| **ACS_USAGE_GUIDE.md** | MEDIUM | ACS implementation details | 4 patches |
| **EXECUTION_TRACES_SUMMARY.md** | LOW | Performance metrics | 2 patches |

**Total New Patches**: 28 operations

---

## Critical Findings

### 1. tools-instructions-config.md - CRITICAL

**Reveals**: **Three-layer instruction pattern** for AI tools:

```
Layer 1: Global persona (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)
Layer 2: Repo-level (./CLAUDE.md, ./AGENTS.md, .github/copilot-instructions.md)
Layer 3: Per-invocation (--system-prompt flags)
```

**Tool Configuration Files**:
- **Claude Code**: `~/.claude/settings.json`, `CLAUDE.md`, `.claude/settings.json`
- **Codex**: `~/.codex/AGENTS.md`, `~/.codex/config.toml`
- **GitHub Copilot**: `.github/copilot-instructions.md` + personal settings

**Impact**: Every phase needs instruction files for each tool!

---

### 2. soft-sandbox-pattern.md - HIGH

**Reveals**: **Soft sandbox pattern** for AI safety:

```
Windows: C:\Users\richg\AI_SANDBOX\{repo}_sandbox
WSL: ~/ai-sandbox/{repo}_sandbox

Strategy: Run AI tools ONLY in sandbox clones
```

**Safety Pattern**:
```yaml
sandbox_root: 
  windows: "C:\\Users\\richg\\AI_SANDBOX"
  wsl: "~/ai-sandbox"

clone_pattern: "{repo}_sandbox"

rules:
  - "AI tools run only in sandbox clones"
  - "Experimental changes on ai-sandbox/* branches"
  - "Stable changes promoted to main repo"
```

**Impact**: Every task needs sandbox configuration!

---

### 3. DOCUMENTATION_INDEX.md - HIGH

**Reveals**: **Documentation hierarchy** and **ACS (AI Codebase Structure)**:

```
Quick Navigation:
  - Getting Started (README, QUICK_START, AGENTS)
  - Architecture Decisions (8 ADRs)
  - Reference Docs (5 deep technical)
  - Guidelines (best practices)
  - AI Agents Guide (.meta/AI_GUIDANCE.md)

ACS Artifacts:
  - CODEBASE_INDEX.yaml
  - QUALITY_GATE.yaml
  - ai_policies.yaml
  - .aiignore
  - .meta/ai_context/*.json
```

**Impact**: Plan needs documentation validation gates!

---

### 4. ai-development-techniques.md - MEDIUM

**Reveals**: **Advanced AI patterns** for code understanding:

1. **Repository Mapping** (AST + PageRank)
2. **GraphRAG** (Knowledge Graphs for dependencies)
3. **Reflexion Loops** (Runtime-aware self-correction)
4. **RAPTOR** (Hierarchical code indexing)
5. **Multimodal Terminal State** (PTY integration)
6. **Episodic Memory** (Learn project conventions)
7. **HyDE** (Hypothetical Document Embeddings)

**Impact**: Future phases should implement these patterns!

---

## Required Patches

### Patch 002: AI Tool Configuration

```json
[
  {
    "op": "add",
    "path": "/meta/ai_tool_configuration",
    "value": {
      "instruction_layers": {
        "global": {
          "claude": "~/.claude/CLAUDE.md",
          "codex": "~/.codex/AGENTS.md",
          "copilot": "GitHub account custom instructions"
        },
        "repo_level": {
          "claude": "./CLAUDE.md",
          "codex": "./AGENTS.md",
          "copilot": ".github/copilot-instructions.md"
        },
        "per_invocation": {
          "claude": "--system-prompt, --append-system-prompt",
          "codex": "prompt text",
          "copilot": "command prompt"
        }
      },
      "config_files": {
        "claude": ["~/.claude/settings.json", ".claude/settings.json"],
        "codex": ["~/.codex/config.toml"],
        "aider": [".aider.conf.yml"]
      }
    }
  },
  {
    "op": "add",
    "path": "/meta/tool_instruction_files_required",
    "value": ["CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"]
  },
  {
    "op": "add",
    "path": "/phases/PH-000/workstreams/WS-000-007",
    "value": {
      "workstream_id": "WS-000-007",
      "workstream_ulid": "01JDK8XWQP8WS000007AICONF1",
      "name": "AI Tool Instruction Files",
      "phase_id": "PH-000",
      "priority": "HIGH",
      "estimated_duration_hours": 1.5,
      "dependencies": [],
      "tasks": {
        "TSK-000-007-001": {
          "task_id": "TSK-000-007-001",
          "task_ulid": "01JDK8XWQP8TSK000007001CLA",
          "name": "Create CLAUDE.md",
          "workstream_id": "WS-000-007",
          "executor": "file_create",
          "inputs": {
            "file_path": {"type": "string", "default": "CLAUDE.md"}
          },
          "outputs": {
            "file_created": {"type": "boolean"}
          },
          "file_scope": {
            "create": ["CLAUDE.md"],
            "modify": [],
            "read_only": ["AGENTS.md", ".github/copilot-instructions.md"]
          }
        },
        "TSK-000-007-002": {
          "task_id": "TSK-000-007-002",
          "task_ulid": "01JDK8XWQP8TSK000007002AGT",
          "name": "Update AGENTS.md for Codex",
          "workstream_id": "WS-000-007",
          "executor": "file_edit",
          "inputs": {
            "file_path": {"type": "string", "default": "AGENTS.md"}
          },
          "file_scope": {
            "create": [],
            "modify": ["AGENTS.md"],
            "read_only": ["CLAUDE.md"]
          }
        },
        "TSK-000-007-003": {
          "task_id": "TSK-000-007-003",
          "task_ulid": "01JDK8XWQP8TSK000007003COP",
          "name": "Verify .github/copilot-instructions.md",
          "workstream_id": "WS-000-007",
          "executor": "validation",
          "command": "Test-Path .github/copilot-instructions.md",
          "file_scope": {
            "create": [],
            "modify": [],
            "read_only": [".github/copilot-instructions.md"]
          }
        }
      }
    }
  }
]
```

### Patch 003: Sandbox Configuration

```json
[
  {
    "op": "add",
    "path": "/meta/sandbox_strategy",
    "value": {
      "pattern": "soft_sandbox",
      "sandbox_roots": {
        "windows": "C:\\Users\\richg\\AI_SANDBOX",
        "wsl": "~/ai-sandbox"
      },
      "clone_pattern": "{repo}_sandbox",
      "branch_pattern": "ai-sandbox/*",
      "rules": [
        "AI tools run only in sandbox clones",
        "Experimental changes on ai-sandbox/* branches",
        "Stable changes promoted to main repo"
      ]
    }
  },
  {
    "op": "add",
    "path": "/phases/PH-000/pre_flight_checks",
    "value": {
      "sandbox_available": {
        "windows": "Test-Path C:\\Users\\richg\\AI_SANDBOX",
        "wsl": "test -d ~/ai-sandbox"
      },
      "git_config": {
        "user_name": "git config user.name",
        "user_email": "git config user.email"
      }
    }
  }
]
```

### Patch 004: Documentation Validation

```json
[
  {
    "op": "add",
    "path": "/meta/documentation_structure",
    "value": {
      "index": "docs/DOCUMENTATION_INDEX.md",
      "categories": [
        "getting_started",
        "architecture_decisions",
        "reference",
        "guidelines",
        "ai_agents"
      ],
      "acs_artifacts": [
        "CODEBASE_INDEX.yaml",
        "QUALITY_GATE.yaml",
        "ai_policies.yaml",
        ".aiignore",
        ".meta/AI_GUIDANCE.md"
      ],
      "generated_context": [
        ".meta/ai_context/repo_summary.json",
        ".meta/ai_context/code_graph.json"
      ]
    }
  },
  {
    "op": "add",
    "path": "/validation/documentation_gates",
    "value": {
      "acs_conformance": {
        "command": "python scripts/validate_acs_conformance.py",
        "required": true
      },
      "repo_summary_current": {
        "command": "python scripts/generate_repo_summary.py --validate",
        "required": false
      },
      "code_graph_acyclic": {
        "command": "python scripts/generate_code_graph.py --validate",
        "required": true
      }
    }
  }
]
```

### Patch 005: Advanced AI Techniques (Future)

```json
[
  {
    "op": "add",
    "path": "/meta/future_ai_techniques",
    "value": {
      "repository_mapping": {
        "technique": "AST + PageRank",
        "tool": "Tree-sitter",
        "priority": "HIGH",
        "estimated_effort_hours": 16
      },
      "graph_rag": {
        "technique": "Knowledge Graph for dependencies",
        "priority": "MEDIUM",
        "estimated_effort_hours": 24
      },
      "reflexion_loops": {
        "technique": "Runtime-aware self-correction",
        "priority": "HIGH",
        "estimated_effort_hours": 12
      },
      "raptor_indexing": {
        "technique": "Hierarchical code indexing",
        "priority": "MEDIUM",
        "estimated_effort_hours": 20
      }
    }
  }
]
```

---

## Summary

### Must Patch Immediately (Priority 1)

1. **AI Tool Configuration** (Patch 002)
   - Add instruction file requirements
   - Add WS-000-007 for creating instruction files
   - ~1.5 hours

2. **Sandbox Strategy** (Patch 003)
   - Add sandbox configuration
   - Add pre-flight checks
   - Critical for safety

3. **Documentation Validation** (Patch 004)
   - Add ACS conformance gates
   - Add code graph validation

### Should Patch Soon (Priority 2)

4. **Advanced AI Techniques** (Patch 005)
   - Document future enhancements
   - Reserve phase for implementation

### Performance Data (Reference Only)

From EXECUTION_TRACES_SUMMARY.md:
- Workstream execution: 1.4s (88% pytest)
- Error detection: 611ms (already cached 9.4×)
- Spec resolution: 87ms (already cached 29×)

**Not urgent** - Already optimized, reference for future phases

---

## Impact on Master Plan

### New Metadata Sections
- `ai_tool_configuration`
- `sandbox_strategy`
- `documentation_structure`
- `future_ai_techniques`

### New Workstream
- **WS-000-007**: AI Tool Instruction Files (1.5 hours)

### New Validation Gates
- `acs_conformance` (blocking)
- `code_graph_acyclic` (blocking)
- `repo_summary_current` (non-blocking)

### Updated Timeline
- Phase 0: 4.5 hours → **6.0 hours** (+1.5 hours for instruction files)

---

**Patches ready to apply?**
