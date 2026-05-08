import os
import sys
import time
import random
import threading
import argparse
import subprocess
import torch
import torch.nn.functional as F
import torch.optim as optim

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH     = "boarhiro_brain.pt"
DATA_FILE      = "data/input.txt"
LOG_FILE       = "boarhiro_train.log"
PID_FILE       = "boarhiro_train.pid"
BLOCK_SIZE     = 128
BATCH_SIZE     = 32
MIN_CHARS      = BLOCK_SIZE + 1
HUNT_INTERVAL  = 60       # seconds between hunter cycles
SAVE_EVERY     = 100      # save checkpoint every N epochs
LOG_EVERY      = 10       # log loss every N epochs
DEVICE         = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Tokenizer ─────────────────────────────────────────────────────────────────
def build_vocab(text: str):
    chars = sorted(set(text))
    stoi  = {ch: i for i, ch in enumerate(chars)}
    itos  = {i: ch for ch, i in stoi.items()}
    return stoi, itos, len(chars)

def encode(text: str, stoi: dict) -> list[int]:
    return [stoi[ch] for ch in text if ch in stoi]

# ── Model ─────────────────────────────────────────────────────────────────────
class BoarhiroModel(torch.nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128,
                 n_heads: int = 4, n_layers: int = 2):
        super().__init__()
        self.token_embed = torch.nn.Embedding(vocab_size, embed_dim)
        self.pos_embed   = torch.nn.Embedding(BLOCK_SIZE, embed_dim)
        encoder_layer    = torch.nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=n_heads,
            dim_feedforward=embed_dim * 4, dropout=0.1, batch_first=True
        )
        self.transformer = torch.nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.head        = torch.nn.Linear(embed_dim, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T = x.shape
        pos  = torch.arange(T, device=x.device)
        out  = self.token_embed(x) + self.pos_embed(pos)
        out  = self.transformer(out)
        return self.head(out)

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg: str):
    """Write timestamped message to log file and stdout."""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ── Hunter ────────────────────────────────────────────────────────────────────
def _hunt_one_cycle() -> str:
    samples = [
        "Function: optimized_search_v2",
        "Logic: recursive_backtracking",
        "Pattern: linear_regression_gradient",
        "Algorithm: depth_first_traversal",
        "Method: gradient_descent_optimizer",
    ]
    return f"\n{random.choice(samples)} | Timestamp: {time.time()}"

def run_hunter_thread(stop_event: threading.Event):
    os.makedirs("data", exist_ok=True)
    log("[Hunter] Active — collecting data...")
    while not stop_event.is_set():
        item = _hunt_one_cycle()
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(item)
        log(f"[Hunter] Collected: {item.strip()}")
        stop_event.wait(HUNT_INTERVAL)
    log("[Hunter] Stopped.")

# ── Bridge ────────────────────────────────────────────────────────────────────
def _project_root() -> str:
    """Always returns the project root regardless of cwd."""
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

def _read_url() -> str:
    env_url = os.environ.get("BOARHIRO_URL", "").strip()
    if env_url:
        return env_url
    root = _project_root()
    for candidate in ["link.txt", "src/link.txt"]:
        path = os.path.join(root, candidate)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                url = f.read().strip()
            if url:
                return url
    return ""

def start_bridge():
    url = _read_url()
    env = os.environ.copy()
    if url:
        env["BOARHIRO_URL"] = url
        print(f"[Bridge] Connecting to {url}")
    else:
        print("[Bridge] No URL in link.txt. Use 'seturl <url>' inside the chat.")
    try:
        subprocess.run(["boarhiro"], env=env)
    except FileNotFoundError:
        subprocess.run([sys.executable, "-m", "boarhiro.interface"], env=env)

