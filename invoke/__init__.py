from __future__ import annotations

import contextlib
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional, Union


@dataclass
class Result:
    stdout: str = ""
    stderr: str = ""
    exited: int = 0

    def __post_init__(self):
        self.return_code = self.exited
        self.ok = self.return_code == 0


class UnexpectedExit(Exception):
    """Exception raised when a command exits unexpectedly."""


class Context:
    def __init__(self) -> None:
        self.cwd: Optional[str] = None

    @contextlib.contextmanager
    def cd(self, path: PathLike) -> Iterable["Context"]:
        prev = self.cwd
        self.cwd = path
        try:
            yield self
        finally:
            self.cwd = prev

    def run(
        self,
        cmd: str,
        *,
        hide: bool = True,
        warn: bool = True,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
        pty: bool = False,
        cwd: Optional[PathLike] = None,
    ) -> Result:
        cwd = cwd or self.cwd
        try:
            completed = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=cwd,
            )
        except subprocess.TimeoutExpired as exc:
            raise UnexpectedExit(str(exc))
        except subprocess.CalledProcessError as exc:
            if warn:
                return Result(stdout=exc.stdout or "", stderr=exc.stderr or "", exited=exc.returncode)
            raise UnexpectedExit(str(exc))
        return Result(stdout=completed.stdout or "", stderr=completed.stderr or "", exited=completed.returncode)


class MockContext:
    def __init__(self, run: Optional[Dict[str, Result]] = None):
        self._run_map = run or {}

    def run(self, cmd: str, **kwargs: Any) -> Result:
        return self._run_map.get(cmd) or Result(stdout="", stderr="", exited=0)

    @contextlib.contextmanager
    def cd(self, path: PathLike) -> Iterable["MockContext"]:
        yield self


def task(func: Optional[Callable[..., Any]] = None, **kwargs: Any) -> Callable[..., Any]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn.is_task = True
        fn.task_kwargs = kwargs
        return fn

    if func is None:
        return decorator
    return decorator(func)


class Collection:
    def __init__(self) -> None:
        self.tasks: Dict[str, Callable[..., Any]] = {}

    def add_task(self, func: Callable[..., Any], *, name: Optional[str] = None) -> None:
        self.tasks[name or func.__name__] = func


@dataclass
class Config:
    data: Dict[str, Any] = field(default_factory=dict)


PathLike = Union[str, os.PathLike[str]]

__all__ = [
    "Context",
    "Result",
    "UnexpectedExit",
    "MockContext",
    "task",
    "Collection",
    "Config",
]
