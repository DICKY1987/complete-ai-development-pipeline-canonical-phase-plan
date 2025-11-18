<#
.SYNOPSIS
  Launch ollama-code-cli in WSL against a Windows repo, local-only.

.PARAMETER RepoPath
  Windows path to the target repository (e.g., C:\Users\richg\ALL_AI\Repo).

.PARAMETER Model
  Ollama model to use (default: qwen2.5-coder:14b).

.NOTES
  - Prefers localhost Ollama; falls back to Windows host IP from WSL.
  - Unsets cloud API keys in the WSL session (local-only guard).
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$RepoPath,
  [string]$Model = "qwen2.5-coder:14b"
)

if (-not (Test-Path -LiteralPath $RepoPath)) {
  Write-Error "Repo path not found: $RepoPath"
  exit 1
}

$wslPath = (wsl -d Ubuntu -- wslpath -a "$RepoPath").Trim()

$bash = @"
set -e
if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  export OLLAMA_API_BASE="http://127.0.0.1:11434"
else
  WIN_IP=
  WIN_IP=$(ip route show | awk '/default/ {print $3}')
  export OLLAMA_API_BASE="http://$WIN_IP:11434"
fi
unset OPENAI_API_KEY ANTHROPIC_API_KEY
cd '$wslPath'
ollama-code-cli --model '$Model'
"@

wsl -d Ubuntu -- bash -lc "$bash"