# ── Infinite training loop ────────────────────────────────────────────────────
def train_forever(skip_hunter: bool = False):
    """
    Runs indefinitely:
      - Hunter thread keeps appending data in the background.
      - Every SAVE_EVERY epochs the model reloads the data file (picks up new
        data the hunter wrote) and saves a checkpoint.
      - Never stops on its own — killed only when the process is terminated.
    """
    log("[Pipeline] BOARHIRO background training started.")
    log(f"[Pipeline] PID: {os.getpid()}  |  Device: {DEVICE}")
    log(f"[Pipeline] Logs  -> {os.path.abspath(LOG_FILE)}")
    log(f"[Pipeline] Model -> {os.path.abspath(MODEL_PATH)}")

    # Write PID so stopboarhiro can kill it
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    # ── Hunter ────────────────────────────────────────────────────────────────
    stop_hunter = threading.Event()
    if not skip_hunter:
        threading.Thread(
            target=run_hunter_thread, args=(stop_hunter,), daemon=True
        ).start()

    # ── Wait for enough data ──────────────────────────────────────────────────
    log(f"[Pipeline] Waiting for {MIN_CHARS}+ chars in {DATA_FILE}...")
    while True:
        size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
        if size > MIN_CHARS:
            break
        time.sleep(2)
    log(f"[Pipeline] Data ready ({size} bytes). Building model...")

    # ── Initial model build ───────────────────────────────────────────────────
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    stoi, itos, vocab_size = build_vocab(text)
    data      = torch.tensor(encode(text, stoi), dtype=torch.long, device=DEVICE)
    model     = BoarhiroModel(vocab_size).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)

    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(
                torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
            )
            log(f"[Trainer] Resumed from checkpoint.")
        except Exception as e:
            log(f"[Trainer] Fresh start (checkpoint load failed: {e}).")

    model.train()
    log(f"[Trainer] Vocab={vocab_size}  Tokens={len(data)}  Running forever...")
    log("-" * 50)

    epoch = 0
    while True:   # ← runs until the process is killed
        epoch += 1

        # Re-read data every SAVE_EVERY epochs to pick up new hunter data
        if epoch % SAVE_EVERY == 0:
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    new_text = f.read()
                new_stoi, _, new_vocab = build_vocab(new_text)
                if new_vocab == vocab_size:          # vocab unchanged — safe reload
                    data = torch.tensor(
                        encode(new_text, new_stoi), dtype=torch.long, device=DEVICE
                    )
                    stoi = new_stoi
            except Exception:
                pass  # keep going with old data if file is mid-write

        ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
        x  = torch.stack([data[i : i + BLOCK_SIZE]         for i in ix])
        y  = torch.stack([data[i + 1 : i + BLOCK_SIZE + 1] for i in ix])

        logits = model(x)
        loss   = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if epoch % LOG_EVERY == 0:
            log(f"[Trainer] Epoch {epoch:>7}  |  Loss: {loss.item():.4f}")

        if epoch % SAVE_EVERY == 0:
            torch.save(model.state_dict(), MODEL_PATH)
            log(f"[Trainer] Checkpoint saved at epoch {epoch}.")

# ── Entry point (foreground pipeline — used by trainboarhiro) ─────────────────
def main():
    parser = argparse.ArgumentParser(
        description="BOARHIRO: hunt data → train forever in background → open bridge."
    )
    parser.add_argument(
        "--no-hunter", action="store_true",
        help="Skip the data hunter, train on existing data/input.txt"
    )
    parser.add_argument(
        "--foreground", action="store_true",
        help="Run training in the foreground instead of as a background process"
    )
    args = parser.parse_args()

    if args.foreground:
        # Blocking — useful for debugging
        train_forever(skip_hunter=args.no_hunter)
        return

    # ── Launch as a detached background process ───────────────────────────────
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # pythonw.exe = no console window on Windows
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable   # fallback (Linux/Mac or missing pythonw)

    cmd = [
        pythonw, "-m", "boarhiro.trainer", "--foreground",
    ]
    if args.no_hunter:
        cmd.append("--no-hunter")

    proc = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=open(os.path.join(project_root, LOG_FILE), "a"),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32" else 0,
        close_fds=True,
    )

    print("=" * 50)
    print("  BOARHIRO training started in the background.")
    print(f"  PID : {proc.pid}")
    print(f"  Log : {os.path.join(project_root, LOG_FILE)}")
    print(f"  Model will save every {SAVE_EVERY} epochs.")
    print()
    print("  Commands:")
    print("    boarhiro              — open the chat interface")
    print("    stopboarhiro          — stop background training")
    print("    Get-Content boarhiro_train.log -Wait   — watch live logs")
    print("=" * 50)

    # Open the bridge immediately so you can chat while it trains
    start_bridge()


# ── Background worker entry (called with --foreground by Popen above) ─────────
if __name__ == "__main__":
    main()
