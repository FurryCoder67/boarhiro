"""
Structured logging implementation for BOARHIRO.

Supports both plain text and JSON output. JSON output is available
when --json-logs flag is enabled, otherwise defaults to readable text.
"""

import json
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class StructuredLogger:
    """Structured logger supporting both text and JSON output."""

    def __init__(self, name: str, json_output: bool = False, debug: bool = False):
        """
        Initialize logger.

        Args:
            name: Logger name (e.g., "trainer", "server", "agent")
            json_output: If True, output JSON format; otherwise plain text
            debug: If True, include DEBUG level messages
        """
        self.name = name
        self.json_output = json_output
        self.debug = debug

    def _log(
        self,
        level: LogLevel,
        message: str,
        **kwargs: Any
    ) -> None:
        """
        Internal logging method.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional structured fields
        """
        # Skip debug messages if not in debug mode
        if level == LogLevel.DEBUG and not self.debug:
            return

        timestamp = datetime.utcnow().isoformat() + "Z"

        if self.json_output:
            # JSON structured log
            log_entry = {
                "timestamp": timestamp,
                "level": level.value,
                "logger": self.name,
                "message": message,
                **kwargs
            }
            print(json.dumps(log_entry), file=sys.stderr)
        else:
            # Plain text log
            fields = " ".join(f"{k}={v}" for k, v in kwargs.items())
            prefix = f"[{timestamp}] [{level.value}] [{self.name}]"
            if fields:
                output = f"{prefix} {message} ({fields})"
            else:
                output = f"{prefix} {message}"
            print(output, file=sys.stderr)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)

    def fatal(self, message: str, **kwargs: Any) -> None:
        """Log fatal message."""
        self._log(LogLevel.FATAL, message, **kwargs)


# Global logger instances cache
_loggers: Dict[str, StructuredLogger] = {}
_json_output = False
_debug_mode = False


def configure_logging(json_output: bool = False, debug: bool = False) -> None:
    """
    Configure global logging behavior.

    Args:
        json_output: Enable JSON output for all loggers
        debug: Enable debug level logging
    """
    global _json_output, _debug_mode
    _json_output = json_output
    _debug_mode = debug


def get_logger(name: str) -> StructuredLogger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name

    Returns:
        StructuredLogger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(
            name, json_output=_json_output, debug=_debug_mode
        )
    return _loggers[name]
