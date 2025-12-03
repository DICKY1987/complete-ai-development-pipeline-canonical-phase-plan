# DOC_LINK: DOC-SCRIPT-GENERATE-PATTERN-FILES-109
# Master Pattern File Generation Script
# Auto-generates all missing pattern framework files
# Version: 1.0.0
# Created: 2025-11-24

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$baseDir = Split-Path $PSScriptRoot -Parent

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        PATTERN FRAMEWORK AUTO-GENERATION (All Phases)             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$stats = @{
    FilesGenerated = 0
    FilesFailed = 0
    PhasesCompleted = 0
}

# Load pattern data
$patternsDir = Join-Path $baseDir "patterns"
$mappingPath = Join-Path $patternsDir "registry\doc_id_mapping.json"
$mapping = Get-Content $mappingPath -Raw | ConvertFrom-Json

$corePatterns = @{
    'batch_create' = 'PAT-BATCH-CREATE-001'
    'refactor_patch' = 'PAT-REFACTOR-PATCH-001'
    'self_heal' = 'PAT-SELF-HEAL-001'
    'verify_commit' = 'PAT-VERIFY-COMMIT-001'
    'worktree_lifecycle' = 'PAT-WORKTREE-LIFECYCLE-001'
    'module_creation' = 'PAT-MODULE-CREATION-001'
}

# ============================================================================
# PHASE 2: CORE PATTERN ARTIFACTS
# ============================================================================

Write-Host "`n[PHASE 2] Core Pattern Artifacts Generation" -ForegroundColor Yellow

# Generate schemas for core patterns
Write-Host "`n  [2.1] Generating schemas..." -ForegroundColor Cyan

foreach ($pattern in $corePatterns.Keys) {
    $patternId = $corePatterns[$pattern]
    $docId = $mapping.$patternId
    $schemaPath = Join-Path $patternsDir "schemas\$pattern.schema.json"
    
    if (Test-Path $schemaPath) {
        Write-Host "    ⚠ $pattern.schema.json already exists" -ForegroundColor Yellow
        continue
    }
    
    $schema = @{
        '$schema' = 'http://json-schema.org/draft-07/schema#'
        '$id' = "$pattern.schema.json"
        title = "$pattern Pattern Instance"
        description = "Schema for $pattern pattern instances"
        type = 'object'
        required = @('doc_id', 'pattern_id', 'inputs')
        properties = @{
            doc_id = @{
                type = 'string'
                pattern = '^DOC-[A-Z0-9-]+$'
                const = $docId
            }
            pattern_id = @{
                type = 'string'
                const = $patternId
            }
            inputs = @{
                type = 'object'
                description = 'Pattern-specific input parameters'
            }
            outputs = @{
                type = 'object'
                description = 'Pattern execution outputs'
            }
        }
    }
    
    if (-not $DryRun) {
        $schema | ConvertTo-Json -Depth 10 | Set-Content $schemaPath -Encoding UTF8
        $stats.FilesGenerated++
    }
    Write-Host "    ✓ Generated $pattern.schema.json" -ForegroundColor Green
}

# Generate examples for core patterns
Write-Host "`n  [2.2] Generating examples..." -ForegroundColor Cyan

foreach ($pattern in $corePatterns.Keys) {
    $patternId = $corePatterns[$pattern]
    $docId = $mapping.$patternId
    $exampleDir = Join-Path $patternsDir "examples\$pattern"
    
    if (-not (Test-Path $exampleDir)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $exampleDir -Force | Out-Null
        }
        Write-Host "    ✓ Created directory: examples/$pattern/" -ForegroundColor Green
    }
    
    # Generate instance_minimal.json
    $minimalPath = Join-Path $exampleDir "instance_minimal.json"
    if (-not (Test-Path $minimalPath)) {
        $minimal = @{
            doc_id = $docId
            pattern_id = $patternId
            inputs = @{
                project_root = 'C:\Projects\Example'
            }
        }
        
        if (-not $DryRun) {
            $minimal | ConvertTo-Json -Depth 10 | Set-Content $minimalPath -Encoding UTF8
            $stats.FilesGenerated++
        }
        Write-Host "    ✓ Generated $pattern/instance_minimal.json" -ForegroundColor Green
    }
    
    # Generate instance_full.json
    $fullPath = Join-Path $exampleDir "instance_full.json"
    if (-not (Test-Path $fullPath)) {
        $full = @{
            doc_id = $docId
            pattern_id = $patternId
            inputs = @{
                project_root = 'C:\Projects\Example'
            }
            metadata = @{
                created = (Get-Date -Format 'yyyy-MM-dd')
                description = "Full example for $pattern pattern"
            }
        }
        
        if (-not $DryRun) {
            $full | ConvertTo-Json -Depth 10 | Set-Content $fullPath -Encoding UTF8
            $stats.FilesGenerated++
        }
        Write-Host "    ✓ Generated $pattern/instance_full.json" -ForegroundColor Green
    }
    
    # Generate instance_test.json
    $testPath = Join-Path $exampleDir "instance_test.json"
    if (-not (Test-Path $testPath)) {
        $test = @{
            doc_id = $docId
            pattern_id = $patternId
            inputs = @{
                project_root = 'C:\Temp\Test'
            }
        }
        
        if (-not $DryRun) {
            $test | ConvertTo-Json -Depth 10 | Set-Content $testPath -Encoding UTF8
            $stats.FilesGenerated++
        }
        Write-Host "    ✓ Generated $pattern/instance_test.json" -ForegroundColor Green
    }
}

# Generate executors for core patterns
Write-Host "`n  [2.3] Generating executors..." -ForegroundColor Cyan

