# VALIDATOR SCRIPT ANALYSIS

## Framework Validators (Reusable - Keep Active)
These are reusable validation tools that should remain in their locations:

### Domain-Specific (Keep in place)
1. **doc_id/validate_doc_id_coverage.py** - Doc ID system validation
2. **glossary/scripts/validate_glossary.py** - Glossary term validation
3. **gui/validate_gui.py** - GUI component validation
4. **patterns/validate_automation.py** - Pattern automation validation

### Tool Adapters (Phase4 - Consider consolidation)
5. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_acs_conformance.py**
6. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_diagrams.py**
7. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_engine.py**
8. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_error_imports.py**
9. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_plan.py**
10. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_workstreams.py**
11. **phase4_routing/modules/tool_adapters/src/tools/validation/validate_workstreams_authoring.py**

### Core Validation Tools (Scripts - Active)
12. **scripts/validate_archival_safety.py** - Archive safety checks
13. **scripts/validate_registry.py** - Registry validation
14. **scripts/validate_phase_plan.py** - Phase plan validation

## Migration/One-Off Validators (Consider archiving after migration complete)
15. **scripts/validate_migration.py** - Migration validation (one-off)
16. **scripts/validate_migration_phase1.py** - Phase 1 migration (one-off)
17. **scripts/validate_extracted_templates.py** - Template extraction (one-off)
18. **scripts/validate_module_manifests.py** - Manifest validation (one-off)
19. **scripts/validate_modules.py** - Module validation (one-off)

## Test-Only Validators (Keep with tests)
20. **phase4_routing/modules/aim_tools/tests/validate_pool.py** - Test fixture
21. **tests/aim/validate_pool.py** - Test fixture
22. **phase4_routing/modules/tool_adapters/src/tools/validate_doc_org.py** - Doc organization

## RECOMMENDATION:
- **Keep active:** Framework validators (1-14)
- **Archive after use:** Migration validators (15-19)
- **No action:** Test fixtures (20-22)
- **Consider:** Move phase4 validators to core.validation module
