#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-VALIDATE-TASK-DEFS-095
<#
.SYNOPSIS
    Validate Task Definition Requirements (TASK-DEF-*)

.DESCRIPTION
    Validates that task definition files meet all requirements defined
    in the orchestration specification.

.PARAMETER TasksDir
    Directory containing task definitions (default: tasks)

.PARAMETER SchemaVersion
    Expected schema version (default: 2.0.0)

.EXAMPLE
    ./validate_task_defs.ps1 -TasksDir tasks -SchemaVersion "2.0.0"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$TasksDir = "tasks",

    [Parameter()]
    [string]$SchemaVersion = "2.0.0",

    [Parameter()]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$script:FailureCount = 0
$script:PassCount = 0
$script:TasksValidated = 0

function Write-Result {
    param(
        [string]$RequirementId,
        [string]$Status,
        [string]$Message
    )

    $statusSymbol = if ($Status -eq "PASS") { "✓" } else { "✗" }
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }

    Write-Host "[$statusSymbol] $RequirementId : " -NoNewline
    Write-Host $Message -ForegroundColor $color

    if ($Status -eq "PASS") {
        $script:PassCount++
    } else {
        $script:FailureCount++
    }
}

function Test-TaskDefinition {
    param([string]$TaskPath)

    $errors = @()

    try {
        $taskJson = Get-Content $TaskPath -Raw | ConvertFrom-Json

        # Required top-level fields
        $requiredFields = @(
            "task_id",
            "workstream_id",
            "name",
            "description",
            "type",
            "status",
            "dependencies",
            "worker_requirements",
            "execution",
            "state"
        )

        foreach ($field in $requiredFields) {
            if (-not $taskJson.PSObject.Properties.Name.Contains($field)) {
                $errors += "Missing required field: $field"
            }
        }

        # Validate execution block
        if ($taskJson.execution) {
            $execFields = @("command", "timeout_seconds", "max_retries")
            foreach ($field in $execFields) {
                if (-not $taskJson.execution.PSObject.Properties.Name.Contains($field)) {
                    $errors += "Missing execution.$field"
                }
            }
        }

        # Validate state block
        if ($taskJson.state) {
            $stateFields = @("created_at", "retry_count")
            foreach ($field in $stateFields) {
                if (-not $taskJson.state.PSObject.Properties.Name.Contains($field)) {
                    $errors += "Missing state.$field"
                }
            }
        }

        # Check schema version if v2.0.0+
        if ($SchemaVersion -eq "2.0.0") {
            # v2.0.0 fields (optional but recommended)
            if (-not $taskJson.PSObject.Properties.Name.Contains("context_requirements")) {
                if ($taskJson.type -eq "aider") {
                    $errors += "Warning: context_requirements recommended for Aider tasks in v2.0.0"
                }
            }

            if (-not $taskJson.PSObject.Properties.Name.Contains("validation_rules")) {
                $errors += "Warning: validation_rules recommended in v2.0.0"
            }
        }

        return $errors

    } catch {
        return @("Invalid JSON: $($_.Exception.Message)")
    }
}

Write-Host "`n=== Validating Task Definition Requirements ===" -ForegroundColor Cyan
Write-Host "Tasks Directory: $TasksDir" -ForegroundColor Gray
Write-Host "Expected Schema Version: $SchemaVersion`n" -ForegroundColor Gray

# TASK-DEF-001: Task File Requirements
Write-Host "`nTASK-DEF-001: Task File Requirements" -ForegroundColor Yellow

