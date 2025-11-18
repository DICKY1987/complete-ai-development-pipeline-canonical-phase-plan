"""gitleaks Plugin - Compatibility Shim

This plugin has been moved to error/plugins/gitleaks/
This shim provides backward compatibility during the refactor.
"""

from error.plugins.gitleaks.plugin import *  # noqa: F401, F403
