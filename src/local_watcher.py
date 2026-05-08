import os
import time
import subprocess

WATCH_FILE = "data/input.txt"

def get_file_size():
    return os.path.getsize(WATCH_FILE) if os.path.exists(WATCH_FILE) else 0

def push_to_github():
    print("New logic detected! Shipping to GitHub...")
    subprocess.run(["git", "add", WATCH_FILE])
    subprocess.run(["git", "commit", "-m", "BOARHIRO Auto-Update: New data added"])
    subprocess.run(["git", "push", "origin", "main"])
    print("Shipped.")

def start_watcher():
    print("Local Watcher is online. Waiting for data...")
    last_size = get_file_size()
    
    while True:
        current_size = get_file_size()
        if current_size > last_size:
            push_to_github()
            last_size = current_size
        
        time.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    start_watcher()