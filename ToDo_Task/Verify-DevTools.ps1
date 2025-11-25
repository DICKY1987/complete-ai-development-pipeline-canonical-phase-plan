<#
    Verify-DevTools.ps1
    - Shows the list of tools it will check
    - Verifies if each tool is installed
    - Reports location (path or module base)

    Designed for your current Windows dev/AI stack.
#>

[CmdletBinding()]
param(
    # Extra directories to search if a command is not on PATH
    [string[]]$ExtraSearchDirs = @(
        "C:\Tools\node",
        "C:\Tools\node\npm",
        "C:\Tools\pipx\bin"
    ),

    # Optional: directory to export JSON/CSV reports
    [string]$OutputDir
)

# -------------------------------
# Helper: Find an executable path
# -------------------------------
function Find-Executable {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Command,

        [string[]]$ExtraPaths = @()
    )

    # 1) Try normal PATH resolution
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    # 2) Try a few extra directories (node/pipx/etc.)
    $candidates = @() + $ExtraPaths

    foreach ($dir in $candidates) {
        if (-not $dir) { continue }
        if (-not (Test-Path $dir)) { continue }

        $exePath   = Join-Path $dir ($Command + ".exe")
        $barePath  = Join-Path $dir $Command

        if (Test-Path $exePath)  { return $exePath }
        if (Test-Path $barePath) { return $barePath }
    }

    return $null
}

# ---------------------------------------
# Tool catalog (edit this to add/remove)
# ---------------------------------------
$tools = @(
    # Phase 1: Critical Runtime
    [pscustomobject]@{ Phase='Runtime'; Name='Git';              Kind='exe';    Command='git';                 Module=$null }
    [pscustomobject]@{ Phase='Runtime'; Name='Python';           Kind='exe';    Command='python';              Module=$null }
    [pscustomobject]@{ Phase='Runtime'; Name='Node.js';          Kind='exe';    Command='node';                Module=$null }
    [pscustomobject]@{ Phase='Runtime'; Name='PowerShell 7';     Kind='exe';    Command='pwsh';                Module=$null }
    [pscustomobject]@{ Phase='Runtime'; Name='GitHub CLI';       Kind='exe';    Command='gh';                  Module=$null }

    # Phase 2: Core Quality Tools
    [pscustomobject]@{ Phase='Quality'; Name='Ruff';             Kind='exe';    Command='ruff';                Module=$null }
    [pscustomobject]@{ Phase='Quality'; Name='Black';            Kind='exe';    Command='black';               Module=$null }
    [pscustomobject]@{ Phase='Quality'; Name='pytest';           Kind='exe';    Command='pytest';              Module=$null }
    [pscustomobject]@{ Phase='Quality'; Name='Semgrep';          Kind='exe';    Command='semgrep';             Module=$null }
    [pscustomobject]@{ Phase='Quality'; Name='Gitleaks';         Kind='exe';    Command='gitleaks';            Module=$null }
    [pscustomobject]@{ Phase='Quality'; Name='PSScriptAnalyzer'; Kind='module'; Command=$null;                 Module='PSScriptAnalyzer' }

    # Phase 3: AI Assistants
    [pscustomobject]@{ Phase='AI';      Name='Aider';            Kind='exe';    Command='aider';               Module=$null }
    [pscustomobject]@{ Phase='AI';      Name='Claude Code CLI';  Kind='exe';    Command='claude';              Module=$null }
    [pscustomobject]@{ Phase='AI';      Name='LangGraph CLI';    Kind='exe';    Command='langgraph';           Module=$null }
    [pscustomobject]@{ Phase='AI';      Name='Invoke';           Kind='exe';    Command='invoke';              Module=$null }

    # Phase 4: MCP Infrastructure
    [pscustomobject]@{ Phase='MCP';     Name='PowerShell.MCP';   Kind='module'; Command=$null;                 Module='PowerShell.MCP' }
    [pscustomobject]@{ Phase='MCP';     Name='GitHub MCP';       Kind='exe';    Command='mcp-server-github';   Module=$null }
    [pscustomobject]@{ Phase='MCP';     Name='Memory MCP';       Kind='exe';    Command='mcp-server-memory';   Module=$null }
    [pscustomobject]@{ Phase='MCP';     Name='Filesystem MCP';   Kind='exe';    Command='mcp-server-filesystem'; Module=$null }
)

