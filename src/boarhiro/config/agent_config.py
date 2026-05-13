"""
Agent and Worker configuration objects.

Mirrors Buildkite Agent's struct-based configuration pattern using Python dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class AgentConfig:
    """Core agent configuration."""

    # Agent identity
    agent_name: str = "boarhiro-agent"
    agent_token: Optional[str] = None

    # Paths
    build_path: str = "/tmp/boarhiro-builds"
    model_path: str = "boarhiro_brain.pt"
    data_path: str = "data/input.txt"

    # Server settings
    server_url: str = "http://localhost:5000"
    server_port: int = 5000

    # Agent capabilities
    tags: Dict[str, str] = field(default_factory=lambda: {"os": "local", "arch": "cpu"})
    metadata: Dict[str, str] = field(default_factory=dict)

    # Feature flags
    enable_training: bool = True
    enable_job_polling: bool = False  # Future: when Buildkite integration is enabled
    no_hunter: bool = False  # Disable data hunting during training

    # Debugging
    debug: bool = False
    json_logs: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.agent_name:
            raise ValueError("agent_name cannot be empty")
        if not self.build_path:
            raise ValueError("build_path cannot be empty")


@dataclass
class WorkerConfig:
    """Worker pool configuration."""

    # Worker identity
    worker_id: str = "worker-0"

    # Concurrency
    max_concurrent_jobs: int = 1  # Serial execution for now
    job_poll_interval_seconds: float = 5.0

    # Timeouts
    job_execution_timeout_seconds: float = 3600.0  # 1 hour
    heartbeat_interval_seconds: float = 30.0

    # Retry policy
    max_retries: int = 3
    retry_backoff_seconds: float = 5.0

    # Output
    capture_stdout: bool = True
    stream_logs: bool = True

    def __post_init__(self):
        """Validate worker configuration."""
        if self.max_concurrent_jobs < 1:
            raise ValueError("max_concurrent_jobs must be at least 1")
        if self.job_poll_interval_seconds <= 0:
            raise ValueError("job_poll_interval_seconds must be positive")
