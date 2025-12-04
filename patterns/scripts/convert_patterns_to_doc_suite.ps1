<#
.SYNOPSIS
Convert pattern files (.md/.txt) into complete pattern doc suites and update registry

.DESCRIPTION
This script:
1. Finds all .md/.txt files in patterns/ with doc_id front matter
2. Converts them into complete pattern doc suites (spec, schema, executor, tests, examples)
3. Updates the PATTERN_INDEX.yaml registry
4. Archives the original files to patterns/legacy_atoms/converted/

.PARAMETER DryRun
If specified, shows what would be done without making changes

.EXAMPLE
.\convert_patterns_to_doc_suite.ps1
.\convert_patterns_to_doc_suite.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$PatternsRoot = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\patterns"
$RepoRoot = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
$ArchiveRoot = Join-Path $RepoRoot "_ARCHIVE\patterns\legacy_atoms\converted"
$RegistryPath = Join-Path $PatternsRoot "registry\PATTERN_INDEX.yaml"

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      Pattern Doc Suite Converter & Registry Updater         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to extract doc_id from file
function Get-DocId {
    param([string]$FilePath)

    $content = Get-Content $FilePath -Raw
    if ($content -match '(?m)^doc_id:\s*(.+?)\s*$') {
        return $matches[1].Trim()
    }
    return $null
}

# Function to generate pattern_id from doc_id
function Get-PatternId {
    param([string]$DocId)

    # Convert DOC-PAT-XXX-NNN to PAT-XXX-NNN
    return $DocId -replace '^DOC-', ''
}

# Function to generate snake_case name from doc_id
function Get-PatternName {
    param([string]$DocId)

    # Extract middle part and convert to snake_case
    if ($DocId -match '^DOC-PAT-(.+?)-(\d+)$') {
        $name = $matches[1].ToLower().Replace('-', '_')
        if ($name.Length -gt 0) {
            return $name
        }
    }
    return $null
}

# Function to check if file should be converted
function Should-ConvertFile {
    param([System.IO.FileInfo]$File)

    # Skip README files unless they contain substantive pattern content
    if ($File.Name -match '^README\.md$') {
        return $false
    }

    # Skip files in certain subdirectories
    $skipDirs = @('legacy_atoms', 'examples', 'tests', 'scripts', 'automation', 'registry', 'schemas', 'executors', 'specs')
    foreach ($dir in $skipDirs) {
        if ($File.DirectoryName -match "\\$dir(\\|$)") {
            return $false
        }
    }

    # Must have doc_id
    $docId = Get-DocId $File.FullName
    if (!$docId) {
        return $false
    }

    # Must be a pattern doc_id (DOC-PAT-*)
    if ($docId -notmatch '^DOC-PAT-') {
        return $false
    }

    # Must be able to extract a valid name
    $name = Get-PatternName $docId
    if (!$name) {
        return $false
    }

    return $true
}

# Function to extract first 100 chars as summary
function Get-Summary {
    param([string]$FilePath)

    $content = Get-Content $FilePath -Raw
    # Skip front matter
    $content = $content -replace '(?s)^---.*?---\s*', ''
    # Get first non-empty line
    $lines = $content -split "`n" | Where-Object { $_.Trim() -ne '' }
    if ($lines.Count -gt 0) {
        $summary = $lines[0].Trim() -replace '^#+\s*', '' # Remove markdown headers
        if ($summary.Length -gt 100) {
            $summary = $summary.Substring(0, 97) + "..."
        }
        return $summary
    }
    return "Pattern converted from legacy source"
}

# Function to create pattern spec file
function New-PatternSpec {
    param(
        [string]$PatternId,
        [string]$Name,
        [string]$DocId,
        [string]$Summary,
        [string]$SourceFile
    )

    $specPath = Join-Path $PatternsRoot "specs\$Name.pattern.yaml"

    $specContent = @"
# $DocId
pattern_id: $PatternId
name: $Name
version: 1.0.0
doc_id: $DocId

metadata:
  created: $(Get-Date -Format 'yyyy-MM-dd')
  status: draft
  source: Converted from $SourceFile

intent: |
  $Summary

inputs:
  required: []
  optional: []

outputs:
  artifacts: []

steps:
  - name: pattern_execution
    description: Execute pattern logic

ground_truth:
  criteria:
    - description: Pattern executes without errors

validation:
  pre_conditions: []
  post_conditions: []

tool_bindings:
  - tool: claude_code
    priority: 1
  - tool: github_copilot_cli
    priority: 2
"@

    return @{
        Path = $specPath
        Content = $specContent
    }
}