# ---------------------------------
# 1) Show the list to the user
# ---------------------------------
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Dev & AI Tool Verification Catalog " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$tools |
    Sort-Object Phase, Name |
    Group-Object Phase |
    ForEach-Object {
        Write-Host ("[Phase: {0}]" -f $_.Name) -ForegroundColor Yellow
        $_.Group | ForEach-Object {
            $kind = if ($_.Kind -eq 'module') { "PSModule: $($_.Module)" } else { "Command: $($_.Command)" }
            Write-Host ("  - {0} ({1})" -f $_.Name, $kind)
        }
        Write-Host ""
    }

Write-Host "Running verification checks..." -ForegroundColor Cyan
Write-Host ""

# ---------------------------------
# 2) Run the checks
# ---------------------------------
$results = foreach ($tool in $tools) {

    if ($tool.Kind -eq 'module') {
        # PowerShell module check
        $mod = Get-Module -ListAvailable -Name $tool.Module | Select-Object -First 1

        if ($mod) {
            [pscustomobject]@{
                Phase     = $tool.Phase
                Tool      = $tool.Name
                Kind      = 'PSModule'
                Installed = $true
                Location  = $mod.ModuleBase
                Detail    = "Module $($tool.Module) v$($mod.Version)"
            }
        }
        else {
            [pscustomobject]@{
                Phase     = $tool.Phase
                Tool      = $tool.Name
                Kind      = 'PSModule'
                Installed = $false
                Location  = ''
                Detail    = "Module '$($tool.Module)' not found. Check installation."
            }
        }
    }
    else {
        # CLI / command check
        $path = Find-Executable -Command $tool.Command -ExtraPaths $ExtraSearchDirs

        if ($path) {
            [pscustomobject]@{
                Phase     = $tool.Phase
                Tool      = $tool.Name
                Kind      = 'Command'
                Installed = $true
                Location  = $path
                Detail    = "Command '$($tool.Command)'"
            }
        }
        else {
            [pscustomobject]@{
                Phase     = $tool.Phase
                Tool      = $tool.Name
                Kind      = 'Command'
                Installed = $false
                Location  = ''
                Detail    = "Command '$($tool.Command)' not found (check PATH and install)."
            }
        }
    }
}

# ---------------------------------
# 3) Pretty table + pipeline output
# ---------------------------------
$results |
    Sort-Object Phase, Tool |
    Format-Table Phase, Tool, Installed, Location -AutoSize |
    Out-Host

Write-Host ""
Write-Host "Tip: You can pipe the results to Export-Csv or ConvertTo-Json for reports." -ForegroundColor DarkGray

# Optional export
if ($OutputDir) {
    try {
        if (-not (Test-Path -LiteralPath $OutputDir)) {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        }
        $ts = Get-Date -Format 'yyyyMMdd_HHmmss'
        $base = Join-Path $OutputDir ("devtools-verification-" + $ts)

        $sorted = $results | Sort-Object Phase, Tool
        $csvPath = "$base.csv"
        $jsonPath = "$base.json"

        $sorted | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csvPath
        $sorted | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8

        Write-Host ("Saved reports: {0} and {1}" -f $csvPath, $jsonPath) -ForegroundColor Green
    }
    catch {
        Write-Warning ("Failed to export reports to '{0}': {1}" -f $OutputDir, $_)
    }
}

# Return objects to the pipeline (for scripts/automation)
$results
