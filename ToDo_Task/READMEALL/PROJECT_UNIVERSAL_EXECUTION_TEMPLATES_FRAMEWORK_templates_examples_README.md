---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1605
---

# Examples - Complete Template Implementations

> **Working Examples Demonstrating UET Framework Patterns**  
> **Purpose**: Learn by example - complete, runnable implementations  
> **Use**: Reference, learning, quick-start new projects

---

## 📋 Overview

This directory contains complete working examples that demonstrate how to use UET Framework templates. Each example is a fully functional implementation you can run, study, and use as a starting point for your own projects.

### What's in This Directory

```
examples/
├── README.md                    # This file
│
├── simple-pipeline/             # Minimal working example
├── multi-phase/                 # Multi-phase workflow
└── advanced/                    # Advanced patterns
```

---

## 🎓 Learning Path

### Start Here: Simple Pipeline

**Best For**: Understanding UET basics

**What You'll Learn**:
- Basic project structure
- How to define a phase
- How to create workstreams
- How to run a simple pipeline

**Time**: 10-15 minutes

---

### Next: Multi-Phase Workflow

**Best For**: Realistic workflows

**What You'll Learn**:
- Multi-phase execution
- Phase dependencies
- Parallel workstreams
- Tool integration

**Time**: 30-45 minutes

---

### Advanced: Complex Patterns

**Best For**: Production usage

**What You'll Learn**:
- Error recovery patterns
- Custom adapters
- Complex DAGs
- Monitoring and reporting

**Time**: 1-2 hours

---

## 📚 Example Catalog

### 1. Simple Pipeline

**Location**: `simple-pipeline/`

**Description**: Minimal working example with one phase, one workstream, and one task.

**Structure**:
```
simple-pipeline/
├── README.md                    # Example guide
├── profile.yaml                 # Project profile
├── phase-01.yaml                # Single phase definition
├── workstream-001.json          # Single workstream
└── run.sh                       # Run script
```

**What It Does**:
1. Loads project profile
2. Executes phase with single workstream
3. Runs one analysis task
4. Generates simple report

**Run It**:
```bash
cd examples/simple-pipeline/
./run.sh
```

**Expected Output**:
```
[INFO] Loading profile: profile.yaml
[INFO] Executing phase: PH-SIMPLE-01
[INFO] Starting workstream: ws-001
[INFO] Running task: task-001 (analysis)
[INFO] Task completed successfully
[INFO] Phase completed: 100%
```

---

### 2. Multi-Phase Workflow

**Location**: `multi-phase/`

**Description**: Complete workflow with analysis, implementation, and validation phases.

**Structure**:
```
multi-phase/
├── README.md                    # Example guide
├── profile.yaml                 # Python project profile
├── phase-01-analysis.yaml       # Discovery phase
├── phase-02-implementation.yaml # Development phase
├── phase-03-validation.yaml     # Testing phase
├── workstreams/                 # Workstream definitions
│   ├── ws-discovery.json
│   ├── ws-code-gen.json
│   ├── ws-refactor.json
│   └── ws-testing.json
└── run.sh                       # Run script
```

**What It Does**:
1. **Phase 1 - Analysis**: Discover requirements and plan implementation
2. **Phase 2 - Implementation**: Generate code in parallel workstreams
3. **Phase 3 - Validation**: Run tests and quality checks

**Run It**:
```bash
cd examples/multi-phase/
./run.sh
```

**Expected Output**:
```
[INFO] Phase 1/3: Analysis
[INFO] - Discovering requirements...
[INFO] - Planning implementation...
[INFO] Phase 1 complete (100%)

[INFO] Phase 2/3: Implementation
[INFO] - Workstream: ws-code-gen (parallel)
[INFO] - Workstream: ws-refactor (parallel)
[INFO] Phase 2 complete (100%)

[INFO] Phase 3/3: Validation
[INFO] - Running tests...
[INFO] - Checking quality gates...
[INFO] Phase 3 complete (100%)

[SUCCESS] All phases completed
```

---

### 3. Advanced Patterns

**Location**: `advanced/`

**Description**: Production-ready patterns including error recovery, custom adapters, and monitoring.

**Structure**:
```
advanced/
├── README.md                    # Example guide
├── profile.yaml                 # Advanced profile with constraints
│
├── parallel-execution/          # Parallel execution patterns
│   ├── dag-complex.yaml
│   └── workstream-parallel.json
│
├── error-recovery/              # Error handling patterns
│   ├── retry-policy.yaml
│   ├── circuit-breaker.yaml
│   └── fallback-config.json
│
├── custom-adapters/             # Custom tool integrations
│   ├── security_scanner.py
│   └── performance_profiler.py
│
├── monitoring/                  # Monitoring and reporting
│   ├── dashboard.html
│   ├── report-template.md
│   └── metrics-config.json
│
└── run.sh                       # Run script
```

**What It Demonstrates**:
- Complex DAG with parallel and sequential sections
- Circuit breaker and retry logic
- Custom adapter implementation
- Real-time monitoring dashboard
- Comprehensive reporting

**Run It**:
```bash
cd examples/advanced/
./run.sh

# View monitoring dashboard
python -m http.server 8000
# Visit http://localhost:8000/monitoring/dashboard.html
```

---

## 🚀 Using Examples

### As Learning Material

```bash
# 1. Read the README
cat examples/simple-pipeline/README.md

# 2. Examine the files
ls -la examples/simple-pipeline/

# 3. Run the example
cd examples/simple-pipeline/
./run.sh

# 4. Modify and experiment
# Change phase-01.yaml, re-run, observe differences
```

