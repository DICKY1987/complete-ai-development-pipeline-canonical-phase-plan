
---

### 1. How they fit together

GitHub Projects/Issues world:

* Projects are **collections of items (issues/PRs/drafts)** that you can view as tables, boards, or roadmaps.
* You get **custom fields** (text, number, date, single-select, iteration, etc.) and flexible views + charts. ([GitHub Docs][1])
* You can **automate** everything with built-in automations, the Projects API, and GitHub Actions. ([GitHub Docs][1])

MASTER_SPLINTER Phase Plan:

* Each YAML file describes a **Phase**: phase_id, workstream_id, dependencies, scope, checks, tasks, acceptance criteria, etc.
* It’s your **internal ground truth spec** for how work should be done.

These are orthogonal but compatible:

* **SPLINTER = spec & execution contract** (in the repo).
* **GitHub PM = visual planning, tracking, and reporting layer** (Issues + Projects).

---

### 2. Practical mapping (so you can use all the GH features)

For each SPLINTER Phase Plan:

* Create **one Issue or Project item** that represents that phase.
* Map SPLINTER fields → GitHub **custom fields** on the project:

Example mappings:

* `phase_identity.phase_id` → text field: **Phase ID**
* `phase_identity.workstream_id` → text field: **Workstream**
* `phase_identity.status` / `phase_state` → single-select field: **Status** (`Planned / In Progress / Blocked / Done`)
* `execution_profile.risk_level` → single-select: **Risk**
* `completion_gate.target_date` → date field: **Target date**
* `dag_and_dependencies.depends_on` → GitHub **issue dependencies / sub-issues** or a text field listing parent IDs. ([GitHub Docs][1])

Then:

* Put a link to the SPLINTER YAML in the issue description.
* Optionally mirror a **short summary** + key acceptance criteria into the issue body.

---

### 3. Using GitHub PM features on top of SPLINTER

Once that mapping exists, you can use:

* **Boards / tables / roadmaps**: Views grouped by `Status`, `Workstream`, `Risk`, or `Iteration`. ([GitHub Docs][1])
* **Insights / charts**: Burn-up, per-iteration progress, etc., based on your custom fields (status, story points, etc.). ([GitHub Docs][1])
* **Sub-issues & dependencies**: Represent SPLINTER sub-tasks or downstream phases as sub-issues. ([GitHub Docs][1])
* **Automation**:

  * Actions that parse the SPLINTER YAML and **update project fields**.
  * Workflows that **move items** between columns or change `Status` when tests pass, PRs merge, etc. ([GitHub Docs][1])

So: **all GitHub PM features remain usable**; they just operate on Issues/Project items that are “backed” by SPLINTER phase specs.

---

### 4. Minimal tweak I’d add to the MASTER_SPLINTER template

To make this first-class, I’d add a small integration block like:

```yaml
github_integration:
  repo: "owner/repo-name"
  issue_number: null          # filled once created
  project_id: null            # or project URL
  project_fields:
    phase_id_field: "Phase ID"
    workstream_field: "Workstream"
    status_field: "Status"
    risk_field: "Risk"
    target_date_field: "Target date"
```

Then an Action / CLI script can:

1. Read the SPLINTER YAML.
2. Create or update the linked Issue/Project item.
3. Sync fields ↔ SPLINTER so GitHub views stay in lockstep with your ground-truth phase plans.

---

Here’s a concrete way to wire MASTER_SPLINTER into GitHub Projects/Issues.

---

## 1. Add a `github_integration` block to the Phase Plan template

Drop this near the bottom of `MASTER_SPLINTER_Phase_Plan_Template.yml` (or wherever you keep integration sections), and then reuse it for all phase specs:

```yaml
github_integration:
  enabled: true

  repo:
    owner: "OWNER_NAME"              # e.g. "DICKY1987"
    name: "REPO_NAME"                # e.g. "complete-ai-development-pipeline-canonical-phase-plan"
    default_branch: "main"

  issue:
    mode: "one-per-phase"            # "one-per-phase" | "none" | "reuse"
    number: null                     # filled once created
    title_template: "[{phase_id}] {title}"
    body_template_path: null         # optional: path to a .md template
    labels:
      - "phase-plan"
      - "workstream:{workstream_id}"
      - "phase:{phase_id}"
    assignees:
      - null                         # optionally set default assignee

  project:
    # Either use a URL OR owner + project_number (Projects v2)
    url: null                        # e.g. "https://github.com/orgs/ORG_NAME/projects/1"
    owner: "ORG_OR_USER"             # e.g. "DICKY1987" or your org
    project_number: null             # e.g. 1
    item_id: null                    # filled by automation once created

    field_mappings:
      phase_id_field: "Phase ID"     # text field in the project
      workstream_field: "Workstream"
      status_field: "Status"         # single-select mapping your SPLINTER status
      risk_field: "Risk"
      target_date_field: "Target date"
      doc_id_field: "doc_id"         # optional, if you want it visible in Projects

      # optional extra fields you might define in your project
      story_points_field: "Story points"
      owner_field: "Owner"

  automation:
    allow_issue_create: true
    allow_issue_update: true
    allow_project_item_create: true
    allow_project_item_update: true

    sync_direction: "yaml->github"   # "yaml->github" | "bidirectional"
    on_phase_status_change_update_project: true
    on_project_status_change_update_phase: false  # flip to true if you want bidirectional

    last_synced_at: null             # filled by automation
    last_synced_by: null             # e.g. "github-actions[bot]" or a username
```

**How this ties into GitHub Projects / Issues**

* Projects can use **custom fields** (text, number, date, single-select, iterations) to track metadata like Phase ID, Risk, Status, etc. ([GitHub Docs][1])
* GitHub Issues + Projects let you **create items, add custom fields, and visualize as board/table/roadmap**. ([GitHub][2])
* The block above is just a **mapping layer**: your orchestrator/Actions script reads this YAML, then calls the GitHub API (GraphQL Projects v2) to create/update the issue & project item and set those fields. ([GitHub Docs][3])

So MASTER_SPLINTER stays ground-truth; GitHub is the UI and reporting.

---

## 2. Example GitHub Actions workflow to sync a Phase Plan → Issues/Project

Create `.github/workflows/splinter_phase_sync.yml`:

```yaml
name: Sync SPLINTER Phase Plan to GitHub Projects

on:
  push:
    paths:
      - "phases/**/*.yml"
      - "phases/**/*.yaml"
  workflow_dispatch: {}

permissions:
  contents: read
  issues: write
  projects: write

jobs:
  sync_phase_to_github:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml requests

      - name: Determine changed SPLINTER phase files
        id: changed
        run: |
          # Collect phase files changed in this push
          files=$(git diff --name-only HEAD~1 HEAD | grep -E '^phases/.*\.ya?ml$' || true)
          echo "files<<EOF" >> $GITHUB_OUTPUT
          echo "$files" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Sync phase files
        if: steps.changed.outputs.files != ''
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "${{ steps.changed.outputs.files }}" | while read file; do
            [ -z "$file" ] && continue
            echo "Syncing $file"

            python scripts/splinter_sync_phase_to_github.py \
              --phase-file "$file" \
              --github-repo "${{ github.repository }}" \
              --github-token "$GITHUB_TOKEN"
          done
```

This assumes a helper script like `scripts/splinter_sync_phase_to_github.py` that:

1. Loads the phase YAML.
2. Reads `github_integration`.
3. Uses GitHub APIs to:

   * Create/update an **Issue**.
   * Ensure the Issue is present in the desired **Project**.
   * Set custom fields to match `field_mappings`.

---

## 3. Sketch of the sync script (high-level logic)

You don’t have to implement now, but this is the behavior:

```python
# scripts/splinter_sync_phase_to_github.py  (sketch)

import argparse, yaml, requests, textwrap

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-file", required=True)
    parser.add_argument("--github-repo", required=True)   # "owner/repo"
    parser.add_argument("--github-token", required=True)
    args = parser.parse_args()

    owner, repo = args.github_repo.split("/")

    data = yaml.safe_load(open(args.phase_file, "r", encoding="utf-8"))
    phase = data.get("phase_identity", {})
    gh = data.get("github_integration", {})

    if not gh.get("enabled", False):
        print("github_integration disabled; skipping")
        return

    # 1. Ensure Issue exists (REST Issues API)
    issue_number = ensure_issue(owner, repo, phase, gh, args.github_token)

    # 2. Ensure Project item exists and fields are synced (GraphQL Projects v2)
    ensure_project_item(owner, gh, issue_number, phase, args.github_token)

    # 3. Update YAML with issue_number / item_id / last_synced_*
    #    (optional – you can write back to file if allowed)
    # save_back_to_yaml(...)

if __name__ == "__main__":
    main()
```

