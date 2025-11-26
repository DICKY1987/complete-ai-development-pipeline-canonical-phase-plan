"""
Auto-generated module migration script
Pattern: EXEC-001 (Batch File Creator)
Generated: {generation_date}
"""

from pathlib import Path
import shutil
import sys

MODULE_ID = "{module_id}"
ULID_PREFIX = "{ulid_prefix}"
SOURCE_DIR = Path("{source_dir}")
DEST_DIR = Path(f"modules/{{MODULE_ID}}")

FILES_TO_MIGRATE = [
    # Populated by generator
    # ("{src_file}", "{ulid}_{dest_file}"),
]

def migrate():
    """Migrate module files with ULID prefixes."""
    print(f"Migrating module: {MODULE_ID}")
    print(f"Source: {SOURCE_DIR}")
    print(f"Destination: {DEST_DIR}")
    
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    for src_name, dest_name in FILES_TO_MIGRATE:
        src = SOURCE_DIR / src_name
        dest = DEST_DIR / dest_name
        
        if not src.exists():
            print(f"❌ Source not found: {src}")
            sys.exit(1)
            
        shutil.copy2(src, dest)
        print(f"✓ {src} → {dest}")

    # Ground truth verification
    migrated = list(DEST_DIR.glob(f"{ULID_PREFIX}_*.py"))
    expected = len(FILES_TO_MIGRATE)
    actual = len(migrated)
    
    assert actual == expected, f"Expected {expected} files, got {actual}"
    print(f"✅ Migrated {actual} files successfully")
    
    return 0

if __name__ == "__main__":
    sys.exit(migrate())
