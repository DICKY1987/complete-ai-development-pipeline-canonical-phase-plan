---
doc_id: DOC-GUIDE-PHASE-4-WORKSTREAM-DISTRIBUTION-461
---

# Phase 4 AI Enhancement - 3-Agent Workstream Distribution

**Goal**: Complete 12 Phase 4 workstreams in parallel across 3 independent agents

**Timeline**: Weeks 3-8 (6 weeks total, ~40 hours per agent = 120 hours total)

**Prerequisites**: Phase 1-3 complete (tests passing, imports fixed, core executor/recovery implemented)

---

## Agent 1: AST & Repository Intelligence Workstream

**Focus**: Code parsing, analysis, and module ranking
**Estimated Time**: 18-23 hours
**Dependencies**: None (fully independent)

### Workstreams Assigned (3 workstreams)

#### WS-04-01A: Complete Tree-sitter Integration
**Effort**: 6-8 hours | **Week**: 3

**Deliverables**:
- `core/ast/parser.py` (165 lines) - Main tree-sitter wrapper
- `core/ast/languages/python.py` (380 lines) - Python AST extraction
- `core/ast/languages/javascript.py` (~300 lines) - JavaScript support
- `core/ast/languages/typescript.py` (~300 lines) - TypeScript support
- `tests/ast/test_parser.py` (200 lines, 20 tests)
- `tests/ast/test_python.py` (300 lines, 30+ tests)

**Dependencies to Install**:
```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

**Success Criteria**:
- Parse Python/JS/TS files without errors
- Extract function signatures, classes, imports
- All 50+ AST tests pass

---

#### WS-04-01B: AST-Based Repository Mapping
**Effort**: 8-10 hours | **Week**: 3-4

**Deliverables**:
- `core/ast/repository_mapper.py` (~400 lines) - Map generator
- `core/ast/signature_extractor.py` (~200 lines) - Extract signatures only
- `core/ast/import_graph.py` (~250 lines) - Build import dependency graph
- `scripts/generate_repository_map.py` - CLI tool
- `AST_REPOSITORY_MAP.yaml` (auto-generated, <5000 tokens)

**Features**:
- Extract: functions, classes, methods, imports (signatures only, no implementation)
- Output: YAML with module → symbols mapping
- Performance: <10 seconds for entire codebase

**Success Criteria**:
- Generate map in <10 seconds
- Map size <5000 tokens
- All public symbols included
- Can identify what modules define what symbols

---

#### WS-04-01C: PageRank Module Ranking
**Effort**: 4-5 hours | **Week**: 4

**Deliverables**:
- `core/ast/pagerank.py` (~150 lines) - PageRank algorithm
- `core/ast/centrality_analyzer.py` (~200 lines) - Analyze module importance
- `scripts/rank_modules.py` - CLI tool
- `MODULE_IMPORTANCE_RANKING.yaml` - Output ranking

**Algorithm**:
1. Build directed graph from imports (A imports B → edge A→B)
2. Apply PageRank to find central modules
3. Score 0.0-1.0 for each module (higher = more important)

**Success Criteria**:
- Top 10 modules match expected core modules (`core.state.db`, `core.engine.orchestrator`, etc.)
- Ranking scores are reasonable (core modules >0.5)

---

### Testing Strategy
- Unit tests for each module
- Integration test: Parse repo → Generate map → Rank modules (full pipeline)
- Performance benchmark: Must complete in <15 seconds total

### Validation Commands
```bash
# Test AST parsing
pytest tests/ast/ -v

# Generate repository map
python scripts/generate_repository_map.py --output AST_REPOSITORY_MAP.yaml

