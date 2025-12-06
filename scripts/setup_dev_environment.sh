#!/usr/bin/env bash
# DOC_LINK: DOC-SCRIPT-SETUP-DEV-ENVIRONMENT-841
# Enhanced development environment bootstrap script
# Automated setup for new developers (Linux/macOS)

set -euo pipefail

SKIP_PRECOMMIT=false
SKIP_TESTS=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-precommit)
            SKIP_PRECOMMIT=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-precommit] [--skip-tests] [--verbose]"
            exit 1
            ;;
    esac
done

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Development Environment Bootstrap                 ║${NC}"
echo -e "${CYAN}║  Complete AI Development Pipeline                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Navigate to repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
echo -e "📁 Repository: ${GRAY}$REPO_ROOT${NC}"

# Step 1: Python version check
echo -e "\n${YELLOW}[1/7] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "  ${GREEN}✅ Found: $PYTHON_VERSION${NC}"

    # Extract version
    if [[ $PYTHON_VERSION =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"

        if [[ $MAJOR -lt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -lt 11 ]]; then
            echo -e "  ${RED}⚠️  Python 3.11+ required, found $MAJOR.$MINOR${NC}"
            echo -e "  ${YELLOW}📥 Install from: https://www.python.org/downloads/${NC}"
            exit 1
        fi
    fi
else
    echo -e "  ${RED}❌ Python not found${NC}"
    echo -e "  ${YELLOW}📥 Install from: https://www.python.org/downloads/${NC}"
    exit 1
fi

# Use python3 explicitly
PYTHON=python3

# Step 2: Install Python dependencies
echo -e "\n${YELLOW}[2/7] Installing Python dependencies...${NC}"
if [[ $VERBOSE == true ]]; then
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install -r requirements.txt
else
    $PYTHON -m pip install --upgrade pip --quiet
    $PYTHON -m pip install -r requirements.txt --quiet
fi
echo -e "  ${GREEN}✅ Dependencies installed${NC}"

# Step 3: Install package in editable mode
echo -e "\n${YELLOW}[3/7] Installing package in development mode...${NC}"
if [[ -f "pyproject.toml" ]]; then
    if [[ $VERBOSE == true ]]; then
        $PYTHON -m pip install -e .
    else
        $PYTHON -m pip install -e . --quiet
    fi
    echo -e "  ${GREEN}✅ Package installed in editable mode${NC}"
else
    echo -e "  ${YELLOW}⚠️  No pyproject.toml found, skipping editable install${NC}"
fi

# Step 4: Setup pre-commit hooks
if [[ $SKIP_PRECOMMIT == false ]]; then
    echo -e "\n${YELLOW}[4/7] Setting up pre-commit hooks...${NC}"
    if [[ $VERBOSE == true ]]; then
        $PYTHON -m pip install pre-commit
    else
        $PYTHON -m pip install pre-commit --quiet
    fi
    pre-commit install --install-hooks
    echo -e "  ${GREEN}✅ Pre-commit hooks installed${NC}"
    echo -e "  ${GRAY}ℹ️  Hooks will run automatically on git commit${NC}"
else
    echo -e "\n${GRAY}[4/7] Skipping pre-commit hooks (--skip-precommit)${NC}"
fi

# Step 5: Create necessary directories
echo -e "\n${YELLOW}[5/7] Creating workspace directories...${NC}"
DIRECTORIES=(.state .ledger .worktrees docs tests scripts reports)
for dir in "${DIRECTORIES[@]}"; do
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        echo -e "  ${GRAY}📁 Created: $dir${NC}"
    fi
done
echo -e "  ${GREEN}✅ Workspace directories ready${NC}"

# Step 6: Validate environment
echo -e "\n${YELLOW}[6/7] Validating environment...${NC}"
VALIDATION_ERRORS=()

# Check critical tools
declare -A TOOLS=(
    ["pytest"]="pytest --version"
    ["black"]="black --version"
    ["isort"]="isort --version"
    ["ruff"]="ruff --version"
)

for tool in "${!TOOLS[@]}"; do
    if ${TOOLS[$tool]} &> /dev/null; then
        echo -e "  ${GREEN}✅ $tool available${NC}"
    else
        echo -e "  ${RED}❌ $tool not found${NC}"
        VALIDATION_ERRORS+=("$tool")
    fi
done

if [[ ${#VALIDATION_ERRORS[@]} -gt 0 ]]; then
    echo -e "  ${YELLOW}⚠️  Some tools missing: ${VALIDATION_ERRORS[*]}${NC}"
    echo -e "  ${YELLOW}💡 Run: pip install pytest black isort ruff${NC}"
fi

# Step 7: Run quick validation tests
if [[ $SKIP_TESTS == false ]]; then
    echo -e "\n${YELLOW}[7/7] Running validation tests...${NC}"
    echo -e "  ${GRAY}🧪 Running quick test suite...${NC}"
    if pytest -x -q -m "not slow" --tb=short 2>&1; then
        echo -e "  ${GREEN}✅ All validation tests passed${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Some tests failed (this is OK for first setup)${NC}"
        echo -e "  ${GRAY}💡 Run 'pytest -v' for details${NC}"
    fi
else
    echo -e "\n${GRAY}[7/7] Skipping validation tests (--skip-tests)${NC}"
fi

# Success summary
echo -e "\n${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Development Environment Ready!                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}📋 Next Steps:${NC}"
echo -e "  1. Read: AGENTS.md (AI agent guidelines)"
echo -e "  2. Read: README.md (project overview)"
echo -e "  3. Run tests: pytest -v"
echo -e "  4. Create feature branch: git checkout -b feature/your-feature"
echo -e "  5. Start coding! 🚀"

echo -e "\n${CYAN}💡 Useful Commands:${NC}"
echo -e "  ${GRAY}pytest -v              # Run all tests${NC}"
echo -e "  ${GRAY}pytest --cov           # Run with coverage${NC}"
echo -e "  ${GRAY}black .                # Format code${NC}"
echo -e "  ${GRAY}ruff check .           # Lint code${NC}"
echo -e "  ${GRAY}pre-commit run --all-files  # Run all pre-commit hooks${NC}"

echo ""
