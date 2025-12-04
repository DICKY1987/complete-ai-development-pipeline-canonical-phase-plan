# GENERATOR SCRIPT ANALYSIS

## Framework Generators (Reusable - Keep Active)

### Phase4 Tool Adapters (Potentially framework-level)
1. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_code_graph.py**
2. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_doc_index.py**
3. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_implementation_map.py**
4. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_repo_summary.py**
5. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_spec_index.py**
6. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_spec_mapping.py**
7. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_workstreams_from_openspec.py**
8. **phase4_routing/modules/tool_adapters/src/tools/generation/generate_workstreams.py**

### Active Dev Tools
9. **scripts/dev/generate_path_index.py** - Path index generation (active)
10. **scripts/generate_readmes.py** - README generation (active)
11. **scripts/generate_repository_map.py** - Repository mapping (active)

## One-Off/Migration Generators (Archive Candidates)
12. **scripts/generate_incomplete_report.py** - Incomplete implementation report
13. **scripts/generate_module_inventory.py** - Module inventory (one-off)
14. **scripts/generate_phase0_decisions.py** - Phase 0 decisions (one-off)
15. **scripts/generate_registry_backfill_plan.py** - Registry backfill (one-off)

## System Analysis (Keep for debugging)
16. **System _Analyze/SYS_generate_incomplete_report.py** - System analysis tool

## RECOMMENDATION:

### Keep Active (Framework/Dev Tools): 1-11
- Phase4 generators are part of tool adapter framework
- Dev tools actively used for maintenance
- README/map generators actively used

### Archive (One-Off): 12-15
- Incomplete implementation reports completed
- Module inventory already generated
- Phase 0 decisions already made
- Registry backfill plan already executed

### Analysis Tools: 16
- Keep for debugging/analysis purposes

## ACTION: Archive one-off generators
