#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pattern System CLI - Invoke patterns from registry
    
.DESCRIPTION
    Unified CLI for discovering and executing patterns from the pattern registry.
    Integrates with UET orchestrator for pattern-driven development.
    
.PARAMETER Action
    Action to perform: list, info, execute, validate
    
.PARAMETER PatternId
    Pattern ID to work with (e.g., PAT-ATOMIC-CREATE-001)
    
.PARAMETER InstancePath
    Path to pattern instance JSON file (for execute action)
    
.EXAMPLE
    .\pattern_cli.ps1 -Action list
    Lists all available patterns
    
.EXAMPLE
    .\pattern_cli.ps1 -Action info -PatternId PAT-ATOMIC-CREATE-001
    Shows detailed information about a pattern
    
.EXAMPLE
    .\pattern_cli.ps1 -Action execute -PatternId PAT-ATOMIC-CREATE-001 -InstancePath instance.json
    Executes a pattern with the given instance
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("list", "info", "execute", "validate", "search")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$PatternId,
    
    [Parameter(Mandatory=$false)]
    [string]$InstancePath,
    
    [Parameter(Mandatory=$false)]
    [string]$Category,
    
    [Parameter(Mandatory=$false)]
    [string]$SearchTerm
)

$ErrorActionPreference = "Stop"

# Constants
$REGISTRY_PATH = "patterns\registry\PATTERN_INDEX.yaml"
$PATTERNS_ROOT = "patterns"

# Helper: Load registry
function Load-Registry {
    if (-not (Test-Path $REGISTRY_PATH)) {
        throw "Pattern registry not found: $REGISTRY_PATH"
    }
    
    # Simple YAML parsing (for MVP, use regex; production should use PowerShell-YAML module)
    $content = Get-Content $REGISTRY_PATH -Raw
    
    # Extract pattern entries (simple parsing)
    $patterns = @()
    $lines = Get-Content $REGISTRY_PATH
    $currentPattern = $null
    
    foreach ($line in $lines) {
        if ($line -match '^\s*-\s+pattern_id:\s+"?([^"]+)"?') {
            if ($currentPattern) {
                $patterns += $currentPattern
            }
            $currentPattern = @{ pattern_id = $matches[1] }
        }
        elseif ($currentPattern) {
            if ($line -match '^\s+name:\s+"?([^"]+)"?') {
                $currentPattern.name = $matches[1]
            }
            elseif ($line -match '^\s+category:\s+"?([^"]+)"?') {
                $currentPattern.category = $matches[1]
            }
            elseif ($line -match '^\s+status:\s+"?([^"]+)"?') {
                $currentPattern.status = $matches[1]
            }
            elseif ($line -match '^\s+spec_path:\s+"?([^"]+)"?') {
                $currentPattern.spec_path = $matches[1]
            }
            elseif ($line -match '^\s+executor_path:\s+"?([^"]+)"?') {
                $currentPattern.executor_path = $matches[1]
            }
            elseif ($line -match '^\s+time_savings_vs_manual:\s+"?([^"]+)"?') {
                $currentPattern.time_savings = $matches[1]
            }
        }
    }
    
    if ($currentPattern) {
        $patterns += $currentPattern
    }
    
    return $patterns
}

# Action: List patterns
function Action-List {
    param($patterns, $category)
    
    Write-Host "`nPattern Registry" -ForegroundColor Cyan
    Write-Host "================`n" -ForegroundColor Cyan
    
    $filtered = $patterns
    if ($category) {
        $filtered = $patterns | Where-Object { $_.category -eq $category }
    }
    
    if ($filtered.Count -eq 0) {
        Write-Host "No patterns found." -ForegroundColor Yellow
        return
    }
    
    Write-Host ("Total patterns: " + $filtered.Count) -ForegroundColor Green
    Write-Host ""
    
    # Group by category
    $grouped = $filtered | Group-Object -Property category | Sort-Object Name
    
    foreach ($group in $grouped) {
        Write-Host ("Category: " + $group.Name) -ForegroundColor Yellow
        foreach ($pattern in $group.Group) {
            $status_icon = switch ($pattern.status) {
                "draft" { "📝" }
                "active" { "✅" }
                "migrated" { "🔄" }
                "spec_only" { "📄" }
                default { "⚪" }
            }
            
            $savings = if ($pattern.time_savings) { " (saves $($pattern.time_savings))" } else { "" }
            Write-Host ("  $status_icon $($pattern.pattern_id): $($pattern.name)$savings") -ForegroundColor White
        }
        Write-Host ""
    }
}

