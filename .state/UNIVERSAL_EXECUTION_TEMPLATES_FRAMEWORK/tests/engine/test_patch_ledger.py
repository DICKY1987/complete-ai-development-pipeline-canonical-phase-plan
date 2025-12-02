"""
Tests for PatchLedger state machine and tracking.

Tests patch creation, validation, application, verification,
commit, rollback, and quarantine workflows.

Author: AI Development Pipeline
Created: 2025-11-23
WS: WS-NEXT-002-002 (Testing)
"""
# DOC_ID: DOC-TEST-ENGINE-TEST-PATCH-LEDGER-174

import pytest
import sys
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.patch_ledger import PatchLedger, ValidationResult


class MockDB:
    """Mock database for testing"""
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize test schema"""
        # Create runs table (for foreign key)
        self.conn.execute("""
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY
            )
        """)
        
        # Create patch_ledger table
        schema_path = Path(__file__).parent.parent.parent / 'schema' / 'migrations' / '003_add_patch_ledger_table.sql'
        with open(schema_path, 'r') as f:
            self.conn.executescript(f.read())
        self.conn.commit()


@pytest.fixture
def db():
    """Create test database"""
    return MockDB()


@pytest.fixture
def ledger(db):
    """Create PatchLedger instance"""
    return PatchLedger(db)


@pytest.fixture
def ledger_id():
    """Generate test ledger ID"""
    return "01HQLEDGER000000000000001"


@pytest.fixture
def patch_id():
    """Generate test patch ID"""
    return "01HQPATCH0000000000000001"


@pytest.fixture
def project_id():
    """Generate test project ID"""
    return "test-project"


class TestValidationResult:
    """Test ValidationResult dataclass"""
    
    def test_initial_validation(self):
        """Test initial validation is all false"""
        result = ValidationResult()
        assert result.format_ok is False
        assert result.scope_ok is False
        assert result.constraints_ok is False
        assert result.tests_ran is False
        assert result.tests_passed is False
        assert result.validation_errors == []
    
    def test_is_valid_all_pass(self):
        """Test is_valid when all checks pass"""
        result = ValidationResult(
            format_ok=True,
            scope_ok=True,
            constraints_ok=True
        )
        assert result.is_valid is True
    
    def test_is_valid_one_fail(self):
        """Test is_valid when one check fails"""
        result = ValidationResult(
            format_ok=True,
            scope_ok=False,
            constraints_ok=True
        )
        assert result.is_valid is False
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = ValidationResult(
            format_ok=True,
            scope_ok=True,
            constraints_ok=False,
            validation_errors=['Scope too large']
        )
        data = result.to_dict()
        
        assert data['format_ok'] is True
        assert data['scope_ok'] is True
        assert data['constraints_ok'] is False
        assert data['validation_errors'] == ['Scope too large']


class TestEntryCreation:
    """Test ledger entry creation"""
    
    def test_create_entry(self, ledger, ledger_id, patch_id, project_id):
        """Test creating a new entry"""
        result = ledger.create_entry(
            ledger_id=ledger_id,
            patch_id=patch_id,
            project_id=project_id
        )
        
        assert result == ledger_id
        
        # Verify entry was created
        entry = ledger.get_entry(ledger_id)
        assert entry is not None
        assert entry['ledger_id'] == ledger_id
        assert entry['patch_id'] == patch_id
        assert entry['project_id'] == project_id
        assert entry['state'] == 'created'
    
    def test_create_entry_with_validation(self, ledger, ledger_id, patch_id, project_id):
        """Test creating entry with validation result"""
        validation = ValidationResult(
            format_ok=True,
            scope_ok=True,
            constraints_ok=True
        )
        
        ledger.create_entry(
            ledger_id=ledger_id,
            patch_id=patch_id,
            project_id=project_id,
            validation=validation
        )
        
        entry = ledger.get_entry(ledger_id)
        assert entry['validation']['format_ok'] is True
        assert entry['validation']['scope_ok'] is True
    
    def test_create_entry_with_workstream(self, ledger, ledger_id, patch_id, project_id):
        """Test creating entry with workstream info"""
        ledger.create_entry(
            ledger_id=ledger_id,
            patch_id=patch_id,
            project_id=project_id,
            phase_id="PH-001",
            workstream_id="WS-001-001"
        )
        
        entry = ledger.get_entry(ledger_id)
        assert entry['phase_id'] == "PH-001"
        assert entry['workstream_id'] == "WS-001-001"
    
    def test_create_entry_state_history(self, ledger, ledger_id, patch_id, project_id):
        """Test entry has initial state history"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        entry = ledger.get_entry(ledger_id)
        assert len(entry['state_history']) == 1
        assert entry['state_history'][0]['state'] == 'created'
        assert entry['state_history'][0]['reason'] == 'Initial creation'


