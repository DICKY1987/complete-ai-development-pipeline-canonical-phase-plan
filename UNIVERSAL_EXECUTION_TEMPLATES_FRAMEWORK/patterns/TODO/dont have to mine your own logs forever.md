Short version: you *don’t* have to mine your own logs forever. There are already good, battle-tested pattern libraries you can steal from and then normalize into your `patterns/` registry.

I’ll split this into two things:

1. **Where to get proven patterns**
2. **How to plug them into your pattern system so you stop re-discovering them**

---

## 1. Where to get proven patterns

### A. Spec / workflow patterns for AI coding

**1. OpenSpec (Fission-AI/OpenSpec)**
This is basically “patterns for AI coding assistants” baked into a framework:

* Ships with example specs, task flows, and “spec-driven development” workflows designed for AI tools.([GitHub][1])
* Focus is: *define the spec & pattern first, then let the AI write code.*
  This maps **directly** to what you’re trying to do (pattern-first execution instead of ad-hoc prompts).

Use it as:

* A source of **spec patterns** (e.g., how to structure a feature spec, acceptance criteria, etc.).
* A reference for **directory layout and IDs** you can mirror in your `patterns/specs/` + `PATTERN_INDEX.yaml`.

---

**2. Claude Code Project Management (CCPM)**

CCPM is a project-management system specifically for Claude Code, built around GitHub Issues + Git worktrees + slash commands.([GitHub][2])

What you get from CCPM (and its enhanced forks):

* **Standardized workflows** for:

  * Spinning up worktrees per task/workstream
  * Moving tasks through states (TODO → DOING → DONE)
  * Handling parallel execution
* The enhanced fork `johnproblems/formaltask` adds more structured task patterns & label flows you can study.([GitHub][3])

Even though CCPM isn’t packaged as “pattern YAML,” each **slash command + issue template + label flow** is essentially a **reusable pattern** you can port into your own pattern files.

---

**3. Claude Code docs & best-practice guides**

* **Claude Code official docs** (code.claude.com). These describe typical workflows (read codebase → plan → edit → test → refactor) that you can freeze into patterns.([Claude Code][4])
* **Anthropic’s “Claude Code: Best practices for agentic coding”** blog post: it outlines recurring workflows like “scoped refactor,” “incremental change & test,” “multi-file edits with safety,” etc.([Anthropic][5])

Those are ready-made **execution patterns** you can formalize as:

* `atomic_create.pattern.yaml`
* `refactor_patch.pattern.yaml`
* `batch_create.pattern.yaml`
* `read_and_map.pattern.yaml`, etc.

---

### B. General workflow / automation pattern catalogs

These aren’t Claude-specific, but they give **names and shapes** to the workflows you’re already doing:

1. **Workflow Patterns (van der Aalst et al.)** – the classic catalog of workflow patterns (sequence, parallel split, synchronization, choice, loops, etc.).([workflowpatterns.com][6])
2. **Cloud / workflow docs with common patterns**

   * AWS “What are common workflow patterns?” (microservice chaining, fan-out/fan-in, human approval steps, error handling).([Amazon Web Services, Inc.][7])
   * New Relic / other workflow-automation docs explaining switches, loops, approvals, etc.([New Relic][8])
3. **AI workflow pattern posts**

   * Articles summarizing “planning → tool-use → reflection” loops as reusable AI patterns.([Weaviate][9])

You don’t need their exact tools; you just need the **pattern shapes** and names, so you can standardize:

* `PLAN_EXECUTE_REFLECT`
* `FAN_OUT_ANALYSIS_THEN_FAN_IN_SUMMARY`
* `APPROVAL_GATE_BEFORE_MERGE`, etc.

Those then become pattern IDs in your own registry.

---

## 2. How to plug these into *your* pattern system

So you’re not asking “where” just for curiosity—you want to stop scraping logs every time. Here’s a concrete way to use the sources above:

### Step 1 – Create a “pattern import” folder

In your main repo, add:

```text
patterns/
  imported/
    openspec/
    ccpm/
    generic_workflows/
```

Drop copied/adapted examples here **as-is** (Markdown, YAML, whatever), *separate* from your canonical `patterns/specs/` and `patterns/executors/`. This keeps original sources intact.

