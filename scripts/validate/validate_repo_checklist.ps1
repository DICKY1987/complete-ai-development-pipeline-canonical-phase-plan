#Requires -Version 5.1
<#
.SYNOPSIS
    Generic repository checklist validator that reads machine-readable JSON specs.

.DESCRIPTION
    This validator reads repo_checklist.json and optional .folder_checklist.json files
    to execute validation checks by requirement_id. It dispatches checks based on rule type
    and emits structured results.

.PARAMETER ChecklistPath
    Path to the main repo checklist JSON file. Default: .ai-orch/checklists/repo_checklist.json

.PARAMETER JsonOutput
    Emit results in JSON format instead of human-readable text.

.PARAMETER RequirementFilter
    Filter to specific requirement IDs (comma-separated). Default: all requirements.

.PARAMETER Verbose
    Show detailed output for each check.

.EXAMPLE
    .\validate_repo_checklist.ps1
    Run all validation checks with human-readable output.

.EXAMPLE
    .\validate_repo_checklist.ps1 -JsonOutput
    Run all checks and emit JSON results.

.EXAMPLE
    .\validate_repo_checklist.ps1 -RequirementFilter "ACS-ARTIFACTS-001,STATE-OBS-001"
    Run only specific requirement checks.
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ChecklistPath = ".ai-orch\checklists\repo_checklist.json",
    
    [Parameter()]
    [switch]$JsonOutput,
    
    [Parameter()]
    [string]$RequirementFilter,
    
    [Parameter()]
    [switch]$VerboseOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Test-JsonFile {
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        
        [Parameter()]
        [string[]]$RequiredFields
    )
    
    if (-not (Test-Path $Path)) {
        return @{
            Valid = $false
            Message = "File not found: $Path"
        }
    }
    
    try {
        $content = Get-Content -Path $Path -Raw | ConvertFrom-Json
        
        if ($RequiredFields) {
            $missing = @()
            foreach ($field in $RequiredFields) {
                if (-not $content.PSObject.Properties.Name.Contains($field)) {
                    $missing += $field
                }
            }
            
            if ($missing.Count -gt 0) {
                return @{
                    Valid = $false
                    Message = "Missing required fields: $($missing -join ', ')"
                    Content = $content
                }
            }
        }
        
        return @{
            Valid = $true
            Message = "Valid JSON with all required fields"
            Content = $content
        }
    }
    catch {
        return @{
            Valid = $false
            Message = "Invalid JSON: $($_.Exception.Message)"
        }
    }
}

function Test-JsonLinesFile {
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        
        [Parameter()]
        [string[]]$RequiredFieldsPerLine
    )
    
    if (-not (Test-Path $Path)) {
        return @{
            Valid = $false
            Message = "File not found: $Path"
        }
    }
    
    try {
        $lines = Get-Content -Path $Path
        $lineNum = 0
        $errors = @()
        
        foreach ($line in $lines) {
            $lineNum++
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            
            try {
                $obj = $line | ConvertFrom-Json
                
                if ($RequiredFieldsPerLine) {
                    $missing = @()
                    foreach ($field in $RequiredFieldsPerLine) {
                        if (-not $obj.PSObject.Properties.Name.Contains($field)) {
                            $missing += $field
                        }
                    }
                    
                    if ($missing.Count -gt 0) {
                        $errors += "Line $lineNum missing fields: $($missing -join ', ')"
                    }
                }
            }
            catch {
                $errors += "Line $lineNum invalid JSON: $($_.Exception.Message)"
            }
        }
        
        if ($errors.Count -gt 0) {
            return @{
                Valid = $false
                Message = "JSONL validation errors: $($errors -join '; ')"
            }
        }
        
        return @{
            Valid = $true
            Message = "Valid JSONL with $lineNum lines"
        }
    }
    catch {
        return @{
            Valid = $false
            Message = "Error reading JSONL: $($_.Exception.Message)"
        }
    }
}

function Invoke-Check {
    param(
        [Parameter(Mandatory)]
        [PSCustomObject]$Rule,
        
        [Parameter(Mandatory)]
        [string]$RepoRoot
    )
    
    $params = $Rule.params
    
    switch ($Rule.type) {
        "required_files" {
            $missing = @()
            foreach ($fileSpec in $params.files) {
                $fullPath = Join-Path $RepoRoot $fileSpec.path
                if (-not (Test-Path $fullPath)) {
                    $missing += "$($fileSpec.path) - $($fileSpec.description)"
                }
            }
            
            if ($missing.Count -gt 0) {
                return @{
                    Status = "FAIL"
                    Message = "Missing required files: $($missing -join '; ')"
                }
            }
            return @{
                Status = "PASS"
                Message = "All $($params.files.Count) required files present"
            }
        }
        
        "directory_layout" {
            $root = Join-Path $RepoRoot $params.root
            $issues = @()
            
            if (-not (Test-Path $root)) {
                return @{
                    Status = "FAIL"
                    Message = "Root directory not found: $($params.root)"
                }
            }
            
            foreach ($dir in $params.required_directories) {
                $fullPath = Join-Path $root $dir
                if (-not (Test-Path $fullPath)) {
                    $issues += "Missing directory: $dir"
                }
            }
            
            foreach ($file in $params.required_files) {
                $fullPath = Join-Path $root $file
                if (-not (Test-Path $fullPath)) {
                    $issues += "Missing file: $file"
                }
            }
            
            if ($issues.Count -gt 0) {
                return @{
                    Status = "FAIL"
                    Message = "$($params.root) layout issues: $($issues -join '; ')"
                }
            }
            
            return @{
                Status = "PASS"
                Message = "$($params.root) layout correct"
            }
        }
        
        "json_file" {
            $fullPath = Join-Path $RepoRoot $params.path
            $result = Test-JsonFile -Path $fullPath -RequiredFields $params.required_fields
            
            return @{
                Status = if ($result.Valid) { "PASS" } else { "FAIL" }
                Message = "$($params.path): $($result.Message)"
            }
        }
        
        "json_lines_file" {
            $fullPath = Join-Path $RepoRoot $params.path
            $result = Test-JsonLinesFile -Path $fullPath -RequiredFieldsPerLine $params.required_fields_per_line
            
            return @{
                Status = if ($result.Valid) { "PASS" } else { "FAIL" }
                Message = "$($params.path): $($result.Message)"
            }
        }
        
        "json_index_files" {
            $indicesDir = Join-Path $RepoRoot $params.indices_dir
            $missing = @()
            
            if (-not (Test-Path $indicesDir)) {
                return @{
                    Status = "FAIL"
                    Message = "Indices directory not found: $($params.indices_dir)"
                }
            }
            
            foreach ($indexFile in $params.required_indices) {
                $fullPath = Join-Path $indicesDir $indexFile
                if (-not (Test-Path $fullPath)) {
                    $missing += $indexFile
                }
                else {
                    $result = Test-JsonFile -Path $fullPath -RequiredFields $params.index_schema_fields
                    if (-not $result.Valid) {
                        $missing += "$indexFile (invalid: $($result.Message))"
                    }
                }
            }
            
            if ($missing.Count -gt 0) {
                return @{
                    Status = "FAIL"
                    Message = "Missing or invalid indices: $($missing -join '; ')"
                }
            }
            
            return @{
                Status = "PASS"
                Message = "All $($params.required_indices.Count) index files valid"
            }
        }
        
        "file_exists" {
            $fullPath = Join-Path $RepoRoot $params.path
            
            if (-not (Test-Path $fullPath)) {
                if ($params.allow_in_parent) {
                    $parentPath = Join-Path (Split-Path $RepoRoot) $params.path
                    if (Test-Path $parentPath) {
                        return @{
                            Status = "PASS"
                            Message = "File found in parent: $($params.path)"
                        }
                    }
                }
                
                return @{
                    Status = "FAIL"
                    Message = "File not found: $($params.path)"
                }
            }
            
            return @{
                Status = "PASS"
                Message = "File exists: $($params.path)"
            }
        }
        
        "workstream_validation" {
            $wsDir = Join-Path $RepoRoot $params.workstreams_dir
            
            if (-not (Test-Path $wsDir)) {
                return @{
                    Status = "FAIL"
                    Message = "Workstreams directory not found: $($params.workstreams_dir)"
                }
            }
            
            $scriptPath = Join-Path $RepoRoot "scripts\validate_workstreams.py"
            if (-not (Test-Path $scriptPath)) {
                return @{
                    Status = "SKIP"
                    Message = "Validation script not found: $scriptPath"
                }
            }
            
            try {
                $output = & python $scriptPath 2>&1
                if ($LASTEXITCODE -eq 0) {
                    return @{
                        Status = "PASS"
                        Message = "Workstream validation passed"
                    }
                }
                else {
                    return @{
                        Status = "FAIL"
                        Message = "Workstream validation failed: $output"
                    }
                }
            }
            catch {
                return @{
                    Status = "FAIL"
                    Message = "Error running validation: $($_.Exception.Message)"
                }
            }
        }
        
        "test_suite" {
            try {
                $env:PYTHONPATH = $RepoRoot
                $output = Invoke-Expression $params.command 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    return @{
                        Status = "PASS"
                        Message = "Test suite passed"
                    }
                }
                else {
                    return @{
                        Status = "FAIL"
                        Message = "Test suite failed (exit code: $LASTEXITCODE)"
                    }
                }
            }
            catch {
                return @{
                    Status = "FAIL"
                    Message = "Error running tests: $($_.Exception.Message)"
                }
            }
        }
        
        default {
            return @{
                Status = "SKIP"
                Message = "Unsupported check type: $($Rule.type)"
            }
        }
    }
}

