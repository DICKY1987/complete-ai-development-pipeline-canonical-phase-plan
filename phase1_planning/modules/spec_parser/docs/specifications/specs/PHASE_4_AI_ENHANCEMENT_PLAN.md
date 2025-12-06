---
doc_id: DOC-GUIDE-PHASE-4-AI-ENHANCEMENT-PLAN-MD-001
---

# Phase 4: AI Enhancement - Advanced Codebase Intelligence

**Created:** 2025-11-22
**Phase ID:** PH-04-AI-ENH
**Estimated Duration:** 6-8 weeks
**Prerequisites:** Phase 3 Complete (Orchestration Engine)
**Status:** Planning

---

## Executive Summary

This phase implements cutting-edge AI-assisted development techniques to enhance the pipeline with:
- **AST-based repository mapping** (Tree-sitter + PageRank)
- **GraphRAG** for semantic code understanding
- **Reflexion loops** for autonomous error correction
- **RAPTOR** for hierarchical code indexing
- **Episodic memory** for learning from past edits
- **HyDE** for improved semantic search
- **Terminal state integration** for context-aware debugging

**Business Value:** Transform from a workflow orchestrator into an intelligent development assistant that learns, adapts, and self-corrects.

---

## Phase Overview

### Phase Structure (6 Weeks)

```
Week 1-2: Foundation (AST Infrastructure)
├── WS-04-01A: Tree-sitter Integration
├── WS-04-01B: AST-Based Repository Mapping
└── WS-04-01C: PageRank Module Ranking

Week 3-4: Semantic Understanding (GraphRAG + RAPTOR)
├── WS-04-02A: Knowledge Graph Construction
├── WS-04-02B: GraphRAG Query Engine
├── WS-04-02C: RAPTOR Hierarchical Indexing
└── WS-04-02D: Semantic Search Infrastructure

Week 5-6: Autonomous Intelligence (Reflexion + Memory)
├── WS-04-03A: Reflexion Loop Framework
├── WS-04-03B: Episodic Memory System
├── WS-04-03C: HyDE Search Enhancement
├── WS-04-03D: Terminal State Integration
└── WS-04-03E: Production Integration & Testing
```

---

## Week 1-2: AST Foundation

### WS-04-01A: Tree-sitter Integration

**Goal:** Add Tree-sitter parser support for Python, JavaScript, TypeScript, and Markdown.

**Deliverables:**
- [ ] `core/ast/parser.py` - Tree-sitter wrapper
- [ ] `core/ast/languages/` - Language-specific parsers (Python, JS, TS, MD)
- [ ] `core/ast/extractors.py` - Extract classes, functions, imports, docstrings
- [ ] `tests/ast/test_parser.py` - 20+ tests for each language
- [ ] `requirements.txt` - Add tree-sitter dependencies

**Acceptance Criteria:**
```python
# Can parse any Python file and extract structure
parser = ASTParser("python")
tree = parser.parse_file("core/state/db.py")
functions = tree.extract_functions()
assert "init_db" in [f.name for f in functions]
```

**Estimated Effort:** 1 week
**Tool:** Codex (implementation) + pytest (validation)
**Cost:** ~$8

---

### WS-04-01B: AST-Based Repository Mapping

**Goal:** Generate compressed repository maps showing only signatures (no implementation).

**Deliverables:**
- [ ] `core/ast/repository_mapper.py` - Repository-wide AST analysis
- [ ] `core/ast/signature_extractor.py` - Strip implementations, keep signatures
- [ ] `core/ast/import_graph.py` - Build import dependency graph
- [ ] `scripts/generate_ast_map.py` - CLI to generate maps
- [ ] `docs/AST_REPOSITORY_MAP.md` - Auto-generated architecture overview
- [ ] `tests/ast/test_repository_mapper.py` - 15+ tests

**Output Format:**
```yaml
# AST_REPOSITORY_MAP.yaml
modules:
  - path: "core/state/db.py"
    signatures:
      - "def init_db(path: str) -> None"
      - "def create_run(...) -> int"
      - "class RunState(Enum)"
    imports:
      - "import sqlite3"
      - "from pathlib import Path"
    imports_from:
      - "core.state.schema"
```

**Acceptance Criteria:**
- Map generated in < 10 seconds for entire codebase
- Token count < 5,000 for entire architecture (10x compression)
- Includes all public APIs, excludes private implementation

