"""Example: Multi-agent code review using ToolProcessPool.

Demonstrates using multiple aider instances to perform
different types of code review on the same codebase.
"""

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.bridge import ToolProcessPool
import time
from typing import Dict, List


def multi_agent_review(files: List[str]) -> Dict[str, Dict[str, str]]:
    """Perform multi-perspective code review.
    
    Args:
        files: List of files to review
        
    Returns:
        Dict mapping filenames to review results
    """
    
    # Define review agents with different focus areas
    review_agents = [
        ("security", "Identify potential security vulnerabilities"),
        ("performance", "Suggest performance optimizations"),
        ("readability", "Improve code readability and documentation"),
    ]
    
    # Create pool with one instance per review type
    pool = ToolProcessPool("aider", count=len(review_agents))
    
    try:
        print(f"Starting {len(review_agents)} review agents...\n")
        time.sleep(2.0)
        
        # Consume startup output
        for i in range(len(review_agents)):
            pool.read_response(i, timeout=3.0)
        
        reviews = {}
        
        for filepath in files:
            print(f"Reviewing: {filepath}")
            reviews[filepath] = {}
            
            # Send file to each agent with different focus
            for i, (agent_type, focus) in enumerate(review_agents):
                print(f"  - {agent_type} review...")
                
                # Add file
                pool.send_prompt(i, f"/add {filepath}")
                time.sleep(0.2)
                
                # Request focused review
                pool.send_prompt(i, f"/ask '{focus} in this file'")
            
            # Collect reviews
            time.sleep(2.0)
            
            for i, (agent_type, _) in enumerate(review_agents):
                # Read multi-line response
                response_lines = []
                for _ in range(15):
                    line = pool.read_response(i, timeout=1.5)
                    if line:
                        response_lines.append(line)
                    else:
                        break
                
                reviews[filepath][agent_type] = "\n".join(response_lines)
                
                if response_lines:
                    print(f"    ✓ {agent_type}: {len(response_lines)} lines")
                else:
                    print(f"    ✗ {agent_type}: No response")
        
        return reviews
        
    finally:
        pool.shutdown()


def print_review_summary(reviews: Dict[str, Dict[str, str]]):
    """Print formatted review summary."""
    print("\n" + "=" * 60)
    print("CODE REVIEW SUMMARY")
    print("=" * 60)
    
    for filepath, agent_reviews in reviews.items():
        print(f"\n📄 {filepath}")
        print("-" * 60)
        
        for agent_type, review_text in agent_reviews.items():
            print(f"\n🔍 {agent_type.upper()} REVIEW:")
            if review_text:
                # Show first 200 chars
                preview = review_text[:200].replace("\n", " ")
                print(f"   {preview}...")
            else:
                print("   (No feedback)")
        
        print()


if __name__ == "__main__":
    # Example files to review
    test_files = [
        "core/state.py",
        "error/engine.py",
    ]
    
    print("Multi-Agent Code Review Demo")
    print("=" * 60)
    
    reviews = multi_agent_review(test_files)
    print_review_summary(reviews)
    
    print(f"\nReviewed {len(reviews)} files with {len(reviews[list(reviews.keys())[0]])} agents")
