#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-TESTING-239
<#
.SYNOPSIS
    Test execution and result parsing library for pattern executors

.DESCRIPTION
    Provides test execution wrappers and result parsing for:
    - pytest (Python)
    - jest (JavaScript)
    - go test (Go)
    - Generic test runners

.NOTES
    Module: testing.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-TESTING-001
#>

#region Test Execution

function Invoke-TestSuite {
    <#
    .SYNOPSIS
        Executes test suite for specified framework
    
    .PARAMETER Framework
        Test framework (pytest, jest, go_test, generic)
    
    .PARAMETER TestPath
        Path to test file or directory
    
    .PARAMETER AdditionalArgs
        Additional command-line arguments for test runner
    
    .PARAMETER Timeout
        Test execution timeout in seconds (default: 300)
    
    .OUTPUTS
        Hashtable with test results: @{ success=$bool; passed=$int; failed=$int; duration_seconds=$float; output=$string }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet('pytest', 'jest', 'go_test', 'generic')]
        [string]$Framework,
        
        [Parameter(Mandatory=$true)]
        [string]$TestPath,
        
        [Parameter(Mandatory=$false)]
        [string[]]$AdditionalArgs = @(),
        
        [Parameter(Mandatory=$false)]
        [int]$Timeout = 300
    )
    
    $result = @{
        success = $false
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
        output = ""
        errors = @()
    }
    
    $startTime = Get-Date
    
    try {
        switch ($Framework) {
            'pytest' {
                $result = Invoke-PytestSuite -TestPath $TestPath -AdditionalArgs $AdditionalArgs -Timeout $Timeout
            }
            'jest' {
                $result = Invoke-JestSuite -TestPath $TestPath -AdditionalArgs $AdditionalArgs -Timeout $Timeout
            }
            'go_test' {
                $result = Invoke-GoTestSuite -TestPath $TestPath -AdditionalArgs $AdditionalArgs -Timeout $Timeout
            }
            'generic' {
                $result = Invoke-GenericTestSuite -TestPath $TestPath -AdditionalArgs $AdditionalArgs -Timeout $Timeout
            }
        }
    }
    catch {
        $result.errors += $_.Exception.Message
    }
    finally {
        $result.duration_seconds = ((Get-Date) - $startTime).TotalSeconds
    }
    
    return $result
}

#endregion

#region Framework-Specific Executors

function Invoke-PytestSuite {
    <#
    .SYNOPSIS
        Executes pytest test suite
    #>
    param(
        [string]$TestPath,
        [string[]]$AdditionalArgs,
        [int]$Timeout
    )
    
    $result = @{
        success = $false
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
        output = ""
        errors = @()
    }
    
    # Build pytest command
    $args = @("-v", "--tb=short", $TestPath) + $AdditionalArgs
    
    # Execute pytest
    $process = Start-Process -FilePath "pytest" -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput "pytest_output.txt" -RedirectStandardError "pytest_error.txt"
    
    $result.output = Get-Content "pytest_output.txt" -Raw -ErrorAction SilentlyContinue
    $errorOutput = Get-Content "pytest_error.txt" -Raw -ErrorAction SilentlyContinue
    
    # Parse pytest output
    $parsed = Parse-PytestResults -Output $result.output
    $result.passed = $parsed.passed
    $result.failed = $parsed.failed
    $result.skipped = $parsed.skipped
    $result.duration_seconds = $parsed.duration_seconds
    
    $result.success = ($process.ExitCode -eq 0)
    
    if ($errorOutput) {
        $result.errors += $errorOutput
    }
    
    # Clean up temp files
    Remove-Item "pytest_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "pytest_error.txt" -ErrorAction SilentlyContinue
    
    return $result
}

function Invoke-JestSuite {
    <#
    .SYNOPSIS
        Executes jest test suite
    #>
    param(
        [string]$TestPath,
        [string[]]$AdditionalArgs,
        [int]$Timeout
    )
    
    $result = @{
        success = $false
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
        output = ""
        errors = @()
    }
    
    # Build jest command
    $args = @("--verbose", $TestPath) + $AdditionalArgs
    
    # Execute jest
    $output = & npx jest @args 2>&1 | Out-String
    $result.output = $output
    
    # Parse jest output
    $parsed = Parse-JestResults -Output $output
    $result.passed = $parsed.passed
    $result.failed = $parsed.failed
    $result.skipped = $parsed.skipped
    $result.duration_seconds = $parsed.duration_seconds
    
    $result.success = ($LASTEXITCODE -eq 0)
    
    return $result
}

