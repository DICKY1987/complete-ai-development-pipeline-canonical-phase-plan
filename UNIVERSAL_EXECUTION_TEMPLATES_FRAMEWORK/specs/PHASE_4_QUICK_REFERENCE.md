# Phase 4 Quick Reference: AI Enhancement Features

**Version:** 1.0.0  
**Phase:** PH-04-AI-ENH  
**Status:** Planning

---

## 🎯 What Phase 4 Delivers

**Transform from:** Workflow orchestrator  
**Transform to:** Intelligent AI assistant that learns, adapts, and self-corrects

### 7 Major Capabilities

| Capability | What It Does | User Benefit |
|-----------|--------------|--------------|
| **AST Repository Map** | Compress codebase into signature-only view | 10x smaller context, no hallucinations |
| **GraphRAG** | Semantic code understanding via knowledge graphs | "What breaks if I change this?" |
| **Reflexion Loops** | Autonomous error fixing with retry | AI fixes its own bugs automatically |
| **RAPTOR Index** | Hierarchical code summaries (system→module→file→line) | Answer arch questions without reading code |
| **Episodic Memory** | Learn from successful edits | Remember project conventions over time |
| **HyDE Search** | Better semantic search via hypothetical code | Find code by what it does, not keywords |
| **Terminal State** | Use shell history as context | Debug without copy-paste |

---

## 📦 Week-by-Week Deliverables

### Week 1-2: AST Foundation
```
✅ WS-04-01A: Tree-sitter parsers (Python, JS, TS, MD)
✅ WS-04-01B: Repository mapper (signature extraction)
✅ WS-04-01C: PageRank module importance ranking
```

**Output:** `AST_REPOSITORY_MAP.yaml` - Your entire codebase in < 5K tokens

### Week 3-4: Semantic Understanding
```
✅ WS-04-02A: Knowledge graph (functions, classes, relationships)
✅ WS-04-02B: GraphRAG query engine
✅ WS-04-02C: RAPTOR hierarchical indexing
✅ WS-04-02D: Vector search infrastructure
```

**Output:** `knowledge_graph.db` + semantic search API

### Week 5-6: Autonomous Intelligence
```
✅ WS-04-03A: Reflexion self-correction loops
✅ WS-04-03B: Episodic memory system
✅ WS-04-03C: HyDE search enhancement
✅ WS-04-03D: Terminal state integration
✅ WS-04-03E: Production integration + testing
```

**Output:** Fully autonomous AI assistant

---

## 🚀 Quick Start (After Phase 4 Complete)

### 1. Generate AST Repository Map

```bash
# One-time setup
python scripts/generate_ast_map.py

# Output: AST_REPOSITORY_MAP.yaml (< 5K tokens)
# Inject into AI context for better understanding
```

### 2. Query the Knowledge Graph

```python
from core.semantic.graphrag import GraphRAG

graph = GraphRAG()

# What calls this function?
graph.query("callers_of('init_db')")
→ ['orchestrator.setup', 'run_workstream.main']

# Impact analysis
graph.query("impact_of_change('core.state.db.create_run')")
→ ['orchestrator.execute_step', 'error_engine.log_error']

# Dependency chain
graph.query("path_between('user_request', 'database_write')")
→ [request_handler → validator → orchestrator → db]
```

### 3. Enable Reflexion Loops

```python
from core.autonomous.reflexion import ReflexionExecutor

# Traditional execution (fails and gives up)
executor.run_task(task)

# Reflexion execution (retries with self-correction)
reflexion = ReflexionExecutor(max_iterations=3)
reflexion.run_task(task)
# → Captures errors, analyzes, fixes, retries automatically
```

### 4. Search with HyDE

```python
from core.semantic.hyde_search import HyDESearch

search = HyDESearch()

# Natural language query
results = search.find("Where do we handle PDF export?")
→ ['utils/export.py:generate_pdf()', 'engine/adapters/pdf.py']

# Conceptual search
results = search.find("database initialization logic")
→ ['core/state/db.py:init_db()', 'core/state/schema.py:create_tables()']
```

### 5. Use Episodic Memory

```python
from core.memory.episodic_memory import EpisodicMemory

memory = EpisodicMemory()

# Recall similar past tasks
context = memory.recall("Add new API endpoint")
→ "Last 3 times: edited api/routes.py and tests/test_api.py, used snake_case"

# AI automatically follows project conventions without being told
```

### 6. Auto-Debug from Terminal

```bash
# Run your failing test
pytest tests/
# ERROR: NameError: name 'init_db' is not defined

# Auto-debug (no copy-paste needed!)
python scripts/debug_auto.py
# AI reads terminal state and suggests fix:
# "Missing import. Add 'from core.state.db import init_db' to test_db.py:1"
```

---

## 📊 Performance Benchmarks

| Operation | Target | Notes |
|-----------|--------|-------|
| AST map generation | < 10s | Entire codebase |
| GraphRAG query | < 100ms | Single traversal |
| Semantic search | < 500ms | Per query |
| Reflexion loop | < 5min | Autonomous fix |
| Memory recall | < 50ms | Find similar tasks |