**Estimated Effort:** 1 week
**Tool:** Codex + Aider (implementation) + pytest
**Cost:** ~$10

---

### WS-04-01C: PageRank Module Ranking

**Goal:** Use PageRank algorithm to identify central/most-important modules.

**Deliverables:**
- [ ] `core/ast/pagerank.py` - PageRank implementation for code graphs
- [ ] `core/ast/centrality_analyzer.py` - Identify critical modules
- [ ] `scripts/analyze_module_importance.py` - CLI tool
- [ ] `docs/MODULE_IMPORTANCE_RANKING.md` - Auto-generated ranking report
- [ ] `tests/ast/test_pagerank.py` - 12+ tests

**Output:**
```yaml
# MODULE_IMPORTANCE_RANKING.yaml
top_modules:
  - module: "core.state.db"
    score: 0.142
    reason: "Central state management, imported by 23 modules"
  - module: "core.engine.orchestrator"
    score: 0.089
    reason: "Primary execution entry point, 15 dependencies"
```

**Acceptance Criteria:**
- Correctly identifies `core.state.db` as most central module
- Ranks modules by architectural importance
- Updates when codebase changes

**Estimated Effort:** 3 days
**Tool:** Codex (algorithm) + pytest
**Cost:** ~$5

---

## Week 3-4: Semantic Understanding

### WS-04-02A: Knowledge Graph Construction

**Goal:** Build a semantic knowledge graph of code relationships.

**Deliverables:**
- [ ] `core/semantic/knowledge_graph.py` - Graph data structure
- [ ] `core/semantic/graph_builder.py` - Construct graphs from AST
- [ ] `core/semantic/relationships.py` - Relationship types (calls, imports, inherits, modifies)
- [ ] `schema/knowledge_graph.schema.json` - Graph schema
- [ ] `.worktrees/knowledge_graph.db` - SQLite storage (nodes + edges)
- [ ] `tests/semantic/test_knowledge_graph.py` - 25+ tests

**Graph Schema:**
```python
# Nodes: functions, classes, modules, variables
# Edges: calls, imports, inherits, modifies, depends_on

# Example query:
"If I change auth.validate_token(), what breaks downstream?"
→ Traverse "calls" edges to find all dependents
```

**Acceptance Criteria:**
- Graph includes all functions/classes in codebase
- Can traverse from any node to its dependencies
- Persists across runs (SQLite storage)

**Estimated Effort:** 1 week
**Tool:** Codex + Aider
**Cost:** ~$12

---

### WS-04-02B: GraphRAG Query Engine

**Goal:** Enable impact analysis queries via graph traversal.

**Deliverables:**
- [ ] `core/semantic/graphrag.py` - Query engine
- [ ] `core/semantic/traversal.py` - Graph traversal algorithms
- [ ] `core/semantic/impact_analyzer.py` - Change impact analysis
- [ ] `scripts/analyze_impact.py` - CLI for impact queries
- [ ] `tests/semantic/test_graphrag.py` - 20+ tests

**Example Queries:**
```python
# What functions call this one?
graphrag.query("callers_of('init_db')")
→ ['orchestrator.setup', 'run_workstream.main', ...]

# What will break if I change this?
graphrag.query("impact_of_change('core.state.db.create_run')")
→ ['orchestrator.execute_step', 'error_engine.log_error', ...]

# What's the dependency chain?
graphrag.query("path_between('user_request', 'database_write')")
→ [request_handler → validator → orchestrator → db]
```

**Acceptance Criteria:**
- Correctly identifies all callers/callees
- Traces dependency chains up to 10 levels deep
- Performance: Query response < 100ms

**Estimated Effort:** 1 week
**Tool:** Codex (implementation) + pytest
**Cost:** ~$10

---

### WS-04-02C: RAPTOR Hierarchical Indexing

**Goal:** Create multi-level abstractions (line → file → module → system).

**Deliverables:**
- [ ] `core/semantic/raptor.py` - Recursive clustering and summarization
- [ ] `core/semantic/summarizer.py` - AI-powered code summarization
- [ ] `core/semantic/hierarchical_index.py` - Multi-level index
- [ ] `.worktrees/raptor_index.db` - Hierarchical storage
- [ ] `tests/semantic/test_raptor.py` - 18+ tests

