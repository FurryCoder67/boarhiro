"""
Core agent worker implementation.

The AgentWorker orchestrates job polling (future), execution, and reporting.
Currently focused on maintaining boarhiro's chat interface and training loop.
"""

import asyncio
from typing import Optional

from boarhiro.config import AgentConfig, WorkerConfig
from boarhiro.logger import get_logger
from boarhiro.utils import ProcessError


class AgentWorker:
    """
    Core agent worker class.

    Manages job lifecycle, worker state, and communication with services.
    """

    def __init__(self, agent_config: AgentConfig, worker_config: WorkerConfig):
        """
        Initialize agent worker.

        Args:
            agent_config: Agent configuration
            worker_config: Worker configuration
        """
        self.agent_config = agent_config
        self.worker_config = worker_config
        self.logger = get_logger(f"worker-{worker_config.worker_id}")

        self._is_running = False
        self._current_job = None
        self._job_count = 0
        self._success_count = 0

    async def start(self) -> None:
        """
        Start the agent worker.

        Sets up background tasks, initializes model, and begins operation.
        Currently maintains boarhiro's existing behavior while preparing
        infrastructure for future job polling.
        """
        if self._is_running:
            self.logger.warning("Worker already running")
            return

        self._is_running = True
        self.logger.info("Agent worker starting", agent=self.agent_config.agent_name)

        try:
            # Future: uncomment when ready to enable job polling
            # await self._polling_loop()
            pass
        except Exception as e:
            self.logger.error("Worker error", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the agent worker gracefully."""
        self._is_running = False
        self.logger.info("Agent worker stopped")

    async def _polling_loop(self) -> None:
        """
        Poll for jobs (future implementation).

        When enabled, will poll the job server for new jobs.
        Currently a placeholder for future Buildkite integration.
        """
        self.logger.debug("Job polling loop starting")

        while self._is_running:
            try:
                # TODO: Poll for jobs
                # jobs = await self._poll_jobs()
                # for job in jobs:
                #     await self._execute_job(job)

                await asyncio.sleep(self.worker_config.job_poll_interval_seconds)
            except Exception as e:
                self.logger.error("Polling error", error=str(e))
                await asyncio.sleep(self.worker_config.retry_backoff_seconds)

    def get_status(self) -> dict:
        """Get current worker status."""
        return {
            "worker_id": self.worker_config.worker_id,
            "is_running": self._is_running,
            "jobs_completed": self._job_count,
            "jobs_successful": self._success_count,
            "current_job": self._current_job,
        }
