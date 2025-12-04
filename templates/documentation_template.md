---
doc_id: DOC-{{category}}-{{topic}}-001
title: {{title}}
audience: {{audience}}
status: {{status}}
version: {{version}}
created: {{created_date}}
last_updated: {{last_updated}}
---

# {{title}}

## Overview

{{overview}}

## Table of Contents

{% for section in sections %}
- [{{section.title}}](#{{section.anchor}})
{% endfor %}

---

{% for section in sections %}
## {{section.title}}

{{section.content}}

{% if section.subsections %}
{% for subsection in section.subsections %}
### {{subsection.title}}

{{subsection.content}}

{% endfor %}
{% endif %}

{% endfor %}

---

## Examples

{% for example in examples %}
### Example {{loop.index}}: {{example.title}}

{{example.description}}

```{{example.language}}
{{example.code}}
```

{% if example.notes %}
**Notes**: {{example.notes}}
{% endif %}

{% endfor %}

---

## Troubleshooting

{% for issue in troubleshooting %}
### {{issue.problem}}

**Symptoms**: {{issue.symptoms}}

**Solution**: {{issue.solution}}

{% if issue.prevention %}
**Prevention**: {{issue.prevention}}
{% endif %}

{% endfor %}

---

## References

{% for ref in references %}
- [{{ref.title}}]({{ref.url}}){% if ref.description %} - {{ref.description}}{% endif %}
{% endfor %}

---

**Document Status**: {{status}}
**Last Updated**: {{last_updated}}
**Maintained By**: {{maintainer}}
