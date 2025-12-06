# DOC_LINK: DOC-PAT-MODULE-CREATION-CONVERGENCE-MODULE-CREATION-CONVERGENCE-EXECUTOR-001
# Pattern: module_creation_convergence (PAT-MODULE-CREATION-CONVERGENCE-001)
# Version: 1.0.0
# Category: template
# Purpose: Create module with convergent structure

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing module_creation_convergence pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-MODULE-CREATION-CONVERGENCE-MODULE-CREATION-CONVERGENCE-EXECUTOR-001" `
    -ExpectedPatternId "PAT-MODULE-CREATION-CONVERGENCE-001"

# Extract inputs
$moduleName = $instance.inputs.module_name
$moduleType = $instance.inputs.module_type
$dependencies = if ($instance.inputs.dependencies) { $instance.inputs.dependencies } else { @() }

Write-PatternLog "Creating module: $moduleName (type: $moduleType)" "INFO"

$filesCreated = @()

try {
    # Step 1: Create module directory
    $modulePath = Join-Path "." $moduleName
    if (-not (Test-Path $modulePath)) {
        New-Item -ItemType Directory -Path $modulePath -Force | Out-Null
        Write-PatternLog "Created module directory: $modulePath" "SUCCESS"
    }

    # Step 2: Create __init__.py
    $initPath = Join-Path $modulePath "__init__.py"
    $initContent = @"
"""
$moduleName module
Type: $moduleType
"""

__version__ = "0.1.0"
__all__ = []
"@
    Set-Content $initPath $initContent -Encoding UTF8
    $filesCreated += $initPath
    Write-PatternLog "Created __init__.py" "SUCCESS"

    # Step 3: Create base files based on module type
    switch ($moduleType) {
        "package" {
            # Create main.py
            $mainPath = Join-Path $modulePath "main.py"
            $mainContent = @"
"""
Main module for $moduleName
"""

def main():
    pass

if __name__ == "__main__":
    main()
"@
            Set-Content $mainPath $mainContent -Encoding UTF8
            $filesCreated += $mainPath
        }

        "library" {
            # Create core.py
            $corePath = Join-Path $modulePath "core.py"
            $coreContent = @"
"""
Core functionality for $moduleName
"""

class Core:
    pass
"@
            Set-Content $corePath $coreContent -Encoding UTF8
            $filesCreated += $corePath
        }

        default {
            Write-PatternLog "Unknown module type: $moduleType" "WARNING"
        }
    }

    # Step 4: Create requirements.txt if dependencies specified
    if ($dependencies.Count -gt 0) {
        $reqPath = Join-Path $modulePath "requirements.txt"
        $reqContent = $dependencies -join "`n"
        Set-Content $reqPath $reqContent -Encoding UTF8
        $filesCreated += $reqPath
        Write-PatternLog "Created requirements.txt with $($dependencies.Count) dependencies" "SUCCESS"
    }

    Write-PatternLog "Module creation complete: $($filesCreated.Count) files created" "SUCCESS"

    $result = New-PatternResult -Success $true -Message "Module created successfully" -Data @{
        module_path = $modulePath
        files_created = $filesCreated
    }

} catch {
    Write-PatternLog "Error creating module: $_" "ERROR"
    throw
}

Write-Output $result
