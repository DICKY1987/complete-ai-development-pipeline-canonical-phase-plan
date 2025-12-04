"""CLI stub for automated debug using terminal capture and reflexion."""

from __future__ import annotations

import argparse

from core.autonomous import ReflexionLoop
from core.memory import EpisodicMemory
from core.terminal import capture_state


def main():
    parser = argparse.ArgumentParser(description="Auto-debug stub (Phase 4).")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()

    memory = EpisodicMemory()

    def run_fn():
        # Placeholder: run user command/task here.
        return {"result": "noop"}

    def validate_fn(_):
        # Placeholder validation always fails in stub.
        state = capture_state(stdout="", stderr="stub failure", exit_code=1)
        return {"success": False, "stderr": "\n".join(state.stderr_tail)}

    loop = ReflexionLoop(run_fn=run_fn, validate_fn=validate_fn, memory=memory)
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
