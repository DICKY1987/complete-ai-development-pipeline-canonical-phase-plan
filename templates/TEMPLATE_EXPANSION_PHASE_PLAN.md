---
doc_id: DOC-GUIDE-TEMPLATE-EXPANSION-PHASE-PLAN-448
---

# Template Expansion Phase Plan
**Pattern**: EXEC-001 (Batch File Creator) + EXEC-002 (Code Module Generator)  
**Goal**: Build 15-template system saving 218h/year  
**Time Estimate**: 3 weeks (36 hours) vs 12 weeks manual (480 hours)  
**ROI**: 13.3:1 (480h saved / 36h invested)  
**Date**: 2025-11-29

---

## Pre-Decisions (Made Once, Applied to All Templates)

### Structural Decisions ✅
- **Template format**: Jinja2 with YAML variable schemas
- **Storage location**: `templates/` with subdirs by category
- **Naming convention**: `{purpose}.template.{ext}`
- **Validation**: Ground truth gates for every template
- **Success metric**: All 10 new templates generate working outputs, zero manual edits needed

### Format Decisions ✅
- **Variable schema**: JSON Schema for validation
- **Generator scripts**: Python 3.12+ with `jinja2`, `pyyaml`, `jsonschema`
- **Documentation**: Each template has companion `{name}.README.md`
- **Ground truth**: Generated output passes existing quality gates

### NOT Decisions (Don't Waste Time) ❌
- Perfect variable naming (use clear, good-enough names)
- Comprehensive edge cases (handle 80% use cases)
- Backward compatibility with old scripts (new templates are greenfield)
- Universal cross-platform support (Windows/PowerShell first)

---

## Independent Workstreams (3 Parallel Tracks)

### **Track 1: Infrastructure Templates** (Agent 1)
*Foundation templates for automation scripts*

**Workstreams:**
- WS-T01: PowerShell Installer Template
- WS-T02: Git Workflow Script Template
- WS-T03: Validation Gate Template
- WS-T04: Registry Backfill Planner Template

**Dependencies:** None (independent)  
**Estimated Time:** 12 hours (3h per template)  
**Agent Assignment:** Codex CLI Agent 1

---

### **Track 2: Process & Configuration Templates** (Agent 2)
*Templates for orchestration and configuration*

**Workstreams:**
- WS-T05: Validation Report Template
- WS-T06: Multi-Agent Orchestration Config Template
- WS-T07: MCP Server Configuration Template
- WS-T08: Error Plugin Scaffold Template

**Dependencies:** None (independent)  
**Estimated Time:** 12 hours (3h per template)  
**Agent Assignment:** Codex CLI Agent 2

---

### **Track 3: Documentation & Quality Templates** (Agent 3)
*Templates for docs and governance*

**Workstreams:**
- WS-T09: Versioned Document Template
- WS-T10: CLAUDE.md Generation Template
- WS-T11: Template Catalog Generator
- WS-T12: Template Validator Tool

**Dependencies:** None (independent)  
**Estimated Time:** 12 hours (3h per template)  
**Agent Assignment:** Codex CLI Agent 3

---

## Phase Breakdown (3 Weeks)

### **Week 1: Template Creation** (Track 1 + 2 + 3 in parallel)

#### **Phase 1A: Discovery & Schema Definition** (Days 1-2, 6 hours)
*All 3 agents work in parallel*

**Track 1 (Agent 1)**:
- WS-T01-SCHEMA: Define PowerShell installer variable schema
- WS-T02-SCHEMA: Define git workflow variable schema
- WS-T03-SCHEMA: Define validation gate variable schema
- WS-T04-SCHEMA: Define registry planner variable schema

**Track 2 (Agent 2)**:
- WS-T05-SCHEMA: Define validation report variable schema
- WS-T06-SCHEMA: Define agent orchestration variable schema
- WS-T07-SCHEMA: Define MCP config variable schema
- WS-T08-SCHEMA: Define error plugin variable schema

**Track 3 (Agent 3)**:
- WS-T09-SCHEMA: Define versioned doc variable schema
- WS-T10-SCHEMA: Define CLAUDE.md variable schema
- WS-T11-SCHEMA: Define catalog generator schema
- WS-T12-SCHEMA: Define validator tool schema

**Ground Truth Gate:**
```powershell
# All schemas validate against JSON Schema meta-schema
Get-ChildItem templates\_schema -Filter *.json | ForEach-Object {
    python -c "import json, jsonschema; schema=json.load(open('$_')); jsonschema.Draft7Validator.check_schema(schema)"
}
# Exit code: 0 (all valid)
```