Implementation details:

* **Issues**:
  Use the REST Issues API to create/update title, body, labels, etc. ([GitHub][4])
* **Projects & custom fields**:
  Use **GraphQL Projects v2** (`ProjectV2`, `ProjectV2Item`, and field value mutations) to:

  * Find the project (by `project_number` and owner).
  * Find or create the item for that issue.
  * Look up field IDs by their names (`Phase ID`, `Status`, etc.).
  * Set field values from the phase spec (`phase_id`, `status`, `risk`, target date, etc.). ([GitHub Docs][3])

Once this is wired:

* MASTER_SPLINTER Phase Plan stays your **single source of truth**.
* Every push that changes a phase spec **automatically keeps GitHub Projects in sync**.
* You can still fully use:

  * Boards / tables / roadmaps.
  * Custom fields for filtering, grouping, charts.
  * Built-in project automations and webhooks. ([GitHub Docs][1])


---

Here’s a concrete, pattern-y layout plus the “how-to” instructions for an agentic AI.

---

## 1. Pattern-style `ensure_issue` / `ensure_project_item` layout

Think of this as a **GH_SYNC pattern module**. You can drop this into something like `modules/github_sync/phase_sync.py`.

```python
"""
Pattern: GH_SYNC_PHASE_V1
Responsibility:
    - Ensure a GitHub Issue exists for a given SPLINTER phase.
    - Ensure a GitHub Project item exists and has correct field values.
    - Never guess: always derive from phase_identity + github_integration.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import textwrap
import requests


# =========
# MODELS
# =========

@dataclass
class PhaseIdentity:
    phase_id: str
    workstream_id: str
    title: str
    status: str
    risk_level: Optional[str] = None
    target_date: Optional[str] = None  # ISO date string, e.g. "2025-12-31"


@dataclass
class GitHubIssueConfig:
    mode: str                         # "one-per-phase" | "none" | "reuse"
    number: Optional[int]
    title_template: str
    body_template_path: Optional[str]
    labels: list
    assignees: list


@dataclass
class GitHubProjectConfig:
    url: Optional[str]
    owner: str
    project_number: Optional[int]
    item_id: Optional[str]
    field_mappings: Dict[str, str]    # logical_name -> project field label


@dataclass
class GitHubIntegrationConfig:
    enabled: bool
    repo_owner: str
    repo_name: str
    default_branch: str
    issue: GitHubIssueConfig
    project: GitHubProjectConfig
    automation: Dict[str, Any]


# =========
# HELPERS
# =========

def _render_issue_title(phase: PhaseIdentity, cfg: GitHubIssueConfig) -> str:
    """
    PATTERN: RENDER_ISSUE_TITLE_V1
    Rule:
        - Only substitute known placeholders.
        - Do NOT silently drop unknown keys.
    """
    template = cfg.title_template or "[{phase_id}] {title}"
    return template.format(
        phase_id=phase.phase_id,
        title=phase.title,
        workstream_id=phase.workstream_id,
        status=phase.status,
        risk_level=phase.risk_level or "unknown",
    )


def _render_issue_body(phase: PhaseIdentity, phase_yaml_path: str) -> str:
    """
    PATTERN: RENDER_ISSUE_BODY_V1
    Minimal, but structured. You can later make this pluggable with a .md template.
    """
    return textwrap.dedent(
        f"""
        # Phase: {phase.phase_id} – {phase.title}

        - Workstream: `{phase.workstream_id}`
        - Status (SPLINTER): `{phase.status}`
        - Risk level: `{phase.risk_level or "unknown"}`
        - Target date: `{phase.target_date or "unset"}`

        Ground-truth phase spec: `{phase_yaml_path}`

        > This issue is synchronized from the SPLINTER Phase Plan.
        > Do not manually edit the phase contract here; change the YAML instead.
        """
    ).strip()


def _github_request(
    method: str,
    url: str,
    token: str,
    *,
    json: Optional[dict] = None,
) -> dict:
    """
    PATTERN: GITHUB_REQUEST_V1
    - Centralize auth, headers, error handling.
    - Raise on non-2xx so orchestrator can decide.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.request(method, url, headers=headers, json=json)
    if not resp.ok:
        raise RuntimeError(
            f"GitHub API error {resp.status_code} for {url}: {resp.text[:500]}"
        )
    return resp.json()


# =========
# CORE: ENSURE ISSUE
# =========

def ensure_issue(
    gh_cfg: GitHubIntegrationConfig,
    phase: PhaseIdentity,
    phase_yaml_path: str,
    token: str,
) -> int:
    """
    PATTERN: GH_SYNC_PHASE_ISSUE_V1

    Behavior:
        - If github_integration.enabled is false or mode == "none": do nothing.
        - If issue.number is set: update title/body/labels.
        - Else: create a new issue and return its number.
    """
    if not gh_cfg.enabled:
        raise RuntimeError("GitHub integration disabled; aborting ensure_issue().")

    issue_cfg = gh_cfg.issue
    if issue_cfg.mode == "none":
        raise RuntimeError("Issue mode is 'none'; ensure_issue() should not be invoked.")

    owner = gh_cfg.repo_owner
    repo = gh_cfg.repo_name

    title = _render_issue_title(phase, issue_cfg)
    body = _render_issue_body(phase, phase_yaml_path)

    labels = [
        *[lbl for lbl in issue_cfg.labels if lbl is not None],
        f"workstream:{phase.workstream_id}",
        f"phase:{phase.phase_id}",
    ]

    if issue_cfg.number:
        # UPDATE EXISTING ISSUE
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_cfg.number}"
        payload = {
            "title": title,
            "body": body,
            "labels": labels,
        }
        _github_request("PATCH", url, token, json=payload)
        return issue_cfg.number

    # CREATE NEW ISSUE
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    if issue_cfg.assignees:
        payload["assignees"] = [a for a in issue_cfg.assignees if a]

    result = _github_request("POST", url, token, json=payload)
    issue_number = result["number"]

    # NOTE:
    # You can optionally write back issue_number into the YAML in a later step.
    return issue_number


# =========
# CORE: ENSURE PROJECT ITEM
# =========

def ensure_project_item(
    gh_cfg: GitHubIntegrationConfig,
    phase: PhaseIdentity,
    issue_number: int,
    token: str,
) -> str:
    """
    PATTERN: GH_SYNC_PHASE_PROJECT_V1

    Behavior:
        - Resolve project id from owner + project_number or URL.
        - Find or create a Project item linked to the issue.
        - Upsert field values (Phase ID, Status, Risk, Target date, doc_id, etc.).
    """
    project_cfg = gh_cfg.project

    if not project_cfg.url and not project_cfg.project_number:
        raise RuntimeError("Project config incomplete: need url or project_number.")

    # 1) Resolve ProjectV2 node id (cached by url/project_number)
    project_node_id = _resolve_project_node_id(project_cfg, token)

    # 2) Ensure item exists for this issue
    item_id = project_cfg.item_id or _find_project_item_for_issue(
        project_node_id, gh_cfg, issue_number, token
    )

    if item_id is None:
        item_id = _create_project_item_for_issue(
            project_node_id, gh_cfg, issue_number, token
        )

    # 3) Upsert field values
    _update_project_item_fields(
        project_node_id,
        item_id,
        project_cfg.field_mappings,
        phase,
        token,
    )

    # Return item_id so caller can optionally write it back into YAML
    return item_id


# =========
# GRAPHQL HELPERS (STUBS)
# =========

def _graphql_request(token: str, query: str, variables: Dict[str, Any]) -> dict:
    """
    PATTERN: GITHUB_GRAPHQL_REQUEST_V1
    - Single entrypoint for GraphQL calls.
    - No business logic.
    """
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    if not resp.ok:
        raise RuntimeError(
            f"GraphQL error {resp.status_code}: {resp.text[:500]}"
        )
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def _resolve_project_node_id(project_cfg: GitHubProjectConfig, token: str) -> str:
    """
    PATTERN: GH_PROJECT_RESOLVE_NODE_ID_V1
    TODO:
        - Implement lookup based on project_cfg.url OR (owner + project_number).
    """
    # PSEUDO:
    # - If project_cfg.url: parse owner/org and project_number from URL
    # - Query: query($org:String!, $number:Int!) { organization(login:$org) { projectV2(number:$number) { id } } }
    raise NotImplementedError


def _find_project_item_for_issue(
    project_node_id: str,
    gh_cfg: GitHubIntegrationConfig,
    issue_number: int,
    token: str,
) -> Optional[str]:
    """
    PATTERN: GH_PROJECT_FIND_ITEM_FOR_ISSUE_V1
    TODO:
        - Query project items with content == issue.
        - Return item id if exists.
    """
    raise NotImplementedError


def _create_project_item_for_issue(
    project_node_id: str,
    gh_cfg: GitHubIntegrationConfig,
    issue_number: int,
    token: str,
) -> str:
    """
    PATTERN: GH_PROJECT_CREATE_ITEM_FOR_ISSUE_V1
    TODO:
        - Use mutation to create item with contentId pointing to the Issue node.
    """
    raise NotImplementedError


def _update_project_item_fields(
    project_node_id: str,
    item_id: str,
    field_mappings: Dict[str, str],
    phase: PhaseIdentity,
    token: str,
) -> None:
    """
    PATTERN: GH_PROJECT_UPDATE_FIELDS_V1
    TODO:
        - Map logical field names -> actual field ids.
        - Use mutations like updateProjectV2ItemFieldValue to set:
            - Phase ID
            - Workstream
            - Status
            - Risk
            - Target date
    """
    # Example mapping (logical_name -> value from PhaseIdentity)
    value_map = {
        "phase_id_field": phase.phase_id,
        "workstream_field": phase.workstream_id,
        "status_field": phase.status,
        "risk_field": phase.risk_level,
        "target_date_field": phase.target_date,
    }

    # PSEUDO-STEPS:
    # 1) Query project fields, build name -> field_id map.
    # 2) For each logical key in field_mappings:
    #       - look up project field name
    #       - then field id
    #       - then value from value_map
    #       - call updateProjectV2ItemFieldValue mutation.
    raise NotImplementedError
```

