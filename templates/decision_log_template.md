---
decision_id: DECISION-{{topic}}-001
date: {{date}}
status: {{status}}
author: {{author}}
---

# Decision: {{title}}

## Context

{{context}}

## Problem Statement

{{problem}}

## Options Considered

{% for option in options %}
### Option {{loop.index}}: {{option.name}}

**Description**: {{option.description}}

**Pros**:
{% for pro in option.pros %}
- {{pro}}
{% endfor %}

**Cons**:
{% for con in option.cons %}
- {{con}}
{% endfor %}

**Recommendation**: {{option.recommendation}}

{% endfor %}

## Decision

**Chosen Option**: {{chosen_option}}

**Rationale**: {{rationale}}

## Consequences

### Positive
{% for consequence in positive_consequences %}
- {{consequence}}
{% endfor %}

### Negative
{% for consequence in negative_consequences %}
- {{consequence}}
{% endfor %}

### Risks
{% for risk in risks %}
- {{risk}}
{% endfor %}

## Implementation Notes

{{implementation_notes}}

## Timeline

- **Decision Date**: {{date}}
- **Implementation Start**: {{implementation_start}}
- **Expected Completion**: {{expected_completion}}

## Related Decisions

{% for related in related_decisions %}
- {{related}}
{% endfor %}

## References

{% for ref in references %}
- {{ref}}
{% endfor %}
