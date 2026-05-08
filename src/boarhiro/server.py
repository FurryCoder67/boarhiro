"""
Local inference server for BOARHIRO.
Loads boarhiro_brain.pt and serves POST /generate -> {"response": "..."}
Runs on http://localhost:5000
"""
import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import torch

# ── Shared config (must match trainer.py) ────────────────────────────────────
BLOCK_SIZE = 128
PORT       = 5000
SERVER_PID_FILE = "boarhiro_server.pid"

def _project_root() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

# ── Model (identical to trainer.py) ──────────────────────────────────────────
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

# ── Generation ────────────────────────────────────────────────────────────────
def generate_response(model: BoarhiroModel, stoi: dict, itos: dict,
                      prompt: str, max_new_tokens: int = 200,
                      temperature: float = 0.8) -> str:
    device = next(model.parameters()).device
    model.eval()

    # Encode prompt — skip unknown chars
    ids = [stoi[ch] for ch in prompt if ch in stoi]
    if not ids:
        return "(no known characters in prompt)"

    # Keep only the last BLOCK_SIZE tokens as context
    ctx = torch.tensor([ids[-BLOCK_SIZE:]], dtype=torch.long, device=device)

    generated = []
    with torch.no_grad():
        for _ in range(max_new_tokens):
            logits = model(ctx)                        # (1, T, vocab)
            logits = logits[0, -1, :] / temperature    # last token logits
            probs  = torch.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1).item()
            generated.append(itos[next_id])
            # Slide context window
            next_tensor = torch.tensor([[next_id]], dtype=torch.long, device=device)
            ctx = torch.cat([ctx[:, 1:], next_tensor], dim=1)

    model.train()
    return "".join(generated)

# ── Model loader ──────────────────────────────────────────────────────────────
_model  = None
_stoi   = None
_itos   = None
_lock   = threading.Lock()

def _load_model():
    global _model, _stoi, _itos
    root       = _project_root()
    model_path = os.path.join(root, "boarhiro_brain.pt")
    data_path  = os.path.join(root, "data", "input.txt")

    if not os.path.exists(data_path):
        return False, "data/input.txt not found."

    with open(data_path, encoding="utf-8", errors="replace") as f:
        text = f.read()

    if not text.strip():
        return False, "data/input.txt is empty."

    chars      = sorted(set(text))
    stoi       = {ch: i for i, ch in enumerate(chars)}
    itos       = {i: ch for ch, i in stoi.items()}
    vocab_size = len(chars)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = BoarhiroModel(vocab_size).to(device)

    if os.path.exists(model_path):
        try:
            model.load_state_dict(
                torch.load(model_path, map_location=device, weights_only=True)
            )
        except RuntimeError as e:
            # Vocab mismatch — stale checkpoint, delete and start fresh
            print(f"[Server] Stale checkpoint detected ({e}). Deleting and starting fresh.", flush=True)
            os.remove(model_path)
            model = BoarhiroModel(vocab_size).to(device)
        except Exception as e:
            return False, f"Could not load model weights: {e}"

    _model = model
    _stoi  = stoi
    _itos  = itos
    return True, "OK"

# ── HTTP handler ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence request logs

    def _send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "model_loaded": _model is not None})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/generate":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data   = json.loads(body)
            prompt = data.get("prompt", "")
        except Exception:
            self._send_json(400, {"error": "invalid JSON"})
            return

        with _lock:
            if _model is None:
                ok, msg = _load_model()
                if not ok:
                    self._send_json(503, {"error": msg})
                    return

        reply = generate_response(_model, _stoi, _itos, prompt)
        self._send_json(200, {"response": reply})

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    root = _project_root()

    # Write PID
    with open(os.path.join(root, SERVER_PID_FILE), "w") as f:
        f.write(str(os.getpid()))

    # Pre-load model at startup
    ok, msg = _load_model()
    if ok:
        print(f"[Server] Model loaded. Listening on http://localhost:{PORT}", flush=True)
    else:
        print(f"[Server] Warning: {msg}", flush=True)
        print(f"[Server] Will retry loading when first request arrives.", flush=True)

    server = HTTPServer(("localhost", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pid_path = os.path.join(root, SERVER_PID_FILE)
        if os.path.exists(pid_path):
            os.remove(pid_path)

if __name__ == "__main__":
    main()
