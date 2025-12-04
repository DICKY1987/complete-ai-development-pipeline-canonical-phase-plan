#!/usr/bin/env python3
"""
Multi-clone guard with command execution.
Provides branch/pipeline level locking and basic metrics.
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-MULTI-CLONE-GUARD-720

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def file_lock(lock_path: Path, timeout: int) -> Iterator[float]:
    start = time.time()
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(
                fd, json.dumps({"held_at": time.time(), "pid": os.getpid()}).encode()
            )
            os.close(fd)
            wait_time = time.time() - start
            try:
                yield wait_time
            finally:
                if os.path.exists(lock_path):
                    os.remove(lock_path)
            return
        except FileExistsError:
            age = time.time() - os.path.getmtime(lock_path)
            if age > timeout * 2:
                os.remove(lock_path)
                continue
            if time.time() - start > timeout:
                raise TimeoutError(f"Timed out acquiring lock {lock_path}")
            time.sleep(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-clone guard executor")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--command", required=True, help="Command to run under lock")
    parser.add_argument(
        "--lock-type",
        choices=["pipeline", "push_only"],
        default="pipeline",
        help="Lock scope",
    )
    parser.add_argument("--lock-root", default=".git/locks", help="Lock directory")
    parser.add_argument(
        "--timeout", type=int, default=900, help="Lock acquisition timeout seconds"
    )
    args = parser.parse_args()

    lock_root = Path(args.lock_root)
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_id = (
        f"merge_pipeline_{args.branch}"
        if args.lock_type == "pipeline"
        else f"branch_{args.branch}"
    )
    lock_path = lock_root / f"{lock_id}.lock"

    try:
        with file_lock(lock_path, args.timeout) as wait_time:
            print(f"OK: Lock acquired ({lock_id}) after {wait_time:.1f}s")
            result = subprocess.run(args.command, shell=True)
            if result.returncode != 0:
                print(f"FAIL: Command failed under lock ({result.returncode})")
                return result.returncode
    except TimeoutError as exc:
        print(f"FAIL: {exc}")
        return 2

    print("OK: Command completed and lock released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
