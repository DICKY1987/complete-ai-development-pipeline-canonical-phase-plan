# Tool Selection

**Purpose**: Decision tree and flow for selecting the appropriate tool adapter based on task requirements and tool profiles.

---

## Tool Selection Decision Tree

```mermaid
graph TD
    Start[Task Ready to Execute] --> CheckProfile{Tool Profile<br/>Specified?}
    
    CheckProfile -->|Yes| LoadProfile[Load Tool Profile]
    CheckProfile -->|No| UseDefault[Use Default Profile]
    
    LoadProfile --> ProfileValid{Profile<br/>Valid?}
    ProfileValid -->|Yes| SelectTool[Select Tool from Profile]
    ProfileValid -->|No| Error1[Error: Invalid Profile]
    
    UseDefault --> SelectTool
    
    SelectTool --> ToolType{Tool Type}
    
    ToolType -->|aider| CheckAider{Aider<br/>Available?}
    ToolType -->|codex| CheckCodex{Codex API<br/>Available?}
    ToolType -->|custom| CheckCustom{Custom Tool<br/>Configured?}
    ToolType -->|manual| ManualMode[Manual Execution Mode]
    
    CheckAider -->|Yes| ConfigureAider[Configure Aider]
    CheckAider -->|No| Fallback1{Fallback<br/>Defined?}
    
    CheckCodex -->|Yes| ConfigureCodex[Configure Codex]
    CheckCodex -->|No| Fallback2{Fallback<br/>Defined?}
    
    CheckCustom -->|Yes| ConfigureCustom[Configure Custom Tool]
    CheckCustom -->|No| Error2[Error: Tool Not Found]
    
    Fallback1 -->|Yes| LoadProfile
    Fallback1 -->|No| Error3[Error: No Fallback]
    
    Fallback2 -->|Yes| LoadProfile
    Fallback2 -->|No| Error3
    
    ConfigureAider --> ValidateAider{Validate<br/>Config}
    ConfigureCodex --> ValidateCodex{Validate<br/>Config}
    ConfigureCustom --> ValidateCustom{Validate<br/>Config}
    
    ValidateAider -->|Pass| InvokeAider[Invoke Aider Adapter]
    ValidateAider -->|Fail| Error4[Error: Invalid Config]
    
    ValidateCodex -->|Pass| InvokeCodex[Invoke Codex Adapter]
    ValidateCodex -->|Fail| Error4
    
    ValidateCustom -->|Pass| InvokeCustom[Invoke Custom Adapter]
    ValidateCustom -->|Fail| Error4
    
    ManualMode --> WaitUser[Wait for User Action]
    
    InvokeAider --> Execute[Execute Task]
    InvokeCodex --> Execute
    InvokeCustom --> Execute
    WaitUser --> Execute
    
    Execute --> Success[Task Complete]
    
    style Success fill:#4caf50,stroke:#2e7d32,color:#fff
    style Error1 fill:#f44336,stroke:#c62828,color:#fff
    style Error2 fill:#f44336,stroke:#c62828,color:#fff
    style Error3 fill:#f44336,stroke:#c62828,color:#fff
    style Error4 fill:#f44336,stroke:#c62828,color:#fff
    style ManualMode fill:#2196f3,stroke:#0d47a1,color:#fff
```

---

## Tool Profile Matching Algorithm

```mermaid
flowchart TD
    Start[Load All Tool Profiles] --> Filter1{Filter by<br/>Language}
    
    Filter1 -->|Match| Filter2{Filter by<br/>Task Type}
    Filter1 -->|No Match| NoProfiles[No Matching Profiles]
    
    Filter2 -->|Match| Filter3{Filter by<br/>Environment}
    Filter2 -->|No Match| NoProfiles
    
    Filter3 -->|Match| Sort[Sort by Priority]
    Filter3 -->|No Match| NoProfiles
    
    Sort --> SelectTop[Select Highest Priority]
    
    SelectTop --> Validate{Validate<br/>Requirements}
    
    Validate -->|Pass| Selected[Profile Selected]
    Validate -->|Fail| TryNext{More<br/>Profiles?}
    
    TryNext -->|Yes| SelectNext[Try Next Profile]
    TryNext -->|No| UseDefault[Use Default]
    
    SelectNext --> Validate
    
    NoProfiles --> UseDefault
    
    Selected --> Return[Return Profile]
    UseDefault --> Return
    
    style Selected fill:#4caf50,stroke:#2e7d32,color:#fff
    style NoProfiles fill:#ff9800,stroke:#e65100
    style UseDefault fill:#2196f3,stroke:#0d47a1,color:#fff
```

