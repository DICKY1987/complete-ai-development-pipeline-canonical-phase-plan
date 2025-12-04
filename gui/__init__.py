"""GUI package - re-exports from src/ for backward compatibility.

This allows tests to import from gui.tui_app, gui.gui_app, etc.
even though the actual modules are in gui/src/
"""
DOC_ID: DOC-CORE-GUI-INIT-605

DOC_ID: DOC - CORE - GUI - INIT - 605

# Re-export src modules for backward compatibility
try:
    from .src import gui_app, textual, tui_app, ui_core
except ImportError:
    # If src modules aren't available, that's okay
    pass
