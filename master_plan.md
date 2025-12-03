{
  "plan_id": "EXECUTION_AND_SAVING_ONE_SHOT_PLAN_V1",
  "version": "0.1.0",
  "description": "Blueprint for one-shot creation of the execution engine and saving (Git) stages, including phases, global services, document suites, I/O contracts, routing, and Git automation.",
  "meta": {
    "owner": "pipeline-core",
    "status": "draft",
    "created_at": null,
    "last_updated_at": null,
    "notes": [
      "This document defines WHAT will exist (structures, files, contracts), not their content.",
      "Actual file creation and detailed writing happens later, after this plan is stable."
    ]
  },
  "phases": [
    {
      "phase_id": "PH0_PLANNING",
      "name": "Planning",
      "section": "PLANNING",
      "role": "Convert specs/PM inputs into structured work",
      "status": "planned",
      "root_folder": "PH0_PLANNING/",
      "key_artifacts": {
        "docs": [],
        "schemas": []
      }
    },
    {
      "phase_id": "PH1_PLAN_TO_EXEC",
      "name": "Plan to Execution Bridge",
      "section": "PLANNING",
      "role": "Emit executable phase_plan JSON from planning artifacts",
      "status": "planned",
      "root_folder": "PH1_PLAN_TO_EXEC/",
      "key_artifacts": {
        "docs": [
          "IOC_PLANNING_TO_EXEC.md"
        ],
        "schemas": [
          "phase_plan.v1.json"
        ]
      }
    },
    {
      "phase_id": "PH2_EXECUTION_ENGINE",
      "name": "Execution Engine",
      "section": "EXECUTION",
      "role": "Run phase plans and orchestrate tools to modify repo state",
      "status": "planned",
      "root_folder": "PH2_EXECUTION_ENGINE/",
      "key_artifacts": {
        "docs": [
          "PHASE_DAG_OVERVIEW.md",
          "PHASE_DAG_LIBRARY.md",
          "PHASE_DAG_MAPPING.md"
        ],
        "schemas": [
          "dag_graph.v1.json",
          "dag_library.v1.json",
          "dag_mapping_rules.v1.json",
          "execution_result.v1.json"
        ],
        "phase_manifest_files": [
          "phase.manifest.json",
          "phase.contracts.json"
        ]
      }
    },
    {
      "phase_id": "PH3_EXEC_TO_ERROR",
      "name": "Execution to Error Bridge",
      "section": "EXECUTION",
      "role": "Translate execution results into error-check targets",
      "status": "planned",
      "root_folder": "PH3_EXEC_TO_ERROR/",
      "key_artifacts": {
        "docs": [
          "IOC_EXEC_TO_ERROR.md"
        ],
        "schemas": [
          "error_check_targets.v1.json"
        ]
      }
    },
    {
      "phase_id": "PH4_ERROR_DETECTION",
      "name": "Error Detection",
      "section": "ERROR",
      "role": "Run linters/tests/analysis tools on changed files",
      "status": "planned",
      "root_folder": "PH4_ERROR_DETECTION/",
      "key_artifacts": {
        "docs": [],
        "schemas": []
      }
    },
    {
      "phase_id": "PH5_ERROR_AUTOFIX",
      "name": "Error Autofix",
      "section": "ERROR",
      "role": "Attempt automated fixes (e.g. via Aider) and quarantine persistent failures",
      "status": "planned",
      "root_folder": "PH5_ERROR_AUTOFIX/",
      "key_artifacts": {
        "docs": [
          "IOC_ERROR_TO_FINALIZATION.md"
        ],
        "schemas": [
          "error_pipeline_result.v1.json"
        ]
      }
    },
    {
      "phase_id": "PH6_FINALIZATION_PREP",
      "name": "Finalization Prep",
      "section": "SAVING",
      "role": "Compute commit plans from clean changes and error pipeline results",
      "status": "planned",
      "root_folder": "PH6_FINALIZATION_PREP/",
      "key_artifacts": {
        "docs": [
          "PHASE_FINALIZATION_OVERVIEW.md"
        ],
        "schemas": [
          "commit_plan.v1.json"
        ]
      }
    },
    {
      "phase_id": "PH7_MERGE_AND_RELEASE",
      "name": "Merge and Release",
      "section": "SAVING",
      "role": "Apply Git operations (commit, push, safe-merge, PRs, local sync)",
      "status": "planned",
      "root_folder": "PH7_MERGE_AND_RELEASE/",
      "key_artifacts": {
        "docs": [
          "PHASE_MERGE_AND_RELEASE_OVERVIEW.md",
          "SAFE_MERGE_STRATEGY_V1.md"
        ],
        "schemas": [
          "git_strategy.v1.json",
          "git_operation_log.v1.json"
        ]
      }
    }
  ],
  "global_services": [
    {
      "service_id": "GLOBAL_AIM",
      "name": "AI Tool & Environment Registry",
      "root_folder": "GLOBAL_AIM/",
      "status": "planned",
      "scope": [
        "tool_registry",
        "ai_environment",
        "capability_resolution"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [],
        "schemas": []
      }
    },
    {
      "service_id": "GLOBAL_DOC_ID",
      "name": "Document ID & Routing",
      "root_folder": "GLOBAL_DOC_ID/",
      "status": "planned",
      "scope": [
        "id_minting",
        "routing",
        "registry"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [
          "DOC_ID_ROUTING_SPEC_V2.md"
        ],
        "schemas": [
          "doc_id_module_routing.json",
          "doc_id_kinds.v1.json"
        ]
      }
    },
    {
      "service_id": "GLOBAL_CAPABILITIES",
      "name": "Capabilities and Module Registry",
      "root_folder": "GLOBAL_CAPABILITIES/",
      "status": "planned",
      "scope": [
        "capabilities",
        "module_registry"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [],
        "schemas": []
      }
    },
    {
      "service_id": "GLOBAL_CORE_STATE",
      "name": "Shared State and Datastore",
      "root_folder": "GLOBAL_CORE_STATE/",
      "status": "planned",
      "scope": [
        "sqlite_state",
        "indices",
        "cross_phase_state"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [],
        "schemas": []
      }
    },
    {
      "service_id": "GLOBAL_UI",
      "name": "Shared UI Helpers",
      "root_folder": "GLOBAL_UI/",
      "status": "planned",
      "scope": [
        "rich_ui",
        "tui",
        "cli_shells"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [],
        "schemas": []
      }
    },
    {
      "service_id": "GLOBAL_UTIL",
      "name": "Shared Utilities",
      "root_folder": "GLOBAL_UTIL/",
      "status": "planned",
      "scope": [
        "logging",
        "helpers",
        "common_libs"
      ],
      "key_artifacts": {
        "service_manifest_files": [
          "service.manifest.json"
        ],
        "docs": [],
        "schemas": []
      }
    }
  ],
  "module_doc_suite": {
    "description": "Universal document set that every module must maintain as its single source of truth.",
    "docs": [
      {
        "id": "MOD_SPEC",
        "filename": "MOD_SPEC.md",
        "required": true,
        "purpose": "Source-of-truth specification for the module’s responsibilities, scope, and behavior."
      },
      {
        "id": "MOD_CONTRACTS",
        "filename": "MOD_CONTRACTS.md",
        "required": true,
        "purpose": "Defines public APIs, CLI entrypoints, and I/O contracts for the module."
      },
      {
        "id": "MOD_DESIGN",
        "filename": "MOD_DESIGN.md",
        "required": true,
        "purpose": "Describes the internal design, components, data flow, and key design decisions."
      },
      {
        "id": "MOD_TEST_PLAN",
        "filename": "MOD_TEST_PLAN.md",
        "required": true,
        "purpose": "Explains the test strategy, coverage, and locations of tests for this module."
      },
      {
        "id": "MOD_OPERATIONS",
        "filename": "MOD_OPERATIONS.md",
        "required": true,
        "purpose": "Operational runbook: how to run, configure, monitor, and debug this module."
      },
      {
        "id": "MOD_CHANGELOG",
        "filename": "MOD_CHANGELOG.md",
        "required": true,
        "purpose": "Chronological list of meaningful changes applied to this module."
      },
      {
        "id": "MOD_DELIVERABLES",
        "filename": "MOD_DELIVERABLES.md",
        "required": true,
        "purpose": "Defines deliverables produced by this module (files, states, outputs) and their consumers/handoffs."
      }
    ],
    "location_pattern": "<PHASE_OR_SERVICE>/modules/<module_id>/docs/"
  },
  "dag_doc_suite": {
    "description": "Execution Engine DAG documentation and schemas at the phase level.",
    "phase_id": "PH2_EXECUTION_ENGINE",
    "docs_folder": "PH2_EXECUTION_ENGINE/docs/",
    "schema_folder": "PH2_EXECUTION_ENGINE/schema/",
    "docs": [
      "PHASE_DAG_OVERVIEW.md",
      "PHASE_DAG_LIBRARY.md",
      "PHASE_DAG_MAPPING.md"
    ],
    "schemas": [
      "dag_graph.v1.json",
      "dag_library.v1.json",
      "dag_mapping_rules.v1.json"
    ]
  },
  "io_contracts": [
    {
      "boundary_id": "PLANNING_TO_EXEC",
      "from_phase": "PH0/PH1",
      "to_phase": "PH2_EXECUTION_ENGINE",
      "human_docs": [
        {
          "filename": "IOC_PLANNING_TO_EXEC.md",
          "phase_folder": "PH1_PLAN_TO_EXEC/docs/"
        }
      ],
      "schemas": [
        {
          "schema_id": "phase_plan",
          "filename": "phase_plan.v1.json",
          "schema_folder": "PH1_PLAN_TO_EXEC/schema/"
        }
      ]
    },
    {
      "boundary_id": "EXEC_TO_ERROR",
      "from_phase": "PH2_EXECUTION_ENGINE",
      "to_phase": "PH3_EXEC_TO_ERROR/PH4_ERROR_DETECTION",
      "human_docs": [
        {
          "filename": "IOC_EXEC_TO_ERROR.md",
          "phase_folder": "PH3_EXEC_TO_ERROR/docs/"
        }
      ],
      "schemas": [
        {
          "schema_id": "execution_result",
          "filename": "execution_result.v1.json",
          "schema_folder": "PH2_EXECUTION_ENGINE/schema/"
        },
        {
          "schema_id": "error_check_targets",
          "filename": "error_check_targets.v1.json",
          "schema_folder": "PH3_EXEC_TO_ERROR/schema/"
        }
      ]
    },
    {
      "boundary_id": "ERROR_TO_FINALIZATION",
      "from_phase": "PH4/PH5",
      "to_phase": "PH6_FINALIZATION_PREP",
      "human_docs": [
        {
          "filename": "IOC_ERROR_TO_FINALIZATION.md",
          "phase_folder": "PH5_ERROR_AUTOFIX/docs/"
        }
      ],
      "schemas": [
        {
          "schema_id": "error_pipeline_result",
          "filename": "error_pipeline_result.v1.json",
          "schema_folder": "PH5_ERROR_AUTOFIX/schema/"
        },
        {
          "schema_id": "commit_plan",
          "filename": "commit_plan.v1.json",
          "schema_folder": "PH6_FINALIZATION_PREP/schema/"
        }
      ]
    }
  ],
  "doc_id_routing_v2": {
    "description": "Planned rules for doc_id v2 routing, binding IDs to phases/services, modules, and kinds.",
    "pattern": "[TYPE]-[SCOPE][MODULE]-[KIND]-[NNN]",
    "components": {
      "TYPE": "High-level category, e.g., DOC, SCR, TST, PAT",
      "SCOPE": "Short scope code mapping to phase or global service, e.g., P0-P7, GA, GD, GC, GS, GU, GX",
      "MODULE": "Module code within a scope, planned as M000-M999 (practically often M00-M99 initially)",
      "KIND": "Artifact kind: SRC, DOC, TST, SCM, CFG, etc.",
      "NNN": "3-digit sequence number within that TYPE/SCOPE/MODULE/KIND family"
    },
    "scope_codes": {
      "phases": {
        "P0": "PH0_PLANNING/",
        "P1": "PH1_PLAN_TO_EXEC/",
        "P2": "PH2_EXECUTION_ENGINE/",
        "P3": "PH3_EXEC_TO_ERROR/",
        "P4": "PH4_ERROR_DETECTION/",
        "P5": "PH5_ERROR_AUTOFIX/",
        "P6": "PH6_FINALIZATION_PREP/",
        "P7": "PH7_MERGE_AND_RELEASE/"
      },
      "global_services": {
        "GA": "GLOBAL_AIM/",
        "GD": "GLOBAL_DOC_ID/",
        "GC": "GLOBAL_CAPABILITIES/",
        "GS": "GLOBAL_CORE_STATE/",
        "GU": "GLOBAL_UI/",
        "GX": "GLOBAL_UTIL/"
      }
    },
    "kinds": {
      "SRC": "src/",
      "DOC": "docs/",
      "TST": "tests/",
      "SCM": "schema/",
      "CFG": "config/"
    },
    "registry_files": {
      "module_routing": "GLOBAL_DOC_ID/schema/doc_id_module_routing.json",
      "kinds": "GLOBAL_DOC_ID/schema/doc_id_kinds.v1.json",
      "spec_doc": "GLOBAL_DOC_ID/docs/DOC_ID_ROUTING_SPEC_V2.md"
    },
    "filename_pattern": "[doc_id]__[short_slug].[ext]"
  },
  "git_pipeline": {
    "description": "High-level behavior of the automated saving (Git) stages.",
    "phases": {
      "finalization_prep": "PH6_FINALIZATION_PREP",
      "merge_and_release": "PH7_MERGE_AND_RELEASE"
    },
    "commit_plan_shape": {
      "schema_id": "commit_plan",
      "filename": "commit_plan.v1.json",
      "example_structure": {
        "commit_plan_id": "CP-YYYY-MM-DD-NNN",
        "execution_id": "EXEC-YYYY-MM-DD-NNN",
        "target_branch": "feature/some-feature",
        "base_branch": "main",
        "strategy": "safe_merge_v1",
        "commit_groups": [
          {
            "group_id": "GRP-001",
            "description": "Description of logical change group",
            "files": [],
            "modules": [],
            "commit_message": ""
          }
        ],
        "quarantine": []
      }
    },
    "strategies": {
      "schema_id": "git_strategy",
      "filename": "git_strategy.v1.json",
      "allowed_values": [
        "ff_only",
        "safe_merge_v1",
        "pr_only"
      ]
    },
    "operation_logging": {
      "schema_id": "git_operation_log",
      "filename": "git_operation_log.v1.json",
      "description": "Records which Git operations were performed during PH7, for auditing and debugging."
    }
  },
  "development_policy": {
    "definition_of_ready": {
      "description": "Conditions for a module/feature to be considered ready for execution.",
      "requires_docs": [
        "MOD_SPEC.md",
        "MOD_CONTRACTS.md",
        "MOD_TEST_PLAN.md",
        "MOD_DELIVERABLES.md"
      ],
      "requires_tests": "At least test skeletons exist for the behaviors being implemented.",
      "requires_contracts": "For new or changed APIs, MOD_CONTRACTS.md must be updated before coding."
    },
    "definition_of_done": {
      "description": "Conditions for a module/feature to be considered complete and eligible for commit/merge.",
      "conditions": [
        "Tests for the touched module(s) exist and pass.",
        "Error pipeline reports clean status (no unresolved errors).",
        "MOD_SPEC, MOD_CONTRACTS, MOD_TEST_PLAN, MOD_DELIVERABLES updated if behavior or outputs changed.",
        "MOD_CHANGELOG updated with summary of changes.",
        "doc_id routing is valid (IDs match paths).",
        "commit_plan.json generated and successfully applied by Git pipeline."
      ]
    }
  },
  "open_questions": [
    "Exact fields and types for phase_plan.v1.json (will be based on your uploaded template).",
    "Precise structure of execution_result.v1.json and error_pipeline_result.v1.json.",
    "Detailed module list and module_ids under each phase and global service.",
    "Decision on how many Git strategies to support initially (e.g., only safe_merge_v1 vs ff_only + PR)."
  ]
}
