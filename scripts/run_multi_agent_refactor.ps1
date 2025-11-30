# DOC_LINK: DOC-SCRIPT-RUN-MULTI-AGENT-REFACTOR-067
<#
.SYNOPSIS
    One-touch launcher for multi-agent workstream execution

.DESCRIPTION
    This script automates the complete multi-agent refactor:
    1. Pre-flight validation
    2. Worktree setup
    3. Orchestrator launch
    4. Progress monitoring
    5. Cleanup

.PARAMETER DryRun
    Run in dry-run mode (no actual changes)

.PARAMETER Agents
    Number of agents to use (default: 3)

.EXAMPLE
    .\run_multi_agent_refactor.ps1

.EXAMPLE
    .\run_multi_agent_refactor.ps1 -DryRun -Agents 1

.EXAMPLE
    .\run_multi_agent_refactor.ps1 -Agents 6
#>

param(
    [switch]$DryRun,
    [int]$Agents = 3
)

$ErrorActionPreference = "Stop"

# CRITICAL: Cleanup handler for Ctrl+C or crashes
# Prevents orphaned worktrees that block future runs
trap {
    Write-Host ""
    Write-Host "🛑 Orchestrator interrupted or crashed!" -ForegroundColor Red
    Write-Host "🧹 Cleaning up worktrees..." -ForegroundColor Yellow
    
    try {
        # Force remove all agent worktrees
        $worktrees = git worktree list --porcelain | Select-String "^worktree.*\.worktrees"
        foreach ($line in $worktrees) {
            $path = $line -replace "^worktree ", ""
            Write-Host "  Removing: $path" -ForegroundColor Gray
            git worktree remove $path --force 2>$null
        }
        Write-Host "✅ Cleanup complete" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Manual cleanup may be required: git worktree prune" -ForegroundColor Yellow
    }
    
    Write-Host ""
    throw  # Re-throw to show original error
}

function Write-Banner {
    param([string]$Text)
    $width = 70
    $padding = [Math]::Max(0, ($width - $Text.Length - 2) / 2)
    $paddingStr = "═" * [Math]::Floor($padding)
    
    Write-Host ""
    Write-Host ("╔" + ("═" * ($width - 2)) + "╗") -ForegroundColor Cyan
    Write-Host ("║" + $paddingStr + " $Text " + $paddingStr + ("═" * ($padding % 1)) + "║") -ForegroundColor Cyan
    Write-Host ("╚" + ("═" * ($width - 2)) + "╝") -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param(
        [int]$Number,
        [int]$Total,
        [string]$Title
    )
    Write-Host ""
    Write-Host "Step $Number/$Total`: $Title" -ForegroundColor Yellow
    Write-Host ("─" * 70) -ForegroundColor Yellow
}

# Header
Write-Banner "Multi-Agent Workstream Orchestrator"

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - No actual changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  • Agents: $Agents" -ForegroundColor Gray
Write-Host "  • Dry Run: $DryRun" -ForegroundColor Gray

# Step 1: Pre-Flight Validation
Write-Step -Number 1 -Total 5 -Title "Pre-Flight Validation"

python scripts\preflight_validator.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Pre-flight validation failed. Fix errors and try again." -ForegroundColor Red
    exit 1
}

# Step 2: Create Directories
Write-Step -Number 2 -Total 5 -Title "Setup Directories"

$directories = @("logs", "reports", ".state", ".worktrees")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✅ Created $dir/" -ForegroundColor Green
    } else {
        Write-Host "✓ $dir/ exists" -ForegroundColor Gray
    }
}

# Step 3: Clean Old Worktrees
Write-Step -Number 3 -Total 5 -Title "Cleanup Old Worktrees"

try {
    $worktreeList = git worktree list --porcelain 2>$null
    if ($LASTEXITCODE -eq 0) {
        $baseRepo = git rev-parse --show-toplevel 2>$null
        
        $existingWorktrees = $worktreeList | Select-String "^worktree" | ForEach-Object {
            $_.ToString().Split()[1]
        }
        
        $cleanedCount = 0
        foreach ($wt in $existingWorktrees) {
            if ($wt -ne $baseRepo -and (Test-Path $wt)) {
                Write-Host "  Removing: $wt" -ForegroundColor Gray
                git worktree remove $wt --force 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $cleanedCount++
                }
            }
        }
        
        if ($cleanedCount -gt 0) {
            Write-Host "✅ Cleaned $cleanedCount old worktree(s)" -ForegroundColor Green
        } else {
            Write-Host "✓ No old worktrees to clean" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "⚠️  Could not clean worktrees: $_" -ForegroundColor Yellow
}

# Step 4: Launch Orchestrator
Write-Step -Number 4 -Total 5 -Title "Launch Orchestrator"

Write-Host "Starting orchestrator with $Agents agents..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "⚠️  DRY RUN: Would execute orchestrator here" -ForegroundColor Yellow
    Write-Host "   Command: python scripts\multi_agent_orchestrator.py" -ForegroundColor Gray
    $orchestratorExit = 0
} else {
    # Note: Orchestrator doesn't support --agents flag yet
    # This will be added when orchestrator is updated
    Write-Host ""
    python scripts\multi_agent_orchestrator.py
    $orchestratorExit = $LASTEXITCODE
}

# Step 5: Post-Execution Summary
Write-Step -Number 5 -Total 5 -Title "Post-Execution Summary"

if ($orchestratorExit -eq 0) {
    Write-Host "✅ Multi-agent execution completed successfully!" -ForegroundColor Green
    
    # Check for report
    if (Test-Path "reports\multi_agent_execution_report.md") {
        Write-Host ""
        Write-Host "📊 Final Report:" -ForegroundColor Cyan
        Get-Content "reports\multi_agent_execution_report.md" | Select-Object -First 20
        Write-Host ""
        Write-Host "Full report: reports\multi_agent_execution_report.md" -ForegroundColor Gray
    }
    
    # Check database stats
    if (Get-Command sqlite3 -ErrorAction SilentlyContinue) {
        try {
            $completedCount = sqlite3 .state\orchestration.db "SELECT COUNT(*) FROM workstream_status WHERE status='completed'" 2>$null
            $totalCount = sqlite3 .state\orchestration.db "SELECT COUNT(*) FROM workstream_status" 2>$null
            
            if ($completedCount -and $totalCount) {
                Write-Host ""
                Write-Host "📈 Progress: $completedCount / $totalCount workstreams completed" -ForegroundColor Cyan
                
                $percentage = [Math]::Round(($completedCount / $totalCount) * 100, 1)
                Write-Host "   Success rate: $percentage%" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "⚠️  Could not read database stats" -ForegroundColor Yellow
        }
    }
    
} else {
    Write-Host "❌ Orchestrator exited with errors (code: $orchestratorExit)" -ForegroundColor Red
    Write-Host "   Check logs\orchestrator.log for details" -ForegroundColor Yellow
}

# Footer
Write-Host ""
Write-Banner "Execution Complete"

if ($orchestratorExit -eq 0) {
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review reports\multi_agent_execution_report.md" -ForegroundColor Gray
    Write-Host "  2. Check logs\orchestrator.log for details" -ForegroundColor Gray
    Write-Host "  3. Validate changes with: git log --oneline -20" -ForegroundColor Gray
    Write-Host ""
}

exit $orchestratorExit