function Invoke-GoTestSuite {
    <#
    .SYNOPSIS
        Executes go test suite
    #>
    param(
        [string]$TestPath,
        [string[]]$AdditionalArgs,
        [int]$Timeout
    )
    
    $result = @{
        success = $false
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
        output = ""
        errors = @()
    }
    
    # Build go test command
    $args = @("test", "-v", $TestPath) + $AdditionalArgs
    
    # Execute go test
    $output = & go @args 2>&1 | Out-String
    $result.output = $output
    
    # Parse go test output
    $parsed = Parse-GoTestResults -Output $output
    $result.passed = $parsed.passed
    $result.failed = $parsed.failed
    $result.skipped = $parsed.skipped
    $result.duration_seconds = $parsed.duration_seconds
    
    $result.success = ($LASTEXITCODE -eq 0)
    
    return $result
}

function Invoke-GenericTestSuite {
    <#
    .SYNOPSIS
        Executes generic test command
    #>
    param(
        [string]$TestPath,
        [string[]]$AdditionalArgs,
        [int]$Timeout
    )
    
    $result = @{
        success = $false
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
        output = ""
        errors = @()
    }
    
    # Execute test command
    $output = & $TestPath @AdditionalArgs 2>&1 | Out-String
    $result.output = $output
    $result.success = ($LASTEXITCODE -eq 0)
    
    return $result
}

#endregion

#region Result Parsing

function Parse-TestResults {
    <#
    .SYNOPSIS
        Parses test output and extracts results
    
    .PARAMETER Output
        Test runner output
    
    .PARAMETER Framework
        Test framework type
    
    .OUTPUTS
        Hashtable with parsed results: @{ passed=$int; failed=$int; duration_seconds=$float }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Output,
        
        [Parameter(Mandatory=$true)]
        [ValidateSet('pytest', 'jest', 'go_test')]
        [string]$Framework
    )
    
    switch ($Framework) {
        'pytest' { return Parse-PytestResults -Output $Output }
        'jest' { return Parse-JestResults -Output $Output }
        'go_test' { return Parse-GoTestResults -Output $Output }
    }
}

function Parse-PytestResults {
    param([string]$Output)
    
    $result = @{
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
    }
    
    # Extract test counts from summary line: "5 passed, 2 failed, 1 skipped in 2.34s"
    if ($Output -match '(\d+)\s+passed') {
        $result.passed = [int]$matches[1]
    }
    if ($Output -match '(\d+)\s+failed') {
        $result.failed = [int]$matches[1]
    }
    if ($Output -match '(\d+)\s+skipped') {
        $result.skipped = [int]$matches[1]
    }
    if ($Output -match 'in\s+([\d.]+)s') {
        $result.duration_seconds = [float]$matches[1]
    }
    
    return $result
}

function Parse-JestResults {
    param([string]$Output)
    
    $result = @{
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
    }
    
    # Extract test counts from Jest output
    if ($Output -match 'Tests:\s+(\d+)\s+passed') {
        $result.passed = [int]$matches[1]
    }
    if ($Output -match '(\d+)\s+failed') {
        $result.failed = [int]$matches[1]
    }
    if ($Output -match '(\d+)\s+skipped') {
        $result.skipped = [int]$matches[1]
    }
    if ($Output -match 'Time:\s+([\d.]+)\s*s') {
        $result.duration_seconds = [float]$matches[1]
    }
    
    return $result
}

function Parse-GoTestResults {
    param([string]$Output)
    
    $result = @{
        passed = 0
        failed = 0
        skipped = 0
        duration_seconds = 0
    }
    
    # Count PASS and FAIL lines
    $result.passed = ([regex]::Matches($Output, '--- PASS:')).Count
    $result.failed = ([regex]::Matches($Output, '--- FAIL:')).Count
    $result.skipped = ([regex]::Matches($Output, '--- SKIP:')).Count
    
    # Extract duration
    if ($Output -match 'ok\s+.*\s+([\d.]+)s') {
        $result.duration_seconds = [float]$matches[1]
    }
    
    return $result
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Invoke-TestSuite',
    'Parse-TestResults'
)
