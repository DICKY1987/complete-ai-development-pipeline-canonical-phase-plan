param(
  [Parameter(Mandatory=$true)][string]$EpicName,
  [string]$BranchName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function RepoRoot() {
  $cur = (Get-Location).Path
  while ($true) {
    if (Test-Path (Join-Path $cur '.git')) { return $cur }
    $parent = Split-Path $cur -Parent
    if ($parent -eq $cur) { return (Get-Location).Path }
    $cur = $parent
  }
}

$root = RepoRoot
$branch = if ($BranchName) { $BranchName } else { "epic/$EpicName" }
$wtPath = Join-Path (Split-Path $root -Parent) ("epic-" + $EpicName)

if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host "[worktree] Adding worktree at $wtPath (branch $branch)"
  pushd $root | Out-Null
  try {
    git worktree add "$wtPath" -b "$branch"
  } finally { popd | Out-Null }
} else {
  Write-Host "[worktree] git not found. Creating directory only: $wtPath"
  New-Item -ItemType Directory -Path $wtPath -Force | Out-Null
}

Write-Host "[worktree] Ready: $wtPath"