# Rank modules
python scripts/rank_modules.py --output MODULE_IMPORTANCE_RANKING.yaml
```

---

## Agent 2: Knowledge Graph & Semantic Search Workstream

**Focus**: Semantic understanding, vector embeddings, and RAG infrastructure
**Estimated Time**: 36-45 hours
**Dependencies**: WS-04-01B (needs repository map), but can stub it for development

### Workstreams Assigned (4 workstreams)

#### WS-04-02A: Knowledge Graph Construction
**Effort**: 10-12 hours | **Week**: 5

**Deliverables**:
- `core/knowledge/knowledge_graph.py` (~500 lines) - Graph management (nodes, edges, queries)
- `core/knowledge/graph_builder.py` (~400 lines) - Build graph from AST
- `core/knowledge/relationships.py` (~200 lines) - Relationship types and weights
- `schema/knowledge_graph_schema.sql` - SQLite schema
- Storage: `.worktrees/knowledge_graph.db`

**Graph Schema**:
- **Nodes**: functions, classes, modules
  Properties: `name`, `type`, `file`, `line_number`
- **Edges**: calls, imports, inherits, modifies, uses
  Properties: `weight`, `frequency`, `edge_type`

**Success Criteria**:
- Build graph for entire codebase (scan all Python files)
- Query: "What calls this function?" returns correct results
- Graph persists to SQLite and can be reloaded

---

#### WS-04-02B: GraphRAG Query Engine
**Effort**: 8-10 hours | **Week**: 5-6

**Deliverables**:
- `core/knowledge/query_engine.py` (~400 lines) - Graph traversal and queries
- `scripts/query_graph.py` - CLI tool

**Queries to Support**:
1. "What functions call X?" (reverse call graph)
2. "What will break if I change X?" (impact analysis)
3. "What's the dependency chain for X?" (path finding)
4. "Find all usages of X" (references)

**Performance**: <100ms per query

**Success Criteria**:
- All 4 query types implemented
- Queries return correct results in <100ms
- Can handle queries on large graphs (1000+ nodes)

---

#### WS-04-02C: RAPTOR Hierarchical Indexing
**Effort**: 12-15 hours | **Week**: 6

**Deliverables**:
- `core/indexing/raptor.py` (~600 lines) - RAPTOR implementation (recursive summarization)
- `core/indexing/summarizer.py` (~300 lines) - AI summarization via OpenAI API
- `schema/raptor_index_schema.sql` - Database schema
- Storage: `.worktrees/raptor_index.db`

**5-Level Hierarchy**:
- **Level 0**: Source code (raw)
- **Level 1**: Function summaries (AI-generated, 1-2 sentences each)
- **Level 2**: File summaries (AI-generated, 1 paragraph each)
- **Level 3**: Module summaries (AI-generated, 2-3 paragraphs each)
- **Level 4**: System summary (AI-generated, 1 page overview)

**AI Cost**: ~$15 for initial indexing (OpenAI API gpt-4o-mini)

**Success Criteria**:
- Can query at any abstraction level
- Summaries are accurate and coherent
- Incremental updates work (only re-summarize changed files)

---

#### WS-04-02D: Semantic Search Infrastructure
**Effort**: 6-8 hours | **Week**: 6

**Deliverables**:
- `core/search/embeddings.py` (~200 lines) - Embedding generation (OpenAI text-embedding-3-small)
- `core/search/vector_store.py` (~300 lines) - Vector storage (ChromaDB or FAISS)
- `core/search/semantic_search.py` (~250 lines) - Semantic search engine
- `scripts/index_codebase.py` - CLI indexer
- Storage: `.worktrees/vector_index/` (persistent ChromaDB collection)

**Features**:
- Embed: code blocks, docstrings, comments
- Search: semantic similarity (cosine distance)
- Performance: <500ms per search

**Success Criteria**:
- Semantic search returns relevant results (top-5 accuracy >80%)
- Embeddings persist and reload correctly
- Can search across 1000+ code blocks

---

### Testing Strategy
- Unit tests for each component
- Integration test: Build graph → Generate RAPTOR summaries → Semantic search
- Query performance benchmarks

### Validation Commands
```bash
# Test knowledge graph
pytest tests/knowledge/ -v

# Build knowledge graph
python scripts/build_knowledge_graph.py --output .worktrees/knowledge_graph.db

# Query graph
python scripts/query_graph.py --query "what calls init_db?"

# Build RAPTOR index
python scripts/build_raptor_index.py --output .worktrees/raptor_index.db

