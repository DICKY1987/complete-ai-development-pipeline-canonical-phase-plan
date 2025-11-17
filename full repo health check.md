You want a **You want a **full repo health check** before doing any syncing. Totally right move. Let’s set this up as:

1. A **manual checklist** (Git commands) that truly looks at *everything*.
2. A **Codex CLI “audit spec”** you can paste so Codex does the inspection and summarizes it for you.

---

## 1. One-time prep

From PowerShell, go to the repo you care about:

```powershell
cd "C:\path\to\your\repo"
```

Sanity check:

```bash
git status -sb
git remote -v
```

Make sure this really is the repo you care about, and you see the right GitHub remote (usually `origin`).

---

## 2. Comprehensive manual audit checklist

### A. Check working tree & ignored stuff

**Goal:** see *all* dirty state: staged, unstaged, untracked, ignored, stashes.

```bash
# 1) Short working tree summary
git status -sb

# 2) Show ignored files as well
git status --ignored

# 3) Any stashed work?
git stash list
```

Look for:

* Anything under **Changes not staged for commit** → edits you haven’t staged
* **Untracked files** → new files never added
* `stash@{n}: ...` → hidden changes you forgot about

If this is noisy, you can later decide: commit, delete, or add to `.gitignore`.

---

### B. Fetch everything from GitHub (don’t change local yet)

**Goal:** your local repo knows the *latest* remote branches & PR commits.

```bash
git fetch --all --prune
```

* `--all` = all remotes (usually just `origin`)
* `--prune` = clean up refs for remote branches that got deleted on GitHub

This doesn’t modify your working files; it only updates remote metadata.

---

### C. Local branch inventory with ahead/behind status

**Goal:** see all local branches, what they track, and whether they’re ahead/behind or “gone”.

```bash
git branch -vv
```

You’ll see lines like:

```text
* main   1234abcd [origin/main: ahead 3, behind 1] message...
  feature-x 5678ef01 [origin/feature-x] message...
  old-branch 9abcdeff [origin/old-branch: gone] message...
  local-only 76543210 message...
```

Pay attention to:

* `ahead N` → local has commits **not pushed** to GitHub
* `behind N` → GitHub has commits **not pulled** locally
* `gone` → remote branch was deleted; your local branch is now orphaned
* No `[...]` at all → local branch doesn’t track any remote

---

### D. Remote branch / PR view

**Goal:** see what exists on GitHub side.

```bash
# All remote branches
git branch -r
```

If you have GitHub CLI (`gh`) installed (recommended):

```bash
# Which repo and URL is this?
gh repo view

# List all open PRs
gh pr list --state open

# Quick summary of current branch in PRs
gh pr status
```

This tells you:

* Which branches have open PRs
* Which PRs are merged/closed
* If current branch is associated with a PR

If you don’t have `gh`, you can use the GitHub web UI, but `gh` makes it scriptable for Codex.

---

### E. Find unpushed commits per branch

**Goal:** detect branches where local history is ahead of remote (even if you forgot).

You can see a lot just from `git branch -vv` (anything with `ahead N`), but for detail:

For each branch you care about:

```bash
# Example for main
git log --oneline origin/main..main

# Example for feature-x
git log --oneline origin/feature-x..feature-x
```

If this prints commits, those are **local-only** commits not on GitHub.

---

### F. Find commits on GitHub that aren’t local

**Goal:** see what you’re missing from GitHub.

For each branch:

```bash
# Commits on origin/main not in local main
git log --oneline main..origin/main
```

If this prints commits, those exist **only in GitHub** right now.

---

### G. Look for old/orphaned local branches

**Goal:** find junk or forgotten work.

```bash
# Show local branches with last commit date
git for-each-ref --format="%(committerdate:short) %(refname:short)" refs/heads | sort
```

Look for:

* Very old branches (months ago)
* Branches with `[origin/...: gone]` in `git branch -vv`
* Branches with no remote tracking at all

These are candidates to either clean up or archive.

---

### H. Global timeline picture

**Goal:** see how branches relate.

```bash
git log --oneline --graph --decorate --all --max-count=50
```

This gives you a quick sense of divergence/merges across branches.

---

### I. Hidden stuff: reflog & stashes

Already looked at stashes; reflog is more “safety net”:

```bash
git reflog --date=short --relative-date --max-count=20
```

This can reveal resets, rebases, checkouts you forgot you did.

---

## 3. How to use this audit: classification

Once you have the data, you want to classify each **local branch** into buckets:

* **Clean & in sync**

  * `git status` clean on that branch
  * `git branch -vv` shows `[origin/branch]` with no ahead/behind

* **Has unpushed commits**

  * `ahead N` or `git log origin/branch..branch` shows commits
  * You’ll want to push these (after verifying)

* **Behind remote**

  * `behind N` or `git log branch..origin/branch` shows commits
  * You’ll want to `git pull --rebase` or merge

* **Diverged**

  * Both ahead and behind → you changed both sides
  * Needs a merge or rebase decision

* **Orphaned local**

  * `[origin/branch: gone]` or no tracking remote
  * Decide: delete, rename, or reattach to a different remote

* **Has outstanding PR**

  * Check via `gh pr status` or `gh pr list`
  * Decide: merge PR, close PR, or update branch

---

## 4. “Do everything for me” – Codex CLI audit spec

Here’s a **ready prompt** you can paste into Codex from the repo root. Codex will just run the commands and give you a structured summary.

> You are my Git repository auditor. Do **not** modify anything yet; only inspect and report.
> I want a **complete picture** of this repo’s state: branches, PRs, uncommitted work, stashes, and differences between local and GitHub.
>
> 1. Confirm we’re in a Git repo and show the current branch and remote:
>
>    * Run: `pwd` (or `Get-Location` on PowerShell)
>    * Run: `git status -sb`
>    * Run: `git remote -v`
> 2. Fetch the latest from all remotes without changing my working tree:
>
>    * Run: `git fetch --all --prune`
> 3. Inspect working tree & stashes:
>
>    * Run: `git status -sb`
>    * Run: `git status --ignored`
>    * Run: `git stash list`
>      Summarize:
>    * Staged changes
>    * Unstaged changes
>    * Untracked files
>    * Ignored files that look suspicious (e.g., compiled code or logs in the wrong place)
>    * Number of stashes and brief descriptions.
> 4. Inventory all local and remote branches:
>
>    * Run: `git branch -vv`
>    * Run: `git branch -r`
>      For each local branch, report:
>    * Tracking remote (or “no upstream”)
>    * Whether it is ahead/behind/diverged from its upstream
>    * If upstream is `[gone]`
>    * Last commit date and short message.
> 5. For each local branch that has a tracking remote, check unpushed/unpulled commits:
>    For each `refs/heads/<branch>` that tracks `origin/<branch>`:
>
>    * Run: `git log --oneline origin/<branch>..<branch> | wc -l` (or equivalent)
>    * Run: `git log --oneline <branch>..origin/<branch> | wc -l`
>      Summarize per branch:
>    * `unpushed_commits` count
>    * `unpulled_commits` count
> 6. Identify orphaned or stale branches:
>
>    * Use `git branch -vv` and `git for-each-ref --format="%(committerdate:short) %(refname:short)" refs/heads | sort`
>    * Flag branches that:
>
>      * Have `[gone]` upstream
>      * Have no upstream
>      * Have no commits in the last 60–90 days
>        Summarize them as candidates for cleanup or review.
> 7. If GitHub CLI (`gh`) is available, inspect PR status:
>
>    * Run: `gh repo view`
>    * Run: `gh pr list --state open`
>    * Run: `gh pr status`
>      Map any local branches to open PRs and note whether they are up to date with their remote.
> 8. Show a compact commit graph overview:
>
>    * Run: `git log --oneline --graph --decorate --all --max-count=50`
>      Include this in the report so I can see branch relationships.
> 9. Produce a final **structured report** (Markdown or JSON) with:
>
>    * **Working tree summary:** dirty/clean, list of key untracked paths, stashes.
>    * **Branch table:** for each local branch → upstream, ahead/behind counts, last commit date, associated PR (if any), and a recommended action (e.g., “sync & keep”, “merge & delete”, “review unpushed work”, “safe to delete after confirmation”).
>    * **PR overview:** list of open PRs, their branches, and whether the local branch is ahead/behind.
>    * **Warnings:** anything risky (diverged branches, unpushed commits on branches with open PRs, very old branches, suspicious ignored files).
>    * **Next-step plan:** a short list of recommended actions in priority order to get this repo fully clean and synchronized.

You can tweak the wording, but that’s the idea: Codex becomes your **Git auditor**, not your “let’s immediately rewrite history” agent.

---

## 5. After the audit: syncing safely

Once you have the report:

* For each **active branch** you care about:

  * Clean up / commit working tree.
  * `git pull --rebase origin <branch>` (resolve conflicts).
  * `git push origin <branch>`.
* For stale or orphaned branches, create a small “cleanup” plan (Codex can help again).