This gives you:

* Clear **pattern IDs** in comments and function names.
* A clean separation between:

  * **HTTP plumbing** (`_github_request`, `_graphql_request`),
  * **business behavior** (`ensure_issue`, `ensure_project_item`),
  * **rendering rules** (`_render_issue_title`, `_render_issue_body`),
  * **GraphQL details** (stubs with TODOs for future implementation).

---

## 2. “How-to” instructions for an agentic AI to tailor `github_integration` field names

Below is a **machine-oriented instruction block** you can store as e.g.
`docs/github_integration/TUNE_FIELD_MAPPINGS_FOR_PROJECT.md` and point your orchestrator at.

````markdown
# [AGENT_TASK] Tailor github_integration.field_mappings to a specific GitHub Project

## [INTENT]

You are configuring the `github_integration` block inside a SPLINTER Phase Plan template so that it matches the **actual custom field names** used in a specific GitHub Project (Projects v2).

Your output will be a **diff-ready YAML snippet** that updates only the `github_integration` section, without changing unrelated parts of the phase plan.

---

## [INPUTS]

You will always be given:

1. The **current** `github_integration` block from the phase plan (YAML fragment).
2. The **GitHub Project definition**, provided in one of these forms:
   - A human-readable description of the project and its fields, or
   - A JSON/GraphQL dump of the project fields (name, data type, id), or
   - A list of field names the user has created in the GitHub UI.

Example logical keys used in `field_mappings`:

- `phase_id_field`
- `workstream_field`
- `status_field`
- `risk_field`
- `target_date_field`
- `doc_id_field`
- Optional: `story_points_field`, `owner_field`, etc.

---

## [OUTPUT]

You must output:

1. A **YAML fragment** that can replace the existing `github_integration` block.
2. The fragment must:
   - Keep structure stable.
   - Only change:
     - `project.url` / `project.owner` / `project.project_number` as needed.
     - `project.field_mappings.*` values to match actual GitHub Project field names.
   - Preserve any other keys not mentioned as-is.

**Do NOT** output prose explanations inside the YAML. Explanations go outside of the code block.

---

## [PROCEDURE]

### Step 1 – Parse the Inputs

1. Read the existing `github_integration` YAML block.
2. Extract:
   - `project.owner`
   - `project.project_number` or `project.url`
   - `project.field_mappings` (logical_name → field label).

3. From the GitHub Project metadata, build a set:
   - `project_field_names = { "Phase ID", "Status", "Risk", "Target date", ... }`

### Step 2 – Build a Logical → Actual Name Mapping

For each **logical key** in `project.field_mappings`:

1. Identify the **intended meaning**:

   - `phase_id_field` → should hold the SPLINTER `phase_id`
   - `workstream_field` → should hold `workstream_id`
   - `status_field` → should represent the phase status
   - `risk_field` → should represent the risk level
   - `target_date_field` → should store the target or due date
   - `doc_id_field` → should store the SPLINTER `doc_id`

2. Find the **closest matching field name** in `project_field_names`:

   - Prefer **exact matches** (case-insensitive).
   - If multiple candidates exist, choose the one whose name most closely matches the meaning.
     - Example mapping:
       - logical: `status_field` → project field: `"Status"`
       - logical: `target_date_field` → project field: `"Target date"`
       - logical: `risk_field` → project field: `"Risk"`
       - logical: `phase_id_field` → project field: `"Phase ID"`
       - logical: `doc_id_field` → project field: `"doc_id"` or `"Doc ID"`

3. If you **cannot confidently map** a logical key:
   - Leave the existing value unchanged.
   - Add a `TODO:` comment in your explanation section (not inside YAML) stating which logical key is unresolved.

### Step 3 – Update field_mappings Values

Construct a new `field_mappings` dictionary where:

- Each logical key remains the same.
- Each value is the **exact GitHub Project field label** you intend to use.

Example:

```yaml
field_mappings:
  phase_id_field: "Phase ID"
  workstream_field: "Workstream"
  status_field: "Status"
  risk_field: "Risk"
  target_date_field: "Target date"
  doc_id_field: "doc_id"
````

Rules:

* Do **not** add new logical keys unless explicitly asked.
* Do **not** remove existing logical keys; if unused, keep them but point them to a reasonable field or leave them as-is.

### Step 4 – Preserve Non-field Settings

When reconstructing the `github_integration` block:

* Copy the original values for:

  * `enabled`
  * `repo.owner`, `repo.name`, `default_branch`
  * `issue.mode`, `issue.title_template`, etc.
  * `automation.*`

* Only change:

  * `project.url` / `project.owner` / `project.project_number` IF the user provided updated values.
  * `project.field_mappings.*` per Step 3.

### Step 5 – Emit Final YAML Fragment

Output a **single YAML code block** containing the updated `github_integration` block.

Example shape:

```yaml
github_integration:
  enabled: true
  repo:
    owner: "DICKY1987"
    name: "complete-ai-development-pipeline-canonical-phase-plan"
    default_branch: "main"

  issue:
    mode: "one-per-phase"
    number: null
    title_template: "[{phase_id}] {title}"
    body_template_path: null
    labels:
      - "phase-plan"
    assignees:
      - null

  project:
    url: "https://github.com/orgs/ORG_NAME/projects/1"
    owner: "ORG_NAME"
    project_number: 1
    item_id: null
    field_mappings:
      phase_id_field: "Phase ID"
      workstream_field: "Workstream"
      status_field: "Status"
      risk_field: "Risk"
      target_date_field: "Target date"
      doc_id_field: "doc_id"

  automation:
    allow_issue_create: true
    allow_issue_update: true
    allow_project_item_create: true
    allow_project_item_update: true
    sync_direction: "yaml->github"
    on_phase_status_change_update_project: true
    on_project_status_change_update_phase: false
    last_synced_at: null
    last_synced_by: null
```

### Step 6 – Report Ambiguities (Outside YAML)

After the YAML block, briefly list:

* Any logical keys you could not confidently map.
* Any assumptions you made (e.g., “Assumed `doc_id_field` → `doc_id` field in project.”).

Keep this explanation short and factual so it can be read by a human or ignored by downstream automation.

---

## [GUARDRAILS]

* **Do NOT** rename logical keys (`phase_id_field`, `status_field`, etc.) unless explicitly instructed.
* **Do NOT** change unrelated parts of the phase plan.
* **Do NOT** invent GitHub field names that don’t exist in the project metadata provided.
* When in doubt, **leave existing mappings unchanged** and surface a TODO in the explanation.

```

If you want, I can next take your **actual** `MASTER_SPLINTER_Phase_Plan_Template.yml` and produce:

- A patched `github_integration` block ready for your real Project,
- Plus a tiny “GH_SYNC pattern registry” entry (PATTERN_ID, description, owner, etc.).
::contentReference[oaicite:0]{index=0}
```
----


Nice, let’s lock this in.

Below is exactly what you asked for:

1. A **drop-in `github_integration` block** you can paste into `MASTER_SPLINTER_Phase_Plan_Template.yml`.
2. A **tiny GH_SYNC pattern registry entry** you can add to your pattern index or a dedicated registry file.

I’ll assume:

* Repo: `DICKY1987/complete-ai-development-pipeline-canonical-phase-plan`
* Project: you’ll use a Projects v2 board with fields named:

  * `Phase ID`
  * `Workstream`
  * `Status`
  * `Risk`
  * `Target date`
  * `doc_id`

You can adjust names later if your actual project fields differ.

---

## 1. Patched `github_integration` block for MASTER_SPLINTER

Paste this as a top-level key in `MASTER_SPLINTER_Phase_Plan_Template.yml` (near the bottom where it fits your structure). You can also merge it into an existing `integration`/`external` section if you have one.

```yaml
github_integration:
  enabled: true

  repo:
    owner: "DICKY1987"
    name: "complete-ai-development-pipeline-canonical-phase-plan"
    default_branch: "main"

  issue:
    mode: "one-per-phase"            # "one-per-phase" | "none" | "reuse"
    number: null                     # filled in once an Issue exists
    title_template: "[{phase_id}] {title}"
    body_template_path: null         # optional: path to custom .md template
    labels:
      - "phase-plan"
      - "splinter-phase"
    assignees:
      - null                         # optional default assignee

  project:
    # You can use either url OR (owner + project_number)
    url: null                        # e.g. "https://github.com/orgs/ORG_NAME/projects/1"
    owner: "DICKY1987"               # or your org name
    project_number: null             # e.g. 1
    item_id: null                    # filled in by sync script once created

    field_mappings:
      # logical_name       : "Exact GitHub Project field label"
      phase_id_field: "Phase ID"
      workstream_field: "Workstream"
      status_field: "Status"
      risk_field: "Risk"
      target_date_field: "Target date"
      doc_id_field: "doc_id"

      # Optional extras if your project defines them:
      story_points_field: "Story points"
      owner_field: "Owner"

  automation:
    allow_issue_create: true
    allow_issue_update: true
    allow_project_item_create: true
    allow_project_item_update: true

    # default: SPLINTER is source of truth → GitHub
    sync_direction: "yaml->github"   # or "bidirectional" later

    on_phase_status_change_update_project: true
    on_project_status_change_update_phase: false

    last_synced_at: null             # set by sync script
    last_synced_by: null             # e.g. "github-actions[bot]"
```

This is “ready” in the sense that:

* If you fill in `project.url` or `project.project_number`,
* and wire up the `ensure_issue` / `ensure_project_item` Python module from the previous message,

then **every phase YAML** can be synced into:

* a GitHub Issue, and
* a row/item in your Project with the right custom fields.

---

## 2. Tiny GH_SYNC pattern registry entry

Add something like this to your pattern registry (e.g. `patterns/registry/PATTERN_INDEX.yaml`) or a dedicated file such as `patterns/registry/gh_sync.yaml` depending on how you structure:

```yaml
- pattern_id: "PAT-GH-SYNC-PHASE-001"
  name: "GH_SYNC_PHASE_V1"
  version: "1.0.0"
  status: "active"

  category: "integration"
  owner_team: "devx-orchestration"
  owner_contact: "github-sync@local"

  description: >
    Synchronize SPLINTER Phase Plan specs with GitHub Issues and Projects v2.
    Ensures each phase has a corresponding Issue and Project item, and that
    project custom fields (Phase ID, Workstream, Status, Risk, Target date,
    doc_id) remain consistent with the ground-truth YAML.

  spec_path: "patterns/specs/GH_SYNC_PHASE_V1.pattern.yaml"
  schema_path: "patterns/schemas/GH_SYNC_PHASE_V1.schema.json"
  executor_path: "patterns/executors/github_sync/phase_sync.py"
  test_path: "patterns/tests/GH_SYNC_PHASE_V1_test.py"
  example_dir: "patterns/examples/github_sync/"

  tags:
    - "github"
    - "projects-v2"
    - "issues"
    - "integration"
    - "splinter"
```

You can then:

* Point `executor_path` at the module that contains `ensure_issue` and `ensure_project_item`.
* Later add a small spec file (`GH_SYNC_PHASE_V1.pattern.yaml`) that defines:

  * required config keys (the `github_integration` shape),
  * allowed `sync_direction` values,
  * and preconditions (e.g. “Project fields must exist before sync”).

---

Here’s a draft `patterns/specs/GH_SYNC_PHASE_V1.pattern.yaml` that should fit your PAT-CHECK-001 expectations and your general pattern style.

You can tweak paths/ids to match your actual registry, but the skeleton is ready to plug in.

```yaml
pattern_id: "PAT-GH-SYNC-PHASE-001"
doc_id: "DOC-PAT-GH-SYNC-PHASE-001"
name: "GH_SYNC_PHASE_V1"
version: "1.0.0"
role: "spec"                       # PAT-CHECK-001 requirement
status: "active"

schema_ref: "../schemas/GH_SYNC_PHASE_V1.schema.json"
executor_ref: "../executors/github_sync/phase_sync.py"

description: >
  Synchronize SPLINTER Phase Plan specs with GitHub Issues and GitHub Projects v2.
  Ensures each phase has a corresponding Issue and Project item, and that project
  custom fields (Phase ID, Workstream, Status, Risk, Target date, doc_id) remain
  consistent with the ground-truth YAML.

tags:
  - "integration"
  - "github"
  - "projects-v2"
  - "issues"
  - "splinter"
  - "orchestration"

ownership:
  owner_team: "devx-orchestration"
  owner_contact: "github-sync@local"

applicability:
  context:
    - "SPLINTER Phase Plans with a github_integration block"
    - "Repos using GitHub Issues and Projects v2 for planning"
  preconditions:
    - "GitHub repository exists and is accessible via GITHUB_TOKEN."
    - "GitHub Project v2 exists and defines the custom fields referenced in field_mappings."
    - "Phase Plan YAML passes structural validation against GH_SYNC_PHASE_V1.schema.json."
  non_goals:
    - "Does not create or manage GitHub Projects themselves."
    - "Does not modify SPLINTER phase semantics or acceptance criteria."
    - "Does not resolve merge conflicts or orchestrate PR lifecycles."

interfaces:
  inputs:
    phase_yaml_path:
      type: "string"
      description: "Path to the SPLINTER Phase Plan YAML file."
    phase_yaml:
      type: "object"
      description: "Parsed Phase Plan YAML document."
    github_token:
      type: "string"
      description: "GitHub API token with repo and project write permissions."
    github_integration:
      type: "object"
      description: "github_integration block from the Phase Plan."
  outputs:
    issue_number:
      type: "integer"
      description: "GitHub Issue number associated with this phase."
    project_item_id:
      type: "string"
      description: "GitHub ProjectV2 item node ID associated with this phase."
    sync_report:
      type: "object"
      description: "Summary of operations performed (created/updated issue, created/updated project item, field updates)."

config_contracts:
  github_integration:
    description: "Configuration block that drives GitHub sync behavior."
    required: true
    fields:
      enabled:
        type: "boolean"
        required: true
      repo:
        type: "object"
        required: true
        fields:
          owner:
            type: "string"
            required: true
          name:
            type: "string"
            required: true
          default_branch:
            type: "string"
            required: true
      issue:
        type: "object"
        required: true
        fields:
          mode:
            type: "string"
            enum: ["one-per-phase", "none", "reuse"]
            required: true
          number:
            type: ["integer", "null"]
            required: false
          title_template:
            type: "string"
            required: true
          body_template_path:
            type: ["string", "null"]
            required: false
          labels:
            type: "array"
            items_type: "string"
            required: true
          assignees:
            type: "array"
            items_type: ["string", "null"]
            required: true
      project:
        type: "object"
        required: true
        fields:
          url:
            type: ["string", "null"]
            required: false
          owner:
            type: "string"
            required: true
          project_number:
            type: ["integer", "null"]
            required: false
          item_id:
            type: ["string", "null"]
            required: false
          field_mappings:
            type: "object"
            required: true
            fields:
              phase_id_field:
                type: "string"
                required: true
              workstream_field:
                type: "string"
                required: true
              status_field:
                type: "string"
                required: true
              risk_field:
                type: "string"
                required: true
              target_date_field:
                type: "string"
                required: true
              doc_id_field:
                type: "string"
                required: true
              story_points_field:
                type: ["string", "null"]
                required: false
              owner_field:
                type: ["string", "null"]
                required: false
      automation:
        type: "object"
        required: true
        fields:
          allow_issue_create:
            type: "boolean"
            required: true
          allow_issue_update:
            type: "boolean"
            required: true
          allow_project_item_create:
            type: "boolean"
            required: true
          allow_project_item_update:
            type: "boolean"
            required: true
          sync_direction:
            type: "string"
            enum: ["yaml->github", "bidirectional"]
            required: true
          on_phase_status_change_update_project:
            type: "boolean"
            required: true
          on_project_status_change_update_phase:
            type: "boolean"
            required: true
          last_synced_at:
            type: ["string", "null"]
            required: false
          last_synced_by:
            type: ["string", "null"]
            required: false

