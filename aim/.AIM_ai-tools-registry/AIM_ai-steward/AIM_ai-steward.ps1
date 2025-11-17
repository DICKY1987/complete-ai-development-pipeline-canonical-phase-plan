<#
  AIM_ai-steward.ps1
  Thin CLI entrypoint for ai-steward (AIM_-prefixed).
  Commands: status | apply | validate | capability
  Options: --json, --registry-root <path>, --whatif
  This script delegates to AIM_modules/AIM_AIToolsRegistry.psm1.
#>

param(
  [Parameter(Position=0)] [ValidateSet('status','apply','validate','capability','help')] [string] $Command = 'help',
  [Parameter(Position=1)] [string] $Capability,
  [Parameter(Position=2)] [string] $Payload,
  [switch] $Json,
  [string] $RegistryRoot,
  [switch] $WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Usage {
  @'
Usage:
  AIM_ai-steward.ps1 status [-Json] [-RegistryRoot <path>]
  AIM_ai-steward.ps1 validate [-Json] [-RegistryRoot <path>]
  AIM_ai-steward.ps1 apply [-WhatIf] [-Json] [-RegistryRoot <path>]
  AIM_ai-steward.ps1 capability <name> <payload-json-or-path> [-Json] [-RegistryRoot <path>]

Env:
  AI_TOOLS_REGISTRY_ROOT (optional, overrides default repo-based lookup)
'@ | Write-Host
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$modulePath = Join-Path $repoRoot 'AIM_modules/AIM_AIToolsRegistry.psm1'
if (-not (Test-Path $modulePath)) {
  Write-Error "Missing module: $modulePath"; exit 1
}

Import-Module $modulePath -Force

$root = Get-RegistryRoot $RegistryRoot

switch ($Command) {
  'help' { Write-Usage; exit 0 }

  'status' {
    $res = Get-AIToolStatus -RegistryRoot $root -AsJson:$Json
    if ($Json) { $res | ConvertTo-Json -Depth 6 } else { $res }
    exit 0
  }

  'validate' {
    $ok = Test-AIRegistry -RegistryRoot $root -AsJson:$Json
    if ($Json) { $ok | ConvertTo-Json -Depth 5 } else { if ($ok.Success) { Write-Host 'Registry valid.' } else { Write-Error $ok.Message } }
    exit ($(if ($ok.Success) {0} else {2}))
  }

  'apply' {
    $res = Invoke-AIToolApply -RegistryRoot $root -AsJson:$Json -WhatIf:$WhatIf
    if ($Json) { $res | ConvertTo-Json -Depth 6 } else { $res }
    exit ($(if ($res.Success) {0} else {3}))
  }

  'capability' {
    if (-not $Capability) { Write-Error 'Missing <name> argument'; Write-Usage; exit 1 }
    if (-not $Payload) { Write-Error 'Missing <payload-json-or-path> argument'; Write-Usage; exit 1 }
    $payloadJson = $null
    if (Test-Path $Payload) {
      $payloadJson = Get-Content -Path $Payload -Raw
    } else {
      $payloadJson = $Payload
    }
    $res = Invoke-AICapability -RegistryRoot $root -Capability $Capability -PayloadJson $payloadJson -AsJson:$Json
    if ($Json) { $res | ConvertTo-Json -Depth 8 } else { $res }
    exit ($(if ($res.Success) {0} else {4}))
  }
}
