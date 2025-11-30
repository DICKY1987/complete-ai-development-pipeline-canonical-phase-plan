---
doc_id: DOC-GUIDE-INVOKE-ADOPTION-1287
---

# Phase G: Invoke/Invoke-Build Adoption & PowerShell Gallery Publishing

**Status**: PROPOSED - Not Yet Started  
**Date Created**: 2025-11-21  
**Dependencies**: Core pipeline functional (PH-05+ complete)  
**Estimated Total Effort**: 48-62 hours  
**Priority**: MEDIUM - Improves maintainability and reusability  

---

## Overview

Phase G modernizes the repository's build and automation infrastructure by:
1. Adopting **Invoke (Python)** for standardized subprocess orchestration
2. Adopting **Invoke-Build (PowerShell)** for task dependency graphs
3. Publishing reusable components to **PowerShell Gallery**
4. Establishing unified configuration hierarchy
5. Reducing duplication across 37+ scripts

**Strategic Value:**
- **Maintainability**: Centralized task definitions replace ad-hoc scripts
- **Performance**: Incremental builds and parallel execution
- **Reusability**: Other projects can consume published modules
- **Testability**: Mock-friendly subprocess abstractions
- **Discoverability**: Clear task graph shows what operations are available

---

## Phase Structure

This phase is divided into 5 workstreams executed in dependency order:

```
WS-G1: Unified Config (Foundation)
  ↓
WS-G2: Invoke Python Adoption (Subprocess Layer)
  ↓
WS-G3: Invoke-Build Adoption (PowerShell Layer)
  ↓
WS-G4: InvokeBuildHelper Integration (Validation Tasks)
  ↓
WS-G5: PowerShell Gallery Publishing (Distribution)
```

---

## WS-G1: Unified Configuration with Invoke Config Hierarchy

**Priority**: HIGH (Foundation for other workstreams)  
**Estimated Effort**: 8-10 hours  
**Risk Level**: MEDIUM (touches many config consumers)  

### Objective
Consolidate scattered configuration files into Invoke's hierarchical config system, providing clear precedence rules and environment-specific overrides.

### Current Pain Points
- Configuration spread across `config/*.yaml`, environment variables, hardcoded defaults
- No clear precedence (env var vs file vs default)
- Each tool/adapter loads config independently
- Difficult to override settings for local development vs CI

### Tasks

#### Part 1: Install Invoke and Create Base Config (2 hours)
1. Add `invoke>=2.2.0` to `requirements.txt`
2. Create `invoke.yaml` at repository root:
```yaml
# Project-level config (versioned)
tools:
  aider:
    timeout: 300
    model: "ollama/qwen2.5-coder:32b"
    flags: ["--yes-always", "--no-auto-commits"]
  pytest:
    timeout: 600
    args: ["-q", "--tb=short"]
  ruff:
    config: "pyproject.toml"
    args: ["check", "."]
  
orchestrator:
  dry_run: false
  max_retries: 3
  
paths:
  repo_root: "."
  workstreams_dir: "workstreams"
  state_db: "state/workstream_pipeline.db"
  worktrees_dir: ".worktrees"
  
error_engine:
  plugins_dir: "error/plugins"
  cache_dir: "state/error_cache"
```

3. Create `.invoke.yaml.example` for user-specific overrides:
```yaml
# User-level config (not versioned - goes in ~/.invoke.yaml or ./.invoke.yaml)
# Override project defaults for local development

tools:
  aider:
    model: "gpt-4"  # Override to use different model locally
  
orchestrator:
  dry_run: true  # Default to dry-run for local testing
```

4. Document precedence in `docs/CONFIGURATION_GUIDE.md`

#### Part 2: Migrate Existing Config Files (3-4 hours)
1. Map `config/tool_profiles.json` → `invoke.yaml` structure
2. Map `config/circuit_breakers.yaml` → `invoke.yaml`
3. Map `config/aim_config.yaml` → `invoke.yaml`
4. Keep domain-specific configs (e.g., `openspec/`) as-is, load via Invoke context
5. Update config loaders to use Invoke:
   - `core/engine/tools.py` → use `Context.config.tools`
   - `core/engine/circuit_breakers.py` → use `Context.config.orchestrator`
   - `aim/bridge.py` → use `Context.config.aim`

