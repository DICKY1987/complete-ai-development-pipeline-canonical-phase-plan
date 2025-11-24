# Pattern Execution Utilities
# Shared functions for all pattern executors
# Version: 1.0.0

function Write-PatternLog {
    <#
    .SYNOPSIS
    Writes structured log messages for pattern execution
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "Cyan" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-PatternInstance {
    <#
    .SYNOPSIS
    Validates pattern instance has correct doc_id and pattern_id
    #>
    param(
        [Parameter(Mandatory=$true)]
        [object]$Instance,
        [Parameter(Mandatory=$true)]
        [string]$ExpectedDocId,
        [Parameter(Mandatory=$true)]
        [string]$ExpectedPatternId
    )
    
    if ($Instance.doc_id -ne $ExpectedDocId) {
        throw "Invalid doc_id. Expected: $ExpectedDocId, Got: $($Instance.doc_id)"
    }
    
    if ($Instance.pattern_id -ne $ExpectedPatternId) {
        throw "Invalid pattern_id. Expected: $ExpectedPatternId, Got: $($Instance.pattern_id)"
    }
    
    Write-PatternLog "Instance validation passed" "SUCCESS"
}

function New-PatternResult {
    <#
    .SYNOPSIS
    Creates standardized pattern execution result
    #>
    param(
        [Parameter(Mandatory=$true)]
        [bool]$Success,
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [object]$Data = @{}
    )
    
    $result = @{
        success = $Success
        message = $Message
        timestamp = Get-Date -Format "o"
        data = $Data
    }
    
    return ($result | ConvertTo-Json -Depth 10)
}

function Invoke-WithRollback {
    <#
    .SYNOPSIS
    Executes action with automatic rollback on failure
    #>
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$Action,
        [Parameter(Mandatory=$true)]
        [scriptblock]$Rollback
    )
    
    try {
        & $Action
    } catch {
        Write-PatternLog "Action failed, rolling back..." "WARNING"
        & $Rollback
        throw
    }
}

function ConvertFrom-Yaml {
    <#
    .SYNOPSIS
    Simple YAML to object converter (basic support)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$YamlContent
    )
    
    # For now, return raw content - full YAML parsing requires external module
    # Pattern executors will use JSON instances
    return $YamlContent
}

# Export functions
Export-ModuleMember -Function @(
    'Write-PatternLog',
    'Test-PatternInstance',
    'New-PatternResult',
    'Invoke-WithRollback',
    'ConvertFrom-Yaml'
)
