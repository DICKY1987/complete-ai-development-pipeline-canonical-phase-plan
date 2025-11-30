"""Orchestrator integration for pattern automation."""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class PatternAutomationHooks:
    """Hooks for pattern detection in orchestrator flows."""
DOC_ID: DOC-PAT-INTEGRATION-ORCHESTRATOR-HOOKS-889

    def __init__(self, db_path: Optional[str] = None, config_path: Optional[str] = None, enabled: bool = True):
        self.patterns_dir = Path(__file__).resolve().parents[2]
        self._detector = None
        self.config = {}
        self.enabled = enabled

        self.config_path = Path(config_path) if config_path else self.patterns_dir / "automation" / "config" / "detection_config.yaml"
        if self.config_path.exists():
            try:
                import yaml

                with self.config_path.open() as f:
                    self.config = yaml.safe_load(f) or {}
                self.enabled = self.config.get("automation_enabled", self.enabled)
                config_db = self.config.get("database", {}).get("path")
                if db_path is None and config_db:
                    db_path = config_db
            except Exception as exc:  # pragma: no cover - defensive logging path
                print(f"[pattern-automation] Failed to load config {self.config_path}: {exc}")

        default_db = self.patterns_dir / "metrics" / "pattern_automation.db"
        self.db_path = str(db_path or default_db)

    def get_detector(self):
        """Lazy load execution detector."""
        if self._detector is None:
            from automation.detectors.execution_detector import ExecutionPatternDetector

            db = sqlite3.connect(self.db_path)
            self._detector = ExecutionPatternDetector(db)
        return self._detector

    def on_task_start(self, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Called before task execution."""
        return {"start_time": datetime.now().isoformat(), "task_spec": task_spec}

    def on_task_complete(
        self, task_spec: Dict[str, Any], result: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ):
        """Called after task execution (success or failure)."""
        if not self.enabled:
            return

        try:
            start_time = datetime.fromisoformat(context.get("start_time")) if context else datetime.now()
            duration = (datetime.now() - start_time).total_seconds()

            operation_kind = task_spec.get("operation_kind", "unknown")
            file_types = self._extract_file_types(task_spec, result)
            tools_used = self._extract_tools_used(task_spec)

            input_sig = self._hash_structure(task_spec.get("inputs", {}))
            output_sig = self._hash_structure(result.get("outputs", {}))

            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO execution_logs
                (operation_kind, file_types, tools_used, input_signature, output_signature,
                 success, time_taken_seconds, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operation_kind,
                    json.dumps(file_types),
                    json.dumps(tools_used),
                    input_sig,
                    output_sig,
                    result.get("success", False),
                    duration,
                    json.dumps(
                        {
                            "task_name": task_spec.get("name"),
                            "inputs_summary": self._summarize(task_spec.get("inputs", {})),
                            "outputs_summary": self._summarize(result.get("outputs", {})),
                        }
                    ),
                ),
            )
            db.commit()
            db.close()

            if result.get("success"):
                self._check_for_patterns_async(operation_kind, input_sig, output_sig)

        except Exception as exc:  # pragma: no cover - defensive logging path
            print(f"[pattern-automation] Logging error (non-fatal): {exc}")

    def _extract_file_types(self, task_spec: Dict[str, Any], result: Dict[str, Any]) -> list:
        """Extract file extensions from task inputs and outputs."""
        file_types = set()
        for value in self._flatten_dict(task_spec.get("inputs", {})):
            if isinstance(value, str) and "." in value:
                ext = Path(value).suffix.lstrip(".")
                if ext and len(ext) <= 10:
                    file_types.add(ext)
        for value in self._flatten_dict(result.get("outputs", {})):
            if isinstance(value, str) and "." in value:
                ext = Path(value).suffix.lstrip(".")
                if ext and len(ext) <= 10:
                    file_types.add(ext)
        return sorted(file_types)

    def _extract_tools_used(self, task_spec: Dict[str, Any]) -> list:
        """Heuristic detection of tools referenced in task spec."""
        tools = set()
        task_str = json.dumps(task_spec).lower()
        tool_keywords = [
            "grep",
            "glob",
            "view",
            "edit",
            "create",
            "powershell",
            "git",
            "pytest",
            "bash",
            "python",
            "npm",
            "docker",
        ]
        for tool in tool_keywords:
            if tool in task_str:
                tools.add(tool)
        return sorted(tools)

    def _hash_structure(self, obj: Any) -> str:
        """Create hash of object structure (not values)."""
        if isinstance(obj, dict):
            keys = sorted(obj.keys())
            structure = {k: self._hash_structure(obj[k]) for k in keys}
        elif isinstance(obj, (list, tuple)):
            structure = [self._hash_structure(item) for item in obj]
        else:
            structure = type(obj).__name__
        return hashlib.md5(json.dumps(structure, sort_keys=True).encode()).hexdigest()

    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = "") -> list:
        """Flatten nested dict to list of values."""
        items = []
        for key, value in data.items():
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, f"{parent_key}.{key}"))
            else:
                items.append(value)
        return items

    def _summarize(self, obj: Any, max_len: int = 100) -> Any:
        """Summarize object for logging."""
        serialized = json.dumps(obj)
        if len(serialized) > max_len:
            return serialized[:max_len] + "..."
        return obj

    def _check_for_patterns_async(self, operation_kind: str, input_sig: str, output_sig: str):
        """Trigger pattern detection in a non-blocking way."""
        try:
            detector = self.get_detector()
            if hasattr(detector, "check_for_patterns"):
                detector.check_for_patterns(operation_kind, input_sig, output_sig)
            elif hasattr(detector, "process_execution"):
                detector.process_execution(operation_kind, input_sig, output_sig)
        except Exception as exc:  # pragma: no cover - defensive logging path
            print(f"[pattern-automation] Detection error (non-fatal): {exc}")


_hooks_instance: Optional[PatternAutomationHooks] = None


def get_hooks(db_path: Optional[str] = None, config_path: Optional[str] = None) -> PatternAutomationHooks:
    """Singleton accessor for PatternAutomationHooks."""
    global _hooks_instance
    if _hooks_instance is None:
        if db_path is None and config_path is None:
            raise ValueError("db_path or config_path required for first initialization")
        _hooks_instance = PatternAutomationHooks(db_path, config_path)
    return _hooks_instance
