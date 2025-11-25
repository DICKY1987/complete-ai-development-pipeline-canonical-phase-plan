# Specification Integration

**Purpose**: Visualization of the OpenSpec to Workstream conversion flow, specification resolution, and change proposal workflow.

---

## OpenSpec → Workstream Conversion Flow

```mermaid
flowchart TD
    Start[OpenSpec File] --> Parse[Parse YAML]
    
    Parse --> Validate{Valid<br/>Schema?}
    
    Validate -->|Yes| Index[Add to Spec Index]
    Validate -->|No| Error1[Validation Error]
    
    Index --> Resolve[Resolve Dependencies]
    
    Resolve --> CheckDeps{Dependencies<br/>Exist?}
    
    CheckDeps -->|Yes| LoadDeps[Load Dependencies]
    CheckDeps -->|No| Error2[Missing Dependencies]
    
    LoadDeps --> CheckCircular{Circular<br/>Dependencies?}
    
    CheckCircular -->|No| BuildDAG[Build Dependency DAG]
    CheckCircular -->|Yes| Error3[Circular Dependency]
    
    BuildDAG --> Convert[Convert to Workstream]
    
    Convert --> GenerateSteps[Generate Steps]
    GenerateSteps --> AssignTools[Assign Tool Profiles]
    AssignTools --> SetDependencies[Set Step Dependencies]
    SetDependencies --> AddMetadata[Add Metadata]
    
    AddMetadata --> ValidateWS{Workstream<br/>Valid?}
    
    ValidateWS -->|Yes| SaveWS[Save Workstream JSON]
    ValidateWS -->|No| Error4[Invalid Workstream]
    
    SaveWS --> LinkCCPM[Link to CCPM Issue]
    LinkCCPM --> Complete[Conversion Complete]
    
    style Complete fill:#4caf50,stroke:#2e7d32,color:#fff
    style Error1 fill:#f44336,stroke:#c62828,color:#fff
    style Error2 fill:#f44336,stroke:#c62828,color:#fff
    style Error3 fill:#f44336,stroke:#c62828,color:#fff
    style Error4 fill:#f44336,stroke:#c62828,color:#fff
```

---

## Specification Architecture

```mermaid
graph TB
    subgraph "Specification Content"
        OpenSpecFiles[OpenSpec YAML Files]
        Templates[Spec Templates]
        ChangeProposals[Change Proposals]
    end
    
    subgraph "Processing Tools"
        Parser[OpenSpec Parser]
        Indexer[Spec Indexer]
        Resolver[Dependency Resolver]
        Validator[Schema Validator]
        Renderer[Spec Renderer]
    end
    
    subgraph "Generated Artifacts"
        SpecIndex[specs_index.json]
        SpecMapping[specs_mapping.json]
        Workstreams[Workstream JSON Files]
    end
    
    subgraph "Bridge Layer"
        Converter[OpenSpec → Workstream Converter]
        ChangeTracker[Change Tracker]
        VersionManager[Version Manager]
    end
    
    subgraph "Integration"
        CoreEngine[Core Workstream Engine]
        CCPM[CCPM/PM Tools]
        Git[Git Repository]
    end
    
    OpenSpecFiles --> Parser
    Templates --> Parser
    ChangeProposals --> ChangeTracker
    
    Parser --> Validator
    Validator --> Indexer
    Indexer --> SpecIndex
    Indexer --> SpecMapping
    
    Parser --> Resolver
    Resolver --> Converter
    
    Converter --> Workstreams
    Converter --> VersionManager
    
    Workstreams --> CoreEngine
    ChangeTracker --> CCPM
    VersionManager --> Git
    
    SpecIndex --> Renderer
    Renderer --> Documentation[Generated Docs]
    
    style Parser fill:#ff9800,stroke:#e65100,stroke-width:3px
    style Converter fill:#2196f3,stroke:#0d47a1,stroke-width:3px,color:#fff
    style SpecIndex fill:#8bc34a,stroke:#558b2f
    style Workstreams fill:#8bc34a,stroke:#558b2f
```

