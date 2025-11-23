"""
UET V2 Master Plan - Patch Application Script

Applies RFC 6902 JSON Patches to copiolt plan_uv2.json to create UET_V2_MASTER_PLAN.json

Usage:
    python apply_patches.py
    python apply_patches.py --validate-only
    python apply_patches.py --patch 001 002

Requirements:
    pip install jsonpatch
"""

import json
import jsonpatch
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_PLAN_PATH = SCRIPT_DIR.parent / "base_plan.json"
OUTPUT_PATH = SCRIPT_DIR / "UET_V2_MASTER_PLAN.json"

PATCH_FILES = [
    SCRIPT_DIR / "001-config-integration.json",
    SCRIPT_DIR / "002-documentation-integration.json",
    SCRIPT_DIR / "003-uet-v2-specifications.json",
    SCRIPT_DIR / "004-planning-reference.json",
    SCRIPT_DIR / "005-adr-architecture-decisions.json",
    SCRIPT_DIR / "007-tool-adapter-interface.json",
    SCRIPT_DIR / "008-resilience-patterns.json",
    SCRIPT_DIR / "009-subagent-architecture-slash-commands.json",
]


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ Failed to load {path.name}: {e}")
        sys.exit(1)


def apply_patches(base_plan: Dict[str, Any], patch_files: List[Path]) -> Dict[str, Any]:
    """Apply all patches to base plan."""
    plan = base_plan.copy()
    total_operations = 0
    
    for patch_file in patch_files:
        if not patch_file.exists():
            print(f"⚠️  Patch file not found: {patch_file.name}")
            continue
        
        print(f"📄 Loading {patch_file.name}...")
        patch_data = load_json(patch_file)
        
        print(f"   Applying {len(patch_data)} operations...")
        try:
            plan = jsonpatch.apply_patch(plan, patch_data)
            total_operations += len(patch_data)
            print(f"   ✅ Applied successfully")
        except jsonpatch.JsonPatchException as e:
            print(f"   ❌ Patch application failed: {e}")
            sys.exit(1)
    
    print(f"\n✅ Applied {total_operations} total operations from {len(patch_files)} patches")
    return plan


def extract_ulids(obj: Any, ulids: List[str] = None) -> List[str]:
    """Recursively extract all ULID values."""
    if ulids is None:
        ulids = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.endswith('_ulid') and isinstance(value, str):
                ulids.append(value)
            extract_ulids(value, ulids)
    elif isinstance(obj, list):
        for item in obj:
            extract_ulids(item, ulids)
    
    return ulids


def validate_plan(plan: Dict[str, Any]) -> bool:
    """Validate the merged plan."""
    print("\n🔍 Validating merged plan...")
    
    # 1. Check ULID uniqueness
    print("   Checking ULID uniqueness...")
    ulids = extract_ulids(plan)
    duplicates = [ulid for ulid, count in Counter(ulids).items() if count > 1]
    
    if duplicates:
        print(f"   ❌ Duplicate ULIDs found: {duplicates}")
        return False
    print(f"   ✅ All {len(ulids)} ULIDs are unique")
    
    # 2. Check required metadata sections
    print("   Checking required metadata...")
    required_meta = [
        'architecture',
        'three_engine_problem',
        'system_alignment',
        'ai_policies',
        'project',
        'constraints'
    ]
    
    meta = plan.get('meta', {})
    missing = [key for key in required_meta if key not in meta]
    
    if missing:
        print(f"   ❌ Missing metadata sections: {missing}")
        return False
    print(f"   ✅ All required metadata present")
    
    # 3. Check phases exist
    print("   Checking phases...")
    phases = plan.get('phases', {})
    # Only require phases that are referenced in dependencies
    referenced_phases = set()
    for phase_id, phase in phases.items():
        for dep in phase.get('dependencies', []):
            referenced_phases.add(dep)
    
    missing_phases = [p for p in referenced_phases if p not in phases]
    if missing_phases:
        print(f"   ❌ Missing phases: {missing_phases}")
        return False
    print(f"   ✅ All referenced phases present ({len(phases)} total)")
    
    # 4. Check validation section
    print("   Checking validation...")
    validation = plan.get('validation', {})
    # Validation sections are optional, just check that validation object exists
    if validation:
        print(f"   ✅ Validation section exists with {len(validation)} rules")
    else:
        print(f"   ⚠️  No validation rules (optional)")
    
    print("\n✅ All validation checks passed")
    return True