**Hierarchy:**
```
Level 4: System Summary
  "Pipeline orchestration system with state management and error detection"

Level 3: Module Summaries
  "core.state - SQLite-based state management for runs and steps"
  "core.engine - Workflow orchestration with retry and circuit breakers"

Level 2: File Summaries
  "db.py - CRUD operations for pipeline state (runs, steps, events)"

Level 1: Function Summaries
  "init_db() - Initialize SQLite database with schema migration support"

Level 0: Source Code
  [actual implementation]
```

**Acceptance Criteria:**
- Generates summaries at all 5 levels
- High-level queries answered from level 3/4 (no need to read code)
- Detailed queries drill down to level 0/1

**Estimated Effort:** 1 week
**Tool:** Codex (implementation) + Claude (summarization) + pytest
**Cost:** ~$15 (includes AI summarization)

---

### WS-04-02D: Semantic Search Infrastructure

**Goal:** Vector embedding search for code and documentation.

**Deliverables:**
- [ ] `core/semantic/embeddings.py` - Generate embeddings via OpenAI/local
- [ ] `core/semantic/vector_store.py` - ChromaDB/FAISS integration
- [ ] `core/semantic/semantic_search.py` - Hybrid search (vector + keyword)
- [ ] `scripts/index_codebase.py` - Generate embeddings for all code
- [ ] `.worktrees/vector_index/` - Persistent vector storage
- [ ] `tests/semantic/test_semantic_search.py` - 15+ tests

**Acceptance Criteria:**
```python
# Natural language code search
search("Where do we handle PDF export?")
→ ['utils/export.py:generate_pdf()', 'engine/adapters/pdf.py']

# Conceptual similarity
search("database initialization logic")
→ ['core/state/db.py:init_db()', 'core/state/schema.py:create_tables()']
```

**Estimated Effort:** 4 days
**Tool:** Codex + OpenAI embeddings
**Cost:** ~$8

---

## Week 5-6: Autonomous Intelligence

### WS-04-03A: Reflexion Loop Framework

**Goal:** Self-correcting autonomous repair system.

**Deliverables:**
- [ ] `core/autonomous/reflexion.py` - Reflexion loop orchestrator
- [ ] `core/autonomous/self_critique.py` - AI-powered error analysis
- [ ] `core/autonomous/repair_generator.py` - Generate fixes from errors
- [ ] `core/engine/retry_with_feedback.py` - Integrate with orchestrator
- [ ] `tests/autonomous/test_reflexion.py` - 20+ tests

**Workflow:**
```python
# Traditional: Generate code → Run → Fail → Give up
# Reflexion: Generate code → Run → Capture stderr → Analyze → Fix → Retry (loop)

# Example:
1. AI generates: db.execute("SLECT * FROM runs")  # Typo
2. Execution fails: "near SLECT: syntax error"
3. Reflexion analyzes stderr: "SQL syntax error, likely typo in SELECT"
4. AI generates fix: "SLECT" → "SELECT"
5. Retry execution → Success
```

**Acceptance Criteria:**
- Fixes at least 70% of simple syntax errors autonomously
- Max 3 retry iterations before human escalation
- Logs all reflexion loops for audit trail

**Estimated Effort:** 1 week
**Tool:** Codex (implementation) + Claude (critique) + pytest
**Cost:** ~$12

---

### WS-04-03B: Episodic Memory System

**Goal:** Learn from successful edits to improve future suggestions.

**Deliverables:**
- [ ] `core/memory/episodic_memory.py` - Memory storage and retrieval
- [ ] `core/memory/edit_history.py` - Track user-accepted vs rejected edits
- [ ] `core/memory/pattern_matcher.py` - Find similar past tasks
- [ ] `.worktrees/episodic_memory.db` - SQLite + vector storage
- [ ] `tests/memory/test_episodic_memory.py` - 18+ tests

**Memory Schema:**
```python
{
  "task_description": "Add new API endpoint",
  "user_prompt": "Add GET /api/status endpoint",
  "files_changed": ["api/routes.py", "tests/test_api.py"],
  "edit_accepted": true,
  "timestamp": "2025-11-22T12:00:00Z",
  "project_conventions": {
    "file_pattern": "api/routes.py for endpoints",
    "test_pattern": "tests/test_api.py for API tests",
    "naming": "snake_case functions"
  }
}
```