---

## 🎓 Learning Curve

### For Developers

**Easy (5 min):**
- Use AST repository map in prompts
- Query knowledge graph for dependencies

**Medium (30 min):**
- Enable reflexion loops for autonomous retry
- Use HyDE search for code discovery

**Advanced (2 hours):**
- Add custom episodic memory patterns
- Extend knowledge graph with custom relationships

### For AI Agents

**Automatic:**
- AST map injected into context automatically
- GraphRAG queries available as tool
- Episodic memory recalled on similar tasks
- Terminal state captured for debugging

**No configuration needed** - Phase 4 features integrate seamlessly

---

## 💰 Cost Model

### One-Time Costs
- **Development:** ~$100 (AI-assisted coding)
- **Initial indexing:** ~$20 (embeddings for codebase)

### Ongoing Costs
- **Embedding updates:** ~$2/week (as code changes)
- **Reflexion loops:** ~$0.50/fix (3 iterations avg)
- **Memory storage:** $0 (SQLite, local)

### Cost Savings
- **Reduced context size:** Save 90% on tokens (AST map vs full dump)
- **Autonomous fixes:** Save dev time on simple errors
- **Better search:** Find code faster, less back-and-forth

---

## 🔧 Configuration

### Feature Flags (Gradual Rollout)

```yaml
# config/ai_enhancement.yaml
features:
  ast_repository_map:
    enabled: true
    auto_inject_context: true
  
  graphrag:
    enabled: true
    cache_queries: true
    cache_ttl_seconds: 3600
  
  reflexion:
    enabled: true
    max_iterations: 3
    timeout_seconds: 300
  
  raptor:
    enabled: true
    levels: 5  # 0=code, 1=function, 2=file, 3=module, 4=system
  
  episodic_memory:
    enabled: true
    max_memories: 1000
    similarity_threshold: 0.7
  
  hyde_search:
    enabled: true
    use_local_embeddings: false  # Set true to avoid OpenAI costs
  
  terminal_state:
    enabled: true
    capture_lines: 100
    capture_env_vars: true
```

---

## 🐛 Troubleshooting

### AST Map Too Large
```bash
# Reduce to only public APIs
python scripts/generate_ast_map.py --public-only

# Exclude tests
python scripts/generate_ast_map.py --exclude tests/
```

### GraphRAG Queries Slow
```bash
# Rebuild indexes
python scripts/rebuild_graph_indexes.py

# Check SQLite indexes
sqlite3 .worktrees/knowledge_graph.db ".schema"
```

### Reflexion Loops Taking Too Long
```yaml
# Reduce max iterations
reflexion:
  max_iterations: 2  # Down from 3
  timeout_seconds: 120  # Down from 300
```

### Embeddings Too Expensive
```yaml
# Use local embeddings instead of OpenAI
hyde_search:
  use_local_embeddings: true  # sentence-transformers
```

---

## 📚 Advanced Usage

### Custom Knowledge Graph Relationships

```python
from core.semantic.knowledge_graph import KnowledgeGraph

graph = KnowledgeGraph()

# Add custom relationship
graph.add_edge(
    source="UserService.create_user",
    target="EmailService.send_welcome",
    relationship="triggers",
    metadata={"async": True}
)

# Query custom relationships
graph.query("what_triggers('EmailService.send_welcome')")
→ ['UserService.create_user (async)']
```

### Custom Episodic Memory Patterns

```python
from core.memory.episodic_memory import EpisodicMemory

memory = EpisodicMemory()

# Store custom pattern
memory.store({
    "pattern": "API endpoint creation",
    "files": ["api/routes.py", "tests/test_api.py"],
    "conventions": {
        "naming": "snake_case",
        "http_method_order": ["GET", "POST", "PUT", "DELETE"]
    }
})

# Recall will now include your custom conventions
```

---

## 🎯 Success Criteria

**Phase 4 is complete when:**

- [ ] All 150+ tests passing
- [ ] AST map reduces context by 10x
- [ ] GraphRAG answers "what breaks if I change X?" correctly
- [ ] Reflexion fixes 70%+ of simple errors autonomously
- [ ] HyDE improves search recall by 30%+
- [ ] Episodic memory recalls relevant past edits
- [ ] Terminal state integration eliminates error copy-paste
- [ ] Zero performance regression on existing workflows

---

## 🔗 Related Documentation

- [Phase 4 Full Plan](PHASE_4_AI_ENHANCEMENT_PLAN.md)
- [UET Framework README](../README.md)
- [Phase 3 Completion](PHASE_3_COMPLETION_REPORT.md)
- [Research References](PHASE_4_AI_ENHANCEMENT_PLAN.md#references)

---

**Last Updated:** 2025-11-22  
**Maintainer:** Phase 4 Team  
**Feedback:** Open issue with tag `phase-4`
