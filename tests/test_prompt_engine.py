"""
Unit tests for Prompt Engine V1.1
"""
# DOC_ID: DOC-TEST-TESTS-TEST-PROMPT-ENGINE-101
# DOC_ID: DOC-TEST-TESTS-TEST-PROMPT-ENGINE-062
import pytest
from pathlib import Path
from modules.core_engine.m010001_prompt_engine import (
    PromptEngine, Classification, PromptContext
)


@pytest.fixture
def prompt_engine(tmp_path):
    """Create PromptEngine instance with temp directory"""
    template_dir = tmp_path / "templates"
    return PromptEngine(template_dir=str(template_dir))


@pytest.fixture
def sample_bundle():
    """Create sample workstream bundle"""
    return {
        'id': 'ws-test-001',
        'openspec_change': 'OS-123',
        'ccpm_issue': 456,
        'gate': 1,
        'files_scope': [
            'src/module.py',
            'src/utils.py'
        ],
        'files_create': [
            'tests/test_module.py'
        ],
        'tasks': [
            'Refactor module.py for clarity',
            'Add unit tests',
            'Update documentation'
        ],
        'acceptance_tests': [
            'pytest -q tests/test_module.py',
            'ruff check src/'
        ],
        'tool': 'aider',
        'metadata': {
            'owner': 'dev@example.com'
        }
    }


@pytest.fixture
def prompt_context(tmp_path):
    """Create sample prompt context"""
    return PromptContext(
        target_app='universal',
        repo_path=str(tmp_path / 'repo'),
        worktree_path=str(tmp_path / 'worktree')
    )


def test_classification_creation():
    """Test Classification dataclass"""
    c = Classification(
        complexity='moderate',
        quality='standard',
        domain='code',
        operation='refactor'
    )
    
    assert c.complexity == 'moderate'
    assert c.quality == 'standard'
    assert c.domain == 'code'
    assert c.operation == 'refactor'


def test_prompt_context_creation(tmp_path):
    """Test PromptContext dataclass"""
    ctx = PromptContext(
        target_app='aider',
        repo_path=str(tmp_path / 'repo'),
        worktree_path=str(tmp_path / 'worktree'),
        additional_context={'key': 'value'}
    )
    
    assert ctx.target_app == 'aider'
    assert ctx.additional_context == {'key': 'value'}


