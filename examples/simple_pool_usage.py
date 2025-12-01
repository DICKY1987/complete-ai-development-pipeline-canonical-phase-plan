"""Example: Simple ToolProcessPool usage.

Basic example showing core functionality of ToolProcessPool.
"""

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.bridge import ToolProcessPool
import time


def basic_usage():
    """Demonstrate basic pool operations."""
    
    print("Creating pool with 2 aider instances...")
    pool = ToolProcessPool("aider", count=2)
    
    try:
        # Check initial status
        statuses = pool.get_status()
        print(f"✓ Spawned {len(statuses)} instances")
        for s in statuses:
            print(f"  Instance {s['index']}: {'alive' if s['alive'] else 'dead'}")
        
        # Wait for startup
        time.sleep(2.0)
        
        # Send commands
        print("\nSending commands...")
        pool.send_prompt(0, "/help")
        pool.send_prompt(1, "/tokens")
        
        # Read responses
        time.sleep(1.0)
        print("\nResponses:")
        
        resp0 = pool.read_response(0, timeout=3.0)
        resp1 = pool.read_response(1, timeout=3.0)
        
        print(f"Instance 0: {resp0[:50] if resp0 else 'None'}...")
        print(f"Instance 1: {resp1[:50] if resp1 else 'None'}...")
        
        # Health check
        health = pool.check_health()
        print(f"\nHealth: {health['alive']}/{health['total']} alive")
        
    finally:
        print("\nShutting down...")
        pool.shutdown()
        print("✓ Clean shutdown")


if __name__ == "__main__":
    basic_usage()
