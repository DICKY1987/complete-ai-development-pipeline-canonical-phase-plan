#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-TRANSACTIONS-1184
# DOC_LINK: DOC-PAT-TRANSACTIONS-976
# DOC_LINK: DOC-PAT-TRANSACTIONS-240
<#
.SYNOPSIS
    Shared transaction management library for pattern executors

.DESCRIPTION
    Provides atomic file operations with rollback capability:
    - Begin/commit/rollback transactions
    - Temp file management
    - Atomic multi-file writes

.NOTES
    Module: transactions.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-TRANSACTIONS-001
#>

#region Transaction Management

function Begin-FileTransaction {
    <#
    .SYNOPSIS
        Begins a new file transaction for atomic operations
    
    .PARAMETER TransactionId
        Unique identifier for this transaction (auto-generated if not provided)
    
    .OUTPUTS
        Hashtable transaction object: @{ id=$string; temp_dir=$string; operations=@(); started_at=$datetime }
    #>
    param(
        [Parameter(Mandatory=$false)]
        [string]$TransactionId = $null
    )
    
    if (-not $TransactionId) {
        $TransactionId = "TXN_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + (Get-Random -Maximum 9999)
    }
    
    # Create temporary directory for transaction
    $tempDir = Join-Path $env:TEMP "file_transactions" $TransactionId
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    $transaction = @{
        id = $TransactionId
        temp_dir = $tempDir
        operations = @()
        started_at = Get-Date
        status = "active"
    }
    
    return $transaction
}

function Add-FileOperation {
    <#
    .SYNOPSIS
        Adds a file operation to the transaction
    
    .PARAMETER Transaction
        Transaction object from Begin-FileTransaction
    
    .PARAMETER Operation
        Operation type: 'create', 'update', 'delete'
    
    .PARAMETER Path
        Target file path
    
    .PARAMETER Content
        File content (for create/update operations)
    
    .OUTPUTS
        Updated transaction object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Transaction,
        
        [Parameter(Mandatory=$true)]
        [ValidateSet('create', 'update', 'delete')]
        [string]$Operation,
        
        [Parameter(Mandatory=$true)]
        [string]$Path,
        
        [Parameter(Mandatory=$false)]
        [string]$Content = $null
    )
    
    $operation = @{
        type = $Operation
        target_path = $Path
        content = $Content
        backup_path = $null
        temp_path = $null
        executed = $false
    }
    
    # For update/delete operations, backup existing file
    if ($Operation -in @('update', 'delete') -and (Test-Path $Path)) {
        $backupFileName = [System.IO.Path]::GetFileName($Path) + ".backup"
        $operation.backup_path = Join-Path $Transaction.temp_dir $backupFileName
        Copy-Item -Path $Path -Destination $operation.backup_path -Force
    }
    
    # For create/update operations, write to temp file first
    if ($Operation -in @('create', 'update') -and $Content) {
        $tempFileName = [System.IO.Path]::GetFileName($Path) + ".temp"
        $operation.temp_path = Join-Path $Transaction.temp_dir $tempFileName
        Set-Content -Path $operation.temp_path -Value $Content -NoNewline
    }
    
    $Transaction.operations += $operation
    
    return $Transaction
}

