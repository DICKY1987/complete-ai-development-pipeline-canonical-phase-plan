# Documentation System Analysis - Quick Reference

This directory contains the documentation system state analysis and findings.

## Files

### Analysis Tool
- **Tool**: `../scripts/analyze_documentation_system.py`
- **Documentation**: `../docs/DOC_reference/tools/DOCUMENTATION_ANALYSIS_CLI.md`
- **Tests**: `../tests/test_analyze_documentation_system.py`

### Reports
- **Latest Analysis**: `DOCUMENTATION_SYSTEM_STATE_ANALYSIS_20251206.md` - Human-readable comprehensive report
- **Latest JSON**: `documentation_system_analysis_20251206.json` - Machine-readable data

## Quick Start

```bash
# Run analysis
python scripts/analyze_documentation_system.py --output reports/doc_analysis.json

# View summary
python scripts/analyze_documentation_system.py | tail -20

# Check specific issues
cat reports/documentation_system_analysis_20251206.json | jq '.link_integrity.doc_ids.duplicates'
```

## Key Findings (2025-12-06)

- **SSOT Coverage**: 8/22 categories (36%) - HIGH RISK
- **Total doc_ids**: 852 documents
- **Duplicate doc_ids**: 39 conflicts requiring resolution
- **CI Automation**: 2/8 validators (25%) integrated

## Recommended Actions

1. **[HIGH]** Resolve 39 duplicate doc_ids
2. **[HIGH]** Create missing SSOT documents (13 categories)
3. **[MEDIUM]** Wire 6 validators into CI pipeline

See full report for details: `DOCUMENTATION_SYSTEM_STATE_ANALYSIS_20251206.md`