---

## Spec Resolution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Parser
    participant Index
    participant Resolver
    participant FileSystem
    participant Converter
    
    User->>Parser: Load spec://feature/auth
    Parser->>Index: Lookup spec URI
    Index-->>Parser: Found: specifications/content/features/auth.yaml
    
    Parser->>FileSystem: Read file
    FileSystem-->>Parser: YAML content
    
    Parser->>Parser: Parse YAML
    Parser->>Parser: Extract dependencies
    
    Note over Parser: Dependencies found:<br/>- spec://common/user<br/>- spec://common/database
    
    Parser->>Resolver: Resolve dependencies
    
    loop For each dependency
        Resolver->>Index: Lookup dependency URI
        Index-->>Resolver: File path
        Resolver->>FileSystem: Read dependency
        FileSystem-->>Resolver: Dependency content
        Resolver->>Resolver: Parse dependency
    end
    
    Resolver-->>Parser: All dependencies resolved
    
    Parser->>Converter: Convert to workstream
    Converter->>Converter: Generate steps
    Converter-->>Parser: Workstream JSON
    
    Parser-->>User: Workstream ready
```

---

## Dependency Resolution (DAG)

```mermaid
graph TD
    FeatureAuth[spec://feature/auth] --> CommonUser[spec://common/user]
    FeatureAuth --> CommonDB[spec://common/database]
    
    CommonUser --> BaseEntity[spec://base/entity]
    CommonDB --> BaseEntity
    
    FeaturePayment[spec://feature/payment] --> CommonUser
    FeaturePayment --> CommonPaymentGateway[spec://common/payment-gateway]
    
    FeatureNotification[spec://feature/notification] --> CommonUser
    FeatureNotification --> CommonEmail[spec://common/email]
    
    CommonEmail --> BaseConfig[spec://base/config]
    CommonPaymentGateway --> BaseConfig
    
    style FeatureAuth fill:#2196f3,stroke:#0d47a1,color:#fff
    style FeaturePayment fill:#2196f3,stroke:#0d47a1,color:#fff
    style FeatureNotification fill:#2196f3,stroke:#0d47a1,color:#fff
    style CommonUser fill:#ff9800,stroke:#e65100
    style CommonDB fill:#ff9800,stroke:#e65100
    style BaseEntity fill:#4caf50,stroke:#2e7d32,color:#fff
    style BaseConfig fill:#4caf50,stroke:#2e7d32,color:#fff
```

---

## Change Proposal Workflow

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create Proposal
    
    DRAFT --> REVIEW: Submit for Review
    DRAFT --> CANCELLED: Cancel
    
    REVIEW --> APPROVED: Approve
    REVIEW --> REJECTED: Reject
    REVIEW --> DRAFT: Request Changes
    
    APPROVED --> IN_PROGRESS: Convert to Workstream
    
    IN_PROGRESS --> TESTING: Workstream Complete
    IN_PROGRESS --> FAILED: Workstream Failed
    
    TESTING --> VERIFIED: Tests Pass
    TESTING --> IN_PROGRESS: Tests Fail
    
    VERIFIED --> MERGED: Merge Changes
    
    MERGED --> [*]
    REJECTED --> [*]
    CANCELLED --> [*]
    FAILED --> [*]
    
    note right of DRAFT
        Author edits proposal
        Dependencies identified
        Impact assessed
    end note
    
    note right of REVIEW
        Team reviews
        CCPM linked
        Gate approval
    end note
    
    note right of IN_PROGRESS
        Workstream executing
        Progress tracked
        Issues logged
    end note
```

---

## Specification Index Structure

```mermaid
graph TD
    subgraph "specs_index.json"
        Index[Root Index]
        
        Index --> Features[features/]
        Index --> Common[common/]
        Index --> Base[base/]
        Index --> Archived[archived/]
        
        Features --> Auth[auth.yaml]
        Features --> Payment[payment.yaml]
        Features --> Notification[notification.yaml]
        
        Common --> User[user.yaml]
        Common --> Database[database.yaml]
        Common --> Email[email.yaml]
        
        Base --> Entity[entity.yaml]
        Base --> Config[config.yaml]
        
        Auth --> AuthMeta[Metadata:<br/>- URI<br/>- Dependencies<br/>- Version<br/>- Status]
        User --> UserMeta[Metadata:<br/>- URI<br/>- Dependencies<br/>- Version<br/>- Status]
    end
    
    style Index fill:#ff9800,stroke:#e65100,stroke-width:3px
    style Features fill:#2196f3,stroke:#0d47a1,color:#fff
    style Common fill:#8bc34a,stroke:#558b2f
    style Base fill:#4caf50,stroke:#2e7d32,color:#fff
```

---

## Spec URI Resolution

```mermaid
flowchart LR
    URI[spec://feature/auth] --> Parse[Parse URI]
    
    Parse --> Extract{Extract<br/>Components}
    
    Extract --> Domain[Domain: feature]
    Extract --> Path[Path: auth]
    Extract --> Version[Version: latest]
    
    Domain --> BuildPath[Build File Path]
    Path --> BuildPath
    
    BuildPath --> Construct[specifications/content/features/auth.yaml]
    
    Construct --> Check{File<br/>Exists?}
    
    Check -->|Yes| Load[Load File]
    Check -->|No| Error[Resolution Error]
    
    Load --> Return[Return Spec]
    
    style Return fill:#4caf50,stroke:#2e7d32,color:#fff
    style Error fill:#f44336,stroke:#c62828,color:#fff
```

**URI Format**: `spec://<domain>/<path>[:<version>]`

**Examples**:
- `spec://feature/auth` → `specifications/content/features/auth.yaml`
- `spec://common/user:v2` → `specifications/content/common/user.v2.yaml`
- `spec://base/entity` → `specifications/content/base/entity.yaml`

---

## Workstream Generation from Spec

```mermaid
sequenceDiagram
    participant Spec as OpenSpec
    participant Converter
    participant TemplateEngine
    participant StepGenerator
    participant Workstream
    
    Spec->>Converter: Load specification
    Converter->>Converter: Parse structure
    
    Converter->>TemplateEngine: Get workstream template
    TemplateEngine-->>Converter: Base template
    
    loop For each task in spec
        Converter->>StepGenerator: Generate step
        StepGenerator->>StepGenerator: Map to tool profile
        StepGenerator->>StepGenerator: Set dependencies
        StepGenerator->>StepGenerator: Add acceptance tests
        StepGenerator-->>Converter: Step definition
    end
    
    Converter->>Workstream: Assemble workstream
    Workstream->>Workstream: Add metadata
    Workstream->>Workstream: Link CCPM issue
    Workstream->>Workstream: Set gate approval
    
    Workstream-->>Converter: Complete workstream JSON
```

---

## Spec Version Management

```mermaid
graph LR
    V1[auth.v1.yaml] -->|Superseded| V2[auth.v2.yaml]
    V2 -->|Superseded| V3[auth.v3.yaml]
    V3 -->|Current| Latest[auth.yaml]
    
    Latest -.->|Symlink| V3
    
    V1 --> Archived1[archived/auth.v1.yaml]
    
    subgraph "Active Versions"
        V2
        V3
        Latest
    end
    
    subgraph "Archived"
        Archived1
    end
    
    style Latest fill:#4caf50,stroke:#2e7d32,color:#fff
    style V3 fill:#8bc34a,stroke:#558b2f
    style V2 fill:#ff9800,stroke:#e65100
    style V1 fill:#9e9e9e,stroke:#424242
```

---

## Spec Inheritance & Templates

```mermaid
graph TD
    BaseTemplate[base-spec.yaml] --> FeatureTemplate[feature-template.yaml]
    BaseTemplate --> CommonTemplate[common-template.yaml]
    
    FeatureTemplate --> AuthSpec[auth.yaml]
    FeatureTemplate --> PaymentSpec[payment.yaml]
    
    CommonTemplate --> UserSpec[user.yaml]
    CommonTemplate --> DatabaseSpec[database.yaml]
    
    AuthSpec -.->|Inherits| FeatureTemplate
    AuthSpec -.->|Inherits| BaseTemplate
    
    style BaseTemplate fill:#4caf50,stroke:#2e7d32,color:#fff
    style FeatureTemplate fill:#2196f3,stroke:#0d47a1,color:#fff
    style CommonTemplate fill:#ff9800,stroke:#e65100
```

**Inheritance Chain**:
```yaml
# auth.yaml inherits from feature-template.yaml
extends: spec://templates/feature

# feature-template.yaml inherits from base
extends: spec://templates/base

# Effective configuration is merged:
# base → feature-template → auth
```

---

## Change Impact Analysis

```mermaid
graph TB
    Change[Spec Change] --> Analyze[Impact Analysis]
    
    Analyze --> FindDependents[Find Dependent Specs]
    
    FindDependents --> Dep1[feature/payment]
    FindDependents --> Dep2[feature/notification]
    FindDependents --> Dep3[common/database]
    
    Dep1 --> CheckBreaking1{Breaking<br/>Change?}
    Dep2 --> CheckBreaking2{Breaking<br/>Change?}
    Dep3 --> CheckBreaking3{Breaking<br/>Change?}
    
    CheckBreaking1 -->|Yes| Flag1[⚠ Requires Update]
    CheckBreaking1 -->|No| OK1[✓ Compatible]
    
    CheckBreaking2 -->|Yes| Flag2[⚠ Requires Update]
    CheckBreaking2 -->|No| OK2[✓ Compatible]
    
    CheckBreaking3 -->|Yes| Flag3[⚠ Requires Update]
    CheckBreaking3 -->|No| OK3[✓ Compatible]
    
    Flag1 --> Report[Impact Report]
    Flag2 --> Report
    Flag3 --> Report
    OK1 --> Report
    OK2 --> Report
    OK3 --> Report
    
    style Flag1 fill:#ff9800,stroke:#e65100
    style Flag2 fill:#ff9800,stroke:#e65100
    style Flag3 fill:#ff9800,stroke:#e65100
    style OK1 fill:#4caf50,stroke:#2e7d32,color:#fff
    style OK2 fill:#4caf50,stroke:#2e7d32,color:#fff
    style OK3 fill:#4caf50,stroke:#2e7d32,color:#fff
```

---

## Spec Validation Pipeline

```mermaid
flowchart TD
    Start[Spec File] --> SchemaValidation{Schema<br/>Valid?}
    
    SchemaValidation -->|No| Error1[Schema Error]
    SchemaValidation -->|Yes| URIValidation{URIs<br/>Valid?}
    
    URIValidation -->|No| Error2[Invalid URI]
    URIValidation -->|Yes| DepValidation{Dependencies<br/>Exist?}
    
    DepValidation -->|No| Error3[Missing Dependency]
    DepValidation -->|Yes| CircularCheck{Circular<br/>Dependency?}
    
    CircularCheck -->|Yes| Error4[Circular Dependency]
    CircularCheck -->|No| ConsistencyCheck{Data<br/>Consistent?}
    
    ConsistencyCheck -->|No| Warning[Consistency Warning]
    ConsistencyCheck -->|Yes| Success[Validation Pass]
    
    Warning --> Success
    
    style Success fill:#4caf50,stroke:#2e7d32,color:#fff
    style Error1 fill:#f44336,stroke:#c62828,color:#fff
    style Error2 fill:#f44336,stroke:#c62828,color:#fff
    style Error3 fill:#f44336,stroke:#c62828,color:#fff
    style Error4 fill:#f44336,stroke:#c62828,color:#fff
    style Warning fill:#ff9800,stroke:#e65100
```

---

## CCPM Integration

```mermaid
sequenceDiagram
    participant Spec as OpenSpec
    participant Bridge as Spec Bridge
    participant Workstream
    participant CCPM as CCPM System
    participant DB as Database
    
    Spec->>Bridge: Create change proposal
    Bridge->>CCPM: Create issue
    CCPM-->>Bridge: Issue ID: PROJ-123
    
    Bridge->>DB: Save mapping
    Note over Bridge,DB: Spec ID ↔ CCPM Issue
    
    Bridge->>Workstream: Convert to workstream
    Workstream->>Workstream: Add CCPM issue link
    
    Note over Workstream: Workstream JSON:<br/>{<br/>  "ccpm_issue": "PROJ-123"<br/>}
    
    Workstream->>CCPM: Start work
    CCPM-->>Workstream: Status: IN_PROGRESS
    
    loop During execution
        Workstream->>CCPM: Update progress
    end
    
    Workstream->>CCPM: Complete
    CCPM->>CCPM: Update issue status
    CCPM-->>Spec: Work complete
```

---

## Specification Metrics

| Metric | Purpose | Typical Value |
|--------|---------|---------------|
| **Total Specs** | Number of specifications | 50-200 |
| **Dependency Depth** | Max dependency chain length | 3-5 levels |
| **Conversion Time** | Spec → Workstream time | <2s |
| **Resolution Success** | % URIs resolved successfully | >99% |
| **Change Frequency** | Specs changed per week | 5-10 |
| **Breaking Changes** | % changes that break dependents | <5% |

---

## Directory Structure

```
specifications/
├── content/              # Specification YAML files
│   ├── features/        # Feature specifications
│   │   ├── auth.yaml
│   │   ├── payment.yaml
│   │   └── notification.yaml
│   ├── common/          # Common/shared specs
│   │   ├── user.yaml
│   │   ├── database.yaml
│   │   └── email.yaml
│   ├── base/            # Base templates
│   │   ├── entity.yaml
│   │   └── config.yaml
│   └── archived/        # Archived versions
│       └── auth.v1.yaml
│
├── changes/             # Change proposals
│   ├── CP-001-add-2fa.yaml
│   └── CP-002-payment-refactor.yaml
│
├── tools/               # Processing tools
│   ├── indexer/         # Spec indexing
│   ├── resolver/        # Dependency resolution
│   ├── guard/           # Validation
│   ├── patcher/         # Spec updates
│   └── renderer/        # Documentation generation
│
└── bridge/              # OpenSpec ↔ Workstream bridge
    ├── converter.py
    ├── change_tracker.py
    └── version_manager.py
```

---

## Configuration Example

```yaml
# Specification configuration
specifications:
  # Content location
  content_dir: "specifications/content"
  changes_dir: "specifications/changes"
  
  # Index settings
  index:
    auto_generate: true
    output_file: "specifications/specs_index.json"
    include_archived: false
    
  # Resolution
  resolution:
    cache_enabled: true
    cache_ttl: 3600
    max_depth: 10
    
  # Conversion
  conversion:
    default_tool_profile: "aider-python"
    auto_generate_tests: true
    validate_workstream: true
    
  # Version management
  versioning:
    enabled: true
    format: "v{major}.{minor}"
    auto_archive: true
    
  # CCPM integration
  ccpm:
    enabled: true
    auto_create_issues: true
    sync_status: true
    base_url: "https://ccpm.example.com"
```

---

## Related Documentation

- [System Architecture](./SYSTEM_ARCHITECTURE.md) - Overall system design
- [OpenSpec Format](../../openspec/README.md) - Specification format details
- [Workstream Schema](../../schema/workstream.schema.json) - Workstream JSON schema

---

**Last Updated**: 2025-11-22  
**Maintainer**: Architecture Team  
**Implementation**: `specifications/tools/`, `specifications/bridge/`
