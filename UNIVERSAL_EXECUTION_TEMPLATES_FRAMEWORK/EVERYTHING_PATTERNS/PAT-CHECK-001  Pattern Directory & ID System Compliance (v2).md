PAT-CHECK-001 – Pattern Directory & ID System Compliance (v2)

Spec ID: PAT-CHECK-001-v2
Status: DRAFT
Depends on: ID-SYSTEM-SPEC-V1 (doc_id format & usage)

0. Scope & Normative Keywords

This spec defines the minimum repository structure and ID-linkage requirements for the patterns/ tree.

Normative keywords MUST, SHOULD, MAY are as defined in RFC 2119.

doc_id is the primary cross-artifact join key, as defined in ID-SYSTEM-SPEC-V1.

pattern_id is a domain-specific label for patterns and MUST NOT replace doc_id as the canonical join key.

1. Directory Layout Requirements

PAT-CHECK-001-001 (MUST)
The repository MUST contain a patterns/ directory at the repository root.

PAT-CHECK-001-002 (MUST)
The following subdirectories MUST exist under patterns/:

patterns/registry/

patterns/specs/

patterns/schemas/

patterns/executors/

patterns/examples/

patterns/tests/

2. Pattern Index (PATTERN_INDEX.yaml) Requirements

PAT-CHECK-001-010 (MUST)
patterns/registry/PATTERN_INDEX.yaml MUST exist and be valid YAML.

PAT-CHECK-001-011 (MUST)
Every pattern entry in PATTERN_INDEX.yaml MUST include at least the following fields:

doc_id

pattern_id

name

version

status

spec_path

schema_path

executor_path

test_path

example_dir

PAT-CHECK-001-012 (MUST)
doc_id in each pattern entry MUST:

Conform to the doc_id format defined in ID-SYS-101 (e.g. matches the pattern [A-Z0-9]+(-[A-Z0-9]+)*).

Represent a logical documentation unit (pattern specification and its associated artifacts), not a single file revision.

PAT-CHECK-001-013 (MUST)
For every pattern entry:

spec_path MUST point to a file under patterns/specs/.

schema_path MUST point to a file under patterns/schemas/.

executor_path MUST point to a file under patterns/executors/.

test_path MUST point to an existing file or glob under patterns/tests/.

example_dir MUST point to a directory under patterns/examples/.

PAT-CHECK-001-014 (MUST)
Automation that links pattern-related artifacts MUST use doc_id as the primary join key.
pattern_id MAY be used as a human-readable or domain-specific label but MUST NOT be the primary key in cross-artifact joins.

3. Pattern Specification Files (patterns/specs/)

PAT-CHECK-001-020 (MUST)
For every pattern entry in PATTERN_INDEX.yaml, the associated spec_path:

MUST exist.

MUST be located under patterns/specs/.

MUST have a filename that matches:
<pattern_name>.pattern.yaml (where <pattern_name> corresponds to name or another well-defined field in the index).

PAT-CHECK-001-021 (MUST)
Each spec file MUST contain a machine-readable header or top-level fields including:

doc_id

pattern_id

name

version

role: spec

schema_ref (path or identifier referencing the schema)

executor_ref (path or identifier referencing the executor implementation)

PAT-CHECK-001-022 (MUST)
The doc_id inside the spec file MUST:

Match the doc_id for the corresponding pattern entry in PATTERN_INDEX.yaml.

Conform to the doc_id format specified in ID-SYSTEM-SPEC-V1.

PAT-CHECK-001-023 (SHOULD)
Spec files SHOULD avoid embedding file-system absolute paths; they SHOULD use repo-relative paths consistent with PATTERN_INDEX.yaml for schema_ref and executor_ref.

4. Schema Files (patterns/schemas/)

PAT-CHECK-001-030 (MUST)
For every pattern entry, the associated schema_path:

MUST exist.

MUST be located under patterns/schemas/.

MUST have a filename that matches:
<pattern_name>.schema.json.

PAT-CHECK-001-031 (SHOULD)
Each schema JSON file SHOULD embed a doc_id field at a stable, predictable location (e.g., top-level "doc_id").

PAT-CHECK-001-032 (MUST)
If a schema file cannot embed doc_id (or embedding is undesirable), a sidecar metadata file MUST exist, for example:

patterns/schemas/<pattern_name>.schema.id.yaml
or

A central index file that maps schema paths to doc_id.

This sidecar or index MUST:

Include the schema_path.

Include the associated doc_id.

PAT-CHECK-001-033 (MUST)
Whether embedded or in a sidecar, the doc_id associated with a schema MUST:

Match the doc_id of the corresponding pattern entry in PATTERN_INDEX.yaml.

Conform to the ID-SYSTEM-SPEC-V1 format requirements.

