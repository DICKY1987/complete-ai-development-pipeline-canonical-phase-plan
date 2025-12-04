---
doc_id: DOC-GUIDE-PATCH1-460
---

--- master_plan.md
+++ master_plan.md
@@ -52,7 +52,8 @@
         "docs": [
           "PHASE_DAG_OVERVIEW.md",
           "PHASE_DAG_LIBRARY.md",
-          "PHASE_DAG_MAPPING.md"
+          "PHASE_DAG_MAPPING.md",
+          "UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md"
         ],
         "schemas": [
           "dag_graph.v1.json",
@@ -256,6 +257,51 @@
         ],
         "docs": [],
         "schemas": []
+      }
+    },
+    {
+      "service_id": "GLOBAL_PATHS",
+      "name": "Path Registry & Indirection Layer",
+      "root_folder": "GLOBAL_PATHS/",
+      "status": "planned",
+      "scope": [
+        "path_registry",
+        "indirection",
+        "ci_enforcement"
+      ],
+      "key_artifacts": {
+        "service_manifest_files": [
+          "service.manifest.json"
+        ],
+        "docs": [
+          "PATH ABSTRACTION & INDIRECTION LAYER.md"
+        ],
+        "schemas": [
+          "path_index.v1.json"
+        ]
+      }
+    },
+    {
+      "service_id": "GLOBAL_PATCH_LEDGER",
+      "name": "Patch Ledger & History",
+      "root_folder": "GLOBAL_PATCH_LEDGER/",
+      "status": "planned",
+      "scope": [
+        "patch_tracking",
+        "ledger",
+        "audit_trail"
+      ],
+      "key_artifacts": {
+        "service_manifest_files": [
+          "service.manifest.json"
+        ],
+        "docs": [
+          "UET_PATCH_MANAGEMENT_SPEC.md"
+        ],
+        "schemas": [
+          "patch_artifact.v1.json",
+          "patch_ledger_entry.v1.json"
+        ]
+      }
     }
   ],
   "module_doc_suite": {
@@ -369,6 +415,24 @@
           "phase_folder": "PH1_PLAN_TO_EXEC/docs/"
         }
       ],
-      "schemas": [
-        {
-          "schema_id": "phase_plan",
-          "filename": "phase_plan.v1.json",
-          "schema_folder": "PH1_PLAN_TO_EXEC/schema/"
-        }
-      ]
+      "schemas": [
+        {
+          "schema_id": "phase_plan",
+          "filename": "phase_plan.v1.json",
+          "schema_folder": "PH1_PLAN_TO_EXEC/schema/"
+        },
+        {
+          "schema_id": "workstream_spec",
+          "filename": "workstream_spec.v1.json",
+          "schema_folder": "PH1_PLAN_TO_EXEC/schema/"
+        },
+        {
+          "schema_id": "execution_request",
+          "filename": "execution_request.v1.json",
+          "schema_folder": "PH1_PLAN_TO_EXEC/schema/"
+        }
+      ]
     },
     {
       "boundary_id": "EXEC_TO_ERROR",
@@ -457,5 +521,84 @@
     "Exact fields and types for phase_plan.v1.json (will be based on your uploaded template).",
     "Precise structure of execution_result.v1.json and error_pipeline_result.v1.json.",
     "Detailed module list and module_ids under each phase and global service.",
-    "Decision on how many Git strategies to support initially (e.g., only safe_merge_v1 vs ff_only + PR)."
-  ]
+    "Decision on how many Git strategies to support initially (e.g., only safe_merge_v1 vs ff_only + PR)."
+  ],
+  "id_system": {
+    "description": "Global rules for doc_id as the single cross-artifact identifier.",
+    "spec_filename": "UTE_ID_SYSTEM_SPEC.md",
+    "schema_filename": "doc_id.v1.json",
+    "requirements": {
+      "all_plan_artifacts_must_have_doc_id": true,
+      "doc_id_field_name": "doc_id",
+      "enforce_single_linking_id": true
+    }
+  },
+  "phase_spec_suite": {
+    "description": "Universal phase spec applied to all phases in this plan.",
+    "spec_filename": "UTE_UNIVERSAL_PHASE_SPECIFICATION.md",
+    "schema_filename": "phase_spec.v1.json",
+    "enforced_for_phases": [
+      "PH0_PLANNING",
+      "PH1_PLAN_TO_EXEC",
+      "PH2_EXECUTION_ENGINE",
+      "PH3_EXEC_TO_ERROR",
+      "PH4_ERROR_DETECTION",
+      "PH5_ERROR_AUTOFIX",
+      "PH6_FINALIZATION_PREP",
+      "PH7_MERGE_AND_RELEASE"
+    ]
+  },
+  "workstream_spec_suite": {
+    "description": "Shape and location of workstream spec documents used by the execution engine.",
+    "spec_filename": "UET_WORKSTREAM_SPEC.md",
+    "schema_filename": "workstream_spec.v1.json",
+    "directory": "workstreams/"
+  },
+  "task_routing": {
+    "description": "Task routing and execution request contracts for sending work to tools/workers.",
+    "spec_filename": "UET_TASK_ROUTING_SPEC.md",
+    "schema_filename": "execution_request.v1.json",
+    "router_config_schema": "router_config.v1.json"
+  },
+  "patching": {
+    "description": "Patch artifacts and patch ledger used for safe file changes.",
+    "spec_filename": "UET_PATCH_MANAGEMENT_SPEC.md",
+    "patch_schema_filename": "patch_artifact.v1.json",
+    "ledger_schema_filename": "patch_ledger_entry.v1.json",
+    "directories": {
+      "patches": ".ledger/patches/",
+      "tasks": ".tasks/"
+    }
+  },
+  "execution_kernel": {
+    "description": "Execution kernel configuration and lifecycle state machines.",
+    "spec_filename": "UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md",
+    "state_machines": {
+      "task": "task_lifecycle.yaml",
+      "workstream": "workstream_lifecycle.yaml",
+      "worker": "worker_lifecycle.yaml"
+    },
+    "config_schema": "execution_kernel_config.v2.json"
+  },
+  "framework_inventory": {
+    "description": "Inventory and validation of the framework/ directory, including core, profiles, and examples.",
+    "spec_filename": "UET_Framework_File_Inventory.md",
+    "core_root": "framework/core/",
+    "profiles_root": "framework/profiles/",
+    "examples_root": "framework/examples/",
+    "validation_script": "scripts/validate_framework_inventory.py"
+  }
 }