**Acceptance Criteria:**
```python
# When user asks to "add new endpoint", system recalls:
memory.recall("Add new API endpoint")
→ "Last 3 times: edited api/routes.py and tests/test_api.py, used snake_case"
→ AI automatically follows project conventions without being told
```

**Estimated Effort:** 1 week
**Tool:** Codex + OpenAI embeddings
**Cost:** ~$10

---

### WS-04-03C: HyDE Search Enhancement

**Goal:** Improve semantic search with hypothetical code generation.

**Deliverables:**
- [ ] `core/semantic/hyde.py` - Hypothetical Document Embeddings
- [ ] `core/semantic/hyde_search.py` - Enhanced search using HyDE
- [ ] `scripts/search_codebase.py` - CLI with HyDE support
- [ ] `tests/semantic/test_hyde.py` - 12+ tests

**How HyDE Works:**
```python
# Traditional search (poor results):
User: "Where do we handle PDF export?"
→ Embed query: [0.23, 0.45, ...]
→ Search vector DB for matching code
→ Results: Misses utils/export.py because words don't match

# HyDE search (better results):
User: "Where do we handle PDF export?"
→ AI generates hypothetical code: "def export_pdf(data):\n  return PDF.generate(data)"
→ Embed generated code: [0.67, 0.12, ...]
→ Search vector DB with code embedding
→ Results: Finds utils/export.py:generate_pdf() (code similarity match!)
```

**Acceptance Criteria:**
- Improves search recall by at least 30% vs keyword search
- Handles natural language queries better than direct embedding

**Estimated Effort:** 3 days
**Tool:** Codex + OpenAI
**Cost:** ~$7

---

### WS-04-03D: Terminal State Integration

**Goal:** Use terminal session state as context for debugging.

**Deliverables:**
- [ ] `core/context/terminal_state.py` - PTY integration
- [ ] `core/context/session_analyzer.py` - Parse shell history, env vars
- [ ] `core/context/error_context.py` - Capture stack traces from terminal
- [ ] `scripts/debug_auto.py` - Automatic debugging from terminal state
- [ ] `tests/context/test_terminal_state.py` - 15+ tests

**Usage:**
```bash
# Traditional: Developer copies error, pastes to AI
pytest tests/
# ERROR: NameError: name 'init_db' is not defined
# Developer: "Hey AI, I got NameError: name 'init_db' is not defined, what's wrong?"

# Terminal State Integration: AI reads terminal automatically
pytest tests/
# ERROR: NameError: name 'init_db' is not defined
python scripts/debug_auto.py  # No arguments needed!
# AI reads:
#   - Last command: pytest tests/
#   - Exit code: 1
#   - Stderr: NameError: name 'init_db' is not defined at test_db.py:23
#   - Env: PYTHONPATH=/wrong/path
# AI suggests: "Missing import. Add 'from core.state.db import init_db' to test_db.py:1"
```

**Acceptance Criteria:**
- Captures last 100 lines of terminal output
- Extracts exit codes and environment variables
- Generates fix suggestions without manual error copy-paste

**Estimated Effort:** 4 days
**Tool:** Codex (implementation) + Claude (analysis)
**Cost:** ~$8

---

### WS-04-03E: Production Integration & Testing

**Goal:** Integrate all Phase 4 features into main pipeline with comprehensive testing.

**Deliverables:**
- [ ] `docs/AI_ENHANCEMENT_GUIDE.md` - User guide for new features
- [ ] `docs/PHASE_4_ARCHITECTURE.md` - Technical architecture
- [ ] `tests/integration/test_ai_enhancement.py` - End-to-end tests
- [ ] `scripts/enable_ai_features.py` - Feature flags for gradual rollout
- [ ] Update `CODEBASE_INDEX.yaml` with new modules
- [ ] Update `QUALITY_GATE.yaml` with new checks

**Integration Points:**
```python
# AST mapping injected into prompts
orchestrator.add_context(ast_map.generate())

# GraphRAG used for impact analysis
before_edit = graphrag.analyze_impact(files_to_change)

# Reflexion enabled for autonomous retry
executor.enable_reflexion(max_iterations=3)

# Episodic memory used for context
memory_context = episodic_memory.recall_similar_tasks(task_description)

# HyDE search for better code discovery
results = hyde_search.find("authentication logic")
```