---

#### **Phase 1B: Template Implementation** (Days 3-5, 18 hours)

**Track 1 (Agent 1)** - Infrastructure Templates:

**WS-T01: PowerShell Installer Template**
```yaml
pattern: EXEC-001
input: templates/_schema/powershell_installer.schema.json
output: templates/install_tool.template.ps1
ground_truth:
  - Renders without errors
  - Generates valid PowerShell syntax
  - Includes ULID generation
  - Includes validation gates
  - Includes audit logging
validation_command: |
  $rendered = Invoke-TemplateRender -Template templates/install_tool.template.ps1 -Vars test_vars.json
  pwsh -NoProfile -Command $rendered -DryRun
expect_exit_code: 0
time_estimate: 3h
```

**WS-T02: Git Workflow Script Template**
```yaml
pattern: EXEC-001
input: templates/_schema/git_workflow.schema.json
output: templates/git_atomic_commit.template.ps1
ground_truth:
  - Conventional commit format validation
  - File staging verification
  - No uncommitted changes check
validation_command: |
  $rendered = Invoke-TemplateRender -Template templates/git_atomic_commit.template.ps1 -Vars test_vars.json
  pwsh -NoProfile -Command $rendered -DryRun
expect_exit_code: 0
time_estimate: 3h
```

**WS-T03: Validation Gate Template**
```yaml
pattern: EXEC-001
input: templates/_schema/validation_gate.schema.json
output: templates/validation_gate.template.yaml
ground_truth:
  - Valid YAML structure
  - All required fields present
  - Commands are executable
validation_command: |
  python -c "import yaml; yaml.safe_load(open('templates/validation_gate.template.yaml'))"
expect_exit_code: 0
time_estimate: 2h
```

**WS-T04: Registry Backfill Planner Template**
```yaml
pattern: EXEC-002
input: templates/_schema/scan_classify.schema.json
output: templates/scan_and_classify.template.py
ground_truth:
  - Python syntax valid
  - Imports resolve
  - Generates JSON output
validation_command: |
  python -m compileall templates/scan_and_classify.template.py -q
  python templates/scan_and_classify.template.py --help
expect_exit_code: 0
time_estimate: 4h
```

---

**Track 2 (Agent 2)** - Process Templates:

**WS-T05: Validation Report Template**
```yaml
pattern: EXEC-001
input: templates/_schema/validation_report.schema.json
output: templates/validation_report.template.md
ground_truth:
  - Valid Markdown syntax
  - All placeholders replaced
  - Tables render correctly
validation_command: |
  python tools/render_template.py templates/validation_report.template.md test_vars.json | 
    mdl --style markdown_style.rb -
expect_exit_code: 0
time_estimate: 2h
```

**WS-T06: Multi-Agent Orchestration Config Template**
```yaml
pattern: EXEC-001
input: templates/_schema/agent_workflow.schema.json
output: templates/agent_workflow.template.yaml
ground_truth:
  - Valid YAML
  - Dependency graph is acyclic
  - All agent_ids referenced exist
validation_command: |
  python tools/validate_workflow.py templates/agent_workflow.template.yaml
expect_exit_code: 0
time_estimate: 4h
```

**WS-T07: MCP Server Configuration Template**
```yaml
pattern: EXEC-001
input: templates/_schema/mcp_config.schema.json
output: templates/claude_desktop_config.template.json
ground_truth:
  - Valid JSON
  - All command binaries exist
  - Env vars are defined
validation_command: |
  python -c "import json; json.load(open('templates/claude_desktop_config.template.json'))"
expect_exit_code: 0
time_estimate: 3h
```

**WS-T08: Error Plugin Scaffold Template**
```yaml
pattern: EXEC-002
input: templates/_schema/error_plugin.schema.json
output: 
  - templates/error_plugin.template.py
  - templates/test_error_plugin.template.py
ground_truth:
  - Python syntax valid
  - Plugin class inherits ErrorPlugin
  - Test file imports plugin
validation_command: |
  python -m compileall templates/error_plugin.template.py -q
  python -m pytest --collect-only templates/test_error_plugin.template.py
expect_exit_code: 0
time_estimate: 3h
```

---

**Track 3 (Agent 3)** - Documentation Templates:

