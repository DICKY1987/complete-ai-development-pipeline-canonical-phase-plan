---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-AGENT_GUIDE_START_HERE-109
---

# Agent Guide - START HERE

> **Quick Navigation**: Find the right agent documentation for your needs

---

## 🎯 What Do You Need?

### "I want to know which agent to use for my task"
➜ **Read**: [Agent Quick Reference](AGENT_QUICK_REFERENCE.md)  
📊 **What you'll find**: Decision tree, task-to-agent mapping, common scenarios  
⏱️ **Reading time**: 5 minutes

---

### "I want to understand all available agents"
➜ **Read**: [Agent Analysis & Recommendations](AGENT_ANALYSIS_AND_RECOMMENDATIONS.md)  
📊 **What you'll find**: Complete analysis of 6 existing agents + 7 recommended new ones  
⏱️ **Reading time**: 15-20 minutes

---

### "I want to develop a custom agent"
➜ **Read**: [Custom Agents Directory](../scripts/agents/README.md)  
📊 **What you'll find**: Development guidelines, templates, standards  
⏱️ **Reading time**: 10 minutes + implementation time

---

### "I just need a quick command"

**Check code quality:**
```bash
python scripts/run_error_engine.py <files>
```

**Validate workstreams:**
```bash
python scripts/validate_workstreams.py
```

**Generate spec index:**
```bash
python scripts/generate_spec_index.py
```

**Start workstream generator (template - needs implementation):**
```bash
python scripts/agents/workstream_generator.py --interactive
```

---

## 📚 All Agent Documentation

| Document | Purpose | Best For |
|----------|---------|----------|
| [Agent Quick Reference](AGENT_QUICK_REFERENCE.md) | Fast decision guide | Choosing the right agent |
| [Agent Analysis & Recommendations](AGENT_ANALYSIS_AND_RECOMMENDATIONS.md) | Comprehensive analysis | Understanding ecosystem |
| [Custom Agents Directory](../scripts/agents/README.md) | Development guide | Building new agents |
| [AGENTS.md](../AGENTS.md) | Repository conventions | All contributors |
| [CLAUDE.md](../CLAUDE.md) | Claude Code instructions | Using Claude Code |
| [.github/copilot-instructions.md](../.github/copilot-instructions.md) | Copilot configuration | Using GitHub Copilot |

---

## 🚀 Quick Start Examples

### Example 1: Small Code Edit
**Use**: GitHub Copilot (in your IDE)  
**Time**: Instant suggestions as you type

### Example 2: Feature Across 3 Files
**Use**: Claude Code with task specification  
**Time**: 30-60 minutes  
**See**: [CLAUDE.md](../CLAUDE.md) for task spec format

### Example 3: Code Quality Check
**Use**: Error Engine  
**Command**: `python scripts/run_error_engine.py <files>`  
**Time**: 2-5 minutes

### Example 4: Create New Workstream
**Current**: Manual (20-30 minutes)  
**Future**: Workstream Generator Agent (5 minutes)  
**Status**: Template ready, needs implementation

---

## 💡 Key Insights

### Existing Agents (Ready to Use)
1. **GitHub Copilot** - Code completion
2. **Claude Code** - Patch-first development
3. **Codex CLI** - Workstream coordination
4. **Error Engine** - 15+ quality plugins
5. **Job Engine** - 4 tool adapters
6. **40+ Scripts** - Automation

### High-Priority Custom Agents (Should Build)
1. **Workstream Generator** - 75% time savings
2. **Code Migration Agent** - Systematic refactoring
3. **Test Generator** - 67% time savings

---

## 📞 Need Help?

- **General questions**: Open an issue
- **Agent not working**: Check [AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md) emergency section
- **Want to contribute**: See [Custom Agents Directory](../scripts/agents/README.md)

---

**Last Updated**: 2025-11-23  
**Maintained By**: AI Development Pipeline Team