If you want, next message we can take Codex’s actual output from this audit and turn it into a concrete per-branch sync plan.
** before doing any syncing. Totally right move. Let’s set this up as:

1. A **manual checklist** (Git commands) that truly looks at *everything*.
2. A **Codex CLI “audit spec”** you can paste so Codex does the inspection and summarizes it for you.

---

## 1. One-time prep

From PowerShell, go to the repo you care about:

```powershell
cd "C:\path\to\your\repo"
```

Sanity check:

```bash
git status -sb
git remote -v
```

Make sure this really is the repo you care about, and you see the right GitHub remote (usually `origin`).

---

## 2. Comprehensive manual audit checklist

### A. Check working tree & ignored stuff

**Goal:** see *all* dirty state: staged, unstaged, untracked, ignored, stashes.

```bash
# 1) Short working tree summary
git status -sb

# 2) Show ignored files as well
git status --ignored

# 3) Any stashed work?
git stash list
```

Look for:

* Anything under **Changes not staged for commit** → edits you haven’t staged
* **Untracked files** → new files never added
* `stash@{n}: ...` → hidden changes you forgot about

If this is noisy, you can later decide: commit, delete, or add to `.gitignore`.

---

### B. Fetch everything from GitHub (don’t change local yet)

**Goal:** your local repo knows the *latest* remote branches & PR commits.

```bash
git fetch --all --prune
```

* `--all` = all remotes (usually just `origin`)
* `--prune` = clean up refs for remote branches that got deleted on GitHub

This doesn’t modify your working files; it only updates remote metadata.

---

### C. Local branch inventory with ahead/behind status

**Goal:** see all local branches, what they track, and whether they’re ahead/behind or “gone”.

```bash
git branch -vv
```

You’ll see lines like:

```text
* main   1234abcd [origin/main: ahead 3, behind 1] message...
  feature-x 5678ef01 [origin/feature-x] message...
  old-branch 9abcdeff [origin/old-branch: gone] message...
  local-only 76543210 message...
```

Pay attention to:

* `ahead N` → local has commits **not pushed** to GitHub
* `behind N` → GitHub has commits **not pulled** locally
* `gone` → remote branch was deleted; your local branch is now orphaned
* No `[...]` at all → local branch doesn’t track any remote

---

### D. Remote branch / PR view

**Goal:** see what exists on GitHub side.

```bash
# All remote branches
git branch -r
```

If you have GitHub CLI (`gh`) installed (recommended):

```bash
# Which repo and URL is this?
gh repo view

# List all open PRs
gh pr list --state open

# Quick summary of current branch in PRs
gh pr status
```

This tells you:

* Which branches have open PRs
* Which PRs are merged/closed
* If current branch is associated with a PR

If you don’t have `gh`, you can use the GitHub web UI, but `gh` makes it scriptable for Codex.

---

### E. Find unpushed commits per branch

**Goal:** detect branches where local history is ahead of remote (even if you forgot).

You can see a lot just from `git branch -vv` (anything with `ahead N`), but for detail:

For each branch you care about:

```bash
# Example for main
git log --oneline origin/main..main

# Example for feature-x
git log --oneline origin/feature-x..feature-x
```

If this prints commits, those are **local-only** commits not on GitHub.

---

### F. Find commits on GitHub that aren’t local

**Goal:** see what you’re missing from GitHub.

For each branch:

```bash
# Commits on origin/main not in local main
git log --oneline main..origin/main
```

If this prints commits, those exist **only in GitHub** right now.

---

### G. Look for old/orphaned local branches

**Goal:** find junk or forgotten work.

```bash
# Show local branches with last commit date
git for-each-ref --format="%(committerdate:short) %(refname:short)" refs/heads | sort
```

Look for:

* Very old branches (months ago)
* Branches with `[origin/...: gone]` in `git branch -vv`
* Branches with no remote tracking at all

These are candidates to either clean up or archive.

---

### H. Global timeline picture

**Goal:** see how branches relate.

```bash
git log --oneline --graph --decorate --all --max-count=50
```

This gives you a quick sense of divergence/merges across branches.

---

### I. Hidden stuff: reflog & stashes

Already looked at stashes; reflog is more “safety net”:

```bash
git reflog --date=short --relative-date --max-count=20
```

This can reveal resets, rebases, checkouts you forgot you did.

---

## 3. How to use this audit: classification

Once you have the data, you want to classify each **local branch** into buckets:

* **Clean & in sync**

  * `git status` clean on that branch
  * `git branch -vv` shows `[origin/branch]` with no ahead/behind

