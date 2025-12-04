---
doc_id: DOC-GUIDE-PIPELINE-RADAR-PLUGIN-928
---

You can think of this as a **“Pipeline Radar” plugin** for your future GUI: one pluggable panel whose only job is to answer:

> “For any file or workstream, where is it right now in the pipeline, and how did it get here?”

Below is a modular design that fits your existing architecture (runs/workstreams DB, error pipeline, AIM, PH-07 GUI plan) and can play nicely with other future panels.

---

## 1. Normalize the states first (so the UI stays simple)

Under the hood you already have multiple state systems:

* **Runs / workstreams** in SQLite (`runs.status`, `workstreams.status`)
* **Orchestrator steps:** EDIT → STATIC → RUNTIME
* **Error pipeline states:** S0…S4, S_SUCCESS, S4_QUARANTINE, S_ERROR_INFRA

For the GUI, collapse that into a small set of **display statuses**:

**Per workstream**

* `Waiting`  (db: `status = 'pending'`)
* `Running – Edit` / `Running – Static` / `Running – Runtime`
  (db: `status = 'editing' | 'static_check' | 'runtime_tests'` )
* `Fixing (Aider)` / `Fixing (Codex)` / `Fixing (Claude)`
  (derived from error pipeline state + `current_agent`)
* `Completed` (db: `status = 'done'`)
* `Failed` (db: `status = 'failed'`, error state not quarantine)
* `Quarantined` (error state `S4_QUARANTINE`)

**Per file**

* `Not started` (file appears in a bundle but its workstreams haven’t run)
* `In progress` (any owning workstream is not done/failed)
* `Passed pipeline` (all owning workstreams are `done` *and* last error state is `S_SUCCESS`)
* `Quarantined` (belongs to a workstream whose final error state is `S4_QUARANTINE`)
* `Stale / changed since last run` (optional: diff vs worktree / last step_attempt)

The GUI panel will **compute these derived statuses** using only read-queries on:

* `workstreams.files_scope` (from metadata_json)
* `workstreams.status`
* `errors` + error pipeline context (for quarantine vs success)
* error pipeline DB if you wire it in later.

---

## 2. Top-level layout: the “Pipeline Radar” panel

Make it a **plugin panel** in PH-07, e.g. `file_pipeline_panel.py`, with its own manifest in `config/plugins/file_pipeline.plugin.json` (fits your planned GUI plugin system).

### Layout idea (3 bands)

1. **Run overview bar (top, compact)**

   * Dropdown: **Run selector** (list of recent `run_id` from `runs` table).
   * Summary chips:

     * `Files passed`  ✅
     * `Files in progress` ⏳
     * `Files in quarantine` 🚫
     * `Workstreams: Waiting | Running | Completed`
   * This can reuse a shared “summary strip” component used by other panels.

2. **Middle: dual view toggle**

   * Tabs (same data, different lens):

     * **Workstream View** (Kanban / swimlane style)
     * **File View** (table or tree)

3. **Bottom: detail inspector**

   * Shows details for the selected file or workstream:

     * Status timeline
     * Last error report
     * Linked OpenSpec change + CCPM issue + GitHub issue
     * Links to other panels (Logs, Tools, AIM, etc.)

---

## 3. Workstream View (Kanban board)

### Columns (based on your workstream status + error pipeline)

* **Waiting** – `workstreams.status = 'pending'`
* **Running** – `status in ('started', 'editing', 'static_check', 'runtime_tests')`
* **Fixing** – derived from error state in `S0_MECHANICAL_AUTOFIX` / `S1_AIDER_FIX` / etc.
* **Quarantine** – final error state `S4_QUARANTINE`
* **Completed** – `workstreams.status = 'done'`

Each **card = one workstream**:

* **Header:** `ws-id` (e.g., `ws-hello-world`)
* **Badges:** `openspec_change`, `ccpm_issue`, `gate`
* **Files:** `files_scope` count, hover → quick list
* **Tool:** `tool` (e.g. aider / codex)
* **Current step:** EDIT / STATIC / RUNTIME / FIX(Aider) / etc. (derived from last `step_attempt.step_name`)

**Interactions:**