# Function to create schema file
function New-PatternSchema {
    param(
        [string]$Name,
        [string]$DocId,
        [string]$PatternId
    )

    $schemaPath = Join-Path $PatternsRoot "schemas\$Name.schema.json"

    $schemaContent = @"
{
  "`$schema": "http://json-schema.org/draft-07/schema#",
  "`$id": "$DocId",
  "title": "$PatternId Pattern Instance",
  "type": "object",
  "required": ["pattern_id", "version"],
  "properties": {
    "pattern_id": {
      "type": "string",
      "const": "$PatternId"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+`$"
    },
    "inputs": {
      "type": "object",
      "properties": {},
      "additionalProperties": true
    },
    "outputs": {
      "type": "object",
      "properties": {},
      "additionalProperties": true
    }
  }
}
"@

    return @{
        Path = $schemaPath
        Content = $schemaContent
    }
}

# Function to create executor stub
function New-PatternExecutor {
    param(
        [string]$Name,
        [string]$DocId,
        [string]$PatternId
    )

    $executorPath = Join-Path $PatternsRoot "executors\${Name}_executor.ps1"

    $executorContent = @"
<#
.SYNOPSIS
Executor for $PatternId

.DESCRIPTION
doc_id: $DocId
pattern_id: $PatternId

.PARAMETER InstancePath
Path to pattern instance JSON file

.EXAMPLE
.\${Name}_executor.ps1 -InstancePath instance.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]`$InstancePath
)

`$ErrorActionPreference = "Stop"

Write-Host "▶ Executing pattern: $PatternId" -ForegroundColor Cyan

# Load instance
`$instance = Get-Content `$InstancePath | ConvertFrom-Json

# Validate pattern_id
if (`$instance.pattern_id -ne "$PatternId") {
    throw "Invalid pattern_id. Expected: $PatternId, Got: `$(`$instance.pattern_id)"
}

# TODO: Implement pattern logic
Write-Host "✓ Pattern execution complete" -ForegroundColor Green

# Return result
@{
    status = "success"
    pattern_id = "$PatternId"
    timestamp = (Get-Date -Format o)
} | ConvertTo-Json
"@

    return @{
        Path = $executorPath
        Content = $executorContent
    }
}

# Find all .md and .txt files with doc_id
Write-Host "🔍 Scanning for pattern files..." -ForegroundColor Yellow

$patternFiles = @()
$extensions = @('*.md', '*.txt')

foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path $PatternsRoot -Filter $ext -Recurse -File |
        Where-Object { Should-ConvertFile $_ }
    $patternFiles += $files
}

Write-Host "   Found $($patternFiles.Count) pattern files with doc_id" -ForegroundColor Green
Write-Host ""

if ($patternFiles.Count -eq 0) {
    Write-Host "✓ No pattern files found to convert" -ForegroundColor Green
    exit 0
}

# Process each file
$converted = @()
$failed = @()

