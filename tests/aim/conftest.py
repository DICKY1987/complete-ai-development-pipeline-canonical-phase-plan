"""Test configuration for AIM+ tests."""

import pytest
from pathlib import Path

# Skip all AIM tests - Phase 4 functionality not yet implemented
# AIM module will be integrated in Phase 4
# See: phase4_routing/modules/aim_tools/ for work-in-progress implementation
pytestmark = pytest.mark.skip(reason="AIM module not yet implemented - Phase 4 roadmap item")

# Test fixtures will be added here as needed
# DOC_LINK: DOC-TEST-AIM-CONFTEST-170
