---
doc_id: DOC-SPEC-README-038
---

# Schema Definitions

> **Purpose**: JSON/YAML/SQL schemas defining workstream and sidecar metadata contracts  
> **Last Updated**: 2025-11-22  
> **Status**: Production

---

## Overview

The `schema/` directory contains all schema definitions that serve as the source of truth for data contracts in the system.

## Directory Structure

```
schema/
├── workstream/         # Workstream schemas
├── jobs/              # Job schemas (for engine/)
├── openspec/          # OpenSpec schemas
└── sql/               # SQL schemas (if present)
```

## Schema Types

### Workstream Schemas

Define the structure of workstream bundles and metadata.

**Key Schemas**:
- Workstream bundle format
- Step definitions
- Metadata contracts
- Validation rules

**Used by**:
- `core/state/bundles.py` - Bundle loading
- `scripts/validate_workstreams.py` - Validation
- Workstream authoring tools

### Job Schemas

Define the structure of job definitions for the engine.

**Key Schemas**:
- Job specification format
- Adapter configurations
- Queue metadata

**Used by**:
- `engine/orchestrator.py` - Job execution
- `engine/queue_manager.py` - Queue management
- Job authoring tools

**Example**: `schema/jobs/aider_job.example.json`

### OpenSpec Schemas

Define OpenSpec change proposal format and metadata.

**Used by**:
- `specifications/bridge/` - OpenSpec conversion
- OpenSpec CLI tools

### Registry Schemas

Define registry records that bind artifact ids to module metadata and paths.

**Key Schema**:
- `registry_entry.schema.json` - Adds `module_id` and `module_kind` fields to
  keep the registry aligned with the module-centric refactor.

## Schema Validation

### Validate Against Schema

```python
import json
from jsonschema import validate

# Load schema
with open('schema/workstream/bundle.schema.json') as f:
    schema = json.load(f)

# Load data
with open('workstreams/example.json') as f:
    data = json.load(f)

# Validate
validate(instance=data, schema=schema)
```

### Using Validation Scripts

```bash
# Validate workstreams
python ./scripts/validate_workstreams.py

# Validate specific file
python ./scripts/validate_workstreams.py --file workstreams/example.json
```

## Schema Versioning

Schemas should be versioned to maintain compatibility:

1. **Breaking changes**: Increment major version
2. **New optional fields**: Increment minor version
3. **Documentation only**: Increment patch version

**Version format**: `v{major}.{minor}.{patch}`

**Example**: `workstream.v1.2.0.schema.json`

## Schema Development

### Adding a New Schema

1. **Create schema file**:
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "title": "My Schema",
     "type": "object",
     "properties": {
       "name": {"type": "string"},
       "version": {"type": "string"}
     },
     "required": ["name"]
   }
   ```

2. **Add validation**:
   - Add to validation scripts
   - Create unit tests

3. **Document it**:
   - Add to this README
   - Include examples
   - Document all fields

4. **Update generators**:
   - Update spec index generator
   - Update mapping generator

### Schema Best Practices

- **Use clear property names**: Descriptive, kebab-case for consistency
- **Include descriptions**: Every property should have a description
- **Set appropriate constraints**: Required fields, types, patterns
- **Provide examples**: Include example files
- **Version carefully**: Breaking changes require migration paths
- **Test thoroughly**: Validate against real data

## Related Documentation

- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository navigation
- [workstreams/](../workstreams/) - Example workstream bundles
- [specifications/](../specifications/) - Spec management
- [engine/README.md](../engine/README.md) - Job schema usage

## Schema Index

### Workstream Schemas
- **Bundle schema**: Defines workstream bundle structure
- **Step schema**: Defines individual step structure
- **Metadata schema**: Defines metadata format

### Job Schemas
- **Job specification**: Defines job format for engine
- **Adapter config**: Defines adapter configuration
- **Queue metadata**: Defines queue entry format

### OpenSpec Schemas
- **Change proposal**: Defines OpenSpec change format
- **Conversion mapping**: Defines spec-to-workstream mapping

## Regenerating Indices

After schema changes, regenerate indices:

```bash
python ./scripts/generate_spec_index.py
python ./scripts/generate_spec_mapping.py
```

## Testing Schemas

Test schemas with real data:

```bash
# Run schema validation tests
pytest tests/pipeline/test_schemas.py -v

# Validate all workstreams
python ./scripts/validate_workstreams.py
```

---

**For AI Tools**: HIGH priority directory - schemas define the contracts for the entire system.