#### Part 3: Update Config Consumers (3-4 hours)
1. Refactor `core/engine/tools.py`:
```python
from invoke import Config

def load_tool_profiles(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load tool profiles from Invoke config hierarchy."""
    if config_path:
        cfg = Config(runtime_path=config_path)
    else:
        cfg = Config(project_location='.')
    
    return cfg.tools.to_dict()
```

2. Update all tool adapters to accept config via context
3. Update orchestrator to load config once and pass down
4. Add environment variable overrides (e.g., `INVOKE_TOOLS_AIDER_TIMEOUT=600`)

#### Part 4: Testing (1 hour)
1. Test config loading from `invoke.yaml`
2. Test user overrides from `.invoke.yaml`
3. Test env var precedence
4. Verify existing tests still pass

### Acceptance Tests
```python
# tests/test_invoke_config.py
def test_config_hierarchy():
    """Config loads from project → user → env in correct order."""
    cfg = Config(project_location='.')
    assert cfg.tools.pytest.timeout == 600  # From invoke.yaml
    
def test_env_override():
    """Environment variables override file config."""
    os.environ['INVOKE_TOOLS_PYTEST_TIMEOUT'] = '900'
    cfg = Config(project_location='.')
    assert cfg.tools.pytest.timeout == 900

def test_tool_profile_migration():
    """Old tool_profiles.json logic works via Invoke config."""
    profiles = load_tool_profiles()
    assert 'aider' in profiles
    assert profiles['aider']['timeout'] == 300
```

### Deliverables
- ✅ `invoke.yaml` at repo root
- ✅ `.invoke.yaml.example` template
- ✅ `docs/CONFIGURATION_GUIDE.md`
- ✅ Updated `core/engine/tools.py` to use Invoke config
- ✅ Tests verifying config hierarchy

### Migration Notes
- **Backward Compatibility**: Keep `config/` directory for 1-2 releases with deprecation warnings
- **CI Integration**: CI can set `INVOKE_*` env vars for overrides
- **Documentation**: Update AGENTS.md with new config patterns

---

## WS-G2: Adopt Invoke for Python Subprocess Orchestration

**Priority**: HIGH  
**Estimated Effort**: 16-24 hours  
**Risk Level**: MEDIUM-HIGH (touches 38+ subprocess call sites)  

### Objective
Replace fragmented `subprocess.run()` calls with Invoke's Context API for consistent error handling, timeouts, and testability.

### Current Pain Points
- 38+ files with subprocess calls, each with slightly different error handling
- Inconsistent timeout handling
- Difficult to test (requires mocking subprocess in every module)
- No centralized logging of command execution
- Scattered retry logic

### Tasks

#### Part 1: Create Invoke Context Wrapper (4-6 hours)
1. Create `core/invoke_utils.py`:
```python
"""Invoke Context utilities for the AI Development Pipeline."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from invoke import Context, Result, UnexpectedExit
from pathlib import Path

@dataclass
class CommandResult:
    """Standardized result matching ToolResult interface."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    started_at: str
    completed_at: str
    duration_sec: float
    timed_out: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def run_command(
    cmd: str,
    *,
    context: Optional[Context] = None,
    timeout: Optional[int] = None,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    warn: bool = True,
) -> CommandResult:
    """
    Run a command via Invoke with standardized result.
    
    Args:
        cmd: Command string to execute
        context: Invoke context (creates default if None)
        timeout: Timeout in seconds (uses config default if None)
        cwd: Working directory
        env: Environment variables to merge
        warn: Don't raise on non-zero exit (default True)
    
    Returns:
        CommandResult with execution details
    """
    if context is None:
        context = Context()
    
    started = datetime.utcnow()
    started_str = started.isoformat() + 'Z'
    
    try:
        # Merge environment
        if env:
            with context.cd(str(cwd) if cwd else '.'):
                result = context.run(
                    cmd,
                    hide=True,
                    warn=warn,
                    timeout=timeout,
                    env=env,
                )
        else:
            with context.cd(str(cwd) if cwd else '.'):
                result = context.run(
                    cmd,
                    hide=True,
                    warn=warn,
                    timeout=timeout,
                )
        
        completed = datetime.utcnow()
        duration = (completed - started).total_seconds()
        
        return CommandResult(
            command=cmd,
            exit_code=result.return_code,
            stdout=result.stdout or '',
            stderr=result.stderr or '',
            success=result.ok,
            started_at=started_str,
            completed_at=completed.isoformat() + 'Z',
            duration_sec=duration,
            timed_out=False,
        )
        
    except Exception as e:
        completed = datetime.utcnow()
        duration = (completed - started).total_seconds()
        
        # Handle timeout specifically
        timed_out = 'timed out' in str(e).lower()
        
        return CommandResult(
            command=cmd,
            exit_code=-1,
            stdout='',
            stderr=str(e),
            success=False,
            started_at=started_str,
            completed_at=completed.isoformat() + 'Z',
            duration_sec=duration,
            timed_out=timed_out,
        )
```