function Commit-FileTransaction {
    <#
    .SYNOPSIS
        Commits the transaction, applying all operations atomically
    
    .PARAMETER Transaction
        Transaction object with operations to commit
    
    .PARAMETER KeepBackups
        If true, preserves backup files after commit
    
    .OUTPUTS
        Hashtable with commit results: @{ success=$bool; operations_applied=$int; errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Transaction,
        
        [Parameter(Mandatory=$false)]
        [switch]$KeepBackups
    )
    
    $result = @{
        success = $true
        operations_applied = 0
        errors = @()
    }
    
    try {
        # Apply all operations
        foreach ($op in $Transaction.operations) {
            try {
                switch ($op.type) {
                    'create' {
                        # Ensure parent directory exists
                        $parentDir = Split-Path $op.target_path -Parent
                        if ($parentDir -and (-not (Test-Path $parentDir))) {
                            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                        }
                        
                        # Copy from temp to target
                        if ($op.temp_path) {
                            Copy-Item -Path $op.temp_path -Destination $op.target_path -Force
                        }
                    }
                    
                    'update' {
                        # Copy from temp to target
                        if ($op.temp_path) {
                            Copy-Item -Path $op.temp_path -Destination $op.target_path -Force
                        }
                    }
                    
                    'delete' {
                        # Delete target file
                        if (Test-Path $op.target_path) {
                            Remove-Item -Path $op.target_path -Force
                        }
                    }
                }
                
                $op.executed = $true
                $result.operations_applied++
            }
            catch {
                $result.success = $false
                $result.errors += "Failed to apply operation on $($op.target_path): $($_.Exception.Message)"
                throw  # Abort transaction on first error
            }
        }
        
        $Transaction.status = "committed"
    }
    catch {
        # Transaction failed, rollback
        $result.success = $false
        $rollbackResult = Rollback-FileTransaction -Transaction $Transaction
        $result.errors += "Transaction rolled back due to error"
        return $result
    }
    finally {
        # Clean up temp directory unless keeping backups
        if (-not $KeepBackups) {
            Remove-Item -Path $Transaction.temp_dir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    return $result
}

function Rollback-FileTransaction {
    <#
    .SYNOPSIS
        Rolls back the transaction, restoring original state
    
    .PARAMETER Transaction
        Transaction object to rollback
    
    .OUTPUTS
        Hashtable with rollback results: @{ success=$bool; operations_reverted=$int; errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Transaction
    )
    
    $result = @{
        success = $true
        operations_reverted = 0
        errors = @()
    }
    
    # Rollback operations in reverse order
    $opsToRollback = $Transaction.operations | Where-Object { $_.executed }
    [array]::Reverse($opsToRollback)
    
    foreach ($op in $opsToRollback) {
        try {
            switch ($op.type) {
                'create' {
                    # Remove created file
                    if (Test-Path $op.target_path) {
                        Remove-Item -Path $op.target_path -Force
                    }
                }
                
                'update' {
                    # Restore from backup
                    if ($op.backup_path -and (Test-Path $op.backup_path)) {
                        Copy-Item -Path $op.backup_path -Destination $op.target_path -Force
                    }
                }
                
                'delete' {
                    # Restore from backup
                    if ($op.backup_path -and (Test-Path $op.backup_path)) {
                        Copy-Item -Path $op.backup_path -Destination $op.target_path -Force
                    }
                }
            }
            
            $result.operations_reverted++
        }
        catch {
            $result.success = $false
            $result.errors += "Failed to rollback operation on $($op.target_path): $($_.Exception.Message)"
        }
    }
    
    $Transaction.status = "rolled_back"
    
    # Clean up temp directory
    Remove-Item -Path $Transaction.temp_dir -Recurse -Force -ErrorAction SilentlyContinue
    
    return $result
}

#endregion

#region Atomic Write Helpers

function Write-FileAtomic {
    <#
    .SYNOPSIS
        Writes file content atomically (all-or-nothing)
    
    .PARAMETER Path
        Target file path
    
    .PARAMETER Content
        File content to write
    
    .PARAMETER Encoding
        File encoding (default: UTF8)
    
    .OUTPUTS
        Boolean indicating success
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,
        
        [Parameter(Mandatory=$true)]
        [string]$Content,
        
        [Parameter(Mandatory=$false)]
        [string]$Encoding = "UTF8"
    )
    
    $txn = Begin-FileTransaction
    
    try {
        $operation = if (Test-Path $Path) { 'update' } else { 'create' }
        Add-FileOperation -Transaction $txn -Operation $operation -Path $Path -Content $Content | Out-Null
        
        $commitResult = Commit-FileTransaction -Transaction $txn
        return $commitResult.success
    }
    catch {
        Rollback-FileTransaction -Transaction $txn | Out-Null
        throw
    }
}

function Write-FilesAtomic {
    <#
    .SYNOPSIS
        Writes multiple files atomically (all succeed or all rollback)
    
    .PARAMETER Files
        Array of file definitions: @{ path=$string; content=$string }
    
    .OUTPUTS
        Hashtable with results: @{ success=$bool; files_written=$int; errors=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files
    )
    
    $txn = Begin-FileTransaction
    
    try {
        foreach ($file in $Files) {
            $operation = if (Test-Path $file.path) { 'update' } else { 'create' }
            Add-FileOperation -Transaction $txn -Operation $operation -Path $file.path -Content $file.content | Out-Null
        }
        
        $commitResult = Commit-FileTransaction -Transaction $txn
        
        return @{
            success = $commitResult.success
            files_written = $commitResult.operations_applied
            errors = $commitResult.errors
        }
    }
    catch {
        $rollbackResult = Rollback-FileTransaction -Transaction $txn
        
        return @{
            success = $false
            files_written = 0
            errors = @("Transaction failed and rolled back: $($_.Exception.Message)")
        }
    }
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Begin-FileTransaction',
    'Add-FileOperation',
    'Commit-FileTransaction',
    'Rollback-FileTransaction',
    'Write-FileAtomic',
    'Write-FilesAtomic'
)
