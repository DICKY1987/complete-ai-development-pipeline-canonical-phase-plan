---
doc_id: DOC-GUIDE-CHECKLIST-1282
---

# Phase G Execution Checklist

**Phase**: Invoke/Invoke-Build Adoption & PowerShell Gallery Publishing  
**Status**: 🟡 NOT STARTED  
**Started**: TBD  
**Target Completion**: TBD  

---

## Pre-Execution Validation

### Prerequisites
- [ ] Core pipeline functional (PH-05+ complete)
- [ ] All tests passing (`pytest -q`)
- [ ] CI pipeline operational
- [ ] Python 3.10+ available
- [ ] PowerShell 7.0+ available
- [ ] Git repository healthy

### Team Readiness
- [ ] Phase plan reviewed and approved
- [ ] Developer capacity allocated (48-62 hours)
- [ ] Stakeholders informed of changes
- [ ] Rollback procedures documented

---

## WS-G1: Unified Configuration ⏳

**Priority**: HIGH | **Effort**: 8-10 hrs | **Status**: ⬜ Not Started

### Part 1: Install Invoke and Create Base Config (2 hrs)
- [ ] Add `invoke>=2.2.0` to `requirements.txt`
- [ ] Run `pip install -r requirements.txt`
- [ ] Create `invoke.yaml` at repository root
  - [ ] Tools configuration (aider, pytest, ruff)
  - [ ] Orchestrator settings
  - [ ] Path configuration
  - [ ] Error engine settings
- [ ] Create `.invoke.yaml.example` template
- [ ] Add `.invoke.yaml` to `.gitignore` (user-specific)
- [ ] Document precedence in `docs/CONFIGURATION_GUIDE.md`

### Part 2: Migrate Existing Config Files (3-4 hrs)
- [ ] Map `config/tool_profiles.json` → `invoke.yaml`
- [ ] Map `config/circuit_breakers.yaml` → `invoke.yaml`
- [ ] Map `config/aim_config.yaml` → `invoke.yaml`
- [ ] Keep domain-specific configs as-is
- [ ] Test config loading from all sources

### Part 3: Update Config Consumers (3-4 hrs)
- [ ] Refactor `core/engine/tools.py::load_tool_profiles()`
- [ ] Update `core/engine/circuit_breakers.py` config loading
- [ ] Update `aim/bridge.py` config loading
- [ ] Add environment variable override support
- [ ] Document new patterns in AGENTS.md

### Part 4: Testing (1 hr)
- [ ] Create `tests/test_invoke_config.py`
- [ ] Test config hierarchy (project → user → env)
- [ ] Test environment variable overrides
- [ ] Verify existing tests still pass
- [ ] Run `pytest -q` - all tests pass

### Acceptance
- [ ] Config loads from `invoke.yaml`
- [ ] User overrides work via `.invoke.yaml`
- [ ] Env vars override file config
- [ ] All tests passing
- [ ] Documentation complete

**Sign-off**: __________ | **Date**: __________

---

## WS-G2: Invoke Python Adoption ⏳

**Priority**: HIGH | **Effort**: 16-24 hrs | **Status**: ⬜ Not Started  
**Depends on**: WS-G1 complete

### Part 1: Create Invoke Context Wrapper (4-6 hrs)
- [ ] Create `core/invoke_utils.py`
  - [ ] `CommandResult` dataclass
  - [ ] `run_command()` function
  - [ ] Timeout handling
  - [ ] Error capture
  - [ ] Result standardization
- [ ] Create `tasks.py` at repo root
  - [ ] `bootstrap` task
  - [ ] `validate` tasks (workstreams, imports)
  - [ ] `test` tasks (unit, integration, pipeline)
  - [ ] `ci` aggregate task
  - [ ] `run_workstream` task
- [ ] Test wrapper with simple commands
- [ ] Document usage patterns

### Part 2: Refactor Tool Adapters (8-12 hrs)
- [ ] Update `core/engine/tools.py::run_tool()`
  - [ ] Replace `subprocess.run()` with `run_command()`
  - [ ] Convert `CommandResult` → `ToolResult`
- [ ] Update error plugins (15 files):
  - [ ] `error/plugins/python_ruff/plugin.py`
  - [ ] `error/plugins/python_mypy/plugin.py`
  - [ ] `error/plugins/python_pylint/plugin.py`
  - [ ] `error/plugins/python_pyright/plugin.py`
  - [ ] `error/plugins/python_bandit/plugin.py`
  - [ ] `error/plugins/python_safety/plugin.py`
  - [ ] `error/plugins/python_black_fix/plugin.py`
  - [ ] `error/plugins/python_isort_fix/plugin.py`
  - [ ] `error/plugins/js_eslint/plugin.py`
  - [ ] `error/plugins/js_prettier_fix/plugin.py`
  - [ ] `error/plugins/yaml_yamllint/plugin.py`
  - [ ] `error/plugins/md_markdownlint/plugin.py`
  - [ ] `error/plugins/md_mdformat_fix/plugin.py`
  - [ ] `error/plugins/powershell_pssa/plugin.py`
  - [ ] `error/plugins/test_runner/plugin.py`
