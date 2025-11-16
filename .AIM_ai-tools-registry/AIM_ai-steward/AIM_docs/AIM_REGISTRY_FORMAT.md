Registry Format (AIM_)

Top-level fields
- tools: object keyed by tool id
- capabilities: optional metadata
- crossToolRulesPath: path to coordination rules JSON

Tool fields
- name: string
- detectCommands: [string]
- versionCommand/updateCommand/installCommand: [string]
- configPaths/logPaths: [string]
- capabilities: [string]
- adapterScript: string (path to adapter script)

See schema: `AIM_config/AIM_registry.schema.json`

