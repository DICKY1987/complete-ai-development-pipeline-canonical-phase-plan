# Error Escalation

**Purpose**: Visualization of error detection, analysis, and escalation flow through the plugin architecture.

---

## Error Detection & Escalation Flow

```mermaid
flowchart TD
    Start[Task Execution] --> Execute[Tool Execution]
    
    Execute -->|Success| Validate[Validate Output]
    Execute -->|Error| CaptureError[Capture Error]
    
    Validate -->|Pass| Success[Task Success]
    Validate -->|Fail| CaptureError
    
    CaptureError --> ErrorEngine[Error Engine]
    
    ErrorEngine --> DetectType{Error Type<br/>Detection}
    
    DetectType --> CheckPlugins[Query Plugin Manager]
    
    CheckPlugins --> PluginLoop{For Each<br/>Plugin}
    
    PluginLoop --> Plugin1[Python Ruff Plugin]
    PluginLoop --> Plugin2[JavaScript ESLint Plugin]
    PluginLoop --> Plugin3[Linting Plugin]
    PluginLoop --> Plugin4[Security Plugin]
    PluginLoop --> Plugin5[Custom Plugins]
    
    Plugin1 --> CanHandle1{Can Handle?}
    Plugin2 --> CanHandle2{Can Handle?}
    Plugin3 --> CanHandle3{Can Handle?}
    Plugin4 --> CanHandle4{Can Handle?}
    Plugin5 --> CanHandle5{Can Handle?}
    
    CanHandle1 -->|Yes| Parse1[Parse Error]
    CanHandle2 -->|Yes| Parse2[Parse Error]
    CanHandle3 -->|Yes| Parse3[Parse Error]
    CanHandle4 -->|Yes| Parse4[Parse Error]
    CanHandle5 -->|Yes| Parse5[Parse Error]
    
    CanHandle1 -->|No| PluginLoop
    CanHandle2 -->|No| PluginLoop
    CanHandle3 -->|No| PluginLoop
    CanHandle4 -->|No| PluginLoop
    CanHandle5 -->|No| PluginLoop
    
    Parse1 --> ErrorClassified[Error Classified]
    Parse2 --> ErrorClassified
    Parse3 --> ErrorClassified
    Parse4 --> ErrorClassified
    Parse5 --> ErrorClassified
    
    ErrorClassified --> Severity{Severity<br/>Level}
    
    Severity -->|INFO| LogInfo[Log Information]
    Severity -->|WARNING| LogWarn[Log Warning]
    Severity -->|ERROR| Recoverable{Recoverable?}
    Severity -->|CRITICAL| Escalate[Escalate Immediately]
    
    LogInfo --> Continue[Continue Execution]
    LogWarn --> Continue
    
    Recoverable -->|Yes| AttemptFix{Auto-Fix<br/>Available?}
    Recoverable -->|No| Escalate
    
    AttemptFix -->|Yes| RunFix[Run Fix Action]
    AttemptFix -->|No| RetryDecision{Should<br/>Retry?}
    
    RunFix -->|Success| Retry[Retry Task]
    RunFix -->|Failed| RetryDecision
    
    RetryDecision -->|Yes| CircuitCheck{Circuit<br/>Breaker}
    RetryDecision -->|No| Escalate
    
    CircuitCheck -->|Closed| Retry
    CircuitCheck -->|Open| FastFail[Fast Fail]
    CircuitCheck -->|Half-Open| TestRetry[Test Retry]
    
    Retry --> Execute
    TestRetry --> Execute
    
    FastFail --> Escalate
    Escalate --> NotifyOps[Notify Operations]
    Escalate --> SaveDiagnostics[Save Diagnostics]
    Escalate --> TaskFailed[Mark Task Failed]
    
    style Success fill:#4caf50,stroke:#2e7d32,color:#fff
    style TaskFailed fill:#f44336,stroke:#c62828,color:#fff
    style Escalate fill:#ff5722,stroke:#bf360c,color:#fff
    style RunFix fill:#2196f3,stroke:#0d47a1,color:#fff
```

