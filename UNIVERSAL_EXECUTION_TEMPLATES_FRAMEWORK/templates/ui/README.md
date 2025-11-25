# UI Templates

> **User Interface Component Templates - Dashboards, Reports, and Monitoring**  
> **Purpose**: Visualize execution progress and results  
> **Layer**: UI (User Interface)

---

## 📋 Overview

UI templates provide starting points for building user interfaces, reports, and monitoring views for the UET Framework. They handle visualization of execution state, progress tracking, and result reporting.

### What's in This Directory

```
ui/
├── README.md                    # This file
├── STYLING_GUIDE.md             # Design and styling standards
│
├── dashboards/                  # Dashboard layout templates
├── reports/                     # Report generation templates
└── monitoring/                  # Monitoring view templates
```

---

## 🎯 Template Categories

### 1. Dashboard Templates (`dashboards/`)

**Purpose**: Interactive real-time views

**Use Cases**:
- Progress tracking dashboards
- Metrics visualization
- Error monitoring
- Resource usage

**Key Templates**:
- `dashboard-progress-template.html` - Execution progress view
- `dashboard-metrics-template.html` - Performance metrics
- `dashboard-errors-template.html` - Error tracking

**Example**:
```html
<!-- dashboard-progress-template.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Pipeline Progress - {{PROJECT_NAME}}</title>
</head>
<body>
    <div class="progress-container">
        <h1>Execution Progress</h1>
        <div class="progress-bar" data-run-id="{{RUN_ID}}">
            <!-- Real-time progress updates -->
        </div>
    </div>
</body>
</html>
```

---

### 2. Report Templates (`reports/`)

**Purpose**: Static generated summaries

**Use Cases**:
- Execution summaries
- Detailed analysis reports
- Historical comparisons
- Export to PDF/HTML

**Key Templates**:
- `report-execution-template.md` - Markdown execution report
- `report-summary-template.md` - High-level summary
- `report-detailed-template.html` - Detailed HTML report

**Example**:
```markdown
<!-- report-execution-template.md -->
# Execution Report: {{RUN_ID}}

**Project**: {{PROJECT_NAME}}  
**Started**: {{START_TIME}}  
**Completed**: {{END_TIME}}  
**Duration**: {{DURATION}}

## Summary
- Total Tasks: {{TASK_COUNT}}
- Completed: {{COMPLETED_COUNT}}
- Failed: {{FAILED_COUNT}}
- Success Rate: {{SUCCESS_RATE}}%

## Details
<!-- Detailed task results -->
```

---

### 3. Monitoring Templates (`monitoring/`)

**Purpose**: Observability and telemetry

**Use Cases**:
- Real-time monitoring configuration
- Historical trend analysis
- Alert definitions
- Metric collection

**Key Templates**:
- `monitoring-realtime-template.json` - Real-time config
- `monitoring-historical-template.json` - Historical analysis

**Example**:
```json
{
  "monitoring_id": "{{MONITOR_ID}}",
  "run_id": "{{RUN_ID}}",
  "refresh_interval": 5,
  "metrics": [
    "progress_percent",
    "tasks_completed",
    "error_count",
    "estimated_completion"
  ]
}
```

---

## 🚀 Quick Start

### Creating a Dashboard

```bash
# 1. Copy template
cp templates/ui/dashboards/dashboard-progress-template.html \
   my-dashboard.html

# 2. Customize
# Replace {{PLACEHOLDERS}}
# Add custom styling
# Connect to data sources

# 3. Preview
python -m http.server 8000
# Visit http://localhost:8000/my-dashboard.html
```

### Generating a Report

```bash
# 1. Copy template
cp templates/ui/reports/report-execution-template.md \
   report.md

# 2. Populate with data
python scripts/generate_report.py \
  --template report.md \
  --run-id run-123 \
  --output report-123.md

# 3. Convert to HTML/PDF (optional)
pandoc report-123.md -o report-123.pdf
```

### Setting Up Monitoring

```bash
# 1. Copy template
cp templates/ui/monitoring/monitoring-realtime-template.json \
   monitoring-config.json

# 2. Configure
# Set run_id, metrics, refresh interval

# 3. Start monitoring
python scripts/start_monitoring.py \
  --config monitoring-config.json
```

---

## 📊 Data Integration

### Connecting to Execution State

```python
# Example: Fetch data for dashboard
from core.state.db import get_run_progress

def get_dashboard_data(run_id):
    """Fetch data for progress dashboard"""
    progress = get_run_progress(run_id)
    
    return {
        'run_id': run_id,
        'progress_percent': progress.completion_percent,
        'tasks_total': progress.tasks_total,
        'tasks_completed': progress.tasks_completed,
        'estimated_completion': progress.eta
    }
```

### Real-time Updates

