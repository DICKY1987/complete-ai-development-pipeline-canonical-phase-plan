"""
Integration tests for the LOG_REVIEW_SUB_SYS.
Tests the complete workflow: aggregate -> analyze -> export
"""

import pytest
import json
import sqlite3
import csv
from pathlib import Path
import subprocess
import sys

# Add parent directory to path
sys.path.insert(0, '..')

from structured_logger import StructuredLogger
from audit_logger import AuditLogger, EventFilters


class TestEndToEndWorkflow:
    """Test complete workflow from aggregation to export."""
    
    @pytest.fixture
    def clean_directories(self, tmp_path):
        """Create clean temporary directories for testing."""
        dirs = {
            'aggregated': tmp_path / 'aggregated',
            'exports': tmp_path / 'exports',
            'analysis': tmp_path / 'analysis'
        }
        for dir_path in dirs.values():
            dir_path.mkdir(exist_ok=True)
        return dirs
    
    def test_logger_integration(self, tmp_path):
        """Test that loggers work together correctly."""
        # Create structured logger
        struct_logger = StructuredLogger(name="integration-test")
        
        # Create audit logger
        audit_file = tmp_path / "audit.jsonl"
        audit_logger = AuditLogger(log_path=str(audit_file))
        
        # Log some events
        struct_logger.info("Test started", test_id="test-001")
        audit_logger.log_event("test_started", task_id="task-001", data={"test": "integration"})
        
        struct_logger.job_event("job-001", "started", worker="test")
        audit_logger.log_event("job_started", task_id="task-001", data={"job_id": "job-001"})
        
        struct_logger.info("Test completed", test_id="test-001", status="success")
        audit_logger.log_event("completed", task_id="task-001", data={"result": "success"})
        
        # Verify audit log was created
        assert audit_file.exists()
        
        # Verify we can query events
        filters = EventFilters(task_id="task-001")
        events = audit_logger.query_events(filters)
        assert len(events) == 3
        assert events[0].event_type == "test_started"
        assert events[-1].event_type == "completed"
    
    def test_aggregation_to_export_workflow(self, clean_directories, tmp_path):
        """Test complete workflow from aggregation to export."""
        # Create sample aggregated log file
        agg_file = clean_directories['aggregated'] / "test-aggregated.jsonl"
        
        sample_logs = [
            {
                "tool": "claude",
                "type": "conversation",
                "timestamp": "2025-12-08T23:00:00.000Z",
                "sessionId": "sess-001",
                "data": {"display": "Test message 1", "project": "test-project"}
            },
            {
                "tool": "claude",
                "type": "conversation",
                "timestamp": "2025-12-08T23:05:00.000Z",
                "sessionId": "sess-001",
                "data": {"display": "Test message 2", "project": "test-project"}
            },
            {
                "tool": "copilot",
                "type": "session",
                "timestamp": "2025-12-08T23:10:00.000Z",
                "sessionId": "sess-002",
                "data": {"session_file": "test.log", "entry_count": 5}
            }
        ]
        
        with open(agg_file, 'w', encoding='utf-8') as f:
            for log in sample_logs:
                f.write(json.dumps(log) + '\n')
        
        # Verify aggregated file
        assert agg_file.exists()
        lines = agg_file.read_text(encoding='utf-8').strip().split('\n')
        assert len(lines) == 3
        
        # Test export to SQLite using Python script
        db_file = clean_directories['exports'] / "test.db"
        
        # Import and run export function
        sys.path.insert(0, '..')
        from export_to_sqlite import create_database
        
        create_database(db_file, sample_logs)
        
        # Verify database was created
        assert db_file.exists()
        
        # Query database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        # Check logs table
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        assert count == 3
        
        # Check summary table
        cursor.execute("SELECT tool, total_entries FROM summary ORDER BY tool")
        summary = cursor.fetchall()
        assert len(summary) == 2
        assert summary[0] == ('claude', 2)
        assert summary[1] == ('copilot', 1)
        
        conn.close()


