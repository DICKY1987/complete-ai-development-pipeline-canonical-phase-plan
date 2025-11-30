# DOC_LINK: DOC-SCRIPT-DEV-UPDATE-MARKDOWN-PATHS-270
import os
import re
from pathlib import Path

def get_repo_root():
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find repository root (.git directory not found)")

REPO_ROOT = get_repo_root()

# Define the old root directories and their new prefixes within meta/
MOVED_DIRS_MAP = {
    "PHASE_DEV_DOCS": "meta/PHASE_DEV_DOCS",
    "plans": "meta/plans",
    "Coordination Mechanisms": "meta/Coordination Mechanisms",
}

# Build a mapping of all old absolute file paths to their new absolute file paths
# and also new absolute file paths to their old absolute file paths
old_to_new_abs_path_map = {}
new_to_old_abs_path_map = {}

# Collect all markdown files currently in the meta directory
all_meta_md_files = list(REPO_ROOT.glob("meta/**/*.md"))

for new_abs_path_obj in all_meta_md_files:
    new_rel_path = str(new_abs_path_obj.relative_to(REPO_ROOT)).replace('\\', '/') # Normalize path separators
    
    # Determine the original relative path
    original_rel_path = None
    for old_dir_name, new_dir_prefix in MOVED_DIRS_MAP.items():
        if new_rel_path.startswith(new_dir_prefix):
            # Reconstruct the original relative path
            # This assumes the structure within the moved directory is preserved
            original_rel_path = old_dir_name + new_rel_path[len(new_dir_prefix):]
            break
    
    if original_rel_path:
        old_abs_path = REPO_ROOT / original_rel_path
        old_to_new_abs_path_map[str(old_abs_path)] = str(new_abs_path_obj)
        new_to_old_abs_path_map[str(new_abs_path_obj)] = str(old_abs_path)
    else:
        print(f"DEBUG: Could not determine original_rel_path for {new_rel_path}")

print(f"DEBUG: old_to_new_abs_path_map keys: {list(old_to_new_abs_path_map.keys())[:5]}...") # Print first 5 keys
print(f"DEBUG: new_to_old_abs_path_map keys: {list(new_to_old_abs_path_map.keys())[:5]}...") # Print first 5 keys


# Regex to find markdown links: [text](link)
# This regex is simplified and might need refinement for edge cases
MARKDOWN_LINK_REGEX = re.compile(r'\[.*?\]\((.*?)\)')

def update_markdown_paths():
    for new_abs_file_path in all_meta_md_files:
        
        # Get the original absolute path of the current file
        original_abs_file_path_str = new_to_old_abs_path_map.get(str(new_abs_file_path))
        if not original_abs_file_path_str:
            print(f"Warning: Could not find original path for {new_abs_file_path}. Skipping.")
            continue
        original_abs_file_path = Path(original_abs_file_path_str)

        content = new_abs_file_path.read_text(encoding='utf-8')
        updated_content = content

        # Find all links in the content
        for match in MARKDOWN_LINK_REGEX.finditer(content):
            link_path = match.group(1)
            
            # Skip absolute URLs
            if link_path.startswith('http://') or link_path.startswith('https://'):
                continue
            
            # Handle absolute paths (starting with /)
            if link_path.startswith('/'):
                # Resolve against repo root
                resolved_old_linked_path = str(REPO_ROOT / link_path[1:])
            else:
                # Resolve relative paths against the original directory of the current file
                resolved_old_linked_path = str(original_abs_file_path.parent / link_path)
            
            # Normalize path to handle '..' and '.'
            resolved_old_linked_path = str(Path(resolved_old_linked_path).resolve())
            
            print(f"DEBUG: Current file: {new_abs_file_path}")
            print(f"DEBUG: Link path: {link_path}")
            print(f"DEBUG: Resolved old linked path: {resolved_old_linked_path}")

            # Check if the linked file was also moved
            if resolved_old_linked_path in old_to_new_abs_path_map:
                new_linked_abs_path = Path(old_to_new_abs_path_map[resolved_old_linked_path])
                
                # Calculate new relative path from the current file's new location to the linked file's new location
                try:
                    new_relative_link_path = os.path.relpath(new_linked_abs_path, new_abs_file_path.parent)
                    # Ensure forward slashes for markdown
                    new_relative_link_path = new_relative_link_path.replace('\\', '/')
                    
                    # Replace the old link_path with the new one in the content
                    # Use re.escape for link_path to handle special characters in regex
                    # This replacement needs to be careful to only replace the link_path part of the markdown link
                    # A more robust approach would be to rebuild the entire link.
                    # For now, let's assume the link_path is unique enough within the link.
                    updated_content = updated_content.replace(f'({link_path})', f'({new_relative_link_path})')
                except ValueError as e:
                    print(f"Error calculating relative path for {new_abs_file_path} to {new_linked_abs_path}: {e}")
                    continue
            else:
                print(f"DEBUG: Linked file {resolved_old_linked_path} not found in old_to_new_abs_path_map.")

        if updated_content != content:
            print(f"Updating links in: {new_abs_file_path}")
            new_abs_file_path.write_text(updated_content, encoding='utf-8')
        else:
            print(f"No changes needed for: {new_abs_file_path}")

if __name__ == "__main__":
    update_markdown_paths()