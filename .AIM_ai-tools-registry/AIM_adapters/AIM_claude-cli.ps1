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
    $res = Invoke-External 'claude' @('--version')
    if ($res.exit -ne 0 -or -not $res.stdout) { $res = Invoke-External 'claude' @('-v') }
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'claude --version ok' } else { 'claude version failed' }
      content = @{ stdout = $res.stdout; stderr = $res.stderr; exit = $res.exit }
    } | ConvertTo-Json -Depth 10
    exit ($res.exit)
  }
  'code_generation' {
    $prompt = $req.payload.prompt
    if (-not $prompt) { $prompt = ($req | ConvertTo-Json -Depth 5) }
    # Non-interactive print mode with JSON output when possible
    $res = Invoke-External 'claude' @('--print','--output-format','json', $prompt)
    if ($res.exit -ne 0) { $res = Invoke-External 'claude' @('--print', $prompt) }
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'claude print ok' } else { 'claude invocation failed' }
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