**Acceptance Criteria:**
- All 150+ new tests passing
- Zero regression in existing functionality
- Feature flags allow gradual rollout
- Performance: < 5% overhead on existing workflows

**Estimated Effort:** 1 week
**Tool:** Codex + Aider + pytest
**Cost:** ~$10

---

## Success Metrics

### Phase Completion Criteria

**Technical Metrics:**
- [ ] 150+ new tests passing (100% pass rate)
- [ ] All 7 workstreams complete
- [ ] Zero breaking changes to existing APIs
- [ ] Documentation complete and validated

**Performance Metrics:**
- [ ] AST map generation: < 10 seconds for entire codebase
- [ ] GraphRAG query response: < 100ms
- [ ] Semantic search: < 500ms per query
- [ ] Reflexion loop: < 5 minutes for autonomous fix

**Quality Metrics:**
- [ ] Reflexion fixes 70%+ of simple errors autonomously
- [ ] HyDE improves search recall by 30%+
- [ ] Episodic memory reduces repetitive questions by 50%+
- [ ] Terminal state integration eliminates manual error copy-paste

---

## Resource Planning

### Time Estimates
- **Week 1-2:** AST Foundation (3 workstreams)
- **Week 3-4:** Semantic Understanding (4 workstreams)
- **Week 5-6:** Autonomous Intelligence (5 workstreams)
- **Total:** 6 weeks (can be parallelized to 4 weeks with 2 developers)

### Cost Estimates
- **Development (AI tools):** ~$100 total
- **Embeddings (one-time):** ~$20 for full codebase
- **Embeddings (ongoing):** ~$2/week for updates
- **Total Phase 4:** ~$120

### Dependencies
- **External:**
  - tree-sitter Python package
  - ChromaDB or FAISS for vectors
  - OpenAI API for embeddings/summarization (or local alternatives)

- **Internal:**
  - Phase 3 complete (orchestration engine)
  - UET framework operational
  - SQLite state management working

---

## Risk Mitigation

### Technical Risks

**Risk:** Tree-sitter may not support all languages
**Mitigation:** Start with Python/JS/TS (covers 95% of codebase), add others later

**Risk:** Vector embeddings cost too much
**Mitigation:** Use local embedding models (sentence-transformers) instead of OpenAI

**Risk:** Reflexion loops may infinite loop
**Mitigation:** Hard cap at 3 iterations, human escalation beyond that

**Risk:** Graph traversal may be slow on large codebases
**Mitigation:** Index graphs in SQLite with proper indexes, cache traversal results

### Integration Risks

**Risk:** New features slow down existing workflows
**Mitigation:** Feature flags for gradual rollout, performance benchmarks

**Risk:** Breaking changes to APIs
**Mitigation:** All new features are additive, zero changes to existing code paths

---

## Next Steps

### Immediate Actions (This Week)
1. Review this plan with stakeholders
2. Approve Phase 4 budget (~$120)
3. Set up tree-sitter development environment
4. Create WS-04-01A workstream bundle

### Week 1 Kickoff
1. Start WS-04-01A (Tree-sitter Integration)
2. Set up CI for AST tests
3. Begin AST parser implementation

### Post-Phase 4
- **Phase 5:** Multi-agent coordination (agents teaching each other via episodic memory)
- **Phase 6:** Full autonomous development (human only approves, doesn't write code)

---

## References

### Research Papers
- **Repository Mapping:** [Aider's repository map implementation](https://aider.chat/docs/repomap.html)
- **GraphRAG:** [Microsoft GraphRAG paper](https://arxiv.org/abs/2404.16130)
- **Reflexion:** [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- **RAPTOR:** [Recursive Abstractive Processing for Tree-Organized Retrieval](https://arxiv.org/abs/2401.18059)
- **HyDE:** [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496)

### Related Documentation
- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml)
- [UET Framework README](../README.md)
- [Phase 3 Completion Report](PHASE_3_COMPLETION_REPORT.md)
- [TODO: Advanced AI Techniques](C:\Users\richg\TODO_TONIGHT\Based on recent developments in AI-.txt)

---

**Document Status:** Draft
**Next Review:** 2025-11-25
**Approved By:** [Pending]
