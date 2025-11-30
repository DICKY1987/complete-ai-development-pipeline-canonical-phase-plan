# DOC_LINK: DOC-TEST-INTERFACES-TEST-WAVES-3-4-126
import pytest
import tempfile
from pathlib import Path
from core.interfaces.file_operations import FileOperations
from core.interfaces.data_provider import DataProvider
from core.interfaces.validation_service import ValidationService
from core.interfaces.cache_manager import CacheManager
from core.interfaces.metrics_collector import MetricsCollector
from core.interfaces.health_checker import HealthChecker
from core.file_ops.local_file_operations import LocalFileOperations
from core.data.state_data_provider import StateDataProvider
from core.validation.basic_validation_service import BasicValidationService
from core.cache.memory_cache_manager import MemoryCacheManager
from core.metrics.simple_metrics_collector import SimpleMetricsCollector
from core.health.system_health_checker import SystemHealthChecker
from core.state.sqlite_store import SQLiteStateStore

class TestFileOperations:
    def test_implements_protocol(self):
        ops = LocalFileOperations()
        assert isinstance(ops, FileOperations)
    
    def test_read_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ops = LocalFileOperations()
            path = Path(tmpdir) / "test.txt"
            ops.write(path, "Hello")
            assert ops.read(path) == "Hello"
    
    def test_patch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ops = LocalFileOperations()
            path = Path(tmpdir) / "test.txt"
            ops.write(path, "Hello World")
            ops.patch(path, "World", "Python")
            assert ops.read(path) == "Hello Python"
    
    def test_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ops = LocalFileOperations()
            path = Path(tmpdir) / "test.txt"
            assert not ops.exists(path)
            ops.write(path, "test")
            assert ops.exists(path)

class TestDataProvider:
    def test_implements_protocol(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteStateStore(Path(tmpdir) / "test.db")
            provider = StateDataProvider(store)
            assert isinstance(provider, DataProvider)
    
    def test_get_workstreams(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteStateStore(Path(tmpdir) / "test.db")
            store.save_workstream({'id': 'ws1', 'status': 'pending'})
            provider = StateDataProvider(store)
            ws_list = provider.get_workstreams()
            assert len(ws_list) == 1
    
    def test_get_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteStateStore(Path(tmpdir) / "test.db")
            store.save_workstream({'id': 'ws1', 'status': 'pending'})
            provider = StateDataProvider(store)
            metrics = provider.get_metrics()
            assert metrics['total_workstreams'] == 1

class TestValidationService:
    def test_implements_protocol(self):
        validator = BasicValidationService()
        assert isinstance(validator, ValidationService)
    
    def test_validate_workstream_valid(self):
        validator = BasicValidationService()
        ws = {'id': 'ws1', 'status': 'pending'}
        errors = validator.validate_workstream(ws)
        assert len(errors) == 0
    
    def test_validate_workstream_missing_fields(self):
        validator = BasicValidationService()
        ws = {}
        errors = validator.validate_workstream(ws)
        assert len(errors) == 2

class TestCacheManager:
    def test_implements_protocol(self):
        cache = MemoryCacheManager()
        assert isinstance(cache, CacheManager)
    
    def test_get_set(self):
        cache = MemoryCacheManager()
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
    
    def test_get_missing(self):
        cache = MemoryCacheManager()
        assert cache.get('nonexistent') is None
    
    def test_invalidate(self):
        cache = MemoryCacheManager()
        cache.set('key1', 'value1')
        cache.invalidate('key1')
        assert cache.get('key1') is None

class TestMetricsCollector:
    def test_implements_protocol(self):
        metrics = SimpleMetricsCollector()
        assert isinstance(metrics, MetricsCollector)
    
    def test_increment(self):
        metrics = SimpleMetricsCollector()
        metrics.increment('jobs.completed')
        metrics.increment('jobs.completed', 2)
        stats = metrics.get_stats()
        assert stats['counters']['jobs.completed'] == 3
    
    def test_gauge(self):
        metrics = SimpleMetricsCollector()
        metrics.gauge('cpu.usage', 45.5)
        stats = metrics.get_stats()
        assert stats['gauges']['cpu.usage'] == 45.5
    
    def test_timing(self):
        metrics = SimpleMetricsCollector()
        metrics.timing('job.duration', 100.0)
        metrics.timing('job.duration', 200.0)
        stats = metrics.get_stats()
        assert stats['timings']['job.duration'] == 150.0

class TestHealthChecker:
    def test_implements_protocol(self):
        health = SystemHealthChecker()
        assert isinstance(health, HealthChecker)
    
    def test_check(self):
        health = SystemHealthChecker()
        results = health.check()
        assert 'system' in results
        assert results['system'] == 'healthy'
    
    def test_is_healthy(self):
        health = SystemHealthChecker()
        assert health.is_healthy() is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
