#!/bin/bash
# GUI Launcher Script (Linux/macOS)
# Sets up Python path and launches GUI application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"

export PYTHONPATH="$SRC_DIR"

echo "============================================================"
echo "AI Pipeline GUI Launcher"
echo "============================================================"
echo ""

# Check if PySide6 is installed
if ! python -c "import PySide6" 2>/dev/null; then
    echo "❌ PySide6 not installed"
    echo ""
    echo "Installing dependencies..."
    python -m pip install -r "$SCRIPT_DIR/requirements-gui.txt"
fi

echo "✅ Dependencies OK"
echo "📁 Working directory: $SRC_DIR"
echo ""

# Parse arguments
USE_MOCK_DATA=""
PANEL="dashboard"

for arg in "$@"; do
    case $arg in
        --mock|-m)
            USE_MOCK_DATA="--use-mock-data"
            ;;
        --panel=*)
            PANEL="${arg#*=}"
            ;;
    esac
done

# Build command
if [ -n "$USE_MOCK_DATA" ]; then
    echo "🔧 Mode: Mock data (testing)"
else
    echo "🔧 Mode: Real SQLite database"
fi
echo "📊 Initial panel: $PANEL"
echo ""

# Launch GUI
echo "🚀 Launching GUI..."
echo ""

cd "$SRC_DIR"
python -m gui_app.main --panel "$PANEL" $USE_MOCK_DATA
