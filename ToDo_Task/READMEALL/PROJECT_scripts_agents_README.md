# Custom Agents Directory

> **Purpose**: House custom automation agents that enhance development workflows  
> **Status**: Initial setup - First agent template created  
> **Documentation**: [docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](../../docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)

---

## Overview

This directory contains custom automation agents designed to reduce manual overhead and improve development efficiency in the AI Development Pipeline.

**Philosophy**: Each agent should be:
- ✅ **Focused**: Solves one specific problem well
- ✅ **Safe**: Validates outputs and handles errors gracefully
- ✅ **Integrated**: Works with existing infrastructure
- ✅ **Documented**: Clear purpose, usage, and examples

---

## Available Agents

### 1. Workstream Generator (Template)

**File**: `workstream_generator.py`  
**Status**: 🔧 Template created - Ready for implementation  
**Priority**: HIGH

**Purpose**: Automatically generate workstream JSON files from natural language descriptions.

**Why it's needed:**
- 38+ workstream files exist, indicating heavy usage
- Manual JSON authoring is error-prone and time-consuming
- Reduces task creation time from 20-30 minutes to ~5 minutes

**Usage:**
```bash
# Interactive mode (recommended)
python scripts/agents/workstream_generator.py --interactive

# Command line mode
python scripts/agents/workstream_generator.py \
  --description "Add retry logic to executor with exponential backoff" \
  --phase PH-007 \
  --files "core/engine/executor.py,tests/engine/test_executor.py" \
  --output workstreams/ws-007-042.json
```

**Implementation checklist:**
- [x] Template created with API structure
- [ ] Implement ID generation logic
- [ ] Add NLP/pattern matching for description parsing
- [ ] Implement intelligent file scope suggestion
- [ ] Add schema validation
- [ ] Create unit tests
- [ ] Update documentation

---

## Planned Agents (Not Yet Implemented)

### 2. Code Migration Agent (HIGH PRIORITY)

**Purpose**: Automated refactoring and import path updates

**Planned features:**
- Detect deprecated import patterns
- Automatically rewrite imports using AST manipulation
- Verify changes don't break functionality
- Generate migration reports

**When to implement**: After workstream generator is complete

---

### 3. Test Generator Agent (MEDIUM PRIORITY)

**Purpose**: Automatically generate test scaffolding

**Planned features:**
- Analyze Python module structure
- Generate test file with fixtures
- Create test stubs for public functions
- Follow existing test patterns

**When to implement**: Phase 2 (Week 3-4)

---

### 4. Documentation Sync Agent (MEDIUM PRIORITY)

**Purpose**: Keep documentation in sync with code changes

**Planned features:**
- Detect when code changes affect docs
- Update relevant markdown files
- Regenerate index files
- Validate cross-references

**When to implement**: Phase 2 (Week 3-4)

---

### 5. Specification Validator Agent (MEDIUM PRIORITY)

**Purpose**: Comprehensive validation of specs and workstreams

**Planned features:**
- Run all validation scripts in order
- Aggregate results into single report
- Check spec-to-code alignment
- Suggest fixes for common issues

**When to implement**: Phase 3 (Week 5-6)

---

### 6. Plugin Scaffold Agent (LOW PRIORITY)

**Purpose**: Generate boilerplate for error detection plugins

**Planned features:**
- Generate plugin directory structure
- Create manifest.json
- Scaffold plugin.py with parse() and fix()
- Add test file template

**When to implement**: Phase 3 (Week 5-6)

---

### 7. Dependency Update Agent (LOW PRIORITY)

**Purpose**: Monitor and update dependencies safely

**Planned features:**
- Check for outdated dependencies
- Analyze breaking changes
- Test updates in isolation
- Create PR with updates

**When to implement**: Phase 4 (Ongoing maintenance)

---

## Development Guidelines

### Creating a New Agent

1. **Design the agent**:
   - Define clear purpose and scope
   - Identify inputs and outputs
   - Design validation strategy
   - Plan integration points

2. **Create the template**:
   ```python
   class CustomAgent:
       def __init__(self, config):
           """Initialize with configuration"""
           pass
       
       def analyze(self, input_data):
           """Analyze input and determine actions"""
           pass
       
       def execute(self, actions):
           """Execute determined actions"""
           pass
       
       def validate(self, results):
           """Validate results meet criteria"""
           pass
       
       def report(self, results):
           """Generate human-readable report"""
           pass
   ```

