import os
import sys
import time
import subprocess
import threading
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
from rich import box

# Force UTF-8 output on Windows so Unicode block art renders correctly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console()

BANNER = """
██████╗  ██████╗  █████╗ ██████╗ ██╗  ██╗██╗██████╗  ██████╗ 
██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██║  ██║██║██╔══██╗██╔═══██╗
██████╔╝██║   ██║███████║██████╔╝███████║██║██████╔╝██║   ██║
██╔══██╗██║   ██║██╔══██║██╔══██╗██╔══██║██║██╔══██╗██║   ██║
██████╔╝╚██████╔╝██║  ██║██║  ██║██║  ██║██║██║  ██║╚██████╔╝
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝
"""

LOCAL_SERVER_URL = "http://localhost:5000"
SERVER_PID_FILE  = "boarhiro_server.pid"

HELP_TEXT = [
    ("help",           "Show this help menu"),
    ("clear",          "Clear the terminal screen"),
    ("status",         "Show status of all services"),
    ("seturl <url>",   "Override server URL (default: localhost:5000)"),
    ("exit / quit",    "Shut down BOARHIRO"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _project_root() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

def _load_url() -> str:
    """Default to local server. Fall back to link.txt for remote override."""
    env_url = os.environ.get("BOARHIRO_URL", "").strip()
    if env_url:
        return env_url
    root = _project_root()
    for candidate in ["link.txt", "src/link.txt"]:
        path = os.path.join(root, candidate)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                saved = f.read().strip()
            if saved:
                return saved
    return LOCAL_SERVER_URL   # always default to local

def _save_url(url: str):
    root = _project_root()
    with open(os.path.join(root, "link.txt"), "w", encoding="utf-8") as f:
        f.write(url)

def _pid_alive(pid: int) -> bool:
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

def _read_pid(pid_file: str) -> int | None:
    path = os.path.join(_project_root(), pid_file)
    if os.path.exists(path):
        try:
            return int(open(path).read().strip())
        except Exception:
            pass
    return None

def _trainer_running() -> bool:
    pid = _read_pid("boarhiro_train.pid")
    return pid is not None and _pid_alive(pid)

def _server_running() -> bool:
    pid = _read_pid(SERVER_PID_FILE)
    return pid is not None and _pid_alive(pid)

def _watcher_running() -> bool:
    pid = _read_pid("boarhiro_watcher.pid")
    return pid is not None and _pid_alive(pid)

# ── Background launchers ──────────────────────────────────────────────────────

def _pythonw() -> str:
    pw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pw if os.path.exists(pw) else sys.executable

def _spawn(cmd: list, log_name: str):
    root = _project_root()
    log  = open(os.path.join(root, log_name), "a", encoding="utf-8")
    kwargs = dict(cwd=root, stdout=log, stderr=subprocess.STDOUT, close_fds=True)
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    return subprocess.Popen(cmd, **kwargs)

def _start_ecosystem():
    """Start trainer, hunter, watcher, and local server if not already running."""
    root  = _project_root()
    lines = []

    # ── Local inference server ────────────────────────────────────────────
    if _server_running():
        lines.append("[dim]Server    :[/dim] [yellow]already running[/yellow]")
    else:
        proc = _spawn([_pythonw(), "-m", "boarhiro.server"], "server.log")
        lines.append(f"[dim]Server    :[/dim] [green]started[/green] (PID {proc.pid})")

    # ── Background trainer ────────────────────────────────────────────────
    if _trainer_running():
        lines.append("[dim]Trainer   :[/dim] [yellow]already running[/yellow]")
    else:
        proc = _spawn(
            [_pythonw(), "-m", "boarhiro.trainer", "--foreground"],
            "boarhiro_train.log"
        )
        lines.append(f"[dim]Trainer   :[/dim] [green]started[/green] (PID {proc.pid})")

    # ── Hunter ────────────────────────────────────────────────────────────
    hunter = os.path.join(root, "src", "auto_generator.py")
    if os.path.exists(hunter):
        proc = _spawn([_pythonw(), hunter], "hunter.log")
        lines.append(f"[dim]Hunter    :[/dim] [green]started[/green] (PID {proc.pid})")

    # ── Watcher ───────────────────────────────────────────────────────────
    watcher = os.path.join(root, "src", "local_watcher.py")
    if os.path.exists(watcher):
        if _watcher_running():
            lines.append("[dim]Watcher   :[/dim] [yellow]already running[/yellow]")
        else:
            proc = _spawn([_pythonw(), watcher], "watcher.log")
            lines.append(f"[dim]Watcher   :[/dim] [green]started[/green] (PID {proc.pid})")

    return lines

# ── Server ping ───────────────────────────────────────────────────────────────

def _wait_for_server(url: str, timeout: int = 15) -> bool:
    """Poll /health until the server is up or timeout expires."""
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
    try:
        r = requests.get(f"{url}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

# ── UI helpers ────────────────────────────────────────────────────────────────

def print_banner():
    console.print(Text(BANNER, style="bold magenta"), justify="center")
    console.print(
        Panel(
            "[bold cyan]Neural Interface v1.0[/bold cyan]  ·  "
            "[dim]Type [bold white]help[/bold white] for commands[/dim]",
            style="dim magenta",
            box=box.ROUNDED,
        )
    )

def print_help():
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    table.add_column("Command", style="bold yellow", min_width=20)
    table.add_column("Description", style="white")
    for cmd, desc in HELP_TEXT:
        table.add_row(cmd, desc)
    console.print(Panel(table, title="[bold cyan]Commands[/bold cyan]",
                        style="dim cyan", box=box.ROUNDED))

def print_status(url: str):
    lines = []

    # Server
    reachable = _ping_server(url)
    dot   = "[bold green]●[/bold green]" if reachable else "[bold red]●[/bold red]"
    state = "online" if reachable else "offline"
    lines.append(f"{dot} [dim]Server   :[/dim] {state}  [dim]{url}[/dim]")

    # Trainer
    if _trainer_running():
        lines.append("[bold green]●[/bold green] [dim]Trainer  :[/dim] running")
    else:
        lines.append("[bold red]●[/bold red] [dim]Trainer  :[/dim] not running")

    # Log tail
    log_path = os.path.join(_project_root(), "boarhiro_train.log")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            tail = f.readlines()[-3:]
        lines.append("")
        lines.append("[dim]Last training log:[/dim]")
        for l in tail:
            lines.append(f"  [dim]{l.rstrip()}[/dim]")

    console.print(Panel("\n".join(lines), title="[bold cyan]Status[/bold cyan]",
                        style="dim cyan", box=box.ROUNDED))

# ── Core request ──────────────────────────────────────────────────────────────

def ask_boarhiro(prompt: str, url: str) -> str:
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
            return f"[red]Server returned {response.status_code}.[/red]\n[dim]{response.text[:300]}[/dim]"
        if not response.text.strip():
            return "[red]Empty response from server.[/red]"
        try:
            data = response.json()
        except Exception:
            return f"[red]Response is not valid JSON.[/red]\n[dim]{response.text[:300]}[/dim]"
        return data.get("response",
                        f"[yellow]No 'response' key in reply.[/yellow]\n[dim]{data}[/dim]")
    except requests.exceptions.ConnectionError:
        return "[red]Connection Error:[/red] Server is not reachable."
    except requests.exceptions.Timeout:
        return "[red]Timeout:[/red] Server took too long to respond."
    except Exception as e:
        return f"[red]Unexpected Error:[/red] {e}"

# ── Main CLI ──────────────────────────────────────────────────────────────────

def run_cli():
    url = _load_url()

    console.clear()
    print_banner()

    # ── Start all background services ─────────────────────────────────────
    with Live(
        Spinner("dots", text=Text(" Starting services...", style="dim cyan")),
        console=console, transient=True,
    ):
        ecosystem_lines = _start_ecosystem()

    console.print(Panel(
        "\n".join(ecosystem_lines),
        title="[bold cyan]Ecosystem[/bold cyan]",
        style="dim cyan", box=box.ROUNDED,
    ))

    # ── Wait for local server to be ready ─────────────────────────────────
    if url == LOCAL_SERVER_URL or "localhost" in url:
        with Live(
            Spinner("dots", text=Text(" Waiting for local server...", style="dim cyan")),
            console=console, transient=True,
        ):
            ready = _wait_for_server(url, timeout=20)

        if ready:
            # Check if model is loaded
            try:
                health = requests.get(f"{url}/health", timeout=3).json()
                if health.get("model_loaded"):
                    console.print(Panel(
                        "[green]● Server ready — model loaded[/green]",
                        style="dim green", box=box.ROUNDED,
                    ))
                else:
                    console.print(Panel(
                        "[yellow]● Server started but model not loaded yet.[/yellow]\n"
                        "[dim]Run [bold white]trainboarhiro[/bold white] first to train a model.[/dim]",
                        style="yellow", box=box.ROUNDED,
                    ))
            except Exception:
                console.print(Panel(
                    "[green]● Server ready[/green]",
                    style="dim green", box=box.ROUNDED,
                ))
        else:
            console.print(Panel(
                "[yellow]● Server is taking longer than expected to start.[/yellow]\n"
                "[dim]Check server.log for details.[/dim]",
                style="yellow", box=box.ROUNDED,
            ))

    # ── Chat loop ──────────────────────────────────────────────────────────
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
                console=console, transient=True,
            ):
                reply = ask_boarhiro(prompt, url)

            console.print(Panel(
                reply,
                title="[bold cyan]BOARHIRO[/bold cyan]",
                style="cyan", box=box.ROUNDED,
            ))

    console.print(Rule(style="magenta"))
    console.print("[bold magenta]BOARHIRO offline. Goodbye.[/bold magenta]")
    console.print(Rule(style="magenta"))