behavior:
  overview:
    - "Treat SPLINTER Phase Plan as single source of truth for phase metadata."
    - "Create or update an Issue representing the phase (if issue.mode != 'none')."
    - "Create or update a Project item representing the phase in Projects v2."
    - "Map SPLINTER fields (phase_id, workstream_id, status, risk, target_date, doc_id) to Project custom fields using field_mappings."
  operations:
    ensure_issue:
      description: "Ensure a GitHub Issue exists for the phase; update if already present."
      preconditions:
        - "github_integration.enabled == true"
        - "issue.mode in ['one-per-phase', 'reuse']"
      postconditions:
        - "Issue exists with title/body/labels consistent with Phase Plan."
      failure_modes:
        - code: "GH_ISSUE_API_ERROR"
          description: "GitHub /issues API returned non-2xx or error payload."
        - code: "GH_ISSUE_DISABLED"
          description: "issue.mode == 'none' but ensure_issue was invoked."
    ensure_project_item:
      description: "Ensure a GitHub Project item exists and has correct field values."
      preconditions:
        - "github_integration.enabled == true"
        - "Project owner + project_number or url is resolvable."
        - "Issue exists and issue_number is known."
      postconditions:
        - "Project item exists linked to the issue."
        - "Fields listed in field_mappings have values consistent with Phase Plan."
      failure_modes:
        - code: "GH_PROJECT_RESOLVE_FAILED"
          description: "ProjectV2 node could not be resolved from owner/project_number or url."
        - code: "GH_PROJECT_ITEM_CREATE_FAILED"
          description: "ProjectV2 item creation mutation failed."
        - code: "GH_PROJECT_FIELD_UPDATE_FAILED"
          description: "One or more field updates failed."

constraints:
  must:
    - "MUST NOT run if github_integration.enabled is false."
    - "MUST validate github_integration structure against schema before execution."
    - "MUST use field_mappings values as exact GitHub Project field labels (no guessing)."
    - "MUST treat the Phase Plan YAML as authoritative for phase_id, workstream_id, status, risk, target_date, doc_id."
    - "MUST fail fast with a clear error if GitHub API calls return non-2xx or GraphQL errors."
  should:
    - "SHOULD avoid modifying Project fields that are not listed in field_mappings."
    - "SHOULD log sync operations (created/updated issue, created/updated project item, field updates)."
    - "SHOULD be idempotent when re-run with identical Phase Plan data."
  must_not:
    - "MUST NOT modify SPLINTER Phase Plan content in-place (no writing back to YAML) unless explicitly enabled by a higher-level pattern."
    - "MUST NOT create GitHub Projects; only use existing Project v2 instances."

telemetry:
  events:
    - name: "gh_sync_phase_started"
      payload_fields:
        - "pattern_id"
        - "phase_id"
        - "repo"
    - name: "gh_sync_phase_completed"
      payload_fields:
        - "pattern_id"
        - "phase_id"
        - "issue_number"
        - "project_item_id"
        - "duration_ms"
    - name: "gh_sync_phase_failed"
      payload_fields:
        - "pattern_id"
        - "phase_id"
        - "error_code"
        - "error_message"

examples:
  minimal_config_snippet:
    github_integration:
      enabled: true
      repo:
        owner: "DICKY1987"
        name: "complete-ai-development-pipeline-canonical-phase-plan"
        default_branch: "main"
      issue:
        mode: "one-per-phase"
        number: null
        title_template: "[{phase_id}] {title}"
        body_template_path: null
        labels:
          - "phase-plan"
          - "splinter-phase"
        assignees:
          - null
      project:
        url: "https://github.com/orgs/ORG_NAME/projects/1"
        owner: "ORG_NAME"
        project_number: 1
        item_id: null
        field_mappings:
          phase_id_field: "Phase ID"
          workstream_field: "Workstream"
          status_field: "Status"
          risk_field: "Risk"
          target_date_field: "Target date"
          doc_id_field: "doc_id"
          story_points_field: "Story points"
          owner_field: "Owner"
      automation:
        allow_issue_create: true
        allow_issue_update: true
        allow_project_item_create: true
        allow_project_item_update: true
        sync_direction: "yaml->github"
        on_phase_status_change_update_project: true
        on_project_status_change_update_phase: false
        last_synced_at: null
        last_synced_by: null
