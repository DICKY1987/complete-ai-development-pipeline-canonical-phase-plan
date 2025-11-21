AIs use built-ins first

# Goal

A single, tool-agnostic **Capability Catalog** that any agent can query to decide: *“Is this already supported natively? If yes, how do I do it?”*

## Core artifacts (keep these separate but linked)

1. **`capabilities.jsonl` (machine-first) — “Capability Cards”**
   One JSON object per built-in feature.

2. **`intent_map.jsonl` — “Intent → Capability” patterns**
   Regex/keywords/DSL mapping user requests to capability IDs with priorities.

3. **`snippets/` — execution recipes**
   Minimal, copy-pastable commands/API calls per platform (PowerShell, bash, REST).

4. **`verify/` — preflight checks**
   Tiny scripts to confirm prerequisites (auth, CLI installed, perms).

5. **`capabilities.md` (human-friendly)**
   Auto-generated index + brief summaries for people.

---

## Capability Card schema (JSONL)

Use stable IDs, tags, and verification hooks so LLMs can reason deterministically.

```json
{
  "id": "cap.gh.issue.create.v1",
  "title": "Create a GitHub issue",
  "summary": "Create an issue in a repo via GitHub CLI.",
  "category": "GitHub/Issues",
  "platforms": ["windows","macos","linux"],
  "tools": ["gh"],
  "prerequisites": [
    "gh installed",
    "gh auth login",
    "repo remote configured or --repo <OWNER/REPO>"
  ],
  "intent_synonyms": [
    "open ticket","new issue","file a bug","feature request"
  ],
  "commands": [
    {"shell":"pwsh","snippet":"gh issue create --title \"{title}\" --body \"{body}\" --assignee \"{user?}\" --label \"{labels?}\""},
    {"shell":"bash","snippet":"gh issue create -t \"{title}\" -b \"{body}\""}
  ],
  "api": [{"name":"REST issues#create","ref":"https://docs.github.com/..."}],
  "limitations": ["Requires repo access and auth."],
  "verification": [{"run":"verify/gh_auth_status.ps1","expect":"OK"}],
  "examples": [
    {"ask":"file a bug for repo X","solution_ref":"commands[0]"}
  ]
}
```

## Intent map entry (JSONL)

```json
{
  "pattern": "(create|open|file).*(issue|bug|ticket)",
  "deny_if": ["jira","linear"], 
  "candidates": [
    {"capability_id":"cap.gh.issue.create.v1","score":0.92},
    {"capability_id":"cap.github.api.issues.create.v1","score":0.75}
  ]
}
```

---

## Built-In-First Gate (how every agent should use it)

1. **Normalize the user ask → intent tokens.**
2. **Query `intent_map.jsonl` → get candidate capability IDs.**
3. **Load Capability Cards → check `verification` scripts.**
4. **If verified**, return the exact `commands/snippets` and stop.
5. **If not verified or no match**, only then propose custom automation; include reason: *“No native capability”* or *“Prereq failed: gh not authed.”*

### Drop-in system prompt snippet

> **Policy:** Before designing new code, consult the Capability Catalog. If a matching capability exists and verifies, return the built-in solution verbatim with prerequisites and one runnable example. Only invent new automation when no verified capability exists. Always cite the `capability_id`.

---

## Minimal retrieval approach (no heavy infra required)

* Start with **BM25 keyword search** over `intent_map.jsonl` (fast and predictable).
* Optionally add embeddings later; still keep regex patterns for determinism.
* Cache the top 50 Capability Cards in memory for speed.

---

## Versioning & governance

* **IDs are immutable**; add `.v2` when behavior changes.
* Each card includes `changed_at`, `source_url`, and a short **changelog**.
* Nightly job to diff upstream docs and open PRs to update cards/snippets.

---

## What to build first (1–2 hours)