2. Create `tasks.py` at repo root with common operations:
```python
"""Invoke tasks for AI Development Pipeline."""
from invoke import task, Collection

@task
def bootstrap(c):
    """Initialize repository skeleton."""
    print("[bootstrap] Initializing repository skeleton...")
    # Call existing bootstrap logic
    c.run("pwsh ./scripts/bootstrap.ps1")

@task
def validate_workstreams(c):
    """Validate all workstream bundle files."""
    c.run("python scripts/validate_workstreams.py")

@task
def validate_imports(c):
    """Check for deprecated import patterns."""
    c.run("python scripts/validate_error_imports.py")

@task(pre=[validate_workstreams, validate_imports])
def validate(c):
    """Run all validation tasks."""
    print("[validate] All validations passed ✅")

@task
def test_unit(c):
    """Run unit tests."""
    c.run("pytest tests/unit -q")

@task
def test_integration(c):
    """Run integration tests."""
    c.run("pytest tests/integration -q")

@task
def test_pipeline(c):
    """Run pipeline tests."""
    c.run("pytest tests/pipeline -q")

@task(pre=[test_unit, test_pipeline, test_integration])
def test(c):
    """Run all tests."""
    print("[test] All tests complete ✅")

@task(pre=[validate, test])
def ci(c):
    """Run full CI validation suite."""
    print("[ci] CI validation complete ✅")

@task
def run_workstream(c, ws_id, dry_run=False):
    """Run a single workstream."""
    cmd = f"python scripts/run_workstream.py --ws-id {ws_id}"
    if dry_run:
        cmd += " --dry-run"
    c.run(cmd)

# Create collection for namespacing
ns = Collection()
ns.add_task(bootstrap)
ns.add_task(validate)
ns.add_task(test)
ns.add_task(ci)
ns.add_task(run_workstream)
```

#### Part 2: Refactor Tool Adapters (8-12 hours)
1. Update `core/engine/tools.py` to use `run_command()`:
```python
from core.invoke_utils import run_command, CommandResult

def run_tool(
    tool_id: str,
    context: Mapping[str, Any],
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None,
) -> ToolResult:
    """Run external tool via Invoke."""
    profile = get_tool_profile(tool_id)
    cmd = render_command(tool_id, context, profile)
    
    # Use Invoke instead of subprocess
    result = run_command(
        cmd,
        timeout=profile.get('timeout'),
        cwd=Path(context.get('working_dir', '.')),
        env=profile.get('env', {}),
    )
    
    # Convert to ToolResult for compatibility
    return ToolResult(
        tool_id=tool_id,
        command_line=result.command,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        timed_out=result.timed_out,
        started_at=result.started_at,
        completed_at=result.completed_at,
        duration_sec=result.duration_sec,
        success=result.success,
    )
```

2. Update all error engine plugins (15 files in `error/plugins/*/plugin.py`):
   - Replace `subprocess.run()` with `run_command()`
   - Remove custom timeout handling (Invoke handles it)
   - Simplify error capture

3. Update engine adapters:
   - `engine/adapters/aider_adapter.py`
   - `engine/adapters/codex_adapter.py`
   - `engine/adapters/tests_adapter.py`
   - `engine/adapters/git_adapter.py`

#### Part 3: Update Tests to Use MockContext (4-6 hours)
1. Create test utilities in `tests/conftest.py`:
```python
import pytest
from invoke import MockContext, Result

@pytest.fixture
def mock_invoke_context():
    """Provide MockContext for testing Invoke-based code."""
    return MockContext(run={
        'echo "test"': Result(stdout='test\n', exited=0),
        'pytest -q': Result(stdout='10 passed\n', exited=0),
    })

@pytest.fixture
def failing_mock_context():
    """MockContext that simulates command failures."""
    return MockContext(run={
        'ruff check .': Result(stderr='error found', exited=1),
    })
```

