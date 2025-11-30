#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-PARALLEL-972
# DOC_LINK: DOC-PAT-PARALLEL-236
<#
.SYNOPSIS
    Shared parallel processing library for pattern executors

.DESCRIPTION
    Provides parallel execution capabilities with progress tracking for:
    - Parallel file operations
    - Parallel validation checks
    - Progress reporting

.NOTES
    Module: parallel.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-PARALLEL-001
#>

#region Parallel Actions

function Invoke-ParallelActions {
    <#
    .SYNOPSIS
        Executes actions in parallel with progress tracking
    
    .PARAMETER Actions
        Array of script blocks or hashtables with: @{ name=$string; action=$scriptblock; params=@{} }
    
    .PARAMETER ThrottleLimit
        Maximum number of parallel threads (default: 5)
    
    .PARAMETER ShowProgress
        Display progress bar during execution
    
    .OUTPUTS
        Array of results: @{ name=$string; success=$bool; result=$object; error=$string; duration_ms=$int }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [array]$Actions,
        
        [Parameter(Mandatory=$false)]
        [int]$ThrottleLimit = 5,
        
        [Parameter(Mandatory=$false)]
        [switch]$ShowProgress
    )
    
    $results = @()
    $completed = 0
    $total = $Actions.Count
    
    if ($ShowProgress) {
        Write-Progress -Activity "Executing parallel actions" -Status "Starting..." -PercentComplete 0
    }
    
    # Execute actions in parallel using ForEach-Object -Parallel
    $results = $Actions | ForEach-Object -ThrottleLimit $ThrottleLimit -Parallel {
        $action = $_
        $actionName = if ($action -is [hashtable]) { $action.name } else { "Action_$($_.ToString().GetHashCode())" }
        $scriptBlock = if ($action -is [hashtable]) { $action.action } else { $action }
        $parameters = if ($action -is [hashtable] -and $action.params) { $action.params } else { @{} }
        
        $result = @{
            name = $actionName
            success = $false
            result = $null
            error = $null
            duration_ms = 0
        }
        
        $startTime = Get-Date
        
        try {
            # Execute the script block
            if ($parameters.Count -gt 0) {
                $result.result = & $scriptBlock @parameters
            }
            else {
                $result.result = & $scriptBlock
            }
            $result.success = $true
        }
        catch {
            $result.error = $_.Exception.Message
            $result.success = $false
        }
        finally {
            $result.duration_ms = [int]((Get-Date) - $startTime).TotalMilliseconds
        }
        
        return $result
    }
    
    if ($ShowProgress) {
        Write-Progress -Activity "Executing parallel actions" -Completed
    }
    
    return $results
}

#endregion

#region Parallel Checks

function Invoke-ParallelChecks {
    <#
    .SYNOPSIS
        Runs validation checks in parallel and aggregates results
    
    .PARAMETER Checks
        Array of check definitions: @{ id=$string; name=$string; check=$scriptblock; severity=$string }
    
    .PARAMETER ThrottleLimit
        Maximum number of parallel threads (default: 5)
    
    .PARAMETER FailFast
        Stop on first critical failure
    
    .OUTPUTS
        Hashtable with aggregated results: @{ passed=$int; failed=$int; checks=@(); all_passed=$bool }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [array]$Checks,
        
        [Parameter(Mandatory=$false)]
        [int]$ThrottleLimit = 5,
        
        [Parameter(Mandatory=$false)]
        [switch]$FailFast
    )
    
    $aggregated = @{
        passed = 0
        failed = 0
        warnings = 0
        checks = @()
        all_passed = $true
        critical_failed = $false
    }
    
    # Execute checks in parallel
    $checkResults = $Checks | ForEach-Object -ThrottleLimit $ThrottleLimit -Parallel {
        $check = $_
        
        $result = @{
            id = $check.id
            name = $check.name
            severity = if ($check.severity) { $check.severity } else { "high" }
            passed = $false
            message = ""
            duration_ms = 0
        }
        
        $startTime = Get-Date
        
        try {
            # Execute the check
            $checkResult = & $check.check
            
            # Interpret result (can be boolean, hashtable, or string)
            if ($checkResult -is [bool]) {
                $result.passed = $checkResult
            }
            elseif ($checkResult -is [hashtable]) {
                $result.passed = $checkResult.passed
                $result.message = $checkResult.message
            }
            else {
                # Treat any non-empty string as failure message
                if ($checkResult) {
                    $result.passed = $false
                    $result.message = $checkResult
                }
                else {
                    $result.passed = $true
                }
            }
        }
        catch {
            $result.passed = $false
            $result.message = "Check failed with exception: $($_.Exception.Message)"
        }
        finally {
            $result.duration_ms = [int]((Get-Date) - $startTime).TotalMilliseconds
        }
        
        return $result
    }
    
    # Aggregate results
    foreach ($checkResult in $checkResults) {
        $aggregated.checks += $checkResult
        
        if ($checkResult.passed) {
            $aggregated.passed++
        }
        else {
            if ($checkResult.severity -eq "warning") {
                $aggregated.warnings++
            }
            else {
                $aggregated.failed++
                $aggregated.all_passed = $false
                
                if ($checkResult.severity -eq "critical") {
                    $aggregated.critical_failed = $true
                    
                    if ($FailFast) {
                        break
                    }
                }
            }
        }
    }
    
    return $aggregated
}

