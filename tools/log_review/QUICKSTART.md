# Quick-Start Guide: Claude Code + Aider Headless Integration

**For**: Orchestrating Aider from Claude Code to execute plans  
**Status**: Ready to use immediately  
**Time**: 5-30 minutes depending on pattern

---

## ⚡ 5-Minute Setup

### Option 1: PowerShell One-Liner (Windows - Fastest)

```powershell
$proj = 'C:\Users\yourname\your-repo'
cd $proj

# Validate
if (-not (Test-Path .git)) { Write-Error "Not a git repo"; exit 1 }

# Define messages
$steps = @(
    '/add README.md'
    '/code Implement .migration scaffolding'
    '/diff'
    '/lint'
    '/commit Aider: migrate: scaffold .migration'
)

# Build command
$cmd = 'aider --yes --auto-commits'
foreach ($s in $steps) {
    $escaped = $s -replace '"', '\"'
    $cmd += " -m `"$escaped`""
}

# Execute
Invoke-Expression $cmd
exit $LASTEXITCODE
```

### Option 2: Bash One-Liner (Unix/Linux/macOS)

```bash
cd ~/your-repo
aider --yes --auto-commits \
  -m "/add README.md" \
  -m "/code Implement .migration scaffolding" \
  -m "/diff" \
  -m "/lint" \
  -m "/commit Aider: migrate: scaffold .migration"
```

### Option 3: Python Script (Most Portable)

```python
#!/usr/bin/env python3
from pathlib import Path
import subprocess

repo = Path(".")
messages = [
    "/add README.md",
    "/code Implement .migration scaffolding",
    "/diff",
    "/lint",
    "/commit Aider: migrate: scaffold .migration"
]

cmd = ["aider", "--yes", "--auto-commits"]
for msg in messages:
    cmd.extend(["-m", msg])

result = subprocess.run(cmd, cwd=repo)
exit(result.returncode)
```

---

## 📋 Three Patterns Explained

### Pattern A: Claude Code ↔ Aider (With Feedback Loop)

Best for: Real-time feedback, asking Claude Code to iterate on Aider output

```powershell
# In Claude Code chat:
"Use the shell MCP tool to run this on my C:\repos\my-project:

$proj = 'C:\repos\my-project'
cd $proj
$msgs = @('/add README.md', '/code Implement feature', '/diff', '/commit')
$cmd = 'aider --yes --auto-commits'
foreach ($m in $msgs) { $cmd += " -m \`"$($m -replace '\"', '\\\"')\`"" }
Invoke-Expression $cmd

Report the exit code and what changes were made."
```

**Advantage**: Claude sees output, can request changes, loop back

---

### Pattern B: Standalone Script (Most Flexible)

Best for: General automation, CI/CD, full control with if/else logic

```bash
#!/bin/bash
set -e

REPO_DIR="$1"
cd "$REPO_DIR"

# Validate
[ -d .git ] || { echo "Not a git repo"; exit 1; }

# Execute
aider --yes --auto-commits \
  -m "/add README.md" \
  -m "/code Implement feature" \
  -m "/diff" \
  -m "/lint" \
  -m "/commit Feature: implement"

echo "✓ Complete"
```

**Advantage**: Scriptable, versionable, works everywhere

---

### Pattern C: Pre-Generated Command Files (Safest for Large Plans)

Best for: Pre-planned migrations, team review, version control

Create `session_fnd_001_scaffold.aider`:
```
/add README.md
/code Create .migration directory with:
- .migration/mapping.yaml (valid empty YAML)
- .migration/transaction.log with format header
- .migration/validation-report.md with section headers
No other files modified.
/diff
/lint
/commit Aider: migrate: scaffold .migration
```

Execute:
```bash
aider --yes --auto-commits /load session_fnd_001_scaffold.aider
```

**Advantage**: Reviewable, auditable, version-controlled

---

## 🛡️ Error Handling

### Pre-Flight Check

```powershell
function Test-Ready {
    $checks = @(
        (Test-Path .git, "Git repo"),
        ((Get-Command aider -EA SilentlyContinue), "Aider installed"),
        ($env:ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY set")
    )
    
    foreach ($check, $desc in $checks) {
        if ($check) { Write-Host "✓ $desc" -ForegroundColor Green }
        else { Write-Host "✗ $desc" -ForegroundColor Red; return $false }
    }
    return $true
}

Test-Ready
```

### Rollback on Failure

```bash
#!/bin/bash
BEFORE=$(git rev-parse HEAD)
aider --yes --auto-commits "$@"

if [ $? -ne 0 ]; then
    echo "Rolling back to $BEFORE..."
    git reset --hard "$BEFORE"
    exit 1
fi
```

---

## 💡 Using with Claude Code

### Method 1: Shell MCP (Real-Time Feedback)

In Claude Code chat:

```
Use the shell MCP tool (don't ask) to run this PowerShell on my repo:

$steps = @('/add main.py', '/code Implement feature X', '/diff', '/commit')
$cmd = 'aider --yes --auto-commits'
foreach ($s in $steps) { $cmd += " -m `"$($s -replace '"', '\"')`"" }
Set-Location C:\repos\my-project
Invoke-Expression $cmd

Report what Aider did.
```

Claude Code will:
1. Execute the command
2. Show you the output
3. Allow you to request changes

---

## ✅ Verification

After running Aider:

```bash
# Check what was changed
git log --oneline | head -5

# See the diff
git show

# Review changes
git diff HEAD~1
```

---

## 📚 Next Steps

1. **Choose your pattern** (A, B, or C above)
2. **Test on a branch**: `git checkout -b test/aider-automation`
3. **Run one small issue** to validate
4. **Generate full command files** for your plan
5. **Execute sequentially**
6. **Review commits** in git log
7. **Merge to main** if happy