- [ ] Update engine adapters (4 files):
  - [ ] `engine/adapters/aider_adapter.py`
  - [ ] `engine/adapters/codex_adapter.py`
  - [ ] `engine/adapters/tests_adapter.py`
  - [ ] `engine/adapters/git_adapter.py`
- [ ] Remove custom timeout/error handling (DRY)

### Part 3: Update Tests with MockContext (4-6 hrs)
- [ ] Create fixtures in `tests/conftest.py`
  - [ ] `mock_invoke_context` fixture
  - [ ] `failing_mock_context` fixture
- [ ] Update `tests/test_tools.py`
- [ ] Update `tests/test_adapters.py`
- [ ] Update plugin tests (15 files)
- [ ] Remove subprocess mocking
- [ ] Verify all tests pass with new mocks

### Part 4: Documentation and Migration (2-3 hrs)
- [ ] Update `docs/ARCHITECTURE.md`
- [ ] Create `docs/INVOKE_MIGRATION_GUIDE.md`
- [ ] Update AGENTS.md with new patterns
- [ ] Add examples to README.md
- [ ] Document `tasks.py` usage

### Acceptance
- [ ] Zero direct `subprocess.run()` in core code
- [ ] All adapters use `run_command()`
- [ ] Tests use `MockContext`
- [ ] `invoke --list` shows available tasks
- [ ] `invoke ci` runs full validation
- [ ] All tests passing
- [ ] Documentation complete

**Sign-off**: __________ | **Date**: __________

---

## WS-G3: Invoke-Build Adoption ⏳

**Priority**: MEDIUM | **Effort**: 8-12 hrs | **Status**: ⬜ Not Started  
**Depends on**: WS-G2 complete

### Part 1: Install Invoke-Build (1 hr)
- [ ] Run `Install-Module -Name InvokeBuild -Scope CurrentUser`
- [ ] Verify installation: `Get-Module -ListAvailable InvokeBuild`
- [ ] Create `build.ps1` at repo root
- [ ] Define basic tasks (Bootstrap, Test, Validate)
- [ ] Test task execution: `Invoke-Build Bootstrap`

### Part 2: Add Incremental Build Support (3-4 hrs)
- [ ] Add `GenerateSpecIndex` task with `-Inputs`/`-Outputs`
- [ ] Add `GenerateSpecMapping` task with dependencies
- [ ] Add `UpdateIndices` aggregate task
- [ ] Add `ValidateSchemas` with input tracking
- [ ] Test incremental behavior (skip on no changes)

### Part 3: Add Parallel Execution (2-3 hrs)
- [ ] Create `TestParallel` task
  - [ ] Configure parallel test suites
  - [ ] Use `Build-Parallel`
- [ ] Create `ValidateParallel` task
  - [ ] Configure parallel validation
- [ ] Benchmark vs sequential execution
- [ ] Document speedup in BUILD_SYSTEM.md

### Part 4: Migrate Existing Scripts (2-3 hrs)
- [ ] Update `scripts/bootstrap.ps1` as wrapper
- [ ] Update `scripts/test.ps1` as wrapper
- [ ] Update other `.ps1` scripts
- [ ] Keep originals for backward compatibility
- [ ] Update CI workflows to use `Invoke-Build`

### Part 5: Documentation (1 hr)
- [ ] Update README.md quick start
- [ ] Create `docs/BUILD_SYSTEM.md`
- [ ] Document all available tasks
- [ ] Document incremental build usage
- [ ] Document parallel execution

### Acceptance
- [ ] `build.ps1` defines all tasks
- [ ] Task dependencies work correctly
- [ ] Incremental builds skip unchanged work
- [ ] Parallel execution works
- [ ] `Invoke-Build ?` lists tasks
- [ ] `Invoke-Build CI` runs full validation
- [ ] CI uses Invoke-Build
- [ ] Documentation complete

**Sign-off**: __________ | **Date**: __________

---

## WS-G4: InvokeBuildHelper Integration ⏳

**Priority**: LOW | **Effort**: 4-6 hrs | **Status**: ⬜ Not Started  
**Depends on**: WS-G3 complete

### Part 1: Install InvokeBuildHelper (1 hr)
- [ ] Run `Install-Module -Name InvokeBuildHelper -Scope CurrentUser`
- [ ] Verify installation
- [ ] Import helper tasks in `build.ps1`

### Part 2: Use Helper Tasks (2-3 hrs)
- [ ] Add Pester test task using helper
- [ ] Add PSScriptAnalyzer task using helper
- [ ] Replace custom validation with helpers
- [ ] Test helper task execution

