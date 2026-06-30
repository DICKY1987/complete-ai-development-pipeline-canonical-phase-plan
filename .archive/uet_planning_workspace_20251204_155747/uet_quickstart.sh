#!/usr/bin/env bash
# DOC_LINK: DOC-SCRIPT-UET-QUICKSTART-FILE-001
# UET Integration - Quick Start Script
#
# This script performs the Week 1 Day 1 setup tasks in one command
# Run from repository root: bash docs/uet_quickstart.sh

set -e  # Exit on error

echo "======================================================================"
echo "UET Framework Integration - Quick Start"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" ]; then
    echo -e "${RED}ERROR: Must run from repository root${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected: Contains README.md and UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/"
    exit 1
fi

echo -e "${YELLOW}[1/7]${NC} Checking prerequisites..."

# Check for Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python not found${NC}"
    exit 1
fi

# Check for UET framework
if [ ! -d "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" ]; then
    echo -e "${RED}ERROR: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Prerequisites OK"
echo ""

# Backup database
echo -e "${YELLOW}[2/7]${NC} Backing up database..."
if [ -f ".worktrees/pipeline_state.db" ]; then
    cp .worktrees/pipeline_state.db .worktrees/pipeline_state_backup_$(date +%Y%m%d_%H%M%S).db
    echo -e "${GREEN}✓${NC} Database backed up"
else
    echo -e "${YELLOW}⚠${NC} No existing database found (OK for fresh install)"
fi
echo ""

# Create directories
echo -e "${YELLOW}[3/7]${NC} Creating target directories..."
mkdir -p core/bootstrap_uet
mkdir -p core/engine/resilience
mkdir -p core/engine/monitoring
mkdir -p tests/uet_integration
mkdir -p schema/migrations
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Copy UET modules
echo -e "${YELLOW}[4/7]${NC} Copying UET modules..."

# Bootstrap
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/__init__.py core/bootstrap_uet/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/discovery.py core/bootstrap_uet/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/selector.py core/bootstrap_uet/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/generator.py core/bootstrap_uet/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/validator.py core/bootstrap_uet/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/orchestrator.py core/bootstrap_uet/

# Resilience
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/__init__.py core/engine/resilience/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/circuit_breaker.py core/engine/resilience/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/retry.py core/engine/resilience/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/resilient_executor.py core/engine/resilience/

# Monitoring
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/__init__.py core/engine/monitoring/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/progress_tracker.py core/engine/monitoring/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/run_monitor.py core/engine/monitoring/

echo -e "${GREEN}✓${NC} UET modules copied"
echo ""

# Copy schemas
echo -e "${YELLOW}[5/7]${NC} Copying schemas and profiles..."
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/project_profile.v1.json schema/
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/router_config.v1.json schema/
cp -r UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/profiles .
echo -e "${GREEN}✓${NC} Schemas and profiles copied"
echo ""

# Verify imports
echo -e "${YELLOW}[6/7]${NC} Verifying imports..."

python -c "from core.bootstrap_uet import ProjectScanner" 2>/dev/null && \
    echo -e "${GREEN}✓${NC} Bootstrap import OK" || \
    echo -e "${RED}✗${NC} Bootstrap import failed"

python -c "from core.engine.resilience import ResilientExecutor" 2>/dev/null && \
    echo -e "${GREEN}✓${NC} Resilience import OK" || \
    echo -e "${RED}✗${NC} Resilience import failed"

python -c "from core.engine.monitoring import ProgressTracker" 2>/dev/null && \
    echo -e "${GREEN}✓${NC} Monitoring import OK" || \
    echo -e "${RED}✗${NC} Monitoring import failed"

echo ""

# Summary
echo -e "${YELLOW}[7/7]${NC} Setup complete!"
echo ""
echo "======================================================================"
echo -e "${GREEN}UET Integration Day 1 Complete!${NC}"
echo "======================================================================"
echo ""
echo "What was installed:"
echo "  ✓ Bootstrap system (core/bootstrap_uet/)"
echo "  ✓ Resilience module (core/engine/resilience/)"
echo "  ✓ Monitoring module (core/engine/monitoring/)"
echo "  ✓ Schemas (schema/*.v1.json)"
echo "  ✓ Profiles (profiles/*)"
echo ""
echo "Next steps:"
echo "  1. Review generated structure:"
echo "     ls -R core/bootstrap_uet/ core/engine/resilience/ core/engine/monitoring/"
echo ""
echo "  2. Apply database migration:"
echo "     sqlite3 .worktrees/pipeline_state.db < schema/migrations/002_uet_foundation.sql"
echo ""
echo "  3. Create bootstrap wrapper (see docs/UET_WEEK1_IMPLEMENTATION.md Task 3.1)"
echo ""
echo "  4. Test bootstrap:"
echo "     python scripts/bootstrap_uet.py ."
echo ""
echo "  5. Run integration tests:"
echo "     pytest tests/uet_integration/test_bootstrap.py -v"
echo ""
echo "Documentation:"
echo "  • Quick Reference: docs/UET_QUICK_REFERENCE.md"
echo "  • Week 1 Plan: docs/UET_WEEK1_IMPLEMENTATION.md"
echo "  • Design Doc: docs/UET_INTEGRATION_DESIGN.md"
echo "  • Progress Tracker: docs/UET_PROGRESS_TRACKER.md"
echo ""
echo "======================================================================"
