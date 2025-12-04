#!/usr/bin/env python3
"""
README Generator - Execution Pattern EXEC-004 (Doc Standardizer)

Ground Truth Verification: file_exists(README.md) per target directory
Batch Size: 6 directories per batch
Decision Elimination: All structural decisions made in folder_metadata.yaml
"""
DOC_ID: DOC - SCRIPT - SCRIPTS - GENERATE - READMES - 716
DOC_ID: DOC - SCRIPT - SCRIPTS - GENERATE - READMES - 716

import os
from datetime import datetime
from pathlib import Path

import yaml

# Template loaded ONCE
TEMPLATE = """# {folder_name}

**Module Path**: `{module_path}`
**Layer**: {layer}
**Status**: {status}

## Purpose

{purpose}

## Contents

{contents}

## Key Components

{key_components}

## Dependencies

{dependencies}

## Usage

{usage}

## Integration Points

{integration_points}

## Related Documentation

{related_docs}

---

**Generated**: {timestamp}
**Framework**: Universal Execution Templates (UET)
"""


def load_folder_metadata():
    """Load ALL context UPFRONT (anti-pattern guard: no mid-batch lookups)"""
    metadata_path = Path(__file__).parent.parent / "folder_metadata.yaml"
    if metadata_path.exists():
        with open(metadata_path) as f:
            return yaml.safe_load(f)
    return {}


def get_directory_structure(path: Path) -> str:
    """Generate directory structure listing"""
    if not path.exists():
        return "Directory not found"

    items = []
    try:
        for item in sorted(path.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_dir():
                items.append(f"- `{item.name}/` - Directory")
            else:
                items.append(f"- `{item.name}` - File")
    except PermissionError:
        return "Permission denied"

    return "\n".join(items) if items else "Empty directory"


def generate_readme(folder_path: Path, metadata: dict) -> str:
    """Generate README content from template and metadata"""
    folder_name = folder_path.name
    rel_path = folder_path.relative_to(Path.cwd())

    # Extract metadata or use defaults
    meta = metadata.get(str(rel_path), {})

    return TEMPLATE.format(
        folder_name=folder_name,
        module_path=str(rel_path).replace("\\", "/"),
        layer=meta.get("layer", "Not specified"),
        status=meta.get("status", "Active"),
        purpose=meta.get("purpose", "Purpose to be documented"),
        contents=get_directory_structure(folder_path),
        key_components=meta.get("key_components", "To be documented"),
        dependencies=meta.get("dependencies", "None specified"),
        usage=meta.get("usage", "Usage examples to be added"),
        integration_points=meta.get("integration_points", "To be documented"),
        related_docs=meta.get("related_docs", "None specified"),
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


def find_folders_without_readme(root_path: Path) -> list[Path]:
    """Find all directories missing README files"""
    folders = []
    exclude_patterns = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".worktrees",
        ".pytest_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_patterns]

        path = Path(dirpath)
        has_readme = any(f.upper().startswith("README") for f in filenames)

        if not has_readme and path != root_path:
            folders.append(path)

    return folders


def create_readme_batch(folders: list[Path], metadata: dict) -> dict:
    """Create READMEs in batch (6 per batch)"""
    results = {"created": [], "failed": []}

    for folder in folders:
        try:
            readme_path = folder / "README.md"
            content = generate_readme(folder, metadata)

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Ground truth verification
            if readme_path.exists():
                results["created"].append(str(folder))
            else:
                results["failed"].append(str(folder))

        except Exception as e:
            results["failed"].append(f"{folder}: {e}")

    return results


def main():
    """Main execution - Pattern EXEC-004"""
    print("README Generator - EXEC-004 Doc Standardizer")
    print("=" * 60)

    # Load ALL context UPFRONT
    print("\n[1/4] Loading metadata...")
    metadata = load_folder_metadata()

    # Find target folders
    print("[2/4] Scanning for folders without READMEs...")
    folders = find_folders_without_readme(Path.cwd())
    print(f"Found {len(folders)} folders without READMEs")

    if not folders:
        print("✅ All folders have READMEs!")
        return

    # Batch execution (6 folders per batch)
    print("\n[3/4] Generating READMEs in batches...")
    batch_size = 6
    all_results = {"created": [], "failed": []}

    for i in range(0, len(folders), batch_size):
        batch = folders[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        print(f"  Batch {batch_num}: {len(batch)} folders")

        results = create_readme_batch(batch, metadata)
        all_results["created"].extend(results["created"])
        all_results["failed"].extend(results["failed"])

    # Verification
    print("\n[4/4] Verification Results:")
    print(f"✅ Created: {len(all_results['created'])}")
    print(f"❌ Failed: {len(all_results['failed'])}")

    if all_results["failed"]:
        print("\nFailed items:")
        for item in all_results["failed"]:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