#endregion

#region Progress Tracking

function Start-ProgressTracker {
    <#
    .SYNOPSIS
        Creates a progress tracker for long-running operations
    
    .PARAMETER Activity
        Activity name for progress display
    
    .PARAMETER TotalSteps
        Total number of steps
    
    .OUTPUTS
        Hashtable progress tracker object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Activity,
        
        [Parameter(Mandatory=$true)]
        [int]$TotalSteps
    )
    
    return @{
        activity = $Activity
        total_steps = $TotalSteps
        current_step = 0
        start_time = Get-Date
        steps_completed = @()
    }
}

function Update-ProgressTracker {
    <#
    .SYNOPSIS
        Updates progress tracker and displays progress bar
    
    .PARAMETER Tracker
        Progress tracker object from Start-ProgressTracker
    
    .PARAMETER StepName
        Name of completed step
    
    .PARAMETER Status
        Current status message
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Tracker,
        
        [Parameter(Mandatory=$true)]
        [string]$StepName,
        
        [Parameter(Mandatory=$false)]
        [string]$Status = ""
    )
    
    $Tracker.current_step++
    $Tracker.steps_completed += @{
        name = $StepName
        completed_at = Get-Date
    }
    
    $percentComplete = [int](($Tracker.current_step / $Tracker.total_steps) * 100)
    $elapsed = (Get-Date) - $Tracker.start_time
    $avgTimePerStep = $elapsed.TotalSeconds / $Tracker.current_step
    $remainingSteps = $Tracker.total_steps - $Tracker.current_step
    $estimatedRemaining = [timespan]::FromSeconds($avgTimePerStep * $remainingSteps)
    
    $statusMessage = if ($Status) { $Status } else { "Step $($Tracker.current_step) of $($Tracker.total_steps): $StepName" }
    
    Write-Progress `
        -Activity $Tracker.activity `
        -Status $statusMessage `
        -PercentComplete $percentComplete `
        -SecondsRemaining ([int]$estimatedRemaining.TotalSeconds)
}

function Complete-ProgressTracker {
    <#
    .SYNOPSIS
        Completes progress tracker and hides progress bar
    
    .PARAMETER Tracker
        Progress tracker object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Tracker
    )
    
    Write-Progress -Activity $Tracker.activity -Completed
    
    $duration = (Get-Date) - $Tracker.start_time
    
    return @{
        total_steps = $Tracker.total_steps
        duration_seconds = $duration.TotalSeconds
        avg_step_duration_ms = ($duration.TotalMilliseconds / $Tracker.total_steps)
        steps = $Tracker.steps_completed
    }
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Invoke-ParallelActions',
    'Invoke-ParallelChecks',
    'Start-ProgressTracker',
    'Update-ProgressTracker',
    'Complete-ProgressTracker'
)
