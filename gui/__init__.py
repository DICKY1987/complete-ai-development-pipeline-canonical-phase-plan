"""GUI package - re-exports from src/ for backward compatibility.

This allows tests to import from gui.tui_app, gui.gui_app, etc.
even though the actual modules are in gui/src/
"""

# Re-export src modules for backward compatibility
try:
    from .src import tui_app, gui_app, ui_core, textual
except ImportError:
    # If src modules aren't available, that's okay
    pass
