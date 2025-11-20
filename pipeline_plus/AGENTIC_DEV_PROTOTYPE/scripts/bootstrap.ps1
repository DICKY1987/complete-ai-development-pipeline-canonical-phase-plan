#!/usr/bin/env pwsh
# Bootstrap script for Game Board Protocol system
# Initializes project structure required for phase execution

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "=== Game Board Protocol Bootstrap ===" -ForegroundColor Cyan
Write-Host ""

# Define project root (parent of scripts directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot

if ($Verbose) {
    Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
}

# Define directories to create
$Directories = @(
    ".tasks",
    ".tasks/queued",
    ".tasks/running",
    ".tasks/complete",
    ".tasks/failed",
    ".ledger",
    ".runs",
    "config",
    "schemas",
    "schemas/generated",
    "specs",
    "specs/metadata",
    "src",
    "src/validators",
    "src/orchestrator",
    "src/adapters",
    "tests",
    "tests/integration",
    "cli",
    "cli/commands",
    "docs",
    "examples",
    "templates"
)

# Create directories
Write-Host "Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $Directories) {
    $fullPath = Join-Path $ProjectRoot $dir
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would create: $dir" -ForegroundColor Gray
    } else {
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Host "  ✓ Created: $dir" -ForegroundColor Green
        } else {
            Write-Host "  ⊙ Exists: $dir" -ForegroundColor DarkGray
        }
    }
}

# Create README files for key directories
$ReadmeFiles = @{
    ".tasks/README.md" = @"
# Task Queue Directory

This directory contains the file-based task queue for phase execution.

## Structure

- `queued/` - Phases waiting to execute
- `running/` - Phases currently executing
- `complete/` - Successfully completed phases
- `failed/` - Failed phase executions

## Usage

Tasks are automatically managed by the orchestrator. Do not manually edit files in this directory.
"@
    ".ledger/README.md" = @"
# Ledger Directory

This directory tracks the execution history and state of all phases.

Each phase execution creates a ledger entry with:
- Execution start/end times
- State transitions
- Test results
- Error messages (if any)

## Format

Ledger files are named `{phase_id}.json` and contain execution metadata.
"@
    "specs/README.md" = @"
# Specifications Directory

This directory contains machine-readable specification documents.

## Files

- `UNIVERSAL_PHASE_SPEC_V1.md` - Universal phase specification
- `PRO_PHASE_SPEC_V1.md` - Professional phase specification template
- `DEV_RULES_V1.md` - Development rules (DO and DONT)
- `metadata/` - Section indices and cross-reference data

## Format

Specs use Spec-Doc v1 format with stable section IDs (UPS-*, PPS-*, DR-*).
"@
}

Write-Host ""
Write-Host "Creating README files..." -ForegroundColor Yellow
foreach ($file in $ReadmeFiles.Keys) {
    $fullPath = Join-Path $ProjectRoot $file
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would create: $file" -ForegroundColor Gray
    } else {
        if (-not (Test-Path $fullPath)) {
            $ReadmeFiles[$file] | Out-File -FilePath $fullPath -Encoding UTF8
            Write-Host "  ✓ Created: $file" -ForegroundColor Green
        } else {
            Write-Host "  ⊙ Exists: $file" -ForegroundColor DarkGray
        }
    }
}

# Create baseline schema file
$SchemaContent = @"
{
  "`$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Phase Specification Schema",
  "description": "Baseline schema for phase specifications (will be enhanced by PH-1E)",
  "type": "object",
  "required": ["phase_id", "objective", "file_scope", "acceptance_tests"],
  "properties": {
    "phase_id": {
      "type": "string",
      "pattern": "^PH-[0-9A-Z]+$",
      "description": "Unique phase identifier (e.g., PH-00, PH-1A)"
    },
    "workstream_id": {
      "type": "string",
      "description": "Workstream identifier"
    },
    "phase_name": {
      "type": "string",
      "description": "Human-readable phase name"
    },
    "objective": {
      "type": "string",
      "minLength": 10,
      "description": "Clear statement of what this phase accomplishes"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^PH-[0-9A-Z]+$"
      },
      "description": "List of phase IDs that must complete before this phase"
    },
    "file_scope": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "description": "Files and directories this phase can modify"
    },
    "acceptance_tests": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["test_id", "description", "command", "expected"],
        "properties": {
          "test_id": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "command": {
            "type": "string"
          },
          "expected": {
            "type": "string"
          }
        }
      },
      "minItems": 1,
      "description": "Programmatic tests that verify phase completion"
    }
  }
}
"@

$SchemaPath = Join-Path $ProjectRoot "config/schema.json"
if ($DryRun) {
    Write-Host ""
    Write-Host "  [DRY RUN] Would create: config/schema.json" -ForegroundColor Gray
} else {
    if (-not (Test-Path $SchemaPath)) {
        $SchemaContent | Out-File -FilePath $SchemaPath -Encoding UTF8
        Write-Host ""
        Write-Host "  ✓ Created: config/schema.json" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "  ⊙ Exists: config/schema.json" -ForegroundColor DarkGray
    }
}

# Create validation rules file
$ValidationRulesContent = @"
{
  "version": "1.0.0",
  "rules": [
    {
      "rule_id": "VR-001",
      "description": "Phase must have at least one acceptance test",
      "severity": "error",
      "check": "acceptance_tests.length >= 1"
    },
    {
      "rule_id": "VR-002",
      "description": "Phase ID must follow PH-XX format",
      "severity": "error",
      "check": "phase_id matches ^PH-[0-9A-Z]+$"
    },
    {
      "rule_id": "VR-003",
      "description": "File scope must not be empty",
      "severity": "error",
      "check": "file_scope.length >= 1"
    },
    {
      "rule_id": "VR-004",
      "description": "Dependencies must reference valid phase IDs",
      "severity": "error",
      "check": "all dependencies match ^PH-[0-9A-Z]+$"
    }
  ]
}
"@

$ValidationRulesPath = Join-Path $ProjectRoot "config/validation_rules.json"
if ($DryRun) {
    Write-Host "  [DRY RUN] Would create: config/validation_rules.json" -ForegroundColor Gray
} else {
    if (-not (Test-Path $ValidationRulesPath)) {
        $ValidationRulesContent | Out-File -FilePath $ValidationRulesPath -Encoding UTF8
        Write-Host "  ✓ Created: config/validation_rules.json" -ForegroundColor Green
    } else {
        Write-Host "  ⊙ Exists: config/validation_rules.json" -ForegroundColor DarkGray
    }
}

# Update .gitignore
$GitignorePath = Join-Path $ProjectRoot ".gitignore"
$GitignoreContent = @"
# Runtime directories
.runs/
.ledger/*.json
.tasks/queued/*.json
.tasks/running/*.json

# Backup files
.patch_backups/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Would update: .gitignore" -ForegroundColor Gray
} else {
    if (Test-Path $GitignorePath) {
        # Append if exists
        Add-Content -Path $GitignorePath -Value "`n# Game Board Protocol runtime`n$GitignoreContent"
        Write-Host "  ✓ Updated: .gitignore" -ForegroundColor Green
    } else {
        # Create new
        $GitignoreContent | Out-File -FilePath $GitignorePath -Encoding UTF8
        Write-Host "  ✓ Created: .gitignore" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Bootstrap Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review created directory structure" -ForegroundColor White
Write-Host "  2. Run validation script to verify setup" -ForegroundColor White
Write-Host "  3. Begin with Phase 0 (PH-00) execution" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "NOTE: This was a dry run. Re-run without -DryRun to apply changes." -ForegroundColor Magenta
}
