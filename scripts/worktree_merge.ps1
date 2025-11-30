# DOC_LINK: DOC-SCRIPT-WORKTREE-MERGE-075
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

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "[worktree] git not found; skipping merge" -ForegroundColor Yellow
  exit 0
}

Write-Host "[worktree] Merging worktree ($wtPath) back to main branch"
pushd $root | Out-Null
try {
  # Fetch branch into repo if needed
  git fetch --all --prune | Out-Null
  # Attempt a merge; default target is current branch
  git merge "$branch"
} finally {
  popd | Out-Null
}

Write-Host "[worktree] Merge attempted for $branch"

