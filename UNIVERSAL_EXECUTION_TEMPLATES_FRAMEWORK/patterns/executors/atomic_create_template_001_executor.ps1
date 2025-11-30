# DOC_LINK: DOC-PAT-ATOMIC-CREATE-TEMPLATE-001-EXECUTOR-208
# Pattern Executor: atomic_create_template
# Pattern ID: PAT-ATOMIC-CREATE-TEMPLATE-001
# Auto-generated: 2025-11-27T10:14:12.334703

param(
    [Parameter(Mandatory=$true)]
    [string]$InstanceFile
)

$ErrorActionPreference = "Stop"

# Read instance
$instance = Get-Content $InstanceFile -Raw | ConvertFrom-Json

Write-Host "[EXEC] Running atomic_create_template..." -ForegroundColor Cyan

# TODO: Implement execution logic based on spec
# Inputs: instance_path

Write-Host "[OK] Execution complete" -ForegroundColor Green
