# System Architecture

**Purpose**: High-level overview of the Complete AI Development Pipeline system architecture, showing all major components and their interactions.

---

## System Overview

```mermaid
graph TB
    subgraph "User Layer"
        CLI[CLI Interface]
        GUI[GUI Dashboard]
        API[REST API]
    end
    
    subgraph "Core Engine"
        Orchestrator[Workstream Orchestrator]
        Scheduler[Step Scheduler]
        Executor[Step Executor]
        StateManager[State Manager]
    end
    
    subgraph "State & Persistence"
        DB[(SQLite Database)]
        Checkpoints[Checkpoint Manager]
        Worktrees[Git Worktrees]
    end
    
    subgraph "Error Detection & Recovery"
        ErrorEngine[Error Engine]
        PluginManager[Plugin Manager]
        CircuitBreaker[Circuit Breaker]
        RetryLogic[Retry Manager]
    end
    
    subgraph "Specification Management"
        SpecIndex[Spec Index]
        SpecResolver[Spec Resolver]
        OpenSpecParser[OpenSpec Parser]
        ChangeProposals[Change Proposals]
    end
    
    subgraph "Tool Adapters"
        AiderAdapter[Aider Adapter]
        CodexAdapter[Codex Adapter]
        CustomAdapter[Custom Tool Adapter]
        ToolRegistry[Tool Registry]
    end
    
    subgraph "External Services"
        Git[Git]
        Aider[Aider CLI]
        OpenAI[OpenAI API]
        CCPM[CCPM/PM Tools]
    end
    
    %% User Layer Connections
    CLI --> Orchestrator
    GUI --> Orchestrator
    API --> Orchestrator
    
    %% Core Engine Flow
    Orchestrator --> Scheduler
    Scheduler --> Executor
    Executor --> StateManager
    StateManager --> DB
    
    %% Checkpoint Integration
    Orchestrator --> Checkpoints
    Checkpoints --> Worktrees
    Checkpoints --> DB
    
    %% Error Detection Flow
    Executor --> ErrorEngine
    ErrorEngine --> PluginManager
    ErrorEngine --> CircuitBreaker
    CircuitBreaker --> RetryLogic
    RetryLogic --> Executor
    
    %% Specification Integration
    Orchestrator --> OpenSpecParser
    OpenSpecParser --> SpecIndex
    SpecIndex --> SpecResolver
    SpecResolver --> ChangeProposals
    
    %% Tool Adapter Flow
    Executor --> ToolRegistry
    ToolRegistry --> AiderAdapter
    ToolRegistry --> CodexAdapter
    ToolRegistry --> CustomAdapter
    
    %% External Service Connections
    AiderAdapter --> Aider
    CodexAdapter --> OpenAI
    Worktrees --> Git
    ChangeProposals --> CCPM
    
    %% Styling
    classDef userLayer fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef coreEngine fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef persistence fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef errorHandling fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef specifications fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef toolAdapters fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef external fill:#eeeeee,stroke:#424242,stroke-width:2px
    
    class CLI,GUI,API userLayer
    class Orchestrator,Scheduler,Executor,StateManager coreEngine
    class DB,Checkpoints,Worktrees persistence
    class ErrorEngine,PluginManager,CircuitBreaker,RetryLogic errorHandling
    class SpecIndex,SpecResolver,OpenSpecParser,ChangeProposals specifications
    class AiderAdapter,CodexAdapter,CustomAdapter,ToolRegistry toolAdapters
    class Git,Aider,OpenAI,CCPM external
```

---

## Component Descriptions

### User Layer (Blue)

**CLI Interface**
- Command-line interface for running workstreams
- Primary entry point for developers
- Supports interactive and batch modes

**GUI Dashboard**
- Web-based visual interface
- Real-time progress monitoring
- Workstream visualization and control

**REST API**
- Programmatic access to pipeline
- Integration with external tools
- Webhook support for events

---

###Core Engine (Orange)

**Workstream Orchestrator**
- Central coordinator for workstream execution
- Loads and validates workstream definitions
- Manages overall workflow lifecycle

**Step Scheduler**
- Dependency resolution (DAG)
- Parallel execution planning
- Worker pool management
- Resource allocation

**Step Executor**
- Executes individual workstream steps
- Tool adapter invocation
- Output capture and validation
- Acceptance test execution

