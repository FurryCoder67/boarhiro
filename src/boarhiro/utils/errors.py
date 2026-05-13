"""
Error hierarchy for BOARHIRO.

Provides typed exceptions for different failure modes,
inspired by Buildkite Agent's error handling patterns.
"""


class BoarhiroError(Exception):
    """Base exception for all BOARHIRO errors."""

    def __init__(self, message: str, context: dict = None):
        """
        Initialize exception with optional context.

        Args:
            message: Error message
            context: Additional context (will be logged)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """String representation includes context if available."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class ConfigError(BoarhiroError):
    """Configuration validation or loading error."""
    pass


class ProcessError(BoarhiroError):
    """Process execution or management error."""
    pass


class ModelError(BoarhiroError):
    """Model loading, training, or inference error."""
    pass


class ServerError(BoarhiroError):
    """Server communication or operation error."""
    pass


class JobError(BoarhiroError):
    """Job execution or management error."""
    pass
