"""
Validation & Circuit Breakers for Pipeline Plus
Safety gates—scope validation, oscillation detection, timeouts
"""
# DOC_ID: DOC-PAT-CORE-ENGINE-M010001-VALIDATORS-518
import time
import psutil
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone


@dataclass
class ScopeResult:
    """Result of scope validation"""
    valid: bool
    violations: List[str] = field(default_factory=list)
    allowed_files: List[str] = field(default_factory=list)
    violating_files: List[str] = field(default_factory=list)


@dataclass
class TimeoutResult:
    """Result of timeout monitoring"""
    timed_out: bool
    reason: Optional[str] = None
    wall_time_sec: float = 0.0
    idle_time_sec: float = 0.0
    killed: bool = False


@dataclass
class CircuitBreakerTrip:
    """Circuit breaker trip event"""
    reason: str
    ws_id: str
    attempt: int
    error_signature: Optional[str] = None
    diff_hash: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


class ScopeValidator:
    """
    Validates that patches only modify allowed files
    """
    
    def __init__(self):
        pass
    
    def validate_patch_scope(
        self,
        patch_files: List[str],
        bundle: Dict[str, Any]
    ) -> ScopeResult:
        """
        Validate that patch only modifies files within bundle scope
        
        Args:
            patch_files: List of files modified in the patch
            bundle: Workstream bundle with files_scope and files_create
            
        Returns:
            ScopeResult with validation details
        """
        # Get allowed files from bundle
        files_scope = bundle.get('files_scope', [])
        files_create = bundle.get('files_create', [])
        allowed_files = set(files_scope + files_create)
        
        # Normalize paths for comparison
        normalized_allowed = {self._normalize_path(f) for f in allowed_files}
        normalized_patch = {self._normalize_path(f) for f in patch_files}
        
        # Find violations
        violations = []
        violating_files = []
        
        for patch_file in normalized_patch:
            if patch_file not in normalized_allowed:
                violations.append(f"File '{patch_file}' is not in declared scope")
                violating_files.append(patch_file)
        
        return ScopeResult(
            valid=len(violations) == 0,
            violations=violations,
            allowed_files=list(normalized_allowed),
            violating_files=violating_files
        )
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for comparison (handle forward/back slashes)
        
        Args:
            path: File path
            
        Returns:
            Normalized path
        """
        return str(Path(path)).replace('\\', '/')


class TimeoutMonitor:
    """
    Monitors process execution with wall clock and idle timeouts
    """
    
    def __init__(self):
        self.process = None
        self.start_time = None
        self.last_output_time = None
    
    def watch_process(
        self,
        process: 'subprocess.Popen',
        wall_clock_sec: int = 600,
        idle_output_sec: int = 120
    ) -> TimeoutResult:
        """
        Monitor process for timeouts
        
        Args:
            process: Subprocess to monitor
            wall_clock_sec: Maximum wall clock time
            idle_output_sec: Maximum time without output
            
        Returns:
            TimeoutResult with timeout details
        """
        self.process = process
        self.start_time = time.time()
        self.last_output_time = self.start_time
        
        try:
            # Get process via psutil for better monitoring
            ps_process = psutil.Process(process.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process already ended or no access
            return TimeoutResult(timed_out=False)
        
        while process.poll() is None:
            current_time = time.time()
            wall_time = current_time - self.start_time
            idle_time = current_time - self.last_output_time
            
            # Check wall clock timeout
            if wall_time > wall_clock_sec:
                self._kill_process(ps_process)
                return TimeoutResult(
                    timed_out=True,
                    reason=f"Wall clock timeout ({wall_clock_sec}s exceeded)",
                    wall_time_sec=wall_time,
                    idle_time_sec=idle_time,
                    killed=True
                )
            
            # Check idle timeout
            if idle_time > idle_output_sec:
                self._kill_process(ps_process)
                return TimeoutResult(
                    timed_out=True,
                    reason=f"Idle timeout ({idle_output_sec}s without output)",
                    wall_time_sec=wall_time,
                    idle_time_sec=idle_time,
                    killed=True
                )
            
            # Sleep briefly to avoid busy waiting
            time.sleep(0.5)
        
        # Process completed normally
        wall_time = time.time() - self.start_time
        return TimeoutResult(
            timed_out=False,
            wall_time_sec=wall_time,
            idle_time_sec=0
        )
    
    def record_output(self):
        """Record that output was received (resets idle timer)"""
        self.last_output_time = time.time()
    
    def _kill_process(self, ps_process: 'psutil.Process'):
        """
        Kill process and all children
        
        Args:
            ps_process: psutil Process object
        """
        try:
            # Kill children first
            children = ps_process.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Kill parent
            ps_process.kill()
            
            # Wait for termination
            try:
                ps_process.wait(timeout=5)
            except psutil.TimeoutExpired:
                pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


class CircuitBreaker:
    """
    Circuit breaker for detecting and preventing oscillation, repeated errors
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        max_error_repeats: int = 2,
        oscillation_threshold: int = 2
    ):
        self.max_attempts = max_attempts
        self.max_error_repeats = max_error_repeats
        self.oscillation_threshold = oscillation_threshold
    
    def check_oscillation(
        self,
        ws_id: str,
        diff_hash: str,
        db_path: Optional[str] = None
    ) -> Optional[CircuitBreakerTrip]:
        """
        Check if diff hash indicates oscillation (repeating same change)
        
        Args:
            ws_id: Workstream ID
            diff_hash: SHA256 hash of diff
            db_path: Optional database path
            
        Returns:
            CircuitBreakerTrip if oscillation detected, None otherwise
        """
        # Import here to avoid circular dependency
        from modules.core_state import get_patches_by_hash
        
        # Query patches with same diff hash
        matching_patches = get_patches_by_hash(ws_id, diff_hash, db_path)
        
        # Check if we've seen this diff too many times
        if len(matching_patches) >= self.oscillation_threshold:
            return CircuitBreakerTrip(
                reason=f"Oscillation detected: same diff repeated {len(matching_patches)} times",
                ws_id=ws_id,
                attempt=len(matching_patches) + 1,
                diff_hash=diff_hash
            )
        
        return None
    
    def should_stop(
        self,
        run_id: str,
        ws_id: str,
        step: str,
        attempt: int,
        error_signature: Optional[str] = None,
        diff_hash: Optional[str] = None,
        db_path: Optional[str] = None
    ) -> Optional[CircuitBreakerTrip]:
        """
        Unified check for whether execution should stop
        
        Args:
            run_id: Run ID
            ws_id: Workstream ID
            step: Step name
            attempt: Current attempt number
            error_signature: Optional error signature for repeat detection
            diff_hash: Optional diff hash for oscillation detection
            db_path: Optional database path
            
        Returns:
            CircuitBreakerTrip if should stop, None otherwise
        """
        # Check attempt limit
        if attempt > self.max_attempts:
            return CircuitBreakerTrip(
                reason=f"Max attempts exceeded ({self.max_attempts})",
                ws_id=ws_id,
                attempt=attempt
            )
        
        # Check error repetition if signature provided
        if error_signature:
            repeat_trip = self._check_error_repeats(
                ws_id, step, error_signature, db_path
            )
            if repeat_trip:
                return repeat_trip
        
        # Check oscillation if diff hash provided
        if diff_hash:
            oscillation_trip = self.check_oscillation(ws_id, diff_hash, db_path)
            if oscillation_trip:
                return oscillation_trip
        
        return None
    
    def _check_error_repeats(
        self,
        ws_id: str,
        step: str,
        error_signature: str,
        db_path: Optional[str] = None
    ) -> Optional[CircuitBreakerTrip]:
        """
        Check if same error is repeating
        
        Args:
            ws_id: Workstream ID
            step: Step name
            error_signature: Error signature to check
            db_path: Optional database path
            
        Returns:
            CircuitBreakerTrip if too many repeats, None otherwise
        """
        # Import here to avoid circular dependency
        from modules.core_state import list_errors
        
        # Query recent errors for this workstream/step
        errors = list_errors(
            ws_id=ws_id,
            limit=10,
            db_path=db_path
        )
        
        # Count consecutive occurrences of same error
        consecutive_count = 0
        for error in errors:
            # Simple signature matching (could be enhanced)
            if error_signature in error.get('error_text', ''):
                consecutive_count += 1
                if consecutive_count >= self.max_error_repeats:
                    return CircuitBreakerTrip(
                        reason=f"Same error repeated {consecutive_count} times",
                        ws_id=ws_id,
                        attempt=consecutive_count,
                        error_signature=error_signature
                    )
            else:
                # Different error, reset counter
                break
        
        return None
    
    def from_config(self, config: Dict[str, Any]) -> 'CircuitBreaker':
        """
        Create CircuitBreaker from configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured CircuitBreaker instance
        """
        return CircuitBreaker(
            max_attempts=config.get('max_attempts', 3),
            max_error_repeats=config.get('max_error_repeats', 2),
            oscillation_threshold=config.get('oscillation_threshold', 2)
        )
