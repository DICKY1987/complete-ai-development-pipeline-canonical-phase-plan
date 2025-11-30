#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-REPORTING-973
# DOC_LINK: DOC-PAT-REPORTING-237
<#
.SYNOPSIS
    Reporting and verification record library for pattern executors

.DESCRIPTION
    Provides execution report and verification record generation:
    - Execution reports (JSON/YAML)
    - Verification records
    - Result formatting

.NOTES
    Module: reporting.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-REPORTING-001
#>

#region Execution Reports

function New-ExecutionReport {
    <#
    .SYNOPSIS
        Creates a structured execution report for pattern execution
    
    .PARAMETER PatternId
        Pattern identifier
    
    .PARAMETER Status
        Execution status (success, failed, partial)
    
    .PARAMETER StartTime
        Execution start time
    
    .PARAMETER EndTime
        Execution end time (default: now)
    
    .PARAMETER Operations
        Array of operations performed
    
    .PARAMETER Errors
        Array of errors encountered
    
    .PARAMETER OutputPath
        Optional file path to save report
    
    .PARAMETER Format
        Output format (json, yaml, hashtable)
    
    .OUTPUTS
        Hashtable execution report
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$PatternId,
        
        [Parameter(Mandatory=$true)]
        [ValidateSet('success', 'failed', 'partial')]
        [string]$Status,
        
        [Parameter(Mandatory=$true)]
        [datetime]$StartTime,
        
        [Parameter(Mandatory=$false)]
        [datetime]$EndTime = (Get-Date),
        
        [Parameter(Mandatory=$false)]
        [array]$Operations = @(),
        
        [Parameter(Mandatory=$false)]
        [array]$Errors = @(),
        
        [Parameter(Mandatory=$false)]
        [hashtable]$Metadata = @{},
        
        [Parameter(Mandatory=$false)]
        [string]$OutputPath = $null,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('json', 'yaml', 'hashtable')]
        [string]$Format = 'hashtable'
    )
    
    $duration = $EndTime - $StartTime
    
    $report = @{
        report_type = "execution"
        pattern_id = $PatternId
        status = $Status
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        execution = @{
            started_at = $StartTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            ended_at = $EndTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            duration_seconds = [math]::Round($duration.TotalSeconds, 3)
        }
        operations = @{
            total = $Operations.Count
            successful = ($Operations | Where-Object { $_.success -eq $true }).Count
            failed = ($Operations | Where-Object { $_.success -eq $false }).Count
            details = $Operations
        }
        errors = @{
            count = $Errors.Count
            details = $Errors
        }
        metadata = $Metadata
    }
    
    # Format output
    $output = switch ($Format) {
        'json' {
            $report | ConvertTo-Json -Depth 10
        }
        'yaml' {
            ConvertTo-Yaml -Data $report
        }
        'hashtable' {
            $report
        }
    }
    
    # Save to file if path provided
    if ($OutputPath) {
        if ($Format -eq 'hashtable') {
            # Convert to JSON for file output
            $report | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath
        }
        else {
            $output | Set-Content -Path $OutputPath
        }
    }
    
    return $output
}

#endregion

#region Verification Records

function New-VerificationRecord {
    <#
    .SYNOPSIS
        Creates a verification record documenting pattern execution results
    
    .PARAMETER PatternId
        Pattern identifier
    
    .PARAMETER InstanceId
        Instance identifier (optional)
    
    .PARAMETER Checks
        Array of check results
    
    .PARAMETER FilesCreated
        Array of created files
    
    .PARAMETER FilesModified
        Array of modified files
    
    .PARAMETER TestResults
        Test execution results
    
    .PARAMETER OutputPath
        File path to save verification record
    
    .PARAMETER Format
        Output format (json, yaml)
    
    .OUTPUTS
        Hashtable verification record
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$PatternId,
        
        [Parameter(Mandatory=$false)]
        [string]$InstanceId = $null,
        
        [Parameter(Mandatory=$false)]
        [array]$Checks = @(),
        
        [Parameter(Mandatory=$false)]
        [array]$FilesCreated = @(),
        
        [Parameter(Mandatory=$false)]
        [array]$FilesModified = @(),
        
        [Parameter(Mandatory=$false)]
        [hashtable]$TestResults = @{},
        
        [Parameter(Mandatory=$false)]
        [hashtable]$ValidationResults = @{},
        
        [Parameter(Mandatory=$false)]
        [string]$OutputPath = $null,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('json', 'yaml', 'hashtable')]
        [string]$Format = 'json'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    
    $record = @{
        doc_type = "verification_record"
        pattern_id = $PatternId
        instance_id = $InstanceId
        timestamp = $timestamp
        verification = @{
            checks_passed = ($Checks | Where-Object { $_.passed -eq $true }).Count
            checks_failed = ($Checks | Where-Object { $_.passed -eq $false }).Count
            all_checks_passed = (($Checks | Where-Object { $_.passed -eq $false }).Count -eq 0)
            check_details = $Checks
        }
        changes = @{
            files_created = $FilesCreated
            files_modified = $FilesModified
            total_changes = $FilesCreated.Count + $FilesModified.Count
        }
        tests = $TestResults
        validation = $ValidationResults
        verified_by = "pattern_executor"
        verification_timestamp = $timestamp
    }
    
    # Format output
    $output = switch ($Format) {
        'json' {
            $record | ConvertTo-Json -Depth 10
        }
        'yaml' {
            ConvertTo-Yaml -Data $record
        }
        'hashtable' {
            $record
        }
    }
    
    # Save to file if path provided
    if ($OutputPath) {
        if ($Format -eq 'hashtable') {
            $record | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath
        }
        else {
            $output | Set-Content -Path $OutputPath
        }
    }
    
    return $output
}

