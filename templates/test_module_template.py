"""Tests for {{module_name}}

DOC_ID_TEMPLATE: DOC-TEST-{{module_id}}-001
Created: {{created_date}}


DOC_ID: DOC-TEST-TEMPLATES-TEST-MODULE-TEMPLATE-348
"""

from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from {{module_path}} import {{imports}}

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def {{fixture_name}}():
    """{{fixture_description}}"""
    {{fixture_setup}}
    yield {{fixture_object}}
    {{fixture_teardown}}


{% for fixture in additional_fixtures %}
@pytest.fixture
def {{fixture.name}}({{fixture.dependencies}}):
    """{{fixture.description}}"""
    {{fixture.setup}}
    yield {{fixture.object}}
    {% if fixture.teardown %}{{fixture.teardown}}{% endif %}


{% endfor %}

# ============================================================================
# Unit Tests
# ============================================================================

{% for test in unit_tests %}
def test_{{test.name}}({{test.fixtures}}):
    """{{test.description}}

    {{test.detailed_description}}
    """
    # Given
    {{test.given}}

    # When
    {{test.when}}

    # Then
    {{test.then}}
    {% if test.cleanup %}

    # Cleanup
    {{test.cleanup}}
    {% endif %}


{% endfor %}

# ============================================================================
# Integration Tests
# ============================================================================

{% if integration_tests %}
@pytest.mark.integration
class TestIntegration{{module_name}}:
    """Integration tests for {{module_name}}"""

    {% for test in integration_tests %}
    def test_{{test.name}}(self, {{test.fixtures}}):
        """{{test.description}}"""
        # Given
        {{test.given}}

        # When
        {{test.when}}

        # Then
        {{test.then}}

    {% endfor %}
{% endif %}

# ============================================================================
# Error Handling Tests
# ============================================================================

{% if error_tests %}
class TestErrorHandling{{module_name}}:
    """Test error handling in {{module_name}}"""

    {% for test in error_tests %}
    def test_{{test.name}}(self, {{test.fixtures}}):
        """{{test.description}}"""
        # Given
        {{test.given}}

        # When/Then
        with pytest.raises({{test.exception}}{% if test.message %}, match="{{test.message}}"{% endif %}):
            {{test.when}}

    {% endfor %}
{% endif %}

# ============================================================================
# Edge Case Tests
# ============================================================================

{% if edge_case_tests %}
@pytest.mark.parametrize("{{edge_case_params}}", [
    {% for case in edge_case_values %}
    {{case}},
    {% endfor %}
])
def test_{{edge_case_name}}({{edge_case_fixtures}}, {{edge_case_params}}):
    """{{edge_case_description}}"""
    # Given
    {{edge_case_given}}

    # When
    {{edge_case_when}}

    # Then
    {{edge_case_then}}
{% endif %}