# Semantic search
python scripts/index_codebase.py --index .worktrees/vector_index/
python scripts/semantic_search.py "validate workstream spec"
```

---

## Agent 3: Autonomous Intelligence & Self-Correction Workstream

**Focus**: AI agents, reflexion loops, episodic memory, and terminal integration
**Estimated Time**: 39-52 hours
**Dependencies**: WS-04-02B (knowledge graph queries), but can mock for development

### Workstreams Assigned (5 workstreams)

#### WS-04-03A: Reflexion Loop Framework
**Effort**: 10-12 hours | **Week**: 7

**Deliverables**:
- `core/autonomous/reflexion.py` (~500 lines) - Reflexion loop orchestrator
- `core/autonomous/error_analyzer.py` (~300 lines) - Parse and analyze stderr/test failures
- `core/autonomous/fix_generator.py` (~350 lines) - Generate code fixes via AI

**Workflow** (max 3 iterations):
1. Generate code (AI agent writes code)
2. Run tests/validation (execute tests)
3. Capture stderr (collect error output)
4. Analyze errors (parse failures, identify root cause)
5. Generate fix (AI proposes correction)
6. Retry (re-run tests)
7. Escalate to human if still failing after 3 iterations

**Success Criteria**:
- Fix 70%+ of simple syntax errors autonomously (tested on known error corpus)
- Never infinite loop (hard cap at 3 iterations)
- Clear escalation message when manual intervention needed

---

#### WS-04-03B: Episodic Memory System
**Effort**: 8-10 hours | **Week**: 7

**Deliverables**:
- `core/memory/episodic_memory.py` (~400 lines) - Memory storage and retrieval
- `core/memory/pattern_learner.py` (~300 lines) - Extract patterns from past tasks
- `schema/episodic_memory_schema.sql` - Database schema
- Storage: `.worktrees/episodic_memory.db` + vector embeddings

**Memory Schema**:
- `task_id`, `task_description`, `user_prompt`, `files_changed`, `edit_accepted`, `project_conventions`
- Store embeddings of task descriptions for semantic retrieval

**Features**:
- Record every code generation task
- Retrieve similar past tasks (semantic search on task descriptions)
- Learn project conventions (e.g., "always use type hints", "prefer dataclasses")

**Success Criteria**:
- Recall similar past tasks with >75% relevance
- Apply learned patterns to new tasks
- Memory persists across sessions

---

#### WS-04-03C: HyDE Search Enhancement
**Effort**: 5-7 hours | **Week**: 7-8

**Deliverables**:
- `core/search/hyde.py` (~250 lines) - HyDE (Hypothetical Document Embeddings) implementation

**How It Works**:
1. User query: "function to validate email"
2. Generate hypothetical code matching query (AI generates example code)
3. Embed generated code (use same embedding model as codebase)
4. Search vectors for similar code (find actual code similar to hypothetical)

**Success Criteria**:
- 30%+ better recall vs keyword search (measured on test query set)
- Works with semantic search from WS-04-02D

---

#### WS-04-03D: Terminal State Integration
**Effort**: 6-8 hours | **Week**: 8

**Deliverables**:
- `core/terminal/state_capture.py` (~300 lines) - Capture terminal output
- `core/terminal/context_manager.py` (~200 lines) - Integrate terminal state into AI context
- `scripts/debug_auto.py` - Auto-debug CLI tool

**Captures**:
- Last 100 lines of terminal output
- Exit codes from subprocess executions
- Environment variables (sanitized, no secrets)
- Current working directory

**Success Criteria**:
- AI can read terminal errors without manual copy-paste
- Terminal state auto-included in error analysis
- No secrets leaked in captured state

---

#### WS-04-03E: Phase 4 Production Integration
**Effort**: 10-15 hours | **Week**: 8

**Deliverables**:
- `docs/PHASE_4_USER_GUIDE.md` - How to use AI features (for developers)
- `docs/PHASE_4_ARCHITECTURE.md` - System architecture documentation
- 150+ new tests for Phase 4 features (integration tests)
- Feature flags for gradual rollout (enable/disable each AI feature)
- Performance validation (ensure <5% overhead vs non-AI mode)

**Integration Tasks**:
1. Wire up all Phase 4 components to orchestrator
2. Add feature flags: `enable_semantic_search`, `enable_reflexion`, etc.
3. Performance benchmarks: Compare run times with/without AI features
4. End-to-end test: Use AI features to complete a full workstream

**Success Criteria**:
- Zero regressions in Phase 1-3 functionality
- All 150+ Phase 4 tests pass
- Performance overhead <5% (measured on benchmark workstreams)
- Documentation complete and accurate

---

### Testing Strategy
- Unit tests for reflexion, memory, HyDE, terminal capture
- Integration test: Full autonomous workflow (reflexion → memory → terminal)
- Performance regression tests

### Validation Commands
```bash
# Test reflexion loop
pytest tests/autonomous/test_reflexion.py -v

