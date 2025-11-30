# DOC_LINK: DOC-PAT-EXECUTE-BATCH-FINAL-342
# DOC_LINK: DOC-PAT-EXECUTE-BATCH-FINAL-298
# DOC_LINK: DOC-PAT-EXECUTE-BATCH-FINAL-283
# DOC_LINK: DOC-PAT-EXECUTE-BATCH-FINAL-268
import json
import os
from pathlib import Path

# Load discovery data
with open('baseline_duplicates_report.json', 'r') as f:
    data = json.load(f)

# Load already removed files
removed_files = set()
for batch_file in ['batch1_results.json', 'batch2_results.json', 'batch3_results.json']:
    if os.path.exists(batch_file):
        with open(batch_file, 'r') as f:
            batch = json.load(f)
            removed_files.update(batch['removed'])

# Get all remaining duplicates
all_duplicates = []
for group in data['duplicate_groups']:
    canonical = group['canonical']
    for file in group['files']:
        if file != canonical and file not in removed_files:
            all_duplicates.append(file)

print(f"📊 Remaining duplicates: {len(all_duplicates)} files")
print(f"\nRemoving all remaining duplicates...\n")

removed = []
skipped = []
errors = []

for i, file in enumerate(all_duplicates, 1):
    if not os.path.exists(file):
        skipped.append(file)
        continue
        
    try:
        os.remove(file)
        removed.append(file)
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(all_duplicates)} files processed...")
    except Exception as e:
        errors.append((file, str(e)))
        print(f"  ✗ Failed: {file[:60]}... - {e}")

print(f"\n📊 Final Cleanup Summary:")
print(f"  ✅ Removed: {len(removed)} files")
print(f"  ⏭️  Skipped: {len(skipped)} files (already removed)")
print(f"  ❌ Errors: {len(errors)} files")

if errors:
    print(f"\n⚠️  Errors encountered:")
    for file, error in errors[:10]:
        print(f"  - {file[:60]}...")

# Save results
results = {
    'batch': 'final',
    'total_attempted': len(all_duplicates),
    'removed': removed,
    'skipped': skipped,
    'errors': errors
}

with open('batch_final_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Cleanup complete!")
print(f"\nTotal duplicates removed: {131 + len(removed)} / 524")
