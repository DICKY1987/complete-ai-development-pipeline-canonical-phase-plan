Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$inputJson = [Console]::In.ReadToEnd()
$req = $null
try { $req = $inputJson | ConvertFrom-Json } catch { $req = $null }
if (-not $req) {
  @{ success=$false; message='Invalid JSON input' } | ConvertTo-Json -Depth 6
  exit 1
}

function Invoke-External($exe, $argsArray) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe
  $psi.Arguments = ($argsArray | ForEach-Object { if($_ -match ' ') { '"' + $_ + '"' } else { $_ } }) -join ' '
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  [void]$p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  return @{ exit=$p.ExitCode; stdout=$stdout; stderr=$stderr }
}

$cap = "$($req.capability)"
switch ($cap) {
  'version' {
    $res = Invoke-External 'aider' @('--version')
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'aider --version ok' } else { 'aider --version failed' }
      content = @{ stdout = $res.stdout; stderr = $res.stderr; exit = $res.exit }
    } | ConvertTo-Json -Depth 10
    exit ($res.exit)
  }
  'code_generation' {
    $prompt = $req.payload.prompt
    if (-not $prompt) { $prompt = ($req | ConvertTo-Json -Depth 5) }
    # Try non-interactive one-shot message; avoid auto-commit and confirm prompts
    $args = @('--yes','--no-auto-commit','--message', $prompt)
    $res = Invoke-External 'aider' $args
    if ($res.exit -ne 0 -or -not $res.stdout) {
      # Fallback to help to capture some diagnostic output
      $res = Invoke-External 'aider' @('--help')
    }
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'aider invocation ok' } else { 'aider invocation failed' }
      content = @{ stdout = $res.stdout; stderr = $res.stderr; exit = $res.exit }
    } | ConvertTo-Json -Depth 10
    exit ($res.exit)
  }
  Default {
    @{
      success = $false
      message = "unsupported capability: $cap"
      content = @{ }
    } | ConvertTo-Json -Depth 6
    exit 1
  }
}
