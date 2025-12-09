"""
Patch Ledger State Machine implementation.

Implements the Patch Ledger state machine per SSOT §2.2.
Tracks patch lifecycle in UET V2 system.

States: PENDING, VALIDATING, STAGED, BLOCKED, APPLIED, VERIFIED, ROLLED_BACK, QUARANTINED, EXPIRED, SUPERSEDED
Reference: DOC-SSOT-STATE-MACHINES-001 §2.2
"""

from typing import Dict, Set, Optional
from datetime import datetime, timezone

from core.state.base import BaseState, BaseStateMachine


class PatchLedgerState(BaseState):
    """
    Patch Ledger states per SSOT §2.2.1.
    """
    
    PENDING = "pending"
    VALIDATING = "validating"
    STAGED = "staged"
    BLOCKED = "blocked"
    APPLIED = "applied"
    VERIFIED = "verified"
    ROLLED_BACK = "rolled_back"
    QUARANTINED = "quarantined"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    
    @classmethod
    def get_terminal_states(cls) -> Set['PatchLedgerState']:
        """Terminal states: VERIFIED, ROLLED_BACK, EXPIRED, SUPERSEDED."""
        return {cls.VERIFIED, cls.ROLLED_BACK, cls.EXPIRED, cls.SUPERSEDED}
    
    @classmethod
    def get_valid_transitions(cls) -> Dict['PatchLedgerState', Set['PatchLedgerState']]:
        """Valid transitions per SSOT §2.2.4."""
        return {
            cls.PENDING: {cls.VALIDATING, cls.EXPIRED},
            cls.VALIDATING: {cls.STAGED, cls.QUARANTINED},
            cls.STAGED: {cls.APPLIED, cls.BLOCKED, cls.SUPERSEDED},
            cls.BLOCKED: {cls.STAGED, cls.QUARANTINED},
            cls.APPLIED: {cls.VERIFIED, cls.ROLLED_BACK},
            cls.QUARANTINED: {cls.VALIDATING, cls.EXPIRED},
            cls.VERIFIED: set(),
            cls.ROLLED_BACK: set(),
            cls.EXPIRED: set(),
            cls.SUPERSEDED: set()
        }


class PatchLedgerStateMachine(BaseStateMachine):
    """
    Patch Ledger state machine for UET V2 patch tracking.
    
    Manages patch lifecycle per SSOT §2.2.
    """
    
    def __init__(self, patch_id: str, task_id: str, metadata: Optional[Dict] = None):
        super().__init__(
            entity_id=patch_id,
            entity_type="patch_ledger",
            initial_state=PatchLedgerState.PENDING,
            metadata=metadata or {}
        )
        
        self.patch_id = patch_id
        self.task_id = task_id
        
        # Patch details
        self.file_path: Optional[str] = None
        self.patch_format: Optional[str] = None  # unified_diff, git_patch, etc.
        self.scope: Optional[str] = None  # function, class, module, file
        
        # Validation
        self.validation_errors: list = []
        self.applied_at: Optional[datetime] = None
        self.verified_at: Optional[datetime] = None
    
    def begin_validation(self):
        """Start patch validation."""
        self.transition(
            PatchLedgerState.VALIDATING,
            reason="Beginning patch validation",
            trigger="validation_started"
        )
    
    def stage(self, reason: str = "Validation passed"):
        """Stage patch for application."""
        self.transition(
            PatchLedgerState.STAGED,
            reason=reason,
            trigger="validation_passed"
        )
    
    def block(self, reason: str):
        """Block patch from application."""
        self.transition(
            PatchLedgerState.BLOCKED,
            reason=reason,
            trigger="patch_blocked"
        )
    
    def unblock(self):
        """Unblock patch."""
        self.transition(
            PatchLedgerState.STAGED,
            reason="Blockers resolved",
            trigger="patch_unblocked"
        )
    
    def apply_patch(self):
        """Apply patch to codebase."""
        self.transition(
            PatchLedgerState.APPLIED,
            reason="Patch applied to codebase",
            trigger="patch_applied"
        )
        self.applied_at = datetime.now(timezone.utc)
    
    def verify(self):
        """Verify patch application."""
        self.transition(
            PatchLedgerState.VERIFIED,
            reason="Patch verified successfully",
            trigger="patch_verified"
        )
        self.verified_at = datetime.now(timezone.utc)
    
    def rollback(self, reason: str):
        """Rollback patch."""
        self.transition(
            PatchLedgerState.ROLLED_BACK,
            reason=reason,
            trigger="patch_rolled_back"
        )
    
    def quarantine(self, reason: str, errors: list = None):
        """Quarantine problematic patch."""
        if errors:
            self.validation_errors.extend(errors)
        self.transition(
            PatchLedgerState.QUARANTINED,
            reason=reason,
            trigger="patch_quarantined"
        )
    
    def expire(self, reason: str = "Patch expired"):
        """Mark patch as expired."""
        self.transition(
            PatchLedgerState.EXPIRED,
            reason=reason,
            trigger="patch_expired"
        )
    
    def supersede(self, new_patch_id: str):
        """Mark patch as superseded by newer version."""
        self.metadata['superseded_by'] = new_patch_id
        self.transition(
            PatchLedgerState.SUPERSEDED,
            reason=f"Superseded by {new_patch_id}",
            trigger="patch_superseded"
        )
    
    def set_patch_details(self, file_path: str, format: str, scope: str):
        """Set patch details."""
        self.file_path = file_path
        self.patch_format = format
        self.scope = scope
    
    def get_patch_info(self) -> Dict:
        """Get patch information."""
        return {
            'patch_id': self.patch_id,
            'task_id': self.task_id,
            'state': self.current_state.value,
            'file_path': self.file_path,
            'patch_format': self.patch_format,
            'scope': self.scope,
            'validation_errors': self.validation_errors,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'is_terminal': self.is_terminal()
        }
