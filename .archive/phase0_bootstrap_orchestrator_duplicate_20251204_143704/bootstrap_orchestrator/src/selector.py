"""Profile Selector - WS-02-01B

Selects the best profile for a project based on discovery results.
Uses a decision tree approach with confidence scoring.
"""

# DOC_ID: DOC-CORE-BOOTSTRAP-SELECTOR-SELECTOR-001

import json
from pathlib import Path
from typing import Dict, Tuple


class ProfileSelector:
    """Selects appropriate profile based on discovery."""

    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles = self._load_profiles()

    def _load_profiles(self) -> Dict:
        """Load all available profiles."""
        profiles = {}
        for profile_dir in self.profiles_dir.iterdir():
            if not profile_dir.is_dir():
                continue

            profile_file = profile_dir / "profile.json"
            if profile_file.exists():
                with open(profile_file) as f:
                    profile = json.load(f)
                    profiles[profile["profile_id"]] = profile

        return profiles

    def select(self, discovery: Dict) -> Tuple[str, Dict]:
        """
        Select best profile for project.

        Args:
            discovery: Output from ProjectScanner.scan()

        Returns:
            (profile_id, profile_data)
        """
        domain = discovery["domain"]
        confidence = discovery.get("domain_confidence", 0.5)
        languages = discovery.get("languages", [])

        # Decision tree
        if domain == "software-dev" and confidence > 0.7:
            # Check primary language
            if languages and languages[0]["language"] == "python":
                return "software-dev-python", self.profiles["software-dev-python"]
            else:
                # For now, fallback to python profile
                return "software-dev-python", self.profiles["software-dev-python"]

        elif domain == "data-pipeline" and confidence > 0.6:
            return "data-pipeline", self.profiles["data-pipeline"]

        elif domain == "operations" and confidence > 0.6:
            return "operations", self.profiles["operations"]

        elif domain == "documentation" and confidence > 0.7:
            return "documentation", self.profiles["documentation"]

        else:
            # Mixed or low confidence -> generic
            return "generic", self.profiles["generic"]


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python selector.py <discovery.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        discovery = json.load(f)

    selector = ProfileSelector()
    profile_id, profile = selector.select(discovery)

    print(json.dumps({"selected_profile": profile_id, "profile": profile}, indent=2))


if __name__ == "__main__":
    main()
