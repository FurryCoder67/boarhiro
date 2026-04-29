import os
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

# CONFIG
GITHUB_USER = "furrycoder67"
GITHUB_REPO = "boarhiro"
LINK_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/link.txt"

console = Console(theme=Theme({"info": "dim cyan", "user": "bold cyan", "ai": "bold magenta", "error": "bold red"}))

def get_brain_url():
    # Priority 1: Local file
    if os.path.exists("link.txt"):
        with open("link.txt", "r") as f:
            return f.read().strip()
    # Priority 2: GitHub
    try:
        r = requests.get(LINK_URL, timeout=3)
        if r.status_code == 200: return r.text.strip()
    except:
        return None
    return None

def run_cli():
    console.clear()
    banner = Text("🐗 BOARHIRO v0.2.0\nNeural Transformer Active", justify="center", style="ai")
    console.print(Panel(banner, border_style="bright_blue"))
    
    url = get_brain_url()
    if not url:
        console.print("[error]❌ Error: Link missing.[/error]")
        return

    endpoint = f"{url.rstrip('/')}/generate"

    while True:
        try:
            inp = Prompt.ask("[user]❯[/user]")
            if inp.lower() in ["exit", "quit"]: break
            
            with console.status("[italic ai]Neural Processing...[/italic ai]", spinner="dots"):
                try:
                    res = requests.post(endpoint, json={"prompt": inp}, timeout=30)
                    reply = res.json().get("response", "Logic void.")
                except:
                    reply = "[error]Link severed.[/error]"

            console.print(Panel(reply, title="[bold white]BOARHIRO[/bold white]", border_style="ai", padding=(1,1)))
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_cli()