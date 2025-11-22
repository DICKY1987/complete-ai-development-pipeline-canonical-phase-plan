# Prompt Engineering Templates and References

**Purpose**: Reusable prompt templates, prompt engineering guides, and AI agent operation specifications for consistent, high-quality AI interactions.

## Overview

The `Prompt/` directory contains carefully crafted prompt templates, prompt engineering best practices, and operational specifications for AI agents. These templates ensure consistent, professional-quality prompts across the pipeline.

## Structure

```
Prompt/
├── AGENT_OPERATIONS_SPEC version1.0.0     # Formal agent operations specification
├── Master Implementation Prompt Template (Reusable).txt  # Reusable master template
├── Plugin Architecture Analysis Prompt Template.md  # Plugin analysis prompt
├── Application Delivery Copilot TEMPLATE.txt  # Application delivery template
├── Application Delivery Copilot TEMPLATEv2.md  # Updated version
├── anthropic_prompt_engineering_guide.md  # Anthropic best practices
├── agentic_ai_prompting_crafting professional_reference.md  # Professional reference
├── PRR_ai_prompt_engineering_reference.md  # Prompt Rendering Reference
├── prr_project_instructions_architecture_aware_prompting_code_generation.md
├── A Guide to High-Quality Prompts for Superior AI (1).txt
├── Foundational Strategies_The Core of a Good Prompt.txt
├── The Core of a Good Prompt (1).txt
├── CHAT_GPT_PROJECT_KNOWL_PROMNT.md  # ChatGPT project knowledge prompt
└── PASTE_READY_Plugin & Modular ARCHITECTURE ANALYSIS PROMPT.txt
```

## Core Templates

### Agent Operations Specification

**File**: `AGENT_OPERATIONS_SPEC version1.0.0`

**Purpose**: Formal XML-based specification for AI agent operations, prompt rendering, and task routing.

**Structure**:
```xml
<AGENT_OPERATIONS_SPEC version="1.0.0">
    <THOUGHT_PROCESS>
        <MAPPING_PROMPT_RENDERING>
            <!-- Clarity, Context, Constraints triads -->
            <!-- Role and persona assignment -->
            <!-- XML-tagged thinking structures -->
        </MAPPING_PROMPT_RENDERING>
        
        <MAPPING_TASK_ROUTING>
            <!-- Central router orchestrator -->
            <!-- Capability registry -->
            <!-- Decision trees -->
        </MAPPING_TASK_ROUTING>
        
        <MAPPING_PATCH_MANAGEMENT>
            <!-- Unified diff artifacts -->
            <!-- Patch validation -->
        </MAPPING_PATCH_MANAGEMENT>
    </THOUGHT_PROCESS>
</AGENT_OPERATIONS_SPEC>
```

**Use Cases**:
- Defining agent behavior contracts
- Standardizing prompt rendering
- Routing tasks to appropriate agents
- Managing code patches and diffs

### Master Implementation Prompt Template

**File**: `Master Implementation Prompt Template (Reusable).txt`

**Purpose**: Comprehensive template for generating complete, production-ready implementations.

**Key Sections**:

#### System Identity & Mission
```xml
<system_identity>
  <name>PROJECT_NAME</name>
  <version>PROJECT_VERSION</version>
  <architecture>Modular Plugin Architecture with V-Model Verification</architecture>
  <output_requirement>COMPLETE, FUNCTIONAL, PRODUCTION-READY</output_requirement>
  <prefix_mandate>ALL files and folders MUST start with "PROJECT_PREFIX"</prefix_mandate>
</system_identity>
```

#### Role Assignment
```xml
<role_assignment priority="CRITICAL">
  <primary_role>Senior Software Architect & Systems Engineer</primary_role>
  <expertise_areas>
    <domain_knowledge years="YEARS_EXPERIENCE" depth="expert">
      - RUNTIME_TECH_STACK (e.g., PowerShell 7+, Node.js 20, Python 3.12)
      - Plugin/Microkernel system design
      - Contract-first API/interface development
      - V-Model verification & ISO/IEC 12207 mindset
      - TDD/BDD/ATDD methodologies
      - Hexagonal/Ports-and-Adapters architecture
    </domain_knowledge>
    <quality_standards>
      <professional_bar>Enterprise Production Standards</professional_bar>
      <accuracy_requirement threshold="100%">Zero placeholders, zero scaffolds</accuracy_requirement>
      <test_coverage minimum="100%">Every function must have unit tests</test_coverage>
    </quality_standards>
  </expertise_areas>
</role_assignment>
```

#### Behavioral Constraints
```xml
<behavioral_constraints>
  <mandatory>
    - Generate COMPLETE, executable code only
    - Create unit tests for EVERY function
    - Execute tests in the target runtime's virtual environment
    - Fix ALL runtime errors before proceeding
    - Loop 5 times minimum for quality assurance
    - Apply contract-first design patterns
    - Follow plugin template patterns strictly
  </mandatory>
</behavioral_constraints>
```

