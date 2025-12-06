# DOC_LINK: DOC-PAT-ATOMIC-CREATE-TEMPLATE-ATOMIC-CREATE-TEMPLATE-EXECUTOR-001
# Pattern: atomic_create_template (PAT-ATOMIC-CREATE-TEMPLATE-001)
# Version: 1.0.0
# Category: execution
# Purpose: Atomic file creation from template

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing atomic_create_template pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-ATOMIC-CREATE-TEMPLATE-ATOMIC-CREATE-TEMPLATE-EXECUTOR-001" `
    -ExpectedPatternId "PAT-ATOMIC-CREATE-TEMPLATE-001"

# Extract inputs
$templatePath = $instance.inputs.template_path
$outputPath = $instance.inputs.output_path
$variables = $instance.inputs.variables

Write-PatternLog "Template: $templatePath" "INFO"
Write-PatternLog "Output: $outputPath" "INFO"

# Step 1: Load template
if (-not (Test-Path $templatePath)) {
    throw "Template file not found: $templatePath"
}

$template = Get-Content $templatePath -Raw
Write-PatternLog "Template loaded" "SUCCESS"

# Step 2: Substitute variables
$content = $template
$varsUsed = @()

foreach ($varName in $variables.PSObject.Properties.Name) {
    $varValue = $variables.$varName
    $placeholder = "{$varName}"

    if ($content -match [regex]::Escape($placeholder)) {
        $content = $content -replace [regex]::Escape($placeholder), $varValue
        $varsUsed += $varName
        Write-PatternLog "  Substituted: $varName" "INFO"
    }
}

Write-PatternLog "Variables substituted: $($varsUsed.Count)" "SUCCESS"

# Step 3: Atomic write to output
$tempPath = "$outputPath.tmp"

try {
    # Write to temp file first
    $outputDir = Split-Path $outputPath -Parent
    if ($outputDir -and -not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    Set-Content -Path $tempPath -Value $content -Encoding UTF8

    # Atomic move
    if (Test-Path $outputPath) {
        Remove-Item $outputPath -Force
    }
    Move-Item $tempPath $outputPath -Force

    Write-PatternLog "File created atomically: $outputPath" "SUCCESS"

    $result = New-PatternResult -Success $true -Message "Template file created successfully" -Data @{
        file_created = $outputPath
        template_vars_used = $varsUsed
    }

} catch {
    # Cleanup temp file on error
    if (Test-Path $tempPath) {
        Remove-Item $tempPath -Force
    }
    throw
}

Write-Output $result
