---
doc_id: DOC-GUIDE-HANDOFF-PROMPT-1223
---

# AI Agent Handoff Prompt - Universal Execution Templates Framework

**Paste this entire prompt into your AI assistant to continue development.**

---

## Context: You are continuing development of the Universal Execution Templates (UET) Framework

### Current Status: 45% Complete (Excellent Progress!)

You are picking up work on a **schema-first, project-agnostic automation framework** that enables AI agents to autonomously install themselves on any project and execute workstreams with full validation and audit trails.

### What Has Been Completed

**Phase 0: Schema Foundation** ✅ 100% COMPLETE
- 17 JSON Schema files in `schema/` directory
- All schemas validate as JSON Schema draft-07
- 22 passing tests in `tests/schema/`
- Covers: runs, patches, prompts, phases, workstreams, tasks, profiles, bootstrap

**Phase 1: Profile System** ✅ 60% COMPLETE
- 5 domain profiles in `profiles/` directory:
  - `software-dev-python/` - Python development (has 4 phase templates)
  - `data-pipeline/` - ETL and data processing
  - `operations/` - Infrastructure and deployments
  - `documentation/` - Docs-only projects
  - `generic/` - Fallback for mixed projects
- All profiles validate against `schema/profile_extension.v1.json`

**Phase 2: Bootstrap Implementation** ✅ 60% COMPLETE
- Three working Python modules in `core/bootstrap/`:
  1. `discovery.py` - Scans projects, detects languages/domain/structure
  2. `selector.py` - Selects appropriate profile based on discovery
  3. `generator.py` - Creates PROJECT_PROFILE.yaml + router_config.json + directories
- **Pipeline works end-to-end and all outputs validate!** ✅

### Current Working Directory
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── schema/                    # 17 JSON schemas (COMPLETE)
├── profiles/                  # 5 domain profiles (COMPLETE)
├── core/bootstrap/            # 3 modules (discovery, selector, generator)
├── tests/schema/              # Schema validation tests
├── STATUS.md                  # Quick status summary
├── SESSION_CHECKPOINT_2025-11-20_FINAL.md  # Full session report
└── UET_FRAMEWORK_COMPLETION_PHASE_PLAN.md  # Complete roadmap
```

### Test the Bootstrap Pipeline
```bash
# This works right now:
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
python core/bootstrap/discovery.py . > test_discovery.json
python core/bootstrap/selector.py test_discovery.json
# You'll see it selects "generic" profile for this mixed-domain project

# To test full pipeline:
mkdir test_output
python core/bootstrap/generator.py test_discovery.json profiles/generic/profile.json test_output
# Check test_output/ for generated PROJECT_PROFILE.yaml and router_config.json
```

---

## Your Mission: Continue Phase 2 Bootstrap

### Next Task: WS-02-03A - Validation Engine (Estimated 4 days)

**Goal:** Add validation layer to ensure bootstrap outputs are correct and consistent

**Create:** `core/bootstrap/validator.py`

**Requirements:**

1. **Schema Validation**
   - Validate PROJECT_PROFILE.yaml against `schema/project_profile.v1.json`
   - Validate router_config.json against `schema/router_config.v1.json`
   - Return clear error messages with field paths

2. **Constraint Checking**
   - Ensure constraints aren't relaxed (e.g., profile says max_lines_changed=300, PROJECT_PROFILE doesn't increase it)
   - Check that forbidden paths are respected
   - Validate resource type consistency

3. **Consistency Checks**
   - Tools in router_config must be in available_tools
   - Profile_id in PROJECT_PROFILE must exist in profiles/
   - Paths in framework_paths must be valid

4. **Auto-Fix Common Issues**
   - Normalize paths (convert \ to / on Windows)
   - Add missing default values
   - Fix common YAML/JSON formatting issues

5. **Human Escalation**
   - For conflicts that can't be auto-fixed, generate clear report
   - Suggest fixes in human-readable format

**Interface:**
```python
class BootstrapValidator:
    def __init__(self, project_profile_path, router_config_path, profile_id):
        """Load artifacts to validate"""
        
    def validate_all(self) -> Dict:
        """
        Run all validations.
        
        Returns:
            {
                "valid": True/False,
                "errors": [...],
                "warnings": [...],
                "auto_fixed": [...],
                "needs_human": [...]
            }
        """
