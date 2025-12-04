# Phase 4 User Guide (AI Features)

This guide covers the Agent 3 features shipped in Phase 4:

- Reflexion loop: automated retry with error parsing and fix generation.
- Episodic memory: recall past tasks and conventions.
- HyDE search: hypothetical-code embeddings to boost recall.
- Terminal capture: automatic stdout/stderr/env context for debugging.

## Feature Flags
- `enable_reflexion`
- `enable_hyde_search`
- `enable_terminal_capture`
- `enable_episodic_memory`

Enable flags in your executor/config before invoking autonomous workflows.

## Quickstart
1. Use `ReflexionLoop` with `max_iterations=3`.
2. Provide `EpisodicMemory` to persist successes/failures.
3. Build a vector store and initialize `HyDESearch` for better code search.
4. Wrap commands in `TerminalContext` to capture failure context automatically.