#endregion

#region Result Formatting

function Format-ExecutionResult {
    <#
    .SYNOPSIS
        Formats execution result for display
    
    .PARAMETER Result
        Result hashtable from pattern execution
    
    .PARAMETER Style
        Display style (detailed, summary, minimal)
    
    .OUTPUTS
        Formatted string for display
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Result,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet('detailed', 'summary', 'minimal')]
        [string]$Style = 'summary'
    )
    
    $output = ""
    
    switch ($Style) {
        'minimal' {
            $statusSymbol = if ($Result.status -eq 'success') { '✓' } else { '✗' }
            $output = "$statusSymbol $($Result.pattern_id): $($Result.status)"
        }
        
        'summary' {
            $output = @"
Pattern Execution Result
========================
Pattern: $($Result.pattern_id)
Status: $($Result.status)
Duration: $($Result.execution_duration_seconds)s

Operations: $($Result.operations.total) total, $($Result.operations.successful) successful, $($Result.operations.failed) failed
Errors: $($Result.errors.count)
"@
        }
        
        'detailed' {
            $output = @"
========================================
PATTERN EXECUTION REPORT
========================================

Pattern ID: $($Result.pattern_id)
Status: $($Result.status)
Timestamp: $($Result.timestamp)

EXECUTION SUMMARY
-----------------
Duration: $($Result.execution_duration_seconds)s
Started: $($Result.execution.started_at)
Ended: $($Result.execution.ended_at)

OPERATIONS
----------
Total: $($Result.operations.total)
Successful: $($Result.operations.successful)
Failed: $($Result.operations.failed)

ERRORS
------
Count: $($Result.errors.count)

"@
            if ($Result.errors.count -gt 0) {
                $output += "Details:`n"
                foreach ($error in $Result.errors.details) {
                    $output += "  - $error`n"
                }
            }
        }
    }
    
    return $output
}

#endregion

#region YAML Conversion Helper

function ConvertTo-Yaml {
    <#
    .SYNOPSIS
        Converts hashtable to YAML format (basic implementation)
    
    .PARAMETER Data
        Hashtable to convert
    
    .PARAMETER IndentLevel
        Current indentation level
    
    .OUTPUTS
        YAML formatted string
    #>
    param(
        [Parameter(Mandatory=$true)]
        $Data,
        
        [Parameter(Mandatory=$false)]
        [int]$IndentLevel = 0
    )
    
    $indent = "  " * $IndentLevel
    $yaml = ""
    
    if ($Data -is [hashtable]) {
        foreach ($key in $Data.Keys) {
            $value = $Data[$key]
            
            if ($value -is [hashtable] -or $value -is [array]) {
                $yaml += "$indent$key:`n"
                $yaml += ConvertTo-Yaml -Data $value -IndentLevel ($IndentLevel + 1)
            }
            else {
                $yaml += "$indent$key: $value`n"
            }
        }
    }
    elseif ($Data -is [array]) {
        foreach ($item in $Data) {
            if ($item -is [hashtable]) {
                $yaml += "$indent-`n"
                $yaml += ConvertTo-Yaml -Data $item -IndentLevel ($IndentLevel + 1)
            }
            else {
                $yaml += "$indent- $item`n"
            }
        }
    }
    
    return $yaml
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'New-ExecutionReport',
    'New-VerificationRecord',
    'Format-ExecutionResult'
)
