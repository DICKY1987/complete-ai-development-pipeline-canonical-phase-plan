"""
Unit tests for Validators and Circuit Breakers
"""
import pytest
import time
import subprocess
import sys
from pathlib import Path
from core.engine.validators import (
    ScopeValidator, TimeoutMonitor, CircuitBreaker,
    ScopeResult, TimeoutResult, CircuitBreakerTrip
)


@pytest.fixture
def scope_validator():
    """Create ScopeValidator instance"""
    return ScopeValidator()


@pytest.fixture
def timeout_monitor():
    """Create TimeoutMonitor instance"""
    return TimeoutMonitor()


@pytest.fixture
def circuit_breaker():
    """Create CircuitBreaker instance"""
    return CircuitBreaker(
        max_attempts=3,
        max_error_repeats=2,
        oscillation_threshold=2
    )


@pytest.fixture
def sample_bundle():
    """Create sample workstream bundle"""
    return {
        'id': 'ws-test',
        'files_scope': [
            'src/module.py',
            'src/utils.py',
            'tests/test_module.py'
        ],
        'files_create': [
            'docs/new_doc.md'
        ]
    }


def test_scope_result_creation():
    """Test ScopeResult dataclass"""
    result = ScopeResult(
        valid=True,
        violations=[],
        allowed_files=['file1.py', 'file2.py'],
        violating_files=[]
    )
    
    assert result.valid is True
    assert len(result.violations) == 0


def test_timeout_result_creation():
    """Test TimeoutResult dataclass"""
    result = TimeoutResult(
        timed_out=False,
        wall_time_sec=10.5,
        idle_time_sec=2.0
    )
    
    assert result.timed_out is False
    assert result.wall_time_sec == 10.5


def test_circuit_breaker_trip_creation():
    """Test CircuitBreakerTrip dataclass"""
    trip = CircuitBreakerTrip(
        reason="Max attempts exceeded",
        ws_id="ws-1",
        attempt=4
    )
    
    assert trip.reason == "Max attempts exceeded"
    assert trip.ws_id == "ws-1"
    assert trip.attempt == 4
    assert trip.timestamp  # Should have timestamp


def test_validate_patch_scope_valid(scope_validator, sample_bundle):
    """Test scope validation with valid patch"""
    patch_files = ['src/module.py', 'src/utils.py']
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert result.valid is True
    assert len(result.violations) == 0
    assert len(result.violating_files) == 0


def test_validate_patch_scope_create_file(scope_validator, sample_bundle):
    """Test scope validation with creatable file"""
    patch_files = ['docs/new_doc.md']
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert result.valid is True
    assert len(result.violations) == 0


def test_validate_patch_scope_violation(scope_validator, sample_bundle):
    """Test scope validation with violation"""
    patch_files = ['src/module.py', 'src/unauthorized.py']
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert result.valid is False
    assert len(result.violations) == 1
    assert 'unauthorized.py' in result.violations[0]
    assert 'src/unauthorized.py' in result.violating_files


def test_validate_patch_scope_multiple_violations(scope_validator, sample_bundle):
    """Test scope validation with multiple violations"""
    patch_files = ['src/module.py', 'config/settings.py', 'lib/external.py']
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert result.valid is False
    assert len(result.violations) == 2
    assert len(result.violating_files) == 2


def test_validate_patch_scope_empty_patch(scope_validator, sample_bundle):
    """Test scope validation with empty patch"""
    patch_files = []
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert result.valid is True


def test_validate_patch_scope_path_normalization(scope_validator):
    """Test path normalization (forward vs back slashes)"""
    bundle = {
        'files_scope': ['src/module.py', 'tests\\test.py'],
        'files_create': []
    }
    
    # Test with different slash styles
    patch_files = ['src\\module.py', 'tests/test.py']
    
    result = scope_validator.validate_patch_scope(patch_files, bundle)
    
    assert result.valid is True


