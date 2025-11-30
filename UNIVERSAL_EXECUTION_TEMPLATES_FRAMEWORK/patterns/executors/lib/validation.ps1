#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-VALIDATION-1185
# DOC_LINK: DOC-PAT-VALIDATION-977
# DOC_LINK: DOC-PAT-VALIDATION-241
<#
.SYNOPSIS
    Shared validation library for pattern executors

.DESCRIPTION
    Provides reusable validation functions for:
    - Pattern instance validation
    - Project structure validation
    - File syntax validation
    - Dependency validation

.NOTES
    Module: validation.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-VALIDATION-001
#>

#region Pattern Instance Validation

function Validate-PatternInstance {
    <#
    .SYNOPSIS
        Validates pattern instance JSON structure and required fields
    
    .PARAMETER InstancePath
        Path to pattern instance JSON file
    
    .PARAMETER RequiredFields
        Array of required field names
    
    .PARAMETER PatternId
        Expected pattern_id value (optional)
    
    .OUTPUTS
        Hashtable with validation results: @{ valid=$true; instance=$obj; errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$InstancePath,
        
        [Parameter(Mandatory=$false)]
        [string[]]$RequiredFields = @("pattern_id", "project_root"),
        
        [Parameter(Mandatory=$false)]
        [string]$PatternId
    )
    
    $validation = @{
        valid = $true
        instance = $null
        errors = @()
    }
    
    # Check file exists
    if (-not (Test-Path $InstancePath)) {
        $validation.valid = $false
        $validation.errors += "Instance file not found: $InstancePath"
        return $validation
    }
    
    # Load and parse JSON
    try {
        $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
        $validation.instance = $instance
    }
    catch {
        $validation.valid = $false
        $validation.errors += "Failed to parse JSON: $_"
        return $validation
    }
    
    # Check required fields
    foreach ($field in $RequiredFields) {
        if (-not ($instance.PSObject.Properties.Name -contains $field)) {
            $validation.valid = $false
            $validation.errors += "Missing required field: $field"
        }
    }
    
    # Validate pattern_id if specified
    if ($PatternId -and $instance.pattern_id -ne $PatternId) {
        $validation.valid = $false
        $validation.errors += "Invalid pattern_id: Expected $PatternId, got $($instance.pattern_id)"
    }
    
    return $validation
}

#endregion

#region Project Structure Validation

function Validate-ProjectStructure {
    <#
    .SYNOPSIS
        Validates project directory structure and required paths
    
    .PARAMETER ProjectRoot
        Root directory of the project
    
    .PARAMETER RequiredPaths
        Array of required relative paths (directories or files)
    
    .PARAMETER CreateMissing
        If true, creates missing directories
    
    .OUTPUTS
        Hashtable with validation results: @{ valid=$true; missing=@(); created=@(); errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot,
        
        [Parameter(Mandatory=$false)]
        [string[]]$RequiredPaths = @(),
        
        [Parameter(Mandatory=$false)]
        [switch]$CreateMissing
    )
    
    $validation = @{
        valid = $true
        missing = @()
        created = @()
        errors = @()
    }
    
    # Check project root exists
    if (-not (Test-Path $ProjectRoot)) {
        $validation.valid = $false
        $validation.errors += "Project root not found: $ProjectRoot"
        return $validation
    }
    
    # Check required paths
    foreach ($relPath in $RequiredPaths) {
        $fullPath = Join-Path $ProjectRoot $relPath
        
        if (-not (Test-Path $fullPath)) {
            $validation.missing += $relPath
            
            if ($CreateMissing) {
                try {
                    # Determine if path is directory or file
                    if ($relPath -match '\.[a-z0-9]+$') {
                        # Has extension, likely a file - create parent dir
                        $parentDir = Split-Path $fullPath -Parent
                        if ($parentDir -and (-not (Test-Path $parentDir))) {
                            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                            $validation.created += $parentDir
                        }
                    }
                    else {
                        # No extension, treat as directory
                        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
                        $validation.created += $relPath
                    }
                }
                catch {
                    $validation.valid = $false
                    $validation.errors += "Failed to create $relPath: $_"
                }
            }
            else {
                $validation.valid = $false
            }
        }
    }
    
    return $validation
}

