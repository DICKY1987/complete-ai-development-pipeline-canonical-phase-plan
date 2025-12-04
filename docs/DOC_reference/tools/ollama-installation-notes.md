---
doc_id: DOC-GUIDE-OLLAMA-INSTALLATION-NOTES-870
---


 ▐▛███▜▌   Claude Code v2.0.46
▝▜█████▛▘  Sonnet 4.5 · Claude Pro
  ▘▘ ▝▝    C:\Users\richg

> read this file, is ollama code installed and configred on this machine
  ⎿  Interrupted · What should Claude do instead?

> "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus\ollama-code.md"

● Read(ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus\ollama-code.md)
  ⎿  Read 27 lines
  ⎿  ALL_AI\CLAUDE.md
  ⎿  ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\CLAUDE.md
  ⎿  ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus\CLAUDE.md

● I'll read that file and check if ollama-code is installed and configured on your machine.

● Bash(where.exe ollama)
  ⎿  C:\Users\richg\AppData\Local\Programs\Ollama\ollama.exe

● Bash(npm list -g | grep -i "ollama-code")
  ⎿  No matches found

● Bash(npm list -g | grep -i "gemini")
  ⎿  ├── @google/gemini-cli@0.16.0

● Bash(ollama list)
  ⎿  NAME                     ID              SIZE      MODIFIED
     qwen2.5-coder:7b         dae161e27b0e    4.7 GB    46 hours ago
     deepseek-coder:latest    3ddd2d3fc8d2    776 MB    47 hours ago

● Bash(npm list -g 2>nul | head -50)
  ⎿  (No content)

● Search(pattern: "**/*ollama-code*")
  ⎿  Found 6 files (ctrl+o to expand)

● Read(AppData\Local\Temp\ollama-code-config.json)
  ⎿  Read 2 lines

● Bash(where.exe ollama-code)
  ⎿  Error: Exit code 1
     INFO: Could not find files for the given pattern(s).

● Bash(gemini --version 2>&1)
  ⎿  0.16.0

● Read(ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\Migrate Codex & adier WSL2 on Windows\DEEPSEEK + OLLAMA-CODE INSTALL & WIRING GUID.md)
  ⎿  Read 412 lines

● Bash(gemini --help 2>&1 | head -30)
  ⎿  Usage: gemini [options] [command]

     Gemini CLI - Launch an interactive CLI, use -p/--prompt for non-interactive mode
     … +28 lines (ctrl+o to expand)

● Bash(wsl -d Ubuntu -- bash -c "which ollama-code 2>/dev/null || echo 'not found'")
  ⎿  /usr/bin/ollama-code

● Bash(wsl -d Ubuntu -- bash -c "npm list -g 2>/dev/null | grep ollama")
  ⎿  ├── @tcsenpai/ollama-code@0.0.3

● Bash(wsl -d Ubuntu -- bash -c "ollama-code --help 2>&1 | head -20")
  ⎿  ollama [options]

     Ollama Code - Launch an interactive CLI, use -p/--prompt for non-interactive mode
     … +19 lines (ctrl+o to expand)

● Bash(wsl -d Ubuntu -- bash -c "test -f ~/.config/ollama-code/config.json && cat ~/.config/ollama-code/config.json || echo 'config not found'")
  ⎿  config not found

● Bash(wsl -d Ubuntu -- bash -c "ip route show | grep default | awk '{print \$3}'")
  ⎿  Error: Exit code 1
     awk: cmd. line:1: {print \}
     awk: cmd. line:1:        ^ backslash not last character on line

● Bash(wsl -d Ubuntu -- bash -c "ip route show | grep default")
  ⎿  default via 172.27.16.1 dev eth0 proto kernel