**WS-T09: Versioned Document Template**
```yaml
pattern: EXEC-001
input: templates/_schema/versioned_doc.schema.json
output: templates/versioned_doc.template.md
ground_truth:
  - Valid YAML frontmatter
  - semver format correct
  - All required fields present
validation_command: |
  python tools/validate_doc_frontmatter.py templates/versioned_doc.template.md
expect_exit_code: 0
time_estimate: 2h
```

**WS-T10: CLAUDE.md Generation Template**
```yaml
pattern: EXEC-002
input: templates/_schema/claude_md.schema.json
output: templates/generate_claude_md.template.py
ground_truth:
  - Extracts commands from Makefile
  - Generates valid Markdown
  - All commands are executable
validation_command: |
  python templates/generate_claude_md.template.py --repo . --output test_CLAUDE.md
  test -f test_CLAUDE.md
expect_exit_code: 0
time_estimate: 4h
```

**WS-T11: Template Catalog Generator**
```yaml
pattern: EXEC-002
input: templates/_schema/template_catalog.schema.json
output: tools/generate_template_catalog.py
ground_truth:
  - Scans templates/ directory
  - Generates templates/README.md
  - Lists all variables per template
validation_command: |
  python tools/generate_template_catalog.py
  test -f templates/README.md
  grep -q "## Available Templates" templates/README.md
expect_exit_code: 0
time_estimate: 3h
```

**WS-T12: Template Validator Tool**
```yaml
pattern: EXEC-002
input: templates/_schema/template_validator.schema.json
output: tools/validate_template.py
ground_truth:
  - Validates variable schema
  - Validates Jinja2 syntax
  - Test renders with sample data
validation_command: |
  python tools/validate_template.py templates/install_tool.template.ps1
expect_exit_code: 0
time_estimate: 3h
```

---

### **Week 2: Integration & Testing** (Sequential)

#### **Phase 2A: Template Renderer Infrastructure** (Days 6-7, 6 hours)

**WS-T13: Core Template Renderer**
```yaml
pattern: EXEC-002
dependencies: [WS-T01 through WS-T12]
input: None
output: tools/render_template.py
features:
  - Jinja2 rendering engine
  - Variable schema validation
  - Multiple output formats (file, stdout)
  - Dry-run mode
ground_truth:
  - All 12 templates render without errors
  - Schema validation catches invalid vars
validation_command: |
  for template in templates/*.template.*; do
    python tools/render_template.py $template test_vars/$template.vars.json --dry-run
  done
expect_exit_code: 0
time_estimate: 6h
```

---

#### **Phase 2B: End-to-End Testing** (Days 8-9, 6 hours)

**WS-T14: Integration Test Suite**
```yaml
pattern: EXEC-002
dependencies: [WS-T13]
output: tests/test_templates_integration.py
test_cases:
  - test_render_all_templates_with_valid_vars
  - test_invalid_vars_caught_by_schema
  - test_generated_output_passes_quality_gates
  - test_template_catalog_includes_all_templates
  - test_validator_catches_syntax_errors
ground_truth:
  - All tests pass
  - Coverage >= 80%
validation_command: |
  pytest tests/test_templates_integration.py -v --cov=tools --cov=templates --cov-report=term
expect_exit_code: 0
time_estimate: 6h
```

---

### **Week 3: Documentation & Deployment** (Sequential)

#### **Phase 3A: Documentation** (Days 10-11, 6 hours)

