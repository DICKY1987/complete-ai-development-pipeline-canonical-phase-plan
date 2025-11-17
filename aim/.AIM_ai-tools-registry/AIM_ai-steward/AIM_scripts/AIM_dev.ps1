param([switch]$Tests)
if ($Tests) {
  Write-Host 'Running Pester tests (if available)...'
  try { Invoke-Pester -Path (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath 'AIM_tests') } catch { Write-Warning 'Pester not installed or test run failed.' }
} else {
  Write-Host 'AIM dev helper. Use -Tests to run tests.'
}

