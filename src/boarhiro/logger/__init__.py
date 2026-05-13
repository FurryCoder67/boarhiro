"""
Structured logging for BOARHIRO.

Provides both plain text and JSON structured logging capabilities,
inspired by Buildkite Agent's logging architecture.
"""

from .structured import StructuredLogger, LogLevel, get_logger

__all__ = ["StructuredLogger", "LogLevel", "get_logger"]
