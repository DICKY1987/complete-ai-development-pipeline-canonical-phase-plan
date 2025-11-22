<#
.SYNOPSIS
    Migrates development process documentation from docs/ to devdocs/

.DESCRIPTION
    Moves phase plans, completion reports, execution summaries, and analysis
    documents from docs/ to their proper locations in devdocs/ according to
    the File Organization System specification.

.PARAMETER DryRun
    Show what would be moved without actually moving files

.PARAMETER ShowDetails
    Show detailed output during migration

.EXAMPLE
    .\scripts\migrate_docs_to_devdocs.ps1 -DryRun
    Preview changes without executing

.EXAMPLE
    .\scripts\migrate_docs_to_devdocs.ps1
    Execute the migration
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$ShowDetails
)

$ErrorActionPreference = "Stop"

# Get repository root
$repoRoot = Split-Path $PSScriptRoot -Parent
$docsDir = Join-Path $repoRoot "docs"
$devdocsDir = Join-Path $repoRoot "devdocs"

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Documentation Migration: docs/ → devdocs/" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be moved" -ForegroundColor Yellow
    Write-Host ""
}

# Migration mappings
$migrations = @(
    # ========================================
    # PHASE PLANS & COMPLETION REPORTS
    # ========================================
    @{
        Category = "AIM Phase Completion Reports"
        Moves = @(
            @{ From = "AIM_PLUS_INTEGRATION_PLAN.md"; To = "execution\AIM_PLUS_INTEGRATION_PLAN.md" }
            @{ From = "AIM_PLUS_PHASE_1AB_COMPLETE.md"; To = "phases\aim\PHASE_1AB_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_1C_COMPLETE.md"; To = "phases\aim\PHASE_1C_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_2A_COMPLETE.md"; To = "phases\aim\PHASE_2A_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_2B_COMPLETE.md"; To = "phases\aim\PHASE_2B_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_3A_COMPLETE.md"; To = "phases\aim\PHASE_3A_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_3B_COMPLETE.md"; To = "phases\aim\PHASE_3B_COMPLETE.md" }
            @{ From = "AIM_PLUS_PHASE_4_COMPLETE.md"; To = "phases\aim\PHASE_4_COMPLETE.md" }
            @{ From = "AIM_PLUS_PROGRESS_SUMMARY.md"; To = "execution\AIM_PLUS_PROGRESS_SUMMARY.md" }
            @{ From = "AIM_PLUS_FINAL_REPORT.md"; To = "execution\AIM_PLUS_FINAL_REPORT.md" }
            @{ From = "AIM_PLUS_FINAL_SUMMARY.md"; To = "execution\AIM_PLUS_FINAL_SUMMARY.md" }
        )
    },
    @{
        Category = "Phase K Documentation Enhancement"
        Moves = @(
            @{ From = "PHASE_K_DOCUMENTATION_ENHANCEMENT_PLAN.md"; To = "phases\phase-k\PLAN.md" }
            @{ From = "PHASE_K1_COMPLETE.md"; To = "phases\phase-k\K1_COMPLETE.md" }
            @{ From = "PHASE_K2_COMPLETE.md"; To = "phases\phase-k\K2_COMPLETE.md" }
            @{ From = "PHASE_K_ENHANCEMENT_RECOMMENDATIONS.md"; To = "phases\phase-k\RECOMMENDATIONS.md" }
        )
    },
    @{
        Category = "UET Integration (Phase H)"
        Moves = @(
            @{ From = "UET_INTEGRATION_PLAN.md"; To = "phases\phase-h\UET_INTEGRATION_PLAN.md" }
            @{ From = "UET_WEEK1_IMPLEMENTATION.md"; To = "phases\phase-h\WEEK1_IMPLEMENTATION.md" }
            @{ From = "UET_IMPLEMENTATION_COMPLETE.md"; To = "phases\phase-h\COMPLETE.md" }
            @{ From = "UET_PROGRESS_TRACKER.md"; To = "execution\UET_PROGRESS_TRACKER.md" }
            @{ From = "UET_INTEGRATION_SUMMARY.md"; To = "execution\UET_INTEGRATION_SUMMARY.md" }
        )
    },
    @{
        Category = "General Phase Planning"
        Moves = @(
            @{ From = "PHASE_PLAN.md"; To = "planning\PHASE_PLAN.md" }
            @{ From = "PHASE_ROADMAP.md"; To = "planning\PHASE_ROADMAP.md" }
        )
    },
    
    # ========================================
    # EXECUTION SUMMARIES & STATUS
    # ========================================
    @{
        Category = "Implementation Summaries"
        Moves = @(
            @{ From = "COMPLETE_IMPLEMENTATION_SUMMARY.md"; To = "execution\COMPLETE_IMPLEMENTATION_SUMMARY.md" }
            @{ From = "ENGINE_STATUS.md"; To = "execution\ENGINE_STATUS.md" }
            @{ From = "FILE_ORGANIZATION_IMPLEMENTATION_SUMMARY.md"; To = "execution\FILE_ORG_IMPLEMENTATION_SUMMARY.md" }
            @{ From = "phase-github-issues-resolution.md"; To = "execution\GITHUB_ISSUES_RESOLUTION.md" }
        )
    },
    
    # ========================================
    # ANALYSIS REPORTS
    # ========================================
    @{
        Category = "Analysis & Assessment"
        Moves = @(
            @{ From = "CORE_DUPLICATE_ANALYSIS.md"; To = "analysis\CORE_DUPLICATE_ANALYSIS.md" }
            @{ From = "LEGACY_ARCHIVE_CANDIDATES.md"; To = "analysis\LEGACY_ARCHIVE_CANDIDATES.md" }
            @{ From = "SPEC_CONSOLIDATION_INVENTORY.md"; To = "analysis\SPEC_CONSOLIDATION_INVENTORY.md" }
            @{ From = "USER_PROCESS_UNDERSTANDING_ASSESSMENT.md"; To = "analysis\USER_PROCESS_ASSESSMENT.md" }
            @{ From = "AI_CODEBASE_STRUCTURE_FEASIBILITY.md"; To = "analysis\AI_CODEBASE_STRUCTURE_FEASIBILITY.md" }
        )
    },
    
    # ========================================
    # PLANNING ARTIFACTS
    # ========================================
    @{
        Category = "Planning Documents"
        Moves = @(
            @{ From = "DEPRECATION_PLAN.md"; To = "planning\DEPRECATION_PLAN.md" }
            @{ From = "FILE_ORGANIZATION_VISUAL.md"; To = "planning\FILE_ORG_VISUAL.md" }
            @{ From = "file-lifecycle-diagram.md"; To = "planning\file-lifecycle-diagram.md" }
        )
    },
    
    # ========================================
    # ARCHIVE
    # ========================================
    @{
        Category = "Archive (2025-11)"
        Moves = @(
            @{ From = "ARCHIVE_2025-11-22_SUMMARY.md"; To = "archive\2025-11\ARCHIVE_SUMMARY.md" }
            @{ From = "DOCUMENTATION_INDEX_OLD.md"; To = "archive\2025-11\DOCUMENTATION_INDEX_OLD.md" }
        )
    }
)

