#!/usr/bin/env python3
"""Convert two prompt files to indexed JSON format."""

import json
import sys
from pathlib import Path

def create_gap_framework_json():
    """Create comprehensive gap-finding framework JSON."""
    return {
        'meta': {
            'doc_id': 'COMPREHENSIVE_GAP_FINDING_FRAMEWORK',
            'version': '1.0.0',
            'source_file': 'Comprehensive Gap-Finding Framework Making It Systematic and Continuous.txt',
            'description': 'Systematic and continuous gap-finding framework across four critical dimensions',
            'notes': [
                'Converted from text format to structured JSON',
                'Covers logical, process, architectural, and automation gaps',
                'Includes tooling recommendations and automation strategies'
            ]
        },
        'index': {
            'metadata': {
                'DOC_ID': {
                    'path': '/meta/doc_id',
                    'description': 'Unique identifier for this framework',
                    'tags': ['meta', 'identifier']
                },
                'VERSION': {
                    'path': '/meta/version',
                    'description': 'Framework version number',
                    'tags': ['meta', 'version']
                }
            },
            'dimensions': {
                'D_LOGICAL_GAPS': {
                    'path': '/dimensions/logical_gaps',
                    'description': 'Logical gaps dimension (correctness, behavior, edge cases)',
                    'tags': ['dimension', 'logical']
                },
                'D_PROCESS_WORKFLOW': {
                    'path': '/dimensions/process_workflow_gaps',
                    'description': 'Process and workflow gaps dimension',
                    'tags': ['dimension', 'process']
                },
                'D_ARCHITECTURAL': {
                    'path': '/dimensions/architectural_gaps',
                    'description': 'Architectural gaps dimension',
                    'tags': ['dimension', 'architecture']
                },
                'D_AUTOMATION': {
                    'path': '/dimensions/automation_gaps',
                    'description': 'Automation and ops gaps dimension',
                    'tags': ['dimension', 'automation']
                }
            },
            'frameworks': {
                'F_TESTING_PYRAMID': {
                    'path': '/dimensions/logical_gaps/frameworks/testing_pyramid',
                    'description': 'Multi-layer coverage analysis framework',
                    'tags': ['framework', 'testing', 'coverage']
                },
                'F_DOMAIN_INVARIANTS': {
                    'path': '/dimensions/logical_gaps/frameworks/domain_invariant_mapping',
                    'description': 'Domain invariant mapping framework',
                    'tags': ['framework', 'domain', 'invariants']
                },
                'F_FAILURE_MODE': {
                    'path': '/dimensions/logical_gaps/frameworks/failure_mode_analysis',
                    'description': 'Comprehensive failure mode analysis',
                    'tags': ['framework', 'failure', 'analysis']
                },
                'F_VALUE_STREAM': {
                    'path': '/dimensions/process_workflow_gaps/frameworks/value_stream_mapping',
                    'description': 'Value stream mapping framework',
                    'tags': ['framework', 'vsm', 'process']
                },
                'F_SDLC_MATURITY': {
                    'path': '/dimensions/process_workflow_gaps/frameworks/sdlc_maturity',
                    'description': 'SDLC maturity assessment framework',
                    'tags': ['framework', 'sdlc', 'maturity']
                },
                'F_TOIL_TRACKING': {
                    'path': '/dimensions/process_workflow_gaps/frameworks/toil_inventory',
                    'description': 'Toil tracking and automation scoring',
                    'tags': ['framework', 'toil', 'sre']
                },
                'F_ATAM': {
                    'path': '/dimensions/architectural_gaps/frameworks/atam',
                    'description': 'Architecture Tradeoff Analysis Method',
                    'tags': ['framework', 'architecture', 'atam']
                },
                'F_C4_ARC42': {
                    'path': '/dimensions/architectural_gaps/frameworks/c4_arc42',
                    'description': 'C4 Model + Arc42 documentation',
                    'tags': ['framework', 'architecture', 'documentation']
                },
                'F_QUALITY_MODELS': {
                    'path': '/dimensions/architectural_gaps/frameworks/quality_models',
                    'description': 'ISO/IEC 25010 quality models',
                    'tags': ['framework', 'quality', 'iso']
                },
                'F_CD_MATURITY': {
                    'path': '/dimensions/automation_gaps/frameworks/cd_maturity',
                    'description': 'Continuous delivery maturity model',
                    'tags': ['framework', 'cd', 'maturity']
                },
                'F_DORA': {
                    'path': '/dimensions/automation_gaps/frameworks/dora_metrics',
                    'description': 'DORA metrics and capabilities',
                    'tags': ['framework', 'dora', 'metrics']
                },
                'F_IAC': {
                    'path': '/dimensions/automation_gaps/frameworks/infrastructure_as_code',
                    'description': 'Infrastructure-as-Code framework',
                    'tags': ['framework', 'iac', 'infrastructure']
                },
                'F_OBSERVABILITY': {
                    'path': '/dimensions/automation_gaps/frameworks/observability_maturity',
                    'description': 'Observability maturity framework',
                    'tags': ['framework', 'observability', 'monitoring']
                }
            },
            'unified': {
                'WORKFLOW': {
                    'path': '/unified_framework/continuous_gap_analysis_workflow',
                    'description': 'Complete continuous gap-finding workflow',
                    'tags': ['unified', 'workflow', 'continuous']
                },
                'GAP_REGISTRY': {
                    'path': '/unified_framework/gap_registry',
                    'description': 'Central gap registry schema and operations',
                    'tags': ['unified', 'registry', 'central']
                },
                'AUTOMATION': {
                    'path': '/unified_framework/making_it_continuous',
                    'description': 'Continuous automation integration points',
                    'tags': ['unified', 'automation', 'ci']
                }
            },
            'tools': {
                'RECOMMENDED_STACK': {
                    'path': '/tools_and_platforms/recommended_stack',
                    'description': 'Recommended tooling stack by category',
                    'tags': ['tools', 'recommendations']
                },
                'ANALYSIS_TOOLS': {
                    'path': '/tools_and_platforms/recommended_stack/analysis_and_detection',
                    'description': 'Analysis and detection tools',
                    'tags': ['tools', 'analysis']
                },
                'WORKFLOW_TOOLS': {
                    'path': '/tools_and_platforms/recommended_stack/workflow_and_process',
                    'description': 'Workflow and process tools',
                    'tags': ['tools', 'workflow']
                },
                'AUTOMATION_TOOLS': {
                    'path': '/tools_and_platforms/recommended_stack/automation_and_iac',
                    'description': 'Automation and IaC tools',
                    'tags': ['tools', 'automation']
                }
            }
        },
        'dimensions': {
            'logical_gaps': {
                'title': 'LOGICAL GAPS (Correctness, Behavior, Edge Cases)',
                'description': 'Testing pyramid + risk surface analysis',
                'frameworks': {
                    'testing_pyramid': {
                        'title': 'Multi-Layer Coverage Analysis',
                        'description': 'Don\'t just measure line coverage—use a coverage stack',
                        'layers': [
                            'Layer 1: Syntactic Coverage (line, branch, MC/DC)',
                            'Layer 2: Semantic Coverage (data flow, path, state machine)',
                            'Layer 3: Property Coverage (mutation, property-based, metamorphic)',
                            'Layer 4: Boundary & Edge Case Coverage'
                        ],
                        'tools_by_language': {
                            'python': ['coverage.py', 'pytest-cov', 'mutmut', 'cosmic-ray', 'hypothesis'],
                            'powershell': ['Pester', 'PSScriptAnalyzer'],
                            'dotnet': ['coverlet', 'Stryker.NET', 'FsCheck'],
                            'javascript': ['nyc', 'c8', 'Stryker', 'fast-check']
                        }
                    },
                    'domain_invariant_mapping': {
                        'title': 'Domain Invariant Mapping (DDD-Inspired Audit)',
                        'description': 'Treat code as an implementation of business rules',
                        'process': [
                            'Extract domain concepts from code and docs',
                            'Identify invariants for each concept',
                            'Map enforcement points in code',
                            'Find enforcement gaps'
                        ],
                        'automation_strategy': [
                            'Use contract testing or design-by-contract tools',
                            'Build invariant monitors that run periodically',
                            'Run as chaos validation'
                        ]
                    },
                    'failure_mode_analysis': {
                        'title': 'Comprehensive Failure Mode Analysis',
                        'description': 'Go beyond "where can this fail" to "what is the blast radius when it fails?"',
                        'automation_tools': ['Chaos Toolkit', 'LitmusChaos', 'Gremlin']
                    }
                }
            },
            'process_workflow_gaps': {
                'title': 'PROCESS / WORKFLOW GAPS',
                'description': 'Value stream + SDLC maturity + toil tracking',
                'frameworks': {
                    'value_stream_mapping': {
                        'title': 'Value Stream Mapping (VSM)',
                        'description': 'Practical implementation for software teams',
                        'measurements': ['Process time', 'Lead time', '% Complete & Accurate', 'Manual vs automated']
                    },
                    'sdlc_maturity': {
                        'title': 'SDLC Maturity Assessment',
                        'description': 'Continuous self-assessment',
                        'tools': ['DORA DevOps Quickcheck', 'Atlassian DevOps Maturity Model', 'CloudBees DevOptics', 'Sleuth', 'LinearB']
                    },
                    'toil_inventory': {
                        'title': 'Toil Inventory & Automation Opportunity Scoring',
                        'description': 'SRE-style toil tracking systematized',
                        'characteristics': ['Manual', 'Repetitive', 'Automatable', 'Tactical', 'Scales linearly']
                    }
                }
            },
            'architectural_gaps': {
                'title': 'ARCHITECTURAL GAPS',
                'description': 'Multi-model architecture assessment',
                'frameworks': {
                    'atam': {
                        'title': 'ATAM (Architecture Tradeoff Analysis Method)',
                        'description': 'Lightweight ATAM for ongoing use',
                        'phases': ['Define quality attribute scenarios', 'Map architecture decisions to scenarios']
                    },
                    'c4_arc42': {
                        'title': 'C4 Model + Arc42 Documentation + Living Architecture',
                        'description': 'Documentation as code + diagram generation',
                        'tools': ['Structurizr', 'arc42', 'Diagrams.py', 'Graphviz', 'Dependabot', 'Renovate']
                    },
                    'quality_models': {
                        'title': 'Quality Models + Technical Debt Quantification',
                        'description': 'ISO/IEC 25010 Software Quality Model',
                        'tools': ['SonarQube', 'Code Climate', 'NDepend']
                    }
                }
            },
            'automation_gaps': {
                'title': 'AUTOMATION GAPS',
                'description': 'CD maturity + DORA + IaC + observability',
                'frameworks': {
                    'cd_maturity': {
                        'title': 'Continuous Delivery Maturity Model',
                        'levels': ['Level 0: Manual/Ad-hoc', 'Level 1: Scripted', 'Level 2: Automated', 'Level 3: Continuous', 'Level 4: Optimized']
                    },
                    'dora_metrics': {
                        'title': 'DORA Metrics + Capability Assessment',
                        'metrics': ['Deployment frequency', 'Lead time for changes', 'Time to restore service', 'Change failure rate'],
                        'capabilities_count': 24
                    },
                    'infrastructure_as_code': {
                        'title': 'Infrastructure-as-Code (IaC) + Policy-as-Code',
                        'description': 'IaC gap analysis and policy enforcement',
                        'tools': ['Terraform', 'Pulumi', 'AWS CDK', 'Open Policy Agent', 'Checkov', 'tfsec']
                    },
                    'observability_maturity': {
                        'title': 'Observability Maturity',
                        'pillars': ['Logs', 'Metrics', 'Traces', 'Context (Metadata)']
                    }
                }
            }
        },
        'unified_framework': {
            'continuous_gap_analysis_workflow': {
                'description': 'Runs automatically, triggers on events',
                'lenses': [
                    {'id': 'LENS_A', 'name': 'Code & Logic Audit', 'trigger': 'On every PR / nightly'},
                    {'id': 'LENS_B', 'name': 'Architecture Assessment', 'trigger': 'Weekly / on major changes'},
                    {'id': 'LENS_C', 'name': 'Process & Workflow Analysis', 'trigger': 'Monthly / quarterly'},
                    {'id': 'LENS_D', 'name': 'Automation & Ops Assessment', 'trigger': 'Monthly / on deployment changes'}
                ],
                'aggregation': 'Merge all gap reports, deduplicate, enrich, score, cluster, generate backlog',
                'remediation': 'Auto-fix, auto-create tickets, auto-suggest PRs, alert owners'
            },
            'gap_registry': {
                'description': 'Central truth store for all gaps',
                'schema': {
                    'gap_id': 'Unique identifier',
                    'title': 'Short description',
                    'type': 'logical|process|architecture|automation',
                    'category': 'Subcategory',
                    'severity': 'critical|high|medium|low',
                    'detected_by': 'List of lenses',
                    'affected_components': 'List of components',
                    'evidence': 'Supporting data',
                    'impact': 'Risk assessment',
                    'remediation': 'Fix details',
                    'status': 'open|in_progress|resolved|wont_fix',
                    'history': 'Audit trail'
                }
            },
            'making_it_continuous': {
                'description': 'Integration points for continuous operation',
                'ci_integration': 'GitHub Actions / GitLab CI / Jenkins',
                'scheduling': 'Cron / event-driven triggers',
                'dashboards': 'Grafana + custom panels',
                'alerting': 'Slack/Teams webhooks + PagerDuty'
            }
        },
        'tools_and_platforms': {
            'recommended_stack': {
                'analysis_and_detection': {
                    'code_quality': ['SonarQube', 'Code Climate', 'DeepSource'],
                    'security': ['Snyk', 'Dependabot', 'Trivy'],
                    'architecture': ['ArchUnit', 'import-linter', 'Structurizr'],
                    'testing': ['pytest + plugins', 'Pester', 'Stryker'],
                    'observability': ['Prometheus + Grafana', 'Datadog', 'New Relic']
                },
                'workflow_and_process': {
                    'vsm_and_metrics': ['LinearB', 'Sleuth', 'Jellyfish'],
                    'dora_tracking': ['CloudBees', 'GitPrime', 'custom dashboards'],
                    'incident_management': ['PagerDuty', 'Opsgenie']
                },
                'automation_and_iac': {
                    'ci_cd': ['GitHub Actions', 'GitLab CI', 'Jenkins X'],
                    'iac': ['Terraform', 'Pulumi', 'AWS CDK'],
                    'policy': ['Open Policy Agent', 'Checkov', 'tfsec']
                },
                'central_orchestration': {
                    'gap_registry': 'Custom (PostgreSQL + REST API)',
                    'dashboard': 'Grafana + custom panels',
                    'alerting': 'Slack/Teams webhooks + PagerDuty'
                }
            }
        },
        'final_synthesis': {
            'answer': 'There is no single named universal framework that covers all four dimensions',
            'unified_approach': [
                'Adopt established frameworks per dimension',
                'Instrument each framework for continuous automated execution',
                'Centralize results in a Gap Registry with common schema',
                'Automate remediation where possible',
                'Make it continuous via scheduled jobs and dashboards'
            ],
            'factory_model': 'Deterministic, observable, self-documenting, continuously improving'
        }
    }

