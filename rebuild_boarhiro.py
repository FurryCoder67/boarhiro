import os
import shutil

def rebuild():
    # 1. List of files/folders to move or clean up
    print("🐗 Starting BOARHIRO Professional Rebuild...")
    
    # Create the new structure
    folders = ['src/boarhiro', 'data', 'tests']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created: {folder}")

    # 2. Create the Configuration File (The "Passport")
    with open("pyproject.toml", "w") as f:
        f.write("""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "boarhiro"
version = "0.1.0"
authors = [{ name="furrycoder67" }]
description = "Transformer-based neural logic hunter"
dependencies = ["torch", "requests", "rich"]

[project.scripts]
boarhiro = "boarhiro.interface:run_cli"

[tool.setuptools.packages.find]
where = ["src"]
""")

    # 3. Create the Package Init
    with open("src/boarhiro/__init__.py", "w") as f:
        f.write("# BOARHIRO Package")

    # 4. Create the Professional Interface
    with open("src/boarhiro/interface.py", "w") as f:
        f.write("""import os, requests, time
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli():
    console.print(Panel("🐗 BOARHIRO SYSTEM ONLINE", style="bold magenta"))
    # This is where the magic happens
    while True:
        prompt = input("❯ ")
        if prompt.lower() in ['exit', 'quit']: break
        print("Connecting to brain...")
""")

    # 5. Create a clean Data file
    with open("data/input.txt", "w") as f:
        f.write("# Paste your 10 clean Python functions here later\n")

    print("\n✅ DONE! Your folder is now 'Professional Standard'.")
    print("👉 Next step: 'git add .', 'git commit', and 'git push'.")

if __name__ == "__main__":
    rebuild()