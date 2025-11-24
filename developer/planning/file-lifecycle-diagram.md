# File lifecycle diagram

This diagram mirrors the file lifecycle states defined in `core/ui_models.py`
and summarizes the typical journey a tracked file takes through the pipeline.

```text
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│DISCOVERED  │→→│CLASSIFIED  │→→│   INTAKE   │→→│   ROUTED   │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
                                                        │
                                                        ▼
                                                ┌────────────┐
                                                │PROCESSING  │
                                                └────────────┘
                                                        │
                                                        ▼
                                                ┌────────────┐
                                                │ IN FLIGHT  │
                                                └────────────┘
                                                   │      │
   (validation failure / manual hold) ┌────────────┘      └────────────┐
                                      ▼                               ▼
                                ┌────────────┐                 ┌────────────┐
                                │QUARANTINED │                 │AWAITING    │
                                └────────────┘                 │ REVIEW     │
                                                                └────────────┘
                                                                       │
                                                                       ▼
                                                               ┌────────────┐
                                                               │AWAITING    │
                                                               │ COMMIT     │
                                                               └────────────┘
                                                                       │
                                                                       ▼
                                                               ┌────────────┐
                                                               │COMMITTED   │
                                                               └────────────┘
```

**Legend**

- Double arrows (`→→`) denote automated state transitions that happen immediately
  after the previous state finishes.
- Vertical single arrows indicate synchronous processing steps that emit timing
  metrics.
- The side branch to `QUARANTINED` captures files that need manual attention;
  once cleared, they can be routed back into the `IN FLIGHT` cadence.
