"""Pytest configuration and fixtures for UET tests."""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary test database."""
DOC_ID: DOC-TEST-TESTS-CONFTEST-072
DOC_ID: DOC-TEST-TESTS-CONFTEST-033
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Set environment variable
    os.environ['PIPELINE_DB_PATH'] = db_path
    
    # Initialize database
    from modules.core_state.m010003_db import init_db
    init_db(db_path)
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope="function")
def worker_pool(temp_db):
    """Create a worker pool with temp database."""
    from modules.core_engine.m010001_worker import WorkerPool
    return WorkerPool(max_workers=4)
