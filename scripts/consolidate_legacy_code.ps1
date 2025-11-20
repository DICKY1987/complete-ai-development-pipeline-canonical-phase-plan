# Legacy Code Consolidation Script
# Moves all shims/deprecated code to _DEPRECATED/ directory

$baseDir = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
$deprecatedDir = Join-Path $baseDir "_DEPRECATED"

# Create target structure
New-Item -Path $deprecatedDir -ItemType Directory -Force | Out-Null
New-Item -Path "$deprecatedDir\core_shims" -ItemType Directory -Force | Out-Null
New-Item -Path "$deprecatedDir\error_shims" -ItemType Directory -Force | Out-Null

Write-Host "=== LEGACY CODE CONSOLIDATION ===" -ForegroundColor Cyan
Write-Host ""

# Move entire src/ directory
Write-Host "[1/3] Moving src/ directory..." -ForegroundColor Yellow
if (Test-Path "$baseDir\src") {
    Move-Item -Path "$baseDir\src" -Destination "$deprecatedDir\src" -Force
    Write-Host "  ✓ Moved src/ → _DEPRECATED/src/" -ForegroundColor Green
}

# Move core shims
Write-Host "[2/3] Moving core shims..." -ForegroundColor Yellow
$coreShims = @("aim_bridge.py", "bundles.py", "crud_operations.py", "db.py", "db_sqlite.py", "worktree.py")
foreach ($file in $coreShims) {
    $source = Join-Path $baseDir "core\$file"
    if (Test-Path $source) {
        $content = Get-Content $source -Raw
        if ($content -match "Compatibility Shim|backward compatibility") {
            Move-Item -Path $source -Destination "$deprecatedDir\core_shims\$file" -Force
            Write-Host "  ✓ Moved core/$file" -ForegroundColor Green
        }
    }
}

# Move error shims
Write-Host "[3/3] Moving error shims..." -ForegroundColor Yellow
$errorShims = @("file_hash_cache.py", "pipeline_engine.py", "plugin_manager.py")
foreach ($file in $errorShims) {
    $source = Join-Path $baseDir "error\$file"
    if (Test-Path $source) {
        $content = Get-Content $source -Raw
        if ($content -match "Compatibility Shim|backward compatibility") {
            Move-Item -Path $source -Destination "$deprecatedDir\error_shims\$file" -Force
            Write-Host "  ✓ Moved error/$file" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "=== MIGRATION COMPLETE ===" -ForegroundColor Cyan
Write-Host "All legacy code moved to: $deprecatedDir" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Run tests to verify nothing breaks: pytest -q" -ForegroundColor White
Write-Host "2. Update import paths if needed" -ForegroundColor White
Write-Host "3. Review _DEPRECATED/ and delete when confirmed unused" -ForegroundColor White
