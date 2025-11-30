# DOC_LINK: DOC-SCRIPT-CONSOLIDATE-ARCHIVES-058
# Archive Consolidation Script
# Consolidates all scattered archive folders into one centralized location
# Date: 2025-11-26

$ErrorActionPreference = "Stop"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Archive Consolidation Script" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Define the consolidation mappings
$timestamp = "2025-11-26"
$targetBase = "archive"

$archiveMappings = @(
    @{
        Source = "archive"
        Target = "$targetBase/${timestamp}_root_archive"
        Description = "Root archive folder"
    },
    @{
        Source = "developer\archive"
        Target = "$targetBase/${timestamp}_developer"
        Description = "Developer archive"
    },
    @{
        Source = "docs\archive"
        Target = "$targetBase/${timestamp}_docs"
        Description = "Documentation archive"
    },
    @{
        Source = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\archive"
        Target = "$targetBase/${timestamp}_uet_root"
        Description = "UET root archive"
    },
    @{
        Source = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\specs\archive"
        Target = "$targetBase/${timestamp}_uet_specs"
        Description = "UET specs archive"
    },
    @{
        Source = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\archive"
        Target = "$targetBase/${timestamp}_uet_patches"
        Description = "UET patches archive"
    },
    @{
        Source = "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive"
        Target = "$targetBase/${timestamp}_uet_meta"
        Description = "UET meta archive"
    }
)

Write-Host "Consolidation Plan:" -ForegroundColor Yellow
Write-Host ""
foreach ($mapping in $archiveMappings) {
    Write-Host "  $($mapping.Description)" -ForegroundColor Cyan
    Write-Host "    FROM: $($mapping.Source)"
    Write-Host "    TO:   $($mapping.Target)"
    
    if (Test-Path $mapping.Source) {
        $fileCount = (Get-ChildItem -Path $mapping.Source -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "    Files: $fileCount" -ForegroundColor Green
    } else {
        Write-Host "    Status: NOT FOUND (will skip)" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "=" * 70 -ForegroundColor Cyan
Read-Host "Press Enter to proceed with consolidation (Ctrl+C to cancel)"

# First, we need to handle the root 'archive' folder specially
# We'll create a temporary name first
Write-Host "`nStep 1: Creating temporary structure..." -ForegroundColor Cyan

$tempArchive = "archive_temp_consolidation"
New-Item -ItemType Directory -Path $tempArchive -Force | Out-Null

# Process each archive folder
$processedCount = 0
$skippedCount = 0

foreach ($mapping in $archiveMappings) {
    Write-Host "`nProcessing: $($mapping.Description)" -ForegroundColor Yellow
    
    if (-not (Test-Path $mapping.Source)) {
        Write-Host "  ⚠️  Source not found, skipping" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    $fileCount = (Get-ChildItem -Path $mapping.Source -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    
    if ($fileCount -eq 0) {
        Write-Host "  ⚠️  Empty folder, skipping" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    # For root archive, we need special handling
    if ($mapping.Source -eq "archive") {
        $tempTarget = "$tempArchive\${timestamp}_root_archive"
        New-Item -ItemType Directory -Path $tempTarget -Force | Out-Null
        
        # Move contents (not the folder itself)
        Get-ChildItem -Path $mapping.Source -Recurse | ForEach-Object {
            $targetPath = $_.FullName.Replace((Resolve-Path $mapping.Source).Path, (Resolve-Path $tempTarget).Path)
            $targetDir = Split-Path $targetPath -Parent
            
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            if ($_.PSIsContainer -eq $false) {
                Copy-Item -Path $_.FullName -Destination $targetPath -Force
            }
        }
        
        Write-Host "  ✅ Copied $fileCount files to temporary location" -ForegroundColor Green
    } else {
        # For other archives, just move to temp
        $targetInTemp = "$tempArchive\$(Split-Path $mapping.Target -Leaf)"
        
        if (Test-Path $mapping.Source) {
            Copy-Item -Path $mapping.Source -Destination $targetInTemp -Recurse -Force
            Write-Host "  ✅ Copied $fileCount files to temporary location" -ForegroundColor Green
        }
    }
    
    $processedCount++
}

Write-Host "`nStep 2: Cleaning up old archive folders..." -ForegroundColor Cyan

foreach ($mapping in $archiveMappings) {
    if ((Test-Path $mapping.Source) -and $mapping.Source -ne "archive") {
        Remove-Item -Path $mapping.Source -Recurse -Force
        Write-Host "  ✅ Removed: $($mapping.Source)" -ForegroundColor Green
    }
}

# Clear the root archive folder contents (but not the folder itself)
if (Test-Path "archive") {
    Get-ChildItem -Path "archive" -Recurse | Remove-Item -Recurse -Force
    Write-Host "  ✅ Cleared: archive/" -ForegroundColor Green
}

Write-Host "`nStep 3: Moving consolidated archives to final location..." -ForegroundColor Cyan

# Move everything from temp to final archive location
Get-ChildItem -Path $tempArchive | ForEach-Object {
    $destination = "archive\$($_.Name)"
    Move-Item -Path $_.FullName -Destination $destination -Force
    Write-Host "  ✅ Moved: $($_.Name)" -ForegroundColor Green
}

# Remove temp folder
Remove-Item -Path $tempArchive -Force

Write-Host "`nStep 4: Creating consolidation manifest..." -ForegroundColor Cyan

$manifest = @"
# Archive Consolidation Manifest
Date: $timestamp
Consolidated by: Archive Consolidation Script

## Summary
Total archive folders consolidated: $processedCount
Skipped (empty or not found): $skippedCount

## Consolidation Details

"@

foreach ($mapping in $archiveMappings) {
    if (Test-Path "archive\$(Split-Path $mapping.Target -Leaf)") {
        $fileCount = (Get-ChildItem -Path "archive\$(Split-Path $mapping.Target -Leaf)" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        $manifest += @"

### $($mapping.Description)
- Original Location: ``$($mapping.Source)``
- New Location: ``$($mapping.Target)``
- Files Archived: $fileCount

"@
    }
}

$manifest | Out-File -FilePath "archive\CONSOLIDATION_MANIFEST.md" -Encoding UTF8

Write-Host "  ✅ Created: archive\CONSOLIDATION_MANIFEST.md" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ ARCHIVE CONSOLIDATION COMPLETE" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  Processed: $processedCount folders"
Write-Host "  Skipped: $skippedCount folders"
Write-Host "  Location: archive/"
Write-Host ""
Write-Host "All archives are now in: archive/" -ForegroundColor Green
Write-Host "Manifest created: archive\CONSOLIDATION_MANIFEST.md" -ForegroundColor Green
Write-Host ""