---

## Error State Machine

```mermaid
stateDiagram-v2
    [*] --> DETECTED: Error Occurs
    
    DETECTED --> ANALYZING: Plugin Processing
    ANALYZING --> CLASSIFIED: Error Identified
    ANALYZING --> UNKNOWN: No Plugin Match
    
    CLASSIFIED --> INFO: Severity = Info
    CLASSIFIED --> WARNING: Severity = Warning
    CLASSIFIED --> ERROR: Severity = Error
    CLASSIFIED --> CRITICAL: Severity = Critical
    
    INFO --> LOGGED: Logged Only
    WARNING --> LOGGED: Logged Only
    
    ERROR --> RECOVERABLE: Can Auto-Fix
    ERROR --> NON_RECOVERABLE: Cannot Fix
    
    CRITICAL --> ESCALATED: Immediate Action
    
    RECOVERABLE --> FIXING: Apply Fix
    FIXING --> RESOLVED: Fix Successful
    FIXING --> FAILED_FIX: Fix Failed
    
    FAILED_FIX --> RETRYING: Retry Available
    FAILED_FIX --> ESCALATED: No Retries
    
    NON_RECOVERABLE --> RETRYING: Retry Available
    NON_RECOVERABLE --> ESCALATED: No Retries
    
    RETRYING --> DETECTED: Retry Execution
    
    UNKNOWN --> ESCALATED: Manual Review
    
    LOGGED --> [*]
    RESOLVED --> [*]
    ESCALATED --> [*]
    
    note right of DETECTED
        Initial error capture
        Stack trace collected
        Context preserved
    end note
    
    note right of ANALYZING
        Plugin matching
        Pattern recognition
        Cause identification
    end note
    
    note right of ESCALATED
        Human intervention
        Operations notified
        Diagnostics saved
    end note
```

---

## Plugin Architecture

```mermaid
graph TB
    subgraph "Error Engine Core"
        ErrorEngine[Error Engine]
        PluginManager[Plugin Manager]
        ErrorCache[Error Cache]
    end
    
    subgraph "Detection Plugins"
        PythonPlugin[Python Ruff Plugin]
        JSPlugin[JavaScript ESLint Plugin]
        LintPlugin[Generic Linting Plugin]
        SecurityPlugin[Security Scanner Plugin]
        TestPlugin[Test Failure Plugin]
        CustomPlugin[Custom Plugin]
    end
    
    subgraph "Plugin Interface"
        Manifest[manifest.json]
        ParseMethod[parse method]
        FixMethod[fix method]
        CanHandleMethod[can_handle method]
    end
    
    subgraph "Output Actions"
        Logger[Logging Service]
        Notifier[Notification Service]
        Diagnostics[Diagnostics Collector]
        Metrics[Metrics Tracker]
    end
    
    ErrorEngine --> PluginManager
    PluginManager --> PythonPlugin
    PluginManager --> JSPlugin
    PluginManager --> LintPlugin
    PluginManager --> SecurityPlugin
    PluginManager --> TestPlugin
    PluginManager --> CustomPlugin
    
    PythonPlugin --> Manifest
    PythonPlugin --> ParseMethod
    PythonPlugin --> FixMethod
    PythonPlugin --> CanHandleMethod
    
    ErrorEngine --> ErrorCache
    ErrorEngine --> Logger
    ErrorEngine --> Notifier
    ErrorEngine --> Diagnostics
    ErrorEngine --> Metrics
    
    style ErrorEngine fill:#ff9800,stroke:#e65100,stroke-width:3px
    style PluginManager fill:#2196f3,stroke:#0d47a1,stroke-width:2px
    style PythonPlugin fill:#8bc34a,stroke:#558b2f
    style JSPlugin fill:#8bc34a,stroke:#558b2f
    style LintPlugin fill:#8bc34a,stroke:#558b2f
    style SecurityPlugin fill:#8bc34a,stroke:#558b2f
    style TestPlugin fill:#8bc34a,stroke:#558b2f
    style CustomPlugin fill:#8bc34a,stroke:#558b2f
```