```

**Test Cases:**
1. Valid artifacts → all checks pass
2. Invalid schema → caught with clear error
3. Relaxed constraint → error with explanation
4. Missing tool → warning (not error)
5. Invalid path → auto-fixed if possible

---

## After WS-02-03A: Next Steps

### WS-02-04A - Bootstrap Orchestrator (Estimated 3 days)

**Create:** `core/bootstrap/orchestrator.py` + CLI entry point

Orchestrate the complete flow:
```
discovery.py → selector.py → generator.py → validator.py → report.json
```

**CLI Interface:**
```bash
uet bootstrap init <project_path>
# Runs full pipeline, generates bootstrap_report.v1.json
```

---

## Key Constraints & Conventions

### Code Style
- Python 3.12+
- Type hints preferred
- Keep modules small (60-150 lines)
- Use pathlib.Path for file operations
- UTF-8 encoding for all files

### Validation
- **ALL outputs must validate against schemas**
- Use `jsonschema` library: `validate(data, schema)`
- Test immediately after creating

### File Operations (Windows)
```python
# Use Set-Content in PowerShell or open() with encoding
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
```

### Testing
```python
# Run all schema tests
pytest tests/schema/ -v

# Run specific test
pytest tests/schema/test_all_schemas.py -v
```

### Git Workflow
```bash
# Make frequent commits
git add -A
git commit -m "WS-02-03A: Add validation engine with constraint checking"
```

---

## Important Files to Reference

1. **UET_FRAMEWORK_COMPLETION_PHASE_PLAN.md** - Full roadmap with all workstreams
2. **SESSION_CHECKPOINT_2025-11-20_FINAL.md** - Detailed progress report
3. **STATUS.md** - Quick status summary
4. **schema/*.json** - All data structure definitions
5. **profiles/*/profile.json** - Domain-specific configurations

---

## Example: How to Validate Against Schema

```python
import json
from jsonschema import validate, ValidationError

# Load schema
with open('schema/project_profile.v1.json') as f:
    schema = json.load(f)

# Load data
with open('PROJECT_PROFILE.yaml') as f:
    import yaml
    data = yaml.safe_load(f)

# Validate
try:
    validate(data, schema)
    print("✅ Valid!")
except ValidationError as e:
    print(f"❌ Invalid: {e.message}")
    print(f"   Path: {'.'.join(str(p) for p in e.path)}")
```

---

## Success Criteria for WS-02-03A

- [ ] `core/bootstrap/validator.py` created
- [ ] All 5 validation types implemented (schema, constraints, consistency, auto-fix, escalation)
- [ ] Returns structured validation results
- [ ] Test suite covers valid, invalid, and edge cases
- [ ] Integration with existing bootstrap modules tested
- [ ] All outputs still validate against schemas
- [ ] Documentation updated
- [ ] Git commit with clear message

---

## Quick Start Commands

```bash
# Navigate to project
cd "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"

# Review current status
cat STATUS.md

# See what's been built
ls -R schema/ profiles/ core/bootstrap/

# Run existing tests
pytest tests/schema/ -v

# Start building validator.py
# (Use the interface and requirements above)
```

---

## Questions? Check These Resources

1. **What schemas exist?** → `ls schema/` (17 files)
2. **What profiles exist?** → `ls profiles/` (5 directories)
3. **What does discovery output?** → `python core/bootstrap/discovery.py .`
4. **What's the phase plan?** → `cat UET_FRAMEWORK_COMPLETION_PHASE_PLAN.md`
5. **Full session details?** → `cat SESSION_CHECKPOINT_2025-11-20_FINAL.md`

---

## Philosophy & Design Principles

1. **Schema-First:** Define data structures before code
2. **Validate Everything:** No invalid artifacts should ever exist
3. **Autonomous:** AI should be able to do this without humans
4. **Project-Agnostic:** Works on any project type
5. **Auditable:** Complete trail of all changes
6. **Reversible:** Patches are unified diffs (works with git)

---

## You've Got This! 🚀

The foundation is **solid**, the architecture is **clean**, and 45% of the framework is **complete and working**. 

Your task is clear: **build the validation engine** to ensure bootstrap outputs are correct.

Start with `core/bootstrap/validator.py` and implement the 5 validation types. Test thoroughly. Make it robust.

**Good luck!** The framework is counting on you. 💪

---

**Last Updated:** 2025-11-20 21:51 UTC  
**Status:** Ready for WS-02-03A  
**Progress:** 45% Complete  
**Next Milestone:** Bootstrap validation engine
