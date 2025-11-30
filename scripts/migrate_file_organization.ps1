# DOC_LINK: DOC-SCRIPT-MIGRATE-FILE-ORGANIZATION-065
# File Organization Migration Script
# Purpose: Migrate files from current mixed structure to organized devdocs/ structure
# Usage: Run interactively or with -WhatIf to preview changes

[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('All', 'Phases', 'Sessions', 'Execution', 'Analysis', 'Handoffs', 'Archive')]
    [string]$Category = 'All',
    [switch]$CreateStructureOnly
)

$ErrorActionPreference = 'Stop'

# Root directory - go up one level from scripts folder
$root = Split-Path -Parent $PSScriptRoot

Write-Host "File Organization Migration Script" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Step 1: Create devdocs structure
function New-DevDocsStructure {
    Write-Host "[1/7] Creating devdocs/ directory structure..." -ForegroundColor Yellow
    
    $directories = @(
        "devdocs",
        "devdocs\phases",
        "devdocs\sessions",
        "devdocs\execution",
        "devdocs\planning",
        "devdocs\analysis",
        "devdocs\handoffs",
        "devdocs\archive",
        "devdocs\meta"
    )
    
    foreach ($dir in $directories) {
        $path = Join-Path $root $dir
        if (-not (Test-Path $path)) {
            if ($PSCmdlet.ShouldProcess($path, "Create directory")) {
                New-Item -ItemType Directory -Path $path -Force | Out-Null
                Write-Host "  ✅ Created: $dir" -ForegroundColor Green
            }
        } else {
            Write-Host "  ℹ️  Exists: $dir" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
}

# Step 2: Migrate phase documentation
function Move-PhaseDocumentation {
    if ($Category -ne 'All' -and $Category -ne 'Phases') { return }
    
    Write-Host "[2/7] Migrating phase documentation..." -ForegroundColor Yellow
    
    # Find all PHASE_*.md files in docs/
    $phaseFiles = Get-ChildItem -Path (Join-Path $root "docs") -Filter "PHASE_*.md" -ErrorAction SilentlyContinue
    
    $phaseMap = @{}
    
    foreach ($file in $phaseFiles) {
        # Extract phase ID (e.g., PHASE_I_PLAN.md -> I)
        if ($file.Name -match "PHASE_([A-Z0-9]+)_(.+)\.md") {
            $phaseId = $matches[1].ToLower()
            $docType = $matches[2]
            
            # Determine new filename
            $newName = switch ($docType) {
                "PLAN" { "PLAN.md" }
                "COMPLETE" { "COMPLETE.md" }
                { $_ -like "*EXECUTION*SUMMARY*" } { "EXECUTION_SUMMARY.md" }
                { $_ -like "*PROGRESS*" } { "PROGRESS.md" }
                { $_ -like "*CHECKLIST*" } { "CHECKLIST.md" }
                default { "$docType.md" }
            }
            
            # Create phase directory
            $phaseDir = Join-Path (Join-Path $root "devdocs\phases") "phase-$phaseId"
            if (-not (Test-Path $phaseDir)) {
                if ($PSCmdlet.ShouldProcess($phaseDir, "Create phase directory")) {
                    New-Item -ItemType Directory -Path $phaseDir -Force | Out-Null
                }
            }
            
            # Move file
            $destination = Join-Path $phaseDir $newName
            if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                Move-Item -Path $file.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($file.Name) → devdocs\phases\phase-$phaseId\$newName" -ForegroundColor Green
            }
        }
    }
    
    Write-Host ""
}

# Step 3: Migrate session logs
function Move-SessionLogs {
    if ($Category -ne 'All' -and $Category -ne 'Sessions') { return }
    
    Write-Host "[3/7] Migrating session logs..." -ForegroundColor Yellow
    
    # Define source directories and their target subdirs
    $sessionSources = @(
        @{ Path = "docs\sessions"; Target = "" },
        @{ Path = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"; Target = "uet"; Filter = "SESSION_*.md" },
        @{ Path = "PROCESS_DEEP_DIVE_OPTOMIZE\session_reports"; Target = "process-deep-dive" },
        @{ Path = "AGENTIC_DEV_PROTOTYPE"; Target = "agentic-proto"; Filter = "SESSION_*.md" }
    )
    
    foreach ($source in $sessionSources) {
        $sourcePath = Join-Path $root $source.Path
        if (-not (Test-Path $sourcePath)) { continue }
        
        # Determine target directory
        $targetBase = Join-Path $root "devdocs\sessions"
        $targetPath = if ($source.Target) {
            $t = Join-Path $targetBase $source.Target
            if (-not (Test-Path $t)) {
                if ($PSCmdlet.ShouldProcess($t, "Create session subdirectory")) {
                    New-Item -ItemType Directory -Path $t -Force | Out-Null
                }
            }
            $t
        } else {
            $targetBase
        }
        
        # Get files
        $filter = if ($source.Filter) { $source.Filter } else { "SESSION_*.md" }
        $files = Get-ChildItem -Path $sourcePath -Filter $filter -File -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            $destination = Join-Path $targetPath $file.Name
            if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                Move-Item -Path $file.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($file.Name) → devdocs\sessions\$($source.Target)" -ForegroundColor Green
            }
        }
    }
    
    Write-Host ""
}

