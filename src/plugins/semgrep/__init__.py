"""semgrep Plugin - Compatibility Shim

This plugin has been moved to error/plugins/semgrep/
This shim provides backward compatibility during the refactor.
"""

from error.plugins.semgrep.plugin import *  # noqa: F401, F403
