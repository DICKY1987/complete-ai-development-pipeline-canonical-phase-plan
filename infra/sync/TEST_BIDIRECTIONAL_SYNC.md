# Test Zero-Touch Sync Bidirectionality

## Test 1: Create File Locally
```powershell
# Create new file
"Test content" > sync-test-create.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub (should appear)
gh repo view --web
```

## Test 2: Edit File Locally
```powershell
# Edit file
"Updated content" >> sync-test-create.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub (should show update)
gh repo view --web
```

## Test 3: Delete File Locally
```powershell
# Delete file
Remove-Item sync-test-create.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub (should be deleted)
gh repo view --web
```

## Test 4: Move File to Folder
```powershell
# Create file and folder
"Content" > move-test.txt
New-Item -Path "test-folder" -ItemType Directory

# Wait 90 seconds for first sync
Start-Sleep -Seconds 90

# Move file
Move-Item move-test.txt test-folder/

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub (should show in test-folder/)
gh repo view --web
```

## Test 5: Create File on GitHub
```powershell
# Go to GitHub web UI
# Click "Add file" → "Create new file"
# Name: remote-test.txt
# Content: "Created on GitHub"
# Commit directly to main

# Wait 60 seconds for pull
Start-Sleep -Seconds 60

# Check local directory
Get-Item remote-test.txt
# Should exist!
```

## Test 6: Rename File Locally
```powershell
# Create file
"Content" > old-name.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Rename
Rename-Item old-name.txt new-name.txt

# Wait 90 seconds
Start-Sleep -Seconds 90

# Check GitHub (should show as renamed)
gh repo view --web
```

## Expected Results

All tests should pass with these outcomes:
- ✅ Local create → GitHub create
- ✅ Local edit → GitHub edit
- ✅ Local delete → GitHub delete
- ✅ Local move → GitHub move
- ✅ Local rename → GitHub rename
- ✅ GitHub create → Local create
- ✅ GitHub edit → Local edit
- ✅ GitHub delete → Local delete

## Timing

- Local → GitHub: ~90 seconds (30s commit + 60s push)
- GitHub → Local: ~60 seconds (next pull cycle)

## Verify Service is Running

```powershell
Get-Service GitAutoSync-* | Format-Table Name, Status
Get-Content .sync-log.txt -Tail 20 -Wait
```