def test_infer_classification_simple(prompt_engine):
    """Test classification inference for simple workstream"""
    bundle = {
        'files_scope': ['src/file.py'],
        'tasks': ['Make small change'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.complexity == 'simple'
    assert classification.quality == 'standard'


def test_infer_classification_moderate(prompt_engine):
    """Test classification inference for moderate workstream"""
    bundle = {
        'files_scope': ['src/a.py', 'src/b.py', 'src/c.py'],
        'tasks': ['Task 1', 'Task 2', 'Task 3'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.complexity == 'moderate'


def test_infer_classification_complex(prompt_engine):
    """Test classification inference for complex workstream"""
    bundle = {
        'files_scope': [f'src/file{i}.py' for i in range(8)],
        'tasks': ['Task 1', 'Task 2', 'Task 3', 'Task 4'],
        'gate': 2
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.complexity == 'complex'
    assert classification.quality == 'production'  # gate >= 2


def test_infer_classification_domain_docs(prompt_engine):
    """Test domain inference for documentation"""
    bundle = {
        'files_scope': ['README.md', 'docs/guide.md'],
        'tasks': ['Update documentation'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.domain == 'docs'


def test_infer_classification_domain_tests(prompt_engine):
    """Test domain inference for tests"""
    bundle = {
        'files_scope': ['tests/test_module.py', 'tests/test_utils.py'],
        'tasks': ['Add tests'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.domain == 'tests'


def test_infer_classification_operation_refactor(prompt_engine):
    """Test operation inference for refactor"""
    bundle = {
        'files_scope': ['src/module.py'],
        'tasks': ['Refactor for clarity', 'Improve structure'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.operation == 'refactor'


def test_infer_classification_operation_bugfix(prompt_engine):
    """Test operation inference for bugfix"""
    bundle = {
        'files_scope': ['src/module.py'],
        'tasks': ['Fix bug in calculation', 'Address edge case'],
        'gate': 1
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.operation == 'bugfix'


def test_infer_classification_explicit(prompt_engine):
    """Test using explicit classification from metadata"""
    bundle = {
        'files_scope': ['src/module.py'],
        'tasks': ['Task'],
        'gate': 1,
        'metadata': {
            'classification': {
                'complexity': 'enterprise',
                'quality': 'production',
                'domain': 'analysis',
                'operation': 'feature'
            }
        }
    }
    
    classification = prompt_engine._infer_classification(bundle)
    
    assert classification.complexity == 'enterprise'
    assert classification.quality == 'production'
    assert classification.domain == 'analysis'
    assert classification.operation == 'feature'


def test_infer_role_simple_code(prompt_engine):
    """Test role inference for simple code work"""
    classification = Classification(
        complexity='simple',
        quality='standard',
        domain='code',
        operation='refactor'
    )
    
    role = prompt_engine._infer_role(classification)
    
    assert 'Software Engineer' in role
    assert 'refactoring' in role


def test_infer_role_senior_docs(prompt_engine):
    """Test role inference for complex documentation"""
    classification = Classification(
        complexity='complex',
        quality='production',
        domain='docs',
        operation='feature'
    )
    
    role = prompt_engine._infer_role(classification)
    
    assert 'Senior' in role
    assert 'Technical Writer' in role


def test_infer_role_principal_code(prompt_engine):
    """Test role inference for enterprise-level work"""
    classification = Classification(
        complexity='enterprise',
        quality='production',
        domain='code',
        operation='bugfix'
    )
    
    role = prompt_engine._infer_role(classification)
    
    assert 'Principal' in role
    assert 'Software Engineer' in role
    assert 'debugging' in role


def test_select_template_aider(prompt_engine):
    """Test template selection for Aider"""
    template = prompt_engine._select_template('aider')
    assert template == 'workstream_v1.1_aider.txt.j2'


def test_select_template_codex(prompt_engine):
    """Test template selection for Codex"""
    template = prompt_engine._select_template('codex')
    assert template == 'workstream_v1.1_codex.txt.j2'


def test_select_template_universal(prompt_engine):
    """Test template selection for universal"""
    template = prompt_engine._select_template('universal')
    assert template == 'workstream_v1.1_universal.txt.j2'


def test_select_template_default(prompt_engine):
    """Test template selection default"""
    template = prompt_engine._select_template('unknown')
    assert template == 'workstream_v1.1_universal.txt.j2'


def test_render_fallback(prompt_engine, sample_bundle, prompt_context):
    """Test fallback rendering when templates unavailable"""
    classification = Classification(
        complexity='moderate',
        quality='standard',
        domain='code',
        operation='refactor'
    )
    role = 'experienced Software Engineer specializing in code refactoring'
    
    rendered = prompt_engine._render_fallback(
        sample_bundle,
        prompt_context,
        classification,
        role
    )
    
    assert 'WORKSTREAM: ws-test-001' in rendered
    assert 'moderate' in rendered
    assert 'OS-123' in rendered
    assert 'src/module.py' in rendered
    assert 'Refactor module.py for clarity' in rendered
    assert 'pytest -q tests/test_module.py' in rendered


def test_render_v11_fallback(prompt_engine, sample_bundle, prompt_context):
    """Test render_v11 uses fallback when templates don't exist"""
    rendered = prompt_engine.render_v11(sample_bundle, prompt_context)
    
    # Should use fallback
    assert 'WORKSTREAM: ws-test-001' in rendered
    assert 'OS-123' in rendered
    assert 'src/module.py' in rendered


def test_render_v11_ascii_only(prompt_engine, sample_bundle, prompt_context):
    """Test that rendered output is ASCII-only"""
    # Add non-ASCII characters to bundle
    sample_bundle['tasks'] = ['Fix issue with café ☕ and naïve']
    
    rendered = prompt_engine.render_v11(sample_bundle, prompt_context)
    
    # Should be ASCII (non-ASCII replaced with ?)
    assert rendered.isascii()


def test_render_v11_empty_lists(prompt_engine, prompt_context):
    """Test rendering with empty lists"""
    bundle = {
        'id': 'ws-empty',
        'openspec_change': 'OS-001',
        'ccpm_issue': 1,
        'gate': 1,
        'files_scope': [],
        'files_create': [],
        'tasks': [],
        'acceptance_tests': [],
        'tool': 'aider'
    }
    
    rendered = prompt_engine.render_v11(bundle, prompt_context)
    
    assert 'ws-empty' in rendered


def test_classification_all_combinations(prompt_engine):
    """Test various combinations of bundle attributes"""
    test_cases = [
        # (file_count, task_count, gate, expected_complexity, expected_quality)
        (1, 1, 1, 'simple', 'standard'),
        (2, 3, 1, 'simple', 'standard'),
        (3, 4, 2, 'moderate', 'production'),
        (6, 5, 1, 'complex', 'standard'),
        (12, 10, 3, 'enterprise', 'production'),
    ]
    
    for file_count, task_count, gate, exp_complexity, exp_quality in test_cases:
        bundle = {
            'files_scope': [f'file{i}.py' for i in range(file_count)],
            'tasks': [f'Task {i}' for i in range(task_count)],
            'gate': gate
        }
        
        classification = prompt_engine._infer_classification(bundle)
        
        assert classification.complexity == exp_complexity, \
            f"Failed for {file_count} files, {task_count} tasks"
        assert classification.quality == exp_quality, \
            f"Failed quality for gate={gate}"


def test_prompt_engine_init_creates_directory(tmp_path):
    """Test that PromptEngine creates template directory if not exists"""
    template_dir = tmp_path / "nonexistent" / "templates"
    assert not template_dir.exists()
    
    engine = PromptEngine(template_dir=str(template_dir))
    
    assert engine.template_dir.exists()
    assert engine.template_dir.is_dir()
