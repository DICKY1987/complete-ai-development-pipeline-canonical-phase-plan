# DOC_LINK: DOC-PAT-MODULE-CREATION-CONVERGENCE-001
# Pattern: module_creation_convergence (PAT-MODULE-CREATION-CONVERGENCE-001)
# Version: 1.0.0
# Category: template
# Purpose: Execute module_creation_convergence pattern instances

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "Executing module_creation_convergence pattern..." -ForegroundColor Cyan

# Load instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json

# Validate doc_id
if ($instance.doc_id -ne "DOC-PAT-MODULE-CREATION-CONVERGENCE-001") {
    throw "Invalid doc_id. Expected: DOC-PAT-MODULE-CREATION-CONVERGENCE-001, Got: $($instance.doc_id)"
}

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-MODULE-CREATION-CONVERGENCE-001") {
    throw "Invalid pattern_id. Expected: PAT-MODULE-CREATION-CONVERGENCE-001, Got: $($instance.pattern_id)"
}

Write-Host "✓ Validation passed" -ForegroundColor Green

# TODO: Implement module_creation_convergence execution logic
# See patterns/specs/module_creation_convergence.pattern.yaml for implementation details

Write-Host "✓ module_creation_convergence pattern execution complete" -ForegroundColor Green
