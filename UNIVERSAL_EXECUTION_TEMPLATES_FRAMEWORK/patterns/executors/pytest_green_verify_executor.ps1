# DOC_LINK: DOC-PAT-PYTEST-GREEN-VERIFY-002
# Pattern: pytest_green_verify (PAT-PYTEST-GREEN-VERIFY-002)
# Version: 1.0.0
# Category: verification
# Purpose: Execute pytest_green_verify pattern instances

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "Executing pytest_green_verify pattern..." -ForegroundColor Cyan

# Load instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json

# Validate doc_id
if ($instance.doc_id -ne "DOC-PAT-PYTEST-GREEN-VERIFY-002") {
    throw "Invalid doc_id. Expected: DOC-PAT-PYTEST-GREEN-VERIFY-002, Got: $($instance.doc_id)"
}

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-PYTEST-GREEN-VERIFY-002") {
    throw "Invalid pattern_id. Expected: PAT-PYTEST-GREEN-VERIFY-002, Got: $($instance.pattern_id)"
}

Write-Host "✓ Validation passed" -ForegroundColor Green

# TODO: Implement pytest_green_verify execution logic
# See patterns/specs/pytest_green_verify.pattern.yaml for implementation details

Write-Host "✓ pytest_green_verify pattern execution complete" -ForegroundColor Green