**Variables to Fill**:
- `PROJECT_NAME`: e.g., "ACME DataHub"
- `PROJECT_VERSION`: e.g., "1.0.0"
- `PROJECT_PREFIX`: e.g., "ACME_"
- `YEARS_EXPERIENCE`: e.g., "10"
- `RUNTIME_TECH_STACK`: e.g., "Python 3.12, FastAPI"

### Plugin Architecture Analysis Template

**File**: `Plugin Architecture Analysis Prompt Template.md`

**Purpose**: Structured prompt for analyzing plugin architectures and generating plugin implementations.

**Sections**:
- Plugin discovery mechanisms
- Manifest schema analysis
- Interface contract extraction
- Dependency resolution
- Example plugin generation

**Usage**:
```markdown
# Plugin Architecture Analysis

## Context
You are analyzing the plugin system in [PROJECT_NAME].

## Tasks
1. Analyze existing plugin manifests in `error/plugins/*/manifest.json`
2. Extract common patterns and contracts
3. Document plugin lifecycle (register → execute → cleanup)
4. Generate example plugin following discovered patterns

## Output Format
- Markdown document with analysis
- Example plugin code
- Updated plugin development guide
```

### Application Delivery Copilot Templates

**Files**: 
- `Application Delivery Copilot TEMPLATE.txt`
- `Application Delivery Copilot TEMPLATEv2.md`

**Purpose**: Templates for building AI copilots that assist with application delivery workflows.

**Use Cases**:
- Automated deployment assistance
- Release note generation
- Rollback decision support
- Environment synchronization

**Key Features**:
- Step-by-step deployment guidance
- Error detection and remediation suggestions
- Compliance checking
- Documentation generation

## Prompt Engineering Guides

### Anthropic Prompt Engineering Guide

**File**: `anthropic_prompt_engineering_guide.md`

**Source**: Anthropic's official best practices

**Key Techniques**:
- **Clear instructions**: Be explicit about desired output format
- **Examples**: Provide 2-3 examples for few-shot learning
- **Role assignment**: "You are an expert..."
- **Chain-of-thought**: Ask AI to think step-by-step
- **Output formatting**: Specify JSON, XML, or markdown structure

**Example**:
```markdown
You are an expert Python developer with 10 years of experience.

Task: Review the following code for potential bugs and security issues.

Code:
[CODE HERE]

Output format:
- List each issue with severity (high/medium/low)
- Provide suggested fix for each issue
- Explain reasoning for each suggestion
```

### Agentic AI Prompting Reference

**File**: `agentic_ai_prompting_crafting professional_reference.md`

**Purpose**: Professional-grade prompt engineering reference for agentic AI systems.

**Topics**:
- Agent persona design
- Task decomposition
- Context window management
- Multi-turn conversations
- Error recovery patterns

### Prompt Rendering Reference (PRR)

**File**: `PRR_ai_prompt_engineering_reference.md`

**Purpose**: Canonical reference for prompt rendering and formatting.

**Principles**:
- **Clarity**: Unambiguous instructions
- **Context**: Sufficient background information
- **Constraints**: Explicit boundaries and limitations

**Prompt Structure**:
```markdown
# [Task Title]

## Role
You are [role definition with expertise].

## Context
[Relevant background information]

## Task
[Specific, actionable instructions]

## Constraints
- [Constraint 1]
- [Constraint 2]

## Output Format
[Exact format specification]

## Examples
[1-3 examples of desired output]
```

### Architecture-Aware Prompting

**File**: `prr_project_instructions_architecture_aware_prompting_code_generation.md`

**Purpose**: Guide for prompts that leverage architectural knowledge for better code generation.

**Techniques**:
- Reference architecture diagrams in prompts
- Specify module boundaries and interfaces
- Include dependency constraints
- Cite coding standards and patterns

**Example**:
```markdown
Generate a new error detection plugin following the architecture in `error/plugins/`.

Architecture Constraints:
- Plugin must export `register()` function
- Manifest schema: `error/plugins/*/manifest.json`
- Use `PluginResult` and `PluginIssue` types from `error/shared/utils/types.py`
- Follow dependency ordering (DAG)

Reference Implementation:
See `error/plugins/python_ruff/` for example.
```

## Foundational Strategies

### The Core of a Good Prompt

**Files**: 
- `Foundational Strategies_The Core of a Good Prompt.txt`
- `The Core of a Good Prompt (1).txt`
- `A Guide to High-Quality Prompts for Superior AI (1).txt`

**Core Principles**:

1. **Specificity**: Vague prompts yield vague results
   - ❌ "Make this better"
   - ✅ "Refactor this function to use list comprehensions and add type hints"

2. **Context**: Provide necessary background
   - ❌ "Fix the bug"
   - ✅ "This function should return a list of integers but returns strings. Fix the type conversion."

