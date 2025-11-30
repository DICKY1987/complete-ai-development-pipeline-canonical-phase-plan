---
doc_id: DOC-GUIDE-BACKGROUND-TASK-1241
---


You treat each **work-stream** as a **task definition**, give it its own **Git work-tree + branch**, then have a small **orchestrator CLI** that:

1. Reads the phase plan
2. Figures out which work-streams can run in parallel
3. Creates/attaches Git work-trees for them
4. Starts background workers (Aider/Codex/etc.) against those work-trees
5. Watches status / logs / timeouts and pushes branches + PRs

I’ll show you a concrete pattern you can drop into your pipeline.

---

## 1. Represent the phase plan as runnable tasks

You want the **phase plan** to be “machine runnable” – i.e. each work-stream is a task with:

* An ID
* Phase + dependencies
* Tool to run (aider/codex/etc.)
* Repo + working dir
* Prompt/instruction file
* Timeout, concurrency group

Example (YAML) you could call `PHASE_PLAN.yaml`:

```yaml
phases:
  - id: PH-07
    name: "Path abstraction + hardcoded path index"
    max_parallel_workstreams: 3

    workstreams:
      - id: WS-07A
        name: "Scan for hardcoded paths"
        repo: "C:\Repos\pipeline-main"
        base_branch: "main"
        tool: "aider"
        prompt_file: "PHASE_DEV_DOCS\AIDER_WS07A.txt"
        timeout_minutes: 60
        depends_on: []          # can start immediately

      - id: WS-07B
        name: "Create PATH_INDEX_SPEC.md"
        repo: "C:\Repos\pipeline-main"
        base_branch: "main"
        tool: "codex"
        prompt_file: "PHASE_DEV_DOCS\CODEX_WS07B.txt"
        timeout_minutes: 90
        depends_on: ["WS-07A"]

      - id: WS-07C
        name: "Refactor scripts to use index"
        repo: "C:\Repos\pipeline-main"
        base_branch: "main"
        tool: "aider"
        prompt_file: "PHASE_DEV_DOCS\AIDER_WS07C.txt"
        timeout_minutes: 120
        depends_on: ["WS-07A", "WS-07B"]
```

Your **orchestrator** just needs to:

* Load this file
* Build a dependency graph
* At any time, find “runnable” workstreams where all `depends_on` are finished.

---

## 2. Map each work-stream to a Git work-tree

For parallel workstreams, the trick is: **each WS gets its own branch + work-tree** so they don’t stomp on each other.

Pattern (from a “main” repo at `C:\Repos\pipeline-main`):

```powershell
function New-WorktreeForWorkstream {
    param(
        [string]$RepoPath,
        [string]$BaseBranch,
        [string]$PhaseId,      # e.g. PH-07
        [string]$WorkstreamId  # e.g. WS-07A
    )

    Set-Location $RepoPath

    $branchName = "ws/$PhaseId/$WorkstreamId"
    $worktreeDir = Join-Path $RepoPath "..\worktrees\$PhaseId-$WorkstreamId"

    # Ensure base branch is up to date
    git fetch origin
    git checkout $BaseBranch
    git pull origin $BaseBranch

    # Create worktree + branch if not exists
    if (-not (git branch --list $branchName)) {
        git worktree add $worktreeDir -b $branchName "origin/$BaseBranch"
    } else {
        git worktree add $worktreeDir $branchName
    }

    return @{
        Branch = $branchName
        Path   = (Resolve-Path $worktreeDir).Path
    }
}
```

This gives you:

* A clean directory per workstream: `...\worktrees\PH-07-WS-07A`
* A dedicated branch: `ws/PH-07/WS-07A`
* Perfect isolation for parallel refactors / AI tools.

You can also record this mapping in a small JSON ledger:

```json
{
  "task_id": "PH-07::WS-07A",
  "branch": "ws/PH-07/WS-07A",
  "worktree_path": "C:\\Repos\\worktrees\\PH-07-WS-07A"
}
```

---

## 3. Launch background workers in parallel (orchestrator)

At this point, “background tasks” = **worker processes** that run Aider/Codex/etc. headless in their own work-tree.

A simple PowerShell pattern:

```powershell
function Start-WorkstreamTask {
    param(
        [string]$TaskId,           # "PH-07::WS-07A"
        [string]$Tool,             # "aider", "codex"
        [string]$WorktreePath,
        [string]$PromptFile,
        [int]$TimeoutMinutes = 60
    )

    $logDir = "C:\AI_PIPELINE\.runs\$TaskId"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null

    $logFile = Join-Path $logDir "stdout-stderr.log"
    $metaFile = Join-Path $logDir "task.json"

    # Write simple metadata
    @{
        task_id       = $TaskId
        tool          = $Tool
        worktree_path = $WorktreePath
        prompt_file   = $PromptFile
        started_at    = (Get-Date).ToString("o")
        timeout_min   = $TimeoutMinutes
        status        = "running"
    } | ConvertTo-Json | Set-Content $metaFile

    $scriptBlock = {
        param($Tool, $WorktreePath, $PromptFile, $LogFile)

        Set-Location $WorktreePath

        switch ($Tool) {
            "aider" {
                aider --message-file $PromptFile *>> $LogFile
            }
            "codex" {
                codex --message-file $PromptFile *>> $LogFile
            }
            default {
                "Unknown tool $Tool" | Out-File -Append $LogFile
                exit 1
            }
        }
    }

    # Background job with timeout + log capture
    $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $Tool, $WorktreePath, $PromptFile, $logFile

    return @{
        TaskId = $TaskId
        Job    = $job
        LogDir = $logDir
    }
}
```

Then a **phase executor** that respects parallelism:

```powershell
function Invoke-PhasePlan {
    param(
        [string]$PlanFile,
        [string]$PhaseId
    )

    $plan = Get-Content $PlanFile | ConvertFrom-Yaml
    $phase = $plan.phases | Where-Object id -eq $PhaseId

    $maxParallel = $phase.max_parallel_workstreams
    $running = @{}
    $completed = @{}
    $failed = @{}

    while ($true) {
        # 1) Find runnable workstreams (deps satisfied)
        $runnable = @()
        foreach ($ws in $phase.workstreams) {
            if ($completed.ContainsKey($ws.id) -or $failed.ContainsKey($ws.id)) { continue }

            $deps = $ws.depends_on
            if ($deps -and ($deps | Where-Object { -not $completed.ContainsKey($_) })) {
                continue # deps not done
            }

            if ($running.ContainsKey($ws.id)) { continue } # already running
            $runnable += $ws
        }

        # 2) Start new tasks up to maxParallel
        foreach ($ws in $runnable) {
            if ($running.Count -ge $maxParallel) { break }

            $wt = New-WorktreeForWorkstream -RepoPath $ws.repo -BaseBranch $ws.base_branch -PhaseId $PhaseId -WorkstreamId $ws.id
            $taskId = "$PhaseId::$($ws.id)"

            $run = Start-WorkstreamTask -TaskId $taskId -Tool $ws.tool -WorktreePath $wt.Path -PromptFile $ws.prompt_file -TimeoutMinutes $ws.timeout_minutes

            $running[$ws.id] = $run
            Write-Host "Started $taskId in background"
        }

        # 3) Check for finished jobs
        foreach ($wsId in @($running.Keys)) {
            $job = $running[$wsId].Job
            if ($job.State -in "Completed", "Failed", "Stopped") {
                $taskId = "$PhaseId::$wsId"
                $taskDir = $running[$wsId].LogDir

                if ($job.Error.Count -eq 0 -and $job.State -eq "Completed") {
                    $completed[$wsId] = $true
                    Write-Host "✅ Completed $taskId"
                } else {
                    $failed[$wsId] = $true
                    Write-Host "❌ Failed $taskId – see logs at $taskDir"
                }

                Remove-Job $job
                $running.Remove($wsId)
            }
        }

        # 4) Exit condition: all done
        if ($running.Count -eq 0 -and
            ($phase.workstreams.id | ForEach-Object { $_ } | Where-Object { -not ($completed.ContainsKey($_) -or $failed.ContainsKey($_)) }).Count -eq 0) {
            break
        }

        Start-Sleep -Seconds 5
    }

    Write-Host "Phase $PhaseId complete. Success: $($completed.Count), Failed: $($failed.Count)"
}
```

That’s a full “parallel work-streams + background tasks” loop:

* Obeys `depends_on`
* Obeys per-phase `max_parallel_workstreams`
* Each WS runs in its own worktree
* All stdout/stderr captured to `.runs/<task-id>/…`

You can wire this into your GUI/“mission control” later.

---

## 4. Tie it into GitHub (branches → PRs)

Once a workstream is marked complete, you can:

1. Run tests / linters in the worktree
2. Commit changes
3. Push branch
4. Create PR

Example post-task hook:

```powershell
function Complete-WorkstreamBranch {
    param(
        [string]$WorktreePath,
        [string]$BranchName,
        [string]$TaskId
    )

    Set-Location $WorktreePath

    git status
    if ((git status --porcelain).Trim()) {
        git add .
        git commit -m "[$TaskId] Automated refactor for $BranchName"
        git push -u origin $BranchName

        # Optional: create PR automatically
        gh pr create `
            --base main `
            --head $BranchName `
            --title "[$TaskId] Automated refactor" `
            --body "Generated by phase plan executor for $TaskId."
    } else {
        Write-Host "No changes in $TaskId – nothing to commit."
    }
}
```

You’d call this in the “job finished successfully” section of `Invoke-PhasePlan`.

---

## 5. How this answers your question directly

> **“How do I automate the use of background tasks with parallel work-streams and GitHub work-trees when executing a phase plan?”**

**Answer in one line:**

* Encode your phase plan as **workstream tasks with dependencies**,
* For each runnable workstream, **create a dedicated Git work-tree/branch**,
* Launch an **AI tool worker** (Aider/Codex/etc.) as a **background job** in that work-tree, with logs + timeout,
* Limit concurrency per phase, and
* On completion, **commit/push and open PRs** from each branch.

If you’d like, I can next:

* Adapt the example functions to **your exact paths + repos**, or
* Generate a **single `PhaseExecutor.ps1`** script you can drop into `ALL_AI` and call like:

```powershell
Invoke-PhasePlan -PlanFile "PHASE_PLAN.yaml" -PhaseId "PH-07"
```
