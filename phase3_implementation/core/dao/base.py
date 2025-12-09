"""
Base Data Access Object (DAO) for all entities.

Provides common CRUD operations and database interaction patterns.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from core.db.connection import DatabaseConnection


class BaseDAO(ABC):
    """Base DAO with common CRUD operations."""
    
    def __init__(self, db_path: str = ".state/pipeline.db"):
        self.db = DatabaseConnection(db_path)
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name for this DAO."""
        pass
    
    @property
    @abstractmethod
    def id_column(self) -> str:
        """Return the primary key column name."""
        pass
    
    def create(self, entity: Dict[str, Any]) -> str:
        """
        Insert a new entity.
        
        Returns:
            The ID of the created entity
        """
        columns = list(entity.keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        values = []
        for col in columns:
            val = entity[col]
            if col == 'metadata' and isinstance(val, dict):
                val = json.dumps(val)
            values.append(val)
        
        query = f"""
            INSERT INTO {self.table_name} ({column_names})
            VALUES ({placeholders})
        """
        
        with self.db.transaction() as conn:
            conn.execute(query, values)
        
        return entity[self.id_column]
    
    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE {self.id_column} = ?"
        
        with self.db.connection() as conn:
            cursor = conn.execute(query, (entity_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_dict(cursor, row)
    
    def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update entity fields.
        
        Returns:
            True if entity was updated, False if not found
        """
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        set_clauses = []
        values = []
        
        for col, val in updates.items():
            set_clauses.append(f"{col} = ?")
            if col == 'metadata' and isinstance(val, dict):
                val = json.dumps(val)
            values.append(val)
        
        values.append(entity_id)
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE {self.id_column} = ?
        """
        
        with self.db.transaction() as conn:
            cursor = conn.execute(query, values)
            return cursor.rowcount > 0
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID.
        
        Returns:
            True if entity was deleted, False if not found
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.id_column} = ?"
        
        with self.db.transaction() as conn:
            cursor = conn.execute(query, (entity_id,))
            return cursor.rowcount > 0
    
    def list_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all entities with pagination."""
        query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        
        with self.db.connection() as conn:
            cursor = conn.execute(query, (limit, offset))
            rows = cursor.fetchall()
        
        return [self._row_to_dict(cursor, row) for row in rows]
    
    def find_by(self, **criteria) -> List[Dict[str, Any]]:
        """Find entities matching criteria."""
        where_clauses = []
        values = []
        
        for col, val in criteria.items():
            where_clauses.append(f"{col} = ?")
            values.append(val)
        
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {' AND '.join(where_clauses)}
            ORDER BY created_at DESC
        """
        
        with self.db.connection() as conn:
            cursor = conn.execute(query, values)
            rows = cursor.fetchall()
        
        return [self._row_to_dict(cursor, row) for row in rows]
    
    def count(self, **criteria) -> int:
        """Count entities matching criteria."""
        if criteria:
            where_clauses = []
            values = []
            for col, val in criteria.items():
                where_clauses.append(f"{col} = ?")
                values.append(val)
            where_clause = f"WHERE {' AND '.join(where_clauses)}"
        else:
            where_clause = ""
            values = []
        
        query = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"
        
        with self.db.connection() as conn:
            cursor = conn.execute(query, values)
            return cursor.fetchone()[0]
    
    def _row_to_dict(self, cursor, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse JSON metadata if present
        if 'metadata' in result and result['metadata']:
            try:
                result['metadata'] = json.loads(result['metadata'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Parse JSON test_results if present
        if 'test_results' in result and result['test_results']:
            try:
                result['test_results'] = json.loads(result['test_results'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        return result
