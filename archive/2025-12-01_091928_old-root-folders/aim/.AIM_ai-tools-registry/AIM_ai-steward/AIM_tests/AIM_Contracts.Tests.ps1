# DOC_LINK: DOC-AIM-AIM-CONTRACTS-TESTS-067
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'AIM contract fixtures' {
  It 'have sample registry fixture files' {
    (Test-Path (Join-Path $PSScriptRoot 'AIM_fixtures/AIM_sample_registry.valid.json')) | Should Be $true
    (Test-Path (Join-Path $PSScriptRoot 'AIM_fixtures/AIM_sample_registry.invalid.json')) | Should Be $true
    (Test-Path (Join-Path $PSScriptRoot 'AIM_fixtures/AIM_sample_rules.valid.json')) | Should Be $true
  }
}
