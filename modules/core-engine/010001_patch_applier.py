"""
Patch Applier - Apply and Track Patches via Ledger
Implements patch state machine and ledger tracking
"""

from pathlib import Path
from typing import Optional
from dataclasses import asdict
import sqlite3
import subprocess
from modules.core_engine.010001_patch_converter import UnifiedPatch


class PatchApplier:
    """Apply patches and track in ledger."""
    
    STATES = ['created', 'validated', 'queued', 'applied', 'verified', 'committed', 'quarantined']
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
    
    def create_ledger_entry(self, patch: UnifiedPatch) -> str:
        """Create entry in patch ledger."""
        self.conn.execute("""
            INSERT INTO patch_ledger 
            (patch_id, workstream_id, content, status, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patch.patch_id,
            patch.workstream_id,
            patch.content,
            patch.status,
            patch.created_at,
            str(patch.metadata)
        ))
        self.conn.commit()
        return patch.patch_id
    
    def apply_patch(self, patch_id: str, workspace: Path) -> bool:
        """Apply patch to workspace."""
        # Get patch from ledger
        cursor = self.conn.execute(
            "SELECT content, status FROM patch_ledger WHERE patch_id = ?",
            (patch_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return False
        
        content, status = row
        
        if status != 'validated':
            return False
        
        try:
            # Write patch to temp file
            patch_file = workspace / f"{patch_id}.patch"
            patch_file.write_text(content)
            
            # Apply with git
            result = subprocess.run(
                ['git', 'apply', str(patch_file)],
                cwd=str(workspace),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.record_in_ledger(patch_id, 'applied')
                return True
            else:
                self.record_in_ledger(patch_id, 'quarantined')
                return False
                
        except Exception as e:
            self.record_in_ledger(patch_id, 'quarantined')
            return False
    
    def validate_patch(self, patch_id: str) -> bool:
        """Validate patch syntax."""
        cursor = self.conn.execute(
            "SELECT content FROM patch_ledger WHERE patch_id = ?",
            (patch_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return False
        
        content = row[0]
        
        # Check for valid diff format
        is_valid = ('---' in content and '+++' in content) or '@@' in content
        
        if is_valid:
            self.record_in_ledger(patch_id, 'validated')
        
        return is_valid
    
    def record_in_ledger(self, patch_id: str, status: str):
        """Update patch status in ledger."""
        if status not in self.STATES:
            raise ValueError(f"Invalid status: {status}")
        
        timestamp_field = f"{status}_at"
        
        self.conn.execute(f"""
            UPDATE patch_ledger 
            SET status = ?, {timestamp_field} = datetime('now')
            WHERE patch_id = ?
        """, (status, patch_id))
        self.conn.commit()
    
    def run_verification_tests(self, workspace: Path) -> bool:
        """Run verification tests (stub)."""
        # Would run actual tests here
        return True
    
    def close(self):
        """Close database connection."""
        self.conn.close()