class TestEntryRetrieval:
    """Test entry retrieval"""
    
    def test_get_entry(self, ledger, ledger_id, patch_id, project_id):
        """Test getting an entry by ID"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        entry = ledger.get_entry(ledger_id)
        
        assert entry is not None
        assert entry['ledger_id'] == ledger_id
    
    def test_get_nonexistent_entry(self, ledger):
        """Test getting an entry that doesn't exist"""
        entry = ledger.get_entry('nonexistent')
        assert entry is None


class TestPatchValidation:
    """Test patch validation"""
    
    def test_validate_patch_success(self, ledger, ledger_id, patch_id, project_id):
        """Test validating patch successfully"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        validation = ValidationResult(
            format_ok=True,
            scope_ok=True,
            constraints_ok=True
        )
        
        result = ledger.validate_patch(ledger_id, validation)
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'validated'
        assert entry['validation']['format_ok'] is True
    
    def test_validate_patch_failure(self, ledger, ledger_id, patch_id, project_id):
        """Test patch validation failure"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        validation = ValidationResult(
            format_ok=True,
            scope_ok=False,
            constraints_ok=True,
            validation_errors=['Scope exceeds limits']
        )
        
        ledger.validate_patch(ledger_id, validation)
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'apply_failed'
        assert entry['validation']['scope_ok'] is False
    
    def test_validate_nonexistent_entry(self, ledger):
        """Test validating nonexistent entry"""
        validation = ValidationResult()
        with pytest.raises(ValueError, match="Ledger entry not found"):
            ledger.validate_patch('nonexistent', validation)
    
    def test_validate_updates_history(self, ledger, ledger_id, patch_id, project_id):
        """Test validation updates state history"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        
        entry = ledger.get_entry(ledger_id)
        assert len(entry['state_history']) == 2
        assert entry['state_history'][1]['state'] == 'validated'


class TestPatchQueuing:
    """Test patch queuing"""
    
    def test_queue_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test queuing a validated patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        
        result = ledger.queue_patch(ledger_id)
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'queued'
    
    def test_queue_nonvalidated_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test cannot queue non-validated patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        with pytest.raises(ValueError, match="Cannot queue"):
            ledger.queue_patch(ledger_id)


class TestPatchApplication:
    """Test patch application"""
    
    def test_apply_patch_success(self, ledger, ledger_id, patch_id, project_id):
        """Test applying patch successfully"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        
        result = ledger.apply_patch(
            ledger_id,
            success=True,
            workspace_path="/tmp/workspace",
            applied_files=["file1.py", "file2.py"]
        )
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'applied'
        assert entry['apply']['workspace_path'] == "/tmp/workspace"
        assert len(entry['apply']['applied_files']) == 2
    
    def test_apply_patch_failure(self, ledger, ledger_id, patch_id, project_id):
        """Test applying patch with failure"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        
        ledger.apply_patch(
            ledger_id,
            success=False,
            error_code="PATCH_001",
            error_message="Failed to apply patch"
        )
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'apply_failed'
        assert entry['apply']['last_error_code'] == "PATCH_001"
    
    def test_apply_increments_attempts(self, ledger, ledger_id, patch_id, project_id):
        """Test apply increments attempt counter"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        
        ledger.apply_patch(ledger_id, success=False, error_message="First attempt failed")
        
        entry = ledger.get_entry(ledger_id)
        assert entry['apply']['attempts'] == 1
        
        # Retry
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        
        entry = ledger.get_entry(ledger_id)
        assert entry['apply']['attempts'] == 2


