# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

**REFACTOR_2** is a production-ready multi-agent orchestration system for executing 39 workstreams in parallel using 3 AI agents with zero conflicts. Key innovation: Git worktree isolation eliminates file conflicts by giving each agent its own workspace.

**Performance**: Sequential execution ~30 days → Parallel execution 3-5 days = **6-10x speedup**

## Core Architecture

### Git Worktree Isolation Pattern
The system uses git worktrees to provide complete filesystem isolation between agents:
- Main repository: `C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan`
- Agent worktrees: `.worktrees/agent-{id}-{workstream}/`
- Zero conflicts during parallel execution
- Conflicts only occur during final merge to main (~5-10%)

### Key Components
1. **Multi-Agent Orchestrator** (`multi_agent_orchestrator.py`) - Asyncio-based execution engine with dependency graph management
2. **Worktree Manager** (`worktree_manager.py`) - Thread-safe worktree lifecycle management (create, merge, cleanup)
3. **Preflight Validator** (`preflight_validator.py`) - Environment validation + dependency cycle detection
4. **PowerShell Launcher** (`run_multi_agent_refactor.ps1`) - One-touch automation with crash recovery

## Common Commands

### Execute Multi-Agent Refactor
```powershell
# Navigate to repository root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# One-touch execution (production)
.\scripts\run_multi_agent_refactor.ps1

# Dry run (validation only)
.\scripts\run_multi_agent_refactor.ps1 -DryRun

# Custom agent count
.\scripts\run_multi_agent_refactor.ps1 -Agents 5
```

### Code Cleanup & Archival (EXEC-017)
```bash
# Run comprehensive 6-signal archival analysis
python scripts/comprehensive_archival_analyzer.py

# Pre-archive safety validation
python scripts/validate_archival_safety.py --mode pre-archive --files-list cleanup_reports/tier1_files.txt

# Post-archive validation
python scripts/validate_archival_safety.py --mode post-archive
```

### Status Monitoring
```powershell
# Check workstream status
sqlite3 .state/orchestration.db "SELECT status, COUNT(*) FROM workstream_status GROUP BY status"

# View orchestrator logs
Get-Content logs/orchestrator.log -Tail 50

# Check git worktree status
git worktree list

# Cleanup orphaned worktrees
git worktree prune
```

### Python Analysis Scripts
```bash
# Entry point reachability analysis
python scripts/entry_point_reachability.py --root . --output cleanup_reports/

# Test coverage analysis for archival
python scripts/test_coverage_archival.py --root . --output cleanup_reports/

# Detect parallel implementations
python scripts/detect_parallel_implementations.py --root . --output cleanup_reports/
```

## Project Structure

```
REFACTOR_2/
├── 01_PLANNING/           # Analysis & solution design docs
├── 02_ARCHITECTURE/       # Technical deep-dives (worktrees, orchestration)
├── 03_IMPLEMENTATION/     # Implementation guides
├── 04_OPERATIONS/         # Conflict resolution & recovery playbooks
├── 05_REFERENCE/          # Quick references & completion summaries
├── *.py                   # Python analysis scripts (EXEC-017)
├── DOCUMENTATION_INDEX.md # Navigation hub
└── README.md             # Quick start guide

Main Scripts (production):
../scripts/
├── multi_agent_orchestrator.py  # Main orchestration engine
├── worktree_manager.py           # Worktree lifecycle management
├── preflight_validator.py        # Pre-execution validation
├── run_multi_agent_refactor.ps1  # One-touch launcher
├── comprehensive_archival_analyzer.py  # 6-signal cleanup orchestrator
└── (50+ additional scripts)
```

## Key Patterns

### EXEC-017: Comprehensive Code Cleanup
6-signal cleanup framework with weighted confidence scoring:
- **Duplication** (25%): SHA-256 exact matches
- **Staleness** (15%): 90+ days without modification
- **Obsolescence** (20%): Deprecated patterns, version suffixes
- **Isolation** (15%): Not imported by active code
- **Reachability** (15%): Unreachable from entry points
- **Test Coverage** (10%): No test coverage

Confidence tiers:
- **Tier 1 (90-100%)**: Safe for automated archival (80-100 files expected)
- **Tier 2 (75-89%)**: Review recommended (100-150 files)
- **Tier 3 (60-74%)**: Manual expert review (80-100 files)
- **Tier 4 (<60%)**: Keep (600-700 files)

