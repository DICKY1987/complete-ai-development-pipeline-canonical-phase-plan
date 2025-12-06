#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-SETUP-DEV-ENVIRONMENT-831
# Enhanced development environment bootstrap script
# Automated setup for new developers

param(
    [switch]$SkipPreCommit,
    [switch]$SkipTests,
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$VerbosePreference = if ($Verbose) { 'Continue' } else { 'SilentlyContinue' }

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Development Environment Bootstrap                 ║" -ForegroundColor Cyan
Write-Host "║  Complete AI Development Pipeline                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Navigate to repository root
$repoRoot = if ($PSScriptRoot) {
    Resolve-Path (Join-Path $PSScriptRoot '..')
} else {
    Get-Location
}
Set-Location $repoRoot
Write-Host "📁 Repository: $repoRoot" -ForegroundColor Gray

# Step 1: Python version check
Write-Host "`n[1/7] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Found: $pythonVersion" -ForegroundColor Green

    # Extract version number
    if ($pythonVersion -match 'Python (\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "  ⚠️  Python 3.11+ required, found $major.$minor" -ForegroundColor Red
            Write-Host "  📥 Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "  ❌ Python not found" -ForegroundColor Red
    Write-Host "  📥 Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Install Python dependencies
Write-Host "`n[2/7] Installing Python dependencies..." -ForegroundColor Yellow
try {
    Write-Host "  📦 Installing from requirements.txt..." -ForegroundColor Gray
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt --quiet
    Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to install dependencies: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Install package in editable mode
Write-Host "`n[3/7] Installing package in development mode..." -ForegroundColor Yellow
try {
    if (Test-Path "pyproject.toml") {
        python -m pip install -e . --quiet
        Write-Host "  ✅ Package installed in editable mode" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  No pyproject.toml found, skipping editable install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  Could not install in editable mode: $_" -ForegroundColor Yellow
}

# Step 4: Setup pre-commit hooks
if (-not $SkipPreCommit) {
    Write-Host "`n[4/7] Setting up pre-commit hooks..." -ForegroundColor Yellow
    try {
        python -m pip install pre-commit --quiet
        pre-commit install --install-hooks
        Write-Host "  ✅ Pre-commit hooks installed" -ForegroundColor Green
        Write-Host "  ℹ️  Hooks will run automatically on git commit" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠️  Failed to install pre-commit hooks: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[4/7] Skipping pre-commit hooks (--SkipPreCommit)" -ForegroundColor Gray
}

# Step 5: Create necessary directories
Write-Host "`n[5/7] Creating workspace directories..." -ForegroundColor Yellow
$directories = @('.state', '.ledger', '.worktrees', 'docs', 'tests', 'scripts', 'reports')
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  📁 Created: $dir" -ForegroundColor Gray
    }
}
Write-Host "  ✅ Workspace directories ready" -ForegroundColor Green

# Step 6: Validate environment
Write-Host "`n[6/7] Validating environment..." -ForegroundColor Yellow
$validationErrors = @()

# Check critical tools
$tools = @{
    'pytest' = 'pytest --version'
    'black' = 'black --version'
    'isort' = 'isort --version'
    'ruff' = 'ruff --version'
}

foreach ($tool in $tools.Keys) {
    try {
        $null = Invoke-Expression $tools[$tool] 2>&1
        Write-Host "  ✅ $tool available" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $tool not found" -ForegroundColor Red
        $validationErrors += $tool
    }
}

if ($validationErrors.Count -gt 0) {
    Write-Host "  ⚠️  Some tools missing: $($validationErrors -join ', ')" -ForegroundColor Yellow
    Write-Host "  💡 Run: pip install pytest black isort ruff" -ForegroundColor Yellow
}

# Step 7: Run quick validation tests
if (-not $SkipTests) {
    Write-Host "`n[7/7] Running validation tests..." -ForegroundColor Yellow
    try {
        Write-Host "  🧪 Running quick test suite..." -ForegroundColor Gray
        $testResult = pytest -x -q -m "not slow" --tb=short 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ All validation tests passed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Some tests failed (this is OK for first setup)" -ForegroundColor Yellow
            Write-Host "  💡 Run 'pytest -v' for details" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠️  Could not run tests: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[7/7] Skipping validation tests (--SkipTests)" -ForegroundColor Gray
}

# Success summary
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ Development Environment Ready!                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Read: AGENTS.md (AI agent guidelines)" -ForegroundColor White
Write-Host "  2. Read: README.md (project overview)" -ForegroundColor White
Write-Host "  3. Run tests: pytest -v" -ForegroundColor White
Write-Host "  4. Create feature branch: git checkout -b feature/your-feature" -ForegroundColor White
Write-Host "  5. Start coding! 🚀" -ForegroundColor White

Write-Host "`n💡 Useful Commands:" -ForegroundColor Cyan
Write-Host "  pytest -v              # Run all tests" -ForegroundColor Gray
Write-Host "  pytest --cov           # Run with coverage" -ForegroundColor Gray
Write-Host "  black .                # Format code" -ForegroundColor Gray
Write-Host "  ruff check .           # Lint code" -ForegroundColor Gray
Write-Host "  pre-commit run --all-files  # Run all pre-commit hooks" -ForegroundColor Gray

Write-Host ""
