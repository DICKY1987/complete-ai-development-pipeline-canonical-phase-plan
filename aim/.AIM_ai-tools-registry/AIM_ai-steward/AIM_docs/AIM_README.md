# AIM ai-steward

Thin CLI + registry module orchestrating local AI tools via a validated runtime registry.

- CLI: `AIM_ai-steward.ps1`
- Module: `AIM_modules/AIM_AIToolsRegistry.psm1`
- Runtime registry root: `%USERPROFILE%\.AIM_ai-tools-registry`

Commands
- `status` — show detected tools and paths
- `validate` — validate runtime registry
- `apply` — idempotent apply (placeholder)
- `capability <name> <payload-json-or-path>` — route a capability via adapters

See also
- `AIM_docs/AIM_REGISTRY_FORMAT.md`
- `AIM_docs/AIM_ADAPTERS_INTERFACE.md`

## Quickstart

Run with this repository as the registry root:

1) Validate and list detected tools
- `pwsh -File AIM_ai-steward/AIM_ai-steward.ps1 validate -Json -RegistryRoot $PWD`
- `pwsh -File AIM_ai-steward/AIM_ai-steward.ps1 status -Json -RegistryRoot $PWD`

2) Invoke a capability (routes via coordination rules)
- `pwsh -File AIM_ai-steward/AIM_ai-steward.ps1 capability code_generation '{"prompt":"Say hello"}' -Json -RegistryRoot $PWD`

Notes
- `aider` works best inside a Git repository; initialize with `git init` in your project.
- `jules` requires `jules login` in an interactive shell before using `jules new "..."`.
- `claude` supports non-interactive output via `--print`; availability may be affected by session limits or setup.
- The routing for `code_generation` is defined in `AIM_cross-tool/AIM_coordination-rules.json` (primary → fallback chain).