def check_circular_dependencies(plan: Dict[str, Any]) -> bool:
    """Check for circular dependencies in phases."""
    print("   Checking for circular dependencies...")
    phases = plan.get('phases', {})
    
    def has_cycle(phase_id: str, visited: set, stack: set) -> bool:
        visited.add(phase_id)
        stack.add(phase_id)
        
        phase = phases.get(phase_id, {})
        for dep in phase.get('dependencies', []):
            if dep not in visited:
                if has_cycle(dep, visited, stack):
                    return True
            elif dep in stack:
                return True
        
        stack.remove(phase_id)
        return False
    
    for phase_id in phases:
        if has_cycle(phase_id, set(), set()):
            print(f"   ❌ Circular dependency detected in {phase_id}")
            return False
    
    print(f"   ✅ No circular dependencies found")
    return True


def main():
    """Main execution."""
    print("=" * 60)
    print("UET V2 Master Plan - Patch Application")
    print("=" * 60)
    
    # Parse arguments
    validate_only = '--validate-only' in sys.argv
    specific_patches = []
    
    if '--patch' in sys.argv:
        idx = sys.argv.index('--patch')
        specific_patches = sys.argv[idx + 1:]
        patch_files = [SCRIPT_DIR / f"{p}-*.json" for p in specific_patches]
        PATCH_FILES.clear()
        PATCH_FILES.extend([f for f in patch_files if f.exists()])
    
    # Load base plan
    if not BASE_PLAN_PATH.exists():
        print(f"❌ Base plan not found: {BASE_PLAN_PATH}")
        sys.exit(1)
    
    print(f"\n📖 Loading base plan: {BASE_PLAN_PATH.name}")
    base_plan = load_json(BASE_PLAN_PATH)
    print(f"   Base plan has {len(base_plan.get('phases', {}))} phases")
    
    if validate_only:
        print("\n🔍 Validation-only mode")
        if validate_plan(base_plan):
            print("\n✅ Base plan is valid")
            sys.exit(0)
        else:
            print("\n❌ Base plan validation failed")
            sys.exit(1)
    
    # Apply patches
    print(f"\n📦 Applying {len(PATCH_FILES)} patches...")
    merged_plan = apply_patches(base_plan, PATCH_FILES)
    
    # Validate merged plan
    if not validate_plan(merged_plan):
        print("\n❌ Validation failed - NOT saving merged plan")
        sys.exit(1)
    
    # Check circular dependencies
    if not check_circular_dependencies(merged_plan):
        print("\n❌ Circular dependency check failed - NOT saving merged plan")
        sys.exit(1)
    
    # Save merged plan
    print(f"\n💾 Saving merged plan to: {OUTPUT_PATH.name}")
    OUTPUT_PATH.write_text(json.dumps(merged_plan, indent=2), encoding='utf-8')
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SUCCESS - UET V2 Master Plan Created")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Total phases: {len(merged_plan.get('phases', {}))}")
    print(f"   - Total ULIDs: {len(extract_ulids(merged_plan))}")
    print(f"   - File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    print(f"\n📄 Output: {OUTPUT_PATH}")
    print("\n🎯 Next steps:")
    print("   1. Review UET_V2_MASTER_PLAN.json")
    print("   2. Create CLAUDE.md, update AGENTS.md")
    print("   3. Set up sandbox directories")
    print("   4. Begin Phase 0 execution")


if __name__ == "__main__":
    main()