1. Seed 20–40 top tasks (GitHub `gh` basics, Claude Code CLI, PowerShell core ops).
2. Write 6–8 **verify** scripts (auth checks, tool presence).
3. Implement a tiny **resolver** (50–100 lines) that:

   * reads `intent_map.jsonl` → candidates
   * loads cards → runs verification
   * outputs: `{capability_id, why_matched, prerequisites, command}`

---

## Example agent response (wired to your catalog)

> **Found built-in:** `cap.gh.issue.create.v1` (0.92 match)
> **Prereqs:** gh installed ✓, auth ✓
> **Run:**
> `gh issue create --title "Crash on startup" --body "Steps to reproduce…" --label "bug"`
> *(Using GitHub’s native capability; no custom script needed.)*

If you want, I can generate a starter **capabilities.jsonl**, **intent_map.jsonl**, and a few **verify/** scripts for your stack (gh, PowerShell, Claude Code CLI) so you can drop them into a repo and start enforcing this gate.


here are concrete examples of what your **snippets/** (execution recipes) and **verify/** (preflight checks) can cover. I’ve grouped them by common tools you use. Each item shows a sample **task**, a minimal **snippet**, and a tiny **verify** script idea (PowerShell) that returns non-zero on failure so agents can gate on it.

---

## GitHub (gh)

1. **Create an issue**
   **snippet/pwsh:**

```powershell
gh issue create --title "Crash on startup" --body "Steps to reproduce…" --label bug
```

**verify/gh_auth_status.ps1:**

```powershell
$auth = gh auth status 2>$null
if ($LASTEXITCODE -ne 0) { Write-Error "gh not authed"; exit 1 }
Write-Output "OK"
```

2. **Open a PR from current branch**
   **snippet/pwsh:**

```powershell
$base="main"; gh pr create --base $base --fill
```

**verify/gh_repo_ready.ps1:**

```powershell
git rev-parse --is-inside-work-tree 2>$null | Out-Null; if ($LASTEXITCODE -ne 0){Write-Error "No git repo"; exit 1}
gh repo view 2>$null; if ($LASTEXITCODE -ne 0){Write-Error "No remote or no access"; exit 1}
"OK"
```

3. **Dispatch a workflow**
   **snippet/pwsh:**

```powershell
gh workflow run ci.yml --ref main
```

**verify/gh_workflow_visible.ps1:**

```powershell
gh workflow list | Select-String -SimpleMatch "ci.yml" | Out-Null
if (-not $?) { Write-Error "ci.yml not found"; exit 1 } ; "OK"
```

4. **Create a release and upload an asset**
   **snippet/pwsh:**

```powershell
$tag="v1.2.3"
gh release create $tag --notes "Automated release"
gh release upload $tag .\dist\app.zip
```

**verify/file_exists.ps1:**

```powershell
param([Parameter(Mandatory)]$Path)
if (-not (Test-Path $Path)) { Write-Error "Missing $Path"; exit 1 } ; "OK"
```

5. **Add an item to GitHub Projects**
   **snippet/pwsh:**

```powershell
gh project item-add --project "OWNER/1" --url "$(gh issue view --json url -q .url)"
```

**verify/gh_projects_enabled.ps1:**

```powershell
gh project list 2>$null; if ($LASTEXITCODE -ne 0){Write-Error "No access to Projects"; exit 1} ; "OK"
```

---

## PowerShell / Windows OS

6. **Install a PowerShell module**
   **snippet/pwsh:**

```powershell
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force
```

**verify/module_available.ps1:**

```powershell
param([Parameter(Mandatory)]$Name)
if (-not (Get-Module -ListAvailable $Name)) { Write-Error "Module $Name missing"; exit 1 } ; "OK"
```

7. **Zip a folder**
   **snippet/pwsh:**

```powershell
Compress-Archive -Path .\src -DestinationPath .\artifacts\src.zip -Force
```

**verify/path_and_write.ps1:**

```powershell
param($Dir,$Out)
if (-not (Test-Path $Dir)) { Write-Error "Missing $Dir"; exit 1 }
New-Item -ItemType Directory -Path (Split-Path $Out) -Force | Out-Null
"OK"
```

8. **Set a persistent user environment variable**
   **snippet/pwsh:**

```powershell
[System.Environment]::SetEnvironmentVariable("MY_TOKEN","<redacted>","User")
```

**verify/env_set.ps1:**

```powershell
param($Name)
$val = [Environment]::GetEnvironmentVariable($Name,"User")
if ([string]::IsNullOrWhiteSpace($val)) { Write-Error "$Name not set"; exit 1 } ; "OK"
```

9. **Start/stop a Windows service**
   **snippet/pwsh:**

```powershell
Stop-Service -Name wuauserv -Force; Start-Sleep 2; Start-Service -Name wuauserv
```

**verify/service_running.ps1:**

```powershell
param($Name)
$s = Get-Service -Name $Name -ErrorAction SilentlyContinue
if (-not $s -or $s.Status -ne 'Running'){ Write-Error "$Name not running"; exit 1 } ; "OK"
```

---

## Git (local)

10. **Create branch and push**
    **snippet/pwsh:**

```powershell
git checkout -b feat/x && git push -u origin feat/x
```

**verify/git_clean.ps1:**

```powershell
$status = git status --porcelain
if ($status){ Write-Error "Uncommitted changes present"; exit 1 } ; "OK"
```

11. **Force-sync remote to local (dangerous; single-dev)**
    **snippet/pwsh:**

```powershell
git push origin +HEAD:main
```

**verify/remote_reachable.ps1:**

```powershell
git ls-remote --exit-code origin 2>$null
if ($LASTEXITCODE -ne 0){ Write-Error "Remote unreachable"; exit 1 } ; "OK"
```

---

## Python / Node / Tooling

12. **Create & use Python venv; run tests**
    **snippet/pwsh:**

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; pytest -q
```

**verify/python_ok.ps1:**

```powershell
python --version 2>$null; if ($LASTEXITCODE -ne 0){ Write-Error "Python missing"; exit 1 } ; "OK"
```

13. **Install a global Node tool**
    **snippet/pwsh:**

```powershell
npm i -g @mermaid-js/mermaid-cli
```

**verify/command_on_path.ps1:**

```powershell
param($Cmd)
if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)){ Write-Error "$Cmd not found"; exit 1 } ; "OK"
```

---

## Docker (if you use it)

14. **Build & run a container**
    **snippet/pwsh:**

```powershell
docker build -t myapp:dev .
docker run --rm -p 8080:8080 myapp:dev
```

**verify/docker_running.ps1:**

```powershell
docker info 2>$null; if ($LASTEXITCODE -ne 0){ Write-Error "Docker not running"; exit 1 } ; "OK"
```

---

## Docs / Validation

15. **Validate JSON against a schema (Python)**
    **snippet/pwsh:**

```powershell
python - <<'PY'
import json, sys, jsonschema
schema=json.load(open('schema.json')); data=json.load(open('data.json'))
jsonschema.validate(instance=data, schema=schema); print("VALID")
PY
```

**verify/files_present.ps1:**

```powershell
'data.json','schema.json' | ForEach-Object { if (-not (Test-Path $_)) { Write-Error "Missing $_"; exit 1 } }
"OK"
```

---

### How these plug into your **Capability Cards**

* Each **snippet** becomes one or more `commands[]` entries (tagged `shell: "pwsh"` or `bash`).
* Each **verify** script is referenced in the card’s `verification[]` list:

  ```json
  {"run":"verify/gh_auth_status.ps1","expect":"OK"}
  ```
* Agents call `verification` first; only if it’s **OK** do they present the snippet as the solution.

If you want, say the word and I’ll package these into starter files:

* `verify/` scripts (ready-to-run .ps1)
* `snippets/` examples
* 6–8 sample **capability cards** that reference them
* a tiny **intent_map.jsonl** so agents can match user asks to these built-ins.


Here’s what a **fully-optimized, built-in-first Capability Catalog** system looks like end-to-end—fast, deterministic, multi-agent, and audit-ready.

# 1) High-level shape

* **Single source of truth**: a versioned **Capability Catalog** (JSONL) plus a tiny **resolver service** every agent can call (HTTP + CLI + PowerShell module).
* **Policy gate**: “Use built-ins first.” Agents must query/verify a native capability before proposing custom automation.
* **Deterministic + observable**: every decision logged, reproducible, and explainable.

# 2) Repo layout (monorepo)

```
cap-catalog/
├─ catalog/
│  ├─ capabilities.jsonl            # Capability Cards (one JSON per line)
│  ├─ intent_map.jsonl              # Intent → capability candidates
│  ├─ synonyms.json                 # Shared lexicon (alias → canonical)
│  ├─ platforms.json                # OS/tool detection rules
│  └─ deprecations.json             # Redirects (cap.v1 → cap.v2)
├─ snippets/                        # Execution recipes (pwsh, bash, REST)
│  ├─ gh/issue_create.ps1
│  └─ …
├─ verify/                          # Preflight checks (exit 0/1, print “OK”)
│  ├─ gh_auth_status.ps1
│  └─ command_on_path.ps1
├─ server/                          # Sidecar service
│  ├─ app.py                        # /resolve, /verify, /run (optional)
│  └─ adapters/                     # gh, powershell, docker, etc.
├─ clients/
│  ├─ ps/CapCatalog.psm1            # PowerShell module: Resolve-Capability
│  └─ py/capcatalog/                # Python client
├─ schemas/
│  ├─ capability.schema.json        # Strict JSON Schema
│  └─ intent_map.schema.json
├─ tests/
│  ├─ resolve_goldens/              # Input → expected capability ID(s)
│  ├─ verify_matrix.yml             # OS x Tool prereq matrix
│  └─ acceptance/
├─ ci/
│  ├─ validate_json.yml             # jsonschema, lint, uniqueness
│  ├─ verify_on_runners.yml         # run verify/ on Win/Linux runners
│  └─ release.yml                   # tag, changelog, artifacts
├─ docs/
│  ├─ capabilities.md               # Human index (auto-generated)
│  └─ integration.md                # “How agents use the gate”
└─ .ledger/                         # Append-only JSONL audit logs
   ├─ decisions.jsonl               # resolver outcomes
   └─ updates.jsonl                 # catalog changes
```

# 3) Core data models (stable, versioned)

**Capability Card (capabilities.jsonl)**

* `id` (immutable, ULID/semver), `title`, `summary`, `category`
* `platforms` (windows/macos/linux), `tools` (gh, docker, pwsh)
* `prerequisites` (natural language)
* `verification[]` (scripts with args, timeouts, expected output)
* `commands[]` (snippets; multiple shells; parameterized placeholders)
* `api[]` (official docs refs), `limitations[]`, `examples[]`
* `changed_at`, `source_url`, `changelog`

**Intent Map (intent_map.jsonl)**

* `pattern` (regex/keywords), optional `embedding_hint`
* `deny_if[]` (disqualifiers, e.g., “jira” for gh flows)
* `candidates[]` `{capability_id, prior}` (priors per environment)
* Optional **routing guards** (requires_os, requires_tool)

# 4) Resolver algorithm (fast + explainable)

1. **Normalize** user ask → tokens, OS/tool context, repo context.
2. **Candidate retrieval**

   * **Regex/keyword match** (primary, deterministic).
   * **BM25** over `intent_map.jsonl` (secondary).
   * (Optional) **embedding similarity** as a small tie-breaker only.
3. **Scoring**

   * Base score from intent_map priors + pattern confidence.
   * Add bonuses for context matches (e.g., gh repo present).
   * Subtract for deny_if or missing platform/tool.
4. **Verification gate**

   * Run each candidate’s `verification` scripts sandboxed with timeouts.
   * Cache pass/fail by (host, repo, user, TTL).
5. **Selection**

   * Pick **first verified** highest-score candidate.
   * If none verify, return “no verified built-in” + top N unverified with reasons.
6. **Output**

   * `{capability_id, why_matched, prerequisites, verified: true/false, commands[], docs_ref, audit_id}`

# 5) Sidecar service (so *any* agent can use it)

* **Endpoints**

  * `POST /resolve` `{ask, context}` → ranked candidates (+ verify results)
  * `POST /verify` `{capability_id}` → pass/fail, transcript
  * `POST /run` `{capability_id, params}` → (optional) executes snippet safely
  * `GET /capabilities/:id` → raw card
  * `GET /search?q=...` → quick lookup
* **Bindings**

  * Local HTTP (localhost:7788)
  * **PowerShell module**: `Resolve-Capability`, `Invoke-Capability`
  * **Python**: `capcatalog.resolve("open a PR")`

# 6) Agent integration (policy gate)

**System prompt snippet (all agents)**

> Before proposing new code/automation, call the Capability Catalog `/resolve`.
> If a verified capability exists, return its snippet verbatim with prerequisites and cite `capability_id`.
> Only invent new automation if no verified capability exists; explain why (e.g., missing tool/auth).

**Minimal code wrapper**

* Intercepts the user ask → calls `/resolve`.
* Injects the best verified snippet + “DoD” into the agent’s working context.
* Records the **decision** in `.ledger/decisions.jsonl`.

# 7) Governance & CI/CD

* **Schema validation** (JSON Schema) on every PR; reject unknown fields.
* **ID guard**: capability IDs immutable; v2 requires deprecation map entry.
* **Cross-OS verify matrix**: CI runs all `verify/` scripts on Windows/Linux.
* **Snippets smoke test**: dry-run/syntax checks (no destructive flags).
* **Docs drift bot**: nightly scraper diffs official docs → opens PRs with suggested card updates.
* **Release**: signed artifacts (catalog snapshot, checksums), changelog generation, SBOM of scripts.

# 8) Security & safety

* **Read-only by default**; `/run` disabled unless explicitly enabled.
* **Command allowlist** + redaction of secrets in logs.
* **Time/CPU caps** for verification; no network unless required.
* **Quarantine** any capability marked “risky” (e.g., force-push) behind extra confirmation.

# 9) Performance targets

* `/resolve` p95 < **60 ms** with warm caches.
* Verify cache TTL **5–15 min** per capability/context.
* Catalog size: 200–600 cards; cold start load < 200 ms.

# 10) Telemetry & value tracking

* Metrics emitted to `metrics.jsonl` (and optional Prometheus):

  * `resolution_attempts`, `verified_hit_rate`, `time_saved_estimate`
  * Top unmatched intents (to drive catalog growth)
  * Fail reasons (auth missing, tool absent, invalid repo)
* Weekly report PR into `docs/metrics.md` with trend charts.

# 11) What “optimal” feels like for you (day-to-day)

* You ask **any** agent: “Open a PR to main and link it to Project Alpha.”

  * Agent calls `/resolve` → `cap.gh.pr.create.v2` verified, `cap.gh.project.item_add.v1` verified.
  * Agent replies with exact `gh` commands, prerequisites status (auth ✓, repo ✓), and runs them if allowed.
* You request something novel → resolver shows **no verified built-in** + closest candidates + missing prerequisites so you can decide to (a) enable a tool, or (b) greenlight custom automation.

# 12) Example “golden path” response (from an agent)

> **Built-in found & verified:** `cap.gh.pr.create.v2`
> **Why:** intent matched `(create|open).*(pr|pull request)`; Windows + gh present; repo remote detected.
> **Prereqs:** gh installed ✓, auth ✓, git repo ✓
> **Run:**
> `gh pr create --base main --fill`
> **Docs:** GitHub CLI → PRs
> *(Using built-ins; no custom code needed.)*
> **Audit:** decision ULID `01JFB…` recorded.

---

If you want, I can generate a **starter repo** (folders, schemas, 12 prefilled Capability Cards for gh/pwsh, verify scripts, a tiny `/resolve` server, and a PowerShell module) so you can see this “finished state” running locally in minutes.
