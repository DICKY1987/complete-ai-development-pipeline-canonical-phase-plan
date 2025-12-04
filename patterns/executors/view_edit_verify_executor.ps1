# DOC_LINK: DOC-PAT-VIEW-EDIT-VERIFY-003
# Pattern: view_edit_verify (PAT-VIEW-EDIT-VERIFY-003)
# Version: 1.0.0
# Category: sequential
# Purpose: View file, edit, verify change

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing view_edit_verify pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-VIEW-EDIT-VERIFY-003" `
    -ExpectedPatternId "PAT-VIEW-EDIT-VERIFY-003"

# Extract inputs
$filePath = $instance.inputs.file_path
$oldStr = $instance.inputs.edit_spec.old_str
$newStr = $instance.inputs.edit_spec.new_str
$verificationCommand = $instance.inputs.verification_command

Write-PatternLog "Target file: $filePath" "INFO"

if (-not (Test-Path $filePath)) {
    throw "File not found: $filePath"
}

# Backup original content
$originalContent = Get-Content $filePath -Raw
Write-PatternLog "Created backup of original content" "INFO"

try {
    # Step 1: View file (log first 10 lines)
    $lines = Get-Content $filePath
    Write-PatternLog "File has $($lines.Count) lines" "INFO"

    # Step 2: Apply edit
    $content = Get-Content $filePath -Raw

    if ($content -notmatch [regex]::Escape($oldStr)) {
        throw "old_str not found in file: $oldStr"
    }

    $newContent = $content -replace [regex]::Escape($oldStr), $newStr
    Set-Content -Path $filePath -Value $newContent -Encoding UTF8 -NoNewline

    Write-PatternLog "Edit applied successfully" "SUCCESS"

    # Step 3: Run verification
    Write-PatternLog "Running verification: $verificationCommand" "INFO"
    $verifyOutput = Invoke-Expression $verificationCommand 2>&1
    $verifyPassed = ($LASTEXITCODE -eq 0)

    if ($verifyPassed) {
        Write-PatternLog "Verification passed" "SUCCESS"

        $result = New-PatternResult -Success $true -Message "Edit applied and verified" -Data @{
            file_path = $filePath
            edit_applied = $true
            verification_passed = $true
        }
    } else {
        Write-PatternLog "Verification failed - rolling back" "WARNING"

        # Rollback: restore original content
        Set-Content -Path $filePath -Value $originalContent -Encoding UTF8 -NoNewline
        Write-PatternLog "File restored to original state" "INFO"

        $result = New-PatternResult -Success $false -Message "Verification failed - edit rolled back" -Data @{
            file_path = $filePath
            edit_applied = $false
            verification_passed = $false
            verification_output = ($verifyOutput -join "`n")
        }
    }

} catch {
    Write-PatternLog "Error: $_" "ERROR"

    # Rollback on error
    Set-Content -Path $filePath -Value $originalContent -Encoding UTF8 -NoNewline
    Write-PatternLog "File restored after error" "INFO"

    throw
}

Write-Output $result
