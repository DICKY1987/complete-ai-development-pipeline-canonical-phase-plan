# Registry System

**Purpose**: Placeholder for future registry system implementation - component registration, discovery, and lifecycle management.

## Overview

The `registry/` directory is currently **empty** but reserved for future implementation of a centralized component registry system. This system will provide service discovery, component registration, and lifecycle management for pipeline components.

## Status

**Current**: Placeholder directory (empty)

**Planned**: Component registry system similar to dependency injection containers or service registries.

## Proposed Architecture

### Component Types

The registry would manage:
- **Tools**: External tools (pytest, ruff, aider, etc.)
- **Plugins**: Error detection plugins
- **Adapters**: Tool adapters and bridges
- **Agents**: AI agents (Aider, Codex, Claude)
- **Workstreams**: Registered workstream bundles
- **Services**: Background services and daemons

### Registry Operations

**Registration**:
```python
from core.registry import ComponentRegistry

registry = ComponentRegistry()

# Register tool
registry.register_tool(
    name="pytest",
    executable="pytest",
    version="7.4.0",
    capabilities=["test", "coverage"],
    config_path="config/tool_profiles.json"
)

# Register plugin
registry.register_plugin(
    plugin_id="python_ruff",
    manifest_path="error/plugins/python_ruff/manifest.json",
    dependencies=["python_black_fix"]
)
```

**Discovery**:
```python
# Find all tools with specific capability
test_tools = registry.find_tools(capability="test")

# Get tool by name
pytest = registry.get_tool("pytest")

# List all plugins for file type
plugins = registry.get_plugins_for_extension(".py")
```

**Lifecycle Management**:
```python
# Initialize component
registry.initialize("pytest")

# Check health
status = registry.health_check("pytest")

# Shutdown component
registry.shutdown("pytest")
```

## Comparison with AIM+

**AIM+ (`aim/`)** provides tool environment management:
- Tool installation and versioning
- Environment health checks
- Path management
- API key management

**Registry (proposed)** would provide runtime component management:
- Component discovery and registration
- Lifecycle management (init, health, shutdown)
- Dependency resolution
- Service orchestration

**Relationship**: AIM ensures tools are installed; Registry manages their runtime usage.

## Design Considerations

### 1. Registration Patterns

**Static Registration** (via config files):
```yaml
# registry/tools.yaml
tools:
  - name: pytest
    executable: pytest
    capabilities: [test, coverage]
    
  - name: ruff
    executable: ruff
    capabilities: [lint, format]
```

**Dynamic Registration** (runtime):
```python
# In plugin __init__.py
def register(registry):
    registry.register_plugin(
        plugin_id="my_plugin",
        capabilities=["lint"],
        handler=MyPluginHandler()
    )
```

### 2. Dependency Resolution

**Topological Ordering**:
```python
# Plugins with dependencies
registry.register("black", dependencies=[])
registry.register("isort", dependencies=[])
registry.register("ruff", dependencies=["black", "isort"])

# Resolve execution order
order = registry.resolve_dependencies()
# Result: ["black", "isort", "ruff"]
```

**Circular Dependency Detection**:
```python
try:
    registry.register("plugin_a", dependencies=["plugin_b"])
    registry.register("plugin_b", dependencies=["plugin_a"])
except CircularDependencyError as e:
    print(f"Circular dependency: {e}")
```

### 3. Health Monitoring

**Component Health Checks**:
```python
class ToolHealthMonitor:
    def check_health(self, tool_name: str) -> HealthStatus:
        tool = registry.get_tool(tool_name)
        
        # Check executable exists
        if not shutil.which(tool.executable):
            return HealthStatus.UNAVAILABLE
        
        # Check version
        version = self._get_version(tool.executable)
        if version != tool.expected_version:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
```

**Automated Health Checks**:
```python
# Periodic health checks
scheduler.schedule(
    interval=60,  # seconds
    task=registry.health_check_all
)
```

### 4. Event System

**Component Lifecycle Events**:
```python
# Subscribe to events
registry.on("component.registered", handle_registration)
registry.on("component.initialized", handle_initialization)
registry.on("component.failed", handle_failure)

def handle_failure(component_name, error):
    logger.error(f"Component {component_name} failed: {error}")
    # Attempt recovery or notify user
```

## Potential Implementations

### Option 1: Lightweight Python Registry

**Advantages**:
- Simple, pure Python
- No external dependencies
- Easy to understand and maintain

**Implementation**:
```python
# registry/simple_registry.py
class ComponentRegistry:
    def __init__(self):
        self._components = {}
    
    def register(self, name, component):
        self._components[name] = component
    
    def get(self, name):
        return self._components.get(name)
    
    def list_all(self):
        return list(self._components.keys())
```