---

## Plugin Interaction Sequence

```mermaid
sequenceDiagram
    participant Task
    participant ErrorEngine
    participant PluginManager
    participant PythonPlugin
    participant Notifier
    participant DB
    
    Task->>ErrorEngine: Error occurred
    Note over Task,ErrorEngine: Error: SyntaxError in file.py
    
    ErrorEngine->>ErrorEngine: Capture stack trace
    ErrorEngine->>DB: Check error cache
    DB-->>ErrorEngine: Not cached
    
    ErrorEngine->>PluginManager: Find handler
    PluginManager->>PythonPlugin: can_handle(error)?
    PythonPlugin-->>PluginManager: True (Python error)
    
    PluginManager-->>ErrorEngine: PythonPlugin selected
    
    ErrorEngine->>PythonPlugin: parse(error)
    PythonPlugin->>PythonPlugin: Parse stack trace
    PythonPlugin->>PythonPlugin: Identify issue
    PythonPlugin-->>ErrorEngine: Classification
    
    Note over ErrorEngine,PythonPlugin: Type: SyntaxError<br/>Severity: ERROR<br/>Recoverable: No
    
    ErrorEngine->>ErrorEngine: Check severity
    ErrorEngine->>ErrorEngine: Check if recoverable
    
    alt Auto-fix available
        ErrorEngine->>PythonPlugin: fix(error)
        PythonPlugin->>PythonPlugin: Apply fix
        PythonPlugin-->>ErrorEngine: Fix result
    else No auto-fix
        ErrorEngine->>ErrorEngine: Determine action
    end
    
    ErrorEngine->>DB: Save error details
    ErrorEngine->>Notifier: Send notification
    ErrorEngine-->>Task: Error classified
```

---

## Error Severity Levels

```mermaid
graph LR
    subgraph "INFO"
        I1[Informational messages]
        I2[Deprecation warnings]
        I3[Style suggestions]
    end
    
    subgraph "WARNING"
        W1[Potential issues]
        W2[Best practice violations]
        W3[Performance concerns]
    end
    
    subgraph "ERROR"
        E1[Execution failures]
        E2[Validation errors]
        E3[Test failures]
    end
    
    subgraph "CRITICAL"
        C1[Security vulnerabilities]
        C2[Data loss risks]
        C3[System failures]
    end
    
    I1 --> Log[Log Only]
    I2 --> Log
    I3 --> Log
    
    W1 --> LogWarn[Log + Warn]
    W2 --> LogWarn
    W3 --> LogWarn
    
    E1 --> Retry[Retry Logic]
    E2 --> Retry
    E3 --> Retry
    
    C1 --> Escalate[Immediate Escalation]
    C2 --> Escalate
    C3 --> Escalate
    
    style I1 fill:#e3f2fd
    style I2 fill:#e3f2fd
    style I3 fill:#e3f2fd
    style W1 fill:#fff3e0
    style W2 fill:#fff3e0
    style W3 fill:#fff3e0
    style E1 fill:#ffebee
    style E2 fill:#ffebee
    style E3 fill:#ffebee
    style C1 fill:#f44336,color:#fff
    style C2 fill:#f44336,color:#fff
    style C3 fill:#f44336,color:#fff
```

---

## Plugin Discovery & Loading

