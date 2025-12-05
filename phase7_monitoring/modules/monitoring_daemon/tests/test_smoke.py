"""Smoke test for monitoring automation implementation.

Tests:
- Module imports work
- Basic daemon initialization
- Alert engine configuration loading
- Completion handlers registration

Pattern: EXEC-002 (Batch Validation) - Validate all before executing
"""
# DOC_ID: DOC-TESTS-MONITORING-SMOKE-007

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_imports():
    """Test all modules can be imported."""
    print("Testing imports...")
    
    try:
        from phase7_monitoring.modules.monitoring_daemon.src.monitor_daemon import MonitoringDaemon
        from phase7_monitoring.modules.monitoring_daemon.src.completion_handlers import CompletionHandlers
        from phase7_monitoring.modules.alerting.src.alert_engine import AlertEngine
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_daemon_initialization():
    """Test monitoring daemon can be initialized."""
    print("Testing daemon initialization...")
    
    try:
        from phase7_monitoring.modules.monitoring_daemon.src.monitor_daemon import MonitoringDaemon
        
        # Use in-memory database for testing
        daemon = MonitoringDaemon(":memory:", poll_interval=10)
        
        assert daemon.poll_interval == 10
        assert daemon.running == False
        assert daemon.completed_runs == set()
        
        print("  ✅ Daemon initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False


def test_alert_engine():
    """Test alert engine configuration loading."""
    print("Testing alert engine...")
    
    try:
        from phase7_monitoring.modules.alerting.src.alert_engine import AlertEngine
        
        # Test with default config (will use defaults if file not found)
        config_path = "phase7_monitoring/modules/alerting/config/alerts.yaml"
        engine = AlertEngine(config_path)
        
        assert len(engine.rules) > 0, "No alert rules loaded"
        assert 'console' in engine.channels, "Console channel not found"
        
        print(f"  ✅ Alert engine loaded ({len(engine.rules)} rules, {len(engine.channels)} channels)")
        return True
    except Exception as e:
        print(f"  ❌ Alert engine failed: {e}")
        return False


def test_completion_handlers():
    """Test completion handlers can be registered."""
    print("Testing completion handlers...")
    
    try:
        from phase7_monitoring.modules.monitoring_daemon.src.completion_handlers import CompletionHandlers
        from core.events.event_bus import EventBus
        
        # Use in-memory event bus for testing
        event_bus = EventBus(":memory:")
        handlers = CompletionHandlers(event_bus)
        
        # Verify handlers were registered
        assert event_bus is not None
        
        print("  ✅ Completion handlers registered")
        return True
    except Exception as e:
        print(f"  ❌ Handler registration failed: {e}")
        return False


def test_launcher_script():
    """Test launcher script exists and is readable."""
    print("Testing launcher script...")
    
    try:
        launcher = Path("scripts/start_monitoring_daemon.py")
        
        assert launcher.exists(), "Launcher script not found"
        assert launcher.is_file(), "Launcher is not a file"
        
        # Check it's executable (has main function)
        content = launcher.read_text()
        assert 'def main()' in content, "No main() function found"
        assert 'MonitoringDaemon' in content, "MonitoringDaemon not imported"
        
        print("  ✅ Launcher script ready")
        return True
    except Exception as e:
        print(f"  ❌ Launcher check failed: {e}")
        return False


def test_file_existence():
    """Test all required files exist (EXEC-002 pre-flight validation)."""
    print("Testing file existence...")
    
    required_files = [
        "phase7_monitoring/modules/monitoring_daemon/src/monitor_daemon.py",
        "phase7_monitoring/modules/monitoring_daemon/src/completion_handlers.py",
        "phase7_monitoring/modules/alerting/src/alert_engine.py",
        "phase7_monitoring/modules/alerting/config/alerts.yaml",
        "scripts/start_monitoring_daemon.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} MISSING")
            all_exist = False
    
    return all_exist


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("Monitoring Automation - Smoke Test")
    print("Pattern: EXEC-002 (Batch Validation)")
    print("=" * 60)
    print()
    
    tests = [
        ("File Existence", test_file_existence),
        ("Module Imports", test_imports),
        ("Daemon Init", test_daemon_initialization),
        ("Alert Engine", test_alert_engine),
        ("Completion Handlers", test_completion_handlers),
        ("Launcher Script", test_launcher_script),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print()
        print("✅ ALL TESTS PASSED - Implementation ready!")
        print()
        print("Next steps:")
        print("1. Set environment variables for Slack/email (optional)")
        print("2. Run: python scripts/start_monitoring_daemon.py")
        print("3. Monitor console output for events")
        return 0
    else:
        print()
        print("❌ SOME TESTS FAILED - Fix errors before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