3. **Examples**: Show desired output
   - Include 1-3 examples of expected results
   - Use few-shot learning for complex tasks

4. **Constraints**: Set boundaries
   - Specify what NOT to do
   - Define quality standards
   - Set time/complexity limits

5. **Format**: Structure output
   - Request JSON, XML, or markdown
   - Specify field names and types
   - Define validation rules

## ChatGPT Project Knowledge Prompt

**File**: `CHAT_GPT_PROJECT_KNOWL_PROMNT.md`

**Purpose**: Template for providing project context to ChatGPT for better assistance.

**Sections**:
- Project overview
- Technology stack
- Repository structure
- Coding standards
- Common tasks and workflows

**Usage**:
```markdown
# Project: AI Development Pipeline

## Overview
This is an AI-powered development pipeline with workstream orchestration,
error detection, and agent escalation.

## Structure
- `core/`: Core pipeline logic
- `error/`: Error detection engine
- `specifications/`: Spec management

## Standards
- Python 3.12+
- PEP 8 style guide
- 100% type hints required
- Pytest for testing

## Common Tasks
1. Add new plugin: See `error/plugins/README.md`
2. Create workstream: See `docs/workstream_authoring.md`
3. Run tests: `pytest -v`
```

## Paste-Ready Templates

### Plugin & Modular Architecture Analysis

**File**: `PASTE_READY_Plugin & Modular ARCHITECTURE ANALYSIS PROMPT.txt`

**Purpose**: Copy-paste ready prompt for analyzing plugin architectures.

**Usage**:
1. Copy entire file content
2. Paste into AI chat
3. AI analyzes plugin system and generates documentation

**Output**: Comprehensive plugin architecture analysis with:
- Plugin discovery flow
- Manifest schema documentation
- Interface contracts
- Dependency graph
- Example plugin code

## Using Prompts in the Pipeline

### In Aider Integration

**Location**: `aider/prompts/`

**Usage**:
```python
from aider.prompts import get_prompt_template

# Load prompt template
prompt = get_prompt_template("fix_errors")

# Fill in variables
prompt_filled = prompt.format(
    error_report=report,
    file_path=file_path
)

# Send to Aider
aider.run(prompt_filled)
```

### In Error Engine

**Agent Adapters** (`error/engine/agent_adapters.py`):
```python
from config.agent_profiles import load_prompt_template

def invoke_aider(file_path, error_report):
    # Load prompt template
    prompt = load_prompt_template("aider_fix")
    
    # Format with context
    prompt_filled = prompt.format(
        error_report=error_report,
        file_path=file_path,
        requirements="Fix linting errors, maintain functionality"
    )
    
    # Execute
    aider.run(prompt_filled)
```

### In Workstream Generation

**OpenSpec Converter** (`scripts/spec_to_workstream.py`):
```python
from Prompt import load_template

# Load workstream generation prompt
prompt = load_template("generate_workstream")

# Fill in OpenSpec data
prompt_filled = prompt.format(
    change_id=change_id,
    requirements=requirements,
    tasks=tasks
)

# Generate workstream via AI
workstream = ai.generate(prompt_filled)
```

## Prompt Library Organization

### By Purpose

**Code Generation**:
- `Master Implementation Prompt Template (Reusable).txt`
- `Plugin Architecture Analysis Prompt Template.md`

**Error Fixing**:
- Agent prompts in `config/agent_profiles.json` → `prompt_templates`

**Documentation**:
- `Application Delivery Copilot TEMPLATE.txt`

**Analysis**:
- `PASTE_READY_Plugin & Modular ARCHITECTURE ANALYSIS PROMPT.txt`

### By AI Model

**Anthropic Claude**:
- `anthropic_prompt_engineering_guide.md`

**OpenAI GPT**:
- `CHAT_GPT_PROJECT_KNOWL_PROMNT.md`

**Generic**:
- Most templates are model-agnostic

## Best Practices

1. **Version prompts**: Track prompt iterations (e.g., `TEMPLATEv2.md`)
2. **Test prompts**: Validate output quality before deployment
3. **Document variables**: List all fill-in variables clearly
4. **Provide examples**: Include 2-3 examples of desired output
5. **Iterate**: Refine prompts based on actual results

## Prompt Metrics

**Evaluate prompt quality**:
- **Accuracy**: Does AI produce correct output?
- **Consistency**: Same input → same output?
- **Completeness**: All required information generated?
- **Efficiency**: Minimal tokens for desired result?

## Related Sections

- **Aider**: `aider/` - Aider integration with prompts
- **Config**: `config/agent_profiles.json` - Agent prompt templates
- **Error Engine**: `error/engine/agent_adapters.py` - Uses prompts for fixes
- **Specifications**: `specifications/` - OpenSpec → Workstream conversion prompts

## See Also

- [Aider Prompt Guide](../aider/README.md#prompts)
- [Agent Profiles](../config/README.md#agent-profiles)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