### Part 3: Documentation (1 hr)
- [ ] Document helper tasks in BUILD_SYSTEM.md
- [ ] Add examples to README.md
- [ ] Update AGENTS.md

### Acceptance
- [ ] InvokeBuildHelper installed
- [ ] Helper tasks integrated
- [ ] Tests pass
- [ ] Documentation complete

**Sign-off**: __________ | **Date**: __________

---

## WS-G5: PowerShell Gallery Publishing ⏳

**Priority**: LOW | **Effort**: 12-16 hrs | **Status**: ⬜ Not Started  
**Depends on**: WS-G3, WS-G4 complete

### Part 1: Create Module Manifests (4-5 hrs)
- [ ] Create `modules/AIPipeline.Core/`
  - [ ] Module manifest (`.psd1`)
  - [ ] Module file (`.psm1`)
  - [ ] Function exports
  - [ ] README.md
- [ ] Create `modules/AIPipeline.CCPM/`
  - [ ] Module manifest
  - [ ] Module file
  - [ ] README.md
- [ ] Create `modules/AIPipeline.ErrorEngine/`
  - [ ] Module manifest
  - [ ] Module file
  - [ ] README.md
- [ ] Test modules locally

### Part 2: Build Pipeline for Modules (4-5 hrs)
- [ ] Add `BuildModules` task to `build.ps1`
- [ ] Add version management
- [ ] Add signing support (if configured)
- [ ] Add `PublishModules` task
- [ ] Configure API key handling
- [ ] Test build pipeline

### Part 3: Documentation and Examples (3-4 hrs)
- [ ] Create module READMEs
- [ ] Add usage examples
- [ ] Document installation
- [ ] Create changelog
- [ ] Add license information

### Part 4: Testing and Publishing (1-2 hrs)
- [ ] Test modules in isolated environment
- [ ] Test installation from local path
- [ ] Publish to test gallery (if available)
- [ ] Publish to production PowerShell Gallery
- [ ] Verify published modules work

### Acceptance
- [ ] Modules packaged and tested
- [ ] Published to PowerShell Gallery
- [ ] Installation works: `Install-Module AIPipeline.Core`
- [ ] Documentation complete
- [ ] Version management in place

**Sign-off**: __________ | **Date**: __________

---

## Post-Execution Validation

### Testing
- [ ] All unit tests pass (`pytest tests/unit -q`)
- [ ] All integration tests pass (`pytest tests/integration -q`)
- [ ] All pipeline tests pass (`pytest tests/pipeline -q`)
- [ ] Invoke tasks work (`invoke ci`)
- [ ] Invoke-Build tasks work (`Invoke-Build CI`)
- [ ] No performance regressions
- [ ] CI pipeline passes

### Documentation
- [ ] README.md updated with new workflows
- [ ] AGENTS.md updated with new patterns
- [ ] ARCHITECTURE.md includes Invoke integration
- [ ] Configuration guide complete
- [ ] Migration guide complete
- [ ] Build system docs complete

### Code Quality
- [ ] No deprecated subprocess calls in core
- [ ] All adapters use standardized interface
- [ ] Configuration centralized
- [ ] Tests use MockContext
- [ ] No regressions in functionality

### Cleanup
- [ ] Remove commented-out old code
- [ ] Archive deprecated config files
- [ ] Update .gitignore
- [ ] Clean up temporary files

---

## Metrics

### Before Phase G
- **Scripts**: 37 (10 PowerShell, 27 Python)
- **Config files**: 9 separate YAML/JSON files
- **Subprocess patterns**: 38+ different implementations
- **Test mocking**: Inconsistent across modules
- **CI commands**: 15+ direct script calls

### After Phase G (Target)
- **Task definitions**: ~30 reusable tasks
- **Config files**: 1 (`invoke.yaml` + overrides)
- **Subprocess patterns**: 1 (`run_command()`)
- **Test mocking**: Standardized `MockContext`
- **CI commands**: 2 (`invoke ci`, `Invoke-Build CI`)

### Success Metrics
- [ ] 90%+ reduction in subprocess boilerplate
- [ ] 50%+ reduction in config file count
- [ ] CI runtime improved by 20%+ (parallel execution)
- [ ] Zero hardcoded paths/timeouts in adapters
- [ ] Test mocking time reduced by 50%

---

## Sign-Off

### Phase Completion
- [ ] All workstreams complete (WS-G1 through WS-G5)
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Documentation complete
- [ ] CI pipeline updated
- [ ] Team trained on new workflows

### Approvals
- **Technical Lead**: __________ | **Date**: __________
- **QA Lead**: __________ | **Date**: __________
- **Project Manager**: __________ | **Date**: __________

---

## Notes

### Lessons Learned
_(To be filled during execution)_

### Issues Encountered
_(To be filled during execution)_

### Recommendations
_(To be filled during execution)_
