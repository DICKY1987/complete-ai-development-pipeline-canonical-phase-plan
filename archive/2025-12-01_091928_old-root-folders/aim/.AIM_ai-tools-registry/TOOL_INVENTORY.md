---
doc_id: DOC-AIM-TOOL-INVENTORY-159
---

# Complete AI Development Pipeline - Tool & Application Inventory
# Generated: 2025-11-18 12:26:48
# Repository: Complete AI Development Pipeline – Canonical Phase Plan

## LEGEND
- **Executable Path**: Where the binary/script is located (system PATH or explicit)
- **Config File(s)**: Repository-local or user-level configuration files
- **Status**: ✅ Configured | ⚠️ Optional | ❌ Not Found | 🔧 External

---

## 1. CORE PLATFORM & RUNTIMES

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 1 | **Windows 10/11** | N/A (OS) | N/A | ✅ |
| 2 | **PowerShell 7** | `C:\Program Files\PowerShell\7\pwsh.exe` | `C:\Users\richg\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`, `.\scripts\*.ps1` | ✅ |
| 3 | **Python 3.12+** | `C:\Python312\python.exe` or `%LOCALAPPDATA%\Programs\Python\` | `.\requirements.txt`, `.\pytest.ini` | ✅ |
| 4 | **Git** | `C:\Program Files\Git\bin\git.exe` | `.\\.gitignore`, `.gitattributes` | ✅ |
| 5 | **SQLite** | Built into Python (`sqlite3` module) | `.\state\*.db` | ✅ |
| 6 | **Node.js** | `C:\Program Files\nodejs\node.exe` | `package.json` (not present) | ⚠️ |
| 7 | **npm** | `C:\Program Files\nodejs\npm.cmd` | N/A | ⚠️ |
| 8 | **WSL2** | `%SystemRoot%\System32\wsl.exe` | `.\scripts\wsl\*.ps1` | ⚠️ |
| 9 | **Ubuntu (WSL)** | `wsl -d Ubuntu` | `~/.bashrc`, `~/.profile` | ⚠️ |

---

## 2. AI CODING ASSISTANTS & LLM ENGINES

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 10 | **Aider** | `%LOCALAPPDATA%\Programs\Python\Scripts\aider.exe` | `.\\.aider.conf.yml`, `.\\.aider.model.settings.yml` | ✅ |
| 11 | **Claude Code** | `~/.claude/` (CLI/agent) | `.\CLAUDE.md`, `.\pm\*.md`, `.\\.claude\` | ✅ |
| 12 | **GitHub Copilot** | VS Code extension / `gh copilot` | `.\\.github\copilot-instructions.md` | ⚠️ |
| 13 | **Gemini 2.0 Flash** | API / Web Interface | N/A (API-based) | ⚠️ |
| 14 | **Ollama** | `C:\Users\richg\AppData\Local\Programs\Ollama\ollama.exe` | `C:\Users\richg\\.ollama\`, env: `OLLAMA_HOST` | ✅ |
| 15 | **DeepSeek-Coder** | Via Ollama (`ollama run deepseek-coder`) | Model stored in Ollama registry | ✅ |
| 16 | **DeepSeek-R1** | Via Ollama (`ollama run deepseek-r1`) | Model stored in Ollama registry | ✅ |
| 17 | **Qwen 2.5-Coder** | Via Ollama (`ollama run qwen2.5-coder`) | Model stored in Ollama registry | ✅ |
| 18 | **ollama-code-cli** | `pipx` or `pip install ollama-code-cli` | `~/.config/ollama-code/config.json` | ⚠️ |

---

## 3. PYTHON DEVELOPMENT TOOLS

### Quality & Testing (Required)

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 19 | **pytest** | `.venv\Scripts\pytest.exe` | `.\pytest.ini` | ✅ |
| 20 | **Ruff** | `.venv\Scripts\ruff.exe` | `.\config\tool_profiles.json` (args) | ✅ |
| 21 | **Black** | `.venv\Scripts\black.exe` | `.\config\tool_profiles.json` (args) | ✅ |
| 22 | **Mypy** | `.venv\Scripts\mypy.exe` | `.\config\tool_profiles.json` (args) | ✅ |

### Code Analysis & Security

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 23 | **Pylint** | `.venv\Scripts\pylint.exe` | `.\src\plugins\python_pylint\manifest.json` | ✅ |
| 24 | **Bandit** | `.venv\Scripts\bandit.exe` | `.\src\plugins\python_bandit\manifest.json` | ✅ |
| 25 | **Safety** | `.venv\Scripts\safety.exe` | `.\src\plugins\python_safety\manifest.json` | ✅ |
| 26 | **Pyright** | `npm install -g pyright` | `.\src\plugins\python_pyright\manifest.json` | ⚠️ |
| 27 | **isort** | `.venv\Scripts\isort.exe` | `.\src\plugins\python_isort_fix\manifest.json` | ✅ |

---

## 4. POWERSHELL TOOLS

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 28 | **PSScriptAnalyzer** | PowerShell Module | `.\config\tool_profiles.json` | ✅ |
| 29 | **Pester** | PowerShell Module | `.\config\tool_profiles.json` | ✅ |

---

## 5. LINTERS & FORMATTERS (Multi-Language)

### Markup & Data

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 30 | **yamllint** | `.venv\Scripts\yamllint.exe` | `.\config\tool_profiles.json` | ⚠️ |
| 31 | **Markdownlint** | `npx markdownlint-cli` | `.\src\plugins\md_markdownlint\manifest.json` | ⚠️ |
| 32 | **mdformat** | `.venv\Scripts\mdformat.exe` | `.\src\plugins\md_mdformat_fix\manifest.json` | ⚠️ |
| 33 | **codespell** | `.venv\Scripts\codespell.exe` | `.\src\plugins\codespell\manifest.json` | ⚠️ |
| 34 | **jq** | `C:\Program Files\jq\jq.exe` or via Chocolatey | `.\src\plugins\json_jq\manifest.json` | ⚠️ |

### JavaScript

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 35 | **ESLint** | `npx eslint` | `.\src\plugins\js_eslint\manifest.json` | ⚠️ |
| 36 | **Prettier** | `npx prettier` | `.\src\plugins\js_prettier_fix\manifest.json` | ⚠️ |

### Security

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 37 | **gitleaks** | `C:\Program Files\gitleaks\gitleaks.exe` | `.\src\plugins\gitleaks\manifest.json` | ⚠️ |
| 38 | **Semgrep** | `pip install semgrep` | `.\src\plugins\semgrep\manifest.json` | ⚠️ |

---

## 6. PROJECT MANAGEMENT & COORDINATION

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 39 | **GitHub CLI (gh)** | `C:\Program Files\GitHub CLI\gh.exe` | `.\config\github.yaml`, `.\docs\ccpm-github-setup.md` | ✅ |
| 40 | **CCPM** | `.\pm\` (command system) | `.\pm\commands\pm\*.md`, `.\\.claude\commands\` | ✅ |
| 41 | **OpenSpec** | `.\openspec\` | `.\openspec\project.md`, `.\openspec\specs\` | ✅ |

---

## 7. SPEC MANAGEMENT TOOLS (Internal)

| # | Tool | Executable Path | Config File(s) | Status |
|---|------|----------------|----------------|--------|
| 42 | **spec_guard** | `.\tools\spec_guard\guard.py` | N/A (internal) | ✅ |
| 43 | **spec_renderer** | `.\tools\spec_renderer\renderer.py` | N/A (internal) | ✅ |
| 44 | **spec_resolver** | `.\tools\spec_resolver\resolver.py` | N/A (internal) | ✅ |
| 45 | **spec_indexer** | `.\tools\spec_indexer\indexer.py` | N/A (internal) | ✅ |
| 46 | **spec_patcher** | `.\tools\spec_patcher\patcher.py` | N/A (internal) | ✅ |
| 47 | **hardcoded_path_indexer** | `.\tools\hardcoded_path_indexer.py` | `.\config\path_index.yaml` | ✅ |

---

## 8. PIPELINE SCRIPTS & AUTOMATION

| # | Script | Path | Config/Dependencies | Status |
|---|--------|------|---------------------|--------|
| 48 | **bootstrap.ps1** | `.\scripts\bootstrap.ps1` | `.\requirements.txt` | ✅ |
| 49 | **test.ps1** | `.\scripts\test.ps1` | `.\pytest.ini` | ✅ |
| 50 | **validate_workstreams.py** | `.\scripts\validate_workstreams.py` | `.\schema\workstream.schema.json` | ✅ |
| 51 | **validate_workstreams_authoring.py** | `.\scripts\validate_workstreams_authoring.py` | `.\schema\workstream.schema.json` | ✅ |
| 52 | **run_workstream.py** | `.\scripts\run_workstream.py` | `.\config\tool_profiles.json` | ✅ |
| 53 | **run_error_engine.py** | `.\scripts\run_error_engine.py` | `.\config\circuit_breakers.yaml` | ✅ |
| 54 | **generate_spec_index.py** | `.\scripts\generate_spec_index.py` | `.\docs\spec\` | ✅ |
| 55 | **generate_spec_mapping.py** | `.\scripts\generate_spec_mapping.py` | `.\docs\spec\` | ✅ |
| 56 | **init_db.py** | `.\scripts\init_db.py` | `.\schema\*.sql` | ✅ |
| 57 | **gh_epic_sync.py** | `.\scripts\gh_epic_sync.py` | `.\config\github.yaml` | ✅ |
| 58 | **gh_issue_update.py** | `.\scripts\gh_issue_update.py` | `.\config\github.yaml` | ✅ |
| 59 | **worktree_start.ps1/.sh** | `.\scripts\worktree_start.ps1` | Git worktree config | ✅ |
| 60 | **worktree_merge.ps1/.sh** | `.\scripts\worktree_merge.ps1` | Git worktree config | ✅ |

---

## 9. PLUGIN SYSTEM (src/plugins/)

| # | Plugin | Manifest Path | Config | Status |
|---|--------|---------------|--------|--------|
| 61 | **echo** | `.\src\plugins\echo\manifest.json` | N/A | ✅ |
| 62 | **test_runner** | `.\src\plugins\test_runner\manifest.json` | `.\src\plugins\test_runner\README.md` | ✅ |
| 63 | **path_standardizer** | `.\src\plugins\path_standardizer\manifest.json` | `.\pm\rules\path-standards.md` | ✅ |

---

## 10. CONFIGURATION HUB

| # | Config File | Purpose | Referenced By |
|---|-------------|---------|---------------|
| 64 | `.\config\tool_profiles.json` | Tool execution settings | All pipeline scripts |
| 65 | `.\config\aim_config.yaml` | AI tool routing/fallback | `.\core\aim_bridge.py` |
| 66 | `.\config\decomposition_rules.yaml` | Workstream decomposition | Planner module |
| 67 | `.\config\circuit_breakers.yaml` | Error handling limits | Error engine |
| 68 | `.\config\section_map.yaml` | Repository sections | Path indexer |
| 69 | `.\config\path_index.yaml` | Path abstraction | Path registry |
| 70 | `.\config\github.yaml` | GitHub integration | gh scripts |
| 71 | `.\schema\workstream.schema.json` | Workstream validation | validate_workstreams.py |
| 72 | `.\pytest.ini` | pytest configuration | pytest |
| 73 | `.\requirements.txt` | Python dependencies | pip install |
| 74 | `.\.aider.conf.yml` | Aider settings | Aider |
| 75 | `.\.aider.model.settings.yml` | Aider model config | Aider |

---

## 11. EXTERNAL DEPENDENCIES (API-based, no local binary)

| # | Service | Auth/Config | Documentation |
|---|---------|-------------|---------------|
| 76 | **OpenAI API** | `OPENAI_API_KEY` env var | API-based, no local install |
| 77 | **Anthropic API** | `ANTHROPIC_API_KEY` env var | API-based, no local install |
| 78 | **DeepSeek API** | `DEEPSEEK_API_KEY` env var | API-based, no local install |
| 79 | **Google Gemini API** | `GOOGLE_API_KEY` env var | API-based, no local install |

---

## INSTALLATION REFERENCE

### Quick Setup Commands

\\\powershell
# 1. Python Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. PowerShell Modules
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
Install-Module -Name Pester -Scope CurrentUser

# 3. GitHub CLI
winget install GitHub.cli

# 4. Ollama (Windows)
# Download from: https://ollama.com/download/windows
ollama pull qwen2.5-coder:7b
ollama pull deepseek-coder
ollama pull deepseek-r1

# 5. Aider
pip install aider-chat

# 6. Optional Node.js tools
npm install -g pyright markdownlint-cli prettier eslint

# 7. Optional Python tools
pip install yamllint codespell semgrep
\\\

---

## ENVIRONMENT VARIABLES

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `OLLAMA_API_BASE` | Ollama endpoint | `http://127.0.0.1:11434` |
| `OLLAMA_HOST` | Ollama server binding | `0.0.0.0:11434` |
| `AIDER_MODEL` | Default Aider model | `ollama_chat/qwen2.5-coder:7b` |
| `OPENAI_API_KEY` | OpenAI authentication | `sk-...` |
| `ANTHROPIC_API_KEY` | Claude authentication | `sk-ant-...` |
| `PYTHONIOENCODING` | Python I/O encoding | `utf-8` |
| `AIDER_NO_AUTO_COMMITS` | Aider behavior | `1` |