# Step 4: Migrate execution summaries and progress reports
function Move-ExecutionDocuments {
    if ($Category -ne 'All' -and $Category -ne 'Execution') { return }
    
    Write-Host "[4/7] Migrating execution summaries and progress reports..." -ForegroundColor Yellow
    
    $patterns = @(
        "*_EXECUTION_SUMMARY.md",
        "*_PROGRESS.md",
        "*_PROGRESS_REPORT.md",
        "*_COMPLETION*.md"
    )
    
    $sourceDirs = @(
        "docs",
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK",
        "error"
    )
    
    foreach ($sourceDir in $sourceDirs) {
        $sourcePath = Join-Path $root $sourceDir
        if (-not (Test-Path $sourcePath)) { continue }
        
        foreach ($pattern in $patterns) {
            $files = Get-ChildItem -Path $sourcePath -Filter $pattern -File -ErrorAction SilentlyContinue
            
            foreach ($file in $files) {
                # Skip if already handled by phase migration
                if ($file.Name -match "^PHASE_[A-Z0-9]+_") { continue }
                
                $destination = Join-Path (Join-Path $root "devdocs\execution") $file.Name
                if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                    Move-Item -Path $file.FullName -Destination $destination -Force
                    Write-Host "  ✅ Moved: $($file.Name) → devdocs\execution\" -ForegroundColor Green
                }
            }
        }
    }
    
    Write-Host ""
}

# Step 5: Migrate analysis reports
function Move-AnalysisReports {
    if ($Category -ne 'All' -and $Category -ne 'Analysis') { return }
    
    Write-Host "[5/7] Migrating analysis reports..." -ForegroundColor Yellow
    
    # Create subdirectories
    $analysisSubdirs = @("process-deep-dive", "agentic-proto")
    foreach ($subdir in $analysisSubdirs) {
        $path = Join-Path (Join-Path $root "devdocs\analysis") $subdir
        if (-not (Test-Path $path)) {
            if ($PSCmdlet.ShouldProcess($path, "Create analysis subdirectory")) {
                New-Item -ItemType Directory -Path $path -Force | Out-Null
            }
        }
    }
    
    # Migrate from docs/analysis/
    $docsAnalysisPath = Join-Path $root "docs\analysis"
    if (Test-Path $docsAnalysisPath) {
        $files = Get-ChildItem -Path $docsAnalysisPath -Filter "*.md" -File -Recurse
        foreach ($file in $files) {
            $destination = Join-Path (Join-Path $root "devdocs\analysis") $file.Name
            if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                Move-Item -Path $file.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($file.Name) → devdocs\analysis\" -ForegroundColor Green
            }
        }
    }
    
    # Migrate METRICS_SUMMARY_*.md from various locations
    $metricsSources = @(
        "PROCESS_DEEP_DIVE_OPTOMIZE\reports",
        "AGENTIC_DEV_PROTOTYPE\analytics\reports"
    )
    
    foreach ($source in $metricsSources) {
        $sourcePath = Join-Path $root $source
        if (-not (Test-Path $sourcePath)) { continue }
        
        $files = Get-ChildItem -Path $sourcePath -Filter "METRICS_SUMMARY_*.md" -File -ErrorAction SilentlyContinue
        $targetDir = if ($source -like "*PROCESS_DEEP_DIVE*") { "process-deep-dive" } else { "agentic-proto" }
        
        foreach ($file in $files) {
            $destination = Join-Path (Join-Path (Join-Path $root "devdocs\analysis") $targetDir) $file.Name
            if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                Move-Item -Path $file.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($file.Name) → devdocs\analysis\$targetDir\" -ForegroundColor Green
            }
        }
    }
    
    Write-Host ""
}

