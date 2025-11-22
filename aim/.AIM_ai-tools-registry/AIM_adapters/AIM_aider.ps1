Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Fix Windows Unicode encoding issues (CRITICAL for aider output display)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

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

# Parse files modified from aider output
function Parse-AiderOutput {
    param([string]$output)
    
    $filesModified = @()
    $filesCreated = @()
    $linesAdded = 0
    $linesRemoved = 0
    
    # Parse output for file changes
    # Aider typically outputs: "Modified: file.py" or "Created: file.py"
    $lines = $output -split "`n"
    foreach ($line in $lines) {
        if ($line -match '^\s*Modified:\s*(.+)$') {
            $filesModified += $matches[1].Trim()
        }
        elseif ($line -match '^\s*Created:\s*(.+)$') {
            $filesCreated += $matches[1].Trim()
        }
        elseif ($line -match '^\s*(\d+)\s+insertion') {
            $linesAdded = [int]$matches[1]
        }
        elseif ($line -match '^\s*(\d+)\s+deletion') {
            $linesRemoved = [int]$matches[1]
        }
    }
    
    return @{
        filesModified = $filesModified
        filesCreated = $filesCreated
        linesAdded = $linesAdded
        linesRemoved = $linesRemoved
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
        $res = Invoke-External 'aider' @('--version') -timeoutSec 5
        $ok = ($res.exit -eq 0)
        
        @{
            success = $ok
            message = if ($ok) { 'aider --version ok' } else { 'aider --version failed' }
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
        
        # Build aider command with robust flags
        $aiderArgs = @(
            '--yes'                    # Auto-approve changes
            '--no-auto-commits'        # Don't auto-commit (pipeline handles commits)
            '--message', $prompt       # The instruction
        )
        
        # Add files if specified
        if ($req.payload.PSObject.Properties['files']) {
            $files = $req.payload.files
            if ($files -is [array]) {
                $aiderArgs += $files
            }
            elseif ($files) {
                $aiderArgs += @($files)
            }
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
            
            $res = Invoke-External 'aider' $aiderArgs -timeoutSec $timeoutSec
            
            if ($res.exit -eq 0) {
                $success = $true
                $lastResult = $res
            }
            elseif ($res.timedOut) {
                # Don't retry on timeout
                break
            }
            else {
                $lastResult = $res
                if ($attempt -le $maxRetries) {
                    # Exponential backoff: 2s, 4s, 8s...
                    Start-Sleep -Seconds ([Math]::Pow(2, $attempt))
                }
            }
        }
        
        $res = $lastResult
        $ok = ($res.exit -eq 0)
        
        # Parse output for structured data
        $parsed = Parse-AiderOutput -output $res.stdout
        
        @{
            success = $ok
            message = if ($ok) { 
                "Code generation completed (attempt $attempt)" 
            } elseif ($res.timedOut) {
                "Timeout after ${timeoutSec} seconds"
            } else { 
                "Aider invocation failed after $attempt attempt(s)" 
            }
            content = @{
                files_modified = $parsed.filesModified
                files_created = $parsed.filesCreated
                lines_added = $parsed.linesAdded
                lines_removed = $parsed.linesRemoved
                exit_code = $res.exit
                attempts = $attempt
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
