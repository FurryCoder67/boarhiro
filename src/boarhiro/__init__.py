"""
BOARHIRO: A transformer-based neural AI that trains itself continuously.

Provides core modules for agent orchestration, inference, and training.
"""

# Agent infrastructure
from boarhiro.agent import AgentWorker
from boarhiro.agent.lifecycle import AgentLifecycle

# Configuration
from boarhiro.config import AgentConfig, WorkerConfig

# Logging
from boarhiro.logger import get_logger, StructuredLogger, configure_logging, LogLevel

# API client
from boarhiro.api import ServerClient

# Error types
from boarhiro.utils import BoarhiroError, ConfigError, ProcessError

# Interface
from boarhiro.interface import run_cli

__all__ = [
    # Agent
    "AgentWorker",
    "AgentLifecycle",
    # Config
    "AgentConfig",
    "WorkerConfig",
    # Logging
    "get_logger",
    "StructuredLogger",
    "configure_logging",
    "LogLevel",
    # API
    "ServerClient",
    # Errors
    "BoarhiroError",
    "ConfigError",
    "ProcessError",
    # Interface
    "run_cli",
]

__version__ = "0.2.0"  # Updated with agent architecture
__author__ = "FurryCoder67"
__license__ = "MIT"
