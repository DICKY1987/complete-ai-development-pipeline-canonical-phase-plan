# Template System - Quick Start Guide

**Created**: 2025-12-09
**Status**: Active

Welcome to the UET Template System! This guide gets you started quickly.

---

## 📚 Documentation Index

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[TEMPLATE_STANDARDS.md](TEMPLATE_STANDARDS.md)** | Complete standards guide | Creating or reviewing templates |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | What was done & why | Understanding the system |
| **[MIGRATION_STATUS.md](MIGRATION_STATUS.md)** | Migration progress | Tracking completion |
| **[TEMPLATE_REGISTRY.yaml](TEMPLATE_REGISTRY.yaml)** | Template catalog | Finding templates |

---

## 🚀 Quick Start

### Using a Template

1. **Find the template you need**
   ```bash
   cat TEMPLATE_REGISTRY.yaml | grep "purpose:"
   ```

2. **Copy it to your project**
   ```bash
   cp templates/doc/doc_readme_module.md.template my-module/README.md
   ```

3. **Fill in the variables**
   - Replace all `${VARIABLE}` placeholders
   - Check the "Template Variables" table in each template

4. **Remove the frontmatter** (optional)
   - Keep it for tracking, or remove the `---` section

### Creating a New Template

1. **Read the standards**
   ```bash
   # Section 1-6 are essential
   less TEMPLATE_STANDARDS.md
   ```

2. **Choose the right category**
   - `doc_` - Documentation
   - `code_` - Code implementations
   - `test_` - Tests
   - `spec_` - Specifications
   - `plan_` - Planning docs
   - `config_` - Configurations

3. **Use the naming convention**
   ```
   {category}_{name}_{type}.{extension}.template
   
   Examples:
   - doc_readme_api.md.template
   - code_service_class.py.template
   - test_integration_suite.py.template
   ```

4. **Include required frontmatter**
   ```yaml
   ---
   doc_id: DOC-{CATEGORY}-{NAME}-{NNN}
   version: 1.0.0
   created: 2025-12-09
   last_updated: 2025-12-09
   status: active
   template_type: code|documentation|test|specification|configuration
   target_extension: .py|.md|.yaml|.json
   ---
   ```

5. **Add required sections**
   - Variable documentation table
   - Usage instructions
   - Complete example
   - Validation checklist

6. **Validate it**
   ```bash
   python validate_templates.py
   ```

---

## 📁 Directory Structure

```
templates/
├── README.md                          ← You are here
├── TEMPLATE_STANDARDS.md              ← Standards guide
├── IMPLEMENTATION_SUMMARY.md          ← What was done
├── MIGRATION_STATUS.md                ← Progress tracking
├── TEMPLATE_REGISTRY.yaml             ← Template catalog
├── validate_templates.py              ← Validation script
│
├── code/                              ← Code templates
│   ├── python/
│   │   └── code_api_endpoint.py.template
│   ├── yaml/
│   └── shell/
│
├── test/                              ← Test templates
│   └── test_unit_standard.py.template
│
├── doc/                               ← Documentation templates
│   ├── doc_decision_record.md.template
│   ├── doc_pull_request.md.template
│   ├── doc_module_manifest.md.template
│   └── doc_readme_module.md.template
│
├── spec/                              ← Specification templates
├── config/                            ← Configuration templates
├── plan/                              ← Planning templates
└── examples/                          ← Example files
    └── example-items.json
```

---

## 🎯 Common Tasks

### Find a Template

**By purpose:**
```bash
grep -r "purpose:" TEMPLATE_REGISTRY.yaml
```

**By category:**
```bash
ls templates/doc/     # Documentation templates
ls templates/code/    # Code templates
ls templates/test/    # Test templates
```

**By name:**
```bash
find templates -name "*api*.template"
```

### Validate Templates

**All templates:**
```bash
python validate_templates.py
```

**Single template:**
```bash
python validate_templates.py templates/doc/doc_readme_module.md.template
```

### Check Migration Status

```bash
cat MIGRATION_STATUS.md
```

---

## 📊 Template Inventory

### Currently Available (7 templates)

#### Documentation (4)
- `doc_decision_record.md.template` - Architecture Decision Records
- `doc_pull_request.md.template` - Pull request descriptions
- `doc_module_manifest.md.template` - AI-readable module specs
- `doc_readme_module.md.template` - Module README files

