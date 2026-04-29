import os
import sys
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

# Customizing the look: Magenta for AI, Cyan for User
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "user": "bold cyan",
    "ai": "bold magenta"
})

console = Console(theme=custom_theme)

class BoarhiroConfig:
    """Handles the persistence of the Colab/Ngrok URL."""
    CONFIG_FILE = ".boarhiro_config"

    @classmethod
    def get_url(cls):
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "r") as f:
                return f.read().strip()
        return None

    @classmethod
    def save_url(cls, url):
        with open(cls.CONFIG_FILE, "w") as f:
            f.write(url)

def show_banner():
    """Renders the aesthetic header."""
    banner = Text(justify="center")
    banner.append("🐗 BOARHIRO v0.1.0\n", style="ai")
    banner.append("Logic. Speed. Minimalism.", style="info")
    
    console.print(Panel(
        banner, 
        border_style="bright_blue", 
        padding=(1, 2),
        subtitle="[bold white]Neural Link Active[/bold white]"
    ))

def run_cli():
    # Clear screen for that 'fresh app' feel
    console.clear()
    show_banner()

    # Handle URL configuration
    url = BoarhiroConfig.get_url()
    if not url or "--reset" in sys.argv:
        console.print("[warning]! Setup Required: Enter your Colab Backend URL[/warning]")
        url = Prompt.ask("[user]URL[/user]")
        if not url.startswith("http"):
            url = f"https://{url}"
        BoarhiroConfig.save_url(url)
        console.print("[info]Link saved successfully.[/info]\n")

    endpoint = f"{url.rstrip('/')}/generate"

    while True:
        try:
            # 1. Styled User Input
            user_input = Prompt.ask("[user]❯[/user]")

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("\n[info]🐗 Shutting down. Logic stored.[/info]")
                break

            if not user_input.strip():
                continue

            # 2. Animated Thinking Status
            with console.status("[italic ai]Consulting the Swarm...[/italic ai]", spinner="bouncingBar"):
                try:
                    response = requests.post(
                        endpoint, 
                        json={"prompt": user_input},
                        timeout=15
                    )
                    response.raise_for_status()
                    data = response.json()
                    ai_reply = data.get("response", "No logic returned.")
                except Exception as e:
                    ai_reply = f"[error]Connection Error:[/error] Could not reach the Brain.\n[dim]{e}[/dim]"

            # 3. Styled Response Panel
            console.print(Panel(
                ai_reply, 
                title="[bold white]BOARHIRO[/bold white]", 
                title_align="left",
                border_style="ai",
                padding=(1, 1)
            ))
            console.print("") # Spacer

        except KeyboardInterrupt:
            console.print("\n[info]Session terminated.[/info]")
            break

if __name__ == "__main__":
    run_cli()