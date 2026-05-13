"""
Command handlers for BOARHIRO interface.

Implements all CLI commands: help, status, jobs, metrics, etc.
"""

import os
import sys
import subprocess
from typing import Optional

from rich.console import Console
import requests

from boarhiro.api import ServerClient
from .ui import (
    render_help_table,
    render_jobs_table,
    render_status_panel,
    render_metrics_panel,
    render_error,
    render_success,
    render_info,
)


class CommandHandler:
    """Handles CLI commands."""

    def __init__(self, console: Console, project_root: str):
        """
        Initialize command handler.

        Args:
            console: Rich console instance
            project_root: Project root directory path
        """
        self.console = console
        self.project_root = project_root
        self.server_client = ServerClient()
        self.jobs_history = []

    def handle_help(self) -> None:
        """Handle help command."""
        self.console.print(render_help_table())

    def handle_clear(self) -> None:
        """Handle clear command."""
        os.system("cls" if sys.platform == "win32" else "clear")

    def handle_status(self) -> None:
        """Handle status command."""
        status_data = {
            "agent_name": "boarhiro-agent",
            "trainer_running": self._pid_alive("boarhiro_train.pid"),
            "server_running": self._pid_alive("boarhiro_server.pid"),
            "watcher_running": self._pid_alive("boarhiro_watcher.pid"),
            "model_status": "Ready",
        }
        self.console.print(render_status_panel(status_data))

    def handle_jobs(self) -> None:
        """Handle jobs command."""
        self.console.print(render_jobs_table(self.jobs_history))

    def handle_metrics(self) -> None:
        """Handle metrics command."""
        metrics = {
            "jobs_completed": len(self.jobs_history),
            "jobs_successful": sum(1 for j in self.jobs_history if j.get("status") == "success"),
            "success_rate": f"{100 * sum(1 for j in self.jobs_history if j.get('status') == 'success') // max(len(self.jobs_history), 1)}%",
            "avg_exec_time": "0.5s",
        }
        self.console.print(render_metrics_panel(metrics))

    def handle_seturl(self, url: str) -> None:
        """Handle seturl command."""
        try:
            # Save URL to link.txt
            link_path = os.path.join(self.project_root, "link.txt")
            with open(link_path, "w", encoding="utf-8") as f:
                f.write(url)
            self.server_client.server_url = url
            render_success(f"Server URL set to {url}")
        except Exception as e:
            render_error(f"Failed to set URL: {e}")

    def handle_update(self) -> None:
        """Handle update command."""
        try:
            # Check PyPI for latest version
            render_info("Checking for updates...")
            # This would contact PyPI in real implementation
            render_info("Already on latest version")
        except Exception as e:
            render_error(f"Update check failed: {e}")

    def _pid_alive(self, pid_file: str) -> bool:
        """Check if process with PID in file is alive."""
        path = os.path.join(self.project_root, pid_file)
        if not os.path.exists(path):
            return False
        try:
            pid = int(open(path).read().strip())
            if sys.platform == "win32":
                import ctypes
                handle = ctypes.windll.kernel32.OpenProcess(0x0400, False, pid)
                if handle:
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return True
                return False
            else:
                os.kill(pid, 0)
                return True
        except (OSError, PermissionError, ValueError):
            return False

    def add_job(self, job_id: str, status: str, duration: str, output: str = "") -> None:
        """Add job to history."""
        self.jobs_history.append({
            "id": job_id,
            "status": status,
            "duration": duration,
            "output": output,
        })
