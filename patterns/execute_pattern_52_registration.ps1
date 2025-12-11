#!/usr/bin/env pwsh
# Execute registration of PATTERN_52 patterns

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$patternsDir = $PSScriptRoot
$repoRoot = Split-Path $patternsDir -Parent

# Load registration plan
$planPath = Join-Path $patternsDir "pattern_52_registration_plan.json"
if (-not (Test-Path $planPath)) {
    throw "Registration plan not found. Run register_pattern_52.ps1 first."
}

$plan = Get-Content $planPath | ConvertFrom-Json

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EXECUTING PATTERN_52 REGISTRATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Processing $($plan.Count) patterns..." -ForegroundColor Yellow
Write-Host "Dry Run: $DryRun" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host ""

# Load templates
$templatesDir = Join-Path $patternsDir "templates"
$specTemplate = Get-Content (Join-Path $templatesDir "pattern-spec.yaml") -Raw -ErrorAction SilentlyContinue
$schemaTemplate = Get-Content (Join-Path $templatesDir "pattern-schema.json") -Raw -ErrorAction SilentlyContinue
$executorTemplate = Get-Content (Join-Path $templatesDir "pattern-executor.ps1") -Raw -ErrorAction SilentlyContinue

# Create minimal templates if they don't exist
if (-not $specTemplate) {
    $specTemplate = @"
# {DOC_ID}
# Pattern: {PATTERN_NAME}
# Pattern ID: {PATTERN_ID}
# Version: 1.0.0
# Created: {CREATED_DATE}
# Category: {CATEGORY}

pattern_id: "{PATTERN_ID}"
name: "{PATTERN_NAME}"
version: "1.0.0"
category: "{CATEGORY}"
status: "draft"

metadata:
  created: "{CREATED_DATE}"
  last_updated: "{CREATED_DATE}"
  author: "Pattern Migration System"
  proven_uses: 0
  doc_id: "{DOC_ID}"

intent: |
  Pattern migrated from PATTERN_52 source files.
  {DESCRIPTION}

applicability:
  when_to_use:
    - "When following {PATTERN_NAME} pattern"
  when_not_to_use:
    - "TBD - requires pattern analysis"

inputs:
  pattern_context:
    type: "object"
    required: true
    description: "Context for pattern execution"

outputs:
  result:
    type: "object"
    description: "Pattern execution result"

steps:
  - step: "S1"
    name: "Load Pattern"
    description: "Load and validate pattern context"
    actions:
      - "Validate input parameters"
      - "Initialize pattern state"

verification:
  ground_truth:
    - condition: "Pattern loaded successfully"
      test: "Verify pattern_id matches"

tools:
  - claude_code
  - github_copilot_cli
  - cursor

notes: |
  This pattern was auto-migrated from PATTERN_52.
  Requires manual review and enhancement.
"@
}

if (-not $schemaTemplate) {
    $schemaTemplate = @"
{
  "`$schema": "http://json-schema.org/draft-07/schema#",
  "`$id": "https://uet.dev/schemas/{PATTERN_NAME}.v1.json",
  "title": "{PATTERN_NAME} Schema",
  "description": "Schema for {PATTERN_ID} pattern instances",
  "type": "object",
  "required": ["pattern_id"],
  "properties": {
    "pattern_id": {
      "type": "string",
      "const": "{PATTERN_ID}",
      "description": "Pattern identifier"
    },
    "context": {
      "type": "object",
      "description": "Pattern execution context"
    }
  }
}
"@
}

