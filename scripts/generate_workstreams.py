import argparse
import json
import sys
from pathlib import Path

# Adjust sys.path to allow importing bundles
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "src"))

from pipeline import planner

def main():
    parser = argparse.ArgumentParser(
        description="Generate draft workstream bundles from a specification (stub).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--spec-id",
        type=str,
        required=True,
        help="Identifier for the specification (e.g., OpenSpec ID, CCPM issue ID)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="workstreams",
        help="Directory to output the generated draft workstream JSON files."
    )
    parser.add_argument(
        "--options",
        type=json.loads,
        default="{}",
        help="JSON string of options for the planner (e.g., '{\"group_by\": \"language\"}')."
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Planner v0 stub: Not yet implemented. See src/pipeline/planner.py.", file=sys.stderr)
    print(f"Attempting to generate draft workstreams for spec-id: {args.spec_id}", file=sys.stderr)
    print(f"Output directory: {output_dir}", file=sys.stderr)
    print(f"Planner options: {args.options}", file=sys.stderr)

    try:
        # Call the planner stub
        draft_bundles = planner.plan_workstreams_from_spec(args.spec_id, args.options)

        if draft_bundles:
            for i, bundle_data in enumerate(draft_bundles):
                # Ensure the ID is unique for the generated stub
                if bundle_data.get("id") == "ws-generated-placeholder":
                    bundle_data["id"] = f"ws-generated-placeholder-{args.spec_id}-{i}"
                
                output_file = output_dir / f"{bundle_data['id']}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(bundle_data, f, indent=2)
                print(f"Generated draft workstream: {output_file}", file=sys.stderr)
        else:
            print("Planner stub generated no workstreams.", file=sys.stderr)

        print("\nNote: This is a v0 planner stub. The generated workstreams are minimal placeholders.", file=sys.stderr)
        print("Full automated planning logic is not yet implemented.", file=sys.stderr)
        sys.exit(0)

    except NotImplementedError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