class TestPatchVerification:
    """Test patch verification"""
    
    def test_verify_patch_success(self, ledger, ledger_id, patch_id, project_id):
        """Test verifying patch with passing tests"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        
        result = ledger.verify_patch(ledger_id, tests_passed=True)
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'verified'
    
    def test_verify_patch_failure(self, ledger, ledger_id, patch_id, project_id):
        """Test verifying patch with failing tests"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        
        ledger.verify_patch(ledger_id, tests_passed=False)
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'apply_failed'


class TestPatchCommit:
    """Test patch commit"""
    
    def test_commit_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test committing verified patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        ledger.verify_patch(ledger_id, tests_passed=True)
        
        result = ledger.commit_patch(ledger_id)
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'committed'
    
    def test_commit_nonverified_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test cannot commit non-verified patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        with pytest.raises(ValueError, match="Cannot commit"):
            ledger.commit_patch(ledger_id)


class TestPatchRollback:
    """Test patch rollback"""
    
    def test_rollback_applied_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test rolling back applied patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        
        result = ledger.rollback_patch(ledger_id, "Breaking change detected")
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'rolled_back'
    
    def test_rollback_verified_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test rolling back verified patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        ledger.verify_patch(ledger_id, tests_passed=True)
        
        ledger.rollback_patch(ledger_id, "Critical bug found")
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'rolled_back'


class TestPatchQuarantine:
    """Test patch quarantine"""
    
    def test_quarantine_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test quarantining a patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        result = ledger.quarantine_patch(
            ledger_id,
            reason="Security concern",
            quarantine_path="/quarantine/patch001"
        )
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'quarantined'
        assert entry['quarantine']['is_quarantined'] is True
        assert entry['quarantine']['quarantine_reason'] == "Security concern"
    
    def test_quarantine_from_any_state(self, ledger, ledger_id, patch_id, project_id):
        """Test can quarantine from any non-terminal state"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        ledger.queue_patch(ledger_id)
        
        # Quarantine from queued state
        ledger.quarantine_patch(ledger_id, "Malicious code detected")
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'quarantined'


class TestPatchDrop:
    """Test patch drop/reject"""
    
    def test_drop_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test dropping a patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        result = ledger.drop_patch(ledger_id, "Duplicate patch")
        assert result is True
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'dropped'
    
    def test_drop_quarantined_patch(self, ledger, ledger_id, patch_id, project_id):
        """Test dropping quarantined patch"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        ledger.quarantine_patch(ledger_id, "Security concern")
        
        ledger.drop_patch(ledger_id, "Cannot be safely applied")
        
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'dropped'


class TestEntryListing:
    """Test entry listing and filtering"""
    
    def test_list_entries_empty(self, ledger):
        """Test listing entries when none exist"""
        entries = ledger.list_entries()
        assert len(entries) == 0
    
    def test_list_all_entries(self, ledger, patch_id, project_id):
        """Test listing all entries"""
        for i in range(3):
            ledger_id = f"01HQLEDGER00000000000000{i}"
            ledger.create_entry(ledger_id, patch_id, project_id)
        
        entries = ledger.list_entries()
        assert len(entries) == 3
    
    def test_list_entries_by_project(self, ledger, patch_id):
        """Test filtering entries by project"""
        ledger.create_entry("01HQLEDGER000000000000001", patch_id, "project-a")
        ledger.create_entry("01HQLEDGER000000000000002", patch_id, "project-b")
        ledger.create_entry("01HQLEDGER000000000000003", patch_id, "project-a")
        
        entries = ledger.list_entries(project_id="project-a")
        assert len(entries) == 2
    
    def test_list_entries_by_state(self, ledger, patch_id, project_id):
        """Test filtering entries by state"""
        ledger.create_entry("01HQLEDGER000000000000001", patch_id, project_id)
        ledger.create_entry("01HQLEDGER000000000000002", patch_id, project_id)
        
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch("01HQLEDGER000000000000001", validation)
        
        validated = ledger.list_entries(state='validated')
        created = ledger.list_entries(state='created')
        
        assert len(validated) == 1
        assert len(created) == 1
    
    def test_list_entries_by_workstream(self, ledger, patch_id, project_id):
        """Test filtering entries by workstream"""
        ledger.create_entry("01HQLEDGER000000000000001", patch_id, project_id, workstream_id="WS-001")
        ledger.create_entry("01HQLEDGER000000000000002", patch_id, project_id, workstream_id="WS-002")
        
        entries = ledger.list_entries(workstream_id="WS-001")
        assert len(entries) == 1


