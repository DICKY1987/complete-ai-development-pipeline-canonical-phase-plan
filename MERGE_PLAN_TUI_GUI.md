# Merge Plan: tui_app/ → gui/

## Executive Summary

Merge the `tui_app/` directory (working TUI implementation) into the `gui/` directory (design documentation) to consolidate all UI-related code and documentation in one location.

## Current State Analysis

### tui_app/ Directory
**Purpose**: Working TUI implementation using Textual framework

**Contents**:
- ✅ **Working Python code** - Fully functional TUI application
- ✅ **5 Panel implementations** - dashboard, file_lifecycle, tool_health, log_stream, pattern_activity
- ✅ **Core framework** - PanelPlugin, PanelRegistry, StateClient, PatternClient
- ✅ **Configuration** - tui_config.yaml (theme, panel refresh rates, logs)
- ✅ **Tests** - Located in `tests/tui_panel_framework/`
- ✅ **Documentation** - README.md with usage instructions

**Key Files** (19 total):
```
tui_app/
├── __init__.py
├── main.py                      # Entry point
├── README.md                    # Usage docs
├── config/
│   ├── __init__.py
│   ├── layout_config.py         # Config models
│   └── tui_config.yaml          # Theme + refresh rates
├── core/
│   ├── __init__.py
│   ├── layout_manager.py        # Panel mounting
│   ├── panel_plugin.py          # Plugin protocol
│   ├── panel_registry.py        # Panel registration
│   ├── pattern_client.py        # Pattern data access
│   ├── sqlite_state_backend.py  # SQLite backend
│   └── state_client.py          # State access layer
└── panels/
    ├── __init__.py
    ├── dashboard_panel.py       # Pipeline summary
    ├── file_lifecycle_panel.py  # File tracking
    ├── log_stream_panel.py      # Log streaming
    ├── pattern_activity_panel.py # Pattern timeline
    └── tool_health_panel.py     # Tool status
```

### gui/ Directory
**Purpose**: Design documentation and specifications for GUI/TUI architecture

**Contents**:
- ✅ **Design documents** - 24 markdown files with architecture, specs, plans
- ✅ **Configuration** - ui_settings.yaml (tool modes, interactive settings)
- ✅ **Test file** - test_ui_settings.py (references `core.ui_settings` - not in tui_app)
- ❌ **No actual UI implementation** - All documentation only

**Key Files** (26 total):
```
gui/
├── README.md                    # GUI overview
├── CLAUDE.md                    # Project instructions
├── ui_settings.yaml             # Tool configuration
├── test_ui_settings.py          # Settings tests (references core.ui_settings)
└── [22 more .md/.txt files]     # Design docs
```

## Conflicts & Overlaps

### 1. README.md Files
- **tui_app/README.md**: Usage instructions for running TUI
- **gui/README.md**: Architecture overview and design principles
- **Resolution**: Merge content, keep both usage and design info

### 2. YAML Configuration Files
- **tui_app/config/tui_config.yaml**: Theme colors, panel refresh rates, log paths
- **gui/ui_settings.yaml**: Tool modes, interactive tool selection
- **Resolution**: Keep both - they configure different aspects
  - Rename `ui_settings.yaml` → `tool_settings.yaml` to clarify purpose
  - Keep `tui_config.yaml` for TUI-specific settings

