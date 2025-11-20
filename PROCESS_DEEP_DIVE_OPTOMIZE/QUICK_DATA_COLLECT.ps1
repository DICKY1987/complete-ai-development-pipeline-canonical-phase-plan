# Quick Data Collection Script
# Consolidates all development artifacts for analysis

param(
    [string]$SessionName = "session_$(Get-Date -Format 'yyyy-MM-dd_HHmm')"
)

Write-Host "🔍 Starting Data Collection: $SessionName" -ForegroundColor Cyan
Write-Host "=" * 60

$BaseDir = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
$SourceDir = "$BaseDir\pipeline_plus\AGENTIC_DEV_PROTOTYPE"
$DestDir = "$BaseDir\PROCESS_DEEP_DIVE_OPTOMIZE"

# Create session directory
$SessionDir = "$DestDir\raw_data\sessions\$SessionName"
New-Item -ItemType Directory -Path $SessionDir -Force | Out-Null

Write-Host "`n📊 1. Collecting Metrics..." -ForegroundColor Yellow
if (Test-Path "$SourceDir\scripts\collect_metrics.py") {
    cd $SourceDir
    python scripts\collect_metrics.py --output "$DestDir\metrics\development_metrics_$SessionName.json"
    Write-Host "   ✓ Metrics collected" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Metrics script not found" -ForegroundColor Red
}

Write-Host "`n📝 2. Copying Session Reports..." -ForegroundColor Yellow
Get-ChildItem -Path $SourceDir -Filter "SESSION*.md" | ForEach-Object {
    Copy-Item $_.FullName -Destination "$DestDir\session_reports\" -Force
    Write-Host "   ✓ Copied: $($_.Name)" -ForegroundColor Green
}

Write-Host "`n📋 3. Backing Up Specifications..." -ForegroundColor Yellow
if (Test-Path "$SourceDir\specs") {
    Copy-Item "$SourceDir\specs\*.json" -Destination "$SessionDir\specifications\" -Force -Recurse
    Write-Host "   ✓ Specifications backed up" -ForegroundColor Green
}

Write-Host "`n🔬 4. Exporting Git History..." -ForegroundColor Yellow
cd $SourceDir
$GitLogDir = "$DestDir\raw_data\git_logs"
New-Item -ItemType Directory -Path $GitLogDir -Force | Out-Null

git log --all --graph --pretty=format:'%h - %an, %ar : %s' > "$GitLogDir\git_history_$SessionName.txt"
git log --all --stat > "$GitLogDir\git_stats_$SessionName.txt"
git log --pretty=format: --name-only --diff-filter=A | Sort-Object | Get-Unique > "$GitLogDir\files_created_$SessionName.txt"
Write-Host "   ✓ Git history exported" -ForegroundColor Green

Write-Host "`n🧪 5. Collecting Test Results..." -ForegroundColor Yellow
if (Test-Path "$SourceDir\tests") {
    $TestResults = @()
    Get-ChildItem -Path "$SourceDir\tests" -Filter "test_*.py" | ForEach-Object {
        $TestResults += @{
            File = $_.Name
            Size = $_.Length
            Modified = $_.LastWriteTime
        }
    }
    $TestResults | ConvertTo-Json | Out-File "$SessionDir\test_inventory.json"
    Write-Host "   ✓ Test inventory created ($($TestResults.Count) files)" -ForegroundColor Green
}

Write-Host "`n📦 6. Archiving Source Code..." -ForegroundColor Yellow
if (Test-Path "$SourceDir\src") {
    Copy-Item "$SourceDir\src" -Destination "$SessionDir\src_snapshot" -Recurse -Force
    $SrcFiles = Get-ChildItem -Path "$SessionDir\src_snapshot" -Filter "*.py" -Recurse
    $TotalLOC = 0
    foreach ($file in $SrcFiles) {
        $TotalLOC += (Get-Content $file.FullName | Measure-Object -Line).Lines
    }
    Write-Host "   ✓ Source archived ($($SrcFiles.Count) files, $TotalLOC LOC)" -ForegroundColor Green
}

Write-Host "`n📊 7. Creating Session Manifest..." -ForegroundColor Yellow
$Manifest = @{
    session_name = $SessionName
    collected_at = Get-Date -Format "o"
    source_directory = $SourceDir
    destination_directory = $DestDir
    artifacts_collected = @{
        metrics = $true
        session_reports = $true
        specifications = $true
        git_history = $true
        test_results = $true
        source_code = $true
    }
    total_source_lines = $TotalLOC
    total_test_files = $TestResults.Count
}
$Manifest | ConvertTo-Json -Depth 5 | Out-File "$SessionDir\MANIFEST.json"
Write-Host "   ✓ Manifest created" -ForegroundColor Green

Write-Host "`n" + ("=" * 60)
Write-Host "✅ Data Collection Complete!" -ForegroundColor Green
Write-Host "`nSession Data Location:" -ForegroundColor Cyan
Write-Host "  $SessionDir"
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Review collected data in PROCESS_DEEP_DIVE_OPTOMIZE/"
Write-Host "  2. Run analysis scripts in analytics/"
Write-Host "  3. Generate insights report"
Write-Host "  4. Save terminal transcript manually (see TERMINAL_SESSION_GUIDE.md)"

Write-Host "`n📁 Quick Access:" -ForegroundColor Cyan
Write-Host "  explorer `"$SessionDir`""