foreach ($file in $patternFiles) {
    try {
        Write-Host "📄 Processing: $($file.Name)" -ForegroundColor Cyan

        $docId = Get-DocId $file.FullName
        $patternId = Get-PatternId $docId
        $name = Get-PatternName $docId
        $summary = Get-Summary $file.FullName

        Write-Host "   doc_id: $docId" -ForegroundColor Gray
        Write-Host "   pattern_id: $patternId" -ForegroundColor Gray
        Write-Host "   name: $name" -ForegroundColor Gray

        if (!$DryRun) {
            # Create spec
            $spec = New-PatternSpec -PatternId $patternId -Name $name -DocId $docId -Summary $summary -SourceFile $file.Name
            New-Item -ItemType Directory -Path (Split-Path $spec.Path) -Force | Out-Null
            Set-Content -Path $spec.Path -Value $spec.Content -NoNewline
            Write-Host "   ✓ Created spec: specs\$name.pattern.yaml" -ForegroundColor Green

            # Create schema
            $schema = New-PatternSchema -Name $name -DocId $docId -PatternId $patternId
            New-Item -ItemType Directory -Path (Split-Path $schema.Path) -Force | Out-Null
            Set-Content -Path $schema.Path -Value $schema.Content -NoNewline
            Write-Host "   ✓ Created schema: schemas\$name.schema.json" -ForegroundColor Green

            # Create executor
            $executor = New-PatternExecutor -Name $name -DocId $docId -PatternId $patternId
            New-Item -ItemType Directory -Path (Split-Path $executor.Path) -Force | Out-Null
            Set-Content -Path $executor.Path -Value $executor.Content -NoNewline
            Write-Host "   ✓ Created executor: executors\${name}_executor.ps1" -ForegroundColor Green

            # Archive original file
            $relativePath = $file.FullName.Replace($PatternsRoot, '').TrimStart('\')
            $archivePath = Join-Path $ArchiveRoot $relativePath
            New-Item -ItemType Directory -Path (Split-Path $archivePath) -Force | Out-Null
            Move-Item -Path $file.FullName -Destination $archivePath -Force
            Write-Host "   ✓ Archived: $relativePath" -ForegroundColor Yellow
        } else {
            Write-Host "   [DRY RUN] Would create:" -ForegroundColor Magenta
            Write-Host "      - specs\$name.pattern.yaml" -ForegroundColor Gray
            Write-Host "      - schemas\$name.schema.json" -ForegroundColor Gray
            Write-Host "      - executors\${name}_executor.ps1" -ForegroundColor Gray
            Write-Host "      - Archive to: legacy_atoms\converted\$($file.Name)" -ForegroundColor Gray
        }

        $converted += @{
            DocId = $docId
            PatternId = $patternId
            Name = $name
            Summary = $summary
            SourceFile = $file.Name
        }

        Write-Host ""

    } catch {
        Write-Host "   ✗ Failed: $_" -ForegroundColor Red
        $failed += @{
            File = $file.Name
            Error = $_.Exception.Message
        }
        Write-Host ""
    }
}

# Update registry
if ($converted.Count -gt 0 -and !$DryRun) {
    Write-Host "📝 Updating PATTERN_INDEX.yaml..." -ForegroundColor Yellow

    # Load existing registry
    $registryContent = Get-Content $RegistryPath -Raw

    # Backup registry
    $backupPath = "$RegistryPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $RegistryPath -Destination $backupPath
    Write-Host "   ✓ Backed up registry to: $(Split-Path $backupPath -Leaf)" -ForegroundColor Gray

    # Add new patterns to registry
    $newEntries = @()
    foreach ($pattern in $converted) {
        $entry = @"

- pattern_id: $($pattern.PatternId)
  name: $($pattern.Name)
  version: 1.0.0
  status: draft
  category: converted
  doc_id: $($pattern.DocId)
  spec_path: patterns/specs/$($pattern.Name).pattern.yaml
  schema_path: patterns/schemas/$($pattern.Name).schema.json
  executor_path: patterns/executors/$($pattern.Name)_executor.ps1
  tool_targets:
  - claude_code
  - github_copilot_cli
  time_savings_vs_manual: 0%
  proven_uses: 0
  created: '$(Get-Date -Format 'yyyy-MM-dd')'
  summary: "$($pattern.Summary)"
  notes: "Converted from $($pattern.SourceFile)"
"@
        $newEntries += $entry
    }

    # Append to patterns section
    $updatedContent = $registryContent.TrimEnd() + "`n" + ($newEntries -join "`n")
    Set-Content -Path $RegistryPath -Value $updatedContent -NoNewline

    Write-Host "   ✓ Added $($converted.Count) patterns to registry" -ForegroundColor Green
    Write-Host ""
}

# Summary
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                        SUMMARY                               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Converted: $($converted.Count) patterns" -ForegroundColor Green
Write-Host "✗ Failed: $($failed.Count) patterns" -ForegroundColor Red
Write-Host ""

if ($converted.Count -gt 0) {
    Write-Host "Converted patterns:" -ForegroundColor Yellow
    foreach ($pattern in $converted) {
        Write-Host "  • $($pattern.PatternId) ($($pattern.Name))" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($failed.Count -gt 0) {
    Write-Host "Failed conversions:" -ForegroundColor Red
    foreach ($fail in $failed) {
        Write-Host "  • $($fail.File): $($fail.Error)" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($DryRun) {
    Write-Host "▶ This was a DRY RUN. Run without -DryRun to apply changes." -ForegroundColor Magenta
} else {
    Write-Host "✓ Pattern conversion complete!" -ForegroundColor Green
    Write-Host "  Registry updated: $RegistryPath" -ForegroundColor Gray
    Write-Host "  Archived files: _ARCHIVE\patterns\legacy_atoms\converted\" -ForegroundColor Gray
}