### Option 2: Plugin-Based Registry

**Advantages**:
- Extensible via plugins
- Follows existing plugin architecture
- Familiar pattern for developers

**Implementation**:
```python
# Uses existing PluginManager pattern
from error.engine.plugin_manager import PluginManager

class ComponentRegistry(PluginManager):
    def register_tool(self, tool_config):
        # Register as plugin with tool-specific manifest
        pass
```

### Option 3: Service Container Pattern

**Advantages**:
- Dependency injection support
- Lazy initialization
- Singleton management

**Implementation**:
```python
# registry/container.py
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register(self, name, factory, singleton=True):
        self._services[name] = {
            "factory": factory,
            "singleton": singleton
        }
    
    def get(self, name):
        if name in self._singletons:
            return self._singletons[name]
        
        service = self._services[name]
        instance = service["factory"]()
        
        if service["singleton"]:
            self._singletons[name] = instance
        
        return instance
```

## Integration Points

### With Existing Systems

**Tool Profiles** (`config/tool_profiles.json`):
```python
# Registry loads from tool profiles
registry = ComponentRegistry()
registry.load_from_config("config/tool_profiles.json")
```

**Plugin System** (`error/plugins/`):
```python
# Registry discovers plugins
from error.engine.plugin_manager import PluginManager

pm = PluginManager()
pm.discover()

for plugin_id, plugin in pm._plugins.items():
    registry.register_plugin(plugin_id, plugin)
```

**AIM+ Integration** (`aim/`):
```python
# Registry queries AIM for tool availability
from aim.bridge import get_tool_info

tool_info = get_tool_info("pytest")
if tool_info["available"]:
    registry.register_tool("pytest", tool_info)
```

## Migration Path

### Phase 1: Design and Specification
- Define registry API contracts
- Document component lifecycle
- Design event system
- Create registry schema

### Phase 2: Core Implementation
- Implement basic registry (Option 1)
- Add component registration
- Implement discovery methods
- Add health checking

### Phase 3: Integration
- Integrate with PluginManager
- Connect to AIM+ for tool info
- Update orchestrator to use registry
- Migrate tool profiles to registry

### Phase 4: Advanced Features
- Add dependency resolution
- Implement lifecycle events
- Add service container pattern
- Build monitoring dashboard

## Example Use Cases

### Use Case 1: Tool Discovery

**Goal**: Find all tools capable of running tests

```python
registry = ComponentRegistry()
test_tools = registry.find_tools(capability="test")
# Returns: ["pytest", "jest", "unittest"]
```

### Use Case 2: Plugin Ordering

**Goal**: Execute plugins in dependency order

```python
registry = ComponentRegistry()
plugins = registry.get_plugins_for_file("module.py")
# Returns: [black, isort, ruff, mypy] (in dependency order)
```

### Use Case 3: Health Monitoring

**Goal**: Check if all required tools are available

```python
registry = ComponentRegistry()
health = registry.health_check_all()

for tool, status in health.items():
    if status != "healthy":
        print(f"Warning: {tool} is {status}")
```

### Use Case 4: Service Lifecycle

**Goal**: Start/stop background services

```python
registry = ComponentRegistry()

# Start all services
registry.start_all_services()

# Graceful shutdown
registry.shutdown_all_services()
```

## Related Sections

- **AIM**: `aim/` - Tool environment management (installation, paths, health)
- **Error Plugins**: `error/plugins/` - Plugin system that registry would manage
- **Config**: `config/` - Configuration files that registry would load
- **Core Engine**: `core/engine/` - Orchestrator that would use registry

## Future Work

**When implementing registry**:
1. Create `registry/registry.py` with ComponentRegistry class
2. Add `registry/schema/` for component schemas
3. Implement `registry/loaders/` for config file loaders
4. Add `registry/monitors/` for health checking
5. Update `core/engine/orchestrator.py` to use registry
6. Migrate existing tool/plugin discovery to registry

**Documentation to create**:
- `registry/API.md` - API reference
- `registry/DESIGN.md` - Architecture decisions
- `registry/MIGRATION.md` - Migration guide from current system

## Temporary Workarounds

**Until registry is implemented**:
- Use `PluginManager` for plugin discovery
- Use `ToolsAdapter` with `tool_profiles.json` for tools
- Use AIM+ for tool availability checking
- Manual dependency management in plugin manifests

## See Also

- [AIM+ README](../aim/README.md) - Tool environment management
- [Plugin Manager](../error/engine/README.md#plugin-manager) - Current plugin discovery
- [Tool Profiles](../config/README.md#tool-profiles) - Current tool configuration
- [Orchestrator Guide](../docs/orchestrator_guide.md)