---

## Tool Adapter Architecture

```mermaid
graph TB
    subgraph "Tool Registry"
        Registry[Tool Adapter Registry]
        ProfileLoader[Profile Loader]
        Validator[Config Validator]
    end
    
    subgraph "Adapters"
        AiderAdapter[Aider Adapter]
        CodexAdapter[Codex Adapter]
        CustomAdapter[Custom Tool Adapter]
        ManualAdapter[Manual Adapter]
    end
    
    subgraph "Adapter Interface"
        Init[initialize method]
        Execute[execute method]
        Validate[validate method]
        Cleanup[cleanup method]
    end
    
    subgraph "External Tools"
        AiderCLI[Aider CLI]
        OpenAI[OpenAI API]
        CustomTool[Custom Script/Binary]
        HumanOperator[Human Operator]
    end
    
    Registry --> ProfileLoader
    Registry --> Validator
    
    Registry --> AiderAdapter
    Registry --> CodexAdapter
    Registry --> CustomAdapter
    Registry --> ManualAdapter
    
    AiderAdapter --> Init
    AiderAdapter --> Execute
    AiderAdapter --> Validate
    AiderAdapter --> Cleanup
    
    AiderAdapter --> AiderCLI
    CodexAdapter --> OpenAI
    CustomAdapter --> CustomTool
    ManualAdapter --> HumanOperator
    
    style Registry fill:#ff9800,stroke:#e65100,stroke-width:3px
    style AiderAdapter fill:#8bc34a,stroke:#558b2f
    style CodexAdapter fill:#8bc34a,stroke:#558b2f
    style CustomAdapter fill:#8bc34a,stroke:#558b2f
    style ManualAdapter fill:#2196f3,stroke:#0d47a1
```

---

## Tool Selection Sequence

```mermaid
sequenceDiagram
    participant Executor
    participant Registry
    participant ProfileLoader
    participant Validator
    participant Adapter
    participant Tool
    
    Executor->>Registry: Select tool for task
    Note over Executor,Registry: Task: "Create Python module"<br/>Language: python
    
    Registry->>ProfileLoader: Load profiles
    ProfileLoader-->>Registry: 3 profiles found
    
    Registry->>Registry: Filter by language (python)
    Registry->>Registry: Filter by task type (create)
    Registry->>Registry: Sort by priority
    
    Note over Registry: Profiles remaining:<br/>1. aider-python (priority:10)<br/>2. codex-python (priority:5)<br/>3. manual (priority:1)
    
    Registry->>Validator: Validate top profile (aider-python)
    
    alt Aider available
        Validator->>Validator: Check aider binary
        Validator->>Validator: Check git repository
        Validator-->>Registry: Valid
        
        Registry->>Adapter: Create Aider adapter
        Adapter->>Adapter: Initialize
        Adapter-->>Registry: Ready
        
        Registry-->>Executor: Aider adapter selected
        
        Executor->>Adapter: Execute task
        Adapter->>Tool: Run aider CLI
        Tool-->>Adapter: Output
        Adapter-->>Executor: Result
        
    else Aider not available
        Validator-->>Registry: Invalid (aider not found)
        Registry->>Validator: Try next profile (codex-python)
        Validator->>Validator: Check API key
        Validator-->>Registry: Valid
        
        Registry-->>Executor: Codex adapter selected
    end
```

---

## Profile Configuration Options

```mermaid
mindmap
  root((Tool Profile))
    Basic Settings
      name
      version
      priority
      enabled
    Tool Configuration
      tool_type
        aider
        codex
        custom
        manual
      command
      arguments
      working_directory
    Matching Rules
      languages
        python
        javascript
        typescript
      task_types
        create
        edit
        refactor
        test
      environments
        dev
        ci
        production
    Execution Settings
      timeout
      retry_attempts
      retry_delay
      env_vars
      stdin_input
    Hooks
      pre_execute
      post_execute
      on_success
      on_failure
    Fallback
      fallback_profile
      fallback_chain
```

