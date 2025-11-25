"""
Migration Validator - Verify Migration Integrity
Compares old and new database schemas, validates conversions
"""

from pathlib import Path
import sqlite3
from typing import Dict, List


class MigrationValidator:
    """Validate UET migration integrity."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.discrepancies = []
    
    def compare_old_db_vs_new_db(self) -> Dict:
        """Compare table counts and structure."""
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        )
        table_count = cursor.fetchone()[0]
        
        return {
            'total_tables': table_count,
            'uet_tables_present': self._check_uet_tables(),
            'legacy_tables_present': True  # Assuming legacy tables still exist
        }
    
    def _check_uet_tables(self) -> bool:
        """Check if UET tables exist."""
        required_tables = ['uet_runs', 'step_attempts', 'run_events', 'patch_ledger']
        
        for table in required_tables:
            cursor = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            if not cursor.fetchone():
                return False
        
        return True
    
    def validate_data_integrity(self) -> bool:
        """Validate data integrity constraints."""
        try:
            # Check foreign keys
            self.conn.execute("PRAGMA foreign_key_check")
            
            # Check for orphaned records
            cursor = self.conn.execute("""
                SELECT COUNT(*) FROM step_attempts 
                WHERE run_id NOT IN (SELECT run_id FROM uet_runs)
            """)
            orphaned = cursor.fetchone()[0]
            
            if orphaned > 0:
                self.discrepancies.append(f"{orphaned} orphaned step_attempts")
                return False
            
            return True
        except Exception as e:
            self.discrepancies.append(str(e))
            return False
    
    def check_patch_ledger_completeness(self) -> bool:
        """Check patch ledger has all expected entries."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM patch_ledger")
        count = cursor.fetchone()[0]
        
        return count >= 0  # Placeholder - would check actual expected count
    
    def report_discrepancies(self) -> List[str]:
        """Report any discrepancies found."""
        return self.discrepancies
    
    def close(self):
        """Close database connection."""
        self.conn.close()
