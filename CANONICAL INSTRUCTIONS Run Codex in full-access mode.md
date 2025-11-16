# CANONICAL INSTRUCTIONS: Run Codex in full-access mode on my Windows dev machine

## Goal
I want Codex CLI to run with:
- Full filesystem access (no workspace-only restriction)
- Network access enabled
- No approval prompts for edits or commands

## Platform assumptions
- OS: Windows 10/11
- Shell: PowerShell (pwsh)
- Codex CLI already installed and on PATH (via `npm install -g @openai/codex` or equivalent).
- My home directory is: C:\Users\richg

## How to launch Codex in full-access mode

1. Open a PowerShell terminal.
2. Change to the directory I want Codex to control (usually my home or a repo root), for example:

   Set-Location "C:\Users\richg"

3. Start Codex with **full disk + network + no prompts** using the official CLI flags:

   codex --sandbox danger-full-access --ask-for-approval never

   - `--sandbox danger-full-access` = full filesystem + network access
   - `--ask-for-approval never` = never ask for confirmation

4. From that point on in the session, you (the AI) may assume:
   - Codex can read/write any files my user account can access.
   - Codex can run commands that modify the local environment (install tools, change config files, etc.).
   - Codex can use `git` to commit and push to my GitHub repos, as long as my Git credentials are already set up.

## Optional: persistent profile (only if you need to edit config.toml)

If you need this behavior to be the default without passing flags, configure `~/.codex/config.toml` like this (pseudo-steps, do not hardcode paths):

- Ensure a config file exists at: %USERPROFILE%\.codex\config.toml
- Set:

  sandbox_mode    = "danger-full-access"
  approval_policy = "never"

Then launching plain `codex` from a PowerShell terminal in my repo should behave the same as:
  codex --sandbox danger-full-access --ask-for-approval never

## Extreme YOLO mode (only in a throwaway VM)

There is a more dangerous flag that disables both sandbox and approvals entirely:

  codex --dangerously-bypass-approvals-and-sandbox

Do NOT use this unless you are explicitly told you are inside a dedicated sandbox VM. Prefer the safer command:

  codex --sandbox danger-full-access --ask-for-approval never

## What NOT to do

- Do NOT invent or rely on custom env vars like CODEX_FS, CODEX_NETWORK, or CODEX_APPROVAL; these are not official.
- Do NOT use flags like --danger-full-access (invalid). Always use the documented flags:
  --sandbox danger-full-access
  --ask-for-approval <mode>
  or --dangerously-bypass-approvals-and-sandbox.