if (-not (Test-Path $TasksDir)) {
    Write-Result "TASK-DEF-001" "FAIL" "Tasks directory not found: $TasksDir"
} else {
    $taskFiles = Get-ChildItem -Path $TasksDir -Recurse -Filter "*.json"
    $taskCount = $taskFiles.Count

    if ($taskCount -eq 0) {
        Write-Host "  No task files found - this may be valid for new installation" -ForegroundColor Yellow
        Write-Result "TASK-DEF-001" "PASS" "Task directory structure exists (0 tasks found)"
    } else {
        $validStructure = $true

        foreach ($taskFile in $taskFiles) {
            # Verify filename matches task_id pattern
            if ($taskFile.Name -notmatch '^task-.*\.json$') {
                Write-Host "  Invalid filename: $($taskFile.Name)" -ForegroundColor Red
                $validStructure = $false
            }

            # Verify in workstream subdirectory
            if ($taskFile.DirectoryName -eq $TasksDir) {
                Write-Host "  Task not in workstream subdirectory: $($taskFile.Name)" -ForegroundColor Red
                $validStructure = $false
            }
        }

        if ($VerboseOutput) {
            Write-Host "  Found $taskCount task files" -ForegroundColor Gray
        }

        Write-Result "TASK-DEF-001" $(if ($validStructure) { "PASS" } else { "FAIL" }) `
            "Task files follow naming convention and directory structure ($taskCount tasks)"
    }
}

# TASK-DEF-002: Task Schema
Write-Host "`nTASK-DEF-002: Task Schema" -ForegroundColor Yellow

if (Test-Path $TasksDir) {
    $taskFiles = Get-ChildItem -Path $TasksDir -Recurse -Filter "*.json"
    $allTasksValid = $true
    $tasksWithErrors = 0

    foreach ($taskFile in $taskFiles) {
        $script:TasksValidated++
        $errors = Test-TaskDefinition $taskFile.FullName

        if ($errors.Count -gt 0) {
            $allTasksValid = $false
            $tasksWithErrors++

            Write-Host "  Errors in $($taskFile.Name):" -ForegroundColor Red
            foreach ($error in $errors) {
                Write-Host "    - $error" -ForegroundColor Red
            }
        } elseif ($VerboseOutput) {
            Write-Host "  ✓ $($taskFile.Name)" -ForegroundColor Gray
        }
    }

    if ($taskFiles.Count -gt 0) {
        $validCount = $taskFiles.Count - $tasksWithErrors
        Write-Result "TASK-DEF-002" $(if ($allTasksValid) { "PASS" } else { "FAIL" }) `
            "Task schema validation: $validCount/$($taskFiles.Count) tasks valid"
    } else {
        Write-Result "TASK-DEF-002" "PASS" `
            "No tasks to validate (new installation)"
    }
} else {
    Write-Result "TASK-DEF-002" "FAIL" `
        "Cannot validate: tasks directory not found"
}

# Additional validation: Check for orphaned tasks
Write-Host "`nAdditional Checks" -ForegroundColor Yellow

if (Test-Path $TasksDir) {
    $taskFiles = Get-ChildItem -Path $TasksDir -Recurse -Filter "*.json"
    $orphanedTasks = @()

    foreach ($taskFile in $taskFiles) {
        try {
            $taskJson = Get-Content $taskFile.FullName -Raw | ConvertFrom-Json

            # Check if task is in correct workstream directory
            $expectedDir = Join-Path $TasksDir $taskJson.workstream_id
            if ($taskFile.DirectoryName -ne $expectedDir) {
                $orphanedTasks += $taskFile.Name
                Write-Host "  Task in wrong directory: $($taskFile.Name)" -ForegroundColor Yellow
                Write-Host "    Expected: $expectedDir" -ForegroundColor Gray
                Write-Host "    Actual: $($taskFile.DirectoryName)" -ForegroundColor Gray
            }

        } catch {
            # Already reported in schema validation
        }
    }

    if ($orphanedTasks.Count -eq 0) {
        Write-Host "  ✓ All tasks in correct workstream directories" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Found $($orphanedTasks.Count) tasks in wrong directories" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "PASSED: $script:PassCount" -ForegroundColor Green
Write-Host "FAILED: $script:FailureCount" -ForegroundColor $(if ($script:FailureCount -gt 0) { "Red" } else { "Green" })
Write-Host "Tasks Validated: $script:TasksValidated" -ForegroundColor Gray

if ($script:FailureCount -gt 0) {
    Write-Host "`nValidation FAILED. See errors above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`nValidation PASSED. All task definition requirements met." -ForegroundColor Green
    exit 0
}
