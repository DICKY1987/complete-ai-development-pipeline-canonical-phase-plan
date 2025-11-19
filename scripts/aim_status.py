#!/usr/bin/env python3
"""AIM Status CLI Utility

Displays tool detection status and capability routing information for AIM registry.

Usage:
    python scripts/aim_status.py
"""

import sys
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aim.bridge import (
    detect_tool,
    get_aim_registry_path,
    get_tool_version,
    load_aim_registry,
    load_coordination_rules,
)


def print_tool_status():
    """Print detection status and version for all tools in AIM registry."""
    try:
        aim_path = get_aim_registry_path()
        print(f"AIM Registry Path: {aim_path}")
        print()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    try:
        registry = load_aim_registry()
    except Exception as e:
        print(f"Error loading registry: {e}")
        return 1

    tools = registry.get("tools", {})

    if not tools:
        print("No tools found in registry.")
        return 0

    # Print header
    print("=" * 70)
    print(f"{'Tool ID':<20} {'Detected':<12} {'Version'}")
    print("=" * 70)

    # Check each tool
    for tool_id in sorted(tools.keys()):
        detected = detect_tool(tool_id)
        detected_str = "Yes" if detected else "No"

        if detected:
            version = get_tool_version(tool_id)
            version_str = version if version else "N/A"
        else:
            version_str = "N/A"

        print(f"{tool_id:<20} {detected_str:<12} {version_str}")

    print("=" * 70)
    print()

    return 0


def print_capability_routing():
    """Print capability routing summary from coordination rules."""
    try:
        rules = load_coordination_rules()
    except Exception as e:
        print(f"Error loading coordination rules: {e}")
        return 1

    capabilities = rules.get("capabilities", {})

    if not capabilities:
        print("No capabilities defined in coordination rules.")
        return 0

    print("Capability Routing:")
    print("=" * 70)

    for cap_name in sorted(capabilities.keys()):
        cap_rules = capabilities[cap_name]
        primary = cap_rules.get("primary", "N/A")
        fallbacks = cap_rules.get("fallback", [])

        print(f"\n{cap_name}:")
        print(f"  Primary:  {primary}")

        if fallbacks:
            fallback_str = ", ".join(fallbacks)
            print(f"  Fallback: {fallback_str}")
        else:
            print(f"  Fallback: (none)")

    print("\n" + "=" * 70)

    return 0


def main():
    """Main entry point."""
    print("\n=== AIM Tool Registry Status ===\n")

    # Print tool detection status
    status = print_tool_status()
    if status != 0:
        return status

    # Print capability routing
    print()
    status = print_capability_routing()

    return status


if __name__ == "__main__":
    sys.exit(main())
