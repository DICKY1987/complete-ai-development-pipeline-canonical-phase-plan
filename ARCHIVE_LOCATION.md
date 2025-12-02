# Archive Location Reference
# DOC_LINK: DOC-REFERENCE-ARCHIVE-LOCATION-2025-12-02

## Archive Moved to External Storage

**Date**: 2025-12-02  
**Reason**: Reduce repository size and separate historical artifacts from active codebase

### External Location

```
C:\Users\richg\ALL_AI\Archives\Complete_AI_Development_Pipeline_Archive_2025-12-02\
```

### Contents Moved

1. **archive/** (456 files, ~68 MB)
   - Historical snapshots and deprecated code
   - Migration backups from 2025-11-26 to 2025-12-02
   - Legacy code from pre-migration phases

2. **legacy/** (105 files)
   - Archived within archive/legacy/
   - Pre-UET migration code

### Directory Structure

```
Complete_AI_Development_Pipeline_Archive_2025-12-02/
├── README.md (restoration instructions)
└── archive/
    ├── 2025-11-26_094125_scripts-backups/
    ├── 2025-11-26_094309_old-structure/
    ├── 2025-11-26_developer/
    ├── 2025-11-26_docs/
    ├── 2025-11-26_root_archive/
    ├── 2025-11-26_uet_meta/
    ├── 2025-11-26_uet_root/
    ├── 2025-11-26_uet_specs/
    ├── 2025-11-30_060626_engine-consolidation/
    ├── 2025-12-01_090348_root-core-engine-cleanup/
    ├── 2025-12-01_091928_old-root-folders/
    ├── 2025-12-01_115945_deprecated_folders/
    ├── 2025-12-02_111954_exec017_migration_cleanup/
    ├── 20251201_121347_generated_temp_files/
    └── legacy/ (105 files)
```

### Restoration Instructions

If you need to restore the archive:

```powershell
# Restore entire archive
Copy-Item -Path "C:\Users\richg\ALL_AI\Archives\Complete_AI_Development_Pipeline_Archive_2025-12-02\archive" `
          -Destination ".\archive" `
          -Recurse

# Restore specific subdirectory
Copy-Item -Path "C:\Users\richg\ALL_AI\Archives\Complete_AI_Development_Pipeline_Archive_2025-12-02\archive\legacy" `
          -Destination ".\archive\legacy" `
          -Recurse
```

### Notes

- Archive is excluded from git via `.gitignore`
- Safe to compress external archive after 90 days
- All files are historical/deprecated
- No active code dependencies on archived files

### Impact

**Before**:
- Repository size: ~183 MB
- Active + Historical code mixed

**After**:
- Repository size: ~115 MB
- Clean separation: Active code only
- Historical code: External storage

### Related Files

- `.gitignore` - Updated to exclude archive/ and legacy/
- `reports/UET_FRAMEWORK_REVIEW.md` - Recommendations for further cleanup
