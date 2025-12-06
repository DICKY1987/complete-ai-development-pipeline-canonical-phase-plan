---
doc_id: DOC-TOOL-ANALYZE-DOCUMENTATION-SYSTEM-001
doc_type: tool_guide
title: Documentation System State Analysis CLI
version: 1.0.0
status: active
owner: ai_agent
related_doc_ids:
  - DOC-DOCS-SYSTEM-STATE-ANALYSIS-CLI-001
description: >
  AI CLI tool that analyzes the current repository and documentation state
  relative to documentation quality, coverage, and automation requirements.
---

# Documentation System State Analysis CLI

**Tool**: `scripts/analyze_documentation_system.py`
**Status**: ✅ Active
**Spec**: Implements DOC-DOCS-SYSTEM-STATE-ANALYSIS-CLI-001

## Purpose

This tool analyzes the current state of the documentation system in the repository and produces a comprehensive, machine-readable report covering:

1. **SSOT Coverage** - Analysis of all 22 Single Source of Truth categories
2. **Link Integrity** - Validation of doc_id, pattern_id, module_id, and phase_id references
3. **Automation State** - Assessment of generators, validators, and CI integration
4. **Overall Assessment** - Risk level and recommended actions

## Usage

### Basic Usage

```bash
# Run analysis and output to stdout
python scripts/analyze_documentation_system.py

# Save report to file
python scripts/analyze_documentation_system.py --output doc_analysis_report.json

# Verbose output during analysis
python scripts/analyze_documentation_system.py --verbose
```

### Options

- `--repo-root PATH` - Repository root path (default: current directory)
- `--output PATH` - Output JSON file path (default: stdout)
- `--verbose` - Show detailed progress during analysis

## Output Format

The tool produces a JSON report with the following structure:

```json
{
  "ssot_coverage": {
    "total_categories": 22,
    "categories": [
      {
        "name": "Glossary & Vocabulary",
        "expected": true,
        "ssot_doc_found": true,
        "ssot_doc_path": "glossary/README.md",
        "doc_id": "DOC-GUIDE-README-424",
        "status": "ok|missing|candidate_only|duplicate",
        "notes": "Additional context"
      }
    ]
  },
  "link_integrity": {
    "doc_ids": {
      "total_in_files": 851,
      "total_in_registry": 5,
      "duplicates": ["DOC-XXX-001"],
      "dangling_references": [
        {
          "from_doc": "DOC-ABC-001",
          "missing_ref": "DOC-MISSING-001",
          "path": "docs/example.md"
        }
      ],
      "unregistered_ids": ["DOC-XYZ-001"]
    },
    "code_to_docs": {
      "implementations_without_docs": [],
      "docs_without_implementations": [],
      "invalid_doc_references_in_code": []
    }
  },
  "automation_state": {
    "generators": {
      "found": ["generate_pattern_files.ps1"],
      "ssot_to_doc_mapping": [],
      "coverage_assessment": "Found 5 generator scripts"
    },
    "validators": {
      "found": ["validate_pattern_registry.ps1"],
      "wired_into_ci": ["validate_pattern_registry.ps1"],
      "not_wired": ["validate_contracts.py"],
      "missing_but_expected": []
    },
    "auto_sections": {
      "docs_with_auto_blocks": ["README.md"],
      "stale_or_inconsistent": []
    },
    "scheduled_jobs": {
      "doc_health_jobs_found": ["doc_id_validation.yml"],
      "gaps": "Limited scheduled documentation health checks found"
    }
  },
  "overall_assessment": {
    "summary": "Documentation system has 8/22 SSOT categories fully documented (36%). Found 39 duplicate doc_ids. Automation: 8 validators, 2 wired to CI.",
    "risk_level": "high|medium|low",
    "key_findings": [
      "SSOT coverage: 8/22 categories have proper documentation",
      "Total doc_ids found: 851"
    ],
    "recommended_next_actions": [
      {
        "priority": "high",
        "description": "Create SSOT documents for missing categories",
        "suggested_files": ["docs/ssot/phase_model.md"]
      }
    ]
  }
}
```

## SSOT Categories Analyzed

The tool checks for SSOT documentation in 22 categories:

### Repo-wide Foundations
1. Glossary & Vocabulary
2. Phase Model (0-7)
3. Module & Folder Taxonomy
4. ID & Registry Scheme

### Execution & Orchestration
5. Task Lifecycle / State Machine
6. Orchestrator Execution Contract
7. Deterministic Mode / Safety Profile
8. Error Handling & Escalation Pipeline
9. Automation Health & Coverage

