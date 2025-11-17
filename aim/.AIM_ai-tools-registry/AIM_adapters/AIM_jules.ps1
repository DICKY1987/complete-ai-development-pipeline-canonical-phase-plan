Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Read input JSON from stdin
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

function Invoke-ByName($name, $argsArray) {
  $gc = Get-Command -All $name -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $gc) { return @{ exit=127; stdout=''; stderr="command not found: $name" } }
  $path = $gc.Path
  if ($path -match '\.ps1$') {
    $pwsh = Join-Path $PSHOME 'pwsh.exe'; if (-not (Test-Path $pwsh)) { $pwsh = 'pwsh' }
    return Invoke-External $pwsh (@('-NoLogo','-NoProfile','-File', $path) + $argsArray)
  } else {
    return Invoke-External $path $argsArray
  }
}

$cap = "$($req.capability)"
switch ($cap) {
  'version' {
    $res = Invoke-ByName 'jules' @('version')
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'jules version ok' } else { 'jules version failed' }
      content = @{ stdout = $res.stdout; stderr = $res.stderr; exit = $res.exit }
    } | ConvertTo-Json -Depth 10
    exit ($res.exit)
  }
  'code_generation' {
    $prompt = $req.payload.prompt
    if (-not $prompt) { $prompt = ($req | ConvertTo-Json -Depth 5) }
    # Attempt non-interactive session creation (requires login). If it fails, return failure to allow fallback.
    $res = Invoke-ByName 'jules' @('new', $prompt)
    $ok = ($res.exit -eq 0)
    @{
      success = $ok
      message = if ($ok) { 'jules new ok' } else { 'jules new failed (likely needs login)' }
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