**WS-T15: Template System Documentation**
```yaml
pattern: EXEC-001
dependencies: [WS-T14]
output:
  - templates/README.md (auto-generated by WS-T11)
  - docs/TEMPLATE_SYSTEM_GUIDE.md
  - docs/TEMPLATE_QUICK_START.md
content:
  - Overview of template system
  - Variable schema documentation
  - Usage examples for each template
  - Contribution guidelines
ground_truth:
  - All templates documented
  - All examples work
validation_command: |
  # Extract and run all example commands from docs
  grep -oP '(?<=```bash\n).*?(?=\n```)' docs/TEMPLATE_SYSTEM_GUIDE.md | bash
expect_exit_code: 0
time_estimate: 6h
```

---

#### **Phase 3B: Deployment & Verification** (Days 12-13, 6 hours)

**WS-T16: Production Deployment**
```yaml
pattern: EXEC-001
dependencies: [WS-T15]
tasks:
  - Commit all templates to main branch
  - Tag release: templates-v1.0.0
  - Generate final validation report
  - Update REFACTOR_2 documentation index
ground_truth:
  - All 12 templates committed
  - Git tag created
  - Validation report shows 100% success
validation_command: |
  git log --oneline --grep="feat: add template system" | grep -q "feat:"
  git tag | grep -q "templates-v1.0.0"
  test -f reports/template_system_validation_report.md
expect_exit_code: 0
time_estimate: 6h
```

---

## Execution Pattern Summary

### Pattern EXEC-001: Batch File Creator
**Used by**: WS-T01, WS-T02, WS-T03, WS-T05, WS-T06, WS-T07, WS-T09, WS-T15, WS-T16

**Steps**:
1. Define variable schema (JSON Schema)
2. Create template file with Jinja2 placeholders
3. Create test variables file
4. Render template with test vars
5. Validate output passes ground truth gates
6. Document template variables

---

### Pattern EXEC-002: Code Module Generator
**Used by**: WS-T04, WS-T08, WS-T10, WS-T11, WS-T12, WS-T13, WS-T14

**Steps**:
1. Define module structure
2. Create generator script
3. Implement core logic
4. Add validation gates
5. Create unit tests
6. Verify ground truth (imports resolve, syntax valid)

---

## Dependency Graph

```
Week 1 (Parallel):
  Track 1: WS-T01 ─┐
           WS-T02  │
           WS-T03  ├─→ Week 2: WS-T13 ─→ WS-T14 ─→ Week 3: WS-T15 ─→ WS-T16
           WS-T04 ─┘
  
  Track 2: WS-T05 ─┐
           WS-T06  │
           WS-T07  ├─→ (Same as above)
           WS-T08 ─┘
  
  Track 3: WS-T09 ─┐
           WS-T10  │
           WS-T11  ├─→ (Same as above)
           WS-T12 ─┘
```

**Critical Path**: Any template → WS-T13 → WS-T14 → WS-T15 → WS-T16 (24 hours)  
**Total Parallelizable Work**: Week 1 (18 hours across 3 agents = 6 hours wall time)  
**Total Sequential Work**: Week 2-3 (24 hours wall time)  
**Total Wall Time**: 30 hours (vs 480 hours manual = 94% savings)

---

## Ground Truth Gates (Applied to All Workstreams)

### Gate 1: Schema Validation
```bash
python -c "import json, jsonschema; jsonschema.validate(instance=json.load(open('vars.json')), schema=json.load(open('schema.json')))"
# Exit code: 0
```

### Gate 2: Template Syntax Valid
```bash
python -c "from jinja2 import Template; Template(open('template.jinja2').read())"
# Exit code: 0
```

### Gate 3: Rendered Output Valid
```bash
# For PowerShell templates:
pwsh -NoProfile -Command (Invoke-TemplateRender template.ps1 vars.json) -Syntax
# For Python templates:
python -m compileall rendered_output.py -q
# For YAML templates:
python -c "import yaml; yaml.safe_load(open('rendered.yaml'))"
# Exit code: 0
```

### Gate 4: Ground Truth Test Passes
```bash
# Template-specific validation (defined in each workstream)
pytest tests/test_{template_name}.py -v
# Exit code: 0
```

---

## Anti-Pattern Guards

### Hallucination of Success
**Rule**: Never mark template complete without all 4 ground truth gates passing  
**Enforcement**: CI checks for `.ok` stamp files + gate passage logs

### Partial Success Amnesia
**Rule**: Checkpoint after each gate passes; record in `.execution/template_progress.jsonl`  
**Enforcement**: Resume script checks progress log before re-running

### Template Scope Creep
**Rule**: Each template handles 80% use case, not 100%  
**Enforcement**: Template README defines explicit scope boundaries

### Manual Editing After Generation
**Rule**: Generated output should work without manual edits  
**Enforcement**: Test suite runs generated output directly, no human touch

---

## Success Metrics

### Quantitative
- **12 new templates created**: ✅ Binary (exist or not)
- **All templates pass 4 ground truth gates**: ✅ 100% pass rate
- **Integration tests pass**: ✅ All tests green
- **Test coverage >= 80%**: ✅ Measured by pytest-cov
- **Zero manual edits to generated output**: ✅ Checked in tests

### Qualitative
- **Templates are discoverable**: ✅ README.md catalog
- **Variables are documented**: ✅ Schema + docs
- **Examples work**: ✅ Docs tested in CI
- **Contributors can add templates**: ✅ Contribution guide exists

---

## Rollback Plan

If any track fails to deliver:

### Week 1 Rollback (Per Track)
- **If Track 1 fails**: Deprioritize infrastructure templates, proceed with Track 2+3
- **If Track 2 fails**: Deprioritize process templates, proceed with Track 1+3
- **If Track 3 fails**: Deprioritize docs templates, proceed with Track 1+2

### Week 2 Rollback
- **If renderer fails**: Fall back to manual Jinja2 rendering per template
- **If tests fail**: Ship templates without test suite (add tests later)

### Week 3 Rollback
- **If docs fail**: Ship templates with inline comments only
- **If deployment fails**: Manual git commit per template

**Minimum Viable Product**: 6 templates (2 per track) + manual rendering = Still 100h/year savings

---

## Telemetry

Track in `.execution/template_expansion_telemetry.jsonl`:

```json
{
  "ulid": "{ULID}",
  "timestamp": "2025-11-29T16:00:00Z",
  "event_type": "template_created",
  "data": {
    "template_name": "install_tool.template.ps1",
    "workstream_id": "WS-T01",
    "agent": "codex-agent-1",
    "duration_seconds": 10800,
    "gates_passed": ["schema_valid", "syntax_valid", "render_valid", "ground_truth_passed"],
    "decisions_eliminated": 45
  }
}
```

---

## Codex CLI Execution Commands

### Launch All Tracks in Parallel (Week 1)
```bash
# Track 1 (Agent 1)
codex execute --workstream WS-T01,WS-T02,WS-T03,WS-T04 --agent agent-1 --worktree .worktrees/track-1

# Track 2 (Agent 2)
codex execute --workstream WS-T05,WS-T06,WS-T07,WS-T08 --agent agent-2 --worktree .worktrees/track-2

# Track 3 (Agent 3)
codex execute --workstream WS-T09,WS-T10,WS-T11,WS-T12 --agent agent-3 --worktree .worktrees/track-3
```

### Sequential Execution (Week 2-3)
```bash
# Wait for all tracks to complete, then:
codex execute --workstream WS-T13 --depends-on WS-T01,WS-T02,...,WS-T12
codex execute --workstream WS-T14 --depends-on WS-T13
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

## Expected Outcomes

### Week 1 Completion
- ✅ 12 templates created and validated
- ✅ 12 variable schemas defined
- ✅ All templates pass ground truth gates
- ✅ 36 hours of work completed in 18 hours wall time (2x speedup via parallelism)

### Week 2 Completion
- ✅ Template renderer tool operational
- ✅ Integration tests pass
- ✅ All 12 templates generate working output

### Week 3 Completion
- ✅ Complete template system documentation
- ✅ Templates deployed to main branch
- ✅ Validation report confirms 100% success
- ✅ **Annual time savings: 218.3 hours unlocked**

---

## Next Steps After Completion

1. **Use templates immediately** for next refactor phase
2. **Measure actual time savings** vs manual approach
3. **Iterate on templates** based on real usage
4. **Add more templates** as patterns emerge (target: 25 templates by Q2)
5. **Contribute learnings** back to UET framework

---

**Total Implementation Time**: 36 hours (3 weeks)  
**Manual Equivalent**: 480 hours (12 weeks)  
**Time Savings**: 444 hours (92.5%)  
**Annual ROI After Deployment**: 218.3h saved / 36h invested = **6:1 first year, 17.5:1 ongoing**

### ROI by template (initial)

| Template | Setup Time | Manual Time | Template Time | Savings | Uses/Year | Annual Savings |
|----------|------------|-------------|---------------|---------|-----------|----------------|
| PowerShell Installer | 2h | 4h | 0.5h | 87% | 10 | 35h |
| Validation Report | 1h | 2h | 0.2h | 90% | 20 | 36h |
| Versioned Doc | 0.5h | 1.5h | 0.45h | 70% | 30 | 31.5h |
| Registry Backfill | 1h | 3h | 0.9h | 70% | 5 | 10.5h |
| Git Workflow | 0.5h | 1h | 0.5h | 50% | 50 | 25h |
| Agent Orchestration | 2h | 4h | 1h | 75% | 8 | 24h |
| MCP Config | 1h | 2h | 0.4h | 80% | 6 | 9.6h |
| CLAUDE.md | 2h | 3h | 1.2h | 60% | 4 | 7.2h |
| Validation Gate | 0.5h | 1h | 0.5h | 50% | 40 | 20h |
| Error Plugin | 2h | 5h | 1.75h | 65% | 6 | 19.5h |
| ALL (10 templates) | 12.5h | - | - | - | 179 | 218.3h/year |
