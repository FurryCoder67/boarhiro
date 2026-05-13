"""
Agent configuration wrapper.

Combines AgentConfig and WorkerConfig for unified agent setup.
"""

from dataclasses import dataclass
from typing import Optional

from boarhiro.config import AgentConfig, WorkerConfig


@dataclass
class AgentStartConfig:
    """Complete configuration for starting an agent."""

    agent: AgentConfig
    worker: WorkerConfig

    # Statistics and telemetry
    enable_feature_reporting: bool = True
    telemetry_endpoint: Optional[str] = None

    def __post_init__(self):
        """Validate combined configuration."""
        if not self.agent or not self.worker:
            raise ValueError("Both agent and worker configs must be provided")
