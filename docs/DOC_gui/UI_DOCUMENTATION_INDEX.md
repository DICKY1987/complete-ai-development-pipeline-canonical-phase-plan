---
doc_id: DOC-GUIDE-UI-DOCUMENTATION-INDEX-800
---

# UI Documentation Index

This directory contains documentation for the AI Development Pipeline user interfaces.

## Core Documentation

### TUI (Terminal User Interface)

- **[TUI Panel Framework Guide](TUI_PANEL_FRAMEWORK_GUIDE.md)** - Complete guide to the Textual-based TUI framework
  - Architecture overview
  - How to add new panels
  - StateClient and PatternClient usage
  - Testing panels

## Quick Links

### Getting Started

```bash
# Launch TUI with dashboard
python -m gui.tui_app.main

# Launch with pattern activity panel
python -m gui.tui_app.main --panel pattern_activity

# Run smoke test
python -m gui.tui_app.main --smoke-test
```

### Running Tests

```bash
# Test TUI framework
pytest tests/tui_panel_framework -q
```

## Architecture Overview

The TUI framework is **TUI-first**, meaning:
- Core functionality implemented in Textual
- GUI wrapper is optional and thin
- Panels are self-contained plugins
- State/pattern clients have pluggable backends

### Current Panels

| Panel | Status | Purpose |
|-------|--------|---------|
| Dashboard | ✓ Complete | Pipeline summary and recent tasks |
| File Lifecycle | Skeleton | Track files through pipeline stages |
| Tool Health | Skeleton | Monitor error detection tools |
| Log Stream | Skeleton | Real-time pipeline logs |
| Pattern Activity | ✓ Complete | Visualize pattern execution |

## Contributing

When adding new panels:
1. Follow the PanelPlugin protocol
2. Use `@register_panel("panel_id")` decorator
3. Add tests in `tests/tui_panel_framework/`
4. Update this index

## Related Documentation

- See `tui_app/README.md` for quick start guide
- See individual panel files for implementation details
