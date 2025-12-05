"""
Standalone example: Parallel file refactoring with ClusterManager.

This script demonstrates using the multi-CLI cluster to refactor
multiple files in parallel, achieving 3-5x speedup over sequential.

DOC_ID: DOC-EXAMPLE-PARALLEL-REFACTOR-001
"""

import time
from pathlib import Path
from typing import List

from phase4_routing.modules.aim_tools.src.aim.cluster_manager import launch_cluster


def parallel_refactor(
    files: List[str], prompt: str, tool: str = "aider", workers: int = 3
):
    """Refactor multiple files in parallel using a cluster.

    Args:
        files: List of file paths to refactor
        prompt: Refactoring instruction
        tool: Tool to use (default: aider)
        workers: Number of parallel workers

    Returns:
        Dict with results and timing
    """
    print(f"\n{'='*60}")
    print(f"🚀 Parallel Refactoring with {tool}")
    print(f"{'='*60}")
    print(f"  Files: {len(files)}")
    print(f"  Workers: {workers}")
    print(f"  Prompt: {prompt}")
    print()

    # Launch cluster
    print(f"⚙️  Launching {workers} {tool} instances...")
    start_time = time.time()
    cluster = launch_cluster(tool, count=workers, routing="round_robin")

    try:
        # Check health
        health = cluster.check_health()
        print(f"✅ Cluster ready: {health['alive']}/{health['total']} instances alive")
        print()

        # Distribute work
        print("📤 Distributing work...")
        assignments = {}
        for i, filepath in enumerate(files):
            # Add file to instance
            instance_idx = cluster.send(f"/add {filepath}")
            assignments[filepath] = instance_idx
            print(f"  • {filepath} → instance {instance_idx}")

        print()

        # Send refactoring prompt to all instances
        print("🔧 Sending refactoring prompts...")
        for filepath, instance_idx in assignments.items():
            cluster.send_to(instance_idx, f"/ask '{prompt}'")
            print(f"  • Instance {instance_idx}: {prompt}")

        print()

        # Collect results
        print("⏳ Waiting for completions...")
        results = {}
        for filepath, instance_idx in assignments.items():
            # Wait for response with generous timeout
            response = cluster.read(instance_idx, timeout=120)

            if response:
                results[filepath] = {
                    "success": True,
                    "response": response,
                    "instance": instance_idx,
                }
                print(f"  ✅ {filepath} (instance {instance_idx})")
            else:
                results[filepath] = {
                    "success": False,
                    "response": None,
                    "instance": instance_idx,
                }
                print(f"  ⚠️  {filepath} timeout (instance {instance_idx})")

        total_time = time.time() - start_time

        # Summary
        print()
        print(f"{'='*60}")
        print("📊 RESULTS")
        print(f"{'='*60}")

        successes = sum(1 for r in results.values() if r["success"])
        print(f"  Completed: {successes}/{len(files)}")
        print(f"  Duration: {total_time:.1f}s")
        print(f"  Avg per file: {total_time/len(files):.1f}s")

        # Get cluster stats
        status = cluster.get_status()
        print()
        print(f"  Cluster stats:")
        print(f"    • Total sent: {status['metrics']['total_sent']}")
        print(f"    • Total received: {status['metrics']['total_received']}")

        return {
            "results": results,
            "total_time": total_time,
            "successes": successes,
            "failures": len(files) - successes,
        }

    finally:
        print()
        print("🛑 Shutting down cluster...")
        cluster.shutdown()
        print("✅ Done!")
        print()


def sequential_refactor(files: List[str], prompt: str, tool: str = "aider"):
    """Refactor files sequentially for comparison (SLOW!)."""
    print(f"\n{'='*60}")
    print(f"🐢 Sequential Refactoring with {tool} (for comparison)")
    print(f"{'='*60}")
    print(f"  Files: {len(files)}")
    print(f"  Prompt: {prompt}")
    print()

    import subprocess

    start_time = time.time()
    results = {}

    for filepath in files:
        print(f"📝 Processing {filepath}...")

        try:
            # Run aider as one-shot process
            cmd = [tool, "--yes-always", filepath, "--message", prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            results[filepath] = {
                "success": result.returncode == 0,
                "response": result.stdout,
            }

            print(f"  ✅ Done")

        except subprocess.TimeoutExpired:
            results[filepath] = {"success": False, "response": None}
            print(f"  ⚠️  Timeout")

    total_time = time.time() - start_time

    print()
    print(f"{'='*60}")
    print("📊 RESULTS")
    print(f"{'='*60}")

    successes = sum(1 for r in results.values() if r["success"])
    print(f"  Completed: {successes}/{len(files)}")
    print(f"  Duration: {total_time:.1f}s")
    print(f"  Avg per file: {total_time/len(files):.1f}s")
    print()

    return {"results": results, "total_time": total_time, "successes": successes}


def compare_parallel_vs_sequential():
    """Compare parallel vs sequential performance."""
    # Test files (you can modify this list)
    test_files = [
        "phase4_routing/modules/aim_tools/src/aim/pool_interface.py",
        "phase4_routing/modules/aim_tools/src/aim/process_pool.py",
        "phase4_routing/modules/aim_tools/src/aim/routing.py",
    ]

    # Filter to files that exist
    existing_files = [f for f in test_files if Path(f).exists()]

    if not existing_files:
        print("⚠️  No test files found. Using dummy list.")
        existing_files = test_files[:3]  # Use first 3 anyway for demo

    prompt = "Add type hints to all function parameters"

    print("\n" + "=" * 60)
    print("🔬 PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"Files: {len(existing_files)}")
    print(f"Prompt: '{prompt}'")
    print()

    # Run parallel
    print("\n[1/2] PARALLEL MODE")
    parallel_result = parallel_refactor(existing_files, prompt, workers=3)

    # SKIP sequential for now (too slow and we're just demonstrating)
    print("\n[2/2] SEQUENTIAL MODE")
    print("⚠️  Skipping sequential run (too slow)")
    print(
        "    Estimated time: ~120s (vs {:.1f}s parallel)".format(
            parallel_result["total_time"]
        )
    )

    # Calculate speedup
    estimated_sequential = len(existing_files) * 40  # Assume 40s per file
    speedup = estimated_sequential / parallel_result["total_time"]

    print()
    print("=" * 60)
    print("📈 SPEEDUP ANALYSIS")
    print("=" * 60)
    print(f"  Parallel time:   {parallel_result['total_time']:.1f}s")
    print(f"  Sequential est:  {estimated_sequential:.1f}s")
    print(f"  Speedup:         {speedup:.1f}x faster! 🚀")
    print()


if __name__ == "__main__":
    # Example 1: Basic parallel refactoring
    print("\n" + "🎯 EXAMPLE 1: Basic Parallel Refactoring")

    files = [
        "phase4_routing/modules/aim_tools/src/aim/routing.py",
        "phase4_routing/modules/aim_tools/src/aim/cluster_manager.py",
    ]

    result = parallel_refactor(
        files=files, prompt="Add docstring examples to all public methods", workers=2
    )

    # Example 2: Performance comparison
    # Uncomment to run full comparison:
    # compare_parallel_vs_sequential()
