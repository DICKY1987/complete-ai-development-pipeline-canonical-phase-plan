"""Logger protocol shim for structured logging tests."""


class Logger:
    """Minimal logger interface."""

    def info(self, message: str, **kwargs):
        raise NotImplementedError

    def error(self, message: str, **kwargs):
        raise NotImplementedError

    def job_event(self, job_id: str, status: str, **kwargs):
        raise NotImplementedError


__all__ = ["Logger"]
