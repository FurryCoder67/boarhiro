"""
Downloads the pre-trained BOARHIRO model from GitHub Releases on first run.
"""
import os
import sys
import urllib.request

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_USER  = "FurryCoder67"
GITHUB_REPO  = "boarhiro"
RELEASE_TAG  = "latest"
MODEL_FILE   = "boarhiro_brain.pt"
DOWNLOAD_URL = (
    f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"
    f"/releases/latest/download/{MODEL_FILE}"
)

def _project_root() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

def model_exists() -> bool:
    return os.path.exists(os.path.join(_project_root(), MODEL_FILE))

def download_model(show_progress: bool = True) -> bool:
    """
    Download boarhiro_brain.pt from GitHub Releases.
    Returns True on success, False on failure.
    """
    dest = os.path.join(_project_root(), MODEL_FILE)

    if show_progress:
        print(f"[Downloader] Fetching pre-trained model from GitHub...", flush=True)
        print(f"[Downloader] {DOWNLOAD_URL}", flush=True)

    def _progress(block_num, block_size, total_size):
        if not show_progress or total_size <= 0:
            return
        downloaded = block_num * block_size
        pct = min(100, downloaded * 100 // total_size)
        mb_done  = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"\r[Downloader] [{bar}] {pct}%  {mb_done:.1f}/{mb_total:.1f} MB",
              end="", flush=True)

    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, dest, reporthook=_progress)
        if show_progress:
            print()  # newline after progress bar
            print(f"[Downloader] Model saved to {dest}", flush=True)
        return True
    except Exception as e:
        if show_progress:
            print(f"\n[Downloader] Download failed: {e}", flush=True)
            print("[Downloader] Will start with an untrained model instead.", flush=True)
        # Clean up partial download
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except Exception:
                pass
        return False

def ensure_model(show_progress: bool = True) -> bool:
    """
    If no model exists, download it.
    Returns True if model is available (either already existed or downloaded).
    """
    if model_exists():
        return True
    return download_model(show_progress=show_progress)