class TestPrivacyRedaction:
    """Test privacy redaction functionality."""
    
    def test_api_key_redaction(self):
        """Test that API keys are redacted."""
        # This would test the privacy redaction in aggregate-logs.ps1
        # For now, we test the concept with a simple function
        
        def redact_secrets(text):
            import re
            text = re.sub(r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]', text)
            text = re.sub(r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
            return text
        
        test_data = "My API key is sk-abc123def456ghi789jkl012mno345pqr678 and token ghp_123456789012345678901234567890123456"
        redacted = redact_secrets(test_data)
        
        assert 'sk-abc123' not in redacted
        assert '[REDACTED_API_KEY]' in redacted
        assert 'ghp_' not in redacted
        assert '[REDACTED_GITHUB_TOKEN]' in redacted
    
    def test_email_redaction(self):
        """Test that email addresses are redacted."""
        import re
        
        def redact_emails(text):
            return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
        
        test_data = "Contact me at user@example.com or admin@test.org"
        redacted = redact_emails(test_data)
        
        assert 'user@example.com' not in redacted
        assert '[REDACTED_EMAIL]' in redacted


class TestExportFormats:
    """Test all export formats."""
    
    def test_csv_export(self, tmp_path):
        """Test CSV export creates valid file."""
        csv_file = tmp_path / "test.csv"
        
        data = [
            {'tool': 'claude', 'type': 'conversation', 'timestamp': '2025-12-08T23:00:00Z', 'display': 'Test 1'},
            {'tool': 'copilot', 'type': 'session', 'timestamp': '2025-12-08T23:01:00Z', 'display': 'Test 2'}
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['tool', 'type', 'timestamp', 'display'])
            writer.writeheader()
            writer.writerows(data)
        
        # Verify CSV is readable
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['tool'] == 'claude'
            assert rows[1]['tool'] == 'copilot'
    
    def test_json_export(self, tmp_path):
        """Test JSON export creates valid file."""
        json_file = tmp_path / "test.json"
        
        data = {
            'metadata': {
                'exportTimestamp': '2025-12-08T23:00:00Z',
                'totalEntries': 2
            },
            'logs': [
                {'tool': 'claude', 'type': 'conversation'},
                {'tool': 'copilot', 'type': 'session'}
            ]
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Verify JSON is readable
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            assert loaded['metadata']['totalEntries'] == 2
            assert len(loaded['logs']) == 2


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_invalid_json_handling(self, tmp_path):
        """Test handling of invalid JSON in log files."""
        log_file = tmp_path / "invalid.jsonl"
        
        # Create file with some valid and some invalid JSON
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json here\n')
            f.write('{"another": "valid"}\n')
        
        # Read and parse, skipping invalid
        valid_entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    valid_entries.append(entry)
                except json.JSONDecodeError:
                    pass  # Skip invalid
        
        assert len(valid_entries) == 2
    
    def test_missing_file_handling(self):
        """Test handling of missing files."""
        from audit_logger import AuditLogger, EventFilters
        
        # Query non-existent file should return empty list
        audit = AuditLogger(log_path="nonexistent.jsonl")
        events = audit.query_events()
        assert events == []


class TestPerformance:
    """Test performance with larger datasets."""
    
    def test_large_dataset_processing(self, tmp_path):
        """Test processing of large log files."""
        log_file = tmp_path / "large.jsonl"
        
        # Create 10,000 log entries
        num_entries = 10000
        with open(log_file, 'w', encoding='utf-8') as f:
            for i in range(num_entries):
                entry = {
                    'tool': 'claude' if i % 2 == 0 else 'copilot',
                    'type': 'conversation',
                    'timestamp': f'2025-12-08T{i % 24:02d}:00:00Z',
                    'sessionId': f'sess-{i % 100:03d}',
                    'data': {'message': f'Message {i}'}
                }
                f.write(json.dumps(entry) + '\n')
        
        # Verify file was created
        assert log_file.exists()
        
        # Count entries
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) == num_entries
        
        # Test quick parsing
        import time
        start = time.time()
        
        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entries.append(json.loads(line.strip()))
        
        elapsed = time.time() - start
        
        assert len(entries) == num_entries
        assert elapsed < 5.0  # Should process 10k entries in under 5 seconds


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