def create_master_splinter_guide_json():
    """Create MASTER_SPLINTER phase plan template guide JSON."""
    return {
        'meta': {
            'doc_id': 'MASTER_SPLINTER_PHASE_PLAN_TEMPLATE_GUIDE',
            'version': '1.0.0',
            'source_file': 'MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md',
            'description': 'AI fill guide for MASTER_SPLINTER_Phase_Plan_Template.yml with decision-elimination rules',
            'notes': [
                'Converted from markdown to structured JSON',
                'Authoritative rules follow DEV_RULES_CORE.md',
                'Decision-elimination ready template guide'
            ]
        },
        'index': {
            'metadata': {
                'DOC_ID': {
                    'path': '/meta/doc_id',
                    'description': 'Unique identifier for this guide',
                    'tags': ['meta', 'identifier']
                },
                'VERSION': {
                    'path': '/meta/version',
                    'description': 'Guide version number',
                    'tags': ['meta', 'version']
                }
            },
            'sections': {
                'S_FILL_GUIDE': {
                    'path': '/fill_guide',
                    'description': 'Instructions for filling each template section',
                    'tags': ['section', 'guide']
                },
                'S_DECISION_RULES': {
                    'path': '/decision_elimination_rules',
                    'description': 'Decision-elimination rules from UTE docs',
                    'tags': ['section', 'rules']
                },
                'S_QUICK_USAGE': {
                    'path': '/quick_usage_pattern',
                    'description': 'Quick usage pattern for AI/tools',
                    'tags': ['section', 'usage']
                },
                'S_UTE_ALIGNMENT': {
                    'path': '/ute_alignment',
                    'description': 'Alignment with UTE playbooks',
                    'tags': ['section', 'alignment']
                },
                'S_WORKSTREAM_SYNC': {
                    'path': '/workstream_sync',
                    'description': 'Workstream sync to GitHub PM',
                    'tags': ['section', 'sync']
                },
                'S_NO_STOP_MODE': {
                    'path': '/no_stop_mode',
                    'description': 'Instructions to finish all tasks without stopping',
                    'tags': ['section', 'resilience']
                }
            },
            'features': {
                'F_NO_STOP': {
                    'path': '/workstream_sync/no_stop_mode',
                    'description': 'Critical no-stop mode feature',
                    'tags': ['feature', 'resilience']
                },
                'F_SUMMARY_REPORT': {
                    'path': '/workstream_sync/summary_report_template',
                    'description': 'Summary report generation',
                    'tags': ['feature', 'reporting']
                },
                'F_EXTENSIONS': {
                    'path': '/workstream_sync/extensions_field_usage',
                    'description': 'Extensions field configuration',
                    'tags': ['feature', 'extensions']
                }
            }
        },
        'fill_guide': {
            'description': 'How to fill each section of MASTER_SPLINTER_Phase_Plan_Template.yml',
            'sections': {
                'doc_id_and_version': 'Keep existing values unless versioning the template',
                'phase_identity': {
                    'fields': ['phase_id', 'workstream_id', 'title', 'summary', 'objective', 'phase_type', 'status', 'estimate_hours', 'gh_item_id', 'tags'],
                    'status_enum': ['not_started', 'in_progress', 'planned', 'blocked', 'done', 'abandoned']
                },
                'dag_and_dependencies': {
                    'fields': ['depends_on', 'may_run_parallel_with', 'parallel_group', 'is_critical_path']
                },
                'scope_and_modules': {
                    'fields': ['repo_root', 'modules', 'file_scope', 'forbidden_paths', 'worktree_strategy']
                },
                'environment_and_tools': {
                    'fields': ['target_os', 'shell', 'lang', 'python_constraints', 'required_services', 'config_files', 'ai_operators', 'tool_profiles']
                },
                'execution_profile': {
                    'fields': ['prompt_template_id', 'run_mode', 'max_runtime', 'concurrency_limits', 'retry_policy']
                },
                'pre_flight_checks': {
                    'required_fields': ['id', 'description', 'when', 'command', 'success_pattern', 'on_fail']
                },
                'execution_plan_steps': {
                    'required_fields': ['id', 'name', 'operation_kind', 'pattern_ids', 'description', 'tool_id', 'inputs', 'expected_outputs', 'requires_human_confirmation']
                },
                'fix_loop_and_circuit_breakers': {
                    'fields': ['enable', 'applies_to', 'config_ref', 'defaults', 'behavior']
                },
                'expected_artifacts': {
                    'types': ['patch', 'log', 'doc', 'db'],
                    'required_fields': ['paths', 'must_exist']
                },
                'acceptance_tests': {
                    'required_fields': ['id', 'description', 'command', 'success_pattern', 'must_pass']
                },
                'completion_gate': {
                    'fields': ['rules_booleans', 'manual_override_controls']
                },
                'observability_and_metrics': {
                    'fields': ['event_tags', 'metrics_toggles']
                },
                'governance_and_constraints': {
                    'fields': ['anti_patterns_blocked', 'notes_for_operators']
                },
                'extensions': {
                    'custom_fields': 'Free-form; leave {} if unused'
                }
            }
        },
        'decision_elimination_rules': {
            'description': 'Apply from UTE docs',
            'rules': [
                'Decide once, apply many: keep structure unchanged; only fill variable fields',
                'Ground truth: success only when declared artifacts exist, commands/tests match success patterns, and git scope is limited to allowed paths',
                'Scope enforcement: all edits constrained to file_scope; never write to forbidden_paths',
                'Verification: rely on pre_flight + acceptance tests + completion_gate',
                'Self-heal policy: prefer deterministic fixes already allowed by tools',
                'Parallelism: only use may_run_parallel_with/max_parallel_steps when scopes dont overlap',
                'Stop on ambiguity: leave clear placeholder tokens rather than guessing'
            ]
        },
        'quick_usage_pattern': {
            'description': 'For AI/Tools',
            'steps': [
                'Load template + this guide; fill every required field',
                'Pre-commit sanity: git status --porcelain (expect clean)',
                'When adding steps/checks/tests, always include: command + success_pattern + must_pass/must_exist',
                'When integrating with GitHub Project sync, keep gh_item_id: null until sync script writes it',
                'Validation: run python -m jsonschema or YAML parse check'
            ]
        },
        'ute_alignment': {
            'description': 'Alignment with UTE playbooks',
            'playbooks': [
                'Decision Elimination Playbook: pre-answer structure, verification, scope',
                'Execution Acceleration Guide: treat template as pre-decided plan',
                'Pattern Recognition writeup: reuse invariant ordering and fields'
            ]
        },
        'workstream_sync': {
            'description': 'Sync workstreams to GitHub Project Manager',
            'quick_start_command': 'python scripts/sync_workstreams_to_github.py',
            'options': {
                'custom_branch': '--branch feature/my-ws-sync',
                'dry_run': '--dry-run'
            },
            'what_it_does': [
                'Creates feature branch (auto-named with timestamp)',
                'Commits each workstream (separate commit per file)',
                'Pushes to remote',
                'Generates summary report (uses template: templates/workstream_summary_report.md)'
            ],
            'no_stop_mode': {
                'description': 'Critical feature - finish all tasks without stopping',
                'guarantees': [
                    'Continues through errors',
                    'Collects all errors and successes',
                    'Always generates final report',
                    'Never halts on individual workstream failures',
                    'Provides complete execution summary'
                ],
                'benefit': 'Get complete picture of all workstreams, even if some fail'
            },
            'summary_report_template': {
                'location': 'templates/workstream_summary_report.md',
                'variables': ['TIMESTAMP', 'FEATURE_BRANCH', 'TOTAL_WORKSTREAMS', 'SUCCESS_COUNT', 'FAILED_COUNT', 'COMMITS_CREATED', 'ERROR_LOG']
            },
            'extensions_field_usage': {
                'workstream_sync': {
                    'enabled': True,
                    'auto_commit': True,
                    'feature_branch_pattern': 'feature/ws-sync-${timestamp}',
                    'github_project_integration': True,
                    'no_stop_mode': True,
                    'summary_report_template': 'templates/workstream_summary_report.md',
                    'sync_script': 'scripts/sync_workstreams_to_github.py'
                },
                'execution_resilience': {
                    'continue_on_error': True,
                    'error_collection_mode': True,
                    'final_report_on_completion': True
                }
            }
        },
        'no_stop_mode': {
            'core_principle': 'NEVER STOP ON ERRORS',
            'execution_model': [
                'Error Collection: Record errors but continue execution',
                'Success Tracking: Track successful operations independently',
                'Final Reporting: Always produce complete summary at end',
                'No Silent Failures: All errors logged and reported'
            ],
            'implementation_pattern': {
                'description': 'Process all items pattern',
                'pseudo_code': 'for item: try process, catch errors, continue; always generate final report'
            },
            'apply_to_phase_execution': {
                'description': 'Ensure each step has error handling that logs but doesn\'t abort',
                'requirements': [
                    'Contributes to final summary report',
                    'Respects execution_resilience.continue_on_error: true'
                ]
            },
            'validation_commands': {
                'acc_resilience_check': {
                    'description': 'Verify no-stop mode is enabled',
                    'command': 'python -c "import yaml; assert yaml.safe_load(open(phase_file))..."',
                    'must_pass': True
                }
            }
        }
    }