5. Executor Files (patterns/executors/)

PAT-CHECK-001-040 (MUST)
For every pattern entry, the associated executor_path:

MUST exist.

MUST be located under patterns/executors/.

MUST have a filename that matches:
<pattern_name>_executor.* (where * is a language-appropriate extension, e.g., .py, .ps1, .sh).

PAT-CHECK-001-041 (MUST)
Each executor file MUST contain a DOC_LINK header or equivalent comment that includes the doc_id. For example:

# DOC_LINK: <DOC_ID>


or language-specific comment syntax (e.g., // DOC_LINK: <DOC_ID>).

PAT-CHECK-001-042 (MUST)
The doc_id used in the executor’s DOC_LINK MUST:

Match the doc_id of the corresponding pattern entry in PATTERN_INDEX.yaml.

Conform to the doc_id format specified in ID-SYSTEM-SPEC-V1.

PAT-CHECK-001-043 (SHOULD)
Executor files SHOULD avoid hard-coding absolute paths to specs, schemas, or tests; automation SHOULD rely on doc_id and repository-relative paths instead.

6. Example Directories (patterns/examples/)

PAT-CHECK-001-050 (MUST)
For every pattern entry, the associated example_dir:

MUST exist.

MUST be a directory under patterns/examples/.

MUST contain at least one .json file.

Ideally, this SHOULD be named instance_minimal.json, but other example names are allowed.

PAT-CHECK-001-051 (SHOULD)
Each example JSON file SHOULD either:

Embed a doc_id field, or

Be referenced by a sidecar or index file that maps example paths to doc_id.

PAT-CHECK-001-052 (MUST)
The doc_id associated with each example (embedded or sidecar) MUST:

Match the doc_id of the corresponding pattern entry in PATTERN_INDEX.yaml.

Conform to ID-SYSTEM-SPEC-V1.

7. Test Files (patterns/tests/)

PAT-CHECK-001-060 (MUST)
For every pattern entry, there MUST be at least one test file under patterns/tests/ whose filename begins with:

test_<pattern_name>_


PAT-CHECK-001-061 (MUST)
Each test file for a pattern MUST include a DOC_LINK header or equivalent comment that includes the doc_id. For example:

# DOC_LINK: <DOC_ID>


PAT-CHECK-001-062 (MUST)
The doc_id used in test files MUST:

Match the doc_id of the corresponding pattern entry in PATTERN_INDEX.yaml.

Conform to ID-SYSTEM-SPEC-V1.

PAT-CHECK-001-063 (SHOULD)
Test files SHOULD be organized so that pattern-level and cross-pattern tests are clearly distinguishable (e.g., via naming, directories, or test markers), while still preserving the doc_id linkage.

8. Cross-Artifact Consistency & Join Semantics

PAT-CHECK-001-070 (MUST)
For any given pattern entry in PATTERN_INDEX.yaml, all of the following artifacts MUST resolve to the same doc_id:

The spec file under patterns/specs/.

The schema file under patterns/schemas/ (or its sidecar).

The executor file under patterns/executors/.

All tests associated with that pattern under patterns/tests/.

All example JSONs (or their sidecars) under patterns/examples/.

PAT-CHECK-001-071 (MUST)
Automation and tools (including future scripts) that perform pattern-level operations MUST treat doc_id as the canonical join key across these artifact types.

PAT-CHECK-001-072 (SHOULD)
Where both pattern_id and doc_id appear, pattern_id SHOULD remain stable and human-meaningful, but any breaking change to the logical pattern unit SHOULD result in either:

A new doc_id, or

A documented versioning decision consistent with ID-SYSTEM-SPEC-V1.

9. Tooling & Script Requirements (PATTERN_DIR_CHECK.ps1)

PAT-CHECK-001-080 (SHOULD)
A PATTERN_DIR_CHECK.ps1 (or equivalent) script SHOULD be implemented to validate all requirements in this spec, including but not limited to:

Directory layout (Section 1).

Pattern index shape and path existence (Section 2).

Spec/schema/executor/example/test file conventions (Sections 3–7).

doc_id existence, format, and cross-artifact consistency (Sections 2–8).

PAT-CHECK-001-081 (SHOULD)
The script SHOULD:

Emit per-requirement PASS/FAIL results keyed by the requirement IDs in this spec (e.g., PAT-CHECK-001-020).

Produce a summary including:

Total checks run.

Number of PASS/FAIL.

Overall pass/fail for PAT-CHECK-001-v2 compliance.

PAT-CHECK-001-082 (SHOULD)
The script SHOULD integrate with the existing STATE / AUDIT layer (e.g., by writing results to .state/ or audit logs) so that PATTERN compliance becomes part of the global repository state and audit trail.