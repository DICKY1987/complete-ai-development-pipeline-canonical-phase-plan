# Simple Pipeline Example

> **Minimal Working Example of UET Framework**  
> **Purpose**: Learn the basics - one phase, one workstream, one task  
> **Time**: 10-15 minutes

---

## 📋 What This Example Demonstrates

- Basic project structure
- How to define a phase
- How to create a workstream
- How to specify a task
- How to run a simple pipeline

---

## 📂 Files in This Example

```
simple-pipeline/
├── README.md                    # This file
├── profile.yaml                 # Project profile
├── phase-01.yaml                # Single phase definition
├── workstream-001.json          # Single workstream
├── task-001.yaml                # Single task
└── run.sh                       # Run script
```

---

## 🚀 Quick Start

### Run the Example

```bash
# Navigate to this directory
cd examples/simple-pipeline/

# Make run script executable
chmod +x run.sh

# Run the example
./run.sh
```

### Expected Output

```
[INFO] Loading profile: profile.yaml
[INFO] Validating configuration...
[INFO] Executing phase: PH-SIMPLE-01
[INFO] Starting workstream: ws-001
[INFO] Running task: task-001 (analysis)
[INFO] Task completed successfully
[INFO] Workstream completed: ws-001
[INFO] Phase completed: PH-SIMPLE-01 (100%)
[SUCCESS] Pipeline completed successfully
```

---

## 📖 What's Happening

### 1. Profile Configuration (`profile.yaml`)

Defines basic project settings:
- Project type: Python
- Tools available: aider (for analysis)
- Constraints: timeouts, resource limits

### 2. Phase Definition (`phase-01.yaml`)

Defines a single phase:
- Phase ID: `PH-SIMPLE-01`
- Contains one workstream: `ws-001`
- Timeout: 10 minutes

### 3. Workstream Bundle (`workstream-001.json`)

Defines a single workstream:
- Workstream ID: `ws-001`
- Contains one task: `task-001`
- Execution mode: sequential

### 4. Task Specification (`task-001.yaml`)

Defines a single task:
- Task ID: `task-001`
- Type: analysis
- Tool: aider
- Action: Analyze project structure

---

## 🎓 Learning Points

### Understanding the Hierarchy

```
Profile (project config)
  └─ Phase (major stage)
      └─ Workstream (execution bundle)
          └─ Task (atomic work unit)
```

### Configuration Flow

1. **Profile** tells framework what tools are available
2. **Phase** defines what needs to be done
3. **Workstream** groups related tasks
4. **Task** specifies the actual work

### Execution Flow

1. Framework loads `profile.yaml`
2. Framework validates configuration
3. Framework executes `phase-01.yaml`
4. Framework runs `workstream-001.json`
5. Framework executes `task-001.yaml` using aider
6. Framework reports results

---

## 🔧 Customizing the Example

### Change the Task

Edit `task-001.yaml`:

```yaml
# Change instructions
instructions: "Analyze code quality and suggest improvements"

# Change files to analyze
input:
  files: ["src/**/*.py", "tests/**/*.py"]
```

### Add Another Task

1. Create `task-002.yaml` (copy and modify `task-001.yaml`)
2. Add to `workstream-001.json`:

```json
{
  "tasks": [
    {"task_id": "task-001", ...},
    {"task_id": "task-002", "task_ref": "file://task-002.yaml", ...}
  ]
}
```

### Change the Timeout

Edit `phase-01.yaml`:

```yaml
execution:
  timeout: 1200  # 20 minutes instead of 10
```

---

## ✅ Validation

### Validate Files

```bash
# Validate profile
python ../../core/bootstrap/validator.py \
  --schema ../../schema/project_profile.v1.json \
  --file profile.yaml

# Validate phase
python ../../core/bootstrap/validator.py \
  --schema ../../schema/phase_spec.v1.json \
  --file phase-01.yaml

# Validate workstream
python ../../core/bootstrap/validator.py \
  --schema ../../schema/workstream_spec.v1.json \
  --file workstream-001.json

# Validate task
python ../../core/bootstrap/validator.py \
  --schema ../../schema/task_spec.v1.json \
  --file task-001.yaml
```

---

## 🐛 Troubleshooting

### "Tool not found" Error

```bash
# Install aider
pip install aider-chat

# Or update profile.yaml to use a different tool
```

### "Schema validation failed"

```bash
# Check file syntax
python -c "import yaml; yaml.safe_load(open('profile.yaml'))"

# Check against schema
python ../../core/bootstrap/validator.py --schema ... --file ...
```

### "Timeout" Error

```bash
# Increase timeout in phase-01.yaml
# Or in task-001.yaml
```

---

## 📚 Next Steps

After completing this example:

1. **Review the Files**: Open each file and read the comments
2. **Modify and Re-run**: Change values and see what happens
3. **Try Multi-Phase Example**: Move to `../multi-phase/`
4. **Create Your Own**: Use these files as templates

---

## 📖 Related Documentation

- **[Templates Overview](../../README.md)** - All available templates
- **[Orchestration Templates](../../orchestration/README.md)** - Phase/workstream details
- **[Configuration Templates](../../configuration/README.md)** - Profile setup
- **[UET Specifications](../../../specs/)** - Detailed specs

---

**Estimated Time**: 10-15 minutes  
**Difficulty**: Beginner  
**Prerequisites**: Python 3.8+, aider-chat installed
