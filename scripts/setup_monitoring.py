"""Setup monitoring with healthchecks.io integration."""
import os
import requests
from typing import Optional


class HealthcheckMonitor:
    """Wrapper for healthchecks.io dead man's switch monitoring."""
    
    def __init__(self, healthcheck_url: Optional[str] = None):
        self.healthcheck_url = healthcheck_url or os.environ.get("HEALTHCHECK_URL")
        self.enabled = bool(self.healthcheck_url)
    
    def ping_start(self):
        """Signal execution start."""
        if self.enabled:
            try:
                requests.get(f"{self.healthcheck_url}/start", timeout=5)
            except Exception as e:
                print(f"⚠️ Healthcheck ping failed: {e}")
    
    def ping_success(self):
        """Signal successful execution."""
        if self.enabled:
            try:
                requests.get(self.healthcheck_url, timeout=5)
                print("✅ Healthcheck: Success")
            except Exception as e:
                print(f"⚠️ Healthcheck ping failed: {e}")
    
    def ping_failure(self, error: str = ""):
        """Signal execution failure."""
        if self.enabled:
            try:
                requests.get(
                    f"{self.healthcheck_url}/fail",
                    timeout=5,
                    data=error.encode("utf-8")
                )
                print("❌ Healthcheck: Failure")
            except Exception as e:
                print(f"⚠️ Healthcheck ping failed: {e}")
