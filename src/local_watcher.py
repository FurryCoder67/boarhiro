import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogicHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py") and "input.txt" not in event.src_path:
            with open(event.src_path, "r") as f:
                content = f.read()
            with open("data/input.txt", "a") as out:
                out.write(f"\n# User Logic Update: {event.src_path}\n{content}")
            print(f"🐗 BOARHIRO absorbed: {event.src_path}")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(LogicHandler(), path='.', recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()