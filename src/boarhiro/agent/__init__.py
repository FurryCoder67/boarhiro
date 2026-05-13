"""
Agent core for BOARHIRO.

Provides the agent worker, lifecycle management, and orchestration.
Inspired by Buildkite Agent's agent package.
"""

from .config import AgentConfig, WorkerConfig
from .worker import AgentWorker

__all__ = ["AgentConfig", "WorkerConfig", "AgentWorker"]