# ============================================================================
# MAIN
# ============================================================================

try {
    $repoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
    $checklistFullPath = Join-Path $repoRoot $ChecklistPath
    
    if (-not (Test-Path $checklistFullPath)) {
        Write-Error "Checklist file not found: $checklistFullPath"
        exit 1
    }
    
    $checklist = Get-Content -Path $checklistFullPath -Raw | ConvertFrom-Json
    
    if (-not $JsonOutput) {
        Write-Host ""
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host "  Repository Checklist Validator" -ForegroundColor Cyan
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host "Checklist ID: $($checklist.checklist_id)" -ForegroundColor White
        Write-Host "Description:  $($checklist.description)" -ForegroundColor White
        Write-Host "Repository:   $repoRoot" -ForegroundColor White
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host ""
    }
    
    $requirements = $checklist.rules
    if ($RequirementFilter) {
        $filterIds = $RequirementFilter -split ','
        $requirements = $requirements | Where-Object { $filterIds -contains $_.requirement_id }
    }
    
    $results = @()
    $passed = 0
    $failed = 0
    $skipped = 0
    
    foreach ($rule in $requirements) {
        if (-not $JsonOutput -and $VerboseOutput) {
            Write-Host "[CHECK] $($rule.requirement_id): $($rule.description)" -ForegroundColor Yellow
        }
        
        $result = Invoke-Check -Rule $rule -RepoRoot $repoRoot
        
        $resultObj = [PSCustomObject]@{
            requirement_id = $rule.requirement_id
            status = $result.Status
            message = $result.Message
            priority = $rule.priority
            type = $rule.type
        }
        
        $results += $resultObj
        
        switch ($result.Status) {
            "PASS" {
                $passed++
                if (-not $JsonOutput) {
                    Write-Host "  ✓ " -ForegroundColor Green -NoNewline
                    Write-Host "[$($rule.requirement_id)] " -ForegroundColor Cyan -NoNewline
                    Write-Host $result.Message -ForegroundColor Gray
                }
            }
            "FAIL" {
                $failed++
                if (-not $JsonOutput) {
                    Write-Host "  ✗ " -ForegroundColor Red -NoNewline
                    Write-Host "[$($rule.requirement_id)] " -ForegroundColor Cyan -NoNewline
                    Write-Host $result.Message -ForegroundColor Red
                }
            }
            "SKIP" {
                $skipped++
                if (-not $JsonOutput) {
                    Write-Host "  ⚠ " -ForegroundColor Yellow -NoNewline
                    Write-Host "[$($rule.requirement_id)] " -ForegroundColor Cyan -NoNewline
                    Write-Host $result.Message -ForegroundColor Yellow
                }
            }
        }
    }
    
    if ($JsonOutput) {
        $output = @{
            checklist_id = $checklist.checklist_id
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            repository = $repoRoot
            summary = @{
                total = $results.Count
                passed = $passed
                failed = $failed
                skipped = $skipped
            }
            results = $results
        }
        
        $output | ConvertTo-Json -Depth 10
    }
    else {
        Write-Host ""
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host "  Summary" -ForegroundColor Cyan
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host "Total:   $($results.Count)" -ForegroundColor White
        Write-Host "Passed:  $passed" -ForegroundColor Green
        Write-Host "Failed:  $failed" -ForegroundColor Red
        Write-Host "Skipped: $skipped" -ForegroundColor Yellow
        Write-Host "=" * 80 -ForegroundColor Cyan
        Write-Host ""
    }
    
    if ($failed -gt 0) { exit 1 } else { exit 0 }
}
catch {
    if ($JsonOutput) {
        @{ error = $_.Exception.Message; stack_trace = $_.ScriptStackTrace } | ConvertTo-Json
    }
    else {
        Write-Host ""
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    }
    exit 1
}
