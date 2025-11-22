Here’s how the seven pipeline_plus docs fit together and how to
  integrate them into your current repo and pipeline.

  Big Picture

  - The set defines a safe, data-driven refactor track plus a local,
    unlimited “code-surgery engine” (DeepSeek via Ollama), all driven by
    your existing workstream/orchestrator model.
  - Treat Aider-optimized workstreams as a tool-specific view generated
    from your tool‑neutral workstream schema. Use Invoke/Invoke-Build as
    a thin outer task runner, not a new brain.

  Doc → Role In Pipeline

  - Aider-optimized" workstreams.md
      - Position: Tool-specific rendering layer.
      - Fit: Keep canonical tasks in schema/workstream.schema.json +
        workstreams/*.json; generate Aider-flavored .md as a view.
      - Integration: Orchestrator maps operations_sequence intents to
        each tool (Aider slash commands vs natural-language steps for
        Codex/Gemini).
  - data and indirection refactor.md
      - Position: Refactor strategy and sequence.
      - Fit: Introduces Hardcoded Path Indexer (WS-01), Section Map (WS-
        02), Path Registry/Resolver (WS-03), then sectioned refactor
        WS-04..N.
      - Integration: Adds tools and configs to make refactors data-
        driven, enforceable in CI, and reversible.
  - fully-autonomous refactor runner.md
      - Position: Scheduler/autorun wrapper.
      - Fit: Wraps your orchestrator + error pipeline into a zero‑touch
        loop that walks dependencies and chooses tools under quotas.
      - Integration: One “autorun” entrypoint that creates worktrees,
        runs EDIT/STATIC/RUNTIME, merges on green, escalates on failure.
  - Invoke_added_pipeline.md
      - Position: Outer CLI task runner.
      - Fit: Use Python Invoke (and optional Invoke-Build on PowerShell)
        to expose clean commands for running workstreams, sections, and
        CI bundles.
      - Integration: Clean, testable entrypoints for dev/CI; not a
        replacement for your orchestrator.
  - ollama-code.md
      - Position: Additional local CLI agent.
      - Fit: Register as a tool_profile alongside Aider; route specific
        mechanical tasks to it.
      - Integration: Another driver option your orchestrator can call
        for code edits/tests locally via Ollama.
  - stuff inside WSL to talk to your Ollama server.md
      - Position: Env wiring.
      - Fit: Ensures WSL tools can reach Windows Ollama via OLLAMA_HOST/
        OLLAMA_API_BASE.
      - Integration: Add docs and optional setup script; avoids “can’t
        reach model” flakiness.
  - What DeepSeek-Coder actually adds to your stack.md
      - Position: Capability definition + routing guidance.
      - Fit: Define DeepSeek-Coder as a local, unmetered “refactor
        worker”; prefer it for large, repetitive edits; escalate to
        frontier models when stuck.
      - Integration: Add a capability card and tool profile; update
        routing rules in orchestrator/quotas.

  Where Everything Lives (proposed additions)

  - Config
      - config/section_map.yaml (section layout + old→new maps)
      - config/path_index.yaml (registry keys → canonical paths/
        sections)
      - config/tool_profiles.json (add ollama.deepseek_coder.local,
        ollama_code.local)
  - Tools
      - tools/hardcoded_path_indexer.py (scan hardcoded paths into
        SQLite)
  - Src
      - src/path_registry.py (resolve_path/list_paths over
        path_index.yaml)
      - src/pipeline/autorun.py (scheduler that drives orchestrator with
        quotas/deps)
  - Scripts
      - scripts/paths_index_cli.py (scan/summary/check; CI-friendly)
      - scripts/paths_resolve_cli.py (resolve/list/debug keys)
      - scripts/run_section_refactor.py (drive WS by section using deps)
      - tasks.py (Invoke tasks: ws, refactor.section, ci.full,
        enforce.paths)
  - Docs
      - docs/HARDCODED_PATH_INDEXER.md, docs/PATH_ABSTRACTION_SPEC.md
      - Aider-rendered workstreams in docs/workstreams/ (generated from
        JSON)
  - Workstreams
      - workstreams/ws-01-path-index.json (indexer)
      - workstreams/ws-02-section-map.json (author/validate map)
      - workstreams/ws-03-path-registry.json (registry/resolver)
      - workstreams/ws-0x-<section>-refactor.json (one per section with
        deps, tests)

  How It Runs (end-to-end)

  - Bootstrap
      - Run indexer (WS-01), build baseline report; validate
        path_index.yaml; pytest -q; tag baseline.
  - Autorun
      - python -m src.pipeline.autorun --plan section_refactor --mode
        zero-touch
      - Scheduler picks next WS respecting deps; selects tool under
        quotas (DeepSeek local first, escalate if needed); creates
        isolated worktree; runs orchestrator EDIT/STATIC/RUNTIME; merges
        on green.
  - CI/Enforcement
      - Add job to run paths_index_cli.py check and fail on forbidden
        patterns or drift from path_index.yaml.
      - Optionally verify no new hardcoded paths in protected sections.

  Concrete Integration Steps

  - Implement data layer first (low-risk, high leverage)
      - Add indexer + CLI, path registry + CLI, section map config,
        and docs.
      - Wire CI job: python scripts/paths_index_cli.py check --fail-
        on deprecated
  - Encode workstreams
      - Author WS-01..WS-03 (indexer, section map, registry) + 1–2
        section refactor WS to pilot.
      - Validate with python scripts/validate_workstreams.py
  - Add tool profiles and drivers
      - Register ollama.deepseek_coder.local and ollama_code.local;
        ensure orchestrator can call both and Aider.
  - Outer CLI
      - Add tasks.py Invoke tasks for ws/refactor/ci; optional Invoke-
        Build file for PowerShell-centric pipelines.
  - Env wiring
      - Document/set OLLAMA_HOST in WSL; add a small PowerShell helper
        to append to ~/.bashrc.

  Risks / Gaps

  - Scope enforcement: ensure orchestrator validates files_scope and
    rejects edits outside worktree/section.
  - Determinism: avoid timestamps, nondeterministic ordering; enforce
    via tests/static checks per WS.
  - Registry drift: keep path_index.yaml the single source of truth;
    indexer “check” gate prevents regressions.
  - Tool parity: Aider view should be generated from core JSON; don’t
    embed Aider-only syntax in canonical spec.
  - Windows-first: provide .ps1 wrappers for all CLIs; keep logic in
    Python for parity.