**State Manager**
- Tracks execution state
- Persists progress to database
- Handles state transitions
- Recovery from failures

---

### State & Persistence (Purple)

**SQLite Database**
- Central state storage
- Workstream metadata
- Execution history
- Configuration cache

**Checkpoint Manager**
- Saves intermediate state
- Enables resume capability
- Manages checkpoint lifecycle
- Validation on restore

**Git Worktrees**
- Isolated execution environments
- Branch per workstream
- Safe experimentation
- Easy rollback

---

### Error Detection & Recovery (Red)

**Error Engine**
- Monitors step execution
- Detects error patterns
- Triggers recovery actions
- Diagnostic collection

**Plugin Manager**
- Loads error detection plugins
- Routes errors to appropriate plugins
- Manages plugin lifecycle
- Extensibility framework

**Circuit Breaker**
- Prevents cascading failures
- Three states: CLOSED, OPEN, HALF_OPEN
- Configurable thresholds
- Automatic recovery

**Retry Manager**
- Exponential backoff
- Jitter for distributed systems
- Per-step retry limits
- Success/failure tracking

---

### Specification Management (Green)

**OpenSpec Parser**
- Parses OpenSpec YAML files
- Converts to internal format
- Validation and linting
- Version compatibility

**Spec Index**
- Fast specification lookup
- Change tracking
- Dependency mapping
- Auto-generated from specs

**Spec Resolver**
- URI-based spec references
- Dependency resolution
- Circular dependency detection
- Version conflict handling

**Change Proposals**
- Tracks spec modifications
- Links to workstreams
- CCPM integration
- Approval workflows

---

### Tool Adapters (Yellow)

**Tool Registry**
- Manages available tools
- Profile matching
- Capability discovery
- Fallback selection

**Aider Adapter**
- Invokes Aider CLI
- Streams output
- Handles interruptions
- Git integration

**Codex Adapter**
- OpenAI Codex API integration
- Prompt management
- Rate limiting
- Response parsing

**Custom Tool Adapter**
- Extensibility point
- User-defined tools
- Standard interface
- Error handling

---

### External Services (Gray)

**Git**
- Version control
- Worktree management
- Commit history
- Branch operations

**Aider CLI**
- AI pair programming
- Code generation
- File editing
- Test creation

**OpenAI API**
- GPT-4/GPT-3.5 access
- Codex endpoints
- Rate limiting
- API key management

**CCPM/PM Tools**
- Project management integration
- Issue tracking
- Time estimates
- Dependency chains

---

## Data Flow: Workstream Execution

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Scheduler
    participant Executor
    participant ToolAdapter
    participant DB
    
    User->>Orchestrator: Run workstream
    Orchestrator->>DB: Load workstream definition
    DB-->>Orchestrator: Workstream JSON
    
    Orchestrator->>Scheduler: Build execution plan
    Scheduler->>Scheduler: Resolve dependencies (DAG)
    Scheduler-->>Orchestrator: Execution order
    
    loop For each step
        Orchestrator->>Executor: Execute step
        Executor->>ToolAdapter: Invoke tool
        ToolAdapter->>ToolAdapter: Run Aider/Codex/etc
        ToolAdapter-->>Executor: Tool output
        
        Executor->>Executor: Validate output
        Executor->>DB: Save step result
        
        alt Success
            Executor-->>Orchestrator: Step complete
        else Failure
            Executor->>Executor: Check circuit breaker
            alt Should retry
                Executor->>Executor: Exponential backoff
                Executor->>ToolAdapter: Retry step
            else Circuit open
                Executor-->>Orchestrator: Step failed
            end
        end
    end
    
    Orchestrator->>DB: Mark workstream complete
    Orchestrator-->>User: Execution summary
