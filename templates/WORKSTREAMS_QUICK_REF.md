---
doc_id: DOC-GUIDE-WORKSTREAMS-QUICK-REF-449
---

# Template Expansion Workstreams - Quick Reference

## 📋 Overview
- **Total Workstreams**: 16
- **Execution Tracks**: 3 (parallel in Week 1)
- **Total Time**: 36 hours (3 weeks)
- **Annual ROI**: 218.3h saved / 36h invested = 6:1

---

## 🚀 Week 1: Parallel Template Creation (18h → 6h wall time)

### Track 1: Infrastructure Templates (Agent 1)
| WS ID | Template | Time | Status |
|-------|----------|------|--------|
| WS-T01 | PowerShell Installer | 3h | ⬜ Not Started |
| WS-T02 | Git Workflow Script | 3h | ⬜ Not Started |
| WS-T03 | Validation Gate | 2h | ⬜ Not Started |
| WS-T04 | Registry Backfill Planner | 4h | ⬜ Not Started |

### Track 2: Process & Config Templates (Agent 2)
| WS ID | Template | Time | Status |
|-------|----------|------|--------|
| WS-T05 | Validation Report | 2h | ⬜ Not Started |
| WS-T06 | Multi-Agent Orchestration | 4h | ⬜ Not Started |
| WS-T07 | MCP Server Config | 3h | ⬜ Not Started |
| WS-T08 | Error Plugin Scaffold | 3h | ⬜ Not Started |

### Track 3: Documentation Templates (Agent 3)
| WS ID | Template | Time | Status |
|-------|----------|------|--------|
| WS-T09 | Versioned Document | 2h | ⬜ Not Started |
| WS-T10 | CLAUDE.md Generator | 4h | ⬜ Not Started |
| WS-T11 | Template Catalog | 3h | ⬜ Not Started |
| WS-T12 | Template Validator | 3h | ⬜ Not Started |

---

## 📦 Week 2: Integration (Sequential, 12h)

| WS ID | Task | Dependencies | Time | Status |
|-------|------|--------------|------|--------|
| WS-T13 | Core Template Renderer | WS-T01..T12 | 6h | ⬜ Not Started |
| WS-T14 | Integration Test Suite | WS-T13 | 6h | ⬜ Not Started |

---

## 📚 Week 3: Documentation & Deployment (Sequential, 12h)

| WS ID | Task | Dependencies | Time | Status |
|-------|------|--------------|------|--------|
| WS-T15 | Template System Documentation | WS-T14 | 6h | ⬜ Not Started |
| WS-T16 | Production Deployment | WS-T15 | 6h | ⬜ Not Started |

---

## 🎯 Execution Commands (Codex CLI)

### Launch Week 1 (All 3 Tracks in Parallel)
```bash
# Terminal 1: Track 1
codex execute --workstream WS-T01,WS-T02,WS-T03,WS-T04 --agent agent-1 --worktree .worktrees/track-1

# Terminal 2: Track 2
codex execute --workstream WS-T05,WS-T06,WS-T07,WS-T08 --agent agent-2 --worktree .worktrees/track-2

# Terminal 3: Track 3
codex execute --workstream WS-T09,WS-T10,WS-T11,WS-T12 --agent agent-3 --worktree .worktrees/track-3
```

### Launch Week 2 (Sequential)
```bash
codex execute --workstream WS-T13 --depends-on WS-T01,WS-T02,...,WS-T12
codex execute --workstream WS-T14 --depends-on WS-T13
```

### Launch Week 3 (Sequential)
```bash
codex execute --workstream WS-T15 --depends-on WS-T14
codex execute --workstream WS-T16 --depends-on WS-T15
```

### Monitor Progress
```bash
codex status --all
codex logs --workstream WS-T01 --tail 50
codex gates --workstream WS-T01 --show-failures
```

---

## ✅ Ground Truth Gates (All Workstreams)