2. Update existing tests:
   - `tests/test_tools.py` → use `mock_invoke_context`
   - `tests/test_adapters.py` → use `mock_invoke_context`
   - Remove subprocess mocking in favor of Invoke mocks

#### Part 4: Documentation and Migration (2-3 hours)
1. Update `docs/ARCHITECTURE.md` with Invoke integration
2. Create `docs/INVOKE_MIGRATION_GUIDE.md`
3. Update AGENTS.md with new subprocess patterns:
```python
# ❌ OLD: Direct subprocess
proc = subprocess.run(['pytest', '-q'], capture_output=True, timeout=60)

# ✅ NEW: Via Invoke
from core.invoke_utils import run_command
result = run_command('pytest -q', timeout=60)
```

### Acceptance Tests
```python
# tests/test_invoke_integration.py
def test_run_command_success(mock_invoke_context):
    """Commands execute via Invoke Context."""
    result = run_command('echo "test"', context=mock_invoke_context)
    assert result.success
    assert 'test' in result.stdout

def test_run_command_timeout():
    """Timeouts are properly detected and reported."""
    # Long-running command with 1-second timeout
    result = run_command('sleep 10', timeout=1)
    assert result.timed_out
    assert not result.success

def test_tool_adapter_uses_invoke():
    """Tool adapters use Invoke instead of subprocess."""
    # Mock tool profile
    with patch('core.engine.tools.get_tool_profile') as mock_profile:
        mock_profile.return_value = {'exe': 'echo', 'timeout': 10}
        
        result = run_tool('test_tool', {})
        assert isinstance(result, ToolResult)
        # Verify no subprocess.run was called
```

### Deliverables
- ✅ `core/invoke_utils.py` - Wrapper utilities
- ✅ `tasks.py` - Common Invoke tasks
- ✅ Updated `core/engine/tools.py`
- ✅ Refactored error plugins (15 files)
- ✅ Refactored engine adapters (4 files)
- ✅ Updated tests with MockContext
- ✅ `docs/INVOKE_MIGRATION_GUIDE.md`

### Migration Strategy
1. **Week 1**: Core utilities and tool.py refactor
2. **Week 2**: Error plugins (batch updates)
3. **Week 3**: Engine adapters and tests
4. **Week 4**: Documentation and cleanup

---

## WS-G3: Adopt Invoke-Build for PowerShell Task Orchestration

**Priority**: MEDIUM  
**Estimated Effort**: 8-12 hours  
**Risk Level**: LOW (PowerShell scripts are currently simple)  

### Objective
Replace 10 ad-hoc PowerShell scripts with structured Invoke-Build tasks that provide dependency graphs, incremental builds, and parallel execution.

### Current State Analysis
```powershell
# Current scripts (no dependencies tracked):
scripts/bootstrap.ps1        # Setup
scripts/test.ps1             # Run pytest + markdown lint
scripts/ccpm_install.ps1     # Install CCPM
scripts/worktree_start.ps1   # Git worktree operations
scripts/worktree_merge.ps1   # Git merge
# ... 5 more scripts
```

### Tasks

#### Part 1: Install Invoke-Build (1 hour)
1. Install from PowerShell Gallery:
```powershell
Install-Module -Name InvokeBuild -Scope CurrentUser -Force
```