---

## SUMMARY STATISTICS

- **Total Tools/Apps**: 79
- **Python Tools**: 13 (pytest, ruff, black, mypy, bandit, etc.)
- **Linters/Formatters**: 11 (yamllint, eslint, markdownlint, etc.)
- **AI Agents**: 8 (Aider, Claude Code, Ollama models, etc.)
- **Internal Scripts**: 13 (validation, generation, orchestration)
- **Config Files**: 12 (tool_profiles, schemas, etc.)
- **Plugins**: 22 (in src/plugins/)

---

## KEY FILE PATHS SUMMARY

\\\
Repository Root: C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\

Core Directories:
├── .aider.conf.yml              # Aider configuration
├── .aider.model.settings.yml    # Aider model settings
├── CLAUDE.md                    # Claude Code instructions
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── config\
│   ├── tool_profiles.json       # Tool execution profiles
│   ├── aim_config.yaml          # AI tool routing
│   ├── circuit_breakers.yaml    # Error handling
│   ├── decomposition_rules.yaml # Workstream rules
│   ├── section_map.yaml         # Repo sections
│   ├── path_index.yaml          # Path registry
│   └── github.yaml              # GitHub config
├── schema\
│   └── workstream.schema.json   # Workstream validation
├── scripts\                     # Automation scripts
├── src\
│   ├── plugins\                 # Plugin system
│   └── pipeline\                # Core pipeline
├── tools\                       # Spec management tools
├── pm\                          # Project management
├── openspec\                    # OpenSpec system
└── workstreams\                 # Workstream bundles
\\\

---

**Generated**: 2025-11-18 12:26:48
**Repository**: Complete AI Development Pipeline – Canonical Phase Plan
