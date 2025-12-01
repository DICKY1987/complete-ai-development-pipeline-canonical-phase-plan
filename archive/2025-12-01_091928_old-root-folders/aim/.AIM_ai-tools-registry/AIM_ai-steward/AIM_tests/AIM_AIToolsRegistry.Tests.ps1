# DOC_LINK: DOC-AIM-AIM-AITOOLSREGISTRY-TESTS-066
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'AIM_AIToolsRegistry module' {
  It 'exports expected functions' {
    $root = Split-Path -Parent $PSScriptRoot
    $modulePath = Join-Path $root 'AIM_modules/AIM_AIToolsRegistry.psm1'
    Import-Module $modulePath -Force
    (Get-Command Get-AIToolStatus) | Should Not BeNullOrEmpty
    (Get-Command Test-AIRegistry) | Should Not BeNullOrEmpty
    (Get-Command Invoke-AIToolApply) | Should Not BeNullOrEmpty
    (Get-Command Invoke-AICapability) | Should Not BeNullOrEmpty
  }
}
