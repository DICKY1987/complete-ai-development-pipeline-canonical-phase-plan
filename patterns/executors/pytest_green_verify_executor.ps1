# DOC_LINK: DOC-PAT-PYTEST-GREEN-VERIFY-002
# Pattern: pytest_green_verify (PAT-PYTEST-GREEN-VERIFY-002)
# Version: 1.0.0
# Category: verification
# Purpose: Verify pytest tests are green

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing pytest_green_verify pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-PYTEST-GREEN-VERIFY-002" `
    -ExpectedPatternId "PAT-PYTEST-GREEN-VERIFY-002"

# Extract inputs
$testPath = $instance.inputs.test_path
$pytestArgs = if ($instance.inputs.pytest_args) { $instance.inputs.pytest_args -join " " } else { "" }

Write-PatternLog "Running pytest on: $testPath" "INFO"

try {
    # Build pytest command
    $command = "pytest $testPath $pytestArgs --tb=short -q"

    Write-PatternLog "Command: $command" "INFO"

    # Execute pytest
    $output = Invoke-Expression $command 2>&1
    $exitCode = $LASTEXITCODE

    # Parse pytest output
    $allGreen = ($exitCode -eq 0)

    # Try to extract test counts from output
    $testsPassed = 0
    $testsFailed = 0

    if ($output -match "(\d+) passed") {
        $testsPassed = [int]$matches[1]
    }

    if ($output -match "(\d+) failed") {
        $testsFailed = [int]$matches[1]
    }

    if ($allGreen) {
        Write-PatternLog "All tests green! ($testsPassed passed)" "SUCCESS"
    } else {
        Write-PatternLog "Tests failed! ($testsPassed passed, $testsFailed failed)" "ERROR"
    }

    # Return result
    $result = New-PatternResult -Success $allGreen -Message "Pytest verification $(if ($allGreen) { 'passed' } else { 'failed' })" -Data @{
        tests_passed = $testsPassed
        tests_failed = $testsFailed
        all_green = $allGreen
        output = $output -join "`n"
    }

} catch {
    Write-PatternLog "Error running pytest: $_" "ERROR"

    $result = New-PatternResult -Success $false -Message "Pytest execution error" -Data @{
        error = $_.ToString()
    }
}

Write-Output $result