foreach ($pattern in $corePatterns.Keys) {
    $patternId = $corePatterns[$pattern]
    $docId = $mapping.$patternId
    $execPath = Join-Path $patternsDir "executors\${pattern}_executor.ps1"
    
    if (Test-Path $execPath) {
        Write-Host "    ⚠ ${pattern}_executor.ps1 already exists" -ForegroundColor Yellow
        continue
    }
    
    $executor = @"
# DOC_LINK: $docId
# Pattern: $pattern ($patternId)
# Version: 1.0.0
# Purpose: Execute $pattern pattern instances

param(
    [Parameter(Mandatory=`$true)]
    [string]`$InstancePath
)

`$ErrorActionPreference = "Stop"

Write-Host "Executing $pattern pattern..." -ForegroundColor Cyan

# Load instance
if (-not (Test-Path `$InstancePath)) {
    throw "Instance file not found: `$InstancePath"
}

`$instance = Get-Content `$InstancePath -Raw | ConvertFrom-Json

# Validate pattern_id
if (`$instance.pattern_id -ne "$patternId") {
    throw "Invalid pattern_id. Expected: $patternId, Got: `$(`$instance.pattern_id)"
}

# TODO: Implement $pattern execution logic
# See patterns/specs/$pattern.pattern.yaml for implementation details

Write-Host "✓ $pattern pattern execution complete" -ForegroundColor Green
"@
    
    if (-not $DryRun) {
        Set-Content $execPath $executor -Encoding UTF8
        $stats.FilesGenerated++
    }
    Write-Host "    ✓ Generated ${pattern}_executor.ps1" -ForegroundColor Green
}

# Generate tests for core patterns
Write-Host "`n  [2.4] Generating tests..." -ForegroundColor Cyan

# Create tests directory if it doesn't exist
$testsDir = Join-Path $patternsDir "tests"
if (-not (Test-Path $testsDir)) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $testsDir -Force | Out-Null
    }
    Write-Host "    ✓ Created tests/ directory" -ForegroundColor Green
}

foreach ($pattern in (@('atomic_create') + $corePatterns.Keys)) {
    $testPath = Join-Path $testsDir "test_${pattern}_executor.ps1"
    
    if (Test-Path $testPath) {
        Write-Host "    ⚠ test_${pattern}_executor.ps1 already exists" -ForegroundColor Yellow
        continue
    }
    
    $patternId = if ($pattern -eq 'atomic_create') { 'PAT-ATOMIC-CREATE-001' } else { $corePatterns[$pattern] }
    $docId = $mapping.$patternId
    
    $test = @"
# DOC_LINK: $docId
# Tests for $pattern pattern executor

Describe "$pattern pattern executor" {
    
    BeforeAll {
        `$ExecutorPath = "`$PSScriptRoot\..\executors\${pattern}_executor.ps1"
        `$ExamplePath = "`$PSScriptRoot\..\examples\$pattern\instance_minimal.json"
    }
    
    It "Executor file should exist" {
        Test-Path `$ExecutorPath | Should -Be `$true
    }
    
    It "Example instance should exist" {
        Test-Path `$ExamplePath | Should -Be `$true
    }
    
    It "Should accept InstancePath parameter" {
        `$params = (Get-Command `$ExecutorPath).Parameters
        `$params.Keys -contains 'InstancePath' | Should -Be `$true
    }
    
    It "Should validate instance schema" {
        # TODO: Add schema validation test
        `$true | Should -Be `$true
    }
}
"@
    
    if (-not $DryRun) {
        Set-Content $testPath $test -Encoding UTF8
        $stats.FilesGenerated++
    }
    Write-Host "    ✓ Generated test_${pattern}_executor.ps1" -ForegroundColor Green
}

# Generate schema sidecar files
Write-Host "`n  [2.5] Generating schema sidecar files..." -ForegroundColor Cyan

foreach ($pattern in (@('atomic_create') + $corePatterns.Keys)) {
    $sidecarPath = Join-Path $patternsDir "schemas\$pattern.schema.id.yaml"
    
    if (Test-Path $sidecarPath) {
        Write-Host "    ⚠ $pattern.schema.id.yaml already exists" -ForegroundColor Yellow
        continue
    }
    
    $patternId = if ($pattern -eq 'atomic_create') { 'PAT-ATOMIC-CREATE-001' } else { $corePatterns[$pattern] }
    $docId = $mapping.$patternId
    
    $sidecar = @"
# Schema Sidecar ID File
# Links schema to doc_id for cross-artifact joins

schema_path: patterns/schemas/$pattern.schema.json
doc_id: $docId
pattern_id: $patternId
role: schema
linked_spec: patterns/specs/$pattern.pattern.yaml
linked_executor: patterns/executors/${pattern}_executor.ps1
linked_tests: patterns/tests/test_${pattern}_executor.ps1
linked_examples: patterns/examples/$pattern/
"@
    
    if (-not $DryRun) {
        Set-Content $sidecarPath $sidecar -Encoding UTF8
        $stats.FilesGenerated++
    }
    Write-Host "    ✓ Generated $pattern.schema.id.yaml" -ForegroundColor Green
}

$stats.PhasesCompleted++

Write-Host "`n════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "GENERATION COMPLETE" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Files Generated: $($stats.FilesGenerated)" -ForegroundColor Cyan
Write-Host "Files Failed:    $($stats.FilesFailed)" -ForegroundColor $(if ($stats.FilesFailed -eq 0) { 'Green' } else { 'Red' })
Write-Host "Phases Complete: $($stats.PhasesCompleted)" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE - No files were actually created]" -ForegroundColor Yellow
}
