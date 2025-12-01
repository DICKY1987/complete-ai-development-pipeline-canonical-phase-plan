# DOC_LINK: DOC-AIM-AIM-ROUTING-TESTS-068
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'AIM routing rules' {
  It 'loads code_generation routing from rules file' {
    $root = Split-Path -Parent $PSScriptRoot
    $rulesPath = Join-Path $root '../AIM_cross-tool/AIM_coordination-rules.json' | Resolve-Path | Select-Object -ExpandProperty Path
    $rules = Get-Content -Path $rulesPath -Raw | ConvertFrom-Json
    $rules.capabilities.code_generation.primary | Should Not BeNullOrEmpty
    $rules.capabilities.code_generation.fallback | Should Not BeNullOrEmpty
  }
}

