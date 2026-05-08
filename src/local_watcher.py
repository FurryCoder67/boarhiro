import os
import sys
import time
import subprocess
import io

# Force UTF-8 output so no encoding crashes on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

WATCH_FILE   = "data/input.txt"
WATCHER_PID  = "boarhiro_watcher.pid"

def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_file_size(path: str) -> int:
    return os.path.getsize(path) if os.path.exists(path) else 0

def push_to_github(path: str, root: str):
    print("Watcher: new data detected, pushing to GitHub...", flush=True)
    subprocess.run(["git", "add", path], cwd=root)
    subprocess.run(["git", "commit", "-m", "BOARHIRO Auto-Update: new training data"], cwd=root)
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=root, capture_output=True, text=True
    )
    if result.returncode == 0:
        print("Watcher: pushed successfully.", flush=True)
    else:
        print(f"Watcher: push failed — {result.stderr.strip()}", flush=True)

def start_watcher():
    root      = _project_root()
    data_path = os.path.join(root, WATCH_FILE)
    pid_path  = os.path.join(root, WATCHER_PID)

    # Write PID so the launcher can check if we're already running
    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))

    print(f"Watcher: online (PID {os.getpid()}), watching {data_path}", flush=True)
    last_size = get_file_size(data_path)

    try:
        while True:
            current_size = get_file_size(data_path)
            if current_size > last_size:
                push_to_github(data_path, root)
                last_size = current_size
            time.sleep(10)
    finally:
        if os.path.exists(pid_path):
            os.remove(pid_path)

if __name__ == "__main__":
    start_watcher()
