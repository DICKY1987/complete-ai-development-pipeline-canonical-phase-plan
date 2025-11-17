Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-AdapterTest {
  param(
    [Parameter(Mandatory)] [string] $ScriptPath
  )
  $pwsh = Join-Path $PSHOME 'pwsh.exe'
  if (-not (Test-Path $pwsh)) { $pwsh = 'pwsh' }
  $json = '{"capability":"version","payload":{},"tool":"test"}'
  $tmp = New-TemporaryFile
  Set-Content -Path $tmp -Value $json -Encoding utf8
  $cmd = "type `"$($tmp.FullName)`" | `"$pwsh`" -NoLogo -NoProfile -File `"$ScriptPath`""
  $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $cmd) -PassThru -WindowStyle Hidden
  $proc.WaitForExit() | Out-Null
  return $proc
}

Describe 'AIM adapters smoke' {
  It 'aider adapter handles version' {
    $script = Join-Path (Split-Path -Parent $PSScriptRoot) '../AIM_adapters/AIM_aider.ps1' | Resolve-Path | Select-Object -ExpandProperty Path
    $p = Invoke-AdapterTest -ScriptPath $script
    $p.ExitCode | Should Be 0
  }

  It 'jules adapter handles version' {
    $script = Join-Path (Split-Path -Parent $PSScriptRoot) '../AIM_adapters/AIM_jules.ps1' | Resolve-Path | Select-Object -ExpandProperty Path
    $p = Invoke-AdapterTest -ScriptPath $script
    $p.ExitCode | Should Be 0
  }

  It 'claude-cli adapter handles version' {
    $script = Join-Path (Split-Path -Parent $PSScriptRoot) '../AIM_adapters/AIM_claude-cli.ps1' | Resolve-Path | Select-Object -ExpandProperty Path
    $p = Invoke-AdapterTest -ScriptPath $script
    $p.ExitCode | Should Be 0
  }
}