# Files to delete (stale auto-generated)
$filesToDelete = @(
    "DOCUMENTATION_INDEX_AUTO.md",
    "DOCUMENTATION_INDEX_GENERATED.md",
    "IMPLEMENTATION_LOCATIONS_AUTO.md"
)

# Statistics
$totalMoves = 0
$totalDeletes = 0
$errors = @()

# Function to ensure target directory exists
function Ensure-Directory {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would create directory: $Path" -ForegroundColor DarkGray
        } else {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            if ($ShowDetails) {
                Write-Host "  ✓ Created directory: $Path" -ForegroundColor DarkGray
            }
        }
    }
}

# Function to move file with Git
function Move-FileWithGit {
    param(
        [string]$FromPath,
        [string]$ToPath
    )
    
    $fromRel = $FromPath.Replace($repoRoot + "\", "")
    $toRel = $ToPath.Replace($repoRoot + "\", "")
    
    if (-not (Test-Path $FromPath)) {
        $script:errors += "Source not found: $fromRel"
        Write-Host "  ✗ Source not found: $fromRel" -ForegroundColor Red
        return $false
    }
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would move: $fromRel → $toRel" -ForegroundColor DarkGray
        return $true
    }
    
    try {
        # Ensure target directory exists
        $targetDir = Split-Path $ToPath -Parent
        Ensure-Directory $targetDir
        
        # Use git mv for proper history tracking
        $gitOutput = git mv $FromPath $ToPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Moved: $fromRel" -ForegroundColor Green
            if ($ShowDetails) {
                Write-Host "      → $toRel" -ForegroundColor DarkGray
            }
            return $true
        } else {
            $script:errors += "Git mv failed: $fromRel - $gitOutput"
            Write-Host "  ✗ Failed: $fromRel - $gitOutput" -ForegroundColor Red
            return $false
        }
    } catch {
        $script:errors += "Exception moving $fromRel : $_"
        Write-Host "  ✗ Error: $fromRel - $_" -ForegroundColor Red
        return $false
    }
}