● Based on my investigation, here's the status of ollama-code on your machine:

  ✅ INSTALLED & PARTIALLY CONFIGURED

  What's Installed:

  1. Ollama (Windows host):
    - Location: C:\Users\richg\AppData\Local\Programs\Ollama\ollama.exe
    - Status: Running and functional
    - Models installed:
        - qwen2.5-coder:7b (4.7 GB)
      - deepseek-coder:latest (776 MB)
  2. ollama-code (WSL Ubuntu):
    - Package: @tcsenpai/ollama-code@0.0.3
    - Location: /usr/bin/ollama-code
    - Status: Installed and accessible in WSL
  3. gemini CLI (Windows):
    - Version: 0.16.0
    - Note: ollama-code is forked from this

  Configuration Status:

  ⚠️ PARTIAL - There's evidence of configuration but not complete:

  1. Config file exists: C:\Users\richg\AppData\Local\Temp\ollama-code-config.json
  {
    "baseUrl": "http://10.255.255.254:11434/v1",
    "model": "deepseek-coder"
  }
  2. Missing WSL config: No config file at ~/.config/ollama-code/config.json in WSL (where ollama-code is actually installed)
  3. Network mismatch: Config points to 10.255.255.254, but your current WSL → Windows host IP is 172.27.16.1

  To Complete Configuration:

  You need to create the proper config in WSL:

  wsl -d Ubuntu -- bash -c "mkdir -p ~/.config/ollama-code && cat > ~/.config/ollama-code/config.json << 'EOF'
  {
    \"baseUrl\": \"http://172.27.16.1:11434/v1\",
    \"model\": \"deepseek-coder\"
  }
  EOF"

  Summary: ollama-code IS installed in WSL, Ollama IS configured with models, but the config file needs to be created/updated in the correct location with the right IP address.

> create phase plan to deliver ready to use ollama code app

● I'll research the current setup and create a comprehensive phase plan to deliver a ready-to-use ollama-code app integrated into your pipeline.

