Main Plan_Complete AI Pipeline Refactor

   This is the execution-ready refactor plan organized into 5 phases (A-E) covering 18 workstreams (WS-06 through WS-21):

   Status: WS-08 (Aider) is ✅ COMPLETED with shim pattern established

   Execution Phases:

     - Phase A (Parallel): WS-06, WS-07, WS-09 - Section consolidations (AIM, PM/CCPM, Spec tools)
     - Phase B (Sequential): WS-10 → WS-11 - OpenSpec integration
     - Phase C (Sequential): WS-12 → WS-13 → WS-14 - Error subsystem (VERY HIGH risk)
     - Phase D (Sequential): WS-15 → WS-16 → WS-17 - Core extraction (VERY HIGH risk)
     - Phase E (Parallel): WS-18, WS-19, WS-20, WS-21 - Post-refactor cleanup

   Supporting Documents:

     - Section_Aware Repo Refactor_Workstream Plan.md - Comprehensive 21-workstream plan with detailed specifications for each workstream
     - dependency-aware path.md - Execution order and parallelization guide with strict dependency graph
     - PATH ABSTRACTION & INDIRECTION LAYER.md - Spec for path registry/resolver system to eliminate hardcoded paths

   Key Insights:

     - Foundation: WS-01 (Hardcoded Path Indexer) must run first as ground truth
     - Risk Management: Low-risk isolated sections first, high-risk core components last
     - Parallelization: 6-9 workstreams can run concurrently in early phases
     - Shim Pattern: Keep original files as re-export stubs during migration
     - Estimated Effort: 160-200 hours realistic, 120-140 hours optimistic