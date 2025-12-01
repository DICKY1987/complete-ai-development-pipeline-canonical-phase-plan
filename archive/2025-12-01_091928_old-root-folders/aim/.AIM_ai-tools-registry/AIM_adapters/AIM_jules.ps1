# DOC_LINK: DOC-AIM-AIM-JULES-062
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Read and parse JSON input from stdin
$inputJson = [Console]::In.ReadToEnd()
$req = $null
try { 
    $req = $inputJson | ConvertFrom-Json 
} catch { 
    $req = $null 
}

if (-not $req) {
    @{ 
        success = $false
        message = 'Invalid JSON input'
        content = @{}
    } | ConvertTo-Json -Depth 6
    exit 1
}

# Helper function to invoke external commands with timeout
function Invoke-External {
    param(
        [string]$exe,
        [array]$argsArray,
        [int]$timeoutSec = 30
    )
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = ($argsArray | ForEach-Object { 
        if($_ -match ' ') { '"' + $_ + '"' } else { $_ } 
    }) -join ' '
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    
    $stdout = New-Object System.Text.StringBuilder
    $stderr = New-Object System.Text.StringBuilder
    
    $stdoutEvent = Register-ObjectEvent -InputObject $process `
        -EventName OutputDataReceived `
        -Action { $Event.MessageData.AppendLine($EventArgs.Data) } `
        -MessageData $stdout
    
    $stderrEvent = Register-ObjectEvent -InputObject $process `
        -EventName ErrorDataReceived `
        -Action { $Event.MessageData.AppendLine($EventArgs.Data) } `
        -MessageData $stderr
    
    try {
        [void]$process.Start()
        $process.BeginOutputReadLine()
        $process.BeginErrorReadLine()
        
        if (-not $process.WaitForExit($timeoutSec * 1000)) {
            # Timeout occurred
            $process.Kill()
            return @{ 
                exit = 124
                stdout = $stdout.ToString()
                stderr = "Timeout after ${timeoutSec} seconds"
                timedOut = $true
            }
        }
        
        $process.WaitForExit() # Ensure async read operations complete
        
        return @{ 
            exit = $process.ExitCode
            stdout = $stdout.ToString()
            stderr = $stderr.ToString()
            timedOut = $false
        }
    }
    finally {
        Unregister-Event -SourceIdentifier $stdoutEvent.Name -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier $stderrEvent.Name -ErrorAction SilentlyContinue
        if (-not $process.HasExited) {
            $process.Kill()
        }
        $process.Dispose()
    }
}

# Helper to find command by name (supports .ps1 scripts and executables)
function Invoke-ByName {
    param(
        [string]$name,
        [array]$argsArray,
        [int]$timeoutSec = 30
    )
    
    $gc = Get-Command -All $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $gc) { 
        return @{ 
            exit = 127
            stdout = ''
            stderr = "command not found: $name"
            timedOut = $false
        } 
    }
    
    $path = $gc.Path
    if ($path -match '\.ps1$') {
        $pwsh = Join-Path $PSHOME 'pwsh.exe'
        if (-not (Test-Path $pwsh)) { $pwsh = 'pwsh' }
        return Invoke-External $pwsh (@('-NoLogo', '-NoProfile', '-File', $path) + $argsArray) -timeoutSec $timeoutSec
    } else {
        return Invoke-External $path $argsArray -timeoutSec $timeoutSec
    }
}

# Parse files modified from jules output
function Parse-JulesOutput {
    param([string]$output)
    
    $filesModified = @()
    $filesCreated = @()
    
    # Jules output parsing (adapt based on actual output format)
    $lines = $output -split "`n"
    foreach ($line in $lines) {
        if ($line -match '^\s*modified:\s*(.+)$') {
            $filesModified += $matches[1].Trim()
        }
        elseif ($line -match '^\s*created:\s*(.+)$') {
            $filesCreated += $matches[1].Trim()
        }
    }
    
    return @{
        filesModified = $filesModified
        filesCreated = $filesCreated
    }
}

# Get timeout from payload or use default
$timeoutSec = 30
if ($req.PSObject.Properties['timeout_ms']) {
    $timeoutSec = [int]($req.timeout_ms / 1000)
}

$cap = "$($req.capability)"

switch ($cap) {
    'version' {
        $res = Invoke-ByName 'jules' @('version') -timeoutSec 5
        $ok = ($res.exit -eq 0)
        
        @{
            success = $ok
            message = if ($ok) { 'jules version ok' } else { 'jules version failed' }
            content = @{ 
                stdout = $res.stdout
                stderr = $res.stderr
                exit = $res.exit
            }
        } | ConvertTo-Json -Depth 10
        
        exit $res.exit
    }
    
    'code_generation' {
        $prompt = $req.payload.prompt
        if (-not $prompt) { 
            $prompt = ($req | ConvertTo-Json -Depth 5) 
        }
        
        # Retry logic with exponential backoff
        $maxRetries = if ($req.PSObject.Properties['max_retries']) { 
            $req.max_retries 
        } else { 
            1 
        }
        
        $attempt = 0
        $success = $false
        $lastResult = $null
        
        while (-not $success -and $attempt -le $maxRetries) {
            $attempt++
            
            # Jules requires login for most operations
            $res = Invoke-ByName 'jules' @('new', $prompt) -timeoutSec $timeoutSec
            
            if ($res.exit -eq 0) {
                $success = $true
                $lastResult = $res
            }
            elseif ($res.timedOut) {
                # Don't retry on timeout
                break
            }
            elseif ($res.stderr -match 'login|auth|credential') {
                # Authentication error - don't retry
                $lastResult = $res
                break
            }
            else {
                $lastResult = $res
                if ($attempt -le $maxRetries) {
                    Start-Sleep -Seconds ([Math]::Pow(2, $attempt))
                }
            }
        }
        
        $res = $lastResult
        $ok = ($res.exit -eq 0)
        
        # Parse output for structured data
        $parsed = Parse-JulesOutput -output $res.stdout
        
        # Determine failure reason
        $errorReason = if ($res.timedOut) {
            "timeout"
        } elseif ($res.stderr -match 'login|auth|credential') {
            "authentication_required"
        } elseif ($res.exit -eq 127) {
            "command_not_found"
        } else {
            "tool_error"
        }
        
        @{
            success = $ok
            message = if ($ok) { 
                "Code generation completed (attempt $attempt)" 
            } elseif ($res.timedOut) {
                "Timeout after ${timeoutSec} seconds"
            } elseif ($errorReason -eq "authentication_required") {
                "Jules requires login (run 'jules login')"
            } else { 
                "Jules invocation failed after $attempt attempt(s)" 
            }
            content = @{
                files_modified = $parsed.filesModified
                files_created = $parsed.filesCreated
                exit_code = $res.exit
                attempts = $attempt
                error_reason = $errorReason
                stdout = $res.stdout
                stderr = $res.stderr
            }
        } | ConvertTo-Json -Depth 10
        
        exit $res.exit
    }
    
    Default {
        @{
            success = $false
            message = "Unsupported capability: $cap"
            content = @{}
        } | ConvertTo-Json -Depth 6
        exit 1
    }
}