def main():
    """Convert both files to JSON."""
    print('Converting files to indexed JSON...')
    print()
    
    # Create gap framework JSON
    gap_framework = create_gap_framework_json()
    gap_file = Path('prompts/COMPREHENSIVE_GAP_FINDING_FRAMEWORK.json')
    with open(gap_file, 'w', encoding='utf-8') as f:
        json.dump(gap_framework, f, indent=2, ensure_ascii=False)
    
    gap_index_count = sum(len(v) for v in gap_framework['index'].values())
    print(f'Created {gap_file.name}')
    print(f'  Index entries: {gap_index_count}')
    print(f'  Dimensions: 4')
    print(f'  Frameworks: 13')
    print()
    
    # Create MASTER_SPLINTER guide JSON
    guide = create_master_splinter_guide_json()
    guide_file = Path('prompts/MASTER_SPLINTER_PHASE_PLAN_TEMPLATE_GUIDE.json')
    with open(guide_file, 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    guide_index_count = sum(len(v) for v in guide['index'].values())
    print(f'Created {guide_file.name}')
    print(f'  Index entries: {guide_index_count}')
    print(f'  Sections: 6')
    print(f'  Features: 3')
    print()
    
    print('Conversion complete!')
    print(f'Total index entries: {gap_index_count + guide_index_count}')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
