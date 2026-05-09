"""
BOARHIRO Neural Interface
A beautiful, minimal CLI for interacting with the BOARHIRO AI system.
"""

import os
import sys
import time
import subprocess
from typing import Optional

import requests
from rich.console import Console
from rich.live import Live
from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table


# Force UTF-8 output on Windows so Unicode block art renders correctly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🐗  BOARHIRO — Self-Training Neural AI  🐗             ║
║                                                               ║
║         Logic. Speed. Minimalism.                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

LOCAL_SERVER_URL = "http://localhost:5000"
SERVER_PID_FILE = "boarhiro_server.pid"

HELP_TEXT = [
    ("help", "Show this help menu"),
    ("clear", "Clear the terminal screen"),
    ("status", "Show status of all services"),
    ("seturl <url>", "Override server URL (default: localhost:5000)"),
    ("update", "Check for and install latest version from PyPI"),
    ("exit / quit", "Shut down BOARHIRO"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _project_root() -> str:
    """Get the absolute path to the project root directory."""
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def _load_url() -> str:
    """Load server URL from environment, config file, or default to localhost."""
    env_url = os.environ.get("BOARHIRO_URL", "").strip()
    if env_url:
        return env_url
    root = _project_root()
    for candidate in ["link.txt", "src/link.txt"]:
        path = os.path.join(root, candidate)
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                saved = f.read().strip()
            if saved:
                return saved
    return LOCAL_SERVER_URL


def _save_url(url: str) -> None:
    """Save server URL to link.txt for future sessions."""
    root = _project_root()
    with open(os.path.join(root, "link.txt"), "w", encoding="utf-8") as f:
        f.write(url)


def _pid_alive(pid: int) -> bool:
    """Check if a process with given PID is still running."""
    try:
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
    except (OSError, PermissionError):
        return False


def _read_pid(pid_file: str) -> Optional[int]:
    """Read a PID from a file, returning None if file doesn't exist or is invalid."""
    path = os.path.join(_project_root(), pid_file)
    if os.path.exists(path):
        try:
            return int(open(path).read().strip())
        except Exception:
            pass
    return None


def _trainer_running() -> bool:
    """Check if the background trainer process is active."""
    pid = _read_pid("boarhiro_train.pid")
    return pid is not None and _pid_alive(pid)


def _server_running() -> bool:
    """Check if the inference server process is active."""
    pid = _read_pid(SERVER_PID_FILE)
    return pid is not None and _pid_alive(pid)


def _watcher_running() -> bool:
    """Check if the data watcher process is active."""
    pid = _read_pid("boarhiro_watcher.pid")
    return pid is not None and _pid_alive(pid)

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS SPAWNING & MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def _pythonw() -> str:
    """Get path to pythonw.exe on Windows, or fall back to python on other systems."""
    pw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pw if os.path.exists(pw) else sys.executable


def _spawn(cmd: list, log_name: str) -> subprocess.Popen:
    """Spawn a detached background subprocess."""
    root = _project_root()
    log = open(os.path.join(root, log_name), "a", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"  # force UTF-8 before any Python code runs
    kwargs = dict(
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
        close_fds=True,
        env=env,
    )
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    return subprocess.Popen(cmd, **kwargs)


def _start_ecosystem() -> list:
    """Start all background services: trainer, server, hunter, and watcher."""
    root = _project_root()
    lines = []

    # Local inference server
    if _server_running():
        lines.append("[dim]Server    :[/dim] [yellow]⦿ already running[/yellow]")
    else:
        proc = _spawn([_pythonw(), "-m", "boarhiro.server"], "server.log")
        lines.append(f"[dim]Server    :[/dim] [green]⦿ started[/green] [dim](PID {proc.pid})[/dim]")

    # Background trainer
    if _trainer_running():
        lines.append("[dim]Trainer   :[/dim] [yellow]⦿ already running[/yellow]")
    else:
        proc = _spawn(
            [_pythonw(), "-m", "boarhiro.trainer", "--foreground"],
            "boarhiro_train.log",
        )
        lines.append(f"[dim]Trainer   :[/dim] [green]⦿ started[/green] [dim](PID {proc.pid})[/dim]")

    # Data hunter
    hunter = os.path.join(root, "src", "auto_generator.py")
    if os.path.exists(hunter):
        proc = _spawn([_pythonw(), hunter], "hunter.log")
        lines.append(f"[dim]Hunter    :[/dim] [green]⦿ started[/green] [dim](PID {proc.pid})[/dim]")

    # File watcher
    watcher = os.path.join(root, "src", "local_watcher.py")
    if os.path.exists(watcher):
        if _watcher_running():
            lines.append("[dim]Watcher   :[/dim] [yellow]⦿ already running[/yellow]")
        else:
            proc = _spawn([_pythonw(), watcher], "watcher.log")
            lines.append(f"[dim]Watcher   :[/dim] [green]⦿ started[/green] [dim](PID {proc.pid})[/dim]")

    return lines

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK & SERVER COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════════

def _wait_for_server(url: str, timeout: int = 15) -> bool:
    """Poll /health endpoint until server is ready or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _ping_server(url: str) -> bool:
    """Check if server is responding to health checks."""
    try:
        r = requests.get(f"{url}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# USER INTERFACE & DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner() -> None:
    """Display the welcome banner and introduction."""
    console.print(Text(BANNER, style="bold cyan"), justify="center")
    console.print(
        Panel(
            "[bold cyan]Neural Interface[/bold cyan]  [dim]·[/dim]  "
            "[dim]Type [bold white]help[/bold white] for commands[/dim]",
            style="dim magenta",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def print_help() -> None:
    """Display the help menu with all available commands."""
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        pad_edge=True,
        expand=True,
        show_lines=False,
    )
    table.add_column("Command", style="bold yellow", min_width=18, no_wrap=True)
    table.add_column("Description", style="white", overflow="fold")

    for cmd, desc in HELP_TEXT:
        table.add_row(cmd, desc)

    console.print(
        Panel(
            table,
            title="[bold cyan]Commands[/bold cyan]",
            style="dim cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def print_status(url: str) -> None:
    """Display the status of all services and recent training logs."""
    reachable = _ping_server(url)
    server_state = "online" if reachable else "offline"
    server_dot = "[bold green]●[/bold green]" if reachable else "[bold red]●[/bold red]"

    trainer_running = _trainer_running()
    trainer_state = "running" if trainer_running else "not running"
    trainer_dot = "[bold green]●[/bold green]" if trainer_running else "[bold red]●[/bold red]"

    header = Table.grid(padding=(0, 1))
    header.add_row(
        f"{server_dot} [dim]Server[/dim]  [bold]{server_state}[/bold]  [dim]{url}[/dim]"
    )
    header.add_row(
        f"{trainer_dot} [dim]Trainer[/dim]  [bold]{trainer_state}[/bold]"
    )

    log_path = os.path.join(_project_root(), "boarhiro_train.log")
    logs_panel: Optional[Panel] = None
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8", errors="replace") as f:
            tail = [ln.rstrip("\n") for ln in f.readlines()[-3:]]

        if tail:
            log_grid = Table.grid(padding=(0, 0))
            for log_line in tail:
                log_grid.add_row(Text(log_line, style="dim"))

            logs_panel = Panel(
                log_grid,
                title="[dim]Recent training logs[/dim]",
                box=box.ROUNDED,
                padding=(0, 2),
            )

    if logs_panel:
        content = Table.grid(header, logs_panel, padding=(0, 1))
        console.print(
            Panel(
                content,
                title="[bold cyan]Status[/bold cyan]",
                style="dim cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                header,
                title="[bold cyan]Status[/bold cyan]",
                style="dim cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

# ═══════════════════════════════════════════════════════════════════════════════
# API COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════════

def ask_boarhiro(prompt: str, url: str) -> str:
    """Send a prompt to BOARHIRO and get a response."""
    try:
        response = requests.post(f"{url}/generate", json={"prompt": prompt}, timeout=30)

        if response.status_code == 404:
            return (
                "[red]404 — /generate not found.[/red]\n"
                "[dim]The server process may still be starting up. Try again in a moment.[/dim]"
            )
        if response.status_code == 503:
            try:
                msg = response.json().get("error", "")
            except Exception:
                msg = response.text[:200]
            return f"[yellow]Server not ready:[/yellow] {msg}"
        if response.status_code != 200:
            return (
                f"[red]Server returned {response.status_code}.[/red]\n"
                f"[dim]{response.text[:300]}[/dim]"
            )

        if not response.text.strip():
            return "[red]Empty response from server.[/red]"

        try:
            data = response.json()
        except Exception:
            return f"[red]Response is not valid JSON.[/red]\n[dim]{response.text[:300]}[/dim]"

        return data.get(
            "response",
            f"[yellow]No 'response' key in reply.[/yellow]\n[dim]{data}[/dim]",
        )

    except requests.exceptions.ConnectionError:
        return "[red]Connection Error:[/red] Server is not reachable."
    except requests.exceptions.Timeout:
        return "[red]Timeout:[/red] Server took too long to respond."
    except Exception as e:
        return f"[red]Unexpected Error:[/red] {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CLI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def run_cli() -> None:
    """Main CLI entry point - starts the BOARHIRO interactive interface."""
    url = _load_url()

    console.clear()
    print_banner()

    import threading
    from boarhiro.updater import check_for_updates

    threading.Thread(
        target=lambda: check_for_updates(silent=False),
        daemon=True,
    ).start()

    from boarhiro.downloader import ensure_model, model_exists
    if not model_exists():
        console.print(
            Panel(
                "[yellow]No trained model found.[/yellow]\nDownloading pre-trained model from GitHub...",
                style="yellow",
                box=box.ROUNDED,
            )
        )
        ok = ensure_model(show_progress=True)
        if ok:
            console.print(
                Panel(
                    "[green]Model downloaded successfully.[/green]",
                    style="dim green",
                    box=box.ROUNDED,
                )
            )
        else:
            console.print(
                Panel(
                    "[yellow]Could not download model. Starting with untrained model.[/yellow]\n"
                    "[dim]Run trainboarhiro to train locally.[/dim]",
                    style="yellow",
                    box=box.ROUNDED,
                )
            )

    with Live(
        Spinner("dots", text=Text(" Starting services...", style="dim cyan")),
        console=console,
        transient=True,
    ):
        ecosystem_lines = _start_ecosystem()

    console.print(
        Panel(
            "\n".join(ecosystem_lines),
            title="[bold cyan]Ecosystem[/bold cyan]",
            style="dim cyan",
            box=box.ROUNDED,
        )
    )

    if url == LOCAL_SERVER_URL or "localhost" in url:
        with Live(
            Spinner("dots", text=Text(" Waiting for local server...", style="dim cyan")),
            console=console,
            transient=True,
        ):
            ready = _wait_for_server(url, timeout=20)

        if ready:
            try:
                health = requests.get(f"{url}/health", timeout=3).json()
                if health.get("model_loaded"):
                    console.print(
                        Panel(
                            "[green]● Server ready — model loaded[/green]",
                            style="dim green",
                            box=box.ROUNDED,
                        )
                    )
                else:
                    console.print(
                        Panel(
                            "[yellow]● Server started but model not loaded yet.[/yellow]\n"
                            "[dim]Run [bold white]trainboarhiro[/bold white] first to train a model.[/dim]",
                            style="yellow",
                            box=box.ROUNDED,
                        )
                    )
            except Exception:
                console.print(
                    Panel(
                        "[green]● Server ready[/green]",
                        style="dim green",
                        box=box.ROUNDED,
                    )
                )
        else:
            console.print(
                Panel(
                    "[yellow]● Server is taking longer than expected to start.[/yellow]\n"
                    "[dim]Check server.log for details.[/dim]",
                    style="yellow",
                    box=box.ROUNDED,
                )
            )

    while True:
        try:
            console.print()
            raw = Prompt.ask("[bold magenta]▶[/bold magenta]")
        except (KeyboardInterrupt, EOFError):
            break

        prompt = raw.strip()
        if not prompt:
            continue

        lower = prompt.lower()

        if lower in ("exit", "quit"):
            break
        elif lower == "help":
            print_help()
        elif lower == "clear":
            console.clear()
            print_banner()
        elif lower == "status":
            print_status(url)
        elif lower == "update":
            from boarhiro.updater import check_for_updates, auto_upgrade

            with Live(
                Spinner("dots", text=Text(" Checking for updates...", style="dim cyan")),
                console=console,
                transient=True,
            ):
                has_update = check_for_updates(silent=True)

            if has_update:
                console.print(
                    Panel(
                        "[yellow]New version available![/yellow]\nUpgrading now...",
                        style="yellow",
                        box=box.ROUNDED,
                    )
                )
                auto_upgrade()
            else:
                console.print(
                    Panel(
                        "[green]You are on the latest version.[/green]",
                        style="dim green",
                        box=box.ROUNDED,
                    )
                )
        elif lower.startswith("seturl "):
            url = prompt[7:].strip()
            try:
                _save_url(url)
                console.print(f"[green]✔[/green] URL saved: [bold]{url}[/bold]")
            except Exception:
                console.print(f"[green]✔[/green] URL set to [bold]{url}[/bold]")
        else:
            with Live(
                Spinner("dots", text=Text(" Thinking...", style="dim cyan")),
                console=console,
                transient=True,
            ):
                reply = ask_boarhiro(prompt, url)

            console.print(
                Panel(
                    reply,
                    title="[bold cyan]BOARHIRO[/bold cyan]",
                    style="cyan",
                    box=box.ROUNDED,
                )
            )

    console.print(Rule(style="magenta"))
    console.print("[bold magenta]BOARHIRO offline. Goodbye.[/bold magenta]")
    console.print(Rule(style="magenta"))

