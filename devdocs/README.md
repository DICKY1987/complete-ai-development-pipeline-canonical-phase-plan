# Developer Documentation (`devdocs/`)

**Purpose**: Ephemeral, session-based, and process-tracking documentation for active development work.

**Last Updated**: 2025-11-22

---

## What Goes in `devdocs/`

This folder contains **developer-facing, process-oriented documentation** that tracks the evolution of the project through phases, sessions, and execution cycles. It is distinct from permanent, user-facing documentation.

### ✅ BELONGS in `devdocs/`

1. **Session Reports & Summaries**
   - AI-assisted development session logs
   - Session checkpoints and final reports
   - Metrics summaries from specific sessions
   - Example: `sessions/uet/SESSION_SUMMARY_2025-11-20_MEGA_SESSION.md`

2. **Phase Planning & Execution**
   - Phase-specific plans (Phase G, Phase H, etc.)
   - Phase completion reports
   - Phase checklists and progress tracking
   - Example: `phases/phase-h/COMPLETE.md`

3. **Execution Reports**
   - Workstream completion reports
   - Implementation summaries for specific features
   - Integration progress tracking
   - Example: `execution/WS-03-02A_COMPLETION_REPORT.md`

4. **Handoff Documentation**
   - Context for handing off work between sessions
   - Transition notes between phases
   - Example: `handoffs/HANDOFF_PROMPT.md`

5. **Process Analysis**
   - User workflow assessments
   - Metrics and performance analysis
   - Process improvement findings
   - Example: `analysis/USER_PROCESS_ASSESSMENT.md`

6. **Planning & Strategy**
   - Roadmaps for upcoming phases
   - Deprecation plans
   - File organization strategies
   - Example: `planning/PHASE_ROADMAP.md`

7. **Archived Development Artifacts**
   - Historical cleanup reports
   - Legacy phase documentation
   - Superseded implementation plans
   - Example: `archive/2025-11/cleanup-reports/`

### ❌ DOES NOT BELONG in `devdocs/`

1. **Permanent Documentation** → Use `docs/`
   - Architecture guides (unless phase-specific)
   - API references
   - User guides
   - Contribution guidelines

2. **Specifications** → Use `specifications/content/`
   - Formal specifications
   - Governance documents
   - Schema definitions

3. **Reference Materials** → Use `docs/`
   - AI development techniques
   - Design patterns
   - Best practices guides

4. **Source Code** → Use appropriate section (`core/`, `error/`, etc.)
   - Implementation files
   - Test files
   - Configuration files

5. **Generated Artifacts** → Use `logs/` or `.worktrees/`
   - Runtime logs
   - Build outputs
   - Database files

---

## Folder Structure

```
devdocs/
├── sessions/           # AI session logs and summaries
│   ├── uet/           # UET framework development sessions
│   ├── agentic-proto/ # Agentic prototype sessions
│   ├── process-deep-dive/ # Process analysis sessions
│   └── phase-*/       # Phase-specific sessions
│
├── phases/            # Phase-by-phase development tracking
│   ├── phase-*/       # Individual phase folders (2a, 2b, 3, 4, etc.)
│   ├── aim/           # AIM+ development phases
│   └── phase-k/       # Documentation enhancement phases
│
├── execution/         # Workstream and feature implementation reports
│   ├── WS-*_COMPLETION_REPORT.md
│   ├── AIM_PLUS_*.md
│   └── UET_*.md
│
├── planning/          # Strategic planning documents
│   ├── PHASE_ROADMAP.md
│   ├── PHASE_PLAN.md
│   └── DEPRECATION_PLAN.md
│
├── analysis/          # Process and codebase analysis
│   ├── agentic-proto/
│   ├── process-deep-dive/
│   └── *_ANALYSIS.md
│
├── handoffs/          # Session transition documentation
│   └── HANDOFF_PROMPT.md
│
├── meta/              # Meta-documentation about devdocs itself
│
└── archive/           # Historical development artifacts
    └── 2025-11/       # Date-organized archives
```

---

## Naming Conventions

### Session Reports
- Format: `SESSION_SUMMARY_YYYY-MM-DD_DESCRIPTOR.md`
- Example: `SESSION_SUMMARY_2025-11-20_MEGA_SESSION.md`

### Phase Documentation
- Format: `{PLAN|COMPLETE|CHECKLIST|PROGRESS}.md`
- Example: `phase-h/COMPLETE.md`

### Execution Reports
- Format: `WS-XX-XXX_COMPLETION_REPORT.md` or `FEATURE_NAME_STATUS.md`
- Example: `WS-03-02A_COMPLETION_REPORT.md`

### Analysis Documents
- Format: `TOPIC_ANALYSIS.md` or `METRICS_SUMMARY_YYYYMMDD.md`
- Example: `CORE_DUPLICATE_ANALYSIS.md`

---

## AI Tool Instructions

### For AI Assistants (Aider, Copilot, etc.)

When creating development documentation:

1. **Check the document type first**:
   - Session report? → `devdocs/sessions/{project}/`
   - Phase tracking? → `devdocs/phases/{phase-name}/`
   - Execution summary? → `devdocs/execution/`
   - Strategic planning? → `devdocs/planning/`
   - Analysis findings? → `devdocs/analysis/`

2. **If it's a permanent reference**:
   - Architecture, patterns, guides → `docs/`
   - Specifications, schemas → `specifications/content/`
   - Prompt templates → `Prompt/`

3. **Use descriptive ALL_CAPS names** for clarity in file listings

4. **Include metadata** in each document:
   ```markdown
   # Document Title
   **Date**: YYYY-MM-DD
   **Phase**: Phase X
   **Status**: [Active|Complete|Archived]
   ```

5. **Archive old reports** to `devdocs/archive/YYYY-MM/` when superseded

### Configuration

Include `devdocs/` in context for:
- ✅ Session planning and handoffs
- ✅ Phase execution tracking
- ✅ Understanding project evolution

Exclude `devdocs/` when:
- ❌ Looking for permanent architecture docs (use `docs/`)
- ❌ Looking for specifications (use `specifications/`)
- ❌ Focusing on current codebase only

---

## Examples

### ✅ Good: Belongs in `devdocs/`
```
devdocs/sessions/phase-4/SESSION_01_FINAL_REPORT.md
devdocs/phases/phase-h/UET_INTEGRATION_PLAN.md
devdocs/execution/AIM_PLUS_FINAL_REPORT.md
devdocs/analysis/CORE_DUPLICATE_ANALYSIS.md
```

### ❌ Bad: Should be elsewhere
```
devdocs/error-engine-architecture.md          → docs/architecture/
devdocs/workstream-schema-v1.md               → specifications/content/
devdocs/ai-development-techniques.md          → docs/
devdocs/folder-governance-spec.md             → specifications/content/governance/
```

---

## Migration Notes

**2025-11-22**: Cleaned up root directory; moved misplaced documentation:
- `Based on recent developments in AI-.txt` → `docs/ai-development-techniques.md`
- `soft sandbox" pattern.txt` → `docs/soft-sandbox-pattern.md`
- `tools has its own "instructions file" + config.txt` → `docs/tools-instructions-config.md`
- `used as a governance document for your pipeline.txt` → `specifications/content/governance/folder-governance-spec.md`

These files were **NOT** appropriate for `devdocs/` as they are permanent reference materials.

---

## Related Documentation

- **Permanent docs**: See `docs/README.md`
- **Specifications**: See `specifications/README.md`
- **Repository structure**: See `DIRECTORY_GUIDE.md`
- **AI guidelines**: See `AGENTS.md`