class TestStateTransitions:
    """Test state machine transitions"""
    
    def test_terminal_states_immutable(self, ledger):
        """Test that terminal states cannot transition"""
        assert not ledger._can_transition('committed', 'validated')
        assert not ledger._can_transition('rolled_back', 'validated')
        assert not ledger._can_transition('dropped', 'validated')
    
    def test_valid_transitions(self, ledger):
        """Test all valid state transitions"""
        # created -> validated
        assert ledger._can_transition('created', 'validated') is True
        
        # validated -> queued
        assert ledger._can_transition('validated', 'queued') is True
        
        # queued -> applied
        assert ledger._can_transition('queued', 'applied') is True
        
        # applied -> verified
        assert ledger._can_transition('applied', 'verified') is True
        
        # verified -> committed
        assert ledger._can_transition('verified', 'committed') is True
        
        # any -> quarantined
        assert ledger._can_transition('created', 'quarantined') is True
        assert ledger._can_transition('applied', 'quarantined') is True
    
    def test_invalid_transitions(self, ledger):
        """Test invalid state transitions"""
        # Cannot go directly from created to applied
        assert ledger._can_transition('created', 'applied') is False
        
        # Cannot go from committed to anything
        assert ledger._can_transition('committed', 'queued') is False
    
    def test_is_terminal(self):
        """Test terminal state detection"""
        assert PatchLedger.is_terminal('committed') is True
        assert PatchLedger.is_terminal('rolled_back') is True
        assert PatchLedger.is_terminal('dropped') is True
        assert PatchLedger.is_terminal('created') is False
        assert PatchLedger.is_terminal('applied') is False


class TestCompleteWorkflow:
    """Test complete patch workflows"""
    
    def test_successful_patch_workflow(self, ledger, ledger_id, patch_id, project_id):
        """Test complete successful patch workflow"""
        # Create
        ledger.create_entry(ledger_id, patch_id, project_id)
        assert ledger.get_entry(ledger_id)['state'] == 'created'
        
        # Validate
        validation = ValidationResult(format_ok=True, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        assert ledger.get_entry(ledger_id)['state'] == 'validated'
        
        # Queue
        ledger.queue_patch(ledger_id)
        assert ledger.get_entry(ledger_id)['state'] == 'queued'
        
        # Apply
        ledger.apply_patch(ledger_id, success=True, workspace_path="/tmp")
        assert ledger.get_entry(ledger_id)['state'] == 'applied'
        
        # Verify
        ledger.verify_patch(ledger_id, tests_passed=True)
        assert ledger.get_entry(ledger_id)['state'] == 'verified'
        
        # Commit
        ledger.commit_patch(ledger_id)
        entry = ledger.get_entry(ledger_id)
        assert entry['state'] == 'committed'
        
        # Check state history
        assert len(entry['state_history']) == 6  # created + 5 transitions
    
    def test_failed_patch_workflow(self, ledger, ledger_id, patch_id, project_id):
        """Test patch workflow with failures"""
        ledger.create_entry(ledger_id, patch_id, project_id)
        
        # Validation fails
        validation = ValidationResult(format_ok=False, scope_ok=True, constraints_ok=True)
        ledger.validate_patch(ledger_id, validation)
        assert ledger.get_entry(ledger_id)['state'] == 'apply_failed'
        
        # Drop the patch
        ledger.drop_patch(ledger_id, "Validation failed")
        assert ledger.get_entry(ledger_id)['state'] == 'dropped'
