# Configure Ollama to Allow WSL Connections
# ==========================================
# This script configures Ollama to listen on the network interface
# so WSL can connect to it.
#
# Run this script to enable Ollama access from WSL.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama WSL Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will configure Ollama to accept connections from WSL." -ForegroundColor Yellow
Write-Host ""

# Check if Ollama is installed
Write-Host "Checking if Ollama is installed..." -ForegroundColor Yellow
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaPath) {
    Write-Host "ERROR: Ollama is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ollama first:" -ForegroundColor Yellow
    Write-Host "  https://ollama.com/download" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Ollama found at: $($ollamaPath.Source)" -ForegroundColor Green
Write-Host ""

# Test current Ollama connection
Write-Host "Testing current Ollama connection..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "✓ Ollama is running and accessible on localhost" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Cannot connect to Ollama on localhost:11434" -ForegroundColor Yellow
    Write-Host "Make sure Ollama is running: ollama serve" -ForegroundColor Gray
}

Write-Host ""

# Check current OLLAMA_HOST setting
$currentHost = [System.Environment]::GetEnvironmentVariable("OLLAMA_HOST", "User")
if ($currentHost) {
    Write-Host "Current OLLAMA_HOST (User): $currentHost" -ForegroundColor Gray
} else {
    Write-Host "OLLAMA_HOST is not set (defaults to 127.0.0.1:11434)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Options" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose how to configure Ollama:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. User Environment Variable (Recommended)" -ForegroundColor Cyan
Write-Host "   Sets OLLAMA_HOST=0.0.0.0:11434 for current user" -ForegroundColor Gray
Write-Host "   Requires Ollama restart or reboot" -ForegroundColor Gray
Write-Host ""
Write-Host "2. System Environment Variable" -ForegroundColor Cyan
Write-Host "   Sets OLLAMA_HOST=0.0.0.0:11434 system-wide" -ForegroundColor Gray
Write-Host "   Requires Ollama restart or reboot" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test Mode (One-time, this session only)" -ForegroundColor Cyan
Write-Host "   Sets for current PowerShell session only" -ForegroundColor Gray
Write-Host "   Good for testing before permanent change" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Skip (I'll configure manually)" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Setting User environment variable..." -ForegroundColor Yellow
        [System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")
        Write-Host "✓ OLLAMA_HOST=0.0.0.0:11434 set for current user" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: You must restart Ollama for this to take effect:" -ForegroundColor Yellow
        Write-Host "  1. Close any running Ollama processes" -ForegroundColor Gray
        Write-Host "  2. Restart Ollama or reboot your computer" -ForegroundColor Gray
        Write-Host "  3. Or run: ollama serve" -ForegroundColor Gray
    }
    "2" {
        Write-Host ""
        Write-Host "Setting System environment variable (requires admin)..." -ForegroundColor Yellow
        try {
            [System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "Machine")
            Write-Host "✓ OLLAMA_HOST=0.0.0.0:11434 set system-wide" -ForegroundColor Green
            Write-Host ""
            Write-Host "IMPORTANT: You must restart Ollama for this to take effect:" -ForegroundColor Yellow
            Write-Host "  1. Close any running Ollama processes" -ForegroundColor Gray
            Write-Host "  2. Restart Ollama or reboot your computer" -ForegroundColor Gray
        } catch {
            Write-Host "ERROR: Failed to set system variable (requires admin privileges)" -ForegroundColor Red
            Write-Host "Try running PowerShell as Administrator, or choose option 1" -ForegroundColor Yellow
        }
    }
    "3" {
        Write-Host ""
        Write-Host "Setting for current session only..." -ForegroundColor Yellow
        $env:OLLAMA_HOST = "0.0.0.0:11434"
        Write-Host "✓ OLLAMA_HOST=0.0.0.0:11434 set for this session" -ForegroundColor Green
        Write-Host ""
        Write-Host "Starting Ollama with this configuration..." -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop Ollama when done testing" -ForegroundColor Gray
        Write-Host ""
        ollama serve
    }
    "4" {
        Write-Host ""
        Write-Host "Skipping automatic configuration." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To configure manually, set this environment variable:" -ForegroundColor Yellow
        Write-Host "  OLLAMA_HOST=0.0.0.0:11434" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Then restart Ollama." -ForegroundColor Gray
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing WSL Connection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($choice -ne "3") {
    Write-Host "After restarting Ollama, test the connection from WSL:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  wsl -d Ubuntu" -ForegroundColor Cyan
    Write-Host "  curl http://172.27.16.1:11434/api/tags" -ForegroundColor Cyan
    Write-Host "  exit" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Expected: JSON response with model list" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Restart Ollama (if you chose option 1 or 2)" -ForegroundColor Yellow
Write-Host "2. Test connection from WSL (see command above)" -ForegroundColor Yellow
Write-Host "3. Test Aider:" -ForegroundColor Yellow
Write-Host "     aider-wsl <your-repo>" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see:" -ForegroundColor Gray
Write-Host "  C:\Users\richg\WSL_CODEX_AIDER\OLLAMA-SETUP-GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