* **Has unpushed commits**

  * `ahead N` or `git log origin/branch..branch` shows commits
  * You’ll want to push these (after verifying)

* **Behind remote**

  * `behind N` or `git log branch..origin/branch` shows commits
  * You’ll want to `git pull --rebase` or merge

* **Diverged**

  * Both ahead and behind → you changed both sides
  * Needs a merge or rebase decision

* **Orphaned local**

  * `[origin/branch: gone]` or no tracking remote
  * Decide: delete, rename, or reattach to a different remote

* **Has outstanding PR**

  * Check via `gh pr status` or `gh pr list`
  * Decide: merge PR, close PR, or update branch

---

## 4. “Do everything for me” – Codex CLI audit spec

Here’s a **ready prompt** you can paste into Codex from the repo root. Codex will just run the commands and give you a structured summary.

> You are my Git repository auditor. Do **not** modify anything yet; only inspect and report.
> I want a **complete picture** of this repo’s state: branches, PRs, uncommitted work, stashes, and differences between local and GitHub.
>
> 1. Confirm we’re in a Git repo and show the current branch and remote:
>
>    * Run: `pwd` (or `Get-Location` on PowerShell)
>    * Run: `git status -sb`
>    * Run: `git remote -v`
> 2. Fetch the latest from all remotes without changing my working tree:
>
>    * Run: `git fetch --all --prune`
> 3. Inspect working tree & stashes:
>
>    * Run: `git status -sb`
>    * Run: `git status --ignored`
>    * Run: `git stash list`
>      Summarize:
>    * Staged changes
>    * Unstaged changes
>    * Untracked files
>    * Ignored files that look suspicious (e.g., compiled code or logs in the wrong place)
>    * Number of stashes and brief descriptions.
> 4. Inventory all local and remote branches:
>
>    * Run: `git branch -vv`
>    * Run: `git branch -r`
>      For each local branch, report:
>    * Tracking remote (or “no upstream”)
>    * Whether it is ahead/behind/diverged from its upstream
>    * If upstream is `[gone]`
>    * Last commit date and short message.
> 5. For each local branch that has a tracking remote, check unpushed/unpulled commits:
>    For each `refs/heads/<branch>` that tracks `origin/<branch>`:
>
>    * Run: `git log --oneline origin/<branch>..<branch> | wc -l` (or equivalent)
>    * Run: `git log --oneline <branch>..origin/<branch> | wc -l`
>      Summarize per branch:
>    * `unpushed_commits` count
>    * `unpulled_commits` count
> 6. Identify orphaned or stale branches:
>
>    * Use `git branch -vv` and `git for-each-ref --format="%(committerdate:short) %(refname:short)" refs/heads | sort`
>    * Flag branches that:
>
>      * Have `[gone]` upstream
>      * Have no upstream
>      * Have no commits in the last 60–90 days
>        Summarize them as candidates for cleanup or review.
> 7. If GitHub CLI (`gh`) is available, inspect PR status:
>
>    * Run: `gh repo view`
>    * Run: `gh pr list --state open`
>    * Run: `gh pr status`
>      Map any local branches to open PRs and note whether they are up to date with their remote.
> 8. Show a compact commit graph overview:
>
>    * Run: `git log --oneline --graph --decorate --all --max-count=50`
>      Include this in the report so I can see branch relationships.
> 9. Produce a final **structured report** (Markdown or JSON) with:
>
>    * **Working tree summary:** dirty/clean, list of key untracked paths, stashes.
>    * **Branch table:** for each local branch → upstream, ahead/behind counts, last commit date, associated PR (if any), and a recommended action (e.g., “sync & keep”, “merge & delete”, “review unpushed work”, “safe to delete after confirmation”).
>    * **PR overview:** list of open PRs, their branches, and whether the local branch is ahead/behind.
>    * **Warnings:** anything risky (diverged branches, unpushed commits on branches with open PRs, very old branches, suspicious ignored files).
>    * **Next-step plan:** a short list of recommended actions in priority order to get this repo fully clean and synchronized.

You can tweak the wording, but that’s the idea: Codex becomes your **Git auditor**, not your “let’s immediately rewrite history” agent.

---

## 5. After the audit: syncing safely

Once you have the report:

* For each **active branch** you care about:

  * Clean up / commit working tree.
  * `git pull --rebase origin <branch>` (resolve conflicts).
  * `git push origin <branch>`.
* For stale or orphaned branches, create a small “cleanup” plan (Codex can help again).

If you want, next message we can take Codex’s actual output from this audit and turn it into a concrete per-branch sync plan.
