# DOC_LINK: DOC-PAT-MODULE-CREATION-001-EXECUTOR-222
# Pattern Executor: module_creation
# Pattern ID: PAT-MODULE-CREATION-001
# Auto-generated: 2025-11-27T10:14:13.068675

param(
    [Parameter(Mandatory=$true)]
    [string]$InstanceFile
)

$ErrorActionPreference = "Stop"

# Read instance
$instance = Get-Content $InstanceFile -Raw | ConvertFrom-Json

Write-Host "[EXEC] Running module_creation..." -ForegroundColor Cyan

# Load shared utilities
$utilsPath = Join-Path $PSScriptRoot "..\..\scripts\pattern_utilities.ps1"
if (Test-Path $utilsPath) { . $utilsPath }

# Parse inputs
$inputs = $instance.pattern.inputs
$moduleName = $inputs.module_name
$language = if ($inputs.language) { $inputs.language } else { "python" }
$targetPath = if ($inputs.project_root) { $inputs.project_root } else { "." }

# Validate required inputs
if (-not $moduleName) {
    throw "Missing required input: module_name"
}

# Create module directory
$modulePath = Join-Path $targetPath $moduleName
if (Test-Path $modulePath) {
    Write-Warning "Module directory already exists: $modulePath"
} else {
    New-Item -ItemType Directory -Path $modulePath -Force | Out-Null
    Write-Host "Created module directory: $modulePath" -ForegroundColor Green
}

# Create basic Python module files
if ($language -eq "python") {
    $initFile = Join-Path $modulePath "__init__.py"
    if (-not (Test-Path $initFile)) {
        @"
"""$moduleName module."""
__version__ = "0.1.0"
"@ | Set-Content -Path $initFile -Encoding UTF8
        Write-Host "Created: $initFile" -ForegroundColor Green
    }

    $mainFile = Join-Path $modulePath "$moduleName.py"
    if (-not (Test-Path $mainFile)) {
        @"
"""Main module implementation."""

def main():
    """Entry point."""
    pass

if __name__ == "__main__":
    main()
"@ | Set-Content -Path $mainFile -Encoding UTF8
        Write-Host "Created: $mainFile" -ForegroundColor Green
    }
}

Write-Host "[OK] Module creation complete" -ForegroundColor Green
