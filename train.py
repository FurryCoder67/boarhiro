import os
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
        B, T    = x.shape
        pos     = torch.arange(T, device=x.device)
        out     = self.token_embed(x) + self.pos_embed(pos)
        out     = self.transformer(out)
        return self.head(out)

# ── Training loop ─────────────────────────────────────────────────────────────
def train_brain(epochs: int = 200):
    input_path = "input.txt"
    if not os.path.exists(input_path):
        print("Error: No input.txt found. Upload it first!")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: input.txt is empty.")
        return

    stoi, itos, vocab_size = build_vocab(text)
    data = torch.tensor(encode(text, stoi), dtype=torch.long, device=DEVICE)

    if len(data) <= BLOCK_SIZE:
        print(f"Error: input.txt is too short (need > {BLOCK_SIZE} characters).")
        return

    model     = BoarhiroModel(vocab_size).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)

    # Load existing checkpoint if available
    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print(f"Resuming from checkpoint: {MODEL_PATH}")
        except Exception as e:
            print(f"Warning: Could not load checkpoint ({e}). Starting fresh.")

    model.train()
    print(f"BOARHIRO is consuming data on {DEVICE}...")
    print(f"Vocab size: {vocab_size}  |  Data tokens: {len(data)}")
    print("-" * 50)

    for epoch in range(1, epochs + 1):
        # Random batch of context windows
        ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
        x  = torch.stack([data[i : i + BLOCK_SIZE]     for i in ix])
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
    print("Run the interface in Kiro to talk to the new version.")


if __name__ == "__main__":
    train_brain(epochs=200)