● Plan(Research ollama-code integration requirements)
  ⎿  Done (42 tool uses · 87.6k tokens · 6m 19s)
  ⎿  User rejected Claude's plan:
     ╭────────────────────────────────────────────────────────────────────────────╮
     │ Phase Plan: Deliver Ready-to-Use ollama-code App                           │
     │                                                                            │
     │ Current State                                                              │
     │                                                                            │
     │ ✅ Already Installed:                                                      │
     │ - Ollama on Windows with models (qwen2.5-coder:7b, deepseek-coder)         │
     │ - ollama-code-cli in WSL Ubuntu (@tcsenpai/ollama-code@0.0.3)              │
     │ - Robust pipeline with tool_profiles.json system                           │
     │ - PowerShell profile with aider/codex helpers                              │
     │                                                                            │
     │ ⚠️ Missing Integration:                                                    │
     │ - WSL config file for ollama-code-cli                                      │
     │ - Tool profile entry in config/tool_profiles.json                          │
     │ - PowerShell helper functions (ollama-code-wsl, ollama-code-here-wsl)      │
     │ - Prompt templates and orchestrator integration                            │
     │ - Documentation and tests                                                  │
     │                                                                            │
     │ 6-Phase Delivery Plan                                                      │
     │                                                                            │
     │ Phase 0: Prerequisites Validation (1-2h)                                   │
     │                                                                            │
     │ - Verify WSL2, Ollama, Node.js, network access from WSL                    │
     │ - Confirm ollama-code-cli responds to --help                               │
     │ - Test Ollama API reachable from WSL (http://172.27.                       │
     │                                                                            │
     │ Phase 1: Configuration Files (2-3h)                                        │
     │                                                                            │
     │ - Create ~/.config/ollama-code/config.json in WSL (baseUrl, model)         │
     │ - Add ollama-code entry to config/tool_profiles.json (after aider pattern) │
     │ - Add ollama-code-wsl/ollama-code-here-wsl to PowerShell profile           │
     │ - Update WSL-Validate-All.ps1 to check ollama-code-cli                     │
     │                                                                            │
     │ Phase 2: Pipeline Integration (4-5h)                                       │
     │                                                                            │
     │ - Create prompt template: aider/templates/prompts/ollama_code_edit.txt.j2  │
     │ - Add run_ollama_code_edit() to aider/engine.py                            │
     │ - Update orchestrator.py to route tool: "ollama-code" workstreams          │
     │ - Create test workstream: ws-test-ollama-code.json                         │
     │                                                                            │
     │ Phase 3: Documentation (2-3h)                                              │
     │                                                                            │
     │ - Create docs/OLLAMA-CODE-INTEGRATION.md (install, config, usage)          │
     │ - Update WSL-INSTALLATION-GUIDE.md with Step 6                             │
     │ - Update docs/ARCHITECTURE.md with ollama-code integration                 │
     │ - Create 2-3 example workstreams                                           │
     │                                                                            │
     │ Phase 4: Testing & Validation (3-4h)                                       │
     │                                                                            │
     │ - Unit tests: tests/integration/test_ollama_code.py                        │
     │ - Smoke tests: tests/integration/test_ollama_code_smoke.py                 │
     │ - Update validate_workstreams.py to recognize ollama-code tool             │
     │ - Run full test suite                                                      │
     │                                                                            │
     │ Phase 5: AIM Integration (Optional, 2-3h)                                  │
     │                                                                            │
     │ - Add ollama-code to AIM_registry.json                                     │
     │ - Create AIM_ollama-code.ps1 adapter                                       │
     │ - Test capability detection                                                │
     │                                                                            │
     │ Total Effort: 16-23 hours (14-20h without optional Phase 5)                │
     │                                                                            │
     │ Critical Path: Phase 0 → 1 → 2 → 4                                         │
     │                                                                            │
     │ Key Deliverables                                                           │
     │                                                                            │
     │ 1. Functional ollama-code integration in pipeline                          │
     │ 2. PowerShell helpers matching aider/codex pattern                         │
     │ 3. WORKSTREAM_V1.1-compliant prompt templates                              │
     │ 4. Comprehensive documentation and tests                                   │
     │ 5. Example workstreams demonstrating usage                                 │
     │                                                                            │
     │ Success Criteria                                                           │
     │                                                                            │
     │ - Can execute: ollama-code-wsl <repo> from PowerShell                      │
     │ - Can run: python scripts/run_workstream.py --ws-id ws-test-ollama-code    │
     │ - All unit tests pass                                                      │
     │ - Documentation enables user self-service setup                            │
     ╰────────────────────────────────────────────────────────────────────────────╯

> the plan im working on now is the best execution yet this file is ai assesment of why, how can thiis plan and future plan be structured like this: "C:\Users\richg\ALL_AI\Complete AI Development Pipeline
– Canonical Phase Plan\given the AI a really good game board to play on.md"

● Read(ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\given the AI a really good game board to play on.md)
  ⎿  Read 159 lines

● Perfect! This document reveals the 7 winning patterns that make AI execution reliable. Let me restructure the ollama-code plan to follow this proven "game board" pattern:

  Key Patterns from "Good Game Board" Analysis

  1. Tight, phase-based tasks with explicit acceptance tests

  - Small, well-defined missions
  - Programmatic checks (not vibes)
  - Clear "run → check → fix → confirm" loops

  2. Automatic verification and self-healing

  - Check outputs after tool runs
  - If tool under-delivers, fix state directly
  - Re-run acceptance checks

  3. Strong isolation: worktrees + file-scoped changes

  - Sandboxed workspace per task
  - Small blast radius
  - Easy to diff, patch, rollback

  4. Patch-first thinking + rich test coverage

  - Crisp feedback: "applied cleanly / failed"
  - "passes test X / fails test X"
  - Not "app crashed somewhere"

  5. Narrow prompts + high-quality context

  - Single tight objective per workstream
  - Concrete questions of repo
  - No giant fuzzy refactors

  6. Parallelism only where dependencies allow

  - Simple dependency graph
  - Less cross-phase interference
  - Clear, independent work chunks

  7. AI as operator, not just code generator

  - Run command → Inspect outputs → Reason → Fix → Re-verify
  - Observable environment matches spec before declaring success

  ---
  RESTRUCTURED: ollama-code Integration Plan (Game Board Pattern)

  Phase Structure Overview

  Phase 0 (Prerequisites)
      ↓
  Phase 1 (WSL Config)
      ↓
  Phase 2A (Tool Profile) ║ Phase 2B (PowerShell Helpers)  ← PARALLEL
      ↓                    ↓
  Phase 3 (Merge & Validate)
      ↓
  Phase 4A (Prompt Template) ║ Phase 4B (Test Workstream)  ← PARALLEL
      ↓                      ↓
  Phase 5 (Orchestrator Integration)
      ↓
  Phase 6 (E2E Validation)

  ---
  Phase 0: Pre-Flight & Prerequisites

  Objective: Verify all hard dependencies exist and are accessible

  Workstream: ws-ollama-code-00-preflight

  File Scope: None (read-only validation)

  Tasks:
  1. Verify WSL2 with Ubuntu version 2
  2. Verify Ollama service responds on Windows (localhost:11434/api/tags)
  3. Verify Ollama accessible from WSL (172.27.16.1:11434/api/tags)
  4. Verify Node.js >=16 in WSL
  5. Verify ollama-code-cli exists in WSL (which ollama-code-cli)

  Acceptance Tests (Programmatic):
  # Test 1: WSL version
  $wslCheck = wsl --list --verbose | Select-String "Ubuntu.*2"
  if (-not $wslCheck) { throw "WSL2 Ubuntu not found" }

  # Test 2: Ollama on Windows
  $ollamaWin = curl -s http://localhost:11434/api/tags | ConvertFrom-Json
  if (-not $ollamaWin.models) { throw "Ollama not responding on Windows" }

  # Test 3: Ollama from WSL
  $ollamaWSL = wsl -d Ubuntu -- curl -sf http://172.27.16.1:11434/api/tags
  if (-not $ollamaWSL) { throw "Ollama not accessible from WSL" }

  # Test 4: Node.js version
  $nodeVer = wsl -d Ubuntu -- node --version
  if ([version]$nodeVer.TrimStart('v') -lt [version]"16.0") { throw "Node.js < 16" }

  # Test 5: ollama-code-cli exists
  $cliPath = wsl -d Ubuntu -- which ollama-code-cli
  if (-not $cliPath) { throw "ollama-code-cli not installed" }

  Self-Healing:
  - If Node.js missing → Run wsl-setup-step3-ubuntu.ps1
  - If ollama-code-cli missing → Run npm install -g @tcsenpai/ollama-code
  - If Ollama not accessible → Run configure-ollama-for-wsl.ps1

  Success Criteria: All 5 tests pass with exit code 0

  ---
  Phase 1: WSL Configuration File

  Objective: Create ollama-code config in WSL with correct network settings

  Workstream: ws-ollama-code-01-wsl-config

  File Scope:
  - CREATE: ~/.config/ollama-code/config.json (in WSL)

  Tasks:
  1. Create directory ~/.config/ollama-code/ in WSL
  2. Write config.json with baseUrl and model
  3. Set baseUrl to Windows host IP (172.27.16.1:11434)
  4. Set default model to deepseek-coder

  Implementation:
  wsl -d Ubuntu -- bash -c "
  mkdir -p ~/.config/ollama-code
  cat > ~/.config/ollama-code/config.json << 'EOF'
  {
    \"baseUrl\": \"http://172.27.16.1:11434\",
    \"model\": \"deepseek-coder\"
  }
  EOF
  "

  Acceptance Tests:
  # Test 1: Config file exists
  $configExists = wsl -d Ubuntu -- test -f ~/.config/ollama-code/config.json && echo "exists"
  if ($configExists -ne "exists") { throw "Config file not created" }

  # Test 2: Config is valid JSON
  $configJson = wsl -d Ubuntu -- cat ~/.config/ollama-code/config.json | ConvertFrom-Json
  if (-not $configJson.baseUrl) { throw "baseUrl missing" }
  if (-not $configJson.model) { throw "model missing" }

  # Test 3: baseUrl points to Windows host
  if ($configJson.baseUrl -notmatch "172\.27\.16\.1") { throw "Incorrect baseUrl" }

  # Test 4: ollama-code-cli can read config
  $cliTest = wsl -d Ubuntu -- ollama-code-cli --help
  if ($LASTEXITCODE -ne 0) { throw "ollama-code-cli cannot read config" }

  Self-Healing:
  - If config invalid → Regenerate with correct format
  - If permissions wrong → chmod 644 ~/.config/ollama-code/config.json

  Success Criteria: Config file exists, valid JSON, correct settings, CLI accepts it

  ---
  Phase 2A: Tool Profile Entry (PARALLEL with 2B)

  Objective: Add ollama-code to tool_profiles.json

  Workstream: ws-ollama-code-02a-tool-profile

  File Scope:
  - MODIFY: config/tool_profiles.json

  Tasks:
  1. Add ollama-code entry after line 126 (after aider profile)
  2. Set type to "ai"
  3. Configure WSL launcher with bash -lc pattern
  4. Set environment variables (OLLAMA_API_BASE, PYTHONIOENCODING)
  5. Add AIM integration fields

  Patch (unified diff):
  --- a/config/tool_profiles.json
  +++ b/config/tool_profiles.json
  @@ -126,6 +126,26 @@
       "aim_tool_id": "aider",
       "aim_capabilities": ["code_edit", "refactor", "explain"]
     },
  +  "ollama-code": {
  +    "type": "ai",
  +    "command": "wsl",
  +    "args": [
  +      "-d", "Ubuntu",
  +      "--", "bash", "-lc",
  +      "export OLLAMA_API_BASE='http://172.27.16.1:11434' && unset OPENAI_API_KEY ANTHROPIC_API_KEY && cd '{worktree_path}' && ollama-code-cli --model '{model_name}' --prompt-file '{prompt_file}'"
  +    ],
  +    "env": {
  +      "PYTHONIOENCODING": "utf-8"
  +    },
  +    "working_dir": "{worktree_path}",
  +    "timeout_sec": 1800,
  +    "success_exit_codes": [0],
  +    "capture_output": true,
  +    "aim_tool_id": "ollama-code",
  +    "aim_capabilities": ["code_generation", "task_execution", "local_only"]
  +  },
     "gh": {
       "type": "utility",
       "command": "gh",

  Acceptance Tests:
  # Test 1: File is valid JSON
  $profiles = Get-Content config/tool_profiles.json | ConvertFrom-Json
  if (-not $profiles) { throw "Invalid JSON" }

  # Test 2: ollama-code key exists
  if (-not $profiles.'ollama-code') { throw "ollama-code profile missing" }

  # Test 3: Required fields present
  $oc = $profiles.'ollama-code'
  if ($oc.type -ne "ai") { throw "Wrong type" }
  if ($oc.command -ne "wsl") { throw "Wrong command" }
  if (-not $oc.args) { throw "Missing args" }
  if (-not $oc.env) { throw "Missing env" }

  # Test 4: Tool profile loads in Python
  python -c "from core.engine.tools import load_tool_profiles; p=load_tool_profiles(); assert 'ollama-code' in p"
  if ($LASTEXITCODE -ne 0) { throw "Python cannot load profile" }

  Self-Healing:
  - If JSON invalid → Revert and re-apply patch
  - If schema validation fails → Fix required fields

  Success Criteria: Valid JSON, profile loads, all required fields present

  ---
  Phase 2B: PowerShell Helper Functions (PARALLEL with 2A)

  Objective: Add ollama-code-wsl helpers to PowerShell profile

  Workstream: ws-ollama-code-02b-ps-helpers

  File Scope:
  - MODIFY: ALL_AI/Profiles/DevProfile.ps1

  Tasks:
  1. Add ollama-code-wsl function after line 83
  2. Add ollama-code-here-wsl function
  3. Follow existing aider-wsl pattern
  4. Auto-detect Ollama IP (localhost or Windows host)

  Patch:
  --- a/ALL_AI/Profiles/DevProfile.ps1
  +++ b/ALL_AI/Profiles/DevProfile.ps1
  @@ -83,6 +83,48 @@
       wsl -d $wslDistro -- bash -lc "source ~/.venvs/codex/bin/activate && cd $wslPath && codex"
   }

  +# Launch ollama-code-cli in WSL for a specific repository
  +function ollama-code-wsl {
  +    param(
  +        [Parameter(Mandatory = $true)]
  +        [string]$RepoName,
  +        [string]$Model = "qwen2.5-coder:14b"
  +    )
  +
  +    $wslDistro = "Ubuntu"
  +    $wslPath = "/home/root/code/$RepoName"
  +
  +    Write-Host "Launching ollama-code-cli in WSL for repo: $RepoName" -ForegroundColor Cyan
  +    Write-Host "Model: $Model" -ForegroundColor Gray
  +
  +    $bash = @"
  +set -e
  +if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  +  export OLLAMA_API_BASE="http://127.0.0.1:11434"
  +else
  +  WIN_IP=`$(ip route show | awk '/default/ {print `$3}')
  +  export OLLAMA_API_BASE="http://`$WIN_IP:11434"
  +fi
  +unset OPENAI_API_KEY ANTHROPIC_API_KEY
  +cd '$wslPath'
  +ollama-code-cli --model '$Model'
  +"@
  +
  +    wsl -d $wslDistro -- bash -lc "$bash"
  +}
  +
  +# Launch ollama-code-cli in WSL for the current directory
  +function ollama-code-here-wsl {
  +    param(
  +        [string]$Model = "qwen2.5-coder:14b"
  +    )
  +
  +    $repoName = Split-Path -Leaf (Get-Location)
  +    Write-Host "Launching ollama-code-cli in WSL for repo: $repoName" -ForegroundColor Cyan
  +    ollama-code-wsl -RepoName $repoName -Model $Model
  +}
  +
   # Refresh profile without closing session
   function Refresh-DevProfile {
       Write-Host "Reloading DevProfile..." -ForegroundColor Yellow

  Acceptance Tests:
  # Test 1: Profile is valid PowerShell
  . $PROFILE
  if ($LASTEXITCODE -ne 0) { throw "Profile syntax error" }

  # Test 2: Functions defined
  $funcs = Get-Command -CommandType Function
  if (-not ($funcs | Where-Object Name -eq "ollama-code-wsl")) { throw "ollama-code-wsl not defined" }
  if (-not ($funcs | Where-Object Name -eq "ollama-code-here-wsl")) { throw "ollama-code-here-wsl not defined" }

  # Test 3: Function signature correct
  $params = (Get-Command ollama-code-wsl).Parameters
  if (-not $params.ContainsKey("RepoName")) { throw "RepoName parameter missing" }
  if (-not $params.ContainsKey("Model")) { throw "Model parameter missing" }

  # Test 4: Help text available
  $help = Get-Help ollama-code-wsl -ErrorAction SilentlyContinue
  # If no explicit help, at least function should exist

  Self-Healing:
  - If syntax error → Revert and re-apply
  - If function conflicts → Rename with unique suffix

  Success Criteria: Profile loads, both functions defined with correct parameters

  ---
  Phase 3: Merge & Validate Configuration

  Objective: Verify Phases 2A and 2B work together

  Workstream: ws-ollama-code-03-merge-validate

  File Scope: None (validation only)

  Tasks:
  1. Reload PowerShell profile
  2. Verify tool profile loads
  3. Test ollama-code-wsl function (dry-run)
  4. Validate end-to-end config chain

  Acceptance Tests:
  # Test 1: Profile reload successful
  . $PROFILE
  if ($LASTEXITCODE -ne 0) { throw "Profile reload failed" }

  # Test 2: Tool profile accessible
  $profiles = Get-Content config/tool_profiles.json | ConvertFrom-Json
  if (-not $profiles.'ollama-code') { throw "Tool profile not accessible" }

  # Test 3: Function can be invoked (mock test)
  $testFunc = ollama-code-wsl -RepoName "test-repo" -WhatIf 2>&1
  # Should not throw error, even if repo doesn't exist

  # Test 4: WSL config + Tool profile + PowerShell helpers all aligned
  $wslConfig = wsl -d Ubuntu -- cat ~/.config/ollama-code/config.json | ConvertFrom-Json
  $toolProfile = $profiles.'ollama-code'
  # Both should reference same Ollama endpoint
  if ($wslConfig.baseUrl -notmatch "172\.27\.16\.1") { throw "Config mismatch" }

  Self-Healing:
  - If profile conflicts → Clear and re-source
  - If tool profile not found → Re-run Phase 2A

  Success Criteria: All components accessible, no conflicts, aligned configuration

  ---
  Phase 4A: Prompt Template (PARALLEL with 4B)

  Objective: Create WORKSTREAM_V1.1 compliant prompt template

  Workstream: ws-ollama-code-04a-prompt-template

  File Scope:
  - CREATE: aider/templates/prompts/ollama_code_edit.txt.j2

  Tasks:
  1. Create Jinja2 template with WORKSTREAM_V1.1 sections
  2. Include [HEADER], [OBJECTIVE], [FILE_SCOPE], [TASKS], [CONSTRAINTS], [EXPECTED_OUTPUT]
  3. Add template variables: ws_id, repo_root, worktree_path, files_scope, tasks, etc.
  4. ASCII-only format (no emojis)

  Acceptance Tests:
  # Test 1: Template file exists
  if (-not (Test-Path "aider/templates/prompts/ollama_code_edit.txt.j2")) {
      throw "Template file missing"
  }

  # Test 2: Template is valid Jinja2
  python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('aider/templates/prompts')); t = env.get_template('ollama_code_edit.txt.j2')"
  if ($LASTEXITCODE -ne 0) { throw "Invalid Jinja2 syntax" }

  # Test 3: Required sections present
  $content = Get-Content "aider/templates/prompts/ollama_code_edit.txt.j2" -Raw
  $sections = @("[HEADER]", "[OBJECTIVE]", "[FILE_SCOPE]", "[TASKS]", "[CONSTRAINTS]", "[EXPECTED_OUTPUT]")
  foreach ($section in $sections) {
      if ($content -notmatch [regex]::Escape($section)) { throw "Missing $section" }
  }

  # Test 4: Template renders with test data
  python -c @"
  from jinja2 import Environment, FileSystemLoader
  env = Environment(loader=FileSystemLoader('aider/templates/prompts'))
  t = env.get_template('ollama_code_edit.txt.j2')
  result = t.render(ws_id='test', repo_root='.', worktree_path='.', files_scope=['test.py'], tasks=['test task'])
  assert '[HEADER]' in result
  assert 'test.py' in result
  "@
  if ($LASTEXITCODE -ne 0) { throw "Template render failed" }

  Self-Healing:
  - If Jinja2 syntax error → Fix and re-validate
  - If sections missing → Add required sections

  Success Criteria: Valid Jinja2, all sections present, renders successfully

  ---
  Phase 4B: Test Workstream (PARALLEL with 4A)

  Objective: Create minimal test workstream for ollama-code

  Workstream: ws-ollama-code-04b-test-workstream

  File Scope:
  - CREATE: workstreams/ws-test-ollama-code.json

  Tasks:
  1. Create test workstream JSON
  2. Set tool to "ollama-code"
  3. Use hello_world.py as test target
  4. Simple task: add comment
  5. Include acceptance test

  Acceptance Tests:
  # Test 1: Workstream file exists
  if (-not (Test-Path "workstreams/ws-test-ollama-code.json")) {
      throw "Workstream file missing"
  }

  # Test 2: Valid JSON
  $ws = Get-Content "workstreams/ws-test-ollama-code.json" | ConvertFrom-Json
  if (-not $ws) { throw "Invalid JSON" }

  # Test 3: Required fields present
  if ($ws.id -ne "ws-test-ollama-code") { throw "Wrong id" }
  if ($ws.tool -ne "ollama-code") { throw "Wrong tool" }
  if (-not $ws.files_scope) { throw "Missing files_scope" }
  if (-not $ws.tasks) { throw "Missing tasks" }
  if (-not $ws.acceptance_tests) { throw "Missing acceptance_tests" }

  # Test 4: Schema validation
  python scripts/validate_workstreams.py workstreams/ws-test-ollama-code.json
  if ($LASTEXITCODE -ne 0) { throw "Schema validation failed" }

  # Test 5: Target file exists
  if (-not (Test-Path $ws.files_scope[0])) { throw "Target file missing" }

  Self-Healing:
  - If schema invalid → Fix required fields
  - If target file missing → Create hello_world.py

  Success Criteria: Valid JSON, passes schema validation, target file exists

  ---
  Phase 5: Orchestrator Integration

  Objective: Wire ollama-code into orchestrator execution flow

  Workstream: ws-ollama-code-05-orchestrator

  File Scope:
  - MODIFY: aider/engine.py (or create if missing)
  - MODIFY: core/engine/orchestrator.py

  Tasks:
  1. Add run_ollama_code_edit() to aider/engine.py
  2. Implement prompt rendering logic
  3. Invoke tool via run_tool("ollama-code", context)
  4. Update orchestrator.py to route tool: "ollama-code"
  5. Add conditional: if tool == "ollama-code": use run_ollama_code_edit()

  Acceptance Tests:
  # Test 1: Function exists in aider/engine.py
  python -c "from aider.engine import run_ollama_code_edit; assert callable(run_ollama_code_edit)"
  if ($LASTEXITCODE -ne 0) { throw "run_ollama_code_edit not found" }

  # Test 2: Orchestrator imports function
  python -c "from core.engine.orchestrator import run_edit_step; import inspect; src = inspect.getsource(run_edit_step); assert 'ollama-code' in src"
  if ($LASTEXITCODE -ne 0) { throw "Orchestrator not updated" }

  # Test 3: Dry-run workstream (no actual execution)
  python scripts/run_workstream.py --ws-id ws-test-ollama-code --dry-run
  if ($LASTEXITCODE -ne 0) { throw "Dry-run failed" }

  # Test 4: Prompt file generated correctly
  python -c @"
  from pathlib import Path
  from aider.engine import run_ollama_code_edit
  from core.state import bundles, db
  # Mock context
  ctx = {'worktree_path': '.', 'repo_root': '.'}
  bundle = bundles.load_bundle('workstreams/ws-test-ollama-code.json')
  # Dry-run should generate prompt file
  "@
  if ($LASTEXITCODE -ne 0) { throw "Prompt generation failed" }

  Self-Healing:
  - If import error → Check function signature matches
  - If routing breaks → Revert orchestrator.py changes

  Success Criteria: Function callable, orchestrator routes correctly, dry-run succeeds

  ---
  Phase 6: End-to-End Validation

  Objective: Execute full workflow and verify all components work

  Workstream: ws-ollama-code-06-e2e-validation

  File Scope: None (execution & validation)

  Tasks:
  1. Execute test workstream: python scripts/run_workstream.py --ws-id ws-test-ollama-code
  2. Verify prompt file created in worktree
  3. Verify ollama-code-cli invoked via WSL
  4. Verify target file modified
  5. Run acceptance tests
  6. Check database for step results

  Acceptance Tests (The Big Ones):
  # Test 1: Workstream executes without errors
  python scripts/run_workstream.py --ws-id ws-test-ollama-code
  if ($LASTEXITCODE -ne 0) { throw "Workstream execution failed" }

  # Test 2: Worktree created
  $worktree = ".worktrees/ws-test-ollama-code"
  if (-not (Test-Path $worktree)) { throw "Worktree not created" }

  # Test 3: Prompt file generated
  $promptFile = "$worktree/.aider/prompts/ws-test-ollama-code_edit.txt"
  if (-not (Test-Path $promptFile)) { throw "Prompt file not generated" }

  # Test 4: Prompt contains required sections
  $prompt = Get-Content $promptFile -Raw
  if ($prompt -notmatch "\[HEADER\]") { throw "Prompt missing HEADER" }
  if ($prompt -notmatch "\[FILE_SCOPE\]") { throw "Prompt missing FILE_SCOPE" }

  # Test 5: Target file modified
  $targetFile = "$worktree/hello_world.py"
  $originalHash = (Get-FileHash "hello_world.py").Hash
  $modifiedHash = (Get-FileHash $targetFile).Hash
  if ($originalHash -eq $modifiedHash) { throw "File not modified" }

  # Test 6: Acceptance tests pass
  cd $worktree
  python hello_world.py
  if ($LASTEXITCODE -ne 0) { throw "Acceptance test failed" }

  # Test 7: Database records result
  python scripts/db_inspect.py | Select-String "ws-test-ollama-code"
  if ($LASTEXITCODE -ne 0) { throw "No database record" }

  # Test 8: Step marked as successful
  python -c @"
  from core.state import crud, db
  session = db.get_session()
  ws = crud.get_workstream_by_id(session, 'ws-test-ollama-code')
  assert ws.status == 'done' or ws.status == 'editing', f'Wrong status: {ws.status}'
  "@
  if ($LASTEXITCODE -ne 0) { throw "Step not marked successful" }

  Self-Healing:
  - If ollama-code-cli fails → Check WSL config, Ollama connectivity
  - If file not modified → Inspect ollama-code-cli output, adjust prompt
  - If acceptance tests fail → Manually verify expected behavior

  Success Criteria:
  - All 8 tests pass
  - File modified as expected
  - Database shows success
  - Observable environment matches spec

  ---
  Summary: How This Structure Follows the "Good Game Board" Pattern

  | Pattern                            | How Applied to ollama-code Plan                                |
  |------------------------------------|----------------------------------------------------------------|
  | 1. Tight phases + acceptance tests | Each phase has 4-8 programmatic PowerShell tests, not vibes    |
  | 2. Self-healing                    | Every phase includes "If X fails → Do Y" recovery logic        |
  | 3. Strong isolation                | Phases 2A/2B parallel, Phase 6 uses worktree, small file scope |
  | 4. Patch-first + tests             | Patches shown as unified diffs, test coverage at every phase   |
  | 5. Narrow prompts                  | Each workstream = 1 tight objective (e.g., "add tool profile") |
  | 6. Smart parallelism               | 2A║2B and 4A║4B run parallel, clear dependency graph           |
  | 7. AI as operator                  | Phase 6 = "Run → Inspect → Verify → Fix → Re-verify" loop      |

  Template for Future Plans

  ### Phase X: [Descriptive Name]
  **Objective**: [Single tight goal]

  **Workstream**: ws-[project]-[phase]-[slug]

  **File Scope**:
  - CREATE: [files to create]
  - MODIFY: [files to modify]

  **Tasks**:
  1. [Specific action]
  2. [Specific action]
  ...

  **Implementation**: [Code/commands if helpful]

  **Acceptance Tests** (Programmatic):
  ```powershell
  # Test 1: [What you're checking]
  [PowerShell command]
  if ([failure condition]) { throw "[Clear error]" }

  # Test 2: ...

  Self-Healing:
  - If [failure] → [Fix action]
  - If [failure] → [Fix action]

  Success Criteria: [Observable state that must be true]

  The key is: **Every phase must be provable via code, not vibes.** The AI acts as an operator who runs, inspects, and fixes until the environment matches the spec.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ bypass permissions on (shift+tab to cycle)                                                                                                                                        Approaching weekly limit