# Step 6: Migrate handoff documents
function Move-HandoffDocuments {
    if ($Category -ne 'All' -and $Category -ne 'Handoffs') { return }
    
    Write-Host "[6/7] Migrating handoff documents..." -ForegroundColor Yellow
    
    $sourceDirs = @(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK",
        "docs"
    )
    
    foreach ($sourceDir in $sourceDirs) {
        $sourcePath = Join-Path $root $sourceDir
        if (-not (Test-Path $sourcePath)) { continue }
        
        $files = Get-ChildItem -Path $sourcePath -Filter "HANDOFF*.md" -File -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            $destination = Join-Path (Join-Path $root "devdocs\handoffs") $file.Name
            if ($PSCmdlet.ShouldProcess($file.FullName, "Move to $destination")) {
                Move-Item -Path $file.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($file.Name) → devdocs\handoffs\" -ForegroundColor Green
            }
        }
    }
    
    Write-Host ""
}

# Step 7: Move completed work to archive
function Move-ToArchive {
    if ($Category -ne 'All' -and $Category -ne 'Archive') { return }
    
    Write-Host "[7/7] Moving completed work to archive..." -ForegroundColor Yellow
    
    # Create 2025-11 archive directory
    $archiveDir = Join-Path (Join-Path $root "devdocs\archive") "2025-11"
    if (-not (Test-Path $archiveDir)) {
        if ($PSCmdlet.ShouldProcess($archiveDir, "Create archive directory")) {
            New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
        }
    }
    
    # Move docs/archive/ contents
    $docsArchivePath = Join-Path $root "docs\archive"
    if (Test-Path $docsArchivePath) {
        $items = Get-ChildItem -Path $docsArchivePath
        foreach ($item in $items) {
            $destination = Join-Path $archiveDir $item.Name
            if ($PSCmdlet.ShouldProcess($item.FullName, "Move to $destination")) {
                Move-Item -Path $item.FullName -Destination $destination -Force
                Write-Host "  ✅ Moved: $($item.Name) → devdocs\archive\2025-11\" -ForegroundColor Green
            }
        }
    }
    
    Write-Host ""
}

# Main execution
try {
    New-DevDocsStructure
    
    if ($CreateStructureOnly) {
        Write-Host "✅ Directory structure created. Run without -CreateStructureOnly to migrate files.`n" -ForegroundColor Green
        exit 0
    }
    
    Move-PhaseDocumentation
    Move-SessionLogs
    Move-ExecutionDocuments
    Move-AnalysisReports
    Move-HandoffDocuments
    Move-ToArchive
    
    Write-Host "✅ Migration complete!`n" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review migrated files in devdocs/" -ForegroundColor White
    Write-Host "  2. Update any cross-references in documentation" -ForegroundColor White
    Write-Host "  3. Consider archiving temporary directories like PROCESS_DEEP_DIVE_OPTOMIZE/" -ForegroundColor White
    Write-Host "  4. Update build scripts to exclude devdocs/ from releases" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error during migration: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