```

---

Here’s a solid **JSON Schema sketch** for `patterns/schemas/GH_SYNC_PHASE_V1.schema.json` that matches the `github_integration` contract we defined in the pattern spec and is suitable for PAT-CHECK-001–style validation.

### Intent / Scope

* This schema is designed to validate the **`github_integration` block** (as used inside your Phase Plans), not the entire Phase Plan.
* You can use it in two ways:

  1. As-is, to validate extracted `github_integration` objects.
  2. Wrapped inside a “full phase plan” schema (where `github_integration` is a required property).

You can adjust `$id` and `title` to match your repo.

---

## `patterns/schemas/GH_SYNC_PHASE_V1.schema.json`

```json
{
  "$id": "https://example.com/schemas/GH_SYNC_PHASE_V1.schema.json",
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "GH_SYNC_PHASE_V1 github_integration config",
  "description": "Schema for the github_integration block used by the GH_SYNC_PHASE_V1 pattern.",
  "type": "object",
  "additionalProperties": false,

  "required": [
    "enabled",
    "repo",
    "issue",
    "project",
    "automation"
  ],

  "properties": {
    "enabled": {
      "type": "boolean",
      "description": "Whether GitHub integration is active for this Phase Plan."
    },

    "repo": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "owner",
        "name",
        "default_branch"
      ],
      "properties": {
        "owner": {
          "type": "string",
          "minLength": 1,
          "description": "GitHub repository owner (user or org)."
        },
        "name": {
          "type": "string",
          "minLength": 1,
          "description": "GitHub repository name."
        },
        "default_branch": {
          "type": "string",
          "minLength": 1,
          "description": "Default branch name for the repo (e.g. 'main')."
        }
      }
    },

    "issue": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "mode",
        "title_template",
        "labels",
        "assignees"
      ],
      "properties": {
        "mode": {
          "type": "string",
          "enum": [
            "one-per-phase",
            "none",
            "reuse"
          ],
          "description": "How Issues are used for this phase."
        },
        "number": {
          "description": "GitHub Issue number, if already created.",
          "anyOf": [
            { "type": "integer", "minimum": 1 },
            { "type": "null" }
          ]
        },
        "title_template": {
          "type": "string",
          "minLength": 1,
          "description": "Template for Issue title, e.g. '[{phase_id}] {title}'."
        },
        "body_template_path": {
          "description": "Optional path to a markdown file used as Issue body template.",
          "anyOf": [
            { "type": "string", "minLength": 1 },
            { "type": "null" }
          ]
        },
        "labels": {
          "type": "array",
          "description": "Base labels to apply to the Issue.",
          "items": {
            "type": "string"
          }
        },
        "assignees": {
          "type": "array",
          "description": "Default assignees for the Issue (usernames).",
          "items": {
            "anyOf": [
              { "type": "string", "minLength": 1 },
              { "type": "null" }
            ]
          }
        }
      }
    },

    "project": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "owner",
        "field_mappings"
      ],
      "properties": {
        "url": {
          "description": "Optional full URL of the GitHub Project v2.",
          "anyOf": [
            { "type": "string", "minLength": 1 },
            { "type": "null" }
          ]
        },
        "owner": {
          "type": "string",
          "minLength": 1,
          "description": "Owner (user/org) of the Project v2."
        },
        "project_number": {
          "description": "Project number for Projects v2 (e.g. 1).",
          "anyOf": [
            { "type": "integer", "minimum": 1 },
            { "type": "null" }
          ]
        },
        "item_id": {
          "description": "Node ID of the ProjectV2 item, once known.",
          "anyOf": [
            { "type": "string", "minLength": 1 },
            { "type": "null" }
          ]
        },

        "field_mappings": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "phase_id_field",
            "workstream_field",
            "status_field",
            "risk_field",
            "target_date_field",
            "doc_id_field"
          ],
          "properties": {
            "phase_id_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for SPLINTER phase_id."
            },
            "workstream_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for SPLINTER workstream_id."
            },
            "status_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for SPLINTER phase status."
            },
            "risk_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for SPLINTER risk level."
            },
            "target_date_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for target/due date."
            },
            "doc_id_field": {
              "type": "string",
              "minLength": 1,
              "description": "Project field label for SPLINTER doc_id."
            },
            "story_points_field": {
              "description": "Optional Project field label for story points.",
              "anyOf": [
                { "type": "string", "minLength": 1 },
                { "type": "null" }
              ]
            },
            "owner_field": {
              "description": "Optional Project field label for owner/driver.",
              "anyOf": [
                { "type": "string", "minLength": 1 },
                { "type": "null" }
              ]
            }
          }
        }
      }
    },

    "automation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "allow_issue_create",
        "allow_issue_update",
        "allow_project_item_create",
        "allow_project_item_update",
        "sync_direction",
        "on_phase_status_change_update_project",
        "on_project_status_change_update_phase"
      ],
      "properties": {
        "allow_issue_create": {
          "type": "boolean",
          "description": "Allow creation of new Issues for phases."
        },
        "allow_issue_update": {
          "type": "boolean",
          "description": "Allow updating existing Issues for phases."
        },
        "allow_project_item_create": {
          "type": "boolean",
          "description": "Allow creation of new Project items."
        },
        "allow_project_item_update": {
          "type": "boolean",
          "description": "Allow updating existing Project items."
        },
        "sync_direction": {
          "type": "string",
          "enum": [
            "yaml->github",
            "bidirectional"
          ],
          "description": "Direction of truth: SPLINTER only, or bidirectional."
        },
        "on_phase_status_change_update_project": {
          "type": "boolean",
          "description": "If true, phase status changes should update Project field."
        },
        "on_project_status_change_update_phase": {
          "type": "boolean",
          "description": "If true, Project status changes may update phase status (only valid when sync_direction is 'bidirectional')."
        },
        "last_synced_at": {
          "description": "Timestamp of last successful sync, if known.",
          "anyOf": [
            { "type": "string", "minLength": 1 },
            { "type": "null" }
          ]
        },
        "last_synced_by": {
          "description": "Actor (username/bot) that performed the last sync, if known.",
          "anyOf": [
            { "type": "string", "minLength": 1 },
            { "type": "null" }
          ]
        }
      }
    }
  }
}
```

---

### How to use this with PAT-CHECK-001

1. Place this file at:

   ```text
   patterns/schemas/GH_SYNC_PHASE_V1.schema.json
   ```

2. Make sure your `GH_SYNC_PHASE_V1.pattern.yaml` has:

   ```yaml
   schema_ref: "../schemas/GH_SYNC_PHASE_V1.schema.json"
   ```

3. In your PAT-CHECK-001 implementation / validator:

   * When validating a **Phase Plan’s `github_integration` block**:

     * Extract `github_integration` from the YAML.
     * Convert to JSON.
     * Validate against `GH_SYNC_PHASE_V1.schema.json`.
   * When validating the **pattern spec**, you only need to check that:

     * `schema_ref` path exists and is valid JSON.
     * (Optionally) run a meta-schema check to ensure the schema file itself conforms to draft-07.

---


Perfect, let’s sketch a **full SPLINTER Phase Plan schema** that plugs in the `GH_SYNC_PHASE_V1` schema via `$ref`.

Assumptions:

* This file lives at:
  `patterns/schemas/SPLINTER_PHASE_PLAN_V1.schema.json`
* `GH_SYNC_PHASE_V1.schema.json` lives in the **same folder** (`patterns/schemas/`), so we can `$ref` it as `"GH_SYNC_PHASE_V1.schema.json"`.

You can tighten or expand individual sections later; this is a solid, usable skeleton.

---

## `patterns/schemas/SPLINTER_PHASE_PLAN_V1.schema.json`

```json
{
  "$id": "https://example.com/schemas/SPLINTER_PHASE_PLAN_V1.schema.json",
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "SPLINTER Phase Plan V1",
  "description": "Full schema for a SPLINTER Phase Plan document, including github_integration via GH_SYNC_PHASE_V1.",
  "type": "object",
  "additionalProperties": false,

  "required": [
    "doc_id",
    "template_version",
    "phase_identity",
    "dag_and_dependencies",
    "scope_and_modules",
    "environment_and_tools",
    "execution_profile",
    "pre_flight_checks",
    "execution_plan",
    "fix_loop_and_circuit_breakers",
    "expected_artifacts",
    "acceptance_tests",
    "completion_gate",
    "observability_and_metrics",
    "governance_and_constraints",
    "github_integration"
  ],

  "properties": {
    "doc_id": {
      "type": "string",
      "minLength": 1
    },
    "template_version": {
      "type": "string",
      "minLength": 1
    },

    "phase_identity": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "phase_id",
        "workstream_id",
        "title",
        "summary",
        "objective",
        "status"
      ],
      "properties": {
        "phase_id": {
          "type": "string",
          "minLength": 1
        },
        "workstream_id": {
          "type": "string",
          "minLength": 1
        },
        "title": {
          "type": "string",
          "minLength": 1
        },
        "summary": {
          "type": "string",
          "minLength": 1
        },
        "objective": {
          "type": "string",
          "minLength": 1
        },
        "status": {
          "type": "string",
          "minLength": 1
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "owner": {
          "type": "string"
        },
        "created_at": {
          "type": "string"
        },
        "updated_at": {
          "type": "string"
        }
      }
    },

    "dag_and_dependencies": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "depends_on",
        "may_run_parallel_with",
        "is_critical_path"
      ],
      "properties": {
        "depends_on": {
          "type": "array",
          "items": { "type": "string" }
        },
        "may_run_parallel_with": {
          "type": "array",
          "items": { "type": "string" }
        },
        "is_critical_path": {
          "type": "boolean"
        },
        "notes": {
          "type": "string"
        }
      }
    },

    "scope_and_modules": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "repo_root",
        "modules",
        "file_scope",
        "forbidden_paths",
        "worktree_strategy"
      ],
      "properties": {
        "repo_root": {
          "type": "string",
          "minLength": 1
        },
        "modules": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "module_id",
              "path"
            ],
            "additionalProperties": false,
            "properties": {
              "module_id": {
                "type": "string",
                "minLength": 1
              },
              "path": {
                "type": "string",
                "minLength": 1
              },
              "description": {
                "type": "string"
              }
            }
          }
        },
        "file_scope": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "forbidden_paths": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "worktree_strategy": {
          "type": "string",
          "minLength": 1
        }
      }
    },

    "environment_and_tools": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "runtimes",
        "cli_tools",
        "services"
      ],
      "properties": {
        "runtimes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [ "name", "version" ],
            "additionalProperties": false,
            "properties": {
              "name": { "type": "string" },
              "version": { "type": "string" }
            }
          }
        },
        "cli_tools": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [ "name", "command" ],
            "additionalProperties": false,
            "properties": {
              "name": { "type": "string" },
              "command": { "type": "string" },
              "description": { "type": "string" }
            }
          }
        },
        "services": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [ "name" ],
            "additionalProperties": false,
            "properties": {
              "name": { "type": "string" },
              "endpoint": { "type": "string" },
              "notes": { "type": "string" }
            }
          }
        }
      }
    },

    "execution_profile": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "risk_level",
        "phase_type",
        "concurrency"
      ],
      "properties": {
        "risk_level": {
          "type": "string"
        },
        "phase_type": {
          "type": "string"
        },
        "concurrency": {
          "type": "string"
        },
        "estimated_duration": {
          "type": "string"
        },
        "notes": {
          "type": "string"
        }
      }
    },

    "pre_flight_checks": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "description"
        ],
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "commands": {
            "type": "array",
            "items": { "type": "string" }
          },
          "expected_result": {
            "type": "string"
          }
        }
      }
    },

    "execution_plan": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "steps"
      ],
      "properties": {
        "steps": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "name",
              "kind"
            ],
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "kind": { "type": "string" },
              "description": { "type": "string" },
              "commands": {
                "type": "array",
                "items": { "type": "string" }
              },
              "inputs": {
                "type": "array",
                "items": { "type": "string" }
              },
              "outputs": {
                "type": "array",
                "items": { "type": "string" }
              },
              "guardrails": {
                "type": "array",
                "items": { "type": "string" }
              },
              "requires_human_review": {
                "type": "boolean"
              }
            }
          }
        }
      }
    },

    "fix_loop_and_circuit_breakers": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "max_retries": {
          "type": "integer",
          "minimum": 0
        },
        "retry_backoff": {
          "type": "string"
        },
        "circuit_breaker_conditions": {
          "type": "array",
          "items": { "type": "string" }
        },
        "notes": {
          "type": "string"
        }
      }
    },

    "expected_artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "path"
        ],
        "properties": {
          "id": { "type": "string" },
          "path": { "type": "string" },
          "description": { "type": "string" },
          "format": { "type": "string" }
        }
      }
    },

    "acceptance_tests": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "description"
        ],
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "commands": {
            "type": "array",
            "items": { "type": "string" }
          },
          "expected_outcome": {
            "type": "string"
          }
        }
      }
    },

    "completion_gate": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "criteria"
      ],
      "properties": {
        "criteria": {
          "type": "array",
          "items": { "type": "string" }
        },
        "signoff_required": {
          "type": "boolean"
        },
        "signoff_roles": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "observability_and_metrics": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "metrics": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [ "name" ],
            "properties": {
              "name": { "type": "string" },
              "description": { "type": "string" },
              "unit": { "type": "string" }
            }
          }
        },
        "logging": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "governance_and_constraints": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "must": {
          "type": "array",
          "items": { "type": "string" }
        },
        "should": {
          "type": "array",
          "items": { "type": "string" }
        },
        "must_not": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "extensions": {
      "type": "object",
      "additionalProperties": true,
      "description": "Custom fields / extensions for phase-specific data."
    },

    "github_integration": {
      "$ref": "GH_SYNC_PHASE_V1.schema.json"
    }
  }
}
```

---

Here’s a small, drop-in **PAT-CHECK-001 validation order note** you can paste into your PAT-CHECK-001 v2 doc (e.g. under a “Validation Order” / “Implementation Notes” section).

You can keep it as plain text or markdown.

```markdown
### PAT-CHECK-001 – Validation Order for SPLINTER Phase Plans

