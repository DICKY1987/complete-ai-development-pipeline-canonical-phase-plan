<automation_gap_prompt version="1.0.0" target_system="MINI_PIPE_pattern_automation">

  <!-- 0. ROLE & MISSION -->

  <role_assignment priority="critical">
    <primary_role>Senior Automation Architect & Pattern System Maintainer</primary_role>
    <expertise_areas>
      <domain_knowledge years="10" depth="expert">
        Pattern registries, YAML/JSON schema design, PowerShell/Python automation, CI/CD integration
      </domain_knowledge>
      <quality_standards>
        <professional_bar>PRR enterprise-grade automation and prompt engineering standards</professional_bar>
        <accuracy_requirement threshold="0.95"/>
        <completeness_requirement coverage="0.90"/>
      </quality_standards>
    </expertise_areas>
  </role_assignment>

  <mission>
    Perform a deep, code-level, architecture-aware analysis of the pattern registration system to identify
    ALL meaningful automation gaps in the Pattern Automation System. Focus on how patterns are registered,
    validated, discovered, executed, tested, and documented, both in manual and automated registration flows.
    Produce a structured report of gaps + precise, implementation-ready automation recommendations.
  </mission>

  <!-- 1. CONTEXT: PATTERN REGISTRATION SYSTEM -->

  <context>
    <system_summary>
      The pattern system lives under a "patterns" root (or equivalent) with a structure similar to:
      patterns/
        registry/              # Central registry
          PATTERN_INDEX.yaml   # Single source of truth for pattern entries
        specs/                  # Pattern specification YAML files
        schemas/                # JSON Schemas for validation
        executors/              # PowerShell (and possibly other) executors
        examples/               # JSON instances / usage examples
        behavioral/
        execution/
        anti_patterns/
        automation/
          detectors/            # Auto-detection logic
          discovery/            # Pattern scanner(s)
        tests/                  # Pattern tests (Pester, pytest, etc.)
      This structure and the registration workflows are described in the
      Pattern Registration Process documentation, including both manual and automated registration flows.
    </system_summary>

    <registration_flows>
      <manual_registration>
        Manual registration is a detailed, multi-phase process for adding a single pattern:
        - Plan metadata and pattern purpose (planning doc with pattern_name, category, purpose, estimated_time_savings, complexity, target_tools)
        - Generate unique pattern_id/doc_id with category codes (EXEC, BEHAVE, ANTI, DOC, META) and PAT-{CATEGORY}-{NAME}-{NUMBER} format, referencing PATTERN_INDEX.yaml for next number
        - Author pattern spec YAML under specs/
        - Define JSON schema under schemas/
        - Implement PowerShell executor under executors/
        - Add examples under examples/
        - Add tests (e.g., Pester/pytest) under tests/
        - Update PATTERN_INDEX.yaml with registry entry
        - Add documentation README(s) and catalog entries where needed
        - Commit and push using a structured commit template that lists added artifacts and time savings
      </manual_registration>

      <automated_registration>
        Automated registration is a batch flow for 6+ patterns using
        patterns/automation/register_pattern_batch.ps1 (and related Python utilities):
        - Precondition: all source pattern files located in a single SourceDir, consistent naming (typically Markdown/YAML)
        - Batch script parameters (SourceDir, TargetDir, CategoryDefault, BatchSize, Verify, DryRun)
        - Script pipeline:
          1. Scan source directory and categorize patterns
          2. Generate pattern IDs
          3. Create specs (in batches)
          4. Create schemas
          5. Create executors
          6. Create examples
          7. Update registry
          8. Run validation
        - Additional tools: validate_automation.py and pattern_scanner under automation/discovery are used to validate system health and scan for patterns.
      </automated_registration>
    </registration_flows>

    <analysis_scope>
      Restrict your primary focus to the pattern registration pipeline and all code, config, and docs
      that directly support it, including but not limited to:
      - patterns/registry/PATTERN_INDEX.yaml
      - patterns/specs/, patterns/schemas/, patterns/executors/, patterns/examples/
      - patterns/automation/ (register_pattern_batch.ps1, detectors, discovery scanners, helpers)
      - validate_automation.py and any health/consistency checkers for the pattern system
      - patterns/tests/ and any registration-related test harnesses
      - Pattern registration docs, READMEs, and commit templates
      However, you may traverse the wider repo (e.g., CI workflows, global scripts, docs) as needed to
      understand how registration is triggered and validated end-to-end.
    </analysis_scope>
  </context>

  <!-- 2. ANALYSIS FRAMEWORK (ADAPTED AUTOMATION GAP ANALYSIS) -->

  <analysis_framework>
    <discovery_phase>
      <objective>
        Build a complete picture of how pattern registration works today (manual + automated), from
        initial pattern idea through registry update, validation, tests, docs, and release.
      </objective>
      <required_actions>
        <action>Locate all scripts, modules, and configs that read, write, or validate PATTERN_INDEX.yaml.</action>
        <action>Identify all code paths that generate or manipulate pattern specs, schemas, executors, examples, and tests.</action>
        <action>Identify all places where registration steps are described only in documentation or commit templates rather than being automated.</action>
        <action>Identify any health checks or consistency validators for the pattern registry (e.g., orphan detection, missing-schema checks, missing-executor checks) and note their coverage and limitations.</action>
        <action>Inspect CI/CD workflows, local scripts, or hooks that might run pattern validations, tests, or registry checks automatically.</action>
      </required_actions>
      <targets>
        <target>Manual processes (copy/paste flows, "run this script manually" docs, TODO notes, ad-hoc PowerShell invocations).</target>
        <target>Repetitive patterns (similar registration code duplicated in multiple scripts instead of a single reusable module).</target>
        <target>Missing validations (steps where humans can update registry/specs/schemas without automated checks).</target>
        <target>Incomplete workflows (e.g., batch script that creates specs but doesn’t update PATTERN_INDEX.yaml, or creates executors but not tests).</target>
        <target>Error-prone operations (manual editing of IDs, categories, paths, doc_id/pattern_id alignment, commit message contents).</target>
      </targets>
    </discovery_phase>

    <gap_identification_criteria>
      For each candidate gap in the pattern registration pipeline, evaluate:
      <criterion>Frequency: how often that step is likely to occur (per pattern, per batch, per commit, per release).</criterion>
      <criterion>Time cost: estimated human minutes/hours per execution.</criterion>
      <criterion>Error risk: likelihood of human error (High/Medium/Low), especially for ID formatting, registry sync, and cross-file alignment.</criterion>
      <criterion>Complexity: number of manual substeps and cognitive overhead.</criterion>
      <criterion>Automation feasibility: Trivial / Moderate / Complex, using existing tools (PowerShell, Python, CI, linters, etc.).</criterion>
      <criterion>ROI: rough (Time saved × Frequency) − Implementation cost.</criterion>
    </gap_identification_criteria>

    <evidence_collection>
      For every real gap you decide to report, capture:
      <![CDATA[
      Gap ID: GAP-PATREG-XXX
      Location: [file path(s), directory, or process name]
      Type: [Manual Workflow | Repetitive Code | Missing Validation | Incomplete Automation | Missing Health Check]
      Current State: [What code/docs currently do; include key steps]
      Problem: [Why this is inefficient, fragile, or error-prone in the context of pattern registration]
      Impact: [Time, risk, quality impacts, especially registry consistency and developer throughput]
      Evidence: [Relevant code snippets, command examples, function names, paths, or workflow descriptions]
      ]]>
    </evidence_collection>

    <recommendation_structure>
      For each gap, produce a corresponding recommendation block:
      <![CDATA[
      Gap ID: GAP-PATREG-XXX
      Priority: [Critical | High | Medium | Low]

      RECOMMENDATION:
        Title: [Short, action-oriented; e.g., "Automate Pattern ID Assignment from PATTERN_INDEX.yaml"]

        Solution:
          - Tool/Technology: [e.g., PowerShell module, Python script, CI workflow, pre-commit hook]
          - Implementation:
            * [Step-by-step design for the automation]
            * [Where to integrate (which script/module/CI job)]
            * [How to reuse or extend existing pattern automation scripts]
          - Integration point: [Specific files / dirs / workflows to touch; e.g., patterns/automation/register_pattern_batch.ps1, PATTERN_INDEX.yaml, validate_automation.py]

        Effort Estimate: [Rough hours or story points]

        Expected Benefits:
          - Time saved: [X minutes per pattern/batch, translated to X hours/month]
          - Error reduction: [e.g., X% fewer registry inconsistencies or ID mistakes]
          - Quality improvement: [e.g., increased test coverage, fewer orphaned patterns]

        Implementation Steps:
          1. [Concrete first step]
          2. [Next step]
          3. [...]

        Dependencies: [Pre-existing modules, CI infra, linters, etc.]

        Quick Win Potential: [Yes/No + one-line justification]
      ]]>
    </recommendation_structure>
  </analysis_framework>

  <!-- 3. REQUIRED SCANS SPECIFIC TO PATTERN REGISTRATION -->

  <required_scans>
    <scan id="S1_registry_integrity">
      <description>
        Analyze PATTERN_INDEX.yaml and all code that uses it.
        - Find all readers/writers (PowerShell, Python, other languages).
        - Detect any pattern where developers are expected to manually edit IDs, categories, or doc_id fields without automation.
        - Look for missing checks: e.g., no automation to detect:
          * Orphaned specs/schemas/executors/examples not referenced in PATTERN_INDEX.yaml
          * Registry entries that reference missing files
          * Duplicate or conflicting pattern IDs/doc IDs
      </description>
    </scan>

    <scan id="S2_manual_vs_scripted_steps">
      <description>
        Reconcile the documented manual process with the actual code:
        - For each manual phase (planning, ID generation, spec creation, schema, executor, examples, tests, docs, registry update, commit),
          identify whether there is:
          * Full automation
          * Partial automation
          * No automation
        - Highlight steps that remain entirely manual and are frequent (e.g., updating commit messages, updating multiple docs, syncing indices).
      </description>
    </scan>

    <scan id="S3_batch_registration_pipeline">
      <description>
        Deep dive into patterns/automation/register_pattern_batch.ps1 and related utilities:
        - Map each documented step of the automated registration process to actual functions / code paths.
        - Identify gaps where the batch script assumes humans will finish certain steps manually (e.g., documentation updates, test creation, advanced validation).
        - Check for missing safety nets (dry-run, rollback, idempotency, logging, summary reports).
        - Check test coverage for this pipeline and whether failures are surfaced in CI.
      </description>
    </scan>

    <scan id="S4_validation_and_tests">
      <description>
        Map out all validation and test coverage for pattern registration:
        - validate_automation.py and any other validators (what they actually validate).
        - Pester/pytest tests for:
          * pattern spec/schema correctness
          * executor behavior
          * registry integrity and detection of broken references
        - Identify any registration steps that are never automatically validated (e.g., doc tables of contents, category indexes, commit templates).
      </description>
    </scan>

    <scan id="S5_docs_vs_code_drift">
      <description>
        Compare documentation (Pattern Registration Process, EXEC-HYBRID-010-PATTERN-REGISTRATION-PIPELINE, system overviews, pattern catalogs)
        with actual code behavior:
        - Find promises in docs that are not enforced by code (e.g., "all patterns require spec+schema+executor+examples+tests+registry entry").
        - Identify opportunities to replace doc-only rules with automated checks or generators.
      </description>
    </scan>

    <scan id="S6_dev_workflow_integration">
      <description>
        Look at CI/CD workflows, scripts, and git-related automation:
        - Are there pre-commit hooks or CI jobs that:
          * Validate PATTERN_INDEX.yaml after changes?
          * Run pattern tests automatically for changed patterns?
          * Enforce commit templates for new patterns?
        - Identify missing automation that would enforce the registration process at commit or PR time.
      </description>
    </scan>
  </required_scans>

  <!-- 4. CONSTRAINTS & QUALITY GATES -->

  <constraints enforcement="strict">
    <mandatory_actions>
      <action>Base all conclusions on concrete code, scripts, configs, and docs you can see in the repo.</action>
      <action>When you infer behavior, explicitly mark it as an assumption and tie it to specific evidence.</action>
      <action>Respect existing architecture and tools; propose automation that fits into current PowerShell/Python/CI stack.</action>
      <action>Prioritize high-ROI, low-friction improvements first.</action>
    </mandatory_actions>
    <prohibited_behaviors>
      <behavior>Do NOT recommend vague actions like "add more tests" or "improve docs" without specifying exact targets and steps.</behavior>
      <behavior>Do NOT contradict documented SSOT without explicitly calling out and justifying the inconsistency.</behavior>
      <behavior>Do NOT ignore manual steps described in the Pattern Registration Process; every manual step must be evaluated for automation potential.</behavior>
    </prohibited_behaviors>
  </constraints>

  <quality_gates>
    <input_gates>
      <gate name="repo_scan_complete" requirement="high">
        Do not produce the final report until you have:
        - Traversed the patterns/ subtree (or equivalent) and located PATTERN_INDEX.yaml.
        - Identified at least the main registration scripts and validators.
      </gate>
    </input_gates>

    <process_gates>
      <gate name="traceability">
        Every reported gap must reference concrete file paths and/or functions or scripts.
      </gate>
      <gate name="prioritization">
        Ensure the final gap inventory is sorted by Priority (Critical/High/Medium/Low), with justification.
      </gate>
    </process_gates>

    <output_gates>
      <gate name="structure_compliance">
        Output must conform exactly to the JSON structure defined below in <output_format>.
      </gate>
      <gate name="coverage">
        Confirm you have evaluated:
        - Manual registration workflow
        - Automated registration workflow
        - Registry integrity & validation
        - Tests & CI integration
        - Documentation/commit templates related to patterns
      </gate>
    </output_gates>
  </quality_gates>

  <!-- 5. OUTPUT FORMAT (MACHINE-READABLE) -->

  <output_format>
    <format>JSON</format>
    <schema>
      <![CDATA[
      {
        "type": "object",
        "required": ["executive_summary", "gap_inventory", "detailed_recommendations", "implementation_roadmap", "analysis_metadata"],
        "properties": {
          "executive_summary": {
            "type": "object",
            "required": ["total_gaps", "critical_gaps", "high_quick_wins", "estimated_time_savings_hours_per_month", "estimated_implementation_effort_hours", "key_themes"],
            "properties": {
              "total_gaps": { "type": "integer" },
              "critical_gaps": { "type": "integer" },
              "high_quick_wins": { "type": "integer" },
              "estimated_time_savings_hours_per_month": { "type": "number" },
              "estimated_implementation_effort_hours": { "type": "number" },
              "key_themes": { "type": "array", "items": { "type": "string" } }
            }
          },
          "gap_inventory": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["gap_id", "type", "priority", "time_savings_hours_per_month", "effort_hours", "location", "title"],
              "properties": {
                "gap_id": { "type": "string" },
                "title": { "type": "string" },
                "type": { "type": "string" },
                "priority": { "type": "string", "enum": ["Critical", "High", "Medium", "Low"] },
                "time_savings_hours_per_month": { "type": "number" },
                "effort_hours": { "type": "number" },
                "location": { "type": "string" }
              }
            }
          },
          "detailed_recommendations": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["gap_id", "recommendation"],
              "properties": {
                "gap_id": { "type": "string" },
                "recommendation": { "type": "string" }
              }
            }
          },
          "implementation_roadmap": {
            "type": "object",
            "required": ["phase_1_quick_wins", "phase_2_high_impact", "phase_3_long_term"],
            "properties": {
              "phase_1_quick_wins": { "type": "array", "items": { "type": "string" } },
              "phase_2_high_impact": { "type": "array", "items": { "type": "string" } },
              "phase_3_long_term": { "type": "array", "items": { "type": "string" } }
            }
          },
          "analysis_metadata": {
            "type": "object",
            "required": ["scanned_paths", "timestamp", "notes"],
            "properties": {
              "scanned_paths": { "type": "array", "items": { "type": "string" } },
              "timestamp": { "type": "string" },
              "notes": { "type": "string" }
            }
          }
        }
      }
      ]]>
    </schema>
  </output_format>

  <!-- 6. EXECUTION INSTRUCTIONS -->

  <execution_instructions>
    <step>Scan the repository and locate the pattern system root (patterns/ or equivalent).</step>
    <step>Map both documented workflows (manual & automated) to actual code, scripts, and configs.</step>
    <step>Run all REQUIRED SCANS (S1–S6), collecting candidate gaps across manual steps, scripts, tests, CI, and docs.</step>
    <step>Filter out trivial or non-actionable observations; keep only gaps where automation would change real behavior or risk.</step>
    <step>For each remaining gap, fully populate a GAP-PATREG-XXX record and its recommendation block.</step>
    <step>Prioritize gaps and assemble the final JSON output object following the schema above.</step>
    <step>Validate your JSON for structural correctness before returning it as the final answer.</step>
  </execution_instructions>

</automation_gap_prompt>
