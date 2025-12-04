"""Artifact Generator - WS-02-02A"""
DOC_ID: DOC-CORE-BOOTSTRAP-GENERATOR-743

DOC_ID: DOC - CORE - BOOTSTRAP - GENERATOR - 743

import json
from pathlib import Path

import yaml


class ArtifactGenerator:
    def __init__(self, discovery, profile, output_dir="."):
        self.discovery = discovery
        self.profile = profile
        self.output_dir = Path(output_dir)
        self.project_id = f"PRJ-{discovery['project_name'].upper().replace(' ', '_')}"

    def generate_all(self):
        # Create directories
        for d in [
            ".tasks",
            ".ledger/patches",
            ".ledger/runs",
            ".worktrees",
            ".quarantine",
            "registry",
        ]:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

        # Generate PROJECT_PROFILE.yaml
        profile_data = {
            "project_id": self.project_id,
            "project_name": self.discovery["project_name"],
            "project_root": self.discovery["project_root"],
            "domain": self.discovery["domain"],
            "profile_id": self.profile["profile_id"],
            "profile_version": self.profile.get("profile_version", "1.0.0"),
            "resource_types": {"files": {"root": ".", "tracked_by": "git"}},
            "available_tools": [],
            "framework_paths": {
                "tasks_dir": ".tasks/",
                "ledger_dir": ".ledger/",
                "worktrees_dir": ".worktrees/",
                "quarantine_dir": ".quarantine/",
                "registry_file": "registry/project.registry.yaml",
            },
            "constraints": {"patch_only": True, "max_lines_changed": 500},
        }

        with open(self.output_dir / "PROJECT_PROFILE.yaml", "w") as f:
            yaml.dump(profile_data, f)

        # Generate router_config.json
        router = {
            "version": "1.0.0",
            "apps": {},
            "routing": {"rules": []},
            "defaults": {"max_attempts": 3, "timeout_seconds": 600},
        }

        with open(self.output_dir / "router_config.json", "w") as f:
            json.dump(router, f, indent=2)

        return {
            "project_profile": "PROJECT_PROFILE.yaml",
            "router_config": "router_config.json",
        }


if __name__ == "__main__":
    import sys

    discovery = json.load(open(sys.argv[1]))
    profile = json.load(open(sys.argv[2]))
    output = sys.argv[3] if len(sys.argv) > 3 else "."
    gen = ArtifactGenerator(discovery, profile, output)
    result = gen.generate_all()
    print(json.dumps({"status": "success", "artifacts": result}, indent=2))
# DOC_LINK: DOC-CORE-BOOTSTRAP-GENERATOR-139
# DOC_LINK: DOC-CORE-BOOTSTRAP-GENERATOR-614
# DOC_LINK: DOC-CORE-BOOTSTRAP-GENERATOR-639
# DOC_LINK: DOC-CORE-BOOTSTRAP-GENERATOR-738
