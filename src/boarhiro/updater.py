"""
Auto-updater for BOARHIRO.
Checks PyPI for new versions and prompts user to upgrade.
"""
import sys
import subprocess
import requests
from packaging import version

PACKAGE_NAME = "boarhiro"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"

def get_installed_version() -> str:
    """Get the currently installed version."""
    try:
        from importlib.metadata import version as get_version
        return get_version(PACKAGE_NAME)
    except Exception:
        return "0.0.0"

def get_latest_version() -> str | None:
    """Fetch the latest version from PyPI."""
    try:
        r = requests.get(PYPI_URL, timeout=3)
        if r.status_code == 200:
            data = r.json()
            return data["info"]["version"]
    except Exception:
        pass
    return None

def check_for_updates(silent: bool = False) -> bool:
    """
    Check if a newer version is available on PyPI.
    Returns True if an update is available.
    """
    current = get_installed_version()
    latest  = get_latest_version()

    if not latest:
        if not silent:
            print("[Updater] Could not check for updates (PyPI unreachable).", flush=True)
        return False

    try:
        if version.parse(latest) > version.parse(current):
            if not silent:
                print(f"\n[Updater] New version available: {latest} (you have {current})", flush=True)
                print(f"[Updater] Run: pip install --upgrade {PACKAGE_NAME}\n", flush=True)
            return True
    except Exception:
        pass

    return False

def auto_upgrade() -> bool:
    """
    Automatically upgrade to the latest version.
    Returns True if upgrade succeeded.
    """
    print("[Updater] Upgrading BOARHIRO...", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("[Updater] Upgrade complete. Restart boarhiro to use the new version.", flush=True)
        return True
    else:
        print(f"[Updater] Upgrade failed: {result.stderr.strip()}", flush=True)
        return False
