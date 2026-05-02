import os
import sys
import signal

PID_FILE = "boarhiro_train.pid"

def main():
    # Try to find the PID file relative to where the user is running from
    pid_path = PID_FILE
    if not os.path.exists(pid_path):
        # Also check the directory where this script lives (project root)
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        pid_path = os.path.join(script_dir, PID_FILE)

    if not os.path.exists(pid_path):
        print("No background training process found (no PID file).")
        sys.exit(0)

    with open(pid_path) as f:
        pid = int(f.read().strip())

    try:
        if sys.platform == "win32":
            import ctypes
            handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
            if handle:
                ctypes.windll.kernel32.TerminateProcess(handle, 0)
                ctypes.windll.kernel32.CloseHandle(handle)
            else:
                print(f"Process {pid} not found — may have already stopped.")
                os.remove(pid_path)
                return
        else:
            os.kill(pid, signal.SIGTERM)

        os.remove(pid_path)
        print(f"BOARHIRO background training stopped (PID {pid}).")

    except (ProcessLookupError, OSError):
        print(f"Process {pid} was not running.")
        if os.path.exists(pid_path):
            os.remove(pid_path)

if __name__ == "__main__":
    main()
