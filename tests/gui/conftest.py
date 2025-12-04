"""GUI tests configuration - adds gui/src to path for imports."""

import sys
from pathlib import Path

# Add gui/src to Python path so 'from gui.tui_app' works
gui_src = Path(__file__).parent.parent.parent / 'gui' / 'src'
if str(gui_src) not in sys.path:
    sys.path.insert(0, str(gui_src))
# DOC_LINK: DOC-TEST-GUI-CONFTEST-305