### 3. test_ui_settings.py
- **Location**: Currently in `gui/`
- **Dependencies**: Imports `core.ui_settings` (doesn't exist in tui_app)
- **Resolution**: Move to `tests/gui/` and fix imports or remove if obsolete

## Merge Strategy

### Phase 1: Prepare gui/ Directory
1. Create subdirectories for organization:
   ```
   gui/
   ├── docs/          # Move all .md/.txt design docs here
   ├── config/        # Configuration files
   ├── tui_app/       # TUI implementation (from tui_app/)
   └── tests/         # Test files
   ```

### Phase 2: Move tui_app/ Contents
1. Move entire `tui_app/` directory → `gui/tui_app/`
2. Update all import paths from `tui_app.` to `gui.tui_app.`
3. Update test imports in `tests/tui_panel_framework/`

### Phase 3: Reorganize gui/ Files
1. Move all design docs to `gui/docs/`:
   - All .md files except README.md and CLAUDE.md
   - All .txt files
2. Move configurations:
   - `gui/ui_settings.yaml` → `gui/config/tool_settings.yaml`
   - Keep `gui/tui_app/config/tui_config.yaml` in place
3. Move tests:
   - `gui/test_ui_settings.py` → `gui/tests/test_tool_settings.py`

### Phase 4: Update Documentation
1. Merge README.md files:
   - Keep gui/README.md as main overview
   - Add section "TUI Implementation" with content from tui_app/README.md
2. Update CLAUDE.md with new structure
3. Update all documentation links to reflect new paths

### Phase 5: Update Imports & Tests
1. Search and replace import paths:
   - `from tui_app.` → `from gui.tui_app.`
   - `import tui_app.` → `import gui.tui_app.`
2. Update test paths in pytest configuration
3. Update main entry point references

### Phase 6: Cleanup
1. Remove empty `tui_app/` directory at root level
2. Update `.gitignore` if needed
3. Update any CI/CD scripts or documentation

## Detailed File Movements

### Documentation Files → gui/docs/
```bash
gui/AIM_ai-steward.md                                → gui/docs/AIM_ai-steward.md
gui/CURRENT_USER_INTERFACE.md                       → gui/docs/CURRENT_USER_INTERFACE.md
gui/GUI_DEVELOPMENT_GUIDE.md                        → gui/docs/GUI_DEVELOPMENT_GUIDE.md
gui/GUI_PIPELINE.txt                                 → gui/docs/GUI_PIPELINE.txt
gui/guifirstbigpromnt.txt                            → gui/docs/guifirstbigpromnt.txt
gui/Hybrid UI_GUI shell_terminal_TUI engine.md      → gui/docs/hybrid-ui-architecture.md
gui/IMPLEMENTATION_SUMMARY_UI_TOOL_SELECTION.md     → gui/docs/IMPLEMENTATION_SUMMARY_UI_TOOL_SELECTION.md
gui/module_outputs_and_visuals.md                   → gui/docs/module_outputs_and_visuals.md
gui/Pipeline Radar" plugin.md                       → gui/docs/pipeline-radar-plugin.md
gui/Plan Map coreStructure to engine Hybrid...md    → gui/docs/architecture-migration-plan.md
gui/PROJECT_UNIVERSAL_EXECUTION...README.md         → gui/docs/PROJECT_UET_FRAMEWORK_README.md
gui/Top-level layout split GUI vs Engine...md       → gui/docs/architecture-boundaries.md
gui/TUI_PANEL_FRAMEWORK_COMPLETION_REPORT.md        → gui/docs/TUI_PANEL_FRAMEWORK_COMPLETION_REPORT.md
gui/UI PAR DOC.txt                                   → gui/docs/UI_PAR_DOC.txt
gui/UI_DATA_REQUIREMENTS.md                         → gui/docs/UI_DATA_REQUIREMENTS.md
gui/UI_DOCUMENTATION_INDEX.md                       → gui/docs/UI_DOCUMENTATION_INDEX.md
gui/UI_DOCUMENTATION_SUMMARY.md                     → gui/docs/UI_DOCUMENTATION_SUMMARY.md
gui/UI_FLOW_DIAGRAM.md                              → gui/docs/UI_FLOW_DIAGRAM.md
gui/UI_IMPLEMENTATION_SUMMARY.md                    → gui/docs/UI_IMPLEMENTATION_SUMMARY.md
gui/UI_INTERACTIVE_TOOL_SELECTION.md                → gui/docs/UI_INTERACTIVE_TOOL_SELECTION.md
gui/UI_QUICK_REFERENCE.md                           → gui/docs/UI_QUICK_REFERENCE.md
gui/UI_TOOL_SELECTION_QUICK_REF.md                  → gui/docs/UI_TOOL_SELECTION_QUICK_REF.md
gui/UI_VISUAL_EXAMPLES.md                           → gui/docs/UI_VISUAL_EXAMPLES.md
```

### TUI Implementation → gui/tui_app/
```bash
tui_app/                    → gui/tui_app/
tui_app/__init__.py         → gui/tui_app/__init__.py
tui_app/main.py             → gui/tui_app/main.py
tui_app/README.md           → gui/tui_app/README.md
tui_app/config/             → gui/tui_app/config/
tui_app/core/               → gui/tui_app/core/
tui_app/panels/             → gui/tui_app/panels/
```

### Configuration Files
```bash
gui/ui_settings.yaml        → gui/config/tool_settings.yaml
tui_app/config/tui_config.yaml → gui/tui_app/config/tui_config.yaml (keep in place)
```

### Test Files
```bash
gui/test_ui_settings.py     → gui/tests/test_tool_settings.py
tests/tui_panel_framework/  → tests/gui/tui_panel_framework/
```

## Import Path Changes

### Python Files to Update
```python
# Before
from tui_app.core.panel_plugin import PanelPlugin
from tui_app.core.state_client import StateClient
import tui_app.panels

# After
from gui.tui_app.core.panel_plugin import PanelPlugin
from gui.tui_app.core.state_client import StateClient
import gui.tui_app.panels
```

### Entry Point Changes
```bash
# Before
python -m tui_app.main

# After
python -m gui.tui_app.main
```

## Final Directory Structure

```
gui/
├── README.md                      # Combined overview + usage
├── CLAUDE.md                      # Updated project instructions
├── .ai-module-manifest           # Existing
├── config/
│   └── tool_settings.yaml        # Renamed from ui_settings.yaml
├── docs/                          # NEW: All design documentation
│   ├── AIM_ai-steward.md
│   ├── CURRENT_USER_INTERFACE.md
│   ├── GUI_DEVELOPMENT_GUIDE.md
│   ├── architecture-boundaries.md
│   ├── architecture-migration-plan.md
│   ├── hybrid-ui-architecture.md
│   ├── pipeline-radar-plugin.md
│   ├── TUI_PANEL_FRAMEWORK_COMPLETION_REPORT.md
│   └── [15 more documentation files]
├── tests/                         # NEW: Test files
│   └── test_tool_settings.py
└── tui_app/                       # NEW: TUI implementation
    ├── __init__.py
    ├── main.py
    ├── README.md
    ├── config/
    │   ├── __init__.py
    │   ├── layout_config.py
    │   └── tui_config.yaml
    ├── core/
    │   ├── __init__.py
    │   ├── layout_manager.py
    │   ├── panel_plugin.py
    │   ├── panel_registry.py
    │   ├── pattern_client.py
    │   ├── sqlite_state_backend.py
    │   └── state_client.py
    └── panels/
        ├── __init__.py
        ├── dashboard_panel.py
        ├── file_lifecycle_panel.py
        ├── log_stream_panel.py
        ├── pattern_activity_panel.py
        └── tool_health_panel.py
```

## Validation Checklist

After merge, verify:
- [ ] All TUI files accessible at `gui/tui_app/`
- [ ] TUI still runs: `python -m gui.tui_app.main --smoke-test`
- [ ] All tests pass: `pytest tests/gui/`
- [ ] Documentation links updated
- [ ] No broken imports
- [ ] Configuration files loadable
- [ ] Git history preserved
- [ ] No duplicate files

## Risks & Mitigation

### Risk 1: Broken Imports
- **Impact**: TUI won't run, tests fail
- **Mitigation**: Comprehensive search/replace, run all tests
- **Rollback**: Git revert if needed

### Risk 2: Test Dependencies
- **Impact**: `test_ui_settings.py` references missing `core.ui_settings`
- **Mitigation**: Fix or remove obsolete tests
- **Rollback**: Skip tests temporarily

### Risk 3: Entry Point Changes
- **Impact**: Users can't run TUI with old command
- **Mitigation**: Update all documentation, add alias script
- **Rollback**: Symlink old path to new path

## Success Criteria

1. ✅ All TUI code moved to `gui/tui_app/`
2. ✅ All design docs organized in `gui/docs/`
3. ✅ TUI runs successfully with new import paths
4. ✅ All tests pass
5. ✅ Documentation updated and accurate
6. ✅ No orphaned files in old `tui_app/` directory
7. ✅ Git commit history preserved

## Execution Timeline

1. **Preparation** (5 min): Create directories, backup
2. **Move Files** (10 min): Execute file movements
3. **Update Imports** (15 min): Search/replace import paths
4. **Update Docs** (10 min): Merge READMEs, update links
5. **Testing** (10 min): Run smoke tests, full test suite
6. **Cleanup** (5 min): Remove old directory, verify
7. **Commit** (5 min): Git commit with detailed message

**Total Estimated Time**: 60 minutes

## Next Steps

1. Review this plan with user
2. Create feature branch for merge
3. Execute merge phases sequentially
4. Test thoroughly
5. Commit and push
6. Update any external documentation (if needed)