```mermaid
flowchart TD
    Start[System Startup] --> ScanPlugins[Scan error/plugins/]
    
    ScanPlugins --> FindManifests{Find manifest.json<br/>files}
    
    FindManifests --> Manifest1[python_ruff/manifest.json]
    FindManifests --> Manifest2[javascript_eslint/manifest.json]
    FindManifests --> Manifest3[linting/manifest.json]
    FindManifests --> Manifest4[security/manifest.json]
    
    Manifest1 --> Validate1{Validate<br/>Schema}
    Manifest2 --> Validate2{Validate<br/>Schema}
    Manifest3 --> Validate3{Validate<br/>Schema}
    Manifest4 --> Validate4{Validate<br/>Schema}
    
    Validate1 -->|Valid| Load1[Load Plugin]
    Validate2 -->|Valid| Load2[Load Plugin]
    Validate3 -->|Valid| Load3[Load Plugin]
    Validate4 -->|Valid| Load4[Load Plugin]
    
    Validate1 -->|Invalid| Skip1[Skip Plugin]
    Validate2 -->|Invalid| Skip2[Skip Plugin]
    Validate3 -->|Invalid| Skip3[Skip Plugin]
    Validate4 -->|Invalid| Skip4[Skip Plugin]
    
    Load1 --> Register[Register with PluginManager]
    Load2 --> Register
    Load3 --> Register
    Load4 --> Register
    
    Register --> Ready[Plugins Ready]
    
    style Ready fill:#4caf50,stroke:#2e7d32,color:#fff
    style Skip1 fill:#ff9800
    style Skip2 fill:#ff9800
    style Skip3 fill:#ff9800
    style Skip4 fill:#ff9800
```

---

## Error Cache & Deduplication

```mermaid
graph TD
    NewError[New Error] --> Hash[Calculate Error Hash]
    Hash --> CheckCache{Error in<br/>Cache?}
    
    CheckCache -->|Yes| GetCached[Get Cached Entry]
    CheckCache -->|No| Analyze[Analyze Error]
    
    GetCached --> Increment[Increment Count]
    GetCached --> CheckThreshold{Count ><br/>Threshold?}
    
    CheckThreshold -->|Yes| Suppress[Suppress Duplicate]
    CheckThreshold -->|No| Report[Report Error]
    
    Analyze --> Classify[Classify Error]
    Classify --> Cache[Add to Cache]
    Cache --> Report
    
    Suppress --> Log[Log Suppression]
    Report --> Process[Process Error]
    
    style Suppress fill:#ff9800,stroke:#e65100
    style Process fill:#4caf50,stroke:#2e7d32,color:#fff
```

**Error Hash Calculation**:
```python
error_hash = sha256(
    error_type +
    error_message +
    file_path +
    line_number
).hexdigest()[:16]
```

---

## Notification Escalation Levels

```mermaid
graph TB
    Error[Error Detected] --> Severity{Severity}
    
    Severity -->|INFO| NoNotify[No Notification]
    Severity -->|WARNING| LogOnly[Log File Only]
    Severity -->|ERROR| TeamNotify[Notify Team]
    Severity -->|CRITICAL| OpsEscalate[Escalate to Ops]
    
    NoNotify --> End1[End]
    LogOnly --> End2[End]
    
    TeamNotify --> Slack[Slack Channel]
    TeamNotify --> Email[Team Email]
    
    OpsEscalate --> PagerDuty[PagerDuty]
    OpsEscalate --> OpsMail[Ops Email]
    OpsEscalate --> SlackUrgent[#incidents Channel]
    
    style NoNotify fill:#e8f5e9
    style LogOnly fill:#fff3e0
    style TeamNotify fill:#ffebee
    style OpsEscalate fill:#f44336,color:#fff
```

---

## Diagnostic Collection

When errors are escalated, the following diagnostics are collected:

```mermaid
mindmap
  root((Error<br/>Diagnostics))
    System Context
      OS & Python version
      Available resources
      Environment variables
      Git repository state
    Task Context
      Workstream ID
      Step ID
      Tool being used
      Execution duration
    Error Details
      Error type
      Stack trace
      Error message
      File & line number
    Execution State
      Previous attempts
      Retry count
      Circuit breaker state
      Recent logs (last 100 lines)
    File State
      Changed files
      File diffs
      File hashes
      Working directory
```

---

## Plugin Manifest Structure

