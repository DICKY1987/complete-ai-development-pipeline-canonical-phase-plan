# DOC_LINK: DOC-SCRIPT-TEST-AIDER-DEEPSEEK-073
# Test script to verify Aider + DeepSeek-R1 integration
# This creates a temporary test and verifies aider can make code changes

Write-Host "=== Testing Aider + Ollama + DeepSeek-R1 ===" -ForegroundColor Cyan
Write-Host ""

# Set environment
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:OLLAMA_API_BASE = "http://127.0.0.1:11434"
$env:AIDER_MODEL = "ollama_chat/deepseek-r1:latest"

# Create temp directory
$testDir = Join-Path $env:TEMP "aider_test_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $testDir | Out-Null
Push-Location $testDir

Write-Host "Test directory: $testDir" -ForegroundColor Yellow
Write-Host ""

# Initialize git repo (aider requires it)
git init -q
git config user.name "Test User"
git config user.email "test@example.com"

# Create a simple Python file
@"
def greet(name):
    return f'Hello, {name}!'

if __name__ == '__main__':
    print(greet('World'))
"@ | Set-Content test.py

git add test.py
git commit -q -m "Initial commit"

Write-Host "Created test.py with greeting function" -ForegroundColor Green
Write-Host ""

# Test 1: Check Ollama is responding
Write-Host "Test 1: Checking Ollama connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -ErrorAction Stop
    $modelNames = $response.models | ForEach-Object { $_.name }
    if ($modelNames -contains "deepseek-r1:latest") {
        Write-Host "  ✓ Ollama is running and deepseek-r1:latest is available" -ForegroundColor Green
    } else {
        Write-Host "  ✗ deepseek-r1:latest not found in Ollama" -ForegroundColor Red
        Write-Host "  Available models: $($modelNames -join ', ')"
        Pop-Location
        Remove-Item -Recurse -Force $testDir
        exit 1
    }
} catch {
    Write-Host "  ✗ Cannot connect to Ollama at http://127.0.0.1:11434" -ForegroundColor Red
    Write-Host "  Error: $_"
    Pop-Location
    Remove-Item -Recurse -Force $testDir
    exit 1
}
Write-Host ""

# Test 2: Run aider to modify the code
Write-Host "Test 2: Running Aider to modify code..." -ForegroundColor Cyan
Write-Host "  Asking Aider to change 'Hello' to 'Hi' in greeting" -ForegroundColor Gray

$output = aider --yes --no-auto-commits --message "Change the greeting to say 'Hi' instead of 'Hello'" test.py 2>&1 | Out-String

# Check if the file was modified
$content = Get-Content test.py -Raw
if ($content -match "Hi,") {
    Write-Host "  ✓ Aider successfully modified the code!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Modified code:" -ForegroundColor Yellow
    Write-Host $content
} else {
    Write-Host "  ✗ Aider did not modify the code as expected" -ForegroundColor Red
    Write-Host ""
    Write-Host "Output:" -ForegroundColor Yellow
    Write-Host $output
    Write-Host ""
    Write-Host "File content:" -ForegroundColor Yellow
    Write-Host $content
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up test directory..." -ForegroundColor Gray
Pop-Location
Remove-Item -Recurse -Force $testDir

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