2. Create `build.ps1` at repo root:
```powershell
#Requires -Version 7.0
#Requires -Modules InvokeBuild

<#
.SYNOPSIS
    Invoke-Build script for AI Development Pipeline
.DESCRIPTION
    Defines build, test, validation, and deployment tasks
    Run with: Invoke-Build <TaskName>
#>

param(
    [string]$Configuration = 'Release'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Helper to get repo root
$script:RepoRoot = $PSScriptRoot

# Task: Bootstrap repository
task Bootstrap {
    Write-Build Cyan "Bootstrapping repository..."
    
    $dirs = 'docs','plans','scripts','tests','assets'
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
            Write-Build Green "Created ./$dir"
        }
    }
    
    # Check for Python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Build Gray "Python: $(python --version 2>&1)"
    }
}

# Task: Validate workstreams
task ValidateWorkstreams {
    Write-Build Cyan "Validating workstream bundles..."
    exec { python scripts/validate_workstreams.py }
}

# Task: Validate imports
task ValidateImports {
    Write-Build Cyan "Checking for deprecated imports..."
    exec { python scripts/validate_error_imports.py }
}

# Task: Run Python unit tests
task TestUnit {
    Write-Build Cyan "Running unit tests..."
    exec { python -m pytest tests/unit -q }
}

# Task: Run integration tests
task TestIntegration {
    Write-Build Cyan "Running integration tests..."
    exec { python -m pytest tests/integration -q }
}

# Task: Run pipeline tests
task TestPipeline {
    Write-Build Cyan "Running pipeline tests..."
    exec { python -m pytest tests/pipeline -q }
}

# Task: Lint Markdown (if markdownlint available)
task LintMarkdown -If (Get-Command markdownlint -ErrorAction SilentlyContinue) {
    Write-Build Cyan "Linting Markdown files..."
    $mdFiles = Get-ChildItem -Recurse -Include *.md
    if ($mdFiles) {
        exec { markdownlint $mdFiles.FullName }
    }
}

# Aggregate: Run all validation
task Validate ValidateWorkstreams, ValidateImports

# Aggregate: Run all tests
task Test TestUnit, TestPipeline, TestIntegration

# Aggregate: Full CI pipeline
task CI Bootstrap, Validate, Test, LintMarkdown {
    Write-Build Green "✅ CI validation complete"
}

# Task: Install CCPM
task InstallCCPM {
    Write-Build Cyan "Installing CCPM..."
    & "$PSScriptRoot/scripts/ccpm_install.ps1"
}

# Task: Clean generated files
task Clean {
    Write-Build Cyan "Cleaning generated files..."
    
    $cleanDirs = '.worktrees','state/*.db','logs/*.log','*.pyc','__pycache__'
    foreach ($pattern in $cleanDirs) {
        Get-ChildItem -Recurse -Include $pattern -Force | Remove-Item -Recurse -Force
    }
}

# Default task
task . CI
```

#### Part 2: Add Incremental Build Support (3-4 hours)
1. Add tasks with input/output tracking:
```powershell
# Task: Generate spec index (only if specs changed)
task GenerateSpecIndex -Inputs openspec/**/*.yaml -Outputs state/spec_index.json {
    Write-Build Cyan "Generating spec index..."
    exec { python scripts/generate_spec_index.py }
}

# Task: Generate spec mapping (only if specs changed)
task GenerateSpecMapping -Inputs openspec/**/*.yaml -Outputs state/spec_mapping.json {
    Write-Build Cyan "Generating spec mapping..."
    exec { python scripts/generate_spec_mapping.py }
}

# Task: Update indices (depends on both)
task UpdateIndices GenerateSpecIndex, GenerateSpecMapping
```

2. Incremental validation:
```powershell
task ValidateSchemas -Inputs schema/*.json, workstreams/*.json {
    Write-Build Cyan "Validating schemas..."
    exec { python scripts/validate_workstreams.py }
}
```

#### Part 3: Add Parallel Execution (2-3 hours)
1. Create parallel test task:
```powershell
# Run test suites in parallel
task TestParallel {
    Write-Build Cyan "Running tests in parallel..."
    
    Build-Parallel @(
        @{ File = 'build.ps1'; Task = 'TestUnit' }
        @{ File = 'build.ps1'; Task = 'TestPipeline' }
        @{ File = 'build.ps1'; Task = 'TestIntegration' }
    )
}
```

2. Parallel validation:
```powershell
task ValidateParallel {
    Build-Parallel @(
        @{ File = 'build.ps1'; Task = 'ValidateWorkstreams' }
        @{ File = 'build.ps1'; Task = 'ValidateImports' }
        @{ File = 'build.ps1'; Task = 'LintMarkdown' }
    )
}
```

#### Part 4: Migrate Existing Scripts (2-3 hours)
1. Keep original scripts as thin wrappers:
```powershell
# scripts/bootstrap.ps1 (new version)
#Requires -Modules InvokeBuild
Invoke-Build Bootstrap
```

2. Update CI workflows to use Invoke-Build:
```yaml
# .github/workflows/ci.yml
- name: Run CI validation
  run: Invoke-Build CI
```

#### Part 5: Documentation (1 hour)
1. Update README.md quick start:
```markdown
## Quick Start

# Bootstrap
Invoke-Build Bootstrap

# Run tests
Invoke-Build Test

# Full CI validation
Invoke-Build CI

# List all tasks
Invoke-Build ?
```