#endregion

#region File Syntax Validation

function Validate-FileSyntax {
    <#
    .SYNOPSIS
        Validates file syntax for supported languages
    
    .PARAMETER FilePath
        Path to file to validate
    
    .PARAMETER Language
        Programming language (python, javascript, powershell, etc.)
    
    .OUTPUTS
        Hashtable with validation results: @{ valid=$true; errors=@(); warnings=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        
        [Parameter(Mandatory=$false)]
        [string]$Language = "auto"
    )
    
    $validation = @{
        valid = $true
        errors = @()
        warnings = @()
    }
    
    # Check file exists
    if (-not (Test-Path $FilePath)) {
        $validation.valid = $false
        $validation.errors += "File not found: $FilePath"
        return $validation
    }
    
    # Auto-detect language from extension
    if ($Language -eq "auto") {
        $ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
        $Language = switch ($ext) {
            ".py" { "python" }
            ".js" { "javascript" }
            ".ts" { "typescript" }
            ".ps1" { "powershell" }
            ".go" { "go" }
            ".java" { "java" }
            ".cs" { "csharp" }
            default { "unknown" }
        }
    }
    
    # Validate syntax based on language
    switch ($Language) {
        "python" {
            # Python syntax check using py_compile
            try {
                $result = python -c "import py_compile; py_compile.compile('$FilePath', doraise=True)" 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $validation.valid = $false
                    $validation.errors += "Python syntax error: $result"
                }
            }
            catch {
                $validation.valid = $false
                $validation.errors += "Python syntax validation failed: $_"
            }
        }
        
        "powershell" {
            # PowerShell syntax check
            try {
                $errors = $null
                $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $FilePath -Raw), [ref]$errors)
                if ($errors.Count -gt 0) {
                    $validation.valid = $false
                    foreach ($err in $errors) {
                        $validation.errors += "Line $($err.Token.StartLine): $($err.Message)"
                    }
                }
            }
            catch {
                $validation.valid = $false
                $validation.errors += "PowerShell syntax validation failed: $_"
            }
        }
        
        "javascript" {
            # JavaScript/Node syntax check
            try {
                $result = node --check $FilePath 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $validation.valid = $false
                    $validation.errors += "JavaScript syntax error: $result"
                }
            }
            catch {
                $validation.warnings += "JavaScript syntax validation skipped (node not available)"
            }
        }
        
        default {
            $validation.warnings += "Syntax validation not implemented for language: $Language"
        }
    }
    
    return $validation
}

#endregion

#region Dependency Validation

function Validate-Dependencies {
    <#
    .SYNOPSIS
        Validates required dependencies are installed
    
    .PARAMETER Dependencies
        Hashtable of dependencies: @{ python=@("pytest", "black"); npm=@("jest") }
    
    .OUTPUTS
        Hashtable with validation results: @{ valid=$true; missing=@(); errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Dependencies
    )
    
    $validation = @{
        valid = $true
        missing = @()
        errors = @()
    }
    
    # Check Python packages
    if ($Dependencies.ContainsKey("python")) {
        foreach ($pkg in $Dependencies["python"]) {
            try {
                $result = python -c "import $pkg" 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $validation.missing += "python:$pkg"
                    $validation.valid = $false
                }
            }
            catch {
                $validation.missing += "python:$pkg"
                $validation.valid = $false
            }
        }
    }
    
    # Check npm packages
    if ($Dependencies.ContainsKey("npm")) {
        foreach ($pkg in $Dependencies["npm"]) {
            try {
                $result = npm list -g $pkg 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $validation.missing += "npm:$pkg"
                    $validation.valid = $false
                }
            }
            catch {
                $validation.missing += "npm:$pkg"
                $validation.valid = $false
            }
        }
    }
    
    # Check executables
    if ($Dependencies.ContainsKey("executables")) {
        foreach ($exe in $Dependencies["executables"]) {
            if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
                $validation.missing += "executable:$exe"
                $validation.valid = $false
            }
        }
    }
    
    return $validation
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Validate-PatternInstance',
    'Validate-ProjectStructure',
    'Validate-FileSyntax',
    'Validate-Dependencies'
)
