import json
import os

# Load discovery data
with open('baseline_duplicates_report.json', 'r') as f:
    data = json.load(f)

# Get documentation duplicates
doc_files = []
for group in data['duplicate_groups']:
    canonical = group['canonical']
    for file in group['files']:
        if file != canonical and (file.endswith('.md') or file.endswith('.txt')):
            doc_files.append(file)

print(f"📊 Documentation duplicates: {len(doc_files)} files")
print(f"\nRemoving first 30 files...\n")

removed = []
skipped = []

for file in doc_files[:30]:
    if not os.path.exists(file):
        skipped.append(file)
        continue
        
    try:
        os.remove(file)
        removed.append(file)
        # Show shortened path
        short_path = file if len(file) < 80 else file[:77] + "..."
        print(f"  ✓ Removed: {short_path}")
    except Exception as e:
        print(f"  ✗ Failed: {file[:50]}... - {e}")
        skipped.append(file)

print(f"\n📊 Batch 3 Summary:")
print(f"  ✅ Removed: {len(removed)} files")
print(f"  ⏭️  Skipped: {len(skipped)} files")

# Save results
results = {
    'batch': 'docs-1',
    'removed': removed,
    'skipped': skipped
}

with open('batch3_results.json', 'w') as f:
    json.dump(results, f, indent=2)