# Action: Show pattern info
function Action-Info {
    param($patterns, $patternId)
    
    $pattern = $patterns | Where-Object { $_.pattern_id -eq $patternId }
    
    if (-not $pattern) {
        Write-Host "Pattern not found: $patternId" -ForegroundColor Red
        return
    }
    
    Write-Host "`nPattern Information" -ForegroundColor Cyan
    Write-Host "===================`n" -ForegroundColor Cyan
    
    Write-Host ("Pattern ID: " + $pattern.pattern_id) -ForegroundColor White
    Write-Host ("Name: " + $pattern.name) -ForegroundColor White
    Write-Host ("Category: " + $pattern.category) -ForegroundColor White
    Write-Host ("Status: " + $pattern.status) -ForegroundColor White
    
    if ($pattern.time_savings) {
        Write-Host ("Time Savings: " + $pattern.time_savings) -ForegroundColor Green
    }
    
    Write-Host "`nFiles:" -ForegroundColor Yellow
    Write-Host ("  Spec: " + $pattern.spec_path) -ForegroundColor White
    if ($pattern.executor_path) {
        Write-Host ("  Executor: " + $pattern.executor_path) -ForegroundColor White
    }
    
    # Check if files exist
    Write-Host "`nAvailability:" -ForegroundColor Yellow
    if (Test-Path $pattern.spec_path) {
        Write-Host "  ✅ Spec exists" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Spec missing" -ForegroundColor Red
    }
    
    if ($pattern.executor_path -and (Test-Path $pattern.executor_path)) {
        Write-Host "  ✅ Executor exists" -ForegroundColor Green
    } elseif ($pattern.executor_path) {
        Write-Host "  ❌ Executor missing (spec-only pattern)" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Action: Execute pattern
function Action-Execute {
    param($patterns, $patternId, $instancePath)
    
    if (-not $instancePath) {
        Write-Host "Instance path required for execute action" -ForegroundColor Red
        return
    }
    
    if (-not (Test-Path $instancePath)) {
        Write-Host "Instance file not found: $instancePath" -ForegroundColor Red
        return
    }
    
    $pattern = $patterns | Where-Object { $_.pattern_id -eq $patternId }
    
    if (-not $pattern) {
        Write-Host "Pattern not found: $patternId" -ForegroundColor Red
        return
    }
    
    if (-not $pattern.executor_path -or -not (Test-Path $pattern.executor_path)) {
        Write-Host "❌ No executor available for this pattern" -ForegroundColor Red
        Write-Host "This is a spec-only pattern. Use with AI tools (Claude, Copilot)." -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nExecuting Pattern: $patternId" -ForegroundColor Cyan
    Write-Host "=====================================`n" -ForegroundColor Cyan
    
    # Invoke executor
    $executorExt = [System.IO.Path]::GetExtension($pattern.executor_path)
    
    switch ($executorExt) {
        ".ps1" {
            & $pattern.executor_path -InstancePath $instancePath
        }
        ".py" {
            python $pattern.executor_path --instance $instancePath
        }
        default {
            Write-Host "Unsupported executor type: $executorExt" -ForegroundColor Red
        }
    }
}

# Action: Validate registry
function Action-Validate {
    Write-Host "`nValidating Pattern Registry..." -ForegroundColor Cyan
    Write-Host "==============================`n" -ForegroundColor Cyan
    
    & "scripts\validate_pattern_registry.ps1"
}

# Action: Search patterns
function Action-Search {
    param($patterns, $searchTerm)
    
    if (-not $searchTerm) {
        Write-Host "Search term required" -ForegroundColor Red
        return
    }
    
    Write-Host "`nSearching for: $searchTerm" -ForegroundColor Cyan
    Write-Host "==========================`n" -ForegroundColor Cyan
    
    $results = $patterns | Where-Object {
        $_.pattern_id -like "*$searchTerm*" -or
        $_.name -like "*$searchTerm*" -or
        $_.category -like "*$searchTerm*"
    }
    
    if ($results.Count -eq 0) {
        Write-Host "No patterns found matching '$searchTerm'" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Found $($results.Count) pattern(s):`n" -ForegroundColor Green
    
    foreach ($pattern in $results) {
        Write-Host ("  • $($pattern.pattern_id): $($pattern.name)") -ForegroundColor White
        Write-Host ("    Category: $($pattern.category) | Status: $($pattern.status)") -ForegroundColor Gray
        Write-Host ""
    }
}

# Main execution
try {
    $patterns = Load-Registry
    
    switch ($Action) {
        "list" {
            Action-List -patterns $patterns -category $Category
        }
        "info" {
            if (-not $PatternId) {
                throw "PatternId required for info action"
            }
            Action-Info -patterns $patterns -patternId $PatternId
        }
        "execute" {
            if (-not $PatternId) {
                throw "PatternId required for execute action"
            }
            Action-Execute -patterns $patterns -patternId $PatternId -instancePath $InstancePath
        }
        "validate" {
            Action-Validate
        }
        "search" {
            Action-Search -patterns $patterns -searchTerm $SearchTerm
        }
    }
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
}
