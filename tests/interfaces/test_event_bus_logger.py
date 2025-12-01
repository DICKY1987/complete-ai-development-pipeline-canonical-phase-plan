"""Tests for EventBus and Logger protocols."""

import pytest
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.event_bus import EventBus
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.logger import Logger
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.events.simple_event_bus import SimpleEventBus
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.logging.structured_logger import StructuredLogger


class TestEventBusProtocol:
    """Test EventBus protocol compliance."""
# DOC_ID: DOC-TEST-INTERFACES-TEST-EVENT-BUS-LOGGER-122
    
    def test_simple_event_bus_implements_protocol(self):
        """SimpleEventBus implements EventBus protocol."""
        bus = SimpleEventBus()
        assert isinstance(bus, EventBus)


class TestSimpleEventBus:
    """Test SimpleEventBus implementation."""
    
    def test_emit_and_subscribe(self):
        """Subscribe and receive events."""
        bus = SimpleEventBus()
        received = []
        
        def handler(payload):
            received.append(payload)
        
        bus.subscribe('test.event', handler)
        bus.emit('test.event', {'data': 'value'})
        
        assert len(received) == 1
        assert received[0]['data'] == 'value'
    
    def test_multiple_subscribers(self):
        """Multiple subscribers receive same event."""
        bus = SimpleEventBus()
        received1 = []
        received2 = []
        
        bus.subscribe('test', lambda p: received1.append(p))
        bus.subscribe('test', lambda p: received2.append(p))
        
        bus.emit('test', {'msg': 'hello'})
        
        assert len(received1) == 1
        assert len(received2) == 1
    
    def test_unsubscribe(self):
        """Unsubscribe stops receiving events."""
        bus = SimpleEventBus()
        received = []
        
        sub_id = bus.subscribe('test', lambda p: received.append(p))
        bus.emit('test', {'n': 1})
        
        bus.unsubscribe(sub_id)
        bus.emit('test', {'n': 2})
        
        assert len(received) == 1


class TestLoggerProtocol:
    """Test Logger protocol compliance."""
    
    def test_structured_logger_implements_protocol(self):
        """StructuredLogger implements Logger protocol."""
        logger = StructuredLogger()
        assert isinstance(logger, Logger)


class TestStructuredLogger:
    """Test StructuredLogger implementation."""
    
    def test_info_logging(self, capsys):
        """Log info message."""
        logger = StructuredLogger('test')
        logger.info('Test message', key='value')
        
        captured = capsys.readouterr()
        assert 'INFO' in captured.err
        assert 'Test message' in captured.err
    
    def test_error_logging(self, capsys):
        """Log error message."""
        logger = StructuredLogger('test')
        logger.error('Error occurred', code=500)
        
        captured = capsys.readouterr()
        assert 'ERROR' in captured.err
    
    def test_job_event(self, capsys):
        """Log job event."""
        logger = StructuredLogger('test')
        logger.job_event('job-001', 'started', tool='aider')
        
        captured = capsys.readouterr()
        assert 'job-001' in captured.err
        assert 'started' in captured.err


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
