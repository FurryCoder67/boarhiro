import os
import requests
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

# --- CONFIGURATION ---
# Your GitHub details (used as a secondary backup)
GITHUB_USER = "furrycoder67"
GITHUB_REPO = "boarhiro"
LINK_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/link.txt"

# Aesthetics Setup
custom_theme = Theme({
    "info": "dim cyan", 
    "user": "bold cyan", 
    "ai": "bold magenta", 
    "error": "bold red"
})
console = Console(theme=custom_theme)

def get_brain_url():
    """
    Finds the Brain URL. 
    Priority 1: Local 'link.txt' (Immediate/Development)
    Priority 2: GitHub 'link.txt' (Remote/Production)
    """
    # 1. Check for local link.txt file in the current directory
    if os.path.exists("link.txt"):
        try:
            with open("link.txt", "r") as f:
                url = f.read().strip()
                if url.startswith("http"):
                    return url
        except Exception:
            pass

    # 2. Fallback: Fetch from GitHub
    try:
        response = requests.get(LINK_URL, timeout=3)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        return None
    return None

def show_banner():
    """Renders the aesthetic header."""
    banner = Text(justify="center")
    banner.append("🐗 BOARHIRO v0.1.0\n", style="ai")
    banner.append("Neural Link Established", style="info")
    
    console.print(Panel(
        banner, 
        border_style="bright_blue", 
        padding=(1, 2),
        subtitle="[bold white]Ready for Instruction[/bold white]"
    ))

def run_cli():
    console.clear()
    show_banner()
    
    # Attempt to sync with the Brain
    with console.status("[info]Synchronizing with Cloud Brain...", spinner="dots"):
        url = get_brain_url()
        time.sleep(1) # Visual breathing room
    
    if not url:
        console.print("[error]❌ Error:[/error] Neural link not found.")
        console.print("[dim]Please ensure your Ngrok URL is saved in 'link.txt'.[/dim]")
        return

    # Set the API endpoint
    endpoint = f"{url.rstrip('/')}/generate"

    while True:
        try:
            # 1. Styled User Input
            user_input = Prompt.ask("[user]❯[/user]")

            # Exit commands
            if user_input.lower() in ["exit", "quit", "bye", "stop"]:
                console.print("\n[info]🐗 Shutting down. Logic stored.[/info]")
                break

            if not user_input.strip():
                continue

            # 2. Animated Thinking Status
            with console.status("[italic ai]Consulting the Swarm...[/italic ai]", spinner="bouncingBar"):
                try:
                    # Send prompt to the Colab Brain
                    response = requests.post(
                        endpoint, 
                        json={"prompt": user_input}, 
                        timeout=20
                    )
                    response.raise_for_status()
                    data = response.json()
                    ai_reply = data.get("response", "Logic void: No data returned.")
                except requests.exceptions.RequestException as e:
                    ai_reply = f"[error]Connection Lost.[/error]\n[dim]Verify Colab is running and your link is correct.[/dim]"

            # 3. Styled Response Panel
            console.print(Panel(
                ai_reply, 
                title="[bold white]BOARHIRO[/bold white]", 
                title_align="left",
                border_style="ai",
                padding=(1, 1)
            ))
            console.print("") # Visual spacer

        except KeyboardInterrupt:
            console.print("\n[info]Session terminated.[/info]")
            break

if __name__ == "__main__":
    run_cli()