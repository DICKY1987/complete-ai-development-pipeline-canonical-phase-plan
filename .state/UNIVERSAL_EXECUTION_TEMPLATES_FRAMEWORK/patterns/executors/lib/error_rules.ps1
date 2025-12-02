#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Error detection and fix rule library for self-healing executors

.DESCRIPTION
    Provides error pattern matching and fix rules for common issues:
    - Import errors
    - Indentation errors
    - Syntax errors
    - Missing dependencies

.NOTES
    Module: error_rules.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-ERROR-RULES-001
#>

#region Rule Registry

$script:FixRules = @(
    @{
        id = "RULE-001"
        pattern = "ModuleNotFoundError: No module named '([^']+)'"
        error_type = "import"
        language = "python"
        description = "Missing Python module import"
        fix = {
            param($match, $file_path)
            $module = $match.Groups[1].Value
            return @{
                action = "add_import"
                module = $module
                suggestion = "Add 'import $module' or install with 'pip install $module'"
            }
        }
    },
    @{
        id = "RULE-002"
        pattern = "IndentationError: (expected an indented block|unexpected indent)"
        error_type = "indentation"
        language = "python"
        description = "Python indentation error"
        fix = {
            param($match, $file_path)
            return @{
                action = "fix_indentation"
                suggestion = "Normalize indentation to 4 spaces"
                auto_fixable = $true
            }
        }
    },
    @{
        id = "RULE-003"
        pattern = "SyntaxError: invalid syntax.*line (\d+)"
        error_type = "syntax"
        language = "python"
        description = "Python syntax error"
        fix = {
            param($match, $file_path)
            $line = $match.Groups[1].Value
            return @{
                action = "review_syntax"
                line = $line
                suggestion = "Review syntax at line $line"
                auto_fixable = $false
            }
        }
    },
    @{
        id = "RULE-004"
        pattern = "NameError: name '(\w+)' is not defined"
        error_type = "undefined_variable"
        language = "python"
        description = "Undefined variable reference"
        fix = {
            param($match, $file_path)
            $var_name = $match.Groups[1].Value
            return @{
                action = "check_variable"
                variable = $var_name
                suggestion = "Ensure '$var_name' is defined before use or import it"
                auto_fixable = $false
            }
        }
    },
    @{
        id = "RULE-005"
        pattern = "ImportError: cannot import name '(\w+)' from '([^']+)'"
        error_type = "import"
        language = "python"
        description = "Invalid import statement"
        fix = {
            param($match, $file_path)
            $name = $match.Groups[1].Value
            $module = $match.Groups[2].Value
            return @{
                action = "fix_import"
                name = $name
                module = $module
                suggestion = "Verify '$name' exists in module '$module' or update import"
                auto_fixable = $false
            }
        }
    },
    @{
        id = "RULE-006"
        pattern = "TypeError: (\w+)\(\) (missing \d+ required positional argument|takes \d+ positional argument)"
        error_type = "function_call"
        language = "python"
        description = "Incorrect function call arguments"
        fix = {
            param($match, $file_path)
            $function = $match.Groups[1].Value
            return @{
                action = "check_function_signature"
                function = $function
                suggestion = "Review function signature for '$function' and fix arguments"
                auto_fixable = $false
            }
        }
    }
)

#endregion

#region Rule Matching

function Get-FixRule {
    <#
    .SYNOPSIS
        Finds matching fix rule for an error message
    
    .PARAMETER ErrorMessage
        Error message from test/compiler output
    
    .PARAMETER Language
        Programming language (python, javascript, etc.)
    
    .PARAMETER FilePath
        Path to file that generated the error
    
    .OUTPUTS
        Hashtable with matched rule and fix details, or $null if no match
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ErrorMessage,
        
        [Parameter(Mandatory=$false)]
        [string]$Language = "python",
        
        [Parameter(Mandatory=$false)]
        [string]$FilePath = ""
    )
    
    foreach ($rule in $script:FixRules) {
        # Skip rules for other languages
        if ($rule.language -ne $Language) {
            continue
        }
        
        # Try to match pattern
        $match = [regex]::Match($ErrorMessage, $rule.pattern)
        
        if ($match.Success) {
            # Execute fix function to get fix details
            $fixDetails = & $rule.fix $match $FilePath
            
            return @{
                rule_id = $rule.id
                error_type = $rule.error_type
                description = $rule.description
                matched_text = $match.Value
                fix = $fixDetails
            }
        }
    }
    
    # No matching rule found
    return $null
}

