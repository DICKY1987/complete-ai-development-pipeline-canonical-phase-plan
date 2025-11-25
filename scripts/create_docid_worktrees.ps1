#!/usr/bin/env pwsh
# Thin wrapper that proxies to the doc_id module script so existing tooling keeps working.

$repoRoot = Split-Path -Parent $PSScriptRoot
$docIdScript = Join-Path $repoRoot "doc_id\\create_docid_worktrees.ps1"

if (-not (Test-Path $docIdScript)) {
    Write-Error "doc_id script not found at $docIdScript"
    exit 1
}

& $docIdScript @args