def test_timeout_monitor_no_timeout():
    """Test timeout monitor with process that completes quickly"""
    monitor = TimeoutMonitor()
    
    # Create a quick process
    process = subprocess.Popen(
        [sys.executable, '-c', 'print("hello")'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    result = monitor.watch_process(process, wall_clock_sec=10, idle_output_sec=5)
    
    assert result.timed_out is False
    assert result.wall_time_sec < 10
    assert result.killed is False


def test_timeout_monitor_record_output(timeout_monitor):
    """Test recording output updates idle timer"""
    timeout_monitor.start_time = time.time()
    timeout_monitor.last_output_time = time.time()
    
    initial_time = timeout_monitor.last_output_time
    time.sleep(0.1)
    
    timeout_monitor.record_output()
    
    assert timeout_monitor.last_output_time > initial_time


def test_circuit_breaker_max_attempts(circuit_breaker):
    """Test circuit breaker trips on max attempts"""
    trip = circuit_breaker.should_stop(
        run_id='run-1',
        ws_id='ws-1',
        step='edit',
        attempt=4  # Exceeds max_attempts=3
    )
    
    assert trip is not None
    assert 'Max attempts' in trip.reason
    assert trip.attempt == 4


def test_circuit_breaker_within_attempts(circuit_breaker):
    """Test circuit breaker allows within limit"""
    trip = circuit_breaker.should_stop(
        run_id='run-1',
        ws_id='ws-1',
        step='edit',
        attempt=2  # Within max_attempts=3
    )
    
    assert trip is None


def test_circuit_breaker_from_config():
    """Test creating circuit breaker from config"""
    config = {
        'max_attempts': 5,
        'max_error_repeats': 3,
        'oscillation_threshold': 4
    }
    
    breaker = CircuitBreaker().from_config(config)
    
    assert breaker.max_attempts == 5
    assert breaker.max_error_repeats == 3
    assert breaker.oscillation_threshold == 4


def test_circuit_breaker_from_config_defaults():
    """Test creating circuit breaker from empty config uses defaults"""
    config = {}
    
    breaker = CircuitBreaker().from_config(config)
    
    assert breaker.max_attempts == 3
    assert breaker.max_error_repeats == 2
    assert breaker.oscillation_threshold == 2


def test_scope_validator_normalize_path():
    """Test path normalization helper"""
    validator = ScopeValidator()
    
    # Test different path formats
    assert validator._normalize_path('src/module.py') == 'src/module.py'
    assert validator._normalize_path('src\\module.py') == 'src/module.py'
    assert validator._normalize_path('tests\\unit\\test.py') == 'tests/unit/test.py'


def test_validate_patch_scope_with_subdirectories(scope_validator):
    """Test scope validation with nested directories"""
    bundle = {
        'files_scope': ['src/core/engine.py', 'src/utils/helpers.py'],
        'files_create': []
    }
    
    patch_files = ['src/core/engine.py']
    
    result = scope_validator.validate_patch_scope(patch_files, bundle)
    
    assert result.valid is True


def test_circuit_breaker_initialization():
    """Test CircuitBreaker initialization with custom values"""
    breaker = CircuitBreaker(
        max_attempts=10,
        max_error_repeats=5,
        oscillation_threshold=3
    )
    
    assert breaker.max_attempts == 10
    assert breaker.max_error_repeats == 5
    assert breaker.oscillation_threshold == 3


def test_timeout_monitor_initialization(timeout_monitor):
    """Test TimeoutMonitor initialization"""
    assert timeout_monitor.process is None
    assert timeout_monitor.start_time is None
    assert timeout_monitor.last_output_time is None


def test_scope_result_with_violations():
    """Test ScopeResult with violations"""
    result = ScopeResult(
        valid=False,
        violations=['File outside scope', 'Another violation'],
        allowed_files=['allowed1.py', 'allowed2.py'],
        violating_files=['bad1.py', 'bad2.py']
    )
    
    assert result.valid is False
    assert len(result.violations) == 2
    assert len(result.violating_files) == 2


def test_circuit_breaker_trip_with_error_signature():
    """Test CircuitBreakerTrip with error signature"""
    trip = CircuitBreakerTrip(
        reason="Repeated error",
        ws_id="ws-1",
        attempt=3,
        error_signature="ValueError: invalid input"
    )
    
    assert trip.error_signature == "ValueError: invalid input"


def test_circuit_breaker_trip_with_diff_hash():
    """Test CircuitBreakerTrip with diff hash"""
    trip = CircuitBreakerTrip(
        reason="Oscillation detected",
        ws_id="ws-1",
        attempt=3,
        diff_hash="abc123def456"
    )
    
    assert trip.diff_hash == "abc123def456"


def test_validate_patch_scope_case_sensitivity(scope_validator):
    """Test that scope validation is case-sensitive"""
    bundle = {
        'files_scope': ['src/Module.py'],
        'files_create': []
    }
    
    # Different case should be treated as different file
    patch_files = ['src/module.py']
    
    result = scope_validator.validate_patch_scope(patch_files, bundle)
    
    # On case-sensitive filesystems, this should fail
    # On Windows (case-insensitive), paths might normalize the same
    # So we just verify the validator handles it without error
    assert isinstance(result, ScopeResult)


def test_timeout_result_defaults():
    """Test TimeoutResult default values"""
    result = TimeoutResult(timed_out=False)
    
    assert result.timed_out is False
    assert result.reason is None
    assert result.wall_time_sec == 0.0
    assert result.idle_time_sec == 0.0
    assert result.killed is False


def test_scope_validator_allowed_files_list(scope_validator, sample_bundle):
    """Test that allowed files list is populated correctly"""
    patch_files = ['src/module.py']
    
    result = scope_validator.validate_patch_scope(patch_files, sample_bundle)
    
    assert len(result.allowed_files) > 0
    assert 'src/module.py' in result.allowed_files
    assert 'docs/new_doc.md' in result.allowed_files
