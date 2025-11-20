<AGENT_OPERATIONS_SPEC version="1.0.0">

    <THOUGHT_PROCESS>
        <MAPPING_PROMPT_RENDERING>
            <ENTRY id="1">
                <SOURCE_CONCEPT>clarity_context_constraints_triads</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/PRINCIPLES/CLARITY_CONTEXT_CONSTRAINTS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="2">
                <SOURCE_CONCEPT>role_persona_assignment</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/PRINCIPLES/ROLE_AND_PERSONA</TARGET_PATH>
            </ENTRY>
            <ENTRY id="3">
                <SOURCE_CONCEPT>xml_ish_tagged_thinking</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/MANDATORY_STRUCTURES/SECTION_DEFINITIONS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="4">
                <SOURCE_CONCEPT>chain_of_thought_stepwise_reasoning</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/PRINCIPLES/REASONING_MODES</TARGET_PATH>
            </ENTRY>
            <ENTRY id="5">
                <SOURCE_CONCEPT>workstream_v1_1_template</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/MANDATORY_STRUCTURES/WORKSTREAM_PROMPT_TEMPLATE</TARGET_PATH>
            </ENTRY>
            <ENTRY id="6">
                <SOURCE_CONCEPT>aider_tuned_prompt_shape</SOURCE_CONCEPT>
                <TARGET_PATH>PROMPT_RENDERING_SPEC/MANDATORY_STRUCTURES/TOOL_SPECIFIC_VIEWS/AIDER_VIEW</TARGET_PATH>
            </ENTRY>
        </MAPPING_PROMPT_RENDERING>

        <MAPPING_TASK_ROUTING>
            <ENTRY id="1">
                <SOURCE_CONCEPT>central_router_orchestrator</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/ARCHITECTURE_AWARENESS/CENTRAL_ROUTER</TARGET_PATH>
            </ENTRY>
            <ENTRY id="2">
                <SOURCE_CONCEPT>contract_first_capability_declarations</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/ARCHITECTURE_AWARENESS/CAPABILITY_REGISTRY</TARGET_PATH>
            </ENTRY>
            <ENTRY id="3">
                <SOURCE_CONCEPT>decision_trees_based_on_classification</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/INTAKE_AND_ANALYSIS_PROTOCOL/TASK_CLASSIFICATION</TARGET_PATH>
            </ENTRY>
            <ENTRY id="4">
                <SOURCE_CONCEPT>hexagonal_bounded_contexts</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/ARCHITECTURE_AWARENESS/BOUNDARIES_AND_CONTEXTS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="5">
                <SOURCE_CONCEPT>timeout_error_circuit_breakers</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/EXECUTION_SAFETY/CIRCUIT_BREAKERS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="6">
                <SOURCE_CONCEPT>router_config_from_prompt_improve</SOURCE_CONCEPT>
                <TARGET_PATH>TASK_ROUTING_SPEC/CONFIG_MODEL/ROUTER_CONFIG_YAML</TARGET_PATH>
            </ENTRY>
        </MAPPING_TASK_ROUTING>

        <MAPPING_PATCH_MANAGEMENT>
            <ENTRY id="1">
                <SOURCE_CONCEPT>unified_diff_as_primary_artifact</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/CODE_GENERATION_STANDARDS/PATCH_AS_CANONICAL_CHANGE</TARGET_PATH>
            </ENTRY>
            <ENTRY id="2">
                <SOURCE_CONCEPT>feature_flags_and_guarded_rollout</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/VALIDATION_AND_ROLLBACK/FEATURE_FLAG_ROLLOUT</TARGET_PATH>
            </ENTRY>
            <ENTRY id="3">
                <SOURCE_CONCEPT>rollback_plan_with_quarantine</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/VALIDATION_AND_ROLLBACK/ROLLBACK_STRATEGY</TARGET_PATH>
            </ENTRY>
            <ENTRY id="4">
                <SOURCE_CONCEPT>ci_pipeline_for_patch_check</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/VALIDATION_AND_ROLLBACK/CI_INTEGRATION_PIPELINE</TARGET_PATH>
            </ENTRY>
            <ENTRY id="5">
                <SOURCE_CONCEPT>minimal_file_creation_and_scope_limits</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/CODE_GENERATION_STANDARDS/SCOPE_AND_FILE_CREATION_LIMITS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="6">
                <SOURCE_CONCEPT>locked_workstreams_and_protected_paths</SOURCE_CONCEPT>
                <TARGET_PATH>PATCH_MANAGEMENT_SPEC/CODE_GENERATION_STANDARDS/PROTECTED_AREAS</TARGET_PATH>
            </ENTRY>
        </MAPPING_PATCH_MANAGEMENT>

        <MAPPING_COOPERATION>
            <ENTRY id="1">
                <SOURCE_CONCEPT>orchestrator_db_state_machine</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/ORCHESTRATOR_CONTRACT/STATE_MODEL</TARGET_PATH>
            </ENTRY>
            <ENTRY id="2">
                <SOURCE_CONCEPT>queue_inbox_task_jsonl</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/QUEUE_CONTRACT/TASK_ENQUEUE_PROTOCOL</TARGET_PATH>
            </ENTRY>
            <ENTRY id="3">
                <SOURCE_CONCEPT>background_workers_per_worktree</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/BACKGROUND_WORKER_CONTRACT/WORKER_BEHAVIOR</TARGET_PATH>
            </ENTRY>
            <ENTRY id="4">
                <SOURCE_CONCEPT>validation_gates_edit_static_runtime</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/ORCHESTRATOR_CONTRACT/PIPELINE_STAGES</TARGET_PATH>
            </ENTRY>
            <ENTRY id="5">
                <SOURCE_CONCEPT>prohibited_cross_scope_edits</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/PROHIBITED_BEHAVIORS/OUT_OF_SCOPE_EDITS</TARGET_PATH>
            </ENTRY>
            <ENTRY id="6">
                <SOURCE_CONCEPT>phase_plan_parallel_workstreams</SOURCE_CONCEPT>
                <TARGET_PATH>COOPERATION_SPEC/ORCHESTRATOR_CONTRACT/PHASE_PLAN_EXECUTION</TARGET_PATH>
            </ENTRY>
        </MAPPING_COOPERATION>
    </THOUGHT_PROCESS>

    <PROMPT_RENDERING_SPEC>

        <PRINCIPLES>
            <PRINCIPLE id="precision_principle">
                <NAME>precision_principle</NAME>
                <SUMMARY>All prompts must be unambiguous, constrained, and operationally specific.</SUMMARY>
                <RULES>
                    <RULE>Specify exact goals, not vague intentions.</RULE>
                    <RULE>Specify environment, repo, and file scope explicitly.</RULE>
                    <RULE>Specify output format and success criteria.</RULE>
                </RULES>
            </PRINCIPLE>

            <PRINCIPLE id="clarity_context_constraints">
                <NAME>clarity_context_constraints</NAME>
                <SUMMARY>Every prompt must explicitly encode clarity, context, and constraints.</SUMMARY>
                <COMPONENTS>
                    <COMPONENT id="clarity">Describe the requested change or analysis in concrete, itemized terms.</COMPONENT>
                    <COMPONENT id="context">Describe project, architecture, dependencies, and triggering events.</COMPONENT>
                    <COMPONENT id="constraints">Describe forbidden behaviors, limits, and formatting requirements.</COMPONENT>
                </COMPONENTS>
            </PRINCIPLE>

            <PRINCIPLE id="role_and_persona">
                <NAME>role_and_persona</NAME>
                <SUMMARY>Every workstream must assign an explicit role/persona to the executing agent.</SUMMARY>
                <RULES>
                    <RULE>Use senior_engineer style personas aligned to the domain (e.g. senior_python_engineer).</RULE>
                    <RULE>Role must emphasize safety, incrementalism, and test-centric behavior.</RULE>
                </RULES>
            </PRINCIPLE>

            <PRINCIPLE id="structured_sections">
                <NAME>structured_sections</NAME>
                <SUMMARY>Use consistent, ASCII-safe section delimiters for all prompts.</SUMMARY>
                <RULES>
                    <RULE>Use bracketed, uppercase section headers: [HEADER], [OBJECTIVE], [CONTEXT], [FILE_SCOPE], [TASKS], [CONSTRAINTS], [EXPECTED_OUTPUT], [VALIDATION_PLAN], [NEXT_STEPS].</RULE>
                    <RULE>Do not invent new top-level section names without orchestrator contract change.</RULE>
                    <RULE>Internal formatting must use numbered lists and bullet lists, not free-form paragraphs.</RULE>
                </RULES>
            </PRINCIPLE>

            <PRINCIPLE id="chain_of_thought_modes">
                <NAME>chain_of_thought_modes</NAME>
                <SUMMARY>Use explicit reasoning modes with controlled verbosity.</SUMMARY>
                <MODES>
                    <MODE id="plan_then_execute">First emit a short, structured plan; then implement edits according to that plan.</MODE>
                    <MODE id="minimal_visible_cot">Keep reasoning concise and primarily in the planning section; avoid verbose commentary in final answers.</MODE>
                    <MODE id="debug_diagnostic">When tasks fail or context is inconsistent, switch to diagnostic reasoning with explicit problem hypotheses.</MODE>
                </MODES>
            </PRINCIPLE>

            <PRINCIPLE id="tool_neutral_core">
                <NAME>tool_neutral_core</NAME>
                <SUMMARY>All workstreams use a tool-neutral core prompt that can be consumed by any CLI agent.</SUMMARY>
                <RULES>
                    <RULE>Do not embed Aider-specific slash commands or Codex-specific syntax into the core template.</RULE>
                    <RULE>Tool-specific hints must live in the EXECUTION_NOTES_FOR_ROUTER or TOOL_VIEW layers.</RULE>
                </RULES>
            </PRINCIPLE>

            <PRINCIPLE id="ascii_only">
                <NAME>ascii_only</NAME>
                <SUMMARY>All prompts rendered for CLI tools must be pure ASCII.</SUMMARY>
                <RULES>
                    <RULE>Do not use emojis, smart quotes, non-ASCII bullets, or unicode arrows.</RULE>
                    <RULE>Use plain characters like "-", ">", "->", "(c)" instead of unicode equivalents.</RULE>
                </RULES>
            </PRINCIPLE>

            <PRINCIPLE id="file_scope_first">
                <NAME>file_scope_first</NAME>
                <SUMMARY>File scope must be specified before operations.</SUMMARY>
                <RULES>
                    <RULE>Always define FILE_SCOPE (files_scope and files_may_create) before listing TASKS.</RULE>
                    <RULE>Tasks must not reference files outside declared scope except as read-only context.</RULE>
                </RULES>
            </PRINCIPLE>
        </PRINCIPLES>

        <MANDATORY_STRUCTURES>

            <SECTION_DEFINITIONS>
                <SECTION id="HEADER">
                    <FIELDS>
                        <FIELD>WORKSTREAM_ID</FIELD>
                        <FIELD>PHASE_ID</FIELD>
                        <FIELD>REPO_ROOT</FIELD>
                        <FIELD>ENTRY_FILES</FIELD>
                        <FIELD>CALLING_APP</FIELD>
                        <FIELD>TARGET_APP</FIELD>
                        <FIELD>CLASSIFICATION</FIELD>
                        <FIELD>RISK_LEVEL</FIELD>
                    </FIELDS>
                </SECTION>
                <SECTION id="OBJECTIVE">
                    <REQUIREMENT>Provide 1-3 sentences describing the exact goal and success criteria.</REQUIREMENT>
                </SECTION>
                <SECTION id="CONTEXT">
                    <REQUIREMENT>Provide structured bullet points describing project, existing behavior, architecture, and triggering change.</REQUIREMENT>
                </SECTION>
                <SECTION id="FILE_SCOPE">
                    <FIELDS>
                        <FIELD>files_scope</FIELD>
                        <FIELD>files_may_create</FIELD>
                    </FIELDS>
                    <RULE>List concrete paths or globs under files_scope that this workstream is allowed to modify.</RULE>
                    <RULE>List only minimal necessary new files under files_may_create.</RULE>
                </SECTION>
                <SECTION id="TASKS">
                    <REQUIREMENT>List numbered, atomic tasks; each must be executable independently.</REQUIREMENT>
                </SECTION>
                <SECTION id="CONSTRAINTS">
                    <REQUIREMENT>List safety and style constraints; include minimalism, no large-scale rewrites, and test-first behavior where applicable.</REQUIREMENT>
                </SECTION>
                <SECTION id="EXPECTED_OUTPUT">
                    <REQUIREMENT>Describe expected artifacts (patch, updated files, logs, test results) and required summary structure.</REQUIREMENT>
                </SECTION>
                <SECTION id="VALIDATION_PLAN">
                    <REQUIREMENT>Describe static checks, tests, or scripts to run for this workstream.</REQUIREMENT>
                </SECTION>
                <SECTION id="NEXT_STEPS">
                    <REQUIREMENT>Describe follow-up work or dependencies for subsequent workstreams.</REQUIREMENT>
                </SECTION>
                <SECTION id="EXECUTION_NOTES_FOR_ROUTER">
                    <REQUIREMENT>Provide hints for router on tool choice, risk, and retry behavior.</REQUIREMENT>
                </SECTION>
            </SECTION_DEFINITIONS>

            <WORKSTREAM_PROMPT_TEMPLATE>
                <CORE_TEMPLATE id="workstream_prompt_v1">
                    <FORMAT>ascii_text</FORMAT>
                    <DELIMITERS>
                        <START>=== WORKSTREAM_PROMPT v1 START ===</START>
                        <END>=== WORKSTREAM_PROMPT v1 END ===</END>
                    </DELIMITERS>
                    <RENDER_ORDER>
                        <ITEM>[HEADER]</ITEM>
                        <ITEM>[OBJECTIVE]</ITEM>
                        <ITEM>[CONTEXT]</ITEM>
                        <ITEM>[FILE_SCOPE]</ITEM>
                        <ITEM>[TASKS]</ITEM>
                        <ITEM>[CONSTRAINTS]</ITEM>
                        <ITEM>[EXPECTED_OUTPUT]</ITEM>
                        <ITEM>[VALIDATION_PLAN]</ITEM>
                        <ITEM>[NEXT_STEPS]</ITEM>
                        <ITEM>[EXECUTION_NOTES_FOR_ROUTER]</ITEM>
                    </RENDER_ORDER>
                </CORE_TEMPLATE>
            </WORKSTREAM_PROMPT_TEMPLATE>

            <TOOL_SPECIFIC_VIEWS>
                <AIDER_VIEW id="workstream_aider_v1_1">
                    <BASE_TEMPLATE_REF>workstream_prompt_v1</BASE_TEMPLATE_REF>
                    <SPECIAL_RULES>
                        <RULE>ENTRY_FILES must map directly to Aider CLI positional file arguments.</RULE>
                        <RULE>Do not ask the model to call `/add` inside the prompt; files are loaded via CLI.</RULE>
                        <RULE>Explain diff expectations: small, patch-friendly, incremental changes.</RULE>
                        <RULE>Prohibit wholesale rewrites of entire modules unless explicitly requested.</RULE>
                    </SPECIAL_RULES>
                </AIDER_VIEW>
                <CODEX_VIEW id="workstream_codex_v1">
                    <BASE_TEMPLATE_REF>workstream_prompt_v1</BASE_TEMPLATE_REF>
                    <SPECIAL_RULES>
                        <RULE>Include explicit instructions for verification (tests, scripts) suitable for Codex CLI.</RULE>
                        <RULE>Keep instructions compact to respect Codex token budget.</RULE>
                    </SPECIAL_RULES>
                </CODEX_VIEW>
                <CLAUDE_CODE_VIEW id="workstream_claude_code_v1">
                    <BASE_TEMPLATE_REF>workstream_prompt_v1</BASE_TEMPLATE_REF>
                    <SPECIAL_RULES>
                        <RULE>Request an explicit plan section in [TASKS] before detailed code edits.</RULE>
                        <RULE>Encourage self-check and summarization in [EXPECTED_OUTPUT].</RULE>
                    </SPECIAL_RULES>
                </CLAUDE_CODE_VIEW>
            </TOOL_SPECIFIC_VIEWS>

            <MESSAGE_FILE_FORMAT>
                <STORAGE_RULES>
                    <RULE>Each workstream prompt must be written to a dedicated message file on disk.</RULE>
                    <RULE>Message files must use ASCII encoding (UTF-8 without non-ASCII characters).</RULE>
                    <RULE>Filename pattern: ws_{WORKSTREAM_ID}_prompt_v1.txt</RULE>
                    <RULE>Message files are read-only instructions; tools must not overwrite them.</RULE>
                </STORAGE_RULES>
            </MESSAGE_FILE_FORMAT>

            <CLASSIFICATION_BLOCK>
                <FIELDS>
                    <FIELD>complexity_level</FIELD>
                    <FIELD>risk_level</FIELD>
                    <FIELD>domain</FIELD>
                    <FIELD>operation_type</FIELD>
                    <FIELD>estimated_runtime_minutes</FIELD>
                </FIELDS>
                <ENUMS>
                    <complexity_level>
                        <VALUE>simple</VALUE>
                        <VALUE>moderate</VALUE>
                        <VALUE>complex</VALUE>
                        <VALUE>enterprise</VALUE>
                    </complexity_level>
                    <risk_level>
                        <VALUE>low</VALUE>
                        <VALUE>medium</VALUE>
                        <VALUE>high</VALUE>
                        <VALUE>critical</VALUE>
                    </risk_level>
                    <domain>
                        <VALUE>code</VALUE>
                        <VALUE>docs</VALUE>
                        <VALUE>infra</VALUE>
                        <VALUE>analysis</VALUE>
                    </domain>
                    <operation_type>
                        <VALUE>refactor</VALUE>
                        <VALUE>bugfix</VALUE>
                        <VALUE>feature</VALUE>
                        <VALUE>analysis_only</VALUE>
                        <VALUE>test_only</VALUE>
                    </operation_type>
                </ENUMS>
            </CLASSIFICATION_BLOCK>

            <RENDERING_PIPELINE>
                <STEPS>
                    <STEP id="1">Receive workstream bundle (JSON) from orchestrator.</STEP>
                    <STEP id="2">Validate bundle against workstream.schema.json.</STEP>
                    <STEP id="3">Derive classification and risk metadata.</STEP>
                    <STEP id="4">Populate CORE_TEMPLATE fields with bundle data.</STEP>
                    <STEP id="5">Apply TOOL_SPECIFIC_VIEW if target tool is known.</STEP>
                    <STEP id="6">Write rendered prompt to message file with ASCII-only constraints.</STEP>
                    <STEP id="7">Return message file path to router/orchestrator.</STEP>
                </STEPS>
            </RENDERING_PIPELINE>
        </MANDATORY_STRUCTURES>
    </PROMPT_RENDERING_SPEC>

    <TASK_ROUTING_SPEC>

        <ARCHITECTURE_AWARENESS>
            <CENTRAL_ROUTER>
                <RESPONSIBILITY>Map incoming tasks to appropriate tools and execution flows.</RESPONSIBILITY>
                <INPUTS>
                    <INPUT>task_description</INPUT>
                    <INPUT>workstream_bundle_id</INPUT>
                    <INPUT>classification_metadata</INPUT>
                    <INPUT>phase_plan_context</INPUT>
                </INPUTS>
                <OUTPUTS>
                    <OUTPUT>selected_tool</OUTPUT>
                    <OUTPUT>tool_config_profile</OUTPUT>
                    <OUTPUT>message_file_path</OUTPUT>
                    <OUTPUT>execution_limits</OUTPUT>
                </OUTPUTS>
            </CENTRAL_ROUTER>

            <CAPABILITY_REGISTRY>
                <BACKING_STORE>aim_registry_or_tool_profiles_json</BACKING_STORE>
                <FIELDS>
                    <FIELD>tool_id</FIELD>
                    <FIELD>capabilities</FIELD>
                    <FIELD>languages</FIELD>
                    <FIELD>max_context_tokens</FIELD>
                    <FIELD>supports_patches</FIELD>
                    <FIELD>supports_runtime_execution</FIELD>
                </FIELDS>
                <EXAMPLE_ENTRY>
                    <tool_id>aider</tool_id>
                    <capabilities>
                        <capability>code_refactor</capability>
                        <capability>bugfix</capability>
                    </capabilities>
                    <languages>
                        <language>python</language>
                        <language>powershell</language>
                    </languages>
                    <max_context_tokens>high</max_context_tokens>
                    <supports_patches>true</supports_patches>
                    <supports_runtime_execution>false</supports_runtime_execution>
                </EXAMPLE_ENTRY>
            </CAPABILITY_REGISTRY>

            <BOUNDARIES_AND_CONTEXTS>
                <RULE>Respect repository boundaries: do not route tasks across repos unless explicitly configured.</RULE>
                <RULE>Respect phase boundaries: some tools may only be allowed for specific phases (design, refactor, test).</RULE>
                <RULE>Respect security boundaries: tools may be restricted from touching sensitive modules.</RULE>
            </BOUNDARIES_AND_CONTEXTS>

            <CONFIG_MODEL>
                <ROUTER_CONFIG_YAML>
                    <KEYS>
                        <KEY>apps</KEY>
                        <KEY>routing_rules</KEY>
                        <KEY>timeouts</KEY>
                        <KEY>logging</KEY>
                        <KEY>queue_backends</KEY>
                    </KEYS>
                </ROUTER_CONFIG_YAML>
            </CONFIG_MODEL>
        </ARCHITECTURE_AWARENESS>

        <INTAKE_AND_ANALYSIS_PROTOCOL>
            <TASK_CLASSIFICATION>
                <STEPS>
                    <STEP id="1">Parse workstream bundle and classification block.</STEP>
                    <STEP id="2">Derive domain, operation_type, complexity_level, risk_level.</STEP>
                    <STEP id="3">Detect special flags: migration, hotfix, experimental, docs_only.</STEP>
                    <STEP id="4">Store classification in orchestrator DB for auditing.</STEP>
                </STEPS>
            </TASK_CLASSIFICATION>

            <TOOL_SELECTION_RULES>
                <RULE id="1">If domain=code and operation_type in (refactor, bugfix) and risk_level in (low, medium), prefer Aider.</RULE>
                <RULE id="2">If complexity_level in (complex, enterprise) or cross_language, consider Codex or Claude Code.</RULE>
                <RULE id="3">If domain=docs or operation_type=analysis_only, route to analysis-capable LLM with minimal filesystem access.</RULE>
                <RULE id="4">If runtime_execution_required=true, route through tools that can run tests or scripts via shell.</RULE>
            </TOOL_SELECTION_RULES>

            <EXECUTION_SAFETY>
                <CIRCUIT_BREAKERS>
                    <PARAMETERS>
                        <PARAMETER>max_retries_per_tool</PARAMETER>
                        <PARAMETER>max_total_runtime_minutes_per_workstream</PARAMETER>
                        <PARAMETER>max_consecutive_failures_per_phase</PARAMETER>
                    </PARAMETERS>
                    <BEHAVIOR>
                        <RULE>On repeated failure of one tool, escalate to alternate tool or halt with quarantine.</RULE>
                        <RULE>On runtime exceeding threshold, terminate worker and mark task as timed_out.</RULE>
                    </BEHAVIOR>
                </CIRCUIT_BREAKERS>
                <TIMEOUTS>
                    <DEFAULT_EDIT_TIMEOUT_MINUTES>60</DEFAULT_EDIT_TIMEOUT_MINUTES>
                    <DEFAULT_STATIC_TIMEOUT_MINUTES>30</DEFAULT_STATIC_TIMEOUT_MINUTES>
                    <DEFAULT_RUNTIME_TIMEOUT_MINUTES>60</DEFAULT_RUNTIME_TIMEOUT_MINUTES>
                </TIMEOUTS>
            </EXECUTION_SAFETY>

            <DELEGATION_AND_RETRY>
                <DELEGATION_RULES>
                    <RULE>Allow router to chain tasks: PLAN tool → EDIT tool → REVIEW tool as separate workstreams.</RULE>
                    <RULE>Do not silently switch tools without recording delegation in orchestrator DB.</RULE>
                </DELEGATION_RULES>
                <RETRY_POLICY>
                    <RULE>On minor errors (e.g., transient network issues), retry up to configured max_retries.</RULE>
                    <RULE>On deterministic logical failures (tests fail due to incorrect behavior), create new fix workstream rather than blind retry.</RULE>
                </RETRY_POLICY>
            </DELEGATION_AND_RETRY>
        </INTAKE_AND_ANALYSIS_PROTOCOL>
    </TASK_ROUTING_SPEC>

    <PATCH_MANAGEMENT_SPEC>

        <CODE_GENERATION_STANDARDS>
            <PATCH_AS_CANONICAL_CHANGE>
                <RULE>Unified diff patch files are the canonical representation of code changes between tools and environments.</RULE>
                <RULE>Every successful workstream must produce either 0 patches (no-op) or 1+ scoped patch files.</RULE>
                <RULE>Patches must be associated with task_id, workstream_id, and source_tool_id.</RULE>
            </PATCH_AS_CANONICAL_CHANGE>

            <PATCH_METADATA_SCHEMA>
                <FIELDS>
                    <FIELD>patch_id</FIELD>
                    <FIELD>task_id</FIELD>
                    <FIELD>workstream_id</FIELD>
                    <FIELD>source_tool</FIELD>
                    <FIELD>target_repo</FIELD>
                    <FIELD>base_commit</FIELD>
                    <FIELD>created_at_utc</FIELD>
                    <FIELD>summary</FIELD>
                    <FIELD>classification</FIELD>
                    <FIELD>risk_level</FIELD>
                </FIELDS>
            </PATCH_METADATA_SCHEMA>

            <SCOPE_AND_FILE_CREATION_LIMITS>
                <RULE>Each patch should focus on a limited set of files consistent with FILE_SCOPE.</RULE>
                <RULE>Do not create large numbers of new files in one patch; prefer incremental introduction.</RULE>
                <RULE>Do not mix unrelated changes (e.g., refactor + feature) in a single patch.</RULE>
            </SCOPE_AND_FILE_CREATION_LIMITS>

            <PROTECTED_AREAS>
                <RULE>Orchestrator maintains a registry of locked workstreams and protected paths.</RULE>
                <RULE>Before applying a patch, validate that no hunks touch locked or protected areas.</RULE>
                <RULE>Reject or quarantine patches that violate protected area constraints.</RULE>
            </PROTECTED_AREAS>

            <PATCH_FILE_NAMING>
                <RULE>Use naming pattern: {task_id}_{workstream_id}_{short_summary}.patch</RULE>
                <RULE>Store patches in a dedicated directory (e.g., .patches/ or .artifacts/patches/).</RULE>
            </PATCH_FILE_NAMING>
        </CODE_GENERATION_STANDARDS>

        <VALIDATION_AND_ROLLBACK>
            <CI_INTEGRATION_PIPELINE>
                <PIPELINE_STEPS>
                    <STEP id="1">Run git apply --check to validate patch consistency against target branch.</STEP>
                    <STEP id="2">Run static linters and formatters on affected files.</STEP>
                    <STEP id="3">Run targeted tests relevant to changed modules.</STEP>
                    <STEP id="4">If all checks pass, apply patch and commit with AI-tagged message.</STEP>
                    <STEP id="5">If any check fails, quarantine patch for manual or automated fix-loop.</STEP>
                </PIPELINE_STEPS>
            </CI_INTEGRATION_PIPELINE>

            <ROLLBACK_STRATEGY>
                <RULE>Patch application must be reversible either via git revert or reverse patches.</RULE>
                <RULE>Orchestrator must record base_commit and post_apply_commit for every patch application.</RULE>
                <RULE>In case of regression, orchestrator can roll back to base_commit or apply reverse patch.</RULE>
            </ROLLBACK_STRATEGY>

            <FEATURE_FLAG_ROLLOUT>
                <RULE>For risky behavioral changes, prefer implementing behind feature flags.</RULE>
                <RULE>Patches introducing feature flags must include documentation on enabling and disabling them.</RULE>
            </FEATURE_FLAG_ROLLOUT>

            <QUARANTINE_POLICY>
                <RULE>Patches that fail validation are stored with status=quarantined and not applied automatically.</RULE>
                <RULE>Quarantined patches can be used as input for follow-up fix workstreams.</RULE>
            </QUARANTINE_POLICY>
        </VALIDATION_AND_ROLLBACK>
    </PATCH_MANAGEMENT_SPEC>

    <COOPERATION_SPEC>

        <ORCHESTRATOR_CONTRACT>
            <STATE_MODEL>
                <STATES>
                    <STATE>pending</STATE>
                    <STATE>running</STATE>
                    <STATE>completed</STATE>
                    <STATE>failed</STATE>
                    <STATE>timed_out</STATE>
                    <STATE>quarantined</STATE>
                </STATES>
                <TRANSITIONS>
                    <TRANSITION>pending -> running</TRANSITION>
                    <TRANSITION>running -> completed</TRANSITION>
                    <TRANSITION>running -> failed</TRANSITION>
                    <TRANSITION>running -> timed_out</TRANSITION>
                    <TRANSITION>failed -> quarantined</TRANSITION>
                </TRANSITIONS>
            </STATE_MODEL>

            <PIPELINE_STAGES>
                <STAGE id="EDIT">Perform code modifications according to workstream prompt.</STAGE>
                <STAGE id="STATIC">Run static analysis and formatting tools.</STAGE>
                <STAGE id="RUNTIME">Run tests or scripts that execute code.</STAGE>
            </PIPELINE_STAGES>

            <PHASE_PLAN_EXECUTION>
                <RULE>Orchestrator reads phase plan describing workstreams, dependencies, and tools.</RULE>
                <RULE>Workstreams with no unmet dependencies may run in parallel up to max_parallel_workstreams.</RULE>
                <RULE>Completion of a workstream updates dependency graph and may unlock downstream workstreams.</RULE>
            </PHASE_PLAN_EXECUTION>

            <ARTIFACT_LOGGING>
                <ARTIFACT>workstream_bundle_json</ARTIFACT>
                <ARTIFACT>rendered_prompt_message_file</ARTIFACT>
                <ARTIFACT>tool_stdout_stderr_log</ARTIFACT>
                <ARTIFACT>patch_files</ARTIFACT>
                <ARTIFACT>validation_reports</ARTIFACT>
            </ARTIFACT_LOGGING>
        </ORCHESTRATOR_CONTRACT>

        <QUEUE_CONTRACT>
            <TASK_ENQUEUE_PROTOCOL>
                <INPUT_FORMAT>JSON_line</INPUT_FORMAT>
                <FIELDS>
                    <FIELD>tool</FIELD>
                    <FIELD>script</FIELD>
                    <FIELD>args</FIELD>
                    <FIELD>cwd</FIELD>
                    <FIELD>task_id</FIELD>
                </FIELDS>
                <FLOW>
                    <STEP>SubmitTask.ps1 creates JSON line and appends to .tasks/inbox/tasks.jsonl.</STEP>
                    <STEP>QueueWorker reads tasks.jsonl and spawns appropriate tool using tool registry.</STEP>
                </FLOW>
            </TASK_ENQUEUE_PROTOCOL>

            <TASK_DIRECTORIES>
                <DIRECTORY>.tasks/inbox</DIRECTORY>
                <DIRECTORY>.tasks/processing</DIRECTORY>
                <DIRECTORY>.tasks/completed</DIRECTORY>
                <DIRECTORY>.tasks/failed</DIRECTORY>
            </TASK_DIRECTORIES>
        </QUEUE_CONTRACT>

        <BACKGROUND_WORKER_CONTRACT>
            <WORKER_BEHAVIOR>
                <RULE>Each worker is bound to a worktree and a task_id.</RULE>
                <RULE>Workers must write stdout/stderr logs to .runs/{task_id}/stdout-stderr.log.</RULE>
                <RULE>Workers must exit with status code indicating success or failure.</RULE>
            </WORKER_BEHAVIOR>

            <WORKTREE_MANAGEMENT>
                <RULE>For each workstream, create a dedicated git worktree and branch.</RULE>
                <RULE>Name pattern: branch=ws/{PHASE_ID}/{WORKSTREAM_ID}, path=worktrees/{PHASE_ID}-{WORKSTREAM_ID}.</RULE>
                <RULE>On completion, orchestrator may merge, push, and create PRs from these branches.</RULE>
            </WORKTREE_MANAGEMENT>
        </BACKGROUND_WORKER_CONTRACT>

        <PROHIBITED_BEHAVIORS>
            <OUT_OF_SCOPE_EDITS>
                <RULE>Do not modify files outside FILE_SCOPE unless explicitly permitted.</RULE>
                <RULE>Do not touch orchestrator state files, queue files, or registry files unless specifically tasked.</RULE>
            </OUT_OF_SCOPE_EDITS>

            <UNSAFE_OPERATIONS>
                <RULE>Do not delete large directories or perform destructive operations without explicit, scoped instructions.</RULE>
                <RULE>Do not bypass validation gates (static or runtime) when applying patches.</RULE>
            </UNSAFE_OPERATIONS>

            <SPEC_MUTATION>
                <RULE>Do not alter this Agent Operations Spec from within workstreams.</RULE>
                <RULE>Changes to this spec must be performed via explicit governance workstreams.</RULE>
            </SPEC_MUTATION>

            <LOG_TAMPERING>
                <RULE>Do not modify or delete logs in .runs/, .tasks/, or orchestrator DB.</RULE>
            </LOG_TAMPERING>
        </PROHIBITED_BEHAVIORS>
    </COOPERATION_SPEC>

</AGENT_OPERATIONS_SPEC>
