#!/bin/bash
# DOC_LINK: DOC-SCRIPT-CHECK-WORKSTREAM-STATUS-282
# Workstream Status Checker
# Checks the completion status of all workstreams across PH-01, PH-02, PH-03

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        WORKSTREAM STATUS CHECKER - PH-01 to PH-03              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes (if terminal supports it)
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file exists in any location
check_file() {
    local file=$1

    # Check in current directory
    if [ -f "$file" ]; then
        echo -e "    ${GREEN}✅ EXISTS${NC}"
        return 0
    fi

    # Check in main branch
    if git show main:"$file" &>/dev/null; then
        echo -e "    ${GREEN}✅ EXISTS in main${NC}"
        return 0
    fi

    echo -e "    ${RED}❌ NOT FOUND${NC}"
    return 1
}

# Function to check if function is implemented
check_implementation() {
    local file=$1
    local function_name=$2

    # Check in current directory
    if [ -f "$file" ] && grep -q "def $function_name" "$file" 2>/dev/null; then
        echo -e "    ${GREEN}✅ IMPLEMENTED${NC}"
        return 0
    fi

    # Check in main branch
    if git show main:"$file" 2>/dev/null | grep -q "def $function_name"; then
        echo -e "    ${GREEN}✅ IMPLEMENTED in main${NC}"
        return 0
    fi

    echo -e "    ${RED}❌ STUB ONLY${NC}"
    return 1
}

# List all workstream branches
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ACTIVE WORKSTREAM BRANCHES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
workstream_branches=$(git branch -a | grep "workstream/" | sed 's/^[+ *]*/  /' | sed 's/remotes\/origin\///')
if [ -z "$workstream_branches" ]; then
    echo "  (none)"
else
    echo "$workstream_branches"
fi
echo ""

# List all worktrees
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ACTIVE WORKTREES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
worktrees=$(git worktree list | grep "ws-ph")
if [ -z "$worktrees" ]; then
    echo "  (none)"
else
    echo "$worktrees" | sed 's/^/  /'
fi
echo ""

# Check key files for each phase
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 KEY FILE IMPLEMENTATION STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# PH-01
echo "┌─ PHASE PH-01: Spec Alignment & Index Mapping"
echo "│"
echo "├─ ws-ph01-module-stubs (Codex):"
echo "│  └─ src/pipeline/ modules:"
check_file "src/pipeline/db.py"

echo "│"
echo "├─ ws-ph01-index-scanner (Codex):"
echo "│  └─ scripts/generate_spec_index.py:"
check_file "scripts/generate_spec_index.py"

echo "│"
echo "├─ ws-ph01-spec-mapping (Claude):"
echo "│  └─ docs/spec/spec_index_map.md:"
check_file "docs/spec/spec_index_map.md"

echo "│"
echo "├─ ws-ph01-tests (Claude):"
echo "│  └─ tests/pipeline/test_spec_index.py:"
check_file "tests/pipeline/test_spec_index.py"

echo "│"
echo "└─ ws-ph01-docs (Codex):"
echo "   └─ docs/ARCHITECTURE.md (updated):"
check_file "docs/ARCHITECTURE.md"

echo ""

# PH-02
echo "┌─ PHASE PH-02: Data Model & State Machine"
echo "│"
echo "├─ ws-ph02-schema (Codex):"
echo "│  └─ schema/schema.sql:"
check_file "schema/schema.sql"

echo "│"
echo "├─ ws-ph02-db-core (Codex):"
echo "│  └─ src/pipeline/db.py::get_connection():"
check_implementation "src/pipeline/db.py" "get_connection"

echo "│"
echo "├─ ws-ph02-state-machine (Claude):"
echo "│  └─ src/pipeline/db.py::validate_state_transition():"
check_implementation "src/pipeline/db.py" "validate_state_transition"

echo "│"
echo "├─ ws-ph02-crud (Claude):"
echo "│  └─ src/pipeline/db.py::create_run():"
check_implementation "src/pipeline/db.py" "create_run"

echo "│"
echo "├─ ws-ph02-scripts (Codex):"
echo "│  └─ scripts/init_db.py:"
check_file "scripts/init_db.py"

echo "│"
echo "├─ ws-ph02-docs (Codex):"
echo "│  └─ docs/state_machine.md:"
check_file "docs/state_machine.md"

echo "│"
echo "└─ ws-ph02-tests (Claude):"
echo "   └─ tests/pipeline/test_db_state.py:"
check_file "tests/pipeline/test_db_state.py"

echo ""

# PH-03
echo "┌─ PHASE PH-03: Tool Profiles & Adapter Layer"
echo "│"
echo "├─ ws-ph03-profiles (Codex):"
echo "│  └─ config/tool_profiles.json:"
check_file "config/tool_profiles.json"

echo "│"
echo "├─ ws-ph03-adapter-core (Claude):"
echo "│  └─ src/pipeline/tools.py::run_tool():"
check_implementation "src/pipeline/tools.py" "run_tool"

echo "│"
echo "├─ ws-ph03-db-integration (Claude):"
echo "│  └─ src/pipeline/tools.py (with DB calls):"
if [ -f "src/pipeline/tools.py" ] && grep -q "record_event\|record_error" "src/pipeline/tools.py" 2>/dev/null; then
    echo -e "    ${GREEN}✅ INTEGRATED${NC}"
elif git show main:"src/pipeline/tools.py" 2>/dev/null | grep -q "record_event\|record_error"; then
    echo -e "    ${GREEN}✅ INTEGRATED in main${NC}"
else
    echo -e "    ${RED}❌ NOT INTEGRATED${NC}"
fi

echo "│"
echo "├─ ws-ph03-tests (Claude):"
echo "│  └─ tests/pipeline/test_tools.py:"
check_file "tests/pipeline/test_tools.py"

echo "│"
echo "└─ ws-ph03-docs (Codex):"
echo "   └─ docs/PHASE_PLAN.md (updated):"
check_file "docs/PHASE_PLAN.md"

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
total_branches=$(git branch -a | grep -c "workstream/" || echo "0")
total_worktrees=$(git worktree list | grep -c "ws-ph" || echo "0")
echo "  Total workstream branches: $total_branches / 17"
echo "  Active worktrees: $total_worktrees"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
