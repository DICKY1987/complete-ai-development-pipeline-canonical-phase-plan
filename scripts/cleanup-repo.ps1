<#
.SYNOPSIS
    Consolidated cleanup script for repository maintenance

.DESCRIPTION
    Unified script replacing cleanup-planning-docs.ps1, cleanup-root-docs.ps1,
    and cleanup-root-planning-docs.ps1

.PARAMETER Target
    Cleanup target: 'planning', 'root', 'all'

.PARAMETER WhatIf
    Show what would be cleaned without making changes

.EXAMPLE
    .\cleanup-repo.ps1 -Target planning
    .\cleanup-repo.ps1 -Target all -WhatIf
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('planning', 'root', 'all')]
    [string]$Target,

    [switch]$WhatIf
)

function Remove-PlanningDocs {
    param([switch]$WhatIf)

    Write-Host "Cleaning planning docs..." -ForegroundColor Cyan

    $patterns = @('*_PLAN.md', '*_PLANNING.md', 'PLAN_*.md')
    foreach ($pattern in $patterns) {
        Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
            if ($WhatIf) {
                Write-Host "  [WhatIf] Would remove: $($_.Name)"
            } else {
                Remove-Item $_.FullName -Force
                Write-Host "  ✓ Removed: $($_.Name)"
            }
        }
    }
}

function Remove-RootClutter {
    param([switch]$WhatIf)

    Write-Host "Cleaning root directory clutter..." -ForegroundColor Cyan

    # Remove temp files
    $tempPatterns = @('*.tmp', '*.bak', '*.backup', 'nul')
    foreach ($pattern in $tempPatterns) {
        Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
            if ($WhatIf) {
                Write-Host "  [WhatIf] Would remove: $($_.Name)"
            } else {
                Remove-Item $_.FullName -Force
                Write-Host "  ✓ Removed: $($_.Name)"
            }
        }
    }

    # Remove .pyc files
    Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | ForEach-Object {
        if ($WhatIf) {
            Write-Host "  [WhatIf] Would remove: $($_.FullName)"
        } else {
            Remove-Item $_.FullName -Force
            Write-Host "  ✓ Removed: $($_.FullName)"
        }
    }
}

# Execute based on target
switch ($Target) {
    'planning' { Remove-PlanningDocs -WhatIf:$WhatIf }
    'root' { Remove-RootClutter -WhatIf:$WhatIf }
    'all' {
        Remove-PlanningDocs -WhatIf:$WhatIf
        Remove-RootClutter -WhatIf:$WhatIf
    }
}

Write-Host "`n✓ Cleanup complete!" -ForegroundColor Green
