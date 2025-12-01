"""Example: Parallel refactoring with aider instances.

This example demonstrates using ToolProcessPool to refactor
multiple files in parallel using separate aider instances.
"""

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.bridge import ToolProcessPool
import time


def parallel_refactor():
    """Refactor 3 files in parallel."""
    
    # Files to refactor
    files_to_refactor = [
        ("core/state.py", "Add comprehensive type hints"),
        ("error/engine.py", "Add error handling for edge cases"),
        ("aim/bridge.py", "Improve docstrings with examples"),
    ]
    
    # Create pool with one instance per file
    pool = ToolProcessPool("aider", count=len(files_to_refactor))
    
    try:
        print(f"Spawned {len(pool.instances)} aider instances")
        
        # Wait for startup
        time.sleep(2.0)
        
        # Consume startup banners
        for i in range(len(files_to_refactor)):
            pool.read_response(i, timeout=3.0)
        
        # Send refactoring tasks
        print("\nSending refactoring tasks...")
        for i, (filepath, task) in enumerate(files_to_refactor):
            print(f"  [{i}] {filepath}: {task}")
            
            # Add file to context
            pool.send_prompt(i, f"/add {filepath}")
            time.sleep(0.3)
            
            # Send refactoring request
            pool.send_prompt(i, f"/ask '{task}'")
        
        # Monitor progress
        print("\nMonitoring progress...")
        time.sleep(3.0)  # Give aider time to process
        
        results = {}
        for i, (filepath, _) in enumerate(files_to_refactor):
            # Read responses (may be multiple lines)
            responses = []
            for _ in range(10):
                line = pool.read_response(i, timeout=2.0)
                if line:
                    responses.append(line)
                else:
                    break
            
            results[filepath] = responses
            
            if responses:
                print(f"\n[{i}] {filepath}:")
                for line in responses[:5]:  # Show first 5 lines
                    print(f"    {line}")
                if len(responses) > 5:
                    print(f"    ... ({len(responses) - 5} more lines)")
            else:
                print(f"\n[{i}] {filepath}: No response yet")
        
        # Health check
        health = pool.check_health()
        print(f"\nFinal health: {health['alive']}/{health['total']} instances alive")
        
        return results
        
    finally:
        print("\nShutting down...")
        pool.shutdown()
        print("Done!")


if __name__ == "__main__":
    results = parallel_refactor()
    print(f"\nProcessed {len(results)} files")
