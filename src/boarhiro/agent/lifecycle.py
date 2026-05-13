"""
Agent lifecycle management.

Handles startup, shutdown, signal handling, and graceful termination.
"""

import asyncio
import signal
import sys
from typing import Optional, Callable

from boarhiro.logger import get_logger


class AgentLifecycle:
    """Manages agent startup, shutdown, and signal handling."""

    def __init__(self):
        """Initialize lifecycle manager."""
        self.logger = get_logger("lifecycle")
        self._shutdown_handlers = []
        self._is_shutting_down = False

    def register_shutdown_handler(self, handler: Callable) -> None:
        """
        Register a callback to be called on shutdown.

        Args:
            handler: Async callable to execute during shutdown
        """
        self._shutdown_handlers.append(handler)

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        # Handle different signals on Windows vs Unix
        try:
            if sys.platform == "win32":
                # Windows: handle SIGINT (Ctrl+C) and SIGTERM
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            else:
                # Unix: handle more signals
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                    signal.signal(sig, self._signal_handler)
        except (ValueError, OSError) as e:
            self.logger.warning("Failed to setup signal handlers", error=str(e))

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle received signals."""
        if self._is_shutting_down:
            self.logger.warning("Already shutting down, ignoring signal")
            return

        self._is_shutting_down = True
        self.logger.info("Received signal, initiating shutdown", signal=signum)

    async def shutdown(self) -> None:
        """Execute shutdown sequence."""
        if self._is_shutting_down:
            self.logger.debug("Shutdown already in progress")
            return

        self._is_shutting_down = True
        self.logger.info("Executing shutdown handlers")

        for handler in self._shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                self.logger.error("Shutdown handler error", error=str(e))

        self.logger.info("Shutdown complete")

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been initiated."""
        return self._is_shutting_down
