---
doc_id: DOC-GUIDE-AUTOMATION-GAP-ANALYSIS-187
---

# Automation Gap Analysis Prompt

## Mission
Analyze this codebase to identify automation gaps and deliver specific, actionable recommendations to close each gap.

## Analysis Framework

### 1. Discovery Phase
Scan the repository for:
- **Manual processes**: Scripts requiring human intervention, TODO comments, manual deployment steps
- **Repetitive patterns**: Similar code blocks, copy-paste patterns, duplicated logic
- **Missing validations**: Lack of pre-commit hooks, CI checks, automated quality gates
- **Incomplete workflows**: Partially automated processes with manual handoffs
- **Error-prone operations**: Manual data transformations, config changes, release processes

### 2. Gap Identification Criteria
For each potential gap, evaluate:
- **Frequency**: How often is this task performed? (Daily/Weekly/Monthly/Rare)
- **Time cost**: Estimated person-hours per execution
- **Error risk**: Probability of human error (High/Medium/Low)
- **Complexity**: Current manual steps required (count and describe)
- **Automation feasibility**: Technical difficulty (Trivial/Moderate/Complex)
- **ROI**: (Time saved × Frequency) - Implementation cost

### 3. Evidence Collection
Document each gap with:
```
Gap ID: GAP-XXX
Location: [file path or process name]
Type: [Manual Workflow | Repetitive Code | Missing Validation | Incomplete Automation]
Current State: [Describe what exists today]
Problem: [What's inefficient or error-prone]
Impact: [Quantify time/risk/quality impact]
Evidence: [Code snippets, file paths, workflow descriptions]
```

### 4. Recommendation Structure
For each identified gap, provide:

```
Gap ID: GAP-XXX
Priority: [Critical | High | Medium | Low]

RECOMMENDATION:
  Title: [Concise action-oriented title]

  Solution: [Specific technical approach]
  - Tool/Technology: [What to use]
  - Implementation: [Step-by-step approach]
  - Integration point: [Where it fits in existing system]

  Effort Estimate: [Hours or story points]

  Expected Benefits:
  - Time saved: [X hours per week/month]
  - Error reduction: [X% fewer incidents]
  - Quality improvement: [Specific metrics]

  Implementation Steps:
  1. [Concrete first step]
  2. [Next step]
  3. [...]

  Dependencies: [Prerequisites or blockers]

  Quick Win Potential: [Yes/No + explanation]
```

## Analysis Scope

### Required Scans
1. **Build & Test**
   - Is there automated testing? (Unit, integration, E2E)
   - Are tests run automatically on commits?
   - Is code coverage tracked?
   - Are builds reproducible?

2. **Deployment & Release**
   - Deployment process automation level
   - Release notes generation
   - Versioning strategy
   - Rollback procedures

3. **Code Quality**
   - Linting/formatting automation
   - Static analysis tools
   - Security scanning
   - Dependency updates

4. **Documentation**
   - Auto-generated docs from code
   - Changelog automation
   - API documentation
   - Architecture diagrams

5. **Development Workflow**
   - Branch protection rules
   - PR templates and automation
   - Issue/ticket tracking integration
   - Local development setup automation

6. **Monitoring & Alerts**
   - Automated error detection
   - Performance monitoring
   - Log aggregation
   - Incident response automation

7. **Data Operations**
   - Database migrations
   - Backup automation
   - Data validation
   - ETL processes

## Output Format

Deliver findings as a structured report:

### Executive Summary
- Total gaps identified: X
- Critical gaps: X
- High-impact quick wins: X
- Total potential time savings: X hours/month
- Estimated implementation effort: X hours

### Gap Inventory (Priority-Sorted)
[Table with: Gap ID | Type | Priority | Time Savings | Effort]

### Detailed Recommendations
[Full recommendation structure for each gap]

### Implementation Roadmap
**Phase 1 (Quick Wins - Week 1-2)**
- [High ROI, low effort items]

**Phase 2 (High Impact - Month 1)**
- [Critical gaps with moderate effort]

**Phase 3 (Long-term - Quarter 1)**
- [Complex but valuable improvements]

### Appendix
- Code examples of manual processes
- Workflow diagrams showing handoffs
- Metrics baseline for measuring improvement

## Analysis Instructions

1. **Be Specific**: Don't just say "add tests" - specify which modules lack tests, what type of tests, and recommended frameworks
2. **Quantify Impact**: Provide estimates (even rough) for time savings and error reduction
3. **Prioritize Ruthlessly**: Focus on highest ROI items first
4. **Consider Context**: Respect existing patterns and tools in the codebase
5. **Think Incrementally**: Break large automation opportunities into smaller deliverable chunks
6. **Validate Feasibility**: Only recommend what's technically possible with available tools/skills

## Example Output Snippet

```
GAP-003: Manual Database Migration Verification
Priority: High

RECOMMENDATION:
  Title: Automate database migration testing in CI pipeline

  Solution: Add migration validation to GitHub Actions workflow
  - Tool/Technology: pytest + sqlalchemy + docker
  - Implementation:
    * Spin up test database in Docker
    * Apply migrations in isolated environment
    * Run schema validation tests
    * Verify rollback procedures
  - Integration point: .github/workflows/ci.yml

  Effort Estimate: 8 hours

  Expected Benefits:
  - Time saved: 2 hours per deployment (8 hours/month)
  - Error reduction: 90% fewer schema-related production incidents
  - Quality improvement: 100% migration coverage before merge

  Implementation Steps:
  1. Create Docker Compose config for test database
  2. Write pytest fixtures for migration testing
  3. Add GitHub Actions job with database service
  4. Update CONTRIBUTING.md with new requirements
  5. Add migration checklist to PR template

  Dependencies: Docker available in CI environment

  Quick Win Potential: Yes - Prevents common class of production errors with moderate effort
```

## Success Criteria

Your analysis is complete when:
- ✅ Every manual process has been evaluated
- ✅ Each gap has a quantified ROI estimate
- ✅ Recommendations are specific and actionable
- ✅ Implementation steps are concrete and sequenced
- ✅ Quick wins are clearly identified
- ✅ Long-term improvements have a roadmap

## Begin Analysis

Start by examining:
1. `.github/workflows/` - CI/CD automation
2. `scripts/` - Existing automation attempts
3. `docs/` - Documentation of manual processes
4. Root config files - Tool configuration completeness
5. `tests/` - Test coverage and automation
6. Issue tracker - Recurring manual tasks or errors

Generate the complete gap analysis report now.
