Hybrid UI_GUI shell_terminal_TUI engine

This style means:

> A **graphical “control cockpit”** that you click around in, wrapped around **one or more terminal/TUI processes** that do the real work and stream logs back.

It does **not** replace your CLI tools. It **organizes and drives** them.

---

## 1. Core idea

### GUI layer (the shell)

* Runs as a normal desktop app (window, buttons, panels, tabs).
* Main jobs:

  * Let you **choose what to run** (pipelines, workstreams, tools).
  * Show **state** (pending, running, quarantined, completed).
  * Let you **inspect details** without digging in the terminal history.
  * Provide **safe controls**: Start, Pause, Retry, Mark-complete, Open-in-editor, etc.

The GUI is like a **mission control dashboard**.

### Terminal/TUI layer (the engine)

* Your existing tools:

  * Aider, Codex CLI, Gemini CLI, git, custom scripts, etc.
* Main jobs:

  * Actually **run the commands**, edit files, execute tests, do refactors.
  * Emit **logs, diffs, and errors** as plain text.
* Often run:

  * In hidden pseudo-terminals (pty) that your GUI controls, or
  * In an embedded terminal widget you can see inside the GUI.

The terminal/TUI layer is the **factory floor** where real work happens.

---

## 2. High-level architecture

Imagine 4 big blocks:

1. **GUI Shell**

   * Main window, menus, sidebars, toolbars.
   * Pipeline board (“what’s running where?”).
   * Detail panels for each file/workstream.
   * Tabs for **Logs**, **Errors**, **Diff**, **Metadata**.

2. **Orchestrator / Job Manager**

   * Sits between GUI and terminal tools.
   * Keeps a **queue of jobs** (e.g., “Run Aider on Workstream X”).
   * Spawns processes in the right environment (PowerShell, WSL, etc.).
   * Tracks **status**: queued → running → succeeded/failed → quarantined.

3. **Terminal/TUI Adapters**

   * One adapter per tool family (Aider, Codex, tests, git, etc.).
   * Know how to:

     * Build the right command line.
     * Provide environment variables (OLLAMA_API_BASE, repo path, etc.).
     * Parse minimal structure from logs (e.g., “ERROR: …”, “TEST FAILED: …”).

4. **State & Storage Layer**

   * Keeps **structured records**:

     * Jobs, pipelines, tools, exits codes.
     * Log file paths, diff files, error JSON, etc.
   * This is what lets the GUI **rebuild its view** after restart.

---

## 3. What it *looks like* to you (UX model)

Picture a single window with these pieces:

### A. Pipeline overview (top or left)

* A **board** of workstreams and files, grouped by state:

  * **Waiting / Not started**
  * **In progress**
  * **Quarantine (needs review)**
  * **Completed / Locked**
* Each work item is a **card**:

  * Title (e.g., `PH07 – Refactor Path Resolver`).
  * Tags: e.g., “Aider first”, “Codex escalation allowed”.
  * Icons: which tools have touched it (Aider, Codex, Claude, Tests).
  * Small status indicator (green = clean, yellow = pending, red = error).

You never have to remember “what did I run last?” — the board shows it.

### B. Detail panel (right side)

When you click a card/workstream:

* **Summary tab**

  * Current status (Running, Waiting, Failed, Completed).
  * History of tool runs (Aider → Tests → Codex → Tests → Claude).
  * Links to the runs (open logs, open diffs).
* **Logs tab**

  * Live streaming log from whatever TUI/CLI is working on it.
  * Search box + filters (show only WARN/ERROR).
* **Files tab**

  * List of files this workstream touches.
  * Quick buttons: “Open in editor”, “Open containing folder”.
* **Controls**

  * Start/Restart.
  * Mark done / lock.
  * Escalate (e.g., “escalate to Codex/Claude”).

### C. Embedded terminal / console area (bottom)

* A **terminal-like view** inside the GUI:

  * Shows exact commands being run.
  * Shows raw TUI if a tool has interactive UI.
* You can switch between:

  * “System logs” (orchestrator).
  * “Tool logs” (Aider, Codex, etc.).
  * Maybe even “Manual shell” tab for ad-hoc commands.

This is where **“terminal/TUI does the heavy lifting and logs”** becomes visible, but you’re **still inside the GUI**.

---

## 4. Execution flow: click → job → TUI → logs → state

Here’s how a typical action flows through the hybrid system:

1. **You click in the GUI**

   * Example: you click “Run Aider on Workstream PH07”.
   * Or you click “Run pipeline: PH07 → tests → Codex if errors”.

