# Execution Pattern: EXEC-HYBRID-003 - Module Documentation Generation

**Pattern ID**: EXEC-HYBRID-003  
**Date**: 2025-12-03  
**Purpose**: Generate module-specific documentation from existing docs  
**Scope**: 31 modules × 3-5 doc files each  
**Estimated Time**: 45 minutes  
**Speedup**: 6x faster than manual (4.5h → 45min)

---

## Pattern Overview

**Problem**: Documentation scattered across global `docs/` directory. Hard to find module-specific docs.

**Solution**: Extract and generate module-specific docs in `module/docs/`, keep architectural docs at root.

**Key Principle**: Module documentation lives with the module - architecture.md, usage.md, api.md.

---

## Pre-Execution Decisions

**Doc Types Per Module**:
- architecture.md - How the module works
- usage.md - How to use the module
- api.md - Public API reference (auto-generated from code)
- README.md - Module overview (already created in EXEC-HYBRID-001)

**Generation Strategy**: Template-based with code introspection  
**Success**: Each module has architecture.md + usage.md

**NOT Deciding**:
- Comprehensive API docs
- Tutorial writing
- Diagram generation
- Video documentation

---

## Template Phase

**architecture.md Template**:

```markdown
# {module_name} Architecture

**Module**: {module_name}  
**Phase**: {phase_number}  
**Layer**: {layer}

## Overview

{overview}

## Components

{component_list}

## Data Flow

{data_flow_description}

## Dependencies

{dependency_list}

## Design Decisions

{design_decisions}
```

**usage.md Template**:

```markdown
# {module_name} Usage Guide

**Module**: {module_name}

## Quick Start

{quick_start_code}

## Common Use Cases

### Use Case 1: {use_case_1_title}

{use_case_1_description}

```python
{use_case_1_code}
```

## Configuration

{configuration_options}

## Troubleshooting

{common_issues}
```

**api.md Template** (auto-generated):

```markdown
# {module_name} API Reference

**Auto-generated from source code**

## Public Functions

{function_list_with_signatures}

## Public Classes

{class_list_with_methods}

## Constants

{constant_list}
```

---

## Batch Execution

### Batch 1: Generate Module Architecture Docs

```powershell
$script = @'
$modules = @(
    @{Path="phase0_bootstrap/modules/bootstrap_orchestrator"; Name="bootstrap_orchestrator"; Phase=0; Overview="Detects repository type, selects appropriate profile, validates baseline configuration"},
    @{Path="phase1_planning/modules/spec_parser"; Name="spec_parser"; Phase=1; Overview="Parses OpenSpec files into structured format"},
    @{Path="phase1_planning/modules/workstream_planner"; Name="workstream_planner"; Phase=1; Overview="Converts specifications into executable workstreams"},
    @{Path="phase4_routing/modules/aim_tools"; Name="aim_tools"; Phase=4; Overview="Matches tasks to AI tools based on capabilities"},
    @{Path="phase6_error_recovery/modules/error_engine"; Name="error_engine"; Phase=6; Overview="Detects, classifies, and orchestrates error recovery"}
)

foreach ($module in $modules) {
    $doc = @"
# $($module.Name) Architecture

**Module**: $($module.Name)  
**Phase**: $($module.Phase)  

## Overview

$($module.Overview)

## Components

See ``src/`` directory for implementation.

## Data Flow

1. Input processing
2. Core logic execution
3. Output generation

## Dependencies

See module imports in source code.

## Design Decisions

See ADR (Architecture Decision Records) if available.
"@
    
    $docsPath = "$($module.Path)/docs"
    New-Item -ItemType Directory -Path $docsPath -Force | Out-Null
    $doc | Out-File "$docsPath/architecture.md" -Encoding UTF8
    Write-Host "✅ Created architecture.md for $($module.Name)"
}
'@

$script | Out-File "scripts/generate_module_architecture_docs.ps1" -Encoding UTF8
& "scripts/generate_module_architecture_docs.ps1"
```

### Batch 2: Generate Module Usage Docs

```powershell
$script = @'
$modules = Get-ChildItem "phase*/modules/*" -Directory -Recurse -Depth 1

foreach ($module in $modules) {
    $moduleName = $module.Name
    $srcPath = Join-Path $module.FullName "src"
    
    # Check if module has Python code
    $hasPython = (Get-ChildItem $srcPath -Filter "*.py" -Recurse -ErrorAction SilentlyContinue).Count -gt 0
    
    if ($hasPython) {
        $doc = @"
# $moduleName Usage Guide

**Module**: $moduleName

## Quick Start

``````python
# Import the module
from $moduleName import *

# Basic usage example
# TODO: Add specific usage example
``````

## Common Use Cases

### Use Case 1: Basic Operation

Describe the most common use case for this module.

``````python
# Example code
``````

## Configuration

See ``config/`` directory for configuration options.

## Troubleshooting

### Common Issues

1. **Issue**: Import errors
   **Solution**: Ensure module is in Python path

## API Reference

See ``api.md`` for full API documentation.
"@
        
        $docsPath = Join-Path $module.FullName "docs"
        New-Item -ItemType Directory -Path $docsPath -Force | Out-Null
        $doc | Out-File "$docsPath/usage.md" -Encoding UTF8
        Write-Host "✅ Created usage.md for $moduleName"
    }
}
'@

$script | Out-File "scripts/generate_module_usage_docs.ps1" -Encoding UTF8
& "scripts/generate_module_usage_docs.ps1"
```

