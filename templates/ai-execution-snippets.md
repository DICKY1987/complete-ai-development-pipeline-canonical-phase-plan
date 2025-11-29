# AI execution snippets (ready-to-run)

Short, repeatable snippets for Copilot/Codex sessions. PowerShell-first; keep paths literal/quoted.

## Safe merge playbook (pre-flight + merge + gates)
```powershell
$feature = "feature/safe-merge-patterns-complete"
$otherBranches = @("chore/add-untracked-files")
$tag = "pre-multi-merge-{0}" -f (Get-Date -Format "yyyyMMdd-HHmmss")

# Pre-flight: review before staging
git status

# Stage & commit current branch work (comment out commit if nothing new)
git add -A
git commit -m "feat: consolidate safe merge patterns and reorganize documentation"
git push origin $feature

# Sync main and snapshot
git checkout main
git pull --ff-only origin main
git tag -a $tag -m "Safety snapshot before merges"

# Merge supporting branches first
foreach ($b in $otherBranches) { git merge $b --no-ff -m "Merge $b" }

# Merge primary branch
git merge $feature --no-ff -m "Merge $feature"

# Gates/tests
python scripts/validate_acs_conformance.py
python scripts/paths_index_cli.py gate --db refactor_paths.db
pytest tests/ -q

# Push main
git push origin main
```

## Windows file/DB check (no `file` binary needed)
```powershell
$db = "refactor_paths.db"
Get-Item -LiteralPath $db | Format-List FullName, Length, LastWriteTime

# Quick SQLite schema check (requires python)
@"
import sqlite3
conn = sqlite3.connect(r"$db")
cur = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for name, sql in cur.fetchall():
    print(name, ":", sql)
"@ | python -
```

## Path-safe command runner (quotes + rg fallback)
```powershell
$target = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline - Canonical Phase Plan"

if (Get-Command rg -ErrorAction SilentlyContinue) {
    rg --files --iglob "*" -g "*" -0 -p $target
} else {
    Get-ChildItem -LiteralPath $target -Recurse -File -Force | ForEach-Object { $_.FullName }
}
```
