# DOC_LINK: DOC-PAT-EXECUTE-BATCH2-340
# DOC_LINK: DOC-PAT-EXECUTE-BATCH2-296
# DOC_LINK: DOC-PAT-EXECUTE-BATCH2-281
# DOC_LINK: DOC-PAT-EXECUTE-BATCH2-266
import json
import os

# Load original batches
with open('cleanup_batches.json', 'r') as f:
    batches = json.load(f)

# Load batch 1 results
with open('batch1_results.json', 'r') as f:
    batch1 = json.load(f)

# Get all cache files and filter out already removed
all_cache = batches['cache']
removed_set = set(batch1['removed'])

# Create batch 2 with remaining cache files (next 51 files)
# First, recalculate from full list
with open('baseline_duplicates_report.json', 'r') as f:
    data = json.load(f)

cache_files = []
for group in data['duplicate_groups']:
    canonical = group['canonical']
    for file in group['files']:
        if file != canonical and ('__pycache__' in file or file.endswith('.pyc')):
            if file not in removed_set:
                cache_files.append(file)

print(f"📊 Remaining cache files: {len(cache_files)}")

# Remove next batch
removed = []
skipped = []

for file in cache_files[:51]:  # Next 51 files
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

print(f"\n📊 Batch 2 Summary:")
print(f"  ✅ Removed: {len(removed)} files")
print(f"  ⏭️  Skipped: {len(skipped)} files")

# Save results
results = {
    'batch': 'cache-2',
    'removed': removed,
    'skipped': skipped
}

with open('batch2_results.json', 'w') as f:
    json.dump(results, f, indent=2)