function Get-AllFixRules {
    <#
    .SYNOPSIS
        Returns all registered fix rules
    
    .PARAMETER Language
        Filter by programming language (optional)
    
    .PARAMETER ErrorType
        Filter by error type (optional)
    
    .OUTPUTS
        Array of fix rule definitions
    #>
    param(
        [Parameter(Mandatory=$false)]
        [string]$Language = $null,
        
        [Parameter(Mandatory=$false)]
        [string]$ErrorType = $null
    )
    
    $filtered = $script:FixRules
    
    if ($Language) {
        $filtered = $filtered | Where-Object { $_.language -eq $Language }
    }
    
    if ($ErrorType) {
        $filtered = $filtered | Where-Object { $_.error_type -eq $ErrorType }
    }
    
    return $filtered
}

#endregion

#region Auto-Fix Implementations

function Invoke-AutoFix {
    <#
    .SYNOPSIS
        Attempts to automatically fix an error based on matched rule
    
    .PARAMETER FilePath
        Path to file to fix
    
    .PARAMETER FixRule
        Fix rule object from Get-FixRule
    
    .OUTPUTS
        Hashtable with fix results: @{ success=$bool; changes_made=$bool; message=$string }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$FixRule
    )
    
    $result = @{
        success = $false
        changes_made = $false
        message = ""
    }
    
    # Check if fix is auto-fixable
    if ($FixRule.fix.auto_fixable -eq $false) {
        $result.message = "Fix requires manual intervention: $($FixRule.fix.suggestion)"
        return $result
    }
    
    # Apply auto-fix based on action type
    try {
        switch ($FixRule.fix.action) {
            "fix_indentation" {
                $content = Get-Content $FilePath -Raw
                
                # Normalize indentation to 4 spaces
                $lines = $content -split "`n"
                $fixedLines = @()
                
                foreach ($line in $lines) {
                    # Replace tabs with 4 spaces
                    $fixedLine = $line -replace "`t", "    "
                    $fixedLines += $fixedLine
                }
                
                $fixedContent = $fixedLines -join "`n"
                Set-Content -Path $FilePath -Value $fixedContent -NoNewline
                
                $result.success = $true
                $result.changes_made = $true
                $result.message = "Fixed indentation errors"
            }
            
            "add_import" {
                $module = $FixRule.fix.module
                $content = Get-Content $FilePath -Raw
                
                # Add import at top of file (after any existing imports)
                $importLine = "import $module`n"
                
                # Find last import line
                $lines = $content -split "`n"
                $lastImportIndex = -1
                
                for ($i = 0; $i -lt $lines.Count; $i++) {
                    if ($lines[$i] -match "^(import |from .* import )") {
                        $lastImportIndex = $i
                    }
                }
                
                if ($lastImportIndex -ge 0) {
                    # Insert after last import
                    $lines = @($lines[0..$lastImportIndex]) + $importLine + @($lines[($lastImportIndex + 1)..($lines.Count - 1)])
                }
                else {
                    # No imports found, add at top
                    $lines = @($importLine) + $lines
                }
                
                $fixedContent = $lines -join "`n"
                Set-Content -Path $FilePath -Value $fixedContent -NoNewline
                
                $result.success = $true
                $result.changes_made = $true
                $result.message = "Added import: $module"
            }
            
            default {
                $result.message = "Auto-fix not implemented for action: $($FixRule.fix.action)"
            }
        }
    }
    catch {
        $result.success = $false
        $result.message = "Auto-fix failed: $($_.Exception.Message)"
    }
    
    return $result
}

#endregion

#region Rule Registry Management

function Add-FixRule {
    <#
    .SYNOPSIS
        Adds a custom fix rule to the registry
    
    .PARAMETER Rule
        Rule definition hashtable
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Rule
    )
    
    # Validate rule structure
    $required = @('id', 'pattern', 'error_type', 'language', 'description', 'fix')
    foreach ($field in $required) {
        if (-not $Rule.ContainsKey($field)) {
            throw "Rule missing required field: $field"
        }
    }
    
    $script:FixRules += $Rule
}

function Import-FixRulesFromJson {
    <#
    .SYNOPSIS
        Imports fix rules from JSON file
    
    .PARAMETER JsonPath
        Path to JSON file with rule definitions
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$JsonPath
    )
    
    if (-not (Test-Path $JsonPath)) {
        throw "Rules file not found: $JsonPath"
    }
    
    $rules = Get-Content $JsonPath -Raw | ConvertFrom-Json
    
    foreach ($rule in $rules) {
        # Convert JSON rule to hashtable with script block fix
        $ruleHash = @{
            id = $rule.id
            pattern = $rule.pattern
            error_type = $rule.error_type
            language = $rule.language
            description = $rule.description
            fix = [scriptblock]::Create($rule.fix_script)
        }
        
        Add-FixRule -Rule $ruleHash
    }
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Get-FixRule',
    'Get-AllFixRules',
    'Invoke-AutoFix',
    'Add-FixRule',
    'Import-FixRulesFromJson'
)
