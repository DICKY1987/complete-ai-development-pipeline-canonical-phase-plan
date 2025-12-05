# PNG Exports

PNG image exports for embedding in markdown documentation.

## 📐 Export Settings

- **Resolution**: 150 DPI (web) or 300 DPI (print)
- **Background**: White (not transparent)
- **Size**: Auto-calculated from diagram
- **Format**: PNG

## 📝 Naming

Match source file names exactly:
- `architecture-layers.png` ← from `source/architecture/architecture-layers.drawio`
- `phase-0-bootstrap.png` ← from `source/phases/phase-0-bootstrap.drawio`

## 📖 Usage in Markdown

```markdown
![Diagram Title](diagrams/exports/png/diagram-name.png)
```