2. Create `docs/BUILD_SYSTEM.md` documenting all tasks

### Acceptance Tests
```powershell
# Test: Task listing works
Invoke-Build ? | Should -Match 'Bootstrap'

# Test: Incremental builds skip unchanged
Invoke-Build GenerateSpecIndex  # First run
$firstTime = (Get-Date)
Invoke-Build GenerateSpecIndex  # Second run should skip
# Verify task was skipped

# Test: Parallel execution works
$before = Get-Date
Invoke-Build TestParallel
$duration = (Get-Date) - $before
# Verify faster than sequential
```

### Deliverables
- ✅ `build.ps1` with task definitions
- ✅ Updated `scripts/*.ps1` as thin wrappers
- ✅ CI workflow using Invoke-Build
- ✅ `docs/BUILD_SYSTEM.md`

---

## WS-G4: Integrate InvokeBuildHelper for Common Patterns

**Priority**: LOW  
**Estimated Effort**: 4-6 hours  
**Risk Level**: LOW  

### Objective
Use community-maintained helper tasks from PowerShell Gallery to standardize validation patterns.

### Tasks

#### Part 1: Install InvokeBuildHelper (1 hour)
```powershell
Install-Module -Name InvokeBuildHelper -Scope CurrentUser
```

#### Part 2: Use Helper Tasks (2-3 hours)
```powershell
# Import helper tasks
. (Resolve-Path "$env:PSModulePath\InvokeBuildHelper\*\InvokeBuildHelperTasks.ps1")

# Use built-in Pester test task
task TestPowerShell {
    Invoke-InvokeBuildHelperPester -Path tests/powershell
}

# Use built-in analyzer task
task AnalyzePowerShell {
    Invoke-InvokeBuildHelperPSScriptAnalyzer -Path scripts/*.ps1
}
```

#### Part 3: Documentation (1 hour)
Document helper tasks in BUILD_SYSTEM.md

### Deliverables
- ✅ Updated `build.ps1` using helper tasks
- ✅ Documentation in BUILD_SYSTEM.md

---

## WS-G5: Publish Modules to PowerShell Gallery

**Priority**: LOW (Future-Facing)  
**Estimated Effort**: 12-16 hours  
**Risk Level**: MEDIUM (requires testing, signing, publishing pipeline)  

### Objective
Package reusable PowerShell components as modules publishable to PowerShell Gallery.

### Proposed Modules

#### AIPipeline.Core
- Bootstrap utilities
- Worktree management
- Configuration helpers

#### AIPipeline.CCPM
- GitHub sync functions
- CCPM integration utilities

#### AIPipeline.ErrorEngine
- Error plugin orchestration
- Detection utilities

### Tasks

#### Part 1: Create Module Manifests (4-5 hours)
1. Create `modules/AIPipeline.Core/AIPipeline.Core.psd1`:
```powershell
@{
    ModuleVersion = '1.0.0'
    GUID = '<new-guid>'
    Author = 'Your Name'
    Description = 'Core utilities for AI Development Pipeline'
    PowerShellVersion = '7.0'
    FunctionsToExport = @(
        'Invoke-PipelineBootstrap',
        'New-PipelineWorktree',
        'Get-PipelineConfig'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('AI', 'Pipeline', 'Automation', 'DevOps')
            LicenseUri = 'https://github.com/yourorg/repo/blob/main/LICENSE'
            ProjectUri = 'https://github.com/yourorg/repo'
        }
    }
}
```

2. Organize functions into module files

#### Part 2: Build Pipeline for Modules (4-5 hours)
```powershell
# build.ps1
task BuildModules {
    $modules = 'AIPipeline.Core', 'AIPipeline.CCPM', 'AIPipeline.ErrorEngine'
    foreach ($mod in $modules) {
        Write-Build Cyan "Building $mod..."
        # Update version in manifest
        # Run tests
        # Sign if configured
    }
}

task PublishModules -If ($env:PUBLISH_TO_GALLERY -eq '1') {
    # Publish to PSGallery with API key
    foreach ($mod in $modules) {
        Publish-Module -Path "modules/$mod" -NuGetApiKey $env:PSGALLERY_API_KEY
    }
}
```

