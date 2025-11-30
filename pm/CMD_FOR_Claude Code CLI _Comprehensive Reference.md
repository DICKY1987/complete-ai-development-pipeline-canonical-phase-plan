---
doc_id: DOC-PM-CMD-FOR-CLAUDE-CODE-CLI-COMPREHENSIVE-020
---

Claude Code CLI – Comprehensive Reference
Overview

Claude Code CLI is a powerful command‑line interface designed to give developers hands‑on control over the Claude language model. It supports interactive coding sessions, one‑shot prompts, multi‑agent orchestration, slash commands, checkpointing, hooks and plugins. This reference targets intermediate–to‑advanced engineers who will use the CLI daily for tasks like writing and refactoring code, running tests, managing projects and automating workflows.

This document synthesizes the official documentation and open‑source repositories to provide a single, in‑depth reference. It covers every major command, flag and feature, explains when each tool is optimal, and includes realistic workflows you can copy‑paste. Sections are organized so you can quickly jump to the topic you need.

Table of Contents

Getting Started

Core CLI Reference

Global flags and configuration

Using the --agents flag

System prompts

Permission modes

Interactive Mode

Slash Commands

Checkpointing

Hooks Reference

Plugins & Extensibility

Advanced & Undocumented Usage

Common End‑to‑End Workflows

Appendix

Getting Started
Installation

Claude Code is distributed as a Node package. A recent Node LTS release (18 or later) is required. The official repository provides several installation methods. The following methods are common:

Homebrew (macOS/Linux) — add the tap and install:

brew install anthropic/claude/claude


NPM — install globally via npm or yarn:

npm install -g @anthropicai/claude-code
# or
yarn global add @anthropicai/claude-code


Windows — download the ZIP from the releases page and follow the included instructions.

Alternative installation methods (e.g., curl script) are described in the README of the anthropics/claude-code repository, which also notes that Node 18+ is required
raw.githubusercontent.com
. Once installed, verify by running claude --version.

Basic invocation

From a terminal inside a project directory, launch the interactive shell by simply typing:

claude


By default, this opens a REPL where you can chat with the model, run slash commands and execute code. To send a single prompt and print the response without entering interactive mode, use the -p (print) flag:

claude -p "Summarize this library and suggest improvements."


When combined with flags, you can customize the session (e.g., set a system prompt, choose a model, add directories to context). The remainder of this document details all available options and features.

Core CLI Reference

Claude Code CLI exposes a small number of top‑level commands plus many configuration flags. The two primary invocation patterns are:

Interactive session: claude (with optional flags) starts an interactive REPL.

Print single response: claude -p <prompt> prints a one‑shot answer and exits.

The CLI accepts numerous flags that control context, agents, prompting and permissions. This section explains each flag, when it is useful and example workflows.

Global flags and configuration
Flag	Description	Optimal when…	Example
--add-dir <path>	Adds a directory to the conversation context. Useful for including project files or code for analysis. Claude will scan the directory and create memory items.	You want the model to understand and reference your codebase or docs without manual uploads.	claude --add-dir src/ --add-dir docs/
--agents <json>	Defines sub‑agents with their own system prompt, description, tools and model. The JSON accepts objects keyed by agent name. Each agent may specify prompt, description, tools, model and optionally output transformations
code.claude.com
.	You have tasks that benefit from specialized agents (e.g., separate code analysis and test running). Useful in combination with slash commands and MCP.	claude --agents '{"tester":{"description":"Runs tests","prompt":"Write and run tests...","tools":["bash"]}}'
--allowed-tools <list>	Restricts which tools the assistant may invoke (e.g., bash, browser, custom tools).	You are working in a sensitive environment and wish to limit capabilities (e.g., disable internet or shell access).	claude --allowed-tools "bash,files"
--disallowed-tools <list>	Disallows specified tools.	Similar to --allowed-tools, but easier when you want to block only a few tools.	claude --disallowed-tools browser
--system-prompt <string>	Sets a custom system prompt that will prepend instructions to every message
code.claude.com
.	You need to steer the model’s behavior or enforce style/structure across the session.	claude --system-prompt "You are a strict unit test generator."
--system-prompt-file <file>	Reads system prompt from a file.	When the prompt is long or stored in project docs.	claude --system-prompt-file .claude/system.md
--append-system-prompt <string>	Appends additional text to the default system prompt instead of replacing it
code.claude.com
.	You want to layer additional instructions without discarding the built‑in prompt.	claude --append-system-prompt "Always reply in JSON."
--output-format <json|md|text>	Controls the format of printed responses (JSON, Markdown or plain text).	When integrating with scripts or wanting raw Markdown.	claude -p "list items" --output-format=json
--input-format <text|markdown>	Specifies the input interpretation format.	Useful when your prompt includes code blocks or Markdown that should be preserved.	claude -p "## Heading\nExplain…" --input-format=markdown
--include-partial-messages	Includes partial assistant messages in streaming output.	When you need incremental streaming (e.g., for long responses).	claude -p "generate large code" --include-partial-messages
--verbose	Enables verbose logging, printing debug information such as tool invocation decisions.	Troubleshooting complex sessions or developing hooks/plugins.	claude --verbose
--max-turns <n>	Maximum number of turns the assistant may take before the session ends.	Limiting cost or preventing infinite loops.	claude -p "explain recursion" --max-turns 3
--model <name>	Selects the underlying LLM (e.g., claude-3-opus, claude-3-sonnet).	Different models trade cost for capability; choose appropriate one.	claude -p "summarize" --model=claude-3-opus
--permission-mode <mode>	Controls how the assistant obtains permission for actions. Modes include interactive (default), auto (auto‑approve), deny (always deny) and dry-run.	Fine‑tuning how tool invocations are authorized. Use auto in CI, dry-run for previewing actions without execution.	claude --permission-mode=auto --allowed-tools=bash
--permission-prompt-tool <tool>	Selects the tool used for permission prompts (e.g., terminal vs gui).	Customizing the UX for permission confirmations.	claude --permission-prompt-tool=terminal
--resume	Resumes the most recent session (restores conversation history and code state).	Continue work after closing the REPL or after a crash.	claude --resume
--continue	Continues a conversation using the same session ID (works with print mode).	Append to a previous one‑shot conversation.	claude -p "Add more details" --continue <id>
--dangerously-skip-permissions	Skips the permission system entirely. This is dangerous and should be used only in trusted environments.	Automation scripts that trust the assistant fully. Use with caution.	claude --dangerously-skip-permissions
Using the --agents flag

The --agents flag allows you to define sub‑agents which can run concurrently or specialize on tasks. The argument is a JSON object keyed by agent names. Each agent definition can specify:

description: human description of the agent’s role.

prompt: system prompt for that agent (similar to --system-prompt).

tools: allowed tools (e.g., bash, browser).

model: model to use for this agent.

output: how to post‑process the agent’s response (e.g., json or custom transformation).

Example: define a coder and tester agent. The coder writes code using bash and the tester runs tests via bash. They communicate through the main conversation.

claude --agents '{
  "coder": {
    "description": "Writes implementation code based on specs.",
    "prompt": "You are a coding agent.  Write clear, tested code.",
    "tools": ["bash"],
    "model": "claude-3-sonnet"
  },
  "tester": {
    "description": "Runs unit tests and reports failures.",
    "prompt": "You are a testing agent.  Run the test suite and report issues.",
    "tools": ["bash"]
  }
}' -p "Implement a stack and verify it."


This command launches multiple agents within a single session. It is optimal when you have clearly separated responsibilities (coding vs testing, analysis vs synthesis). Complex tasks can be decomposed into specialized agents that collaborate, leading to more reliable outputs
code.claude.com
.

System prompts

System prompts prime the model’s behavior at the beginning of the session. Use --system-prompt or --system-prompt-file to provide a new system message; use --append-system-prompt to add to the default prompt instead of replacing it
code.claude.com
. System prompts are ideal for:

Enforcing code style guides (e.g., require docstrings or comment formats).

Limiting the assistant’s scope (e.g., only answer within the Python standard library).

Providing domain context (e.g., “you are an expert on Kubernetes”).

For long prompts stored in files, use --system-prompt-file. If you only need to add a small requirement (like returning JSON), --append-system-prompt is simpler.

Permission modes

The permission system ensures that potentially dangerous tool invocations (such as running shell commands) require user approval. Use --permission-mode to change how approvals are handled:

interactive (default) — the assistant asks for confirmation each time before using a tool.

auto — auto‑approves all tool uses. Use in trusted automation or non‑interactive environments.

deny — denies all tool invocations. Useful for exploring suggestions without executing any actions.

dry-run — simulates tool invocations but does not execute them. Helps preview what will happen.

Combine permission mode with --allowed-tools or --disallowed-tools for fine‑grained security. To bypass the system entirely (not recommended except in internal scripts), --dangerously-skip-permissions removes all checks.

Interactive Mode

Running claude with no prompt enters an interactive REPL. You can chat with the model, run code, issue slash commands and manage conversation history. Key features include:

Keyboard shortcuts and editing

Ctrl+C — cancel the current assistant request.

Ctrl+D — exit the session.

Ctrl+L — clear the screen.

Ctrl+O — toggle verbose output (show hidden context and system messages)
code.claude.com
.

Ctrl+R — reverse search through your previous inputs (similar to bash history).

Ctrl+Enter (multiline) — insert a newline within your message; press Enter on an empty line to send.

Esc (in Vim mode) — switch between insert and normal mode; gg, G, :q and other Vim motions work.

Use these shortcuts to navigate and edit messages quickly. The REPL supports long prompts, code blocks and Markdown. When a message is sent, the assistant may request permissions for tool actions; respond “yes” or “no” as appropriate.

Running shell commands

Prefix a line with ! to execute a shell command in your project’s working directory. The command and its output will be added to the conversation. This is equivalent to using the bash tool. For example:

!ls -la src


This runs ls and returns the directory listing, which you can reference in your next message. You can run any CLI tool available in your environment; the assistant will ask for permission before executing it.

Background tasks

Some shell commands take a long time to run (e.g., npm install, pytest). You can run them asynchronously by pressing Ctrl+B or using the /bashes slash command. This creates a background task identified by an ID. You can continue interacting with the assistant while the task runs, and later check its status or output
code.claude.com
. This workflow is ideal for package installations, test runs and long builds. Typical usage:

Press Ctrl+B after typing a shell command (or append --background if supported by the slash command implementation).

Continue your conversation; the model may respond to other questions.

Once the task finishes, the assistant prints the results or you can retrieve them with /bashes.

Rich inputs and memory

You can paste images or large files directly into the REPL. Claude will store them in session memory and refer to them when reasoning. Use the # prefix to view or clear memory items. For example, #memory lists saved items. This feature is useful for code reviews, diagrams or design documents.

Permission prompts in interactive mode

When the assistant needs to run a tool, it will ask: “Do you want to run this bash command?” You can reply y/yes, n/no, or ask for more details. To automatically approve all requests in interactive mode, restart the session with --permission-mode=auto or respond all yes to permit subsequent tool uses.

Slash Commands

Slash commands extend the REPL with user‑defined and built‑in commands. They are typed at the beginning of a line and start with /. The official docs categorize them as built‑in commands, plugin commands, and MCP commands (multi‑party collaboration). This section summarizes the most important built‑ins and explains how to create your own.

Built‑in slash commands

Claude Code includes numerous built‑in slash commands covering context management, configuration, debugging and workflow automation. Below is a non‑exhaustive list of the most common commands and their purpose:

Command	Purpose	Optimal usage & example
/add-dir <path>	Adds a directory to the conversation context. Equivalent to the --add-dir flag but usable mid‑session
code.claude.com
.	After starting an interactive session, run /add-dir src to load your source code so Claude can answer questions about it.
/agents	Displays currently configured agents. Useful when using --agents or multi-agent workflows.	Run /agents to see each agent’s description and status.
/bashes	Lists background bash tasks, their status and outputs
code.claude.com
.	After running a long command with Ctrl+B, type /bashes to check if it finished.
/bug	Creates a bug report template to file an issue with the Claude team.	Use when encountering reproducible errors or unexpected behavior.
/clear	Clears conversation history (context and messages).	Start fresh without restarting the CLI.
/compact [instructions]	Compacts the conversation by summarizing old messages using the LLM. Accepts optional instructions (e.g., retain certain details)
code.claude.com
.	When the conversation becomes long and you need to free up token budget.
/config	Shows or edits configuration settings (e.g., default model, permission mode).	Inspect current configuration or override defaults temporarily.
/context	Lists the current memory/context items (files, images) and allows removal.	Clear or inspect loaded directories or files.
/cost	Displays estimated token usage and cost for the session.	Monitor spend during long interactions.
/doctor	Runs diagnostics on your environment and configuration.	Use if the CLI is misbehaving or to ensure dependencies are installed.
/exit	Exits the session.	Equivalent to Ctrl+D.
/export	Exports the conversation history and memory to a file or clipboard.	Save transcripts for documentation or follow‑up.
/help	Shows help for slash commands and general usage.	Use to discover commands or see syntax.
/hooks	Lists configured hooks and their triggers.	Useful when developing custom hooks.
/init	Initializes a .claude directory in the current project and optionally installs templates or plugins.	Run when starting a new project or enabling plugin features.
/login / /logout	Authenticates your Claude account.	Required for using remote models or certain features.
/memory	Views and manages memory items (similar to #memory).	Inspect file and image memory.
/model [name]	Gets or sets the current model.	Quickly switch between models (e.g., claude-3-haiku vs opus).
/output-style [style]	Sets the style of assistant responses (e.g., concise, detailed).	Fine‑tune output verbosity without editing system prompts.
/permissions	Shows the current permission settings and prompts to adjust them.	Confirm or modify the permission mode mid‑session.
/pr_comments	Generates pull‑request‑style comments for code changes.	Useful during code review workflows.
/privacy-settings	Adjusts data retention and telemetry settings.	Meet compliance requirements.
/review	Performs an AI‑assisted code review on the current context.	After loading a code directory, run /review to get feedback.
/sandbox	Opens a temporary sandbox environment for experiments.	Running untrusted code or exploring new ideas.
/rewind	Reverts to the previous checkpoint (see Checkpointing).	Undo an unwanted model action or code edit.
/status / /statusline	Displays current status (model, agents, memory items) and shows a status bar.	Monitor session state.
/terminal-setup	Configures your terminal for improved integration (e.g., customizing prompts).	When first configuring your environment.
/todos	Lists outstanding TODO items extracted from your code.	Manage tasks directly from the CLI.
/usage	Shows usage statistics such as token counts and cost.	Monitor resource consumption.
/vim	Toggles Vim mode editing (enable/disable).	Switch between standard and Vim keybindings.

These built‑ins are integrated into the CLI and available without plugins. Many accept sub‑commands or flags; type /help for detailed usage. Slash commands are executed by the assistant, so they count against your token budget.

Creating custom slash commands

Custom slash commands are defined by placing Markdown files in .claude/commands/ (project‑specific) or ~/.claude/commands (user‑specific). The filename becomes the command name (e.g., deploy.md becomes /deploy). Files support optional [frontmatter] with fields such as:

allowed-tools: comma‑separated list of tools allowed during execution.

argument-hint: hint text shown in auto‑completion.

description: short description displayed in /help and completion lists.

model: override the default model.

disable-model-invocation: if true, skip calling the LLM and just run the command’s bash script.

Inside the Markdown body, you can reference arguments as $ARGUMENTS, $1, $2, etc. You can call tools by prefixing with ! (e.g., !npm test); such commands will obey the allowed tools list and require permissions
code.claude.com
. File references use @filename to insert file contents or @[start:end] to slice lines. Use 思考: ... to instruct the assistant to think before executing the command.

For plugin commands, names are namespaced as /plugin-name:command-name, ensuring separation between different plugins
code.claude.com
. Slash commands support auto‑discovery and appear in auto‑completion menus. When building custom commands, keep them modular: avoid long prompts, prefer generating small tasks, and run heavy work inside separate tools or agents.

Slash commands vs. skills

Slash commands are executable scripts integrated into the CLI, while agent skills are Markdown assets loaded into memory that influence the assistant’s behavior. A built‑in comparison table notes that slash commands are better for procedural tasks and external tool invocations, whereas skills excel at knowledge/instruction encoding
code.claude.com
. When deciding between them, consider whether your functionality needs to call tools or simply provide guidance.

Checkpointing

Claude Code automatically creates checkpoints before editing files. Checkpoints capture the state of files and the conversation at that moment. You can revert to an earlier state by typing double Esc or using the /rewind command. Important facts:

Automatic creation: Every time the assistant edits a file via the files or bash tools, a checkpoint is saved, including the previous version of the file and the conversation state.

Persistence: Checkpoints persist across sessions. If you exit and later resume the session (claude --resume), the checkpoints remain available
code.claude.com
.

Recovery: Use /rewind to view and restore from a previous checkpoint. Choose whether to revert just the code, just the conversation or both.

Limitations: Checkpoints do not track external shell commands or modifications made outside the CLI (e.g., manual edits in your editor). They are not a substitute for version control; use Git for long‑term history
code.claude.com
.

Optimal usage: Use checkpoints when iterating on a feature or exploring alternatives. For example, ask Claude to refactor a function, run tests via slash commands, and if the change fails, rewind to the previous checkpoint and try a different approach. Checkpoints provide short‑term recovery within the context of the conversation.

Hooks Reference

Hooks provide a way to intercept and respond to events inside the CLI. They are configured via settings.json files in either ~/.claude/ (user‑level) or .claude/ (project‑level). A hook definition consists of an event, a matcher and an action. Event types include:

PreToolUse — fired before a tool runs. The hook can modify or block the tool invocation. Use matchers to target specific tools (e.g., only bash commands). Example: a Python script that prevents running grep commands
raw.githubusercontent.com
.

PermissionRequest — fired when the assistant requests permission to use a tool. You can implement an automated policy (e.g., auto‑approve safe commands, deny dangerous ones).

PostToolUse — runs after a tool finishes. Useful for logging or post‑processing outputs.

Notification — triggered by slash commands like /notify; allows integrations with external systems (e.g., sending Slack notifications).

UserPromptSubmit — fired when the user sends a prompt; can modify or reject inputs.

Stop — triggered when the assistant finishes, enabling custom summarization or logging
code.claude.com
.

SubagentStop — similar to Stop but specific to sub‑agents.

PreCompact — before conversation compaction occurs.

SessionStart / SessionEnd — triggered at the beginning and end of a session; environment variables like CLAUDE_SESSION_ID and CLAUDE_PROJECT_DIR are available
code.claude.com
.

Hooks can be implemented in two ways:

Script hooks: Provide a path to an executable script (Python, Bash, etc.) in settings.json under the relevant event. The script receives a JSON payload describing the context and returns a JSON response that can modify or cancel the action
code.claude.com
. Use the CLAUDE_PROJECT_DIR environment variable to access project files.

Prompt‑based hooks: Provide a natural language prompt (string) instead of a script. The LLM is asked to decide what to do and returns a JSON instruction. For example, a Stop prompt‑based hook might instruct Claude to generate a summary when the session ends
code.claude.com
.

Hook configurations can be combined. Use matchers to restrict hooks to specific tools or agents. For example:

{
  "hooks": {
    "PreToolUse": {
      "match": { "tool": "bash", "pattern": "rm -rf" },
      "script": "./prevent_rm.sh"
    },
    "SessionStart": {
      "prompt": "When a session starts, remind the user to add a README file if missing."
    }
  }
}


Hooks are powerful for enforcing policies, automating tasks and integrating with external systems. Avoid writing expensive or long‑running scripts; they block the CLI until they finish.

Plugins & Extensibility

Claude Code supports plugins that bundle commands, agents, skills, hooks and even entire MCP (multi‑party collaboration) servers. A plugin is a directory with a plugin.json manifest containing metadata and lists of components
code.claude.com
:

{
  "name": "feature-dev",
  "version": "1.0.0",
  "description": "Workflow for starting new features",
  "commands": ["commands/feature-dev.md"],
  "agents": ["agents/planner.md"],
  "skills": ["skills/refactor"],
  "hooks": "hooks.json",
  "mcpServers": ["servers/issue-manager.json"]
}

Plugin components

Commands — Markdown files placed in commands/. They define slash commands using the same syntax as project commands. Use namespacing (plugin-name:command-name) to avoid collisions.

Agents — Markdown files in agents/. Agents define system prompts and tool configurations for multi‑agent workflows. They can be invoked via the --agents flag or used by slash commands.

Skills — Directories under skills/ containing a SKILL.md file and optional supporting files. Skills are loaded into the assistant’s memory to provide domain knowledge or style guidance.

Hooks — A hooks.json file describing hook events and scripts/prompts to execute. Equivalent to project settings but packaged within the plugin
code.claude.com
.

MCP servers — JSON files under servers/ that describe remote servers for multi‑party collaboration. They expose slash commands that interact with external systems (e.g., GitHub PR review). MCP commands are namespaced with double underscores (/mcp__server__command)
code.claude.com
.

Plugins must follow a standard directory structure and have version numbers. They can be installed manually by copying into the ~/.claude/plugins directory or by using /init to scaffold them. Use claude --debug to see loaded plugins and troubleshoot issues
code.claude.com
.

Official plugin examples

The open‑source repositories include several example plugins demonstrating common workflows:

agent‑sdk‑dev — provides the /new-sdk-app command that scaffolds a new Agent SDK application. It guides you through collecting requirements, planning, generating code and running tests
raw.githubusercontent.com
.

commit‑commands — offers /commit and /commit-push-pr commands that stage changes, commit with an AI‑generated message and optionally push and create a pull request
raw.githubusercontent.com
.

code‑review — includes /code-review for reviewing diffs and generating PR comments.

feature‑dev — provides a workflow for creating new features, including planning tasks and verifying with sub‑agents.

These plugins illustrate how to combine commands, agents and hooks to automate complex workflows. Installing them gives you additional slash commands and capabilities out of the box.

Advanced & Undocumented Usage

While most features are documented, the open‑source repositories reveal a few advanced behaviors you may find useful:

Local mode and offline workflows

The CLI now supports local mode where commands can run without contacting remote servers. When enabled via configuration (e.g., local: true in settings), the assistant runs purely with local models and tools. This is useful for offline development or when working with proprietary data. The changelog notes that the local mode was modernized in early 2025
raw.githubusercontent.com
.

Automatic GitHub label creation and context accuracy safeguards

The ccpm repository indicates that initializing a project may automatically create GitHub labels and that context creation commands enforce self‑verification checkpoints
raw.githubusercontent.com
. When using /context:create or /re-init from the ccpm plugin, follow the prompts to review and confirm context generation; this ensures the assistant does not misinterpret your repository.

Multi‑party collaboration (MCP) commands

Plugins can register MCP servers that expose commands for collaboration. MCP commands are namespaced with double underscores (e.g., /mcp__github__open_issue). The docs caution that these commands may have stricter permission requirements and may be disabled in some environments. Use /mcp to view available servers and /permissions to configure access
code.claude.com
.

Customizing cost estimation

The cost display (/cost or /usage) uses built‑in rates for each model. You can override these via configuration if you have negotiated pricing. Add a pricing object to your settings specifying cost per token and call. This allows accurate budgeting.

Common End‑to‑End Workflows

This section demonstrates realistic workflows combining commands, slash commands, checkpoints and plugins.

Interactive coding with checkpoints and slash commands

Start a session and load your project:

claude --add-dir src/ --model=claude-3-sonnet


Explore files and ask questions: Ask the assistant to explain a function or suggest improvements.

Refactor using slash commands: Use /review to perform an AI code review. Run !pytest to verify that tests still pass. If you run the tests in the background (Ctrl+B), continue discussing design while they run. Use /bashes to check status.

Checkpoint and rewind: If the assistant makes an undesired change, use /rewind to revert to the previous checkpoint. Try another approach.

Commit changes: Use the commit‑commands plugin’s /commit or /commit-push-pr to stage and commit modifications with an AI‑generated message. Optionally push and open a PR.

This workflow showcases how interactive mode, slash commands and checkpointing work together to create an iterative development loop.

Setting up a test‑driven development (TDD) workflow with hooks and plugins

Install the feature‑dev and commit‑commands plugins (copy into ~/.claude/plugins or use /init).

Create a hook in .claude/settings.json that auto‑runs tests after every code edit. For example:

{
  "hooks": {
    "PostToolUse": {
      "match": { "tool": "files" },
      "script": "./.claude/scripts/run_tests.sh"
    }
  }
}


run_tests.sh might call pytest and notify the assistant if tests fail.

Start interactive session: claude --add-dir src/ --permission-mode=auto.

Generate tests first: ask the assistant to create unit tests for the feature. Use /todos to track tasks.

Implement the feature: edit files via the assistant or run commands yourself. After each change, the hook triggers pytest automatically and reports results. Use checkpoints to revert if necessary.

Commit: once tests pass and the feature is complete, run /commit-push-pr to push the branch and create a pull request.

Building a new Agent SDK application

Load the agent‑sdk‑dev plugin and run /new-sdk-app. The assistant will ask for details about your project (name, language, dependencies)
raw.githubusercontent.com
.

Answer the questions. The command will generate a project scaffold, including code templates and configuration files.

Run the verification agents (provided by the plugin). They test that the new app can compile and run tests. The CLI uses multiple sub‑agents for planning, code generation and testing.

Iterate: modify the generated code, run tests, and commit when satisfied.

Context creation and project management with ccpm plugin

Initialize the project using /init and selecting the ccpm template. This sets up context and testing commands.

Generate context: run /context:create to ask Claude to summarize the repository and create context files. Review and confirm the generated context (self‑verification checkpoints ensure accuracy
raw.githubusercontent.com
).

Prime testing: run /testing:prime to prepare a test environment. Then use /testing:run to run tests whenever needed.

Use /code-review and /pr_comments for AI‑assisted code review and generating PR comments. Combine with Git hooks to enforce quality.

Appendix
Commands by category
Category	Commands
Context management	--add-dir, /add-dir, /context, /clear, /memory, /compact
Model & settings	--model, /model, --system-prompt, --append-system-prompt, /config, /output-style, /privacy-settings, /permissions, /usage
Agents & multi‑agent	--agents, /agents, /mcp
Shell & background tasks	!command, Ctrl+B, /bashes, /sandbox
Checkpointing	/rewind, --resume, --continue
Hooks & plugins	/hooks, /init, /help
Workflow automation	/review, /pr_comments, /todos, /code-review (plugin), /commit, /commit-push-pr
Slash commands by context
Scenario	Useful commands
Starting a new project	/init, --add-dir, /hooks, /context
Running tests	!pytest, Ctrl+B, /bashes, /testing:run (ccpm)
Code review	/review, /code-review (plugin), /pr_comments
Managing context & memory	/context, /memory, /compact, /clear
Debugging environment	/doctor, /config, /status, /usage

This reference is based on the official Claude Code CLI documentation and the related open‑source repositories. Citations refer to sections in those sources for further reading.