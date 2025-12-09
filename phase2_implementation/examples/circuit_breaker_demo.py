"""
Circuit Breaker demonstration and usage examples.

Shows practical usage of the Circuit Breaker state machine
for tool execution protection.

Reference: DOC-SSOT-STATE-MACHINES-001 §2.4
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError


def unreliable_tool(fail: bool = False):
    """Simulates an unreliable external tool."""
    if fail:
        raise RuntimeError("Tool execution failed")
    return "Tool executed successfully"


def demo_basic_usage():
    """Demonstrate basic circuit breaker usage."""
    print("=" * 60)
    print("DEMO 1: Basic Circuit Breaker Usage")
    print("=" * 60)

    cb = CircuitBreaker(tool_id="demo-tool", failure_threshold=3, cooldown_seconds=2)

    print(f"\n1. Initial state: {cb.current_state.value}")

    # Successful executions
    print("\n2. Execute successful requests...")
    for i in range(3):
        result = cb.call(unreliable_tool, fail=False)
        print(f"   Request {i+1}: {result}")

    print(f"   State: {cb.current_state.value}, Failures: {cb.failure_count}")

    # Trigger failures
    print("\n3. Trigger failures to open circuit...")
    for i in range(3):
        try:
            cb.call(unreliable_tool, fail=True)
        except RuntimeError as e:
            print(f"   Failure {i+1}: {e}")

    print(f"   State: {cb.current_state.value} (circuit opened!)")

    # Fast fail
    print("\n4. Attempt request while circuit is OPEN...")
    try:
        cb.call(unreliable_tool, fail=False)
    except CircuitBreakerOpenError as e:
        print(f"   REJECTED: {e}")

    # Recovery
    print(f"\n5. Waiting {cb.cooldown_seconds} seconds for cooldown...")
    time.sleep(cb.cooldown_seconds + 0.5)

    print("   Attempting recovery (HALF_OPEN state)...")
    result = cb.call(unreliable_tool, fail=False)
    print(f"   Recovery successful: {result}")
    print(f"   State: {cb.current_state.value} (circuit closed!)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CIRCUIT BREAKER STATE MACHINE - DEMONSTRATION")
    print("Reference: SSOT §2.4")
    print("=" * 60)

    demo_basic_usage()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\n✅ Circuit Breaker implementation working correctly!")
    print()
