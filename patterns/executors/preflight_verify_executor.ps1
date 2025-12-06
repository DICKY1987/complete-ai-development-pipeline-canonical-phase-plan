# DOC_LINK: DOC-PAT-PREFLIGHT-VERIFY-PREFLIGHT-VERIFY-EXECUTOR-001
# Pattern: preflight_verify (PAT-PREFLIGHT-VERIFY-001)
# Version: 1.0.0
# Category: verification
# Purpose: Run preflight checks before operation

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing preflight_verify pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-PREFLIGHT-VERIFY-PREFLIGHT-VERIFY-EXECUTOR-001" `
    -ExpectedPatternId "PAT-PREFLIGHT-VERIFY-001"

# Extract inputs
$checks = $instance.inputs.checks
$failFast = if ($instance.inputs.fail_fast) { $instance.inputs.fail_fast } else { $false }

Write-PatternLog "Running $($checks.Count) preflight checks..." "INFO"

$results = @()
$checksPassed = 0
$checksFailed = 0

foreach ($check in $checks) {
    Write-PatternLog "Check: $($check.name)" "INFO"

    try {
        # Execute check command
        $checkResult = Invoke-Expression $check.command
        $passed = $LASTEXITCODE -eq 0

        if ($passed) {
            $checksPassed++
            Write-PatternLog "  ✓ Passed" "SUCCESS"
        } else {
            $checksFailed++
            Write-PatternLog "  ✗ Failed" "ERROR"

            if ($failFast) {
                Write-PatternLog "Fail-fast enabled, aborting remaining checks" "WARNING"
                break
            }
        }

        $results += @{
            name = $check.name
            passed = $passed
            output = $checkResult
        }

    } catch {
        $checksFailed++
        Write-PatternLog "  ✗ Error: $_" "ERROR"

        $results += @{
            name = $check.name
            passed = $false
            error = $_.ToString()
        }

        if ($failFast) {
            break
        }
    }
}

$canProceed = ($checksFailed -eq 0)

Write-PatternLog "Preflight checks complete: $checksPassed passed, $checksFailed failed" $(if ($canProceed) { "SUCCESS" } else { "ERROR" })

# Return result
$result = New-PatternResult -Success $canProceed -Message "Preflight checks $(if ($canProceed) { 'passed' } else { 'failed' })" -Data @{
    checks_passed = $checksPassed
    checks_failed = $checksFailed
    can_proceed = $canProceed
    results = $results
}

Write-Output $result
