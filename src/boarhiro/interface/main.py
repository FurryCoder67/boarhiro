"""
Main CLI loop for BOARHIRO interface.

Orchestrates the chat interface, command handling, and service management.
"""

import os
import sys
import subprocess
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from .ui import render_banner, render_error, render_success, render_info
from .commands import CommandHandler


console = Console()


def _project_root() -> str:
    """Get project root directory."""
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def _load_url() -> str:
    """Load server URL from config or environment."""
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
    return "http://localhost:5000"


def _save_url(url: str) -> None:
    """Save server URL to link.txt."""
    root = _project_root()
    with open(os.path.join(root, "link.txt"), "w", encoding="utf-8") as f:
        f.write(url)


def _spawn_service(cmd: list, pid_file: str, log_file: str) -> None:
    """Spawn a background service."""
    root = _project_root()
    log_path = os.path.join(root, log_file)
    
    try:
        if sys.platform == "win32":
            # Windows: use CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(
                cmd,
                stdout=open(log_path, "a"),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            # Unix: use NOHUP
            subprocess.Popen(
                cmd,
                stdout=open(log_path, "a"),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,
            )
    except Exception as e:
        render_error(f"Failed to spawn service: {e}")


def run_cli() -> None:
    """Main CLI entry point."""
    # Force UTF-8 on Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    root = _project_root()
    server_url = _load_url()
    handler = CommandHandler(console, root)

    # Print banner
    console.print(render_banner())
    render_info("Type 'help' for commands")

    # Main loop
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]boarhiro[/]").strip()

            if not user_input:
                continue

            # Parse command and arguments
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # Handle commands
            if command in ("exit", "quit"):
                render_info("Shutting down...")
                break
            elif command == "help":
                handler.handle_help()
            elif command == "clear":
                handler.handle_clear()
            elif command == "status":
                handler.handle_status()
            elif command == "jobs":
                handler.handle_jobs()
            elif command == "metrics":
                handler.handle_metrics()
            elif command == "seturl":
                if args:
                    handler.handle_seturl(args)
                    server_url = args
                else:
                    render_error("Usage: seturl <url>")
            elif command == "update":
                handler.handle_update()
            else:
                # Treat as chat prompt
                try:
                    response = handler.server_client.generate(user_input)
                    console.print(f"[bold magenta]boarhiro:[/] {response}")
                    handler.add_job(f"job-{len(handler.jobs_history)}", "success", "0.1s", response[:100])
                except Exception as e:
                    render_error(f"Generation failed: {e}")

        except KeyboardInterrupt:
            render_info("Use 'exit' to quit")
        except Exception as e:
            render_error(f"Error: {e}")


if __name__ == "__main__":
    run_cli()