# Function to delete file with Git
function Remove-FileWithGit {
    param([string]$Path)
    
    $relPath = $Path.Replace($repoRoot + "\", "")
    
    if (-not (Test-Path $Path)) {
        Write-Host "  ⊘ Already removed: $relPath" -ForegroundColor DarkGray
        return $true
    }
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would delete: $relPath" -ForegroundColor DarkGray
        return $true
    }
    
    try {
        $gitOutput = git rm $Path 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Deleted: $relPath" -ForegroundColor Yellow
            return $true
        } else {
            $script:errors += "Git rm failed: $relPath - $gitOutput"
            Write-Host "  ✗ Failed to delete: $relPath - $gitOutput" -ForegroundColor Red
            return $false
        }
    } catch {
        $script:errors += "Exception deleting $relPath : $_"
        Write-Host "  ✗ Error deleting: $relPath - $_" -ForegroundColor Red
        return $false
    }
}

# ========================================
# EXECUTE MIGRATIONS
# ========================================

Write-Host "📦 Processing Migrations..." -ForegroundColor Cyan
Write-Host ""

foreach ($migration in $migrations) {
    Write-Host "▶ $($migration.Category)" -ForegroundColor Blue
    
    foreach ($move in $migration.Moves) {
        $sourcePath = Join-Path $docsDir $move.From
        $targetPath = Join-Path $devdocsDir $move.To
        
        if (Move-FileWithGit -FromPath $sourcePath -ToPath $targetPath) {
            $totalMoves++
        }
    }
    
    Write-Host ""
}

# ========================================
# DELETE STALE FILES
# ========================================

Write-Host "🗑️  Removing Stale Files..." -ForegroundColor Cyan
Write-Host ""

foreach ($file in $filesToDelete) {
    $filePath = Join-Path $docsDir $file
    
    if (Remove-FileWithGit -Path $filePath) {
        $totalDeletes++
    }
}

Write-Host ""

# ========================================
# SUMMARY
# ========================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Migration Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN RESULTS:" -ForegroundColor Yellow
} else {
    Write-Host "✅ MIGRATION COMPLETE:" -ForegroundColor Green
}

Write-Host "   Files moved:   $totalMoves" -ForegroundColor White
Write-Host "   Files deleted: $totalDeletes" -ForegroundColor White
Write-Host "   Errors:        $($errors.Count)" -ForegroundColor $(if ($errors.Count -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "⚠️  ERRORS ENCOUNTERED:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   • $error" -ForegroundColor Red
    }
    Write-Host ""
}

if (-not $DryRun -and $errors.Count -eq 0) {
    Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Review changes: git status" -ForegroundColor White
    Write-Host "   2. Commit migration: git commit -m 'docs: migrate dev artifacts to devdocs/'" -ForegroundColor White
    Write-Host "   3. Update any broken links in remaining docs/" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 TIP: Run 'git log --follow <file>' to verify history is preserved" -ForegroundColor DarkGray
    Write-Host ""
}

if ($DryRun) {
    Write-Host "To execute migration, run without -DryRun flag" -ForegroundColor Yellow
    Write-Host ""
}

# Exit with error code if there were failures
if ($errors.Count -gt 0) {
    exit 1
}

exit 0