### Gate 1: Schema Validation
```bash
python -c "import json, jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('schema.json')))"
# Exit code: 0
```

### Gate 2: Template Syntax
```bash
python -c "from jinja2 import Template; Template(open('template.jinja2').read())"
# Exit code: 0
```

### Gate 3: Render Test
```bash
python tools/render_template.py template.jinja2 vars.json --output test.out
# Exit code: 0
```

### Gate 4: Output Validation
```bash
# PowerShell: pwsh -NoProfile -File test.ps1 -Syntax
# Python: python -m compileall test.py -q
# YAML: python -c "import yaml; yaml.safe_load(open('test.yaml'))"
# Exit code: 0
```

---

## 📊 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Templates Created | 12 | File count in templates/ |
| Ground Truth Gates Pass | 100% | All gates exit 0 |
| Integration Tests Pass | 100% | pytest exit 0 |
| Test Coverage | ≥ 80% | pytest-cov report |
| Zero Manual Edits | Yes | Tests run generated output directly |

---

## 🔄 Rollback Plan

| Failure Point | Rollback Action | Impact |
|---------------|-----------------|--------|
| Track 1 fails | Ship Track 2+3 only | 60% of savings |
| Track 2 fails | Ship Track 1+3 only | 60% of savings |
| Track 3 fails | Ship Track 1+2 only | 70% of savings |
| Renderer fails | Manual Jinja2 rendering | 80% of savings |
| Tests fail | Ship without test suite | 100% of savings (add tests later) |

**Minimum Viable Product**: 6 templates (2 per track) = 100h/year savings

---

## 📈 Expected Outcomes

### Week 1 Complete
- ✅ 12 templates created
- ✅ 12 schemas defined
- ✅ All ground truth gates pass
- ✅ 18h work done in 6h wall time (3x speedup)

### Week 2 Complete
- ✅ Template renderer operational
- ✅ Integration tests green
- ✅ All templates generate working output

### Week 3 Complete
- ✅ Documentation complete
- ✅ Templates deployed to main
- ✅ **Annual savings: 218.3 hours unlocked**

---

## 📁 File Structure After Completion

```
templates/
├── README.md                          # Auto-generated catalog (WS-T11)
├── TEMPLATE_EXPANSION_PHASE_PLAN.md   # This plan
├── workstreams/                       # Workstream definitions
│   ├── WS-T01-powershell-installer-template.yaml
│   ├── WS-T05-validation-report-template.yaml
│   ├── WS-T09-versioned-doc-template.yaml
│   └── ... (13 more)
├── _schema/                           # JSON Schema definitions
│   ├── powershell_installer.schema.json
│   ├── validation_report.schema.json
│   └── ... (10 more)
├── _examples/                         # Example variable files
│   ├── install_tool.example.json
│   └── ... (12 more)
├── install_tool.template.ps1          # WS-T01
├── git_atomic_commit.template.ps1     # WS-T02
├── validation_gate.template.yaml      # WS-T03
├── scan_and_classify.template.py      # WS-T04
├── validation_report.template.md      # WS-T05
├── agent_workflow.template.yaml       # WS-T06
├── claude_desktop_config.template.json # WS-T07
├── error_plugin.template.py           # WS-T08
├── versioned_doc.template.md          # WS-T09
└── ... (3 more)

tools/
├── render_template.py                 # WS-T13
├── validate_template.py               # WS-T12
├── generate_template_catalog.py       # WS-T11
├── generate_claude_md.py              # WS-T10
└── validate_doc_frontmatter.py        # WS-T09

tests/
└── test_templates_integration.py      # WS-T14

docs/
├── TEMPLATE_SYSTEM_GUIDE.md           # WS-T15
└── TEMPLATE_QUICK_START.md            # WS-T15
```

---

**Ready to Execute**: All workstream definitions created  
**Next Step**: Launch Week 1 parallel execution with Codex CLI