### Pattern System & Validation
10. Pattern Architecture & PAT-CHECK Rules
11. Doc Types & Frontmatter Schemas
12. README Structure & Doc Style

### Git, Branches & Multi-Agent Workflow
13. Branching & Multi-Agent Strategy
14. Safe Merge & Auto-Sync Strategy
15. GitHub Project / Issues Integration

### External Tools & Adapters
16. Tool Adapter Catalog
17. OpenSpec → Pipeline Integration
18. Claude Code Project Management (CCPM) Integration

### Data, Logs, and Monitoring
19. Logging & Event Schema
20. State Store & Registry Persistence
21. GUI / Dashboard Contract

### Per-Module SSOTs
22. Module Contract & Responsibilities (per module)

## Status Values

### SSOT Status
- `ok` - SSOT document found with valid doc_id
- `candidate_only` - Document found but missing doc_id or not marked as SSOT
- `missing` - No SSOT document found for this category
- `duplicate` - Multiple documents claiming to be SSOT for same category

### Risk Levels
- `low` - ≥70% SSOT categories properly documented
- `medium` - 40-70% SSOT categories properly documented
- `high` - <40% SSOT categories properly documented

## Integration

### CI/CD Integration

Add to `.github/workflows/documentation.yml`:

```yaml
name: Documentation Health Check
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Analyze Documentation System
        run: |
          python scripts/analyze_documentation_system.py \
            --output doc_analysis_report.json
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: doc-analysis-report
          path: doc_analysis_report.json
```

### As a Pre-Commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: doc-analysis
      name: Documentation System Analysis
      entry: python scripts/analyze_documentation_system.py
      language: system
      pass_filenames: false
      stages: [commit]
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/test_analyze_documentation_system.py -v

# Run specific test
pytest tests/test_analyze_documentation_system.py::test_scan_docs_for_ids -v
```

### Adding New SSOT Categories

To add a new SSOT category to check:

1. Add to `SSOT_CATEGORIES` dict in `analyze_documentation_system.py`
2. Add mapping in `_check_ssot_category()` method
3. Update documentation
4. Add test case

## Examples

### Example 1: Quick Check

```bash
$ python scripts/analyze_documentation_system.py
📊 Documentation System Analysis
Repository: /path/to/repo

🔍 Scanning repository...
  Found 1086 markdown files

================================================================================
📋 SUMMARY
================================================================================
Overall: Documentation system has 8/22 SSOT categories fully documented (36%). 
Found 39 duplicate doc_ids. Automation: 8 validators, 2 wired to CI.
Risk Level: HIGH

Key Findings:
  • SSOT coverage: 8/22 categories have proper documentation
  • Total doc_ids found: 851
  • Validators found: 8
  • CI-integrated validators: 2

Recommended Actions:
  [HIGH] Create SSOT documents for missing categories
  [HIGH] Resolve duplicate doc_ids
  [MEDIUM] Wire validators into CI pipeline
```

### Example 2: Generate Report for Review

```bash
$ python scripts/analyze_documentation_system.py \
    --output /tmp/doc_report.json

# Review specific sections
$ cat /tmp/doc_report.json | jq '.ssot_coverage.categories[] | select(.status == "missing")'
$ cat /tmp/doc_report.json | jq '.link_integrity.doc_ids.duplicates'
```

## Troubleshooting

### Issue: Tool runs slowly

**Solution**: The tool scans all markdown files. For large repos:
- Use `--repo-root` to scan only specific directories
- Run on CI with caching enabled

### Issue: Missing doc_ids not detected

**Solution**: Ensure documents have proper YAML frontmatter:
```yaml
---
doc_id: DOC-XXX-YYY-001
---
```

### Issue: False positives for duplicates

**Solution**: Check if doc_ids follow the correct format and are unique. Update docs with new unique IDs.

## Related Documentation

- **Spec**: DOC-DOCS-SYSTEM-STATE-ANALYSIS-CLI-001 - Requirements specification
- **Glossary**: SSOT Policy - `glossary/SSOT_POLICY_README.md`
- **Registry**: Pattern Index - `patterns/registry/PATTERN_INDEX.yaml`
- **Tests**: `tests/test_analyze_documentation_system.py`

## Change Log

### v1.0.0 (2025-12-06)
- Initial implementation
- 22 SSOT categories
- Link integrity checking
- Automation state analysis
- Risk assessment and recommendations
- Full test coverage

---

**Maintainer**: AI Agents
**Last Updated**: 2025-12-06
**Status**: Active