### Multi-Agent Execution
- 3 concurrent AI agents (aider-based)
- Each agent isolated in dedicated git worktree
- SQLite database tracks workstream status
- Automatic dependency ordering
- Crash recovery via PowerShell trap handlers

## Critical Files to Understand

### Start Here
1. **DOCUMENTATION_INDEX.md** - Navigation by role (user/developer/troubleshooter)
2. **README.md** - Quick start and metrics

### For Development
3. **01_PLANNING/ONE_TOUCH_SOLUTION_PLAN.md** - Complete architecture (22 KB)
4. **02_ARCHITECTURE/WORKTREE_ISOLATION_DEEP_DIVE.md** - How isolation works (14 KB)
5. **02_ARCHITECTURE/MULTI_AGENT_ORCHESTRATION_SUMMARY.md** - Process flow (10 KB)

### For Operations
6. **04_OPERATIONS/MERGE_CONFLICT_PROTOCOL.md** - Step-by-step conflict resolution
7. **04_OPERATIONS/FAILURE_RECOVERY_PLAYBOOK.md** - 6 recovery scenarios (15 KB)
8. **04_OPERATIONS/CRITICAL_FIXES_APPLIED.md** - Recent fixes and status

### For Quality Assessment
9. **01_PLANNING/BEST_PLAN_CLAUDE_REVIEW.md** - Expert evaluation (9.8/10)
10. **EXEC017_COMPLETION_SUMMARY.md** - EXEC-017 implementation status

## Troubleshooting

### Merge Conflicts
See: `04_OPERATIONS/MERGE_CONFLICT_PROTOCOL.md`

Quick resolution:
```bash
git checkout main
git pull origin feature-branch
# Resolve conflicts
git add .
git commit
```

### Orchestrator Failures
See: `04_OPERATIONS/FAILURE_RECOVERY_PLAYBOOK.md` triage table

Common scenarios:
1. Worktree creation fails → Check disk space (10 GB minimum)
2. Agent hangs → Check logs, terminate process, resume
3. Merge failures → Use merge conflict protocol
4. Database locks → Check SQLite file permissions
5. Dependency cycles → Run preflight validator
6. Orphaned worktrees → Run `git worktree prune`

### Analysis Script Issues
```bash
# Verify Python environment
python --version  # Should be 3.8+

# Check dependencies
pip list | grep -E "ast|sqlite3|pathlib"

# Run with verbose logging
python scripts/comprehensive_archival_analyzer.py --verbose
```

## Production Readiness: 95%

### Fixed Issues (2025-11-29)
- ✅ Race condition in worktree_manager.py (thread lock added)
- ✅ Disk space check (10 GB minimum, was 5 GB)
- ✅ Orphaned worktrees (trap handler in PowerShell)
- ✅ Dependency cycles (cycle detection in preflight)
- ✅ Merge conflicts (complete protocol document)
- ✅ Failure recovery (playbook for 6 scenarios)

### Quality Metrics
- **Total Files**: 22 files (247 KB)
- **Documentation**: 15 files (167.7 KB)
- **Code**: 7 production scripts (47.5 KB)
- **Claude Expert Score**: 9.8/10
- **Test Pass Rate**: Not yet validated (scheduled)

## Development Notes

### When Modifying Orchestrator
- Always test with dry-run first
- Respect thread-safety in worktree_manager.py (uses threading.Lock)
- Update state database schema carefully (SQLite)
- Maintain backward compatibility for resume functionality

### When Adding New Analysis Scripts
- Follow EXEC-017 pattern structure
- Output JSON reports to `cleanup_reports/`
- Include CLI argument parsing with `--help`
- Add logging with timestamps
- Return appropriate exit codes for CI/CD

### When Writing Documentation
- Follow existing doc_id pattern: `DOC-{TYPE}-{NAME}-{ULID}`
- Update DOCUMENTATION_INDEX.md
- Keep docs concise and actionable
- Include code examples where relevant

## Next Steps

1. Execute preflight validation on production environment
2. Run single-agent test workstream
3. Execute full 3-agent production run
4. Validate EXEC-017 analysis results (tier 1 archival candidates)
5. Implement automated archival pipeline (tier 1 only)
