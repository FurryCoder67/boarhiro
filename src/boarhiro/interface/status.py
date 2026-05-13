"""
Status dashboard for BOARHIRO interface.

Displays agent status, metrics, and job history.
"""

from rich.console import Console
from rich.layout import Layout
from rich.live import Live

from .ui import render_banner, render_status_panel, render_metrics_panel


class StatusDashboard:
    """Displays live status dashboard."""

    def __init__(self, console: Console):
        """
        Initialize dashboard.

        Args:
            console: Rich console instance
        """
        self.console = console
        self.status_data = {}
        self.metrics = {}

    def update_status(self, status_data: dict) -> None:
        """Update status data."""
        self.status_data = status_data

    def update_metrics(self, metrics: dict) -> None:
        """Update metrics data."""
        self.metrics = metrics

    def render(self) -> Layout:
        """
        Render dashboard layout.

        Returns:
            Rich Layout with panels
        """
        layout = Layout()
        layout.split_column(
            Layout(name="banner", size=8),
            Layout(name="body"),
        )

        layout["banner"].update(render_banner())

        body_layout = layout["body"]
        body_layout.split_row(
            Layout(render_status_panel(self.status_data), name="status"),
            Layout(render_metrics_panel(self.metrics), name="metrics"),
        )

        return layout

    def display(self) -> None:
        """Display dashboard in live mode."""
        with Live(self.render(), console=self.console, refresh_per_second=2) as live:
            pass  # Live display is rendered
