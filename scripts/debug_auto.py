"""CLI for automated debug using terminal capture and reflexion.

DOC_ID: DOC-SCRIPT-SCRIPTS-DEBUG-AUTO-765
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.autonomous.reflexion import ReflexionLoop
from core.memory.episodic_memory import EpisodicMemory
from core.terminal.state_capture import capture_state


def main():
    parser = argparse.ArgumentParser(description="Auto-debug with reflexion loop")
    parser.add_argument("--task-id", required=True, help="Unique task identifier")
    parser.add_argument("--description", required=True, help="Task description")
    parser.add_argument("--command", help="Command to execute and debug")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max retry iterations")
    args = parser.parse_args()

    memory = EpisodicMemory()

    def run_fn():
        """Execute the user's command/task."""
        if args.command:
            import subprocess
            result = subprocess.run(
                args.command,
                shell=True,
                capture_output=True,
                text=True
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        else:
            # No command specified - placeholder behavior
            return {"result": "noop", "exit_code": 0}

    def validate_fn(run_result):
        """Validate the execution result."""
        exit_code = run_result.get("exit_code", 1)
        stderr = run_result.get("stderr", "")
        
        if exit_code == 0:
            return {"success": True, "stderr": ""}
        else:
            state = capture_state(
                stdout=run_result.get("stdout", ""),
                stderr=stderr,
                exit_code=exit_code
            )
            return {"success": False, "stderr": "\n".join(state.stderr_tail)}

    loop = ReflexionLoop(
        run_fn=run_fn,
        validate_fn=validate_fn,
        memory=memory,
        max_iterations=args.max_iterations
    )
    result = loop.run(
        task_id=args.task_id,
        task_description=args.description,
        user_prompt=args.description,
        files_changed=[],
    )
    print(f"Completed with success={result.success}, escalated={result.escalated}")


if __name__ == "__main__":
    main()
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DEBUG-AUTO-709
