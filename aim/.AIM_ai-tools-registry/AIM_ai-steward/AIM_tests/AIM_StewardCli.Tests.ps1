Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'AIM_ai-steward CLI' {
  It 'prints help' {
    $root = Split-Path -Parent $PSScriptRoot
    $cli = Join-Path $root 'AIM_ai-steward.ps1'
    $pwsh = Join-Path $PSHOME 'pwsh.exe'
    if (-not (Test-Path $pwsh)) { $pwsh = 'pwsh' }
    $args = "-NoLogo -NoProfile -File `"$cli`" help"
    $p = Start-Process -FilePath $pwsh -ArgumentList $args -PassThru -Wait -WindowStyle Hidden
    $p.ExitCode | Should Be 0
  }
}
