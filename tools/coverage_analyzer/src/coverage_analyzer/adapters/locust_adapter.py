"""
Locust Adapter - Layer 4 Operational Validation.

Integrates Locust load testing framework for operational validation.
Measures system behavior under load, performance metrics, and stability.
"""
DOC_ID: DOC-SCRIPT-ADAPTERS-LOCUST-ADAPTER-813

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from coverage_analyzer.adapters.base_adapter import BaseAdapter, ToolNotAvailableError

logger = logging.getLogger(__name__)


class LocustAdapter(BaseAdapter):
    """Adapter for Locust load testing framework."""

    def __init__(self):
        """Initialize the Locust adapter."""
        super().__init__()
        self.tool_name = "locust"

    def _get_tool_name(self) -> str:
        """Get the tool name."""
        return "locust"

    def is_available(self) -> bool:
        """Check if Locust is installed and available."""
        try:
            result = subprocess.run(
                ["locust", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            available = result.returncode == 0
            if available:
                logger.debug(f"Locust version: {result.stdout.strip()}")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Locust not found. Install: pip install locust")
            return False

    def execute(
        self,
        target_path: Optional[str] = None,
        users: int = 10,
        spawn_rate: int = 2,
        run_time: str = "30s",
        locustfile: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute Locust load tests.

        Args:
            target_path: Path to project (for finding locustfile)
            users: Number of concurrent users to simulate
            spawn_rate: User spawn rate (users per second)
            run_time: Test duration (e.g., "30s", "1m")
            locustfile: Path to locustfile (optional, auto-detect if None)
            **kwargs: Additional Locust options

        Returns:
            Dict containing load test results and metrics

        Raises:
            ToolNotAvailableError: If Locust is not available or execution fails
        """
        if not self.is_available():
            raise ToolNotAvailableError(
                "Locust not available. Install: pip install locust"
            )

        # Find or validate locustfile
        locust_path = self._find_locustfile(target_path, locustfile)
        if not locust_path:
            # Create a minimal locustfile for basic testing
            locust_path = self._create_minimal_locustfile(target_path)

        logger.info(
            f"Running Locust: users={users}, spawn_rate={spawn_rate}, time={run_time}"
        )

        # Prepare Locust command
        cmd = [
            "locust",
            "-f",
            str(locust_path),
            "--headless",
            "--users",
            str(users),
            "--spawn-rate",
            str(spawn_rate),
            "--run-time",
            run_time,
            "--html",
            "locust_report.html",
            "--csv",
            "locust_stats",
        ]

        # Add host if provided
        if "host" in kwargs:
            cmd.extend(["--host", kwargs["host"]])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
                cwd=target_path,
            )

            if result.returncode != 0:
                logger.warning(f"Locust execution issues: {result.stderr}")

            # Parse results
            metrics = self._parse_locust_output(
                result.stdout, result.stderr, target_path
            )

            logger.info(
                f"Load test complete: {metrics.get('total_requests', 0)} requests"
            )
            return metrics

        except subprocess.TimeoutExpired:
            logger.error("Locust execution timed out")
            raise ToolNotAvailableError("Locust execution timed out (>5 min)")
        except Exception as e:
            logger.error(f"Locust execution failed: {e}")
            raise ToolNotAvailableError(f"Locust execution failed: {e}")

    def _find_locustfile(
        self, target_path: Optional[str], locustfile: Optional[str]
    ) -> Optional[Path]:
        """Find locustfile in project."""
        if locustfile:
            path = Path(locustfile)
            if path.exists():
                return path

        if target_path:
            # Common locustfile locations
            candidates = [
                Path(target_path) / "locustfile.py",
                Path(target_path) / "tests" / "locustfile.py",
                Path(target_path) / "load_tests" / "locustfile.py",
            ]
            for candidate in candidates:
                if candidate.exists():
                    logger.debug(f"Found locustfile: {candidate}")
                    return candidate

        return None

    def _create_minimal_locustfile(self, target_path: Optional[str]) -> Path:
        """Create a minimal locustfile for basic testing."""
        locustfile_content = '''"""
Minimal Locustfile for basic load testing.
Auto-generated by coverage_analyzer.
"""

from locust import HttpUser, task, between


class MinimalUser(HttpUser):
    """Minimal user for basic load testing."""

    wait_time = between(1, 2)

    @task
    def index(self):
        """Test index endpoint."""
        self.client.get("/")
'''

        # Create in temp directory or target path
        if target_path:
            locust_path = Path(target_path) / "locustfile_generated.py"
        else:
            temp_dir = tempfile.gettempdir()
            locust_path = Path(temp_dir) / "locustfile_generated.py"

        locust_path.write_text(locustfile_content)
        logger.info(f"Created minimal locustfile: {locust_path}")
        return locust_path

    def _parse_locust_output(
        self, stdout: str, stderr: str, target_path: Optional[str]
    ) -> Dict[str, Any]:
        """Parse Locust output to extract metrics."""
        metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "min_response_time": 0.0,
            "max_response_time": 0.0,
            "requests_per_second": 0.0,
            "failure_rate": 0.0,
            "users": 0,
            "tool_name": "locust",
        }

        # Try to parse CSV stats if available
        if target_path:
            csv_path = Path(target_path) / "locust_stats_stats.csv"
            if csv_path.exists():
                try:
                    metrics.update(self._parse_csv_stats(csv_path))
                except Exception as e:
                    logger.warning(f"Failed to parse CSV stats: {e}")

        # Parse from stdout as fallback
        lines = stdout.split("\n") + stderr.split("\n")
        for line in lines:
            if "requests" in line.lower() and "(" in line:
                # Extract request count
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i > 0:
                            metrics["total_requests"] = int(part)
                            break
                except Exception:
                    pass

            if "response time" in line.lower() or "median" in line.lower():
                # Extract response times
                try:
                    import re

                    numbers = re.findall(r"\d+\.?\d*", line)
                    if numbers:
                        metrics["avg_response_time"] = float(numbers[0])
                except Exception:
                    pass

        # Calculate derived metrics
        if metrics["total_requests"] > 0:
            metrics["failure_rate"] = (
                metrics["failed_requests"] / metrics["total_requests"]
            ) * 100

        return metrics

    def _parse_csv_stats(self, csv_path: Path) -> Dict[str, Any]:
        """Parse Locust CSV statistics file."""
        import csv

        metrics = {}

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Aggregated":
                    metrics["total_requests"] = int(row.get("Request Count", 0))
                    metrics["failed_requests"] = int(row.get("Failure Count", 0))
                    metrics["avg_response_time"] = float(
                        row.get("Average Response Time", 0)
                    )
                    metrics["min_response_time"] = float(
                        row.get("Min Response Time", 0)
                    )
                    metrics["max_response_time"] = float(
                        row.get("Max Response Time", 0)
                    )
                    metrics["requests_per_second"] = float(row.get("Requests/s", 0))

        return metrics
