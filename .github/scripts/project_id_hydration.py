import json
import os
import sys
from typing import Dict

from github_project_utils import GitHubProjectClient


def run() -> None:
    org = os.getenv("TARGET_ORG") or os.getenv("GITHUB_REPOSITORY_OWNER")
    project_number = os.getenv("PROJECT_NUMBER")
    if not org or not project_number:
        raise RuntimeError("TARGET_ORG and PROJECT_NUMBER env vars are required")
    client = GitHubProjectClient()
    project_id, fields = client.resolve_project_and_fields(org, int(project_number))

    result: Dict[str, object] = {"project_node_id": project_id, "fields": []}
    for field in fields:
        entry = {
            "id": field.get("id"),
            "name": field.get("name"),
            "type": field.get("__typename"),
        }
        if field.get("options"):
            entry["options"] = field["options"]
        result["fields"].append(entry)

    output_path = os.getenv("OUTPUT_PATH", ".github/scripts/id_cache.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote project metadata to {output_path}")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print(f"Hydration failed: {exc}")
        sys.exit(1)