if (-not $executorTemplate) {
    $executorTemplate = @"
#!/usr/bin/env pwsh
# {DOC_ID}
<#
.SYNOPSIS
    Executor for {PATTERN_NAME} pattern ({PATTERN_ID})

.DESCRIPTION
    Auto-generated executor for {PATTERN_ID}.
    Requires manual implementation.

.PARAMETER InstancePath
    Path to pattern instance JSON file

.EXAMPLE
    .\{FILE_SYSTEM_NAME}_executor.ps1 -InstancePath instance.json

.NOTES
    Pattern: {PATTERN_ID}
    Version: 1.0.0
    Status: Draft - Requires Implementation
#>

param(
    [Parameter(Mandatory=`$true)]
    [string]`$InstancePath
)

`$ErrorActionPreference = "Stop"

Write-Host "{PATTERN_NAME} Executor" -ForegroundColor Cyan
Write-Host "=" * 50

# Load instance
if (-not (Test-Path `$InstancePath)) {
    throw "Instance file not found: `$InstancePath"
}

`$instance = Get-Content `$InstancePath -Raw | ConvertFrom-Json

# Validate pattern ID
if (`$instance.pattern_id -ne "{PATTERN_ID}") {
    throw "Invalid pattern_id: Expected {PATTERN_ID}, got `$(`$instance.pattern_id)"
}

Write-Host "Pattern validated: {PATTERN_ID}" -ForegroundColor Green

# TODO: Implement pattern logic

`$result = @{
    status = "success"
    pattern_id = "{PATTERN_ID}"
    message = "Executor requires implementation"
}

return `$result
"@
}

$successCount = 0
$failCount = 0

foreach ($pattern in $plan) {
    Write-Host "Processing: $($pattern.PatternID)" -ForegroundColor Cyan

    try {
        # Create spec
        $spec = $specTemplate `
            -replace '\{PATTERN_ID\}', $pattern.PatternID `
            -replace '\{DOC_ID\}', $pattern.DocID `
            -replace '\{PATTERN_NAME\}', $pattern.FileSystemName `
            -replace '\{CATEGORY\}', $pattern.Category `
            -replace '\{CREATED_DATE\}', (Get-Date -Format 'yyyy-MM-dd') `
            -replace '\{DESCRIPTION\}', "Migrated from $($pattern.SourceFile)"

        # Create schema
        $schema = $schemaTemplate `
            -replace '\{PATTERN_ID\}', $pattern.PatternID `
            -replace '\{PATTERN_NAME\}', $pattern.FileSystemName

        # Create executor
        $executor = $executorTemplate `
            -replace '\{PATTERN_ID\}', $pattern.PatternID `
            -replace '\{DOC_ID\}', $pattern.DocID `
            -replace '\{PATTERN_NAME\}', $pattern.Name `
            -replace '\{FILE_SYSTEM_NAME\}', $pattern.FileSystemName

        if (-not $DryRun) {
            # Write spec file
            $specPath = Join-Path $repoRoot $pattern.SpecPath
            $specDir = Split-Path $specPath -Parent
            if (-not (Test-Path $specDir)) {
                New-Item -Path $specDir -ItemType Directory -Force | Out-Null
            }
            Set-Content -Path $specPath -Value $spec -Encoding UTF8

            # Write schema file
            $schemaPath = Join-Path $repoRoot $pattern.SchemaPath
            $schemaDir = Split-Path $schemaPath -Parent
            if (-not (Test-Path $schemaDir)) {
                New-Item -Path $schemaDir -ItemType Directory -Force | Out-Null
            }
            Set-Content -Path $schemaPath -Value $schema -Encoding UTF8

            # Write executor file
            $executorPath = Join-Path $repoRoot $pattern.ExecutorPath
            $executorDir = Split-Path $executorPath -Parent
            if (-not (Test-Path $executorDir)) {
                New-Item -Path $executorDir -ItemType Directory -Force | Out-Null
            }
            Set-Content -Path $executorPath -Value $executor -Encoding UTF8

            Write-Host "  ✓ Created spec, schema, and executor" -ForegroundColor Green
        } else {
            Write-Host "  [DRY RUN] Would create spec, schema, and executor" -ForegroundColor Yellow
        }

        $successCount++
    }
    catch {
        Write-Host "  ✗ Failed: $_" -ForegroundColor Red
        $failCount++
    }
}

# Update registry
Write-Host ""
Write-Host "Updating registry..." -ForegroundColor Cyan

$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"
$registryContent = if (Test-Path $registryPath) {
    Get-Content $registryPath -Raw
} else {
    @"
# Pattern Registry Index
# Auto-generated by Pattern Registration System

metadata:
  total_patterns: 0
  last_updated: "$(Get-Date -Format 'yyyy-MM-dd')"
  version: "1.0.0"

patterns:
"@
}

# Parse existing patterns count
if ($registryContent -match 'total_patterns:\s*(\d+)') {
    $currentCount = [int]$matches[1]
} else {
    $currentCount = 0
}

# Add new patterns to registry
$newEntries = foreach ($pattern in $plan) {
    @"

- pattern_id: $($pattern.PatternID)
  name: $($pattern.FileSystemName)
  version: 1.0.0
  status: draft
  category: $($pattern.Category)
  doc_id: $($pattern.DocID)
  spec_path: $($pattern.SpecPath)
  schema_path: $($pattern.SchemaPath)
  executor_path: $($pattern.ExecutorPath)
  created: '$(Get-Date -Format 'yyyy-MM-dd')'
  summary: "Migrated from $($pattern.SourceFile)"
"@
}

if (-not $DryRun) {
    # Update total count
    $newTotal = $currentCount + $successCount
    $registryContent = $registryContent -replace 'total_patterns:\s*\d+', "total_patterns: $newTotal"
    $todayDate = Get-Date -Format 'yyyy-MM-dd'
    $registryContent = $registryContent -replace 'last_updated:\s*[''"]?[\d\-]+[''"]?', "last_updated: '$todayDate'"

    # Append new patterns
    $updatedRegistry = $registryContent + ($newEntries -join "")

    Set-Content -Path $registryPath -Value $updatedRegistry -Encoding UTF8
    Write-Host "  ✓ Registry updated with $successCount new patterns" -ForegroundColor Green
} else {
    Write-Host "  [DRY RUN] Would add $successCount patterns to registry" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  REGISTRATION COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Total patterns: $($plan.Count)" -ForegroundColor White
Write-Host "  Successful: $successCount" -ForegroundColor Green
Write-Host "  Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Red' } else { 'Gray' })
Write-Host ""

if (-not $DryRun) {
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review generated patterns in specs/, schemas/, and executors/" -ForegroundColor Gray
    Write-Host "  2. Enhance pattern specifications with actual details" -ForegroundColor Gray
    Write-Host "  3. Implement executor logic" -ForegroundColor Gray
    Write-Host "  4. Test patterns" -ForegroundColor Gray
    Write-Host "  5. Commit to version control" -ForegroundColor Gray
}
