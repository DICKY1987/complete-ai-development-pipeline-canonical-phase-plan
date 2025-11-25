# UET Operator Guide
**Version**: 1.0.0

## Running with UET
```powershell
$env:PIPELINE_ENGINE = "uet"
$env:PIPELINE_MAX_WORKERS = "4"
python -m core.cli run-phase phase-01
```

## Monitoring
```powershell
Get-Content .execution/telemetry.jsonl -Wait
```
