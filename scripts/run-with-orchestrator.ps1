# Universal Orchestrator Wrapper
# DOC_ID: DOC-SCRIPTS-ORCHESTRATOR-WRAPPER-001

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,
    
    [Parameter(Mandatory=$true)]
    [string]$Phase,
    
    [hashtable]$Params = @{},
    [int]$Timeout = 300,
    [switch]$NoTelemetry
)

$ErrorActionPreference = "Stop"

Write-Host "[orchestrator] Creating run for $ScriptPath in phase $Phase"

$runId = & python -c @"
import sys; sys.path.insert(0, '.');
from core.engine.orchestrator import Orchestrator;
orch = Orchestrator();
run_id = orch.create_run('scripts', '$Phase', metadata={'script': '$ScriptPath'});
print(run_id)
"@

if (-not $runId) {
    Write-Error "Failed to create orchestrator run"
    exit 1
}

if (-not $NoTelemetry) {
    $paramsJson = ($Params | ConvertTo-Json -Compress).Replace('"', '\"')
    & python -c @"
import sys; sys.path.insert(0, '.');
from patterns.automation.integration.orchestrator_hooks import PatternAutomationHooks;
hooks = PatternAutomationHooks(enabled=True);
hooks.on_task_start({'script': '$ScriptPath', 'phase': '$Phase', 'params': {}})
"@ 2>$null
}

Write-Host "[orchestrator] Executing $ScriptPath with timeout ${Timeout}s"

$job = Start-Job -ScriptBlock {
    param($path, $args)
    & $path @args
} -ArgumentList $ScriptPath, $Params

$completed = Wait-Job -Job $job -Timeout $Timeout
$output = Receive-Job -Job $job
$exitCode = if ($completed.State -eq 'Completed') { 0 } else { 1 }

if (-not $NoTelemetry) {
    & python -c @"
import sys; sys.path.insert(0, '.');
from patterns.automation.integration.orchestrator_hooks import PatternAutomationHooks;
hooks = PatternAutomationHooks(enabled=True);
hooks.on_task_complete({'script': '$ScriptPath'}, {'success': $($exitCode -eq 0), 'exit_code': $exitCode}, {})
"@ 2>$null
}

$state = if ($exitCode -eq 0) { "completed" } else { "failed" }
& python -c @"
import sys; sys.path.insert(0, '.');
from core.engine.orchestrator import Orchestrator;
orch = Orchestrator();
orch.update_run_state('$runId', '$state')
"@ 2>$null

Write-Host "[orchestrator] Run $runId`: $state"
Write-Host $output

exit $exitCode
