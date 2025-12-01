param(
    [string]$RootPath = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan",
    [string]$OutputPath,
    [string[]]$Extensions = @(".md", ".txt"),
    [string[]]$NameKeywords = @(
        "PLAN",
        "REPORT",
        "QUICKSTART",
        "SUMMARY",
        "COMPLETE",
        "COMPLETED",
        "CHAT",
        "PHASE"
    ),
    [switch]$NewestFirst
)

if (-not (Test-Path -LiteralPath $RootPath)) {
    Write-Error "RootPath does not exist: $RootPath"
    exit 1
}

if (-not $OutputPath) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputPath = Join-Path -Path (Get-Location) -ChildPath "file_index_$timestamp.csv"
}

Write-Host "Scanning:" $RootPath
Write-Host "Output file:" $OutputPath
Write-Host "Extensions:" ($Extensions -join ", ")
Write-Host "Keywords:"   ($NameKeywords -join ", ")
Write-Host ""

$allFiles = Get-ChildItem -LiteralPath $RootPath -Recurse -File -ErrorAction SilentlyContinue

$matchingFiles = $allFiles | Where-Object {
    $hasValidExtension = $Extensions -contains $_.Extension
    if (-not $hasValidExtension) { return $false }

    $name = $_.BaseName
    $matchesKeyword = $false
    foreach ($kw in $NameKeywords) {
        if ($name -like "*$kw*") {
            $matchesKeyword = $true
            break
        }
    }
    return $matchesKeyword
}

$results = $matchingFiles | Select-Object `
    @{ Name = 'FullPath';     Expression = { $_.FullName } },
    @{ Name = 'LastModified'; Expression = { $_.LastWriteTime } },
    @{ Name = 'SizeBytes';    Expression = { $_.Length } }

$results = $results | Sort-Object -Property LastModified -Descending:$NewestFirst.IsPresent

$results | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

Write-Host "Files found:" $results.Count
Write-Host "Report written to:" $OutputPath
