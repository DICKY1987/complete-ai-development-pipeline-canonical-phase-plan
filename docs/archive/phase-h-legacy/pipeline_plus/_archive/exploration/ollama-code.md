4. ollama-code – CLI agent closest in spirit to Aider

What it is

ollama-code is a CLI coding agent forked from Qwen Code / Gemini CLI, specifically redesigned to use locally hosted Ollama models for coding workflows.
GitHub
+1

Why it’s interesting

It’s very close to your desired shape:

Pure CLI, privacy-first.

Runs tasks against code in a workspace.

Since it’s open-source and purely local, it’s effectively unlimited use within your hardware limits.

Compared to Aider

Think of it as:

Aider → highly optimized “patch / multi-file edit” copilot.

ollama-code → more “task / workflow oriented CLI” that could be wrapped in your orchestrator like another tool_profile.

Might be a good additional tool_profile in tool_profiles.json next to aider, pointing at your DeepSeek Ollama model.