---

### Step 2 – Normalize into your PATTERN_INDEX

For each pattern you adopt (say, “atomic file creation” from your UET docs or “scoped refactor” from Claude best-practices):

1. Assign a **stable pattern_id** (`PAT-ATOMIC-CREATE-001`).
2. Create:

   * `patterns/specs/atomic_create.pattern.yaml`
   * `patterns/schemas/atomic_create.schema.json`
   * `patterns/executors/atomic_create_executor.*`
   * `patterns/examples/atomic_create/…`
3. Add an entry in `patterns/registry/PATTERN_INDEX.yaml`.

That way:

* Once a pattern is in the index, **you never need log-mining for that behavior again**.
* Any AI agent or CLI can be forced to pick a **pattern_id first**, then fill in parameters.

---

### Step 3 – Seed “common tasks” from external sources

The fastest wins for you (based on all our previous chats) are:

* **Create / extend module** (module skeleton, tests, CLI, docs)
  → Source shapes from OpenSpec specs + Claude Code best-practice flow.
* **Scoped refactor with tests**
  → Steal the change-plan + “small batch with tests” shape from Claude docs & CCPM task flows.
* **Parallel workstreams with Git worktrees**
  → Directly formalize CCPM’s “one worktree per issue” approach as a `GIT_WORKTREE_WORKSTREAM` pattern.
* **Docs & ID synchronization**
  → A pattern that reads `DOC_LINK` and IDs and ensures docs/spec/tests stay in sync when files move.

---

### Step 4 – Make “pattern-first” usage mandatory

Once you have that small core library:

* Your prompts / slash commands should *always* look like:

  > “Use pattern `PAT-REF-001 (scoped refactor)` with these parameters: …
  > Do **not** invent a new workflow unless no existing pattern fits; if so, emit `PATTERN_SUGGESTION` instead of acting ad-hoc.”

* For Claude Code & Copilot CLI you can even bake this into:

  * A “Planner” prompt that **chooses pattern_id**.
  * An “Executor” prompt that fills in the fields defined by the pattern schema.

---

### TL;DR

**Where to look:**

* **OpenSpec** – spec-driven AI dev patterns you can lift directly.([GitHub][1])
* **CCPM + forks** – proven task + worktree patterns for Claude Code.([GitHub][2])
* **Claude Code docs & best-practice posts** – de-facto execution patterns: refactor, add tests, multi-file changes.([Claude Code][4])
* **General workflow catalogs** – formal names and shapes for sequences, fan-out/fan-in, approvals, loops, etc.([workflowpatterns.com][6])

If you want, next step I can do is: **list 10 concrete pattern IDs** you should create first (name + short intent + where to steal the structure from), so you have a starting library without staring at logs.

[1]: https://github.com/Fission-AI/OpenSpec?utm_source=chatgpt.com "Fission-AI/OpenSpec: Spec-driven development for AI ..."
[2]: https://github.com/automazeio/ccpm?utm_source=chatgpt.com "automazeio/ccpm: Project management system for Claude ..."
[3]: https://github.com/johnproblems/formaltask?utm_source=chatgpt.com "johnproblems/formaltask: Enhanced CCPM fork: AI- ..."
[4]: https://code.claude.com/docs/en/overview?utm_source=chatgpt.com "Claude Code overview - Claude Code Docs"
[5]: https://www.anthropic.com/engineering/claude-code-best-practices?utm_source=chatgpt.com "Claude Code: Best practices for agentic coding"
[6]: https://www.workflowpatterns.com/documentation/documents/coopis.pdf?utm_source=chatgpt.com "Advanced Workflow Patterns"
[7]: https://aws.amazon.com/what-is/workflow/?utm_source=chatgpt.com "What is a Workflow? - Cloud Computing Workflows Explained"
[8]: https://docs.newrelic.com/docs/workflow-automation/introduction-to-workflow/?utm_source=chatgpt.com "Introduction to Workflow Automation"
[9]: https://weaviate.io/blog/what-are-agentic-workflows?utm_source=chatgpt.com "What Are Agentic Workflows? Patterns, Use Cases, ..."