#### Code (1)
- `code_api_endpoint.py.template` - RESTful CRUD endpoints

#### Test (1)
- `test_unit_standard.py.template` - Standard unit tests

#### Examples (1)
- `example-items.json` - Example JSON data

### Coming Soon (8 templates)

- Specification templates
- Planning templates
- Configuration templates
- More test templates

See [MIGRATION_STATUS.md](MIGRATION_STATUS.md) for details.

---

## 🔍 Template Quality Standards

All templates must have:

- ✅ Proper naming (`{category}_{name}_{type}.{ext}.template`)
- ✅ YAML frontmatter with all required fields
- ✅ Variable documentation table
- ✅ Clear instructions
- ✅ Complete usage example
- ✅ Validation checklist

Run `python validate_templates.py` to check compliance.

---

## 💡 Best Practices

### DO ✅
- Use descriptive variable names
- Provide working examples
- Include validation checklists
- Test templates before committing
- Document all assumptions
- Keep templates focused

### DON'T ❌
- Mix multiple patterns in one template
- Leave placeholder code (TODO, FIXME)
- Skip documentation sections
- Hardcode values that should be variables
- Create templates for one-time use

---

## 🛠️ Tools

### validate_templates.py
Validates templates against standards.

```bash
python validate_templates.py
```

Checks:
- File naming convention
- Frontmatter presence and validity
- Required fields
- Version format
- Status values

### Coming Soon
- `fill_template.py` - Automated variable substitution
- `list_templates.py` - Template browser/search
- `create_template.py` - Template scaffolding tool

---

## 📈 Metrics

### Migration Progress
- **Total Templates**: 15
- **Migrated**: 7 (47%)
- **Remaining**: 8 (53%)

### Quality Score
- **Naming Compliance**: 100% (7/7)
- **Frontmatter Compliance**: 100% (7/7)
- **Documentation Completeness**: 100% (7/7)
- **Examples Included**: 100% (7/7)

---

## 🆘 Getting Help

### For Template Users
1. Check template's "Instructions" section
2. Review the "Usage Example"
3. Consult TEMPLATE_STANDARDS.md

### For Template Authors
1. Read TEMPLATE_STANDARDS.md (sections 1-6)
2. Look at existing templates as examples
3. Use validation script to check work

### For Issues
- **Template bugs**: File issue with label `template-bug`
- **New template requests**: File issue with label `template-request`
- **Improvements**: Submit PR with label `template-enhancement`

---

## 🎓 Learning Path

**New to templates?** Start here:
1. Read this README (you're here!)
2. Look at `doc_readme_module.md.template` (simplest example)
3. Create a README for an existing module using the template
4. Review IMPLEMENTATION_SUMMARY.md to understand the system

**Creating templates?** Follow this:
1. Read TEMPLATE_STANDARDS.md sections 1-6
2. Study 2-3 existing templates in your category
3. Draft your template following the structure
4. Run `validate_templates.py`
5. Test by creating real artifact
6. Submit for review

**Maintaining templates?** Remember to:
1. Update version on changes (patch/minor/major)
2. Update `last_updated` date
3. Add to changelog if major/minor version
4. Re-validate after changes
5. Update TEMPLATE_REGISTRY.yaml

---

## 📅 Roadmap

### Phase 1: Foundation ✅ (Complete)
- Standards document created
- Directory structure established
- Registry system implemented
- Initial 7 templates migrated

### Phase 2: Migration (In Progress)
- [ ] Migrate remaining 8 templates
- [ ] Validate all templates
- [ ] Archive old templates
- [ ] Update all documentation

### Phase 3: Tooling (Planned)
- [ ] Variable substitution tool
- [ ] Template browser CLI
- [ ] Usage analytics
- [ ] Template scaffolding tool

### Phase 4: Integration (Future)
- [ ] Integrate with workstream system
- [ ] AI-assisted template creation
- [ ] Template marketplace
- [ ] Cross-project template sharing

---

## 📞 Contact

**Owner**: UET Framework Team
**Review Cycle**: Quarterly
**Next Review**: 2026-03-09

---

**Last Updated**: 2025-12-09
**Version**: 1.0.0