```

---

## Error Handling Flow

```mermaid
graph LR
    StepExecution[Step Execution] --> CheckError{Error?}
    CheckError -->|No| Success[Mark Success]
    CheckError -->|Yes| ErrorEngine[Error Engine]
    
    ErrorEngine --> PluginAnalysis[Plugin Analysis]
    PluginAnalysis --> ErrorType{Error Type}
    
    ErrorType -->|Transient| CheckCircuit{Circuit Breaker}
    ErrorType -->|Permanent| Fail[Mark Failed]
    
    CheckCircuit -->|Closed| Retry[Retry with Backoff]
    CheckCircuit -->|Open| FastFail[Fast Fail]
    CheckCircuit -->|Half-Open| TestRetry[Test Retry]
    
    Retry --> StepExecution
    TestRetry --> StepExecution
    
    FastFail --> WaitCooldown[Wait Cooldown]
    WaitCooldown --> CheckCircuit
    
    Success --> NextStep[Next Step]
    Fail --> Compensation[Run Compensations]
    
    style Success fill:#4caf50,stroke:#2e7d32,color:#fff
    style Fail fill:#f44336,stroke:#c62828,color:#fff
    style Retry fill:#ff9800,stroke:#e65100,color:#fff
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevCLI[Developer CLI]
        DevWorktrees[Local Worktrees]
        DevDB[(Local SQLite)]
    end
    
    subgraph "CI/CD Environment"
        CICD[CI/CD Pipeline]
        TestWorktrees[Test Worktrees]
        TestDB[(Test Database)]
    end
    
    subgraph "Production Environment"
        ProdAPI[Production API]
        ProdGUI[Production GUI]
        ProdDB[(Production DB)]
        ProdWorktrees[Production Worktrees]
    end
    
    DevCLI --> DevWorktrees
    DevCLI --> DevDB
    
    CICD --> TestWorktrees
    CICD --> TestDB
    
    ProdAPI --> ProdDB
    ProdAPI --> ProdWorktrees
    ProdGUI --> ProdDB
    ProdGUI --> ProdWorktrees
    
    DevCLI -.->|Push| CICD
    CICD -.->|Deploy| ProdAPI
    
    style DevCLI fill:#e3f2fd
    style CICD fill:#fff3e0
    style ProdAPI fill:#e8f5e9
    style ProdGUI fill:#e8f5e9
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Database** | SQLite | State persistence, execution history |
| **Language** | Python 3.10+ | Core implementation |
| **CLI** | Click/Argparse | Command-line interface |
| **GUI** | Flask/FastAPI | Web dashboard |
| **Visualization** | Mermaid | Architecture diagrams |
| **Version Control** | Git | Worktrees, versioning |
| **AI Tools** | Aider, OpenAI Codex | Code generation |
| **Validation** | Pydantic, JSON Schema | Data validation |
| **Testing** | Pytest | Unit/integration tests |
| **CI/CD** | GitHub Actions | Automation |

---

## Directory Structure Mapping

```
Repository Root
│
├─ core/                    → Core Engine (Orange)
│  ├─ state/               → State & Persistence (Purple)
│  ├─ engine/              → Orchestrator, Scheduler, Executor
│  └─ planning/            → Workstream planning
│
├─ error/                   → Error Detection & Recovery (Red)
│  ├─ engine/              → Error Engine, State Machine
│  └─ plugins/             → Detection plugins
│
├─ specifications/          → Specification Management (Green)
│  ├─ content/             → OpenSpec files
│  ├─ tools/               → Indexer, resolver, etc.
│  └─ bridge/              → OpenSpec → Workstream
│
├─ aim/                     → Tool Adapters (Yellow)
├─ aider/                   → Aider integration
│
├─ workstreams/             → Workstream definitions
├─ schema/                  → JSON schemas
├─ config/                  → Tool profiles, configs
│
└─ scripts/                 → Automation scripts
```

---

## Key Design Principles

### 1. **Separation of Concerns**
- Core engine independent of tools
- Error detection decoupled from execution
- Specifications separate from execution

### 2. **Extensibility**
- Plugin architecture for error detection
- Adapter pattern for tools
- Custom tool support

### 3. **Resilience**
- Circuit breaker pattern
- Retry with exponential backoff
- Checkpoint/resume capability

### 4. **Observability**
- Comprehensive logging
- State machine tracking
- Execution history

### 5. **Isolation**
- Git worktrees per workstream
- Process-level isolation for tools
- Database transaction safety

---

## Related Documentation

- [Task Lifecycle](./TASK_LIFECYCLE.md) - Detailed state machine
- [Error Escalation](./ERROR_ESCALATION.md) - Error handling flow
- [Tool Selection](./TOOL_SELECTION.md) - Tool adapter architecture
- [Spec Integration](./SPEC_INTEGRATION.md) - OpenSpec workflow

---

**Last Updated**: 2025-11-22  
**Maintainer**: Architecture Team  
**Auto-Validation**: `python scripts/validate_diagrams.py`
