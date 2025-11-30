# DOC_LINK: DOC-SCRIPT-SET-AIDER-ENV-070
# Set Aider Environment Variables
# Run this before using aider, or add to your PowerShell profile

# Fix Unicode encoding issues on Windows
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Set Ollama API base
$env:OLLAMA_API_BASE = "http://127.0.0.1:11434"

# Set default model to DeepSeek-R1 (matches .aider.conf.yml)
$env:AIDER_MODEL = "ollama_chat/deepseek-r1:latest"

Write-Host "✓ Aider environment configured:" -ForegroundColor Green
Write-Host "  PYTHONIOENCODING = $env:PYTHONIOENCODING"
Write-Host "  PYTHONUTF8 = $env:PYTHONUTF8"
Write-Host "  OLLAMA_API_BASE = $env:OLLAMA_API_BASE"
Write-Host "  AIDER_MODEL = $env:AIDER_MODEL"
Write-Host ""
Write-Host "You can now run: aider" -ForegroundColor Cyan
