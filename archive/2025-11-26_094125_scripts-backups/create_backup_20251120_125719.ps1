# DOC_LINK: DOC-SCRIPT-CREATE-BACKUP-20251120-125719-082
# Lightweight Backup Script
# Timestamp: 20251120_125719
# Backs up only code/config files, excludes node_modules

$source = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\pipeline_plus'
$dest = 'C:\Users\richg\ALL_AI\pipeline_plus_BACKUP_20251120_125719'

Write-Host 'Creating selective backup...' -ForegroundColor Yellow
robocopy $source $dest /E /XD node_modules .git __pycache__ .pytest_cache /NFL /NDL /NJH /NJS /nc /ns /np
Write-Host '✓ Backup complete' -ForegroundColor Green
