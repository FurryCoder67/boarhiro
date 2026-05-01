import os
import time
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

console = Console()

BANNER = r"""
  ____   ___    _    ____  _   _ ___ ____   ___  
 | __ ) / _ \  / \  |  _ \| | | |_ _|  _ \ / _ \ 
 |  _ \| | | |/ _ \ | |_) | |_| || || |_) | | | |
 | |_) | |_| / ___ \|  _ <|  _  || ||  _ <| |_| |
 |____/ \___/_/   \_\_| \_\_| |_|___|_| \_\\___/ 
"""

HELP_TEXT = [
    ("help",        "Show this help menu"),
    ("clear",       "Clear the terminal screen"),
    ("status",      "Show current connection status"),
    ("seturl <url>","Set the Colab/server URL"),
    ("exit / quit", "Shut down BOARHIRO"),
]


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
    table.add_column("Command", style="bold yellow", min_width=18)
    table.add_column("Description", style="white")
    for cmd, desc in HELP_TEXT:
        table.add_row(cmd, desc)
    console.print(Panel(table, title="[bold cyan]Commands[/bold cyan]", style="dim cyan", box=box.ROUNDED))


def print_status(url: str):
    if not url:
        status = "[bold red]● OFFLINE[/bold red]  — no URL configured"
    else:
        status = f"[bold green]● CONNECTED[/bold green]  — [dim]{url}[/dim]"
    console.print(Panel(status, title="[bold cyan]Status[/bold cyan]", style="dim cyan", box=box.ROUNDED))


def ask_boarhiro(prompt: str, url: str) -> str:
    try:
        response = requests.post(f"{url}/generate", json={"prompt": prompt}, timeout=30)
        return response.json().get("response", "⚠  No response field in reply.")
    except requests.exceptions.ConnectionError:
        return "[red]Connection Error:[/red] Cannot reach the server. Check your URL."
    except requests.exceptions.Timeout:
        return "[red]Timeout:[/red] The server took too long to respond."
    except Exception as e:
        return f"[red]Error:[/red] {e}"


def run_cli():
    url = os.environ.get("BOARHIRO_URL", "")

    console.clear()
    print_banner()

    while True:
        try:
            console.print()
            raw = Prompt.ask("[bold magenta]▶[/bold magenta]")
        except (KeyboardInterrupt, EOFError):
            break

        prompt = raw.strip()
        if not prompt:
            continue

        # ── built-in commands ──────────────────────────────────────────────
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
            console.print(f"[green]✔[/green] URL set to [bold]{url}[/bold]")

        # ── send to brain ──────────────────────────────────────────────────
        else:
            if not url:
                console.print(
                    Panel(
                        "[yellow]No server URL configured.[/yellow]\n"
                        "Use [bold white]seturl <url>[/bold white] or set the "
                        "[bold white]BOARHIRO_URL[/bold white] environment variable.",
                        style="yellow",
                        box=box.ROUNDED,
                    )
                )
                continue

            # Animated spinner while waiting
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
