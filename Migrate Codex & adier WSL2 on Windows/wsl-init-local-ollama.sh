#!/usr/bin/env bash
set -euo pipefail

# Append a local-only Ollama/Aider init block to ~/.bashrc if not present
if ! grep -qE ">>> OLLAMA_LOCAL_INIT >>>" "$HOME/.bashrc" 2>/dev/null; then
  cat >> "$HOME/.bashrc" <<'EOF'
# >>> OLLAMA_LOCAL_INIT >>>
# Resolve local Ollama endpoint: prefer localhost, else Windows host IP
if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  export OLLAMA_API_BASE="http://127.0.0.1:11434"
else
  WIN_IP=$(ip route show | awk '/default/ {print $3}')
  export OLLAMA_API_BASE="http://$WIN_IP:11434"
fi
# Local-only: avoid accidental cloud usage in this session
unset OPENAI_API_KEY ANTHROPIC_API_KEY
# <<< OLLAMA_LOCAL_INIT <<<
EOF
fi

# Install tools locally for user
python3 -m pip install --user --upgrade pip
python3 -m pip install --user aider-install ollama-code-cli

# Install aider CLI entrypoints
if command -v aider-install >/dev/null 2>&1; then
  aider-install || true
fi

echo "[wsl-init-local-ollama] Initialization complete."
echo "Open a new shell or run: source ~/.bashrc"
echo "Then test: curl \"$OLLAMA_API_BASE/api/tags\""

