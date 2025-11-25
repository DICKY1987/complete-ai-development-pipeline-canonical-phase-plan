# ADR-0005: Python Primary Language

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need to choose primary programming language(s) for the development pipeline

---

## Decision

We will use **Python as the primary implementation language**, with **PowerShell for Windows-specific automation**. All core pipeline logic, orchestration, and tooling will be written in Python.

---

## Rationale

### Python Strengths for This Project

1. **AI Tool Ecosystem:** Best-in-class libraries for AI integration (OpenAI, Anthropic, LangChain)
2. **Cross-Platform:** Works identically on Windows, macOS, Linux
3. **Readability:** Clear syntax makes it easy for AI agents to understand and generate
4. **Rich Standard Library:** Built-in support for JSON, subprocess, sqlite3, pathlib
5. **Testing Ecosystem:** pytest, unittest, coverage tools are mature
6. **Package Management:** pip and virtual environments are well-understood
7. **Type Hints:** Optional static typing via type annotations improves AI code generation

### PowerShell for Windows Gaps

PowerShell fills Windows-specific needs:
- System administration tasks (registry, services, processes)
- Native Windows tooling integration
- Existing PowerShell scripts in ecosystem
- User preference (many Windows developers prefer PS over bash)

### Division of Responsibility

- **Python:** Core logic, orchestration, state management, tool adapters, tests
- **PowerShell:** Bootstrap scripts, environment setup, Windows-specific automation
- **Shell Scripts (.sh):** Linux/macOS parity where beneficial (not required)

---

## Consequences

### Positive

- **AI-Friendly:** AI models excel at reading and writing Python
- **Developer Pool:** Large Python developer community
- **Library Availability:** Can leverage existing tools (NetworkX, Pydantic, Rich)
- **Consistent Style:** Single language reduces context switching
- **Testing Quality:** Excellent test tooling improves reliability

### Negative

- **Performance:** Python slower than compiled languages (acceptable for our use case)
- **Type Safety:** Optional typing means runtime errors possible (mitigated by tests)
- **Windows Users Learn Python:** Some may prefer C# or PowerShell-only

### Neutral

- **Version Management:** Must specify Python version (3.10+)
- **Dependency Management:** Need requirements.txt and venv conventions

---

## Alternatives Considered

### Alternative 1: TypeScript/Node.js

**Pros:**
- Excellent async/await support
- npm ecosystem is large
- Type safety with TypeScript

**Rejected because:**
- Less AI tooling integration (LangChain Python > JS)
- Callback hell in older Node code
- Python ecosystem is more mature for data/ML tasks

### Alternative 2: Go

**Pros:**
- Fast compilation and execution
- Great concurrency primitives
- Single binary deployment

**Rejected because:**
- Verbose error handling
- Less AI/ML library support
- Smaller developer pool familiar with Go
- AI models less proficient at generating Go code

### Alternative 3: Rust

**Pros:**
- Memory safety guarantees
- Excellent performance
- Growing ecosystem

**Rejected because:**
- Steep learning curve
- Slower development velocity
- Minimal AI/ML tooling
- AI models struggle with Rust's complexity

### Alternative 4: C# / .NET

**Pros:**
- Excellent Windows integration
- Strong type system
- Good performance

**Rejected because:**
- Less cross-platform (improving but Python better)
- Smaller AI/ML ecosystem vs Python
- Higher complexity for scripting tasks

---

## Related Decisions

- [ADR-0004: Section-Based Organization](0004-section-based-organization.md) - Code structure
- [ADR-0002: Hybrid Architecture](0002-hybrid-architecture.md) - GUI may use different tech

---

## References

- **Python Version:** Python 3.10+ required
- **Requirements:** `requirements.txt`
- **Style Guide:** Black formatter, PEP 8 conventions
- **Scripts:** `scripts/*.py` (Python), `scripts/*.ps1` (PowerShell)
- **Type Checking:** Optional via mypy or Pyright

---

## Notes

### Python Version Choice

We require **Python 3.10+** because:
- **Pattern Matching:** `match/case` statements improve readability
- **Type Hints:** Improved union types (`X | Y` syntax)
- **Performance:** Better startup time and runtime performance
- **Availability:** Widely available (released Oct 2021)

### PowerShell Strategy

PowerShell scripts are **thin wrappers** that:
- Set up environment variables
- Call Python scripts with appropriate arguments
- Provide Windows-native error messages

**Pattern:**
```powershell
# scripts/run_workstream.ps1
$ErrorActionPreference = "Stop"
python scripts/run_workstream.py @args
exit $LASTEXITCODE
```

### Future Language Considerations

- **Performance-Critical Paths:** May use Rust extensions via PyO3
- **GUI Implementation:** May use TypeScript/Electron or Python/Qt
- **Database Migrations:** SQL (technology-agnostic)

### AI Code Generation Quality

Python benefits most from AI assistance:
- **GPT-4:** Excellent Python generation
- **Claude:** Strong Python comprehension
- **Copilot:** Best suggestions in Python
- **Aider:** Optimized for Python codebases

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