```javascript
// Example: Real-time progress updates
function updateProgress(runId) {
    fetch(`/api/runs/${runId}/progress`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('progress-bar').style.width = 
                `${data.progress_percent}%`;
            document.getElementById('tasks-completed').textContent = 
                `${data.tasks_completed} / ${data.tasks_total}`;
        });
}

// Refresh every 5 seconds
setInterval(() => updateProgress('{{RUN_ID}}'), 5000);
```

---

## 🎨 Styling Guide

### Design Principles

1. **Clarity**: Information should be easy to scan
2. **Consistency**: Use consistent colors and layouts
3. **Responsiveness**: Work on different screen sizes
4. **Accessibility**: Follow WCAG guidelines

### Color Scheme

```css
:root {
    /* Status colors */
    --success: #28a745;
    --warning: #ffc107;
    --error: #dc3545;
    --info: #17a2b8;
    
    /* Progress colors */
    --progress-bg: #e9ecef;
    --progress-fill: #007bff;
    
    /* Text colors */
    --text-primary: #212529;
    --text-secondary: #6c757d;
}
```

### Layout Patterns

```css
/* Dashboard container */
.dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Card layout */
.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}

/* Progress bar */
.progress {
    height: 30px;
    background: var(--progress-bg);
    border-radius: 15px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--progress-fill);
    transition: width 0.3s ease;
}
```

---

## 📈 Common UI Patterns

### Pattern 1: Progress Indicator

```html
<div class="progress-section">
    <h3>Overall Progress</h3>
    <div class="progress">
        <div class="progress-fill" style="width: {{PROGRESS}}%">
            {{PROGRESS}}%
        </div>
    </div>
    <p>{{TASKS_COMPLETED}} of {{TASKS_TOTAL}} tasks completed</p>
</div>
```

### Pattern 2: Task List

```html
<div class="task-list">
    <h3>Tasks</h3>
    <ul>
        {{#TASKS}}
        <li class="task task-{{STATUS}}">
            <span class="task-id">{{TASK_ID}}</span>
            <span class="task-status">{{STATUS}}</span>
            <span class="task-duration">{{DURATION}}s</span>
        </li>
        {{/TASKS}}
    </ul>
</div>
```

### Pattern 3: Error Display

```html
<div class="errors-section">
    <h3>Errors ({{ERROR_COUNT}})</h3>
    {{#ERRORS}}
    <div class="error-card">
        <h4>{{ERROR_TYPE}}</h4>
        <p>{{ERROR_MESSAGE}}</p>
        <pre>{{ERROR_TRACE}}</pre>
    </div>
    {{/ERRORS}}
</div>
```

---

## 🔄 Dynamic Updates

### WebSocket Integration

```javascript
// Real-time updates via WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    
    if (update.type === 'progress') {
        updateProgressBar(update.data);
    } else if (update.type === 'task_complete') {
        addTaskToList(update.data);
    } else if (update.type === 'error') {
        showError(update.data);
    }
};
```

### Polling Alternative

```javascript
// Simple polling for updates
async function pollForUpdates(runId) {
    while (true) {
        const response = await fetch(`/api/runs/${runId}/status`);
        const status = await response.json();
        
        updateUI(status);
        
        if (status.completed) {
            break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}
```

---

## ✅ Best Practices

### Performance

- **Lazy load**: Load data only when needed
- **Debounce updates**: Avoid excessive re-renders
- **Use pagination**: For large datasets
- **Cache responses**: Reduce API calls

### Accessibility

- **Use semantic HTML**: `<nav>`, `<main>`, `<article>`
- **ARIA labels**: For screen readers
- **Keyboard navigation**: Tab through elements
- **Color contrast**: WCAG AA compliance

### Error Handling

```javascript
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        showErrorMessage('Failed to load data. Please try again.');
        return null;
    }
}
```

---

## 📚 Related Documentation

- **[Templates Main README](../README.md)** - Overview
- **[STYLING_GUIDE.md](STYLING_GUIDE.md)** - Design standards
- **[Orchestration Templates](../orchestration/README.md)** - Execution data
- **[UET Monitoring Spec](../../specs/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md)**

---

## 🛠️ Tools and Libraries

### Recommended Libraries

**JavaScript**:
- **Chart.js**: For graphs and charts
- **WebSocket**: Real-time updates
- **Mustache.js**: Template rendering

**Python**:
- **Jinja2**: Template engine
- **Flask/FastAPI**: Web framework
- **Plotly**: Interactive charts

**CSS**:
- **Bootstrap**: Component library
- **Tailwind**: Utility-first CSS
- **Custom**: Use provided styling guide

---

## 📞 Support

**Q: How do I add real-time updates?**  
A: Use WebSocket or polling. See [Dynamic Updates](#-dynamic-updates).

**Q: Can I use React/Vue/Angular?**  
A: Yes! Templates are starting points. Use any framework you prefer.

**Q: How do I export reports to PDF?**  
A: Use tools like `pandoc` (Markdown → PDF) or `wkhtmltopdf` (HTML → PDF).

---

**Last Updated**: 2025-11-23  
**Related**: [Configuration](../configuration/README.md), [Examples](../examples/README.md)
