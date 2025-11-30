"""
Module Inventory Generator - EXEC-001 Pattern
Discovers all logical modules in the codebase and generates inventory.

Usage:
    python scripts/generate_module_inventory.py
    
Output:
    MODULES_INVENTORY.yaml - Complete module catalog
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-GENERATE-MODULE-INVENTORY-210
# DOC_ID: DOC-SCRIPT-SCRIPTS-GENERATE-MODULE-INVENTORY-147

import yaml
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import re


def discover_core_modules() -> List[Dict[str, Any]]:
    """Discover modules in core/ directory."""
    modules = []
    core_path = Path("core")
    
    if not core_path.exists():
        return modules
    
    # core/state/, core/engine/, core/planning/
    for subdir in core_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("_"):
            py_files = list(subdir.glob("*.py"))
            if py_files:
                modules.append({
                    'id': f"core-{subdir.name}",
                    'name': f"Core {subdir.name.title()}",
                    'layer': 'infra' if subdir.name == 'state' else 'domain',
                    'source_dir': str(subdir),
                    'files': [str(f) for f in py_files if f.name != '__init__.py']
                })
    
    return modules


def discover_error_modules() -> List[Dict[str, Any]]:
    """Discover error detection modules."""
    modules = []
    
    # error/engine/
    error_engine = Path("error/engine")
    if error_engine.exists():
        py_files = list(error_engine.glob("*.py"))
        if py_files:
            modules.append({
                'id': 'error-engine',
                'name': 'Error Detection Engine',
                'layer': 'domain',
                'source_dir': str(error_engine),
                'files': [str(f) for f in py_files if f.name != '__init__.py']
            })
    
    # error/plugins/*
    plugins_dir = Path("error/plugins")
    if plugins_dir.exists():
        for plugin in plugins_dir.iterdir():
            if plugin.is_dir() and not plugin.name.startswith("_"):
                py_files = list(plugin.glob("*.py"))
                if py_files:
                    modules.append({
                        'id': f"error-plugin-{plugin.name.replace('_', '-')}",
                        'name': f"Error Plugin: {plugin.name}",
                        'layer': 'ui',
                        'source_dir': str(plugin),
                        'files': [str(f) for f in py_files if f.name != '__init__.py']
                    })
    
    return modules


def discover_aim_modules() -> List[Dict[str, Any]]:
    """Discover AIM modules."""
    modules = []
    aim_path = Path("aim")
    
    if not aim_path.exists():
        return modules
    
    # AIM has submodules: registry/, environment/, services/
    for subdir in aim_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("_"):
            py_files = list(subdir.glob("*.py"))
            if py_files:
                modules.append({
                    'id': f"aim-{subdir.name}",
                    'name': f"AIM {subdir.name.title()}",
                    'layer': 'api',
                    'source_dir': str(subdir),
                    'files': [str(f) for f in py_files if f.name != '__init__.py']
                })
    
    return modules


def discover_pm_modules() -> List[Dict[str, Any]]:
    """Discover PM modules."""
    modules = []
    pm_path = Path("pm")
    
    if not pm_path.exists():
        return modules
    
    # PM structure: commands/, workspace/
    for subdir in pm_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("_"):
            py_files = list(subdir.glob("*.py"))
            if py_files:
                modules.append({
                    'id': f"pm-{subdir.name}",
                    'name': f"PM {subdir.name.title()}",
                    'layer': 'api',
                    'source_dir': str(subdir),
                    'files': [str(f) for f in py_files if f.name != '__init__.py']
                })
    
    return modules


def discover_specifications_modules() -> List[Dict[str, Any]]:
    """Discover specifications modules."""
    modules = []
    specs_path = Path("specifications")
    
    if not specs_path.exists():
        return modules
    
    # specifications/tools/, specifications/bridge/
    for subdir in specs_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("_") and subdir.name != "content":
            py_files = []
            # Recursively find Python files
            for py_file in subdir.rglob("*.py"):
                if py_file.name != '__init__.py':
                    py_files.append(str(py_file))
            
            if py_files:
                modules.append({
                    'id': f"specifications-{subdir.name}",
                    'name': f"Specifications {subdir.name.title()}",
                    'layer': 'domain' if subdir.name == 'tools' else 'api',
                    'source_dir': str(subdir),
                    'files': py_files
                })
    
    return modules


def detect_dependencies(module: Dict[str, Any], all_modules: List[Dict[str, Any]]) -> List[str]:
    """Detect module dependencies by analyzing imports."""
    dependencies = set()
    
    for file_path in module['files']:
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            # Find import statements
            imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            
            for imp in imports:
                # Check if import matches another module
                for other_module in all_modules:
                    if other_module['id'] == module['id']:
                        continue
                    
                    # Check if import starts with module's source directory
                    source_pattern = other_module['source_dir'].replace('/', '.').replace('\\', '.')
                    if imp.startswith(source_pattern):
                        dependencies.add(other_module['id'])
        except Exception:
            # Skip files that can't be read
            pass
    
    return sorted(list(dependencies))


def generate_ulid_prefix(index: int) -> str:
    """Generate ULID prefix for module (6 characters)."""
    # Use timestamp prefix 01 + 4-char hex counter
    return f"01{index:04X}"


def generate_inventory():
    """Generate complete module inventory."""
    print("🔍 Discovering modules...")
    
    all_modules = []
    all_modules.extend(discover_core_modules())
    all_modules.extend(discover_error_modules())
    all_modules.extend(discover_aim_modules())
    all_modules.extend(discover_pm_modules())
    all_modules.extend(discover_specifications_modules())
    
    print(f"   Found {len(all_modules)} modules")
    
    # Generate ULIDs and detect dependencies
    print("🔗 Analyzing dependencies...")
    for i, module in enumerate(all_modules):
        module['ulid_prefix'] = generate_ulid_prefix(i)
        module['dependencies'] = detect_dependencies(module, all_modules)
        module['file_count'] = len(module['files'])
        
        print(f"   {module['id']}: {module['file_count']} files, {len(module['dependencies'])} dependencies")
    
    # Build inventory structure
    inventory = {
        'metadata': {
            'generated': '2025-11-25T22:00:00Z',
            'total_modules': len(all_modules),
            'version': '1.0.0'
        },
        'layers': {
            'infra': [m['id'] for m in all_modules if m['layer'] == 'infra'],
            'domain': [m['id'] for m in all_modules if m['layer'] == 'domain'],
            'api': [m['id'] for m in all_modules if m['layer'] == 'api'],
            'ui': [m['id'] for m in all_modules if m['layer'] == 'ui']
        },
        'modules': all_modules
    }
    
    # Write to YAML
    output_path = Path("MODULES_INVENTORY.yaml")
    with output_path.open('w', encoding='utf-8') as f:
        yaml.dump(inventory, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ Generated {output_path}")
    print(f"   Total modules: {len(all_modules)}")
    print(f"   By layer:")
    for layer, module_ids in inventory['layers'].items():
        print(f"     {layer}: {len(module_ids)}")
    
    # Generate summary statistics
    total_files = sum(m['file_count'] for m in all_modules)
    print(f"   Total files: {total_files}")
    
    # Identify dependency-free modules (good migration candidates)
    independent = [m['id'] for m in all_modules if len(m['dependencies']) == 0]
    print(f"   Independent modules (migrate first): {len(independent)}")
    for mod_id in independent[:5]:  # Show first 5
        print(f"     - {mod_id}")


if __name__ == "__main__":
    generate_inventory()
