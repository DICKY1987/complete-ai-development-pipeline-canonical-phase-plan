# ADR-XXXX: [Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]  
**Date:** YYYY-MM-DD  
**Deciders:** [Names or roles]  
**Context:** [Brief description of the problem or situation]

---

## Decision

[Describe the decision that was made. Be concise but complete.]

Example:
> We will use SQLite for state storage instead of PostgreSQL or Redis.

---

## Rationale

[Explain WHY this decision was made. Include key factors, constraints, and reasoning.]

Example:
> - **Simplicity:** SQLite requires no separate server process
> - **Developer Experience:** Zero-configuration, works out of the box
> - **Requirements Met:** Our workload is primarily single-writer, low concurrency
> - **Constraints:** Project must run on Windows, macOS, and Linux without dependencies

---

## Consequences

### Positive

- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

Example:
- Faster onboarding - no database server setup required
- Reduced operational complexity
- Cross-platform compatibility guaranteed

### Negative

- [Tradeoff 1]
- [Tradeoff 2]

Example:
- Limited concurrent write capacity
- Scalability constraints for very large datasets

### Neutral

- [Neutral consequence 1]

Example:
- Database file requires backup strategy

---

## Alternatives Considered

### Alternative 1: [Name]

**Description:** [What it is]

**Rejected because:**
- [Reason 1]
- [Reason 2]

Example:
### Alternative 1: PostgreSQL

**Description:** Industry-standard relational database with advanced features

**Rejected because:**
- Requires separate server process and configuration
- Adds deployment complexity for local development
- Overkill for our single-writer use case

---

### Alternative 2: [Name]

**Description:** [What it is]

**Rejected because:**
- [Reason 1]

---

## Related Decisions

- [ADR-XXXX: Related Decision Title](XXXX-related-decision.md)
- Links to related architecture documents

---

## References

- [Link to relevant code](../../path/to/code.py)
- [Link to relevant documentation](../relevant-doc.md)
- External references if applicable

---

## Notes

[Optional section for additional context, migration notes, or future considerations]

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial draft | Name |
| YYYY-MM-DD | Accepted | Name |
