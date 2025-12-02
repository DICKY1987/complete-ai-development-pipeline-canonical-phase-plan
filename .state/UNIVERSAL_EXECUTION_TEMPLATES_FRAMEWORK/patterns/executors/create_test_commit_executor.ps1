# DOC_LINK: DOC-PAT-CREATE-TEST-COMMIT-001
# Pattern: create_test_commit (PAT-CREATE-TEST-COMMIT-001)
# Version: 1.0.0
# Category: sequential
# Purpose: Create file, run tests, commit if green

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load common utilities
. "$PSScriptRoot\..\scripts\pattern_utilities.ps1"

Write-PatternLog "Executing create_test_commit pattern..." "INFO"

# Load and validate instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
Test-PatternInstance -Instance $instance `
    -ExpectedDocId "DOC-PAT-CREATE-TEST-COMMIT-001" `
    -ExpectedPatternId "PAT-CREATE-TEST-COMMIT-001"

# Extract inputs
$filePath = $instance.inputs.file_path
$fileContent = $instance.inputs.file_content
$testCommand = $instance.inputs.test_command
$commitMessage = $instance.inputs.commit_message

Write-PatternLog "Creating file: $filePath" "INFO"

# Step 1: Create file
$fileDir = Split-Path $filePath -Parent
if ($fileDir -and -not (Test-Path $fileDir)) {
    New-Item -ItemType Directory -Path $fileDir -Force | Out-Null
    Write-PatternLog "Created directory: $fileDir" "INFO"
}

try {
    # Create file
    Set-Content -Path $filePath -Value $fileContent -Encoding UTF8
    Write-PatternLog "File created successfully" "SUCCESS"
    
    # Step 2: Run tests
    Write-PatternLog "Running tests: $testCommand" "INFO"
    $testOutput = Invoke-Expression $testCommand 2>&1
    $testPassed = ($LASTEXITCODE -eq 0)
    
    if ($testPassed) {
        Write-PatternLog "Tests passed" "SUCCESS"
        
        # Step 3: Commit
        Write-PatternLog "Committing changes..." "INFO"
        git add $filePath 2>&1 | Out-Null
        git commit -m $commitMessage 2>&1 | Out-Null
        $commitSha = git rev-parse HEAD
        
        Write-PatternLog "Committed: $commitSha" "SUCCESS"
        
        # Return success result
        $result = New-PatternResult -Success $true -Message "File created and committed" -Data @{
            file_path = $filePath
            commit_sha = $commitSha
            test_results = "PASS"
        }
    } else {
        Write-PatternLog "Tests failed - rolling back" "WARNING"
        
        # Rollback: delete file
        Remove-Item $filePath -Force
        Write-PatternLog "File removed (rollback)" "INFO"
        
        $result = New-PatternResult -Success $false -Message "Tests failed - file creation rolled back" -Data @{
            test_results = "FAIL"
            test_output = ($testOutput -join "`n")
        }
    }
    
} catch {
    Write-PatternLog "Error: $_" "ERROR"
    
    # Cleanup on error
    if (Test-Path $filePath) {
        Remove-Item $filePath -Force
        Write-PatternLog "Cleaned up file after error" "INFO"
    }
    
    throw
}

Write-Output $result
