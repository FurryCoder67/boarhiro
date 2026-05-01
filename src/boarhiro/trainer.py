import os
import sys
import torch
import torch.nn.functional as F
import torch.optim as optim

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = "boarhiro_brain.pt"
BLOCK_SIZE  = 128
BATCH_SIZE  = 32
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Tokenizer (character-level) ───────────────────────────────────────────────
def build_vocab(text: str):
    chars = sorted(set(text))
    stoi  = {ch: i for i, ch in enumerate(chars)}
    itos  = {i: ch for ch, i in stoi.items()}
    return stoi, itos, len(chars)

def encode(text: str, stoi: dict) -> list[int]:
    return [stoi[ch] for ch in text]

# ── Model (minimal transformer) ───────────────────────────────────────────────
class BoarhiroModel(torch.nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128, n_heads: int = 4, n_layers: int = 2):
        super().__init__()
        self.token_embed = torch.nn.Embedding(vocab_size, embed_dim)
        self.pos_embed   = torch.nn.Embedding(BLOCK_SIZE, embed_dim)
        encoder_layer    = torch.nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=n_heads, dim_feedforward=embed_dim * 4,
            dropout=0.1, batch_first=True
        )
        self.transformer = torch.nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.head        = torch.nn.Linear(embed_dim, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T = x.shape
        pos  = torch.arange(T, device=x.device)
        out  = self.token_embed(x) + self.pos_embed(pos)
        out  = self.transformer(out)
        return self.head(out)

# ── Training loop ─────────────────────────────────────────────────────────────
def train_brain(epochs: int = 200):
    # Look for input.txt next to cwd first, then data/input.txt
    for candidate in ["input.txt", "data/input.txt"]:
        if os.path.exists(candidate):
            input_path = candidate
            break
    else:
        print("Error: No input.txt found. Place it in the project root or data/ folder.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: input.txt is empty.")
        sys.exit(1)

    stoi, itos, vocab_size = build_vocab(text)
    data = torch.tensor(encode(text, stoi), dtype=torch.long, device=DEVICE)

    if len(data) <= BLOCK_SIZE:
        print(f"Error: input.txt is too short (need > {BLOCK_SIZE} characters).")
        sys.exit(1)

    model     = BoarhiroModel(vocab_size).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)

    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
            print(f"Resuming from checkpoint: {MODEL_PATH}")
        except Exception as e:
            print(f"Warning: Could not load checkpoint ({e}). Starting fresh.")

    model.train()
    print(f"BOARHIRO training on {DEVICE}")
    print(f"Vocab size : {vocab_size}")
    print(f"Data tokens: {len(data)}")
    print(f"Epochs     : {epochs}")
    print("-" * 50)

    for epoch in range(1, epochs + 1):
        ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
        x  = torch.stack([data[i : i + BLOCK_SIZE]         for i in ix])
        y  = torch.stack([data[i + 1 : i + BLOCK_SIZE + 1] for i in ix])

        logits = model(x)
        loss   = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:>4}/{epochs}  |  Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    print("-" * 50)
    print(f"Brain saved to {MODEL_PATH}")
    print("Run 'boarhiro' to talk to the new version.")

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train the BOARHIRO brain.")
    parser.add_argument(
        "--epochs", type=int, default=200,
        help="Number of training epochs (default: 200)"
    )
    args = parser.parse_args()
    train_brain(epochs=args.epochs)

if __name__ == "__main__":
    main()
