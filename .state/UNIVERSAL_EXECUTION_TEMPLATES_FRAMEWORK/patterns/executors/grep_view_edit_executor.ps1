# DOC_LINK: DOC-PAT-GREP-VIEW-EDIT-002
# Pattern: grep_view_edit (PAT-GREP-VIEW-EDIT-002)
# Version: 1.0.0
# Category: sequential
# Purpose: Search, view context, edit file

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing grep_view_edit pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-GREP-VIEW-EDIT-002" `
    -ExpectedPatternId "PAT-GREP-VIEW-EDIT-002"

# Extract inputs
$pattern = $instance.inputs.pattern
$fileGlob = $instance.inputs.file_glob
$editAction = $instance.inputs.edit_action

Write-PatternLog "Searching for pattern: $pattern" "INFO"
Write-PatternLog "In files matching: $fileGlob" "INFO"

# Step 1: Search for pattern
$files = Get-ChildItem -Path $fileGlob -File -ErrorAction SilentlyContinue

if (-not $files) {
    Write-PatternLog "No files match glob pattern" "WARNING"
    
    $result = New-PatternResult -Success $false -Message "No files found" -Data @{
        files_matched = @()
        edits_applied = 0
    }
    
    Write-Output $result
    return
}

$matchedFiles = @()
$editsApplied = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    
    if ($content -match $pattern) {
        $matchedFiles += $file.FullName
        Write-PatternLog "Match found in: $($file.Name)" "INFO"
        
        # Step 2: View context (show line with match)
        $lines = Get-Content $file.FullName
        $matchingLines = $lines | Select-String -Pattern $pattern
        
        foreach ($match in $matchingLines) {
            Write-PatternLog "  Line $($match.LineNumber): $($match.Line.Trim())" "INFO"
        }
        
        # Step 3: Apply edit if specified
        if ($editAction) {
            $oldStr = $editAction.old_str
            $newStr = $editAction.new_str
            
            $newContent = $content -replace [regex]::Escape($oldStr), $newStr
            Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
            
            $editsApplied++
            Write-PatternLog "  Edit applied to: $($file.Name)" "SUCCESS"
        }
    }
}

Write-PatternLog "Search complete: $($matchedFiles.Count) files matched, $editsApplied edits applied" "SUCCESS"

$result = New-PatternResult -Success $true -Message "Grep and edit complete" -Data @{
    files_matched = $matchedFiles
    edits_applied = $editsApplied
}

Write-Output $result
