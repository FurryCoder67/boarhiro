import os, json
from rich.console import Console
from rich.prompt import Prompt
from .bridge import ask_boarhiro

CONFIG_PATH = os.path.expanduser("~/.boarhiro_config.json")
console = Console()

def run_cli():
    console.print("\n[bold white]  BOARHIRO[/bold white] [dim]v0.1.0[/dim]\n  " + "—"*20)
    
    if not os.path.exists(CONFIG_PATH):
        url = Prompt.ask("  [cyan]Enter Backend API URL[/cyan]")
        with open(CONFIG_PATH, "w") as f: json.dump({"api_url": url}, f)
        config = {"api_url": url}
    else:
        with open(CONFIG_PATH, "r") as f: config = json.load(f)

    while True:
        query = Prompt.ask("[bold white]>[/bold white]")
        if query.lower() in ["exit", "quit"]: break
        
        with console.status("", spinner="dots"):
            response = ask_boarhiro(query, config["api_url"])
        console.print(f"\n  [bold]BOARHIRO[/bold]\n  {response}\n")