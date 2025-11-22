
### 1. Task-enqueue script (pushes tasks to Aider)

The patch in the log shows a new PowerShell script that lives at:

> `scripts/SubmitTask.ps1`

Key behavior from that patch:

* It builds a **single JSON task line** and enqueues it to `.tasks/inbox`:

  ```powershell
  $task = [ordered]@{ tool = $Tool }
  if ($Script)  { $task.script = $Script }
  if ($Args)    { $task.args   = $Args }
  if ($Cwd)     { $task.cwd    = $Cwd }
  if ($Tool -eq 'aider' -and $Model) { $task.model = $Model }
  ```
* It then writes that JSON as a line into a `.jsonl` file under `.tasks/inbox`:

  ```powershell
  $json = ($task | ConvertTo-Json -Compress)
  Add-Content -Path $outPath -Value $json
  Write-Host "Enqueued task to: $outPath" -ForegroundColor Green
  ```

This is the **front door** that “pushes” work to Aider: you call `scripts/SubmitTask.ps1 -Tool aider ...`, and it drops an Aider task into the queue.

### 2. Worker that actually runs Aider

In the same log, Codex also added the orchestration docs describing the worker that consumes those tasks:

* `QueueWorker.ps1`:

  > “Processes JSONL tasks from `.tasks/` and executes tools.”

And in `OPERATIONS.md`, Aider is explicitly one of the supported tools:

```text
- aider: { "tool":"aider", "args":["-m","/add README.md","-m","/commit ."] }
```

So the flow is:

1. **Submit/enqueue** an Aider task:

   ```powershell
   pwsh -File scripts/SubmitTask.ps1 -Tool aider -Args @('-m','/add README.md')
   ```
2. **QueueWorker.ps1** picks up the JSONL task from `.tasks/inbox` and, using `Config/ToolRegistry.psd1`, executes `aider` with the configured flags (`--yes`, `--auto-commits`, etc.).

### 3. Extra aider-specific orchestration bits

There’s also adapter work for Aider in `AIM_adapters/AIM_aider.ps1` to make non-interactive Aider calls more robust (this shows the broader orchestration layer around Aider):

---

**Bottom line:**
Yes, the orchestration that pushes tasks to Aider is present. The main piece you’re looking for is:

* **`scripts/SubmitTask.ps1`** → builds and enqueues JSONL tasks, including `tool = 'aider'`, into `.tasks/inbox`.
  paired with
* **`scripts/QueueWorker.ps1`** → reads the queue and actually calls `aider` according to `Config/ToolRegistry.psd1`.