#### Part 3: Documentation and Examples (3-4 hours)
1. Create README for each module
2. Add usage examples
3. Document installation

#### Part 4: Testing and Publishing (1-2 hours)
1. Test modules in isolated environment
2. Publish to test gallery first
3. Publish to production PSGallery

### Deliverables
- ✅ Module manifests (`.psd1`)
- ✅ Module files (`.psm1`)
- ✅ Build/publish pipeline
- ✅ Documentation and examples
- ✅ Published to PowerShell Gallery

---

## Success Criteria

### For WS-G1 (Config)
- [ ] All config loaded via `invoke.yaml`
- [ ] User overrides work via `.invoke.yaml`
- [ ] Environment variables override files
- [ ] Tests pass with new config system

### For WS-G2 (Invoke Python)
- [ ] Zero direct `subprocess.run()` calls in core code
- [ ] All adapters use `run_command()`
- [ ] Tests use `MockContext`
- [ ] `tasks.py` provides common operations
- [ ] CI runs via `inv ci`

### For WS-G3 (Invoke-Build)
- [ ] `build.ps1` defines all tasks
- [ ] Task dependencies work correctly
- [ ] Incremental builds skip unchanged work
- [ ] Parallel execution speeds up CI
- [ ] CI uses `Invoke-Build CI`

### For WS-G4 (Helper)
- [ ] InvokeBuildHelper installed
- [ ] Common patterns use helper tasks
- [ ] Documentation complete

### For WS-G5 (Gallery)
- [ ] Modules packaged and tested
- [ ] Published to PowerShell Gallery
- [ ] Installation instructions documented
- [ ] Version management in place

---

## Risk Mitigation

### Risk: Breaking Existing Workflows
**Mitigation**: 
- Keep original scripts as thin wrappers during transition
- Maintain backward compatibility for 2 releases
- Document migration path clearly

### Risk: Learning Curve for Invoke
**Mitigation**:
- Provide examples in `tasks.py`
- Document common patterns in AGENTS.md
- Use MockContext examples in tests/conftest.py

### Risk: Invoke-Build Not Available on All Systems
**Mitigation**:
- Check for module availability in CI
- Auto-install if missing
- Provide fallback to direct script calls

### Risk: Publishing to Gallery Requires Approval
**Mitigation**:
- Start with private/test gallery
- Get approvals early
- Document publishing process

---

## Dependencies

### External
- `invoke>=2.2.0` (Python package)
- `InvokeBuild` (PowerShell module)
- `InvokeBuildHelper` (PowerShell module, optional)
- PowerShell Gallery account for publishing

### Internal
- Core pipeline must be functional (PH-05+)
- Tests must exist for validation
- CI workflows must be operational

---

## Rollback Plan

If adoption causes issues:

1. **Immediate Rollback (WS-G2)**:
   - Revert `core/engine/tools.py`
   - Restore subprocess calls
   - Use git revert for batch changes

2. **Gradual Rollback (WS-G3)**:
   - CI can call original scripts directly
   - Remove Invoke-Build dependency
   - Keep build.ps1 for reference

3. **Config Rollback (WS-G1)**:
   - Restore original config files
   - Remove invoke.yaml
   - Revert config loaders

---

## Timeline Estimate

**Assuming 1 developer working part-time (20 hrs/week):**

- **Week 1-2**: WS-G1 (Config) - 8-10 hours
- **Week 3-5**: WS-G2 (Invoke Python) - 16-24 hours  
- **Week 6-7**: WS-G3 (Invoke-Build) - 8-12 hours
- **Week 8**: WS-G4 (Helper) - 4-6 hours
- **Week 9-10**: WS-G5 (Gallery Publishing) - 12-16 hours

**Total Duration**: 10-12 weeks part-time, or 2-3 weeks full-time

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Create workstream bundles** for each WS-G* workstream
3. **Prioritize WS-G1** as foundation (can execute independently)
4. **Execute in order**: G1 → G2 → G3 → G4 → G5
5. **Track progress** in phase checklist

---

## References

- Original evaluation: `Invoke_POWERSHELLGALLERY.md`
- Invoke docs: https://www.pyinvoke.org/
- Invoke-Build: https://github.com/nightroman/Invoke-Build
- PowerShell Gallery: https://www.powershellgallery.com/
- InvokeBuildHelper: https://www.powershellgallery.com/packages/InvokeBuildHelper
