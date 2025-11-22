
Short answer: **yes, you *can* let Copilot apply edits without asking you every time in Copilot CLI**, but you have to do it via its **tool-approval system**, not a generic “trust all edits” button.

Below is the distilled version from the GitHub docs + your `copilot_cli_tasks_index.csv`.

---

## 1. In an *ongoing* Copilot CLI session

When Copilot CLI wants to edit files or run a tool, you get a permissions prompt like:

> 1. Yes
> 2. Yes, and approve TOOL for the rest of the running session
> 3. No, and tell Copilot what to do differently

From the docs: choosing option **2** means Copilot can use that tool again “without asking for your permission, for the duration of the currently running session.” ([GitHub Docs][1])

So for *file edits*:

1. The first time Copilot asks to use the `write` tool (or a specific edit action), choose:

   * **“Yes, and approve TOOL for the rest of the running session”**.
2. From that point on, **all edits via that tool happen without further prompts** until you end that CLI session. ([GitHub Docs][1])

You can’t retroactively flip a “global allow” switch for an already-running session, but *the next time* it asks to use a tool, choosing option 2 effectively does what you want for the rest of that session.

---

## 2. Start Copilot CLI with flags that auto-approve edits

From **About GitHub Copilot CLI**, there are three key approval flags: ([GitHub Docs][1])

* `--allow-all-tools`
* `--allow-tool 'write'`
* `--allow-tool 'shell(...)'` / `--deny-tool 'shell(...)'`

### 2.1 “Allow all edits, but *only* edits” (safer)

If you just want Copilot to freely modify files (no per-edit prompts), **but still have to approve shell commands**, use:

```bash
copilot --allow-tool 'write'
```

* `write` = “file modification tools (non-shell)” in Copilot’s terms. ([GitHub Docs][1])
* With this flag, **it can edit files without asking**, but it will *still* prompt when it wants to run shell commands like `rm`, `npm`, `git`, etc.

Example (programmatic mode):

```bash
copilot -p "Refactor this repo to use environment variables for config" --allow-tool 'write'
```

### 2.2 “Allow literally everything” (max power, max risk)

If you truly want **no prompts at all** for tools (edits *and* shell commands), you can use:

```bash
copilot --allow-all-tools
```

Per the docs:

> `--allow-all-tools` allows Copilot to use **any tool** without asking for your approval. ([GitHub Docs][1])

Example:

```bash
copilot -p "Run tests and fix failing ones" --allow-all-tools
```

This is what most blog posts use when they’re running Copilot in “headless” / automated mode. ([The GitHub Blog][2])

> ⚠️ **Huge warning**: with `--allow-all-tools`, Copilot can run any shell command you can, including destructive ones like `rm -rf` or `git push -f`. GitHub explicitly flags this as a security risk and recommends sandboxing (VM, container, or dedicated box). ([GitHub Docs][1])

### 2.3 “Mostly allow everything, but block the scary stuff”

You can combine flags to create a “soft sandbox”:

```bash
copilot \
  --allow-all-tools \
  --deny-tool 'shell(rm)' \
  --deny-tool 'shell(git push)'
```

That gives you **no prompts except** when Copilot tries to use `rm` or `git push` (those are blocked outright). ([GitHub Docs][1])

---

## 3. Making this align with your task index file

In your `copilot_cli_tasks_index.csv` you already have:

```text
key:  copilot.permissions.view.cli.env.v1.ph6
cmd:  copilot help permissions
desc: Show permissions and allow/deny settings.
```

That’s exactly how you get the **built-in help** for these flags in your environment.

From the docs, `copilot help permissions` will show the same tool-approval flags (`--allow-all-tools`, `--allow-tool`, `--deny-tool`) and how they map to the permission system. ([GitHub Docs][3])

So for your “session template” or task pipeline, you can slot in:

```bash
# View current permissions docs
copilot help permissions

# Start a “no edit prompts” session
copilot --allow-tool 'write'
# or:
copilot --allow-all-tools --deny-tool 'shell(rm)' --deny-tool 'shell(git push)'
```

---

## 4. Trusted directories vs approvals (different layers)

Two separate mechanisms:

1. **Trusted directories**

   * On session start, Copilot asks if you “trust this folder.”
   * You can persist that by editing `trusted_folders` in `config.json` (under `~/.copilot` or the config path shown by `copilot help config`). ([GitHub Docs][1])

2. **Tool approvals (edits, shell, MCP, etc.)**

   * Controlled per-session by:

     * interactive prompt options (Yes once / Yes for rest of session), and
     * CLI flags: `--allow-all-tools`, `--allow-tool`, `--deny-tool`. ([GitHub Docs][1])

Trusted folders stop the **“Do you trust this directory?”** prompt; the **flags** stop the **“Can I run this tool?”** prompts.

---

## 5. If you meant Copilot *inside an IDE* (VS Code / JetBrains)

The above is **only** for **GitHub Copilot CLI**.

In VS Code / JetBrains:

* There is **no** equivalent one-click “auto-apply any edit this session” setting.
* You still have to:

  * accept inline suggestions,
  * run code actions,
  * or apply edits from Copilot Chat manually.

If your goal is “zero-touch edits,” the officially supported way is to **drive changes through Copilot CLI** with `--allow-tool 'write'` or `--allow-all-tools`, ideally in a sandboxed clone of your repo.

---

### TL;DR for your use case

* **Current ongoing session**:
  Next time Copilot asks to use `write`, pick **“Yes, and approve TOOL for the rest of the running session.”** That will auto-approve edits for that session.

* **New sessions** (recommended, more explicit):

  * Only edits auto-approved:

    ```bash
    copilot --allow-tool 'write'
    ```
  * Absolutely everything auto-approved (dangerous):

    ```bash
    copilot --allow-all-tools
    ```


[1]: https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli "About GitHub Copilot CLI - GitHub Docs"
[2]: https://github.blog/ai-and-ml/github-copilot-cli-101-how-to-use-github-copilot-from-the-command-line/?utm_source=chatgpt.com "How to use GitHub Copilot from the command line"
[3]: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli?utm_source=chatgpt.com "Using GitHub Copilot CLI"
