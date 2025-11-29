import json
import os
import sys

# Load duplicate report
with open('baseline_duplicates_report.json', 'r') as f:
    data = json.load(f)

print(f"\n📊 Duplicate Analysis:")
print(f"  Total groups: {len(data['duplicate_groups'])}")
print(f"  Total duplicates: {data['total_duplicates']}")
print(f"  Space savings: {data['potential_savings_mb']:.2f} MB\n")

# Categorize duplicates
cache_files = []
doc_files = []
other_files = []

for group in data['duplicate_groups']:
    canonical = group['canonical']
    for file in group['files']:
        if file != canonical:  # Skip canonical
            if '__pycache__' in file or file.endswith('.pyc'):
                cache_files.append(file)
            elif file.endswith('.md') or file.endswith('.txt'):
                doc_files.append(file)
            else:
                other_files.append(file)

print(f"📁 Categorized duplicates:")
print(f"  Python cache: {len(cache_files)} files")
print(f"  Documentation: {len(doc_files)} files")
print(f"  Other: {len(other_files)} files\n")

# Show strategy
print(f"🎯 Cleanup Strategy:")
print(f"  Batch 1: Remove {len(cache_files)} cache files (safe, auto-regenerated)")
print(f"  Batch 2: Remove {len(doc_files)} documentation duplicates")
print(f"  Batch 3: Remove {len(other_files)} other duplicates\n")

# Export batches for review
batches = {
    'cache': cache_files[:50],  # First 50 cache files
    'docs': doc_files[:50],    # First 50 docs
    'other': other_files[:50]  # First 50 others
}

with open('cleanup_batches.json', 'w') as f:
    json.dump(batches, f, indent=2)

print(f"✅ Batch plan exported to: cleanup_batches.json")
print(f"\nNext: Review batches, then execute removal")