### Batch 3: Auto-Generate API Docs

```powershell
# Use Python introspection to generate API docs
$script = @'
import os
import importlib
import inspect
from pathlib import Path

def generate_api_docs(module_path):
    """Generate API documentation from Python source code."""
    module_name = os.path.basename(module_path)
    src_path = os.path.join(module_path, "src")
    
    if not os.path.exists(src_path):
        return
    
    # Find all Python files
    py_files = list(Path(src_path).rglob("*.py"))
    
    doc = f"# {module_name} API Reference\n\n"
    doc += "**Auto-generated from source code**\n\n"
    
    for py_file in py_files:
        if "__init__.py" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        doc += f"## {py_file.stem}\n\n"
        
        # Read file content
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract functions and classes (simple regex approach)
        import re
        
        # Find functions
        functions = re.findall(r'^def (\w+)\((.*?)\):', content, re.MULTILINE)
        if functions:
            doc += "### Functions\n\n"
            for func_name, params in functions:
                if not func_name.startswith('_'):  # Only public functions
                    doc += f"- `{func_name}({params})`\n"
            doc += "\n"
        
        # Find classes
        classes = re.findall(r'^class (\w+).*?:', content, re.MULTILINE)
        if classes:
            doc += "### Classes\n\n"
            for class_name in classes:
                if not class_name.startswith('_'):  # Only public classes
                    doc += f"- `{class_name}`\n"
            doc += "\n"
    
    # Write API doc
    docs_path = os.path.join(module_path, "docs")
    os.makedirs(docs_path, exist_ok=True)
    
    with open(os.path.join(docs_path, "api.md"), 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"✅ Generated api.md for {module_name}")

# Find all modules
for root, dirs, files in os.walk("./"):
    if "modules" in dirs:
        modules_path = os.path.join(root, "modules")
        for module_dir in os.listdir(modules_path):
            module_path = os.path.join(modules_path, module_dir)
            if os.path.isdir(module_path):
                generate_api_docs(module_path)
'@

$script | Out-File "scripts/generate_api_docs.py" -Encoding UTF8
python scripts/generate_api_docs.py
```

---

## Validation Gates

### Gate 1: All Modules Have Docs

```powershell
$modules = Get-ChildItem "phase*/modules/*" -Directory -Recurse -Depth 1

foreach ($module in $modules) {
    $docsPath = Join-Path $module.FullName "docs"
    $hasArchitecture = Test-Path "$docsPath/architecture.md"
    $hasUsage = Test-Path "$docsPath/usage.md"
    
    if (-not $hasArchitecture -or -not $hasUsage) {
        Write-Host "❌ Missing docs: $($module.Name)" -ForegroundColor Red
    } else {
        Write-Host "✅ $($module.Name)" -ForegroundColor Green
    }
}
```

### Gate 2: Docs Are Not Empty

```powershell
$allDocs = Get-ChildItem "phase*/modules/*/docs/*.md" -Recurse

foreach ($doc in $allDocs) {
    $content = Get-Content $doc -Raw
    if ($content.Length -lt 100) {  # Suspiciously short
        Write-Host "⚠️ Short doc: $($doc.FullName)" -ForegroundColor Yellow
    }
}
```

### Gate 3: Architectural Docs at Root

```powershell
# Keep high-level architecture docs at root
$rootDocs = @(
    "docs/architecture/",
    "docs/reference/",
    "docs/adr/"
)

foreach ($dir in $rootDocs) {
    if (Test-Path $dir) {
        Write-Host "✅ $dir preserved" -ForegroundColor Green
    }
}
```

---

## Success Metrics

**Completion Criteria**:
- ✅ All 31 modules have docs/architecture.md
- ✅ All 31 modules have docs/usage.md
- ✅ API docs auto-generated for modules with code
- ✅ Root docs/ preserved for architectural content

**Time Savings**:
- Manual: 4.5 hours (31 modules × 9 min each)
- Pattern: 45 minutes (template generation + validation)
- Speedup: 6x faster

**Documentation Coverage**:
- 31 × 3 = 93 module docs generated
- Root architectural docs preserved
- Total: ~100+ documentation files organized

---

## Ground Truth Commands

```powershell
# Count module docs
$architectureDocs = (Get-ChildItem "phase*/modules/*/docs/architecture.md" -Recurse).Count
$usageDocs = (Get-ChildItem "phase*/modules/*/docs/usage.md" -Recurse).Count
$apiDocs = (Get-ChildItem "phase*/modules/*/docs/api.md" -Recurse).Count

Write-Host "Architecture docs: $architectureDocs (Expected: 31)"
Write-Host "Usage docs: $usageDocs (Expected: 31)"
Write-Host "API docs: $apiDocs"

# All modules documented
$modules = (Get-ChildItem "phase*/modules/*" -Directory -Recurse -Depth 1).Count
Write-Host "Modules: $modules (Expected: 31)"
```
