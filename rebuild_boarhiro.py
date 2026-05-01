import os

def rebuild():
    print("Starting BOARHIRO Professional Rebuild (Emoji-Free Version)...")
    
    # 1. Create the new structure
    folders = ['src/boarhiro', 'data', 'tests']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # 2. Create the Configuration File
    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write("""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "boarhiro"
version = "0.1.0"
authors = [{ name="furrycoder67" }]
description = "Transformer-based neural logic hunter"
dependencies = ["torch", "requests", "rich"]

[project.scripts]
boarhiro = "boarhiro.interface:run_cli"

[tool.setuptools.packages.find]
where = ["src"]
""")

    # 3. Create the Package Init
    with open("src/boarhiro/__init__.py", "w", encoding="utf-8") as f:
        f.write("# BOARHIRO Package\n")

    # 4. Create the Professional Interface (Emojis removed for compatibility)
    with open("src/boarhiro/interface.py", "w", encoding="utf-8") as f:
        f.write("""import os, requests, time
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli():
    console.print(Panel("BOARHIRO SYSTEM ONLINE", style="bold magenta"))
    while True:
        prompt = input(">> ")
        if prompt.lower() in ['exit', 'quit']: break
        print("Connecting to brain...")
""")

    # 5. Create a clean Data file
    with open("data/input.txt", "w", encoding="utf-8") as f:
        f.write("# Paste your clean training data here\n")

    # 6. Create the training script
    with open("train.py", "w", encoding="utf-8") as f:
        f.write("""import os
import torch
import torch.nn.functional as F
import torch.optim as optim

MODEL_PATH = "boarhiro_brain.pt"
BLOCK_SIZE  = 128
BATCH_SIZE  = 32
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_vocab(text):
    chars = sorted(set(text))
    stoi  = {ch: i for i, ch in enumerate(chars)}
    itos  = {i: ch for ch, i in stoi.items()}
    return stoi, itos, len(chars)

def encode(text, stoi):
    return [stoi[ch] for ch in text]

class BoarhiroModel(torch.nn.Module):
    def __init__(self, vocab_size, embed_dim=128, n_heads=4, n_layers=2):
        super().__init__()
        self.token_embed = torch.nn.Embedding(vocab_size, embed_dim)
        self.pos_embed   = torch.nn.Embedding(BLOCK_SIZE, embed_dim)
        encoder_layer    = torch.nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=n_heads, dim_feedforward=embed_dim * 4,
            dropout=0.1, batch_first=True
        )
        self.transformer = torch.nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.head        = torch.nn.Linear(embed_dim, vocab_size)

    def forward(self, x):
        B, T = x.shape
        pos  = torch.arange(T, device=x.device)
        out  = self.token_embed(x) + self.pos_embed(pos)
        out  = self.transformer(out)
        return self.head(out)

def train_brain(epochs=200):
    if not os.path.exists("input.txt"):
        print("Error: No input.txt found. Upload it first!")
        return
    with open("input.txt", "r", encoding="utf-8") as f:
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
    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print(f"Resuming from checkpoint: {MODEL_PATH}")
        except Exception as e:
            print(f"Warning: Could not load checkpoint ({e}). Starting fresh.")
    model.train()
    print(f"BOARHIRO consuming data on {DEVICE} | vocab={vocab_size} | tokens={len(data)}")
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
    print(f"Brain saved to {MODEL_PATH}. Run the interface to talk to the new version.")

if __name__ == "__main__":
    train_brain(epochs=200)
""")

    print("\nSUCCESS! The structure is built.")
    print("Files created: src/boarhiro/, data/input.txt, train.py")

if __name__ == "__main__":
    rebuild()