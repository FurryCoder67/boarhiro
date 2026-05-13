"""
UI rendering components for BOARHIRO interface.

Provides panels, tables, and visual elements for the terminal interface.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.style import Style

console = Console()


def render_banner() -> str:
    """Render the BOARHIRO banner."""
    banner = r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🐗  BOARHIRO — Self-Training Neural AI  🐗             ║
║                                                               ║
║         Logic. Speed. Minimalism. Architecture.              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    return banner


def render_status_panel(status_data: dict) -> Panel:
    """
    Render agent/service status panel.

    Args:
        status_data: Dictionary with status information

    Returns:
        Rich Panel with formatted status
    """
    trainer = "🟢 Running" if status_data.get("trainer_running") else "🔴 Stopped"
    server = "🟢 Running" if status_data.get("server_running") else "🔴 Stopped"
    watcher = "🟢 Running" if status_data.get("watcher_running") else "🔴 Stopped"

    content = f"""
Agent:   [bold cyan]{status_data.get("agent_name", "boarhiro")}[/]
Status:  [bold]Active[/]

Services:
  • Trainer: {trainer}
  • Server:  {server}
  • Watcher: {watcher}

Model: [yellow]{status_data.get("model_status", "Loaded")}[/]
"""

    return Panel(
        content.strip(),
        title="[bold cyan]Agent Status[/]",
        border_style="cyan",
        box=box.ROUNDED,
    )


def render_metrics_panel(metrics: dict) -> Panel:
    """
    Render metrics panel.

    Args:
        metrics: Dictionary with performance metrics

    Returns:
        Rich Panel with metrics
    """
    content = f"""
Jobs Completed:   [bold green]{metrics.get('jobs_completed', 0)}[/]
Successful:       [bold green]{metrics.get('jobs_successful', 0)}[/]
Success Rate:     [bold yellow]{metrics.get('success_rate', '0%')}[/]
Avg Exec Time:    [bold magenta]{metrics.get('avg_exec_time', 'N/A')}[/]
"""

    return Panel(
        content.strip(),
        title="[bold magenta]Metrics[/]",
        border_style="magenta",
        box=box.ROUNDED,
    )


def render_help_table() -> Table:
    """
    Render help command table.

    Returns:
        Rich Table with command help
    """
    table = Table(
        title="[bold cyan]Available Commands[/]",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
    )
    table.add_column("Command", style="bold green")
    table.add_column("Description", style="white")

    help_items = [
        ("help", "Show this help menu"),
        ("clear", "Clear the screen"),
        ("status", "Show detailed agent and service status"),
        ("jobs", "List recent jobs and their status"),
        ("metrics", "Show performance metrics"),
        ("seturl <url>", "Set custom server URL"),
        ("update", "Check for and install latest version"),
        ("exit / quit", "Shut down BOARHIRO"),
    ]

    for cmd, desc in help_items:
        table.add_row(cmd, desc)

    return table


def render_jobs_table(jobs: list) -> Table:
    """
    Render job history table.

    Args:
        jobs: List of job dictionaries

    Returns:
        Rich Table with job history
    """
    table = Table(
        title="[bold yellow]Recent Jobs[/]",
        show_header=True,
        header_style="bold yellow",
        box=box.ROUNDED,
    )
    table.add_column("ID", style="bold white")
    table.add_column("Status", style="white")
    table.add_column("Duration", style="cyan")
    table.add_column("Output", style="white", overflow="fold")

    for job in jobs[-10:]:  # Show last 10 jobs
        status_color = "green" if job.get("status") == "success" else "red"
        table.add_row(
            job.get("id", "N/A"),
            f"[{status_color}]{job.get('status', 'unknown')}[/]",
            job.get("duration", "N/A"),
            job.get("output", "")[:60],
        )

    return table


def render_error(message: str) -> None:
    """
    Render error message.

    Args:
        message: Error message to display
    """
    console.print(f"[bold red]✗ Error:[/] {message}")


def render_success(message: str) -> None:
    """
    Render success message.

    Args:
        message: Success message to display
    """
    console.print(f"[bold green]✓ Success:[/] {message}")


def render_info(message: str) -> None:
    """
    Render info message.

    Args:
        message: Info message to display
    """
    console.print(f"[bold cyan]ℹ Info:[/] {message}")


def render_warning(message: str) -> None:
    """
    Render warning message.

    Args:
        message: Warning message to display
    """
    console.print(f"[bold yellow]⚠ Warning:[/] {message}")