Implementations of PAT-CHECK-001 MUST validate SPLINTER Phase Plans and
their GitHub integration in the following order:

1. **Pattern Registry & Specs**
   1.1. Validate `patterns/registry/PATTERN_INDEX.yaml`:
        - Must be valid YAML.
        - Every `pattern_id` entry must have `spec_path`, `schema_path`,
          `executor_path`, `test_path`, and `example_dir`.
   1.2. For `PAT-GH-SYNC-PHASE-001` (`GH_SYNC_PHASE_V1`):
        - Ensure `spec_path` exists and is valid YAML.
        - Ensure `schema_path` exists and is valid JSON (`GH_SYNC_PHASE_V1.schema.json`).
        - Ensure `executor_path` exists (e.g. `patterns/executors/github_sync/phase_sync.py`).

2. **Global SPLINTER Phase Plan Schema**
   For each SPLINTER Phase Plan document (e.g. under `phases/`):
   2.1. Parse YAML and validate against
        `patterns/schemas/SPLINTER_PHASE_PLAN_V1.schema.json`:
        - This schema defines the full Phase Plan structure:
          `phase_identity`, `dag_and_dependencies`, `scope_and_modules`,
          `environment_and_tools`, `execution_profile`, `pre_flight_checks`,
          `execution_plan`, `fix_loop_and_circuit_breakers`,
          `expected_artifacts`, `acceptance_tests`, `completion_gate`,
          `observability_and_metrics`, `governance_and_constraints`,
          `extensions`, and `github_integration`.
        - `github_integration` MUST be present and MUST conform to its `$ref`
          definition.

3. **Nested GitHub Integration Schema (GH_SYNC)**
   3.1. The `github_integration` property of the Phase Plan MUST be
        validated via the `$ref` to:
        `patterns/schemas/GH_SYNC_PHASE_V1.schema.json`.

   3.2. Implementations MAY either:
        - Rely on the `$ref` resolution provided by the JSON Schema engine, or
        - Explicitly extract `github_integration` and independently validate it
          against `GH_SYNC_PHASE_V1.schema.json`.

   3.3. A Phase Plan is considered **non-compliant with PAT-CHECK-001** if:
        - It passes the top-level SPLINTER schema but its `github_integration`
          block fails `GH_SYNC_PHASE_V1` schema validation, OR
        - It omits `github_integration` when it is required by
          `SPLINTER_PHASE_PLAN_V1.schema.json`.

4. **Execution Preconditions for GH_SYNC_PHASE_V1**
   Before executing the `GH_SYNC_PHASE_V1` pattern:
   4.1. The corresponding Phase Plan MUST have:
        - Passed validation against `SPLINTER_PHASE_PLAN_V1.schema.json`.
        - Passed validation of `github_integration` against
          `GH_SYNC_PHASE_V1.schema.json`.
   4.2. If either validation fails, the GH_SYNC executor MUST NOT run and
        MUST emit a clear, machine-readable error indicating which schema
        failed and why.

Implementations that follow this order ensure that:
- Registry and pattern specs are structurally sound before use.
- Every SPLINTER Phase Plan is structurally valid as a whole.
- The `github_integration` contract is guaranteed correct before any
  GitHub-side effects (Issues / Projects) occur.
```

---

Here’s a **full but still “skeleton”** `validate_phase_plan.py` that follows the PAT-CHECK-001 order we defined:

* Validate **PATTERN_INDEX + GH_SYNC spec/schema** (step 1).
* Validate the **Phase Plan** against `SPLINTER_PHASE_PLAN_V1.schema.json` (step 2).
* Validate **github_integration** against `GH_SYNC_PHASE_V1.schema.json` (step 3).
* Emit a **JSON report** to stdout.

You can drop this into `scripts/validate_phase_plan.py`.

```python
#!/usr/bin/env python
"""
validate_phase_plan.py

PAT-CHECK-001-aligned validator for SPLINTER Phase Plans.

Validation order:

1. Pattern Registry & GH_SYNC pattern:
   - patterns/registry/PATTERN_INDEX.yaml
   - patterns/specs/GH_SYNC_PHASE_V1.pattern.yaml
   - patterns/schemas/GH_SYNC_PHASE_V1.schema.json

2. Full Phase Plan schema:
   - patterns/schemas/SPLINTER_PHASE_PLAN_V1.schema.json

3. Nested github_integration block:
   - validate via GH_SYNC_PHASE_V1.schema.json

Outputs a machine-readable JSON report to stdout.
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # pip install pyyaml
from jsonschema import Draft7Validator, RefResolver  # pip install jsonschema


# =========================
# DATA MODELS
# =========================

@dataclass
class CheckResult:
    id: str
    description: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    details: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


@dataclass
class ValidationReport:
    ok: bool
    phase_file: str
    checks: List[CheckResult]
    errors: List[Dict[str, Any]]


# =========================
# UTILITIES
# =========================

def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _make_error(code: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "context": context or {},
    }


def validate_with_schema(
    instance: Any,
    schema: Dict[str, Any],
    base_uri: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return a list of error dicts (empty list == no errors).
    """
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    validator = Draft7Validator(schema, resolver=resolver)

    errors: List[Dict[str, Any]] = []
    for e in validator.iter_errors(instance):
        errors.append(
            {
                "path": list(e.path),
                "message": e.message,
                "validator": e.validator,
                "validator_value": e.validator_value,
            }
        )
    return errors


# =========================
# VALIDATION STEPS
# =========================

