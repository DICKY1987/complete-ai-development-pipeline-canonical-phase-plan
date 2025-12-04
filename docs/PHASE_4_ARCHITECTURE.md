# Phase 4 Architecture (Autonomous Intelligence)

## Components
- `core/autonomous/reflexion.py`: orchestrates generate → validate → analyze → fix with a hard iteration cap.
- `core/autonomous/error_analyzer.py`: parses stderr/test output into structured errors.
- `core/autonomous/fix_generator.py`: pluggable fix generation hook.
- `core/memory/episodic_memory.py`: SQLite-backed memory of past tasks with semantic recall.
- `core/memory/pattern_learner.py`: derives conventions and success rates from episodes.
- `core/search/hyde.py`: HyDE search that embeds hypothetical code for queries.
- `core/terminal/state_capture.py`: captures stdout/stderr/env/cwd tails safely.
- `core/terminal/context_manager.py`: context manager wrapper for capture.

## Data Stores
- `.worktrees/episodic_memory.db`: episodic memory store (SQLite + embeddings).
- Vector index: provided by `InMemoryVectorStore` (can be swapped for FAISS/Chroma).

## Feature Flags (suggested)
- `enable_reflexion`, `enable_hyde_search`, `enable_terminal_capture`, `enable_episodic_memory`.

## Flow
1. Run task with `ReflexionLoop` (max 3 iterations).
2. On failure, parse errors → generate fix suggestion → retry.
3. Persist success/failure to episodic memory.
4. Use `HyDESearch` to improve code retrieval.
5. Capture terminal output/state for better diagnostics.