```json
{
  "name": "python_ruff",
  "version": "1.0.0",
  "description": "Python error detection using Ruff",
  
  "capabilities": {
    "languages": ["python"],
    "error_types": ["syntax", "runtime", "linting"],
    "auto_fix": true
  },
  
  "priority": 10,
  
  "patterns": [
    "*.py",
    "SyntaxError",
    "IndentationError",
    "NameError"
  ],
  
  "entry_point": "plugin.py",
  "class_name": "RuffPlugin",
  
  "config": {
    "ruff_path": "ruff",
    "auto_fix_enabled": true,
    "severity_mapping": {
      "E": "ERROR",
      "W": "WARNING",
      "I": "INFO"
    }
  }
}
```

---

## Auto-Fix Flow

```mermaid
sequenceDiagram
    participant ErrorEngine
    participant Plugin
    participant FileSystem
    participant Git
    participant Validator
    
    ErrorEngine->>Plugin: Error requires fix
    Plugin->>Plugin: Analyze error
    Plugin->>Plugin: Generate fix
    
    Plugin->>FileSystem: Backup original file
    Plugin->>FileSystem: Apply fix
    
    Plugin->>Validator: Validate fix
    
    alt Fix Valid
        Validator-->>Plugin: Fix OK
        Plugin->>Git: Stage changes
        Plugin-->>ErrorEngine: Fix successful
    else Fix Invalid
        Validator-->>Plugin: Fix failed
        Plugin->>FileSystem: Restore backup
        Plugin-->>ErrorEngine: Fix failed
    end
```

---

## Error Metrics Tracked

| Metric | Purpose | Alert Threshold |
|--------|---------|----------------|
| **Error Rate** | Errors per hour | >10/hour |
| **Repeat Errors** | Same error recurring | >3 times |
| **Plugin Match Rate** | % errors matched by plugins | <80% |
| **Auto-Fix Success** | % fixes that work | <50% |
| **Escalation Rate** | % errors escalated | >20% |
| **Response Time** | Time to classify error | >5s |

---

## Integration with Core Engine

```mermaid
graph LR
    Executor[Step Executor] -->|Error| ErrorEngine[Error Engine]
    ErrorEngine -->|Classification| Executor
    
    Executor -->|Retry Decision| CircuitBreaker[Circuit Breaker]
    CircuitBreaker -->|Allow/Deny| Executor
    
    ErrorEngine -->|Diagnostics| DB[(Database)]
    ErrorEngine -->|Notifications| NotifyService[Notification Service]
    ErrorEngine -->|Metrics| Metrics[Metrics Service]
    
    PluginManager[Plugin Manager] --> ErrorEngine
    ErrorCache[Error Cache] --> ErrorEngine
    
    style ErrorEngine fill:#ff9800,stroke:#e65100,stroke-width:3px
```

---

## Configuration Example

```yaml
error_detection:
  # Plugin settings
  plugins:
    enabled: true
    directory: "error/plugins"
    auto_load: true
    
  # Error cache
  cache:
    enabled: true
    max_size: 1000
    ttl_seconds: 3600
    deduplicate: true
    
  # Severity thresholds
  severity:
    auto_fix_levels: [WARNING, ERROR]
    escalate_levels: [CRITICAL]
    suppress_levels: [INFO]
    
  # Notifications
  notifications:
    slack:
      enabled: true
      channel: "#pipeline-alerts"
      severity_threshold: ERROR
    
    email:
      enabled: true
      recipients: ["team@example.com"]
      severity_threshold: CRITICAL
      
    pagerduty:
      enabled: true
      severity_threshold: CRITICAL
      
  # Diagnostics
  diagnostics:
    collect_on_escalation: true
    save_logs: true
    max_log_lines: 100
    include_file_diffs: true
```

---

## Related Documentation

- [Task Lifecycle](./TASK_LIFECYCLE.md) - Task state machine
- [System Architecture](./SYSTEM_ARCHITECTURE.md) - Overall architecture
- [Plugin Development Guide](../development/PLUGIN_DEVELOPMENT.md) - Creating custom plugins

---

**Last Updated**: 2025-11-22  
**Maintainer**: Architecture Team  
**Implementation**: `error/engine/error_engine.py`, `error/plugins/`
