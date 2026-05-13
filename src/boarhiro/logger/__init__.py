"""
Structured logging for BOARHIRO.

Provides both plain text and JSON structured logging capabilities,
inspired by Buildkite Agent's logging architecture.
"""

from .structured import StructuredLogger, LogLevel, get_logger, configure_logging

__all__ = ["StructuredLogger", "LogLevel", "get_logger", "configure_logging"]