---

## Timeout & Retry Configuration

```mermaid
gantt
    title Tool Execution with Retries
    dateFormat  HH:mm:ss
    axisFormat %H:%M:%S
    
    section Attempt 1
    Execution (timeout 5min)  :a1, 00:00:00, 300s
    Timeout Reached           :milestone, after a1, 0s
    
    section Retry 1
    Backoff Delay (2s)        :b1, after a1, 2s
    Execution (timeout 5min)  :a2, after b1, 120s
    Failure Detected          :milestone, after a2, 0s
    
    section Retry 2
    Backoff Delay (4s)        :b2, after a2, 4s
    Execution (timeout 5min)  :a3, after b2, 60s
    Success                   :milestone, after a3, 0s
```

---

## Fallback Chain Example

```mermaid
graph LR
    Task[Execute Task] --> Profile1[Aider Profile]
    
    Profile1 -->|Success| Done1[Complete]
    Profile1 -->|Fail| Profile2[Codex Profile]
    
    Profile2 -->|Success| Done2[Complete]
    Profile2 -->|Fail| Profile3[Custom Script Profile]
    
    Profile3 -->|Success| Done3[Complete]
    Profile3 -->|Fail| Profile4[Manual Profile]
    
    Profile4 -->|Success| Done4[Complete]
    Profile4 -->|Fail| Failed[Task Failed]
    
    style Done1 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Done2 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Done3 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Done4 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Failed fill:#f44336,stroke:#c62828,color:#fff
    style Profile1 fill:#2196f3,stroke:#0d47a1,color:#fff
    style Profile2 fill:#2196f3,stroke:#0d47a1,color:#fff
    style Profile3 fill:#ff9800,stroke:#e65100,color:#fff
    style Profile4 fill:#9e9e9e,stroke:#424242,color:#fff
```

---

## Tool Profile Priority Scoring

```mermaid
graph TD
    Start[Calculate Score] --> BaseScore[Base Priority: profile.priority]
    
    BaseScore --> LangMatch{Language<br/>Match?}
    LangMatch -->|Exact| AddLang[+50 points]
    LangMatch -->|Partial| AddPartial[+25 points]
    LangMatch -->|No| AddLang0[+0 points]
    
    AddLang --> TaskMatch{Task Type<br/>Match?}
    AddPartial --> TaskMatch
    AddLang0 --> TaskMatch
    
    TaskMatch -->|Exact| AddTask[+30 points]
    TaskMatch -->|No| AddTask0[+0 points]
    
    AddTask --> EnvMatch{Environment<br/>Match?}
    AddTask0 --> EnvMatch
    
    EnvMatch -->|Match| AddEnv[+20 points]
    EnvMatch -->|No| AddEnv0[+0 points]
    
    AddEnv --> Recent{Recently<br/>Successful?}
    AddEnv0 --> Recent
    
    Recent -->|Yes| AddRecent[+10 points]
    Recent -->|No| AddRecent0[+0 points]
    
    AddRecent --> FinalScore[Final Score]
    AddRecent0 --> FinalScore
    
    FinalScore --> Sort[Sort Profiles by Score]
    
    style FinalScore fill:#4caf50,stroke:#2e7d32,color:#fff
```

**Example Scoring**:
```
Profile: aider-python
- Base priority: 10
- Language match (python): +50
- Task type match (create): +30
- Environment match (dev): +20
- Recently successful: +10
= Total: 120 points

Profile: codex-python
- Base priority: 5
- Language match (python): +50
- Task type match (none): +0
- Environment match (dev): +20
- Recently successful: +0
= Total: 75 points

Winner: aider-python (120 > 75)
```

---

## Environment-Specific Selection

