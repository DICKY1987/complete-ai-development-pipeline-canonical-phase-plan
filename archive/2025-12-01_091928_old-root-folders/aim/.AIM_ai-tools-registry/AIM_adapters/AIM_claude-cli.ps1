# DOC_LINK: DOC-AIM-AIM-CLAUDE-CLI-061
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

# Parse Claude output for structured data
function Parse-ClaudeOutput {
    param([string]$output)
    
    $filesModified = @()
    $filesCreated = @()
    
    # Claude CLI may output file changes in various formats
    # Adapt based on actual output
    $lines = $output -split "`n"
    foreach ($line in $lines) {
        if ($line -match 'modified|changed|updated|edited') {
            # Try to extract filename patterns
            if ($line -match '([a-zA-Z0-9_./\\-]+\.[a-z]{2,4})') {
                $file = $matches[1]
                if ($filesModified -notcontains $file) {
                    $filesModified += $file
                }
            }
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
        # Try both --version and -v flags
        $res = Invoke-External 'claude' @('--version') -timeoutSec 5
        
        if ($res.exit -ne 0 -or -not $res.stdout) { 
            $res = Invoke-External 'claude' @('-v') -timeoutSec 5
        }
        
        $ok = ($res.exit -eq 0)
        
        @{
            success = $ok
            message = if ($ok) { 'claude --version ok' } else { 'claude version failed' }
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
        
        # Build claude command arguments
        $claudeArgs = @('--print')  # Non-interactive mode
        
        # Try to use JSON output if supported
        $claudeArgs += @('--output-format', 'json')
        
        # Add the prompt
        $claudeArgs += $prompt
        
        # Retry logic with exponential backoff
        $maxRetries = if ($req.PSObject.Properties['max_retries']) { 
            $req.max_retries 
        } else { 
            1 
        }
        
        $attempt = 0
        $success = $false
        $lastResult = $null
        $jsonFallback = $false
        
        while (-not $success -and $attempt -le $maxRetries) {
            $attempt++
            
            $res = Invoke-External 'claude' $claudeArgs -timeoutSec $timeoutSec
            
            # If JSON output failed, retry without it
            if ($res.exit -ne 0 -and -not $jsonFallback -and ($res.stderr -match 'format|invalid')) {
                $claudeArgs = @('--print', $prompt)
                $jsonFallback = $true
                $res = Invoke-External 'claude' $claudeArgs -timeoutSec $timeoutSec
            }
            
            if ($res.exit -eq 0) {
                $success = $true
                $lastResult = $res
            }
            elseif ($res.timedOut) {
                # Don't retry on timeout
                break
            }
            elseif ($res.stderr -match 'login|auth|api[_-]?key|credential') {
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
        $parsed = Parse-ClaudeOutput -output $res.stdout
        
        # Determine failure reason
        $errorReason = if ($res.timedOut) {
            "timeout"
        } elseif ($res.stderr -match 'login|auth|api[_-]?key|credential') {
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
                "Claude requires authentication (check API key)"
            } else { 
                "Claude invocation failed after $attempt attempt(s)" 
            }
            content = @{
                files_modified = $parsed.filesModified
                files_created = $parsed.filesCreated
                exit_code = $res.exit
                attempts = $attempt
                error_reason = $errorReason
                used_json_fallback = $jsonFallback
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
