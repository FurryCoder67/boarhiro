"""
Configuration management for BOARHIRO agent.

Provides struct-like configuration patterns inspired by Buildkite Agent.
Uses dataclasses for clean, type-hinted configuration objects.
"""

from .agent_config import AgentConfig, WorkerConfig

__all__ = ["AgentConfig", "WorkerConfig"]
