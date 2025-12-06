# DOC_LINK: DOC-PAT-BATCH-FILE-CREATION-BATCH-FILE-CREATION-EXECUTOR-001
# Pattern: batch_file_creation (PAT-BATCH-FILE-CREATION-001)
# Version: 1.0.0
# Category: parallel
# Purpose: Create multiple files in parallel

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing batch_file_creation pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-BATCH-FILE-CREATION-BATCH-FILE-CREATION-EXECUTOR-001" `
    -ExpectedPatternId "PAT-BATCH-FILE-CREATION-001"

# Extract inputs
$files = $instance.inputs.files
$parallelLimit = if ($instance.inputs.parallel_limit) { $instance.inputs.parallel_limit } else { 4 }

Write-PatternLog "Creating $($files.Count) files (parallel limit: $parallelLimit)..." "INFO"

$filesCreated = 0
$failures = @()

# Create files (simulated parallel batches)
foreach ($file in $files) {
    try {
        $filePath = $file.path
        $fileContent = $file.content

        # Create directory if needed
        $fileDir = Split-Path $filePath -Parent
        if ($fileDir -and -not (Test-Path $fileDir)) {
            New-Item -ItemType Directory -Path $fileDir -Force | Out-Null
        }

        # Create file
        Set-Content -Path $filePath -Value $fileContent -Encoding UTF8
        $filesCreated++
        Write-PatternLog "  ✓ Created: $filePath" "SUCCESS"

    } catch {
        $failures += @{
            path = $file.path
            error = $_.ToString()
        }
        Write-PatternLog "  ✗ Failed: $($file.path) - $_" "ERROR"
    }
}

$success = ($failures.Count -eq 0)
Write-PatternLog "Batch creation complete: $filesCreated/$($files.Count) created" $(if ($success) { "SUCCESS" } else { "WARNING" })

$result = New-PatternResult -Success $success -Message "Batch file creation $(if ($success) { 'completed' } else { 'completed with failures' })" -Data @{
    files_created = $filesCreated
    failures = $failures
}

Write-Output $result