2. **GUI sends a request to the Orchestrator**

   * The orchestrator creates a **Job** record:

     * Job ID, workstream ID, target tool (Aider), repo path, config, priority.
   * Status: `QUEUED`.

3. **Orchestrator spawns the terminal/TUI process**

   * Chooses environment:

     * PowerShell or WSL, depending on what that tool needs.
   * Assembles the exact command:

     * e.g., `aider --message-file PHASE_DEV_DOCS\AIDER_INSTRUCTIONS_PH07.txt`.
   * Starts child process in a pseudo-terminal, capturing:

     * STDOUT, STDERR, exit code.
   * Status: `RUNNING`.

4. **Logs stream back into the GUI**

   * The terminal output is:

     * Written to a log file, AND
     * Streamed live to the GUI log pane.
   * The GUI can colorize or organize lines (INFO/WARN/ERROR).

5. **Process ends**

   * Orchestrator reads the exit code:

     * `0` → success → status: `COMPLETED` (or “Ready for next stage”).
     * Non-zero → failure → status: `FAILED` or `QUARANTINE`.
   * It may parse the log for:

     * “tests failed”
     * “syntax error”
     * “AI refused action”
   * It saves metadata for later: timestamp, duration, tool version, etc.

6. **GUI updates the board**

   * The card moves columns (e.g., In Progress → Quarantine).
   * A badge appears to show failure or success.
   * You can now click into details, retry, or escalate.

All the complexity stays *behind* the GUI. To you, it’s just:

> “I clicked Run; I see logs; the card moved to **Done** or **Quarantine**.”

---

## 5. Division of responsibility (why this works well)

### GUI side (control & layout)

* **Focus**: state, visibility, safety.
* Responsibilities:

  * Track **what** should happen, not **how**.
  * Present **current snapshot** of all workstreams and tools.
  * Prevent accidents (e.g., running tools on locked/complete workstreams).
  * Offer explicit actions like:

    * “Start next workstream automatically when this one finishes”.
    * “Do not allow any tool to modify completed workstreams.”

### Terminal/TUI side (heavy lifting & logs)

* **Focus**: doing work, not presenting complex UI.
* Responsibilities:

  * Run **long-lived or chatty** tasks:

    * AI refactors, big tests, git operations.
  * Emit **machine-readable-enough** logs or sidecar files:

    * JSON with error details.
    * Standardized output formats for tests, linters, etc.
  * Handle interactive steps when necessary (the GUI can script answers or pass flags to make them non-interactive when safe).

---

## 6. Benefits for your pipeline

For your multi-agent AI pipeline (Aider → Codex → Gemini → Claude → etc.), this hybrid model gives you:

1. **Clear global picture**

   * GUI shows:

     * Which workstreams are active.
     * Which step of the pipeline each workstream is on (Aider / Codex / Claude / Tests).
     * Which ones are blocked or quarantined.

2. **Reuse of existing tools**

   * No need to re-implement Aider, Codex, or tests as GUI components.
   * You just **wrap** them and capture their outputs.

3. **Better safety**

   * Finished workstreams can be visually marked as **Locked**:

     * The GUI refuses to send new jobs targeting those.
     * The orchestrator can double-check and deny jobs on locked items.
   * Cuts down on “oops, I re-ran a tool on a completed module.”

4. **Deterministic logging**

   * Every run:

     * Has a Job ID.
     * Stores logs, exit code, and file touches.
   * GUI is just a **view over this log/state**, so:

     * You can crash/restart and still know what happened.

5. **Easy future expansion**

   * Want a **“Metrics” tab** later? Use the logs/state to show:

     * Average refactor time per tool.
     * Error rates by stage (Aider vs Codex vs Claude).
   * Want **auto-escalation**?

     * Orchestrator can read structured error JSON and auto-schedule the next tool in the chain.

---

## 7. Mental model summary

If you want a short mental model for this type:

> * **GUI = Mission control**: Cards, boards, buttons, progress.
> * **Terminal/TUI = Engines**: Aider, Codex, tests, git, etc.
> * **Orchestrator = Traffic cop**: decides what runs, when, with what data, and records results.

Everything you already do in raw terminals stays there—but **coordinated, visible, and controlled** through a single GUI shell.

If you’d like, next step I can:

* Map this hybrid model directly onto your stack
  (PowerShell + WSL + Aider + Codex + Git + your log/ledger design), **and**
* Sketch the first “GUI mod” as a standalone module: e.g., a “Workstream board + Log viewer” component that plugs into your future full GUI.
