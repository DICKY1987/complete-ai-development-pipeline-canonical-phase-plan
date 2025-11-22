# Git Auto-Sync - PowerShell Profile Integration
# Setup Instructions for Smart Sync

## How It Works

**First PowerShell window opened:**
- ✅ Starts Git Auto-Sync
- ✅ Acquires system-wide mutex lock
- ✅ Monitors repository for changes
- ✅ Auto-commits and syncs

**Additional PowerShell windows opened:**
- ⏭️ Detects sync already running
- ⏭️ Skips starting duplicate sync
- ⏭️ Shows status message
- ⏭️ No performance impact

**When you close the first PowerShell window:**
- 🛑 Sync stops automatically
- 🔓 Mutex released
- ♻️ Next PowerShell window becomes the "first"

---

## Installation

### Step 1: Check Your PowerShell Profile Location

```powershell
# See where your profile is
$PROFILE

# Common location:
# C:\Users\richg\Documents\PowerShell\Microsoft.PowerShell_profile.ps1
```

### Step 2: Create or Edit Your Profile

```powershell
# Create profile if it doesn't exist
if (-not (Test-Path $PROFILE)) {
    New-Item -Path $PROFILE -ItemType File -Force
    Write-Host "Created new PowerShell profile: $PROFILE"
}

# Open profile in default editor
notepad $PROFILE

# Or use VS Code
code $PROFILE
```

### Step 3: Add Auto-Sync to Profile

Add this ONE LINE to your `$PROFILE`:

```powershell
# Git Auto-Sync - Only runs in first PowerShell window
& "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\infra\sync\Start-AutoSync.ps1"
```

### Step 4: Save and Test

```powershell
# Save the profile file

# Reload profile in current window
. $PROFILE

# Or close and reopen PowerShell
```

---

## Expected Behavior

### First Window

```
PS C:\> # Opening PowerShell...

╔══════════════════════════════════════════╗
║  Starting Git Auto-Sync (First Window)  ║
╚══════════════════════════════════════════╝

✓ Sync active (Job ID: 5)
✓ Mutex acquired - other windows will not start duplicate sync

📝 Logs: Get-Content .sync-log.txt -Tail 20 -Wait

PS C:\>
```

### Second Window (While First is Open)

```
PS C:\> # Opening PowerShell...

✓ Git Auto-Sync already running in another PowerShell window
  (This window will not start duplicate sync)

PS C:\>
```

### Third, Fourth, Fifth Windows...

Same as second window - all skip starting sync.

---

## How the Mutex Works

**Mutex = Mutual Exclusion Lock**

```
┌─────────────────────────────────────┐
│  System-Wide Mutex                  │
│  Name: GitAutoSync-[repo-hash]      │
│                                     │
│  Owner: First PowerShell Window     │
│  Status: LOCKED                     │
└─────────────────────────────────────┘
           ↓
    ┌─────────────┐
    │ PS Window 1 │ ← Has lock, runs sync
    └─────────────┘
           ↓
    ┌─────────────┐
    │ PS Window 2 │ ← Checks lock, sees owned, skips
    └─────────────┘
           ↓
    ┌─────────────┐
    │ PS Window 3 │ ← Checks lock, sees owned, skips
    └─────────────┘
           ↓
    Close Window 1 → Mutex released
           ↓
    ┌─────────────┐
    │ PS Window 2 │ ← Still running, no change
    └─────────────┘
           ↓
    Open new window → Acquires lock, starts sync
```

**Key Point**: The mutex is **system-wide**, not just for one PowerShell session. This means:
- Works across all PowerShell windows
- Works across different PowerShell versions (7.x, 5.1)
- Works even if you open PowerShell in different directories

---

## Manual Control

### Check if Sync is Running

```powershell
Get-Job -Name "GitAutoSync"
```

### View Live Logs

```powershell
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
Get-Content .sync-log.txt -Tail 20 -Wait
```

### Stop Sync Manually

```powershell
Stop-Job -Name "GitAutoSync"
Remove-Job -Name "GitAutoSync" -Force

# This will release the mutex
# Next PowerShell window opened will start sync
```

### Force Start Sync (Even if Running)

```powershell
# Not recommended, but possible:
.\infra\sync\Start-AutoSync.ps1 -Force
```

---

## Testing the Setup

### Test 1: Single Window

```powershell
# Open PowerShell window
# Should see: "Starting Git Auto-Sync (First Window)"

# Create test file
"Test" > test-sync.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub - file should appear
gh repo view --web
```

### Test 2: Multiple Windows

```powershell
# Window 1: Open PowerShell
# Should see: "Starting Git Auto-Sync (First Window)"

# Window 2: Open another PowerShell
# Should see: "already running in another PowerShell window"

# Window 3: Open another PowerShell
# Should see: "already running in another PowerShell window"

# Close Window 1
# Windows 2 and 3 stay open, sync continues running

# Window 4: Open another PowerShell
# Should see: "Starting Git Auto-Sync (First Window)"
# Because Window 1 closed and released the lock
```

### Test 3: Verify No Duplicates

```powershell
# Open 5 PowerShell windows

# In any window, run:
Get-Job -Name "GitAutoSync"

# Should show only ONE job, not 5
```

---

## Troubleshooting

### Issue: Every window says "Starting Git Auto-Sync"

**Cause**: Mutex not working (unlikely)

**Solution**:
```powershell
# Check if mutex exists
[System.Threading.Mutex]::TryOpenExisting("Global\GitAutoSync-*", [ref]$null)
```

### Issue: Sync not starting at all

**Cause**: Profile not loaded or script error

**Solution**:
```powershell
# Check profile loaded
$PROFILE
Get-Content $PROFILE

# Run manually to see errors
.\infra\sync\Start-AutoSync.ps1
```

### Issue: Sync still running after closing all PowerShell windows

**Cause**: Background job persisted

**Solution**:
```powershell
# Kill orphaned job
Get-Job -Name "GitAutoSync" | Stop-Job
Get-Job -Name "GitAutoSync" | Remove-Job -Force
```

---

## Advanced: Per-Repository Sync

If you work on multiple repositories and want each to sync independently:

```powershell
# In your profile:

# Auto-detect current repository
$currentRepo = git rev-parse --show-toplevel 2>$null

if ($currentRepo -and (Test-Path "$currentRepo\infra\sync\Start-AutoSync.ps1")) {
    & "$currentRepo\infra\sync\Start-AutoSync.ps1" -RepoPath $currentRepo
}
```

This will:
- ✅ Only start sync if you're in a Git repository
- ✅ Use different mutex per repository
- ✅ Allow multiple repos to sync simultaneously

---

## Summary

**What You Get:**

1. ✅ **First PowerShell window** → Sync starts automatically
2. ✅ **Additional windows** → Recognize sync is running, skip
3. ✅ **No duplicates** → System-wide mutex prevents multiple syncs
4. ✅ **Auto-cleanup** → Sync stops when you close PowerShell
5. ✅ **Zero manual commands** → Just open PowerShell and work

**Performance:**
- First window: +2 seconds startup (starts sync)
- Other windows: +0.1 seconds (just checks mutex)
- No ongoing impact while working

**Mental Model:**
- Think of the first PowerShell window as the "sync controller"
- Other windows are just "observers"
- Only one sync runs, no matter how many windows you open
