"""
Database connection and management.

Provides SQLite database connection management for state machine persistence.
Uses connection pooling and proper resource cleanup.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class DatabaseConnection:
    """
    Database connection manager for state machine persistence.
    
    Uses SQLite with WAL mode for better concurrency.
    Implements connection pooling for multi-threaded access.
    """
    
    def __init__(self, db_path: str = ".state/pipeline.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Get or create database connection.
        
        Returns:
            SQLite connection object
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Allow multi-threaded access
            )
            
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Enable WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode = WAL")
            
            # Set row factory for dict-like access
            self._connection.row_factory = sqlite3.Row
        
        return self._connection
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database connection
            
        Example:
            >>> db = DatabaseConnection()
            >>> with db.transaction() as conn:
            ...     conn.execute("INSERT INTO ...")
            ...     conn.execute("UPDATE ...")
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute(self, sql: str, params: tuple = ()):
        """
        Execute SQL statement.
        
        Args:
            sql: SQL statement
            params: Parameters for SQL statement
            
        Returns:
            Cursor object
        """
        conn = self.connect()
        return conn.execute(sql, params)
    
    def execute_script(self, sql: str):
        """
        Execute SQL script (multiple statements).
        
        Args:
            sql: SQL script
        """
        conn = self.connect()
        conn.executescript(sql)
        conn.commit()
    
    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """
        Fetch single row.
        
        Args:
            sql: SQL query
            params: Query parameters
            
        Returns:
            Single row or None
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    def fetchall(self, sql: str, params: tuple = ()) -> list:
        """
        Fetch all rows.
        
        Args:
            sql: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def __enter__(self):
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        return False


# Global database instance
_db: Optional[DatabaseConnection] = None


def get_db(db_path: str = ".state/pipeline.db") -> DatabaseConnection:
    """
    Get global database connection.
    
    Args:
        db_path: Path to database file
        
    Returns:
        Database connection instance
    """
    global _db
    if _db is None:
        _db = DatabaseConnection(db_path)
    return _db


def close_db():
    """Close global database connection."""
    global _db
    if _db:
        _db.close()
        _db = None