# Test episodic memory
pytest tests/memory/test_episodic_memory.py -v

# Test HyDE search
pytest tests/search/test_hyde.py -v

# Test terminal capture
pytest tests/terminal/test_state_capture.py -v

# Full Phase 4 integration test
pytest tests/integration/test_phase4_e2e.py -v

# Performance validation
python scripts/benchmark_phase4_overhead.py
```

---

## Dependencies Between Agents

### Agent 1 → Agent 2
- **WS-04-01B** (Repository Mapping) → **WS-04-02A** (Knowledge Graph)
  - Agent 2 can start by mocking repository map, then integrate real one when Agent 1 completes

### Agent 2 → Agent 3
- **WS-04-02B** (Query Engine) → **WS-04-03A** (Reflexion)
  - Agent 3 can use knowledge graph queries to improve error analysis
  - Not a hard blocker: Reflexion works without it, just better with it

### No Other Dependencies
- All other workstreams are independent
- Agents can work in parallel starting Week 3

---

## Parallel Execution Strategy

### Week 3-4: Foundation Phase
- **Agent 1**: WS-04-01A (Tree-sitter) → WS-04-01B (Repo Mapping)
- **Agent 2**: WS-04-02A (Knowledge Graph - can mock repo map initially)
- **Agent 3**: WS-04-03B (Episodic Memory - fully independent)

### Week 5-6: Advanced Features
- **Agent 1**: WS-04-01C (PageRank - uses completed repo map)
- **Agent 2**: WS-04-02B (GraphRAG Queries) → WS-04-02C (RAPTOR)
- **Agent 3**: WS-04-03A (Reflexion) → WS-04-03C (HyDE)

### Week 7-8: Integration Phase
- **Agent 1**: Help with testing/documentation
- **Agent 2**: WS-04-02D (Semantic Search) → Integration testing
- **Agent 3**: WS-04-03D (Terminal State) → WS-04-03E (Phase 4 Integration)

---

## Success Metrics

### Agent 1 (AST & Repository Intelligence)
- ✅ Can parse Python/JS/TS files
- ✅ Repository map generated in <10 seconds
- ✅ Module rankings accurate (top 10 match expectations)
- ✅ All AST tests pass (50+ tests)

### Agent 2 (Knowledge Graph & Semantic Search)
- ✅ Knowledge graph built for entire codebase
- ✅ GraphRAG queries return correct results in <100ms
- ✅ RAPTOR index generated (5 levels)
- ✅ Semantic search recall >80%
- ✅ All knowledge/search tests pass (80+ tests)

### Agent 3 (Autonomous Intelligence)
- ✅ Reflexion loop fixes 70%+ of simple errors
- ✅ Episodic memory recalls similar tasks with >75% relevance
- ✅ HyDE search improves recall by 30%+
- ✅ Terminal state captured without secrets
- ✅ Phase 4 integration complete with <5% overhead
- ✅ All autonomous/integration tests pass (150+ tests)

---

## Risk Mitigation

### Risk: Agent 1 delays → Agent 2 blocked
**Mitigation**: Agent 2 uses mock repository map until WS-04-01B completes

### Risk: AI API costs exceed budget
**Mitigation**: Use gpt-4o-mini for all calls, batch processing, cache embeddings

### Risk: Performance overhead >5%
**Mitigation**: Add feature flags, lazy loading, aggressive caching

### Risk: Scope creep
**Mitigation**: Stick to defined 12 workstreams, defer nice-to-haves to post-100%

---

## Communication Protocol

### Daily Sync (Async)
Each agent posts to shared channel:
1. **Completed today**: Which workstreams/tasks finished
2. **Blocked on**: Any dependencies waiting on other agents
3. **Starting tomorrow**: Next workstream/task

### Integration Points
- **End of Week 4**: Agent 1 delivers repository map → Agent 2 integrates
- **End of Week 6**: Agent 2 delivers knowledge graph → Agent 3 integrates
- **End of Week 8**: All agents merge for final integration testing

---

## Handoff Instructions for Each Agent

### Agent 1 Handoff
**Context**: You are responsible for AST parsing, repository mapping, and module ranking.

**Start here**:
1. Install dependencies: `pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript`
2. Read `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md` for execution patterns
3. Start with WS-04-01A (Tree-sitter integration)
4. Follow test-driven development: write tests first, then implementation
5. Commit after each workstream completion

**Output artifacts**:
- `core/ast/` module (fully implemented and tested)
- `AST_REPOSITORY_MAP.yaml` (auto-generated, <5000 tokens)
- `MODULE_IMPORTANCE_RANKING.yaml` (module rankings)

### Agent 2 Handoff
**Context**: You are responsible for knowledge graph, RAPTOR indexing, and semantic search.

**Start here**:
1. Install dependencies: `pip install chromadb openai networkx`
2. Create mock repository map if Agent 1 not done: `{"modules": {"core.state.db": {"functions": ["init_db", "get_db"]}}}`
3. Start with WS-04-02A (Knowledge Graph)
4. Use gpt-4o-mini for all OpenAI API calls to minimize costs
5. Add `.worktrees/` to `.gitignore` (storage for databases)

**Output artifacts**:
- `core/knowledge/` module (graph construction and queries)
- `core/indexing/` module (RAPTOR hierarchical summaries)
- `core/search/` module (semantic search)
- `.worktrees/knowledge_graph.db`, `.worktrees/raptor_index.db`, `.worktrees/vector_index/`

### Agent 3 Handoff
**Context**: You are responsible for autonomous intelligence, reflexion loops, and Phase 4 integration.

**Start here**:
1. Install dependencies: `pip install openai`
2. Start with WS-04-03B (Episodic Memory - fully independent)
3. For reflexion loop, use existing error detection infrastructure in `error/` module
4. Ensure terminal capture sanitizes secrets (never log API keys, passwords)
5. Final integration: Add feature flags to `core/engine/orchestrator.py`

**Output artifacts**:
- `core/autonomous/` module (reflexion loop)
- `core/memory/` module (episodic memory)
- `core/search/hyde.py` (HyDE search)
- `core/terminal/` module (terminal state capture)
- `docs/PHASE_4_USER_GUIDE.md`, `docs/PHASE_4_ARCHITECTURE.md`
- 150+ integration tests

---

## Final Checklist (All Agents)

Before marking Phase 4 complete:

- [ ] All 12 workstreams implemented
- [ ] All 280+ Phase 4 tests passing (50 AST + 80 knowledge/search + 150 autonomous/integration)
- [ ] Documentation complete (user guide + architecture doc)
- [ ] Performance overhead <5% (measured on benchmark workstreams)
- [ ] AI API costs within budget (~$15 initial + $10/week ongoing)
- [ ] Feature flags working (can disable each AI feature independently)
- [ ] Zero regressions in Phase 1-3 functionality
- [ ] Code reviewed and merged to main branch

**When all checkboxes checked**: Phase 4 is production-ready! 🎉

---

## Estimated Timeline

| Week | Agent 1 | Agent 2 | Agent 3 |
|------|---------|---------|---------|
| 3 | WS-04-01A (Tree-sitter) | WS-04-02A (Knowledge Graph) | WS-04-03B (Episodic Memory) |
| 4 | WS-04-01B (Repo Mapping) | WS-04-02A (cont.) | WS-04-03A (Reflexion) |
| 5 | WS-04-01C (PageRank) | WS-04-02B (GraphRAG Queries) | WS-04-03A (cont.) |
| 6 | Testing + Documentation | WS-04-02C (RAPTOR) | WS-04-03C (HyDE) |
| 7 | Integration Support | WS-04-02D (Semantic Search) | WS-04-03D (Terminal State) |
| 8 | Final Testing | Integration Testing | WS-04-03E (Phase 4 Integration) |

**Total**: 6 weeks, 3 agents, ~120 hours total effort

**Cost**: ~$15 AI API (initial) + $10/week ongoing = ~$75 total for Phase 4