3. **Implement the logic**:
   - Follow repository conventions (see [AGENTS.md](../../AGENTS.md))
   - Use existing utilities where possible
   - Handle errors gracefully
   - Add logging for debugging

4. **Add tests**:
   - Create `tests/agents/test_<agent_name>.py`
   - Test happy paths
   - Test error conditions
   - Test edge cases

5. **Document**:
   - Update this README
   - Add usage examples
   - Document configuration options
   - Add to [AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](../../docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)

6. **Integrate**:
   - Add to [QUALITY_GATE.yaml](../../QUALITY_GATE.yaml) if validation agent
   - Update [ai_policies.yaml](../../ai_policies.yaml) if affects edit zones
   - Add to [scripts/README.md](../README.md)

---

## Testing Agents

```bash
# Test individual agent
python -m pytest tests/agents/test_workstream_generator.py -v

# Test all agents
python -m pytest tests/agents/ -v

# Run agent in dry-run mode (if supported)
python scripts/agents/workstream_generator.py --dry-run --description "test task"
```

---

## Agent Standards

### Input Validation
- ✅ Validate all inputs before processing
- ✅ Provide clear error messages
- ✅ Support dry-run mode where applicable

### Output Quality
- ✅ Validate outputs against schemas
- ✅ Generate reports for user review
- ✅ Provide undo/rollback capability where applicable

### Integration
- ✅ Use existing repository utilities
- ✅ Follow import path standards
- ✅ Respect edit zones from ai_policies.yaml

### Documentation
- ✅ Inline docstrings for all public methods
- ✅ Usage examples in module docstring
- ✅ Command-line help text
- ✅ README entry with purpose and usage

---

## Metrics and Success Criteria

Track these metrics for each agent:

- **Usage frequency**: How often is the agent used?
- **Time saved**: Reduction in manual effort
- **Error rate**: Percentage of valid outputs
- **User satisfaction**: Feedback from developers

**Target metrics:**
- ✅ 90%+ valid outputs without manual editing
- ✅ 50%+ time reduction vs. manual approach
- ✅ Positive user feedback
- ✅ Regular usage (weekly or more)

---

## Contributing

### Adding a New Agent

1. Review [AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](../../docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)
2. Create feature branch: `git checkout -b feature/agent-<name>`
3. Implement agent following standards above
4. Add tests and documentation
5. Submit PR with:
   - Agent implementation
   - Tests
   - Documentation updates
   - Usage examples

### Improving Existing Agents

1. Create issue describing improvement
2. Create feature branch
3. Implement improvements
4. Update tests and documentation
5. Submit PR

---

## Resources

### Documentation
- [AGENT_ANALYSIS_AND_RECOMMENDATIONS.md](../../docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md) - Full analysis
- [AGENT_QUICK_REFERENCE.md](../../docs/AGENT_QUICK_REFERENCE.md) - Quick reference guide
- [AGENTS.md](../../AGENTS.md) - Repository conventions
- [CLAUDE.md](../../CLAUDE.md) - Claude Code instructions

### Related Infrastructure
- [error/plugins/](../../error/plugins/) - Error detection plugins (similar pattern)
- [engine/adapters/](../../engine/adapters/) - Job engine adapters (integration pattern)
- [scripts/](../) - Automation scripts

### Schemas
- [schema/workstream-bundle.schema.json](../../schema/workstream-bundle.schema.json)
- [schema/jobs/](../../schema/jobs/) - Job schemas

---

## Status Summary

| Agent | Status | Priority | ETA |
|-------|--------|----------|-----|
| Workstream Generator | 🔧 Template | HIGH | Week 1-2 |
| Code Migration | 📋 Planned | HIGH | Week 1-2 |
| Test Generator | 📋 Planned | MEDIUM | Week 3-4 |
| Doc Sync | 📋 Planned | MEDIUM | Week 3-4 |
| Spec Validator | 📋 Planned | MEDIUM | Week 5-6 |
| Plugin Scaffold | 📋 Planned | LOW | Week 5-6 |
| Dependency Updater | 📋 Planned | LOW | Ongoing |

**Legend**: ✅ Complete | 🔧 In Progress | 📋 Planned

---

**Last Updated**: 2025-11-23  
**Next Review**: After first agent implementation complete  
**Feedback**: Open issue or update this README