```mermaid
graph TB
    Start[Task Execution] --> GetEnv{Check<br/>Environment}
    
    GetEnv -->|dev| DevProfiles[Development Profiles]
    GetEnv -->|ci| CIProfiles[CI Profiles]
    GetEnv -->|prod| ProdProfiles[Production Profiles]
    
    DevProfiles --> Dev1[Aider with Interactive]
    DevProfiles --> Dev2[Local Codex]
    
    CIProfiles --> CI1[Codex API Only]
    CIProfiles --> CI2[No Interactive Tools]
    
    ProdProfiles --> Prod1[Manual Approval Required]
    ProdProfiles --> Prod2[Logged & Monitored]
    
    Dev1 --> Execute[Execute]
    Dev2 --> Execute
    CI1 --> Execute
    CI2 --> Execute
    Prod1 --> Execute
    Prod2 --> Execute
    
    style DevProfiles fill:#e3f2fd
    style CIProfiles fill:#fff3e0
    style ProdProfiles fill:#ffebee
```

---

## Tool Adapter Interface

All adapters must implement this interface:

```python
class ToolAdapter(ABC):
    """Base class for all tool adapters."""
    
    @abstractmethod
    def initialize(self, config: Dict) -> None:
        """Initialize the adapter with configuration."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate tool is available and configured correctly."""
        pass
    
    @abstractmethod
    def execute(self, task: Task) -> ExecutionResult:
        """Execute the task using the tool."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources after execution."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return list of tool capabilities."""
        pass
```

---

## Configuration Example

```yaml
# Tool profiles configuration
tool_profiles:
  # Aider profile for Python development
  - name: aider-python
    enabled: true
    priority: 10
    
    tool:
      type: aider
      command: aider
      args:
        - "--yes"
        - "--no-pretty"
    
    matching:
      languages: [python]
      task_types: [create, edit, refactor]
      environments: [dev, ci]
    
    execution:
      timeout: 300
      retry_attempts: 3
      retry_delay: 2
      env_vars:
        AIDER_MODEL: "gpt-4-turbo"
    
    hooks:
      pre_execute: "scripts/pre_aider.sh"
      post_execute: "scripts/post_aider.sh"
    
    fallback: codex-python

  # Codex profile
  - name: codex-python
    enabled: true
    priority: 5
    
    tool:
      type: codex
      api_endpoint: "https://api.openai.com/v1"
    
    matching:
      languages: [python, javascript, typescript]
      task_types: [create, edit]
      environments: [dev, ci, prod]
    
    execution:
      timeout: 60
      retry_attempts: 5
      retry_delay: 1
      env_vars:
        OPENAI_API_KEY: "${OPENAI_API_KEY}"
    
    fallback: manual
    
  # Manual fallback
  - name: manual
    enabled: true
    priority: 1
    
    tool:
      type: manual
    
    matching:
      languages: ["*"]  # Matches all
      task_types: ["*"]
      environments: ["*"]
```

---

## Tool Selection Metrics

| Metric | Purpose | Threshold |
|--------|---------|-----------|
| **Selection Time** | Time to select adapter | <100ms |
| **Success Rate** | % tasks successfully executed | >90% |
| **Fallback Rate** | % using fallback | <10% |
| **Timeout Rate** | % tasks timing out | <5% |
| **Profile Match Rate** | % tasks with profile match | >95% |

---

## Integration with Core Engine

```mermaid
graph LR
    Executor[Step Executor] --> Registry[Tool Registry]
    Registry --> ProfileLoader[Profile Loader]
    Registry --> Adapter[Selected Adapter]
    
    Adapter --> Tool[External Tool]
    
    Registry --> Config[config/tool_profiles.yaml]
    Adapter --> EnvVars[Environment Variables]
    
    Tool --> Output[Execution Output]
    Output --> Executor
    
    style Registry fill:#ff9800,stroke:#e65100,stroke-width:3px
    style Executor fill:#2196f3,stroke:#0d47a1,color:#fff
```

---

## Related Documentation

- [System Architecture](./SYSTEM_ARCHITECTURE.md) - Overall architecture
- [Task Lifecycle](./TASK_LIFECYCLE.md) - Task execution flow
- [Tool Profile Configuration](../examples/tool_profile_annotated.yaml) - Detailed config reference

---

**Last Updated**: 2025-11-22  
**Maintainer**: Architecture Team  
**Implementation**: `aim/tool_registry.py`, `aim/adapters/`
