import os, requests, time
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli():
    console.print(Panel("BOARHIRO SYSTEM ONLINE", style="bold magenta"))
    while True:
        prompt = input(">> ")
        if prompt.lower() in ['exit', 'quit']: break
        print("Connecting to brain...")
