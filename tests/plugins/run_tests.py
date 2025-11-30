"""
Test runner for error pipeline plugin tests.

Usage:
    pytest tests/plugins/                    # Run all plugin tests
    pytest tests/plugins/ -v                 # Verbose output
    pytest tests/plugins/ -k test_python     # Run only Python tests
    pytest tests/plugins/ --tb=short         # Short traceback
    pytest tests/plugins/ -x                 # Stop on first failure
"""
# DOC_ID: DOC-TEST-PLUGINS-RUN-TESTS-141
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import pytest
    
    # Run tests with common options
    sys.exit(pytest.main([
        "tests/plugins/",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-ra",  # Show summary of all test results
    ]))
