# DOC_LINK: DOC-SCRIPT-AIDER-OLLAMA-051
# Wrapper script to run aider with Ollama and proper encoding
# Usage: .\scripts\aider-ollama.ps1 [aider arguments]

# Set environment variables for UTF-8 encoding
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

# Set Ollama API base
$env:OLLAMA_API_BASE = 'http://127.0.0.1:11434'

# Use DeepSeek-R1 by default (matches .aider.conf.yml)
$env:AIDER_MODEL = 'ollama_chat/deepseek-r1:latest'

Write-Host "Starting Aider with DeepSeek-R1..." -ForegroundColor Cyan

# Run aider with all passed arguments (config file will be used automatically)
aider $args