### As Starting Points

```bash
# 1. Copy example to your project
cp -r examples/multi-phase/ my-project/

# 2. Customize for your needs
cd my-project/
# Edit profile.yaml
# Modify phases
# Add/remove workstreams

# 3. Run your customized version
./run.sh
```

### For Testing

```bash
# Use examples to test framework changes
pytest tests/examples/test_simple_pipeline.py
pytest tests/examples/test_multi_phase.py
pytest tests/examples/test_advanced.py
```

---

## 🎯 Example Comparison

| Feature | Simple | Multi-Phase | Advanced |
|---------|--------|-------------|----------|
| **Phases** | 1 | 3 | 5+ |
| **Workstreams** | 1 | 4 | 10+ |
| **Tasks** | 1 | 8 | 20+ |
| **Parallel Execution** | No | Yes | Yes |
| **Error Recovery** | No | No | Yes |
| **Custom Adapters** | No | No | Yes |
| **Monitoring** | No | Basic | Advanced |
| **Complexity** | Minimal | Moderate | High |
| **Run Time** | < 1 min | 5-10 min | 15-30 min |
| **Best For** | Learning | Real projects | Production |

---

## 📝 Customization Guide

### Modifying Simple Pipeline

```yaml
# 1. Change the task
# File: workstream-001.json
{
  "tasks": [
    {
      "task_id": "my-custom-task",  # Change this
      "tool": "aider",               # Change tool
      "instructions": "New task"     # Change instructions
    }
  ]
}

# 2. Add a new task
{
  "tasks": [
    # ... existing task ...
    {
      "task_id": "task-002",
      "tool": "pytest",
      "instructions": "Run tests"
    }
  ]
}
```

### Extending Multi-Phase

```bash
# 1. Add a new phase
cp phase-03-validation.yaml phase-04-deployment.yaml

# 2. Edit phase-04-deployment.yaml
# Change phase_id: "PH-DEPLOY-01"
# Update description and workstreams

# 3. Update run script to include new phase
```

### Adapting Advanced Example

```python
# 1. Create custom adapter
# File: custom-adapters/my_tool.py

from core.adapters.base import ToolAdapter

class MyToolAdapter(ToolAdapter):
    def detect_capabilities(self):
        return {
            "capabilities": ["my_capability"],
            "version": "1.0.0",
            "available": True
        }
    
    def execute(self, request):
        # Your implementation
        pass

# 2. Register in router config
# 3. Use in tasks
```

---

## ✅ Testing Examples

### Unit Tests

```python
# tests/examples/test_simple_pipeline.py
import pytest
from core.bootstrap.orchestrator import BootstrapOrchestrator

def test_simple_pipeline_loads():
    """Simple pipeline should load successfully"""
    bootstrap = BootstrapOrchestrator("examples/simple-pipeline")
    profile = bootstrap.load_profile()
    assert profile is not None

def test_simple_pipeline_runs():
    """Simple pipeline should execute successfully"""
    # Run and verify success
    pass
```

### Integration Tests

```bash
# Run all example tests
pytest tests/examples/ -v

# Run specific example
pytest tests/examples/test_multi_phase.py -v
```

---

## 🔍 Troubleshooting

### Common Issues

**Example won't run**:
```bash
# Check dependencies
pip install -r requirements.txt

# Validate files
python scripts/validate_example.py examples/simple-pipeline/
```

**Phase fails**:
```bash
# Check logs
cat .state/runs/run-latest.log

# Validate phase definition
python core/bootstrap/validator.py \
  --schema schema/phase_spec.v1.json \
  --file phase-01.yaml
```

**Tool not found**:
```bash
# Check tool availability
python scripts/check_tool_availability.py \
  --profile profile.yaml

# Install missing tools
pip install aider-chat pytest ruff
```

---

## 📚 Related Documentation

- **[Templates Main README](../README.md)** - Template overview
- **[Orchestration Templates](../orchestration/README.md)** - Phase/workstream details
- **[Adapter Templates](../adapters/README.md)** - Tool integration
- **[Configuration Templates](../configuration/README.md)** - Profile setup
- **[UET Specifications](../../specs/)** - Detailed specs

---

## 🤝 Contributing Examples

### Adding a New Example

1. **Create directory**: `examples/my-example/`
2. **Add README.md**: Explain what it demonstrates
3. **Include all files**: Profile, phases, workstreams, run script
4. **Add tests**: Create test file in `tests/examples/`
5. **Update this README**: Add to example catalog
6. **Submit PR**: Include description and screenshots

### Example Checklist

```markdown
- [ ] README.md with clear explanation
- [ ] profile.yaml (validated)
- [ ] All phase files (validated)
- [ ] All workstream files (validated)
- [ ] run.sh script that works
- [ ] requirements.txt if needed
- [ ] Test file in tests/examples/
- [ ] Screenshots/output examples
- [ ] Entry in examples/README.md
```

---

## 📞 Support

**Q: Which example should I start with?**  
A: Start with `simple-pipeline/` to understand basics, then move to `multi-phase/`.

**Q: Can I use examples in production?**  
A: Examples are starting points. Review and customize for production use.

**Q: How do I debug a failing example?**  
A: Check logs in `.state/runs/`, validate files, verify tool availability.

**Q: Can I contribute my own examples?**  
A: Yes! See [Contributing Examples](#-contributing-examples).

---

**Last Updated**: 2025-11-23  
**Related**: [Orchestration](../orchestration/README.md), [Configuration](../configuration/README.md)
