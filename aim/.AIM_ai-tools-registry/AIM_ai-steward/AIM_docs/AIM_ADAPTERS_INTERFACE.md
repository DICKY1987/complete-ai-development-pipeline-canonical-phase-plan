---
doc_id: DOC-AIM-AIM-ADAPTERS-INTERFACE-164
---

Adapter Interface (AIM_)

Purpose
- Normalize CLI tool invocation behind a stable JSON I/O contract.

Input (stdin JSON)
- capability: string (e.g., "code_generation")
- payload: object (tool-agnostic content)
- tool: string (tool id)

Output (stdout JSON)
- success: boolean
- content: object (tool-specific result)
- message: string (human-friendly summary)

Exit Codes
- 0: success
- non-zero: failure (stderr may include tool stderr)

Notes
- Adapters must not modify registry; only perform invocation/translation.
- Keep adapters idempotent for read-like capabilities.