* Click a card → detail inspector (bottom) switches to “workstream details”.
* Right-click → context menu (future): “open in Logs panel”, “open in CCPM”, “open OpenSpec change”.

Because PH-07 says GUI must be read-heavy and write-light, this Kanban is **view-only**; no drag-drop changing states.

---

## 4. File View (file-centric table/tree)

You explicitly want **“where a file is in the pipeline”**, so this view is key.

### Data source

Build a read-API or query in `state_client.py` (PH-07) that:

1. Reads **all workstreams** and their `metadata_json.files_scope`.
2. Builds a map: `file_path -> [workstream_ids]`.
3. For the selected run, fetches `workstreams.status`, recent `step_attempts`, and last known error state.

### UI structure

* **Left filter sidebar**

  * Filter by:

    * Status (Passed / In progress / Quarantined / Not started)
    * File type (.py, .ps1, .md, .json, etc.)
    * Owning workstream (`ws-*`)
    * Path prefix (e.g., `src/pipeline/`, `docs/`, etc.)

* **Center: main table (or tree, grouped by folder)**
  Columns:

  * `File` (with repo-relative path)
  * `Status` (badge: Passed / In progress / Quarantined / Not started)
  * `Owning workstreams` (chips: `ws-001`, `ws-002`)
  * `Last step` (EDIT / STATIC / RUNTIME)
  * `Last run` (run_id + timestamp)
  * `Last agent` (none / mechanical / aider / codex / claude)

* **Right: file detail panel**

  * **Timeline** of pipeline states for this file:

    * EDIT → STATIC → RUNTIME → SUCCESS or QUARANTINE
  * **Last error summary** (if quarantined):

    * error code, message, last tool, error pipeline state.
  * Buttons (links only, not actions):

    * “View workstreams” → focuses Workstream tab and highlights the rows.
    * “View logs/events” → opens Logs panel filtered by this file.
    * “View OpenSpec/CCPM” → opens spec panel or external link.

---

## 5. Quarantine Center (specialized subview)

Because quarantine is a big deal for your error pipeline, give it a dedicated view:

* Either a **tab in the same panel** or a **separate panel plugin** (`quarantine_panel.py`) that reuses the same data service.

### Contents

* **Summary at top**:

  * `Quarantined files: N`
  * `Quarantined workstreams: M`
  * `Top error signatures` (from `errors.signature` with counts)

* **Main list/table**

  * Row per quarantined workstream or per file (toggle).
  * Columns:

    * ID (file or ws)
    * Error signature
    * Last agent (aider/codex/claude)
    * Attempts count
    * When quarantined

This view should be **read-only**, but it sets you up to add “unquarantine / re-run” actions later via a **separate, highly constrained service**.

---

## 6. Integration with other GUI components (future-friendly)

Design the panel as **one plugin** in the PH-07 plugin ecosystem so it composes cleanly:

* **Uses shared services**:

  * `state_client` for DB queries (runs, workstreams, step_attempts, errors).
  * `logs_client` for event log drill-downs.
  * `config_client` for session filters (e.g., default run, default view).
* **Emits no direct DB writes** (respecting GUI permissions matrix).
* **Subscribes to an event bus** / polling tick:

  * e.g. `engine_client` emits “run_updated”, “workstream_updated”.
  * Panel listens and refreshes only the affected rows.

Other panels it should cooperate with:

* **Dashboard panel:** shows a tiny version of your “run overview” strip; clicking it opens the full Pipeline Radar panel.
* **Runs panel:** choose a run there, broadcast selected run_id → Pipeline Radar updates.
* **Logs panel:** “view logs for this workstream/file” uses logs panel’s API.

---

## 7. Minimal v1 vs fancy v2

To keep things realistic:

### v1 (low effort, high value)

* Implement **one panel plugin** with:

  * Run selector
  * One table view:

    * rows = workstreams
    * columns = ws-id, status, files count, last step, has_quarantine (bool)
  * Clicking a row shows simple detail card.

This already answers:

* “What workstreams are waiting / in progress / done?”
* “Which ones are in trouble/quarantine?”

### v2 (full vision)

* Add **File View**, **Kanban View**, and **Quarantine Center** as described.
* Add integration paths to Logs, Tools, AIM, and CCPM/OpenSpec panels.
* Add small visual timeline per file/workstream.

---

