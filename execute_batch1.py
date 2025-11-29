import json
import os
import shutil
from pathlib import Path

# Load batches
with open('cleanup_batches.json', 'r') as f:
    batches = json.load(f)

def remove_batch(name, files, batch_size=20):
    """Remove files in small batches"""
    removed = []
    skipped = []
    
    for i, file in enumerate(files):
        if not os.path.exists(file):
            skipped.append(file)
            continue
            
        try:
            os.remove(file)
            removed.append(file)
            print(f"  ✓ Removed: {file}")
        except Exception as e:
            print(f"  ✗ Failed: {file} - {e}")
            skipped.append(file)
    
    return removed, skipped

print("\n🗑️  BATCH 1: Python Cache Files\n")
print("=" * 80)

cache_files = batches['cache']
print(f"\nRemoving {len(cache_files)} cache files...\n")

removed, skipped = remove_batch('cache', cache_files)

print(f"\n📊 Batch 1 Summary:")
print(f"  ✅ Removed: {len(removed)} files")
print(f"  ⏭️  Skipped: {len(skipped)} files (already removed or missing)")
print(f"\n✅ Batch 1 complete!")

# Save results
results = {
    'batch': 'cache',
    'total_attempted': len(cache_files),
    'removed': removed,
    'skipped': skipped
}

with open('batch1_results.json', 'w') as f:
    json.dump(results, f, indent=2)