def step_1_validate_pattern_registry_and_gh_sync(
    repo_root: Path,
) -> CheckResult:
    """
    Step 1: Validate PATTERN_INDEX and GH_SYNC pattern spec/schema.
    """
    description = "Validate PATTERN_INDEX and GH_SYNC pattern (spec + schema)"
    errors: List[Dict[str, Any]] = []

    try:
        patterns_dir = repo_root / "patterns"
        registry_path = patterns_dir / "registry" / "PATTERN_INDEX.yaml"
        gh_spec_path = patterns_dir / "specs" / "GH_SYNC_PHASE_V1.pattern.yaml"
        gh_schema_path = patterns_dir / "schemas" / "GH_SYNC_PHASE_V1.schema.json"

        # 1.1 PATTERN_INDEX.yaml exists and is valid YAML
        if not registry_path.is_file():
            errors.append(_make_error(
                "PAT_INDEX_MISSING",
                f"Missing pattern registry at {registry_path}",
            ))
        else:
            try:
                registry_data = load_yaml(registry_path)
            except Exception as ex:
                errors.append(_make_error(
                    "PAT_INDEX_INVALID_YAML",
                    f"Failed to parse PATTERN_INDEX.yaml: {ex}",
                ))
                registry_data = None

            # Minimal structural sanity check
            if registry_data is not None and not isinstance(registry_data, list):
                errors.append(_make_error(
                    "PAT_INDEX_BAD_STRUCTURE",
                    "Expected PATTERN_INDEX.yaml to be a list of pattern entries.",
                ))

        # 1.2 GH_SYNC spec exists and is valid YAML
        if not gh_spec_path.is_file():
            errors.append(_make_error(
                "GH_SYNC_SPEC_MISSING",
                f"Missing GH_SYNC pattern spec at {gh_spec_path}",
            ))
        else:
            try:
                _ = load_yaml(gh_spec_path)
            except Exception as ex:
                errors.append(_make_error(
                    "GH_SYNC_SPEC_INVALID_YAML",
                    f"Failed to parse GH_SYNC spec: {ex}",
                ))

        # GH_SYNC schema exists and is valid JSON
        if not gh_schema_path.is_file():
            errors.append(_make_error(
                "GH_SYNC_SCHEMA_MISSING",
                f"Missing GH_SYNC schema at {gh_schema_path}",
            ))
        else:
            try:
                _ = load_json(gh_schema_path)
            except Exception as ex:
                errors.append(_make_error(
                    "GH_SYNC_SCHEMA_INVALID_JSON",
                    f"Failed to parse GH_SYNC schema: {ex}",
                ))

    except Exception as ex:
        errors.append(_make_error(
            "STEP1_UNEXPECTED_EXCEPTION",
            f"Unexpected exception during step 1: {ex}",
        ))

    if errors:
        return CheckResult(
            id="STEP_1_PATTERN_REGISTRY_AND_GH_SYNC",
            description=description,
            status="FAIL",
            errors=errors,
            details="One or more registry/spec/schema checks failed.",
        )
    else:
        return CheckResult(
            id="STEP_1_PATTERN_REGISTRY_AND_GH_SYNC",
            description=description,
            status="PASS",
            details="PATTERN_INDEX and GH_SYNC spec/schema are present and parseable.",
        )


def step_2_validate_phase_plan_structure(
    repo_root: Path,
    phase_path: Path,
) -> CheckResult:
    """
    Step 2: Validate full Phase Plan YAML against SPLINTER_PHASE_PLAN_V1 schema.
    """
    description = "Validate Phase Plan against SPLINTER_PHASE_PLAN_V1.schema.json"
    errors: List[Dict[str, Any]] = []

    try:
        phase_data = load_yaml(phase_path)

        schema_path = repo_root / "patterns" / "schemas" / "SPLINTER_PHASE_PLAN_V1.schema.json"
        if not schema_path.is_file():
            errors.append(_make_error(
                "SPLINTER_SCHEMA_MISSING",
                f"Missing SPLINTER Phase Plan schema at {schema_path}",
            ))
        else:
            schema = load_json(schema_path)
            base_uri = f"file://{schema_path.parent.resolve()}/"

            schema_errors = validate_with_schema(phase_data, schema, base_uri=base_uri)
            if schema_errors:
                errors.extend(
                    _make_error(
                        "SPLINTER_SCHEMA_VALIDATION_ERROR",
                        "SPLINTER Phase Plan failed schema validation.",
                        {"schema_errors": schema_errors},
                    )
                )

    except Exception as ex:
        errors.append(_make_error(
            "STEP2_UNEXPECTED_EXCEPTION",
            f"Unexpected exception during step 2: {ex}",
        ))

    if errors:
        return CheckResult(
            id="STEP_2_SPLINTER_PHASE_SCHEMA",
            description=description,
            status="FAIL",
            errors=errors,
            details="Phase Plan did not pass SPLINTER_PHASE_PLAN_V1 schema validation.",
        )
    else:
        return CheckResult(
            id="STEP_2_SPLINTER_PHASE_SCHEMA",
            description=description,
            status="PASS",
            details="Phase Plan conforms to SPLINTER_PHASE_PLAN_V1 schema.",
        )


def step_3_validate_github_integration_block(
    repo_root: Path,
    phase_path: Path,
) -> CheckResult:
    """
    Step 3: Validate github_integration block with GH_SYNC_PHASE_V1 schema.
    """
    description = "Validate github_integration block against GH_SYNC_PHASE_V1.schema.json"
    errors: List[Dict[str, Any]] = []

    try:
        phase_data = load_yaml(phase_path)
        gh_block = phase_data.get("github_integration")

        if gh_block is None:
            errors.append(_make_error(
                "GITHUB_INTEGRATION_MISSING",
                "Phase Plan is missing github_integration block.",
            ))
        else:
            schema_path = repo_root / "patterns" / "schemas" / "GH_SYNC_PHASE_V1.schema.json"
            if not schema_path.is_file():
                errors.append(_make_error(
                    "GH_SYNC_SCHEMA_MISSING",
                    f"Missing GH_SYNC schema at {schema_path}",
                ))
            else:
                schema = load_json(schema_path)
                base_uri = f"file://{schema_path.parent.resolve()}/"
                schema_errors = validate_with_schema(gh_block, schema, base_uri=base_uri)
                if schema_errors:
                    errors.extend(
                        _make_error(
                            "GH_SYNC_SCHEMA_VALIDATION_ERROR",
                            "github_integration block failed GH_SYNC schema validation.",
                            {"schema_errors": schema_errors},
                        )
                    )

    except Exception as ex:
        errors.append(_make_error(
            "STEP3_UNEXPECTED_EXCEPTION",
            f"Unexpected exception during step 3: {ex}",
        ))

    if errors:
        return CheckResult(
            id="STEP_3_GH_SYNC_SCHEMA",
            description=description,
            status="FAIL",
            errors=errors,
            details="github_integration block did not pass GH_SYNC_PHASE_V1 schema validation.",
        )
    else:
        return CheckResult(
            id="STEP_3_GH_SYNC_SCHEMA",
            description=description,
            status="PASS",
            details="github_integration block conforms to GH_SYNC_PHASE_V1 schema.",
        )


# =========================
# MAIN ENTRYPOINT
# =========================

def build_report(repo_root: Path, phase_file: Path) -> ValidationReport:
    all_checks: List[CheckResult] = []
    all_errors: List[Dict[str, Any]] = []

    # Step 1: Registry + GH_SYNC pattern
    step1 = step_1_validate_pattern_registry_and_gh_sync(repo_root)
    all_checks.append(step1)
    if step1.errors:
        all_errors.extend(step1.errors)

    # Step 2: SPLINTER Phase Plan schema
    step2 = step_2_validate_phase_plan_structure(repo_root, phase_file)
    all_checks.append(step2)
    if step2.errors:
        all_errors.extend(step2.errors)

    # Step 3: GH_SYNC github_integration block
    step3 = step_3_validate_github_integration_block(repo_root, phase_file)
    all_checks.append(step3)
    if step3.errors:
        all_errors.extend(step3.errors)

    ok = all(c.status == "PASS" for c in all_checks)

    return ValidationReport(
        ok=ok,
        phase_file=str(phase_file),
        checks=all_checks,
        errors=all_errors,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a SPLINTER Phase Plan against PAT-CHECK-001 + GH_SYNC schemas."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Path to repository root (where patterns/, phases/, etc. live).",
    )
    parser.add_argument(
        "--phase-file",
        type=Path,
        required=True,
        help="Path to the SPLINTER Phase Plan YAML file to validate.",
    )

    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root.resolve()
    phase_file: Path = args.phase_file.resolve()

    report = build_report(repo_root, phase_file)

    # Emit machine-readable JSON report to stdout
    output = asdict(report)
    # Convert dataclass CheckResult objects to dicts explicitly
    output["checks"] = [asdict(c) for c in report.checks]

    print(json.dumps(output, indent=2))

    # Exit code: 0 if ok, 1 if any failures
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

### How to use it

From repo root:

```bash
python scripts/validate_phase_plan.py \
  --repo-root . \
  --phase-file phases/example_phase.yaml
```

* Exit code `0` → passes PAT-CHECK-001 checks for:

  * Registry + GH_SYNC spec/schema,
  * SPLINTER_PHASE_PLAN_V1 schema,
  * GH_SYNC_PHASE_V1 schema on `github_integration`.
* Exit code `1` → at least one failure; details are in the JSON printed to stdout.

You can then wire this into:

* A **pre-commit hook**, or
* A **GitHub Action** that blocks merges when `ok: false`.
