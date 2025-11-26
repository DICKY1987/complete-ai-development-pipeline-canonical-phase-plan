# Repository Glossary

**Location**: `/glossary/`  
**Purpose**: Comprehensive terminology management for the AI Development Pipeline

---

## Quick Start

```bash
# Navigate to glossary
cd glossary

# View glossary
cat glossary.md

# Validate glossary
python scripts/validate_glossary.py

# Check for orphaned terms
python scripts/validate_glossary.py --check-orphans
```

---

## Folder Structure

```
glossary/
├── README.md                           # This file
├── glossary.md                         # Main glossary (user-facing, 75+ terms)
├── .glossary-metadata.yaml             # Machine-readable metadata
├── GLOSSARY_SYSTEM_OVERVIEW.md         # System overview and guide
│
├── docs/                               # Governance documentation
│   ├── DOC_GLOSSARY_GOVERNANCE.md      # Governance framework
│   ├── DOC_GLOSSARY_SCHEMA.md          # Term schema definition
│   └── DOC_GLOSSARY_CHANGELOG.md       # Update history
│
├── scripts/                            # Tooling
│   ├── README.md                       # Tooling documentation
│   ├── validate_glossary.py            # ✅ Validation tool (working)
│   ├── update_term.py                  # 🚧 Update tool (planned)
│   ├── extract_terms.py                # 🚧 Extract tool (planned)
│   ├── add_term.py                     # 🚧 Add tool (planned)
│   └── generate_glossary_index.py      # 🚧 Index generator (planned)
│
├── config/                             # Configuration
│   └── glossary_policy.yaml            # Validation rules (to create)
│
├── updates/                            # Patch specifications
│   └── README.md                       # Patch update docs (to create)
│
└── proposals/                          # New term proposals
    └── README.md                       # Proposal process (to create)
```

---

## Files Overview

### Core Files

**[glossary.md](glossary.md)**
- **Type**: User-facing documentation
- **Content**: 75+ terms organized alphabetically
- **Categories**: Core Engine, Patch Management, Error Detection, Specifications, State Management, Integrations, Framework, Project Management
- **Format**: Markdown with cross-references

**[.glossary-metadata.yaml](.glossary-metadata.yaml)**
- **Type**: Machine-readable metadata
- **Content**: Term IDs, implementation paths, relationships, patch history
- **Format**: YAML
- **Purpose**: Tracking, automation, validation

**[GLOSSARY_SYSTEM_OVERVIEW.md](GLOSSARY_SYSTEM_OVERVIEW.md)**
- **Type**: System documentation
- **Content**: Overview of entire glossary system
- **Audience**: Developers, architects, maintainers

### Documentation

**[docs/DOC_GLOSSARY_GOVERNANCE.md](docs/DOC_GLOSSARY_GOVERNANCE.md)**
- Complete governance framework
- Term lifecycle management
- Update mechanisms
- Quality standards
- Review processes

**[docs/DOC_GLOSSARY_SCHEMA.md](docs/DOC_GLOSSARY_SCHEMA.md)**
- JSON Schema for terms
- Metadata format
- Validation rules
- Templates

**[docs/DOC_GLOSSARY_CHANGELOG.md](docs/DOC_GLOSSARY_CHANGELOG.md)**
- Version history
- Patch-based changes
- Quality metrics
- Upcoming changes

### Tooling

**[scripts/validate_glossary.py](scripts/validate_glossary.py)** ✅ Working
- Validate structure and content
- Check cross-references
- Find orphaned terms
- Verify implementation paths

See [scripts/README.md](scripts/README.md) for complete tooling documentation.

---

## Term Identification System

All terms use unique IDs in format: `TERM-<CATEGORY>-<SEQUENCE>`

### Categories

| Code | Category | Description | Example |
|------|----------|-------------|---------|
| `ENGINE` | Core Engine | Execution orchestration | TERM-ENGINE-001 (Orchestrator) |
| `PATCH` | Patch Management | Patch lifecycle | TERM-PATCH-001 (Patch Artifact) |
| `ERROR` | Error Detection | Error handling | TERM-ERROR-001 (Error Plugin) |
| `SPEC` | Specifications | Spec management | TERM-SPEC-001 (OpenSpec) |
| `STATE` | State Management | Database & state | TERM-STATE-003 (Pipeline Database) |
| `INTEG` | Integrations | External tools | TERM-INTEG-001 (AIM) |
| `FRAME` | Framework | UET & foundations | TERM-FRAME-001 (UET) |
| `PM` | Project Management | CCPM & planning | TERM-PM-001 (CCPM) |

---

## Term Lifecycle

```
proposed → draft → active → deprecated → archived
    ↓         ↓       ↓
  rejected  rejected (updated)
```

**States**:
- **proposed** - Under review, not yet official
- **draft** - Being developed, not finalized
- **active** - Current, in-use term
- **deprecated** - Discouraged, replacement available
- **archived** - Historical, no longer relevant

---

## Common Tasks

### View the Glossary

```bash
# Read full glossary
cat glossary.md

# Search for a term
grep -i "orchestrator" glossary.md

# View metadata
cat .glossary-metadata.yaml
```

### Validate

```bash
# Full validation
python scripts/validate_glossary.py

# Quick check (structure only)
python scripts/validate_glossary.py --quick

# Check for orphaned terms
python scripts/validate_glossary.py --check-orphans

# Verify implementation paths
python scripts/validate_glossary.py --check-paths
```

### Add a New Term (Manual)

1. Edit `glossary.md`:
   ```markdown
   ### New Term
   **Category**: Core Engine
   **Definition**: Component that does X.
   
   **Related Terms**: [Orchestrator](#orchestrator)
   ```

2. Edit `.glossary-metadata.yaml`:
   ```yaml
   TERM-ENGINE-XXX:
     name: "New Term"
     category: "Core Engine"
     status: "active"
     added_date: "2025-11-25"
     last_modified: "2025-11-25T00:00:00Z"
   ```

3. Validate:
   ```bash
   python scripts/validate_glossary.py
   ```

### Update a Term

1. Edit definition in `glossary.md`
2. Update `last_modified` in `.glossary-metadata.yaml`
3. Add entry to `docs/DOC_GLOSSARY_CHANGELOG.md`
4. Validate

---

## Quality Standards

### Required for All Terms

- ✅ Clear definition (20-1000 characters)
- ✅ Category assignment
- ✅ At least 1 related term (recommend 2-5)
- ✅ Metadata entry with dates

### Recommended

- Implementation path (for code-based terms)
- Usage examples (for complex concepts)
- Schema references (for schema-driven terms)
- Type variants (where applicable)

### Quality Metrics

Current scores:
- **Total Terms**: 79
- **Active Terms**: 72
- **Implementation Coverage**: ~95%
- **Avg Related Terms**: 3.2
- **Orphaned Terms**: 0 (target)

---

## Integration Points

### With Repository Systems

1. **UET Framework**
   - Term IDs reference UET concepts
   - Schema refs link to UET schemas
   - Patch updates align with patch-first workflow

2. **Documentation**
   - Cross-referenced in all docs
   - Part of documentation index
   - Linked from implementation locations

3. **Codebase**
   - Implementation paths tracked
   - Entry points documented
   - Auto-extraction planned

4. **CI/CD**
   - Validation in PR checks (planned)
   - Auto-update changelog (planned)
   - Path verification

---

## Governance

**Review Cadence**:
- **Daily**: Automated validation (planned CI)
- **Weekly**: New term proposals reviewed
- **Monthly**: Quality review and refinement
- **Quarterly**: Comprehensive audit

**Approval Authority**:
- **New Terms**: Architecture team (2+ approvals)
- **Updates**: Any contributor (peer review)
- **Deprecation**: Architecture team decision
- **Schema Changes**: Architecture + governance team

---

## Contributing

### Proposing New Terms

Create a file in `proposals/`:

```yaml
# proposals/new-term.yaml
name: "New Concept"
category: "Core Engine"
definition: "Component that..."
status: "proposed"
proposed_by: "your-name"
rationale: "This concept appears frequently but lacks definition"
```

Then create GitHub issue with label `glossary-proposal`.

### Reporting Issues

Found an issue? Create GitHub issue with label `glossary-feedback`:

```markdown
**Term**: [Term Name] (TERM-XXX-NNN)
**Issue**: [unclear | incorrect | missing | improvement]
**Details**: [Description]
**Suggested Fix**: [Your suggestion]
```

### Development

See [scripts/README.md](scripts/README.md) for:
- Tool development guide
- Workflow documentation
- CI integration
- Future enhancements

---

## Related Documentation

### In This Folder

- [GLOSSARY_SYSTEM_OVERVIEW.md](GLOSSARY_SYSTEM_OVERVIEW.md) - Complete system overview
- [docs/DOC_GLOSSARY_GOVERNANCE.md](docs/DOC_GLOSSARY_GOVERNANCE.md) - Governance framework
- [docs/DOC_GLOSSARY_SCHEMA.md](docs/DOC_GLOSSARY_SCHEMA.md) - Schema definition
- [docs/DOC_GLOSSARY_CHANGELOG.md](docs/DOC_GLOSSARY_CHANGELOG.md) - Update history
- [scripts/README.md](scripts/README.md) - Tooling documentation

### Repository Documentation

- `../docs/DOC_DOCUMENTATION_INDEX.md` - Master documentation index
- `../docs/DOC_IMPLEMENTATION_LOCATIONS.md` - Code implementation locations
- `../docs/DOC_ARCHITECTURE.md` - System architecture
- `../README.md` - Repository overview

---

## Quick Reference

```bash
# Navigate to glossary
cd glossary

# Validate
python scripts/validate_glossary.py

# View term count
grep -c "^### " glossary.md

# List all term IDs
grep "^  TERM-" .glossary-metadata.yaml

# Find orphaned terms
python scripts/validate_glossary.py --check-orphans

# Check specific term
grep -A 10 "### Orchestrator" glossary.md
```

---

## Status

**Framework**: ✅ Complete  
**Documentation**: ✅ Complete  
**Validation Tool**: ✅ Working  
**Additional Tools**: 🚧 Planned and documented  
**CI Integration**: 🚧 Planned  

**Ready for**: Production use, term additions, validation

---

## Support

**Questions**: Contact architecture team  
**Issues**: Create GitHub issue with `glossary-*` label  
**Contributions**: Submit PR with validation passing

---

**Last Updated**: 2025-11-25  
**Version**: 1.0.0  
**Maintained By**: Architecture Team
