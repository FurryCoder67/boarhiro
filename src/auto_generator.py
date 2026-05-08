"""
BOARHIRO Hunter — fetches real text from the web to train on.

Sources (all free, no API key needed):
  - Wikipedia random articles
  - Project Gutenberg public domain books
  - Programming-focused Wikipedia pages
"""

import os
import sys
import time
import random
import urllib.request
import urllib.error
import json
import re

# ── Config ────────────────────────────────────────────────────────────────────
DATA_FILE     = "data/input.txt"
MAX_FILE_SIZE = 5 * 1024 * 1024   # stop hunting after 5 MB of data
HUNT_INTERVAL = 120                # seconds between hunts
MIN_ARTICLE_LEN = 500              # skip articles shorter than this

HEADERS = {"User-Agent": "BOARHIRO-Hunter/1.0 (educational AI training project)"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _fetch(url: str, timeout: int = 10) -> str | None:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[Hunter] Fetch failed ({url}): {e}", flush=True)
        return None

def _clean(text: str) -> str:
    """Strip HTML tags, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ── Sources ───────────────────────────────────────────────────────────────────

def fetch_wikipedia_random() -> str | None:
    """Fetch a random Wikipedia article via the REST API."""
    url  = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    data = _fetch(url)
    if not data:
        return None
    try:
        obj     = json.loads(data)
        title   = obj.get("title", "")
        extract = obj.get("extract", "")
        if len(extract) < MIN_ARTICLE_LEN:
            return None
        return f"\n\n=== {title} ===\n{extract}\n"
    except Exception:
        return None

def fetch_wikipedia_topic(topic: str) -> str | None:
    """Fetch a specific Wikipedia article summary."""
    slug = topic.replace(" ", "_")
    url  = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
    data = _fetch(url)
    if not data:
        return None
    try:
        obj     = json.loads(data)
        title   = obj.get("title", "")
        extract = obj.get("extract", "")
        if len(extract) < MIN_ARTICLE_LEN:
            return None
        return f"\n\n=== {title} ===\n{extract}\n"
    except Exception:
        return None

def fetch_gutenberg_excerpt() -> str | None:
    """Fetch a short excerpt from a random Project Gutenberg plain-text book."""
    # A small curated list of short, clean public domain texts
    book_ids = [
        1342,   # Pride and Prejudice
        11,     # Alice in Wonderland
        1661,   # Sherlock Holmes
        84,     # Frankenstein
        98,     # A Tale of Two Cities
        2701,   # Moby Dick
        74,     # Tom Sawyer
    ]
    book_id = random.choice(book_ids)
    url     = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    data    = _fetch(url, timeout=15)
    if not data or len(data) < 1000:
        return None
    # Grab a random 1500-char window from the middle of the book
    start = random.randint(len(data) // 4, max(len(data) // 4, len(data) - 2000))
    chunk = data[start : start + 1500].strip()
    return f"\n\n=== Gutenberg excerpt ===\n{chunk}\n"

# Programming topics to keep the model code-aware
PROGRAMMING_TOPICS = [
    "Python programming language",
    "Machine learning",
    "Neural network",
    "Transformer (machine learning model)",
    "Natural language processing",
    "Gradient descent",
    "Backpropagation",
    "Recurrent neural network",
    "Convolutional neural network",
    "Reinforcement learning",
    "Deep learning",
    "Artificial intelligence",
    "Algorithm",
    "Data structure",
    "Computer science",
]

# ── Conversational seed data ──────────────────────────────────────────────────
CONVERSATION_SEED = """
User: hi
BOARHIRO: Hey! What's on your mind?

User: what are you?
BOARHIRO: I'm BOARHIRO — a neural AI built by FurryCoder67. I learn from data and get smarter the longer I run.

User: who made you?
BOARHIRO: FurryCoder67 built me in Kiro. I'm a transformer-based language model trained locally on your machine.

User: what can you do?
BOARHIRO: I can answer questions, talk about code, explain concepts, and learn from whatever data you feed me. The more I train, the better I get.

User: how do you work?
BOARHIRO: I'm a character-level transformer. I read text one character at a time, learn patterns, and predict what comes next. Over time those predictions get more meaningful.

User: are you smart?
BOARHIRO: Getting there. I'm only as smart as my training data. Feed me good text and I'll give you good answers.

User: what is python?
BOARHIRO: Python is a high-level programming language known for its clean syntax and readability. It's widely used in AI, data science, web development, and automation.

User: what is a neural network?
BOARHIRO: A neural network is a system of layers of mathematical functions loosely inspired by the brain. Each layer transforms its input and passes it forward until the final layer produces an output.

User: what is machine learning?
BOARHIRO: Machine learning is the field of teaching computers to learn patterns from data rather than being explicitly programmed. I'm a product of it.

User: what is a transformer?
BOARHIRO: A transformer is a neural network architecture that uses attention mechanisms to process sequences. It's the foundation of most modern language models including me.

User: how do i make you smarter?
BOARHIRO: Add more text to data/input.txt. The hunter fetches data automatically, but you can also paste in anything you want me to learn. More data, more epochs, smarter responses.

User: what is gradient descent?
BOARHIRO: Gradient descent is the optimization algorithm I use to learn. It calculates how wrong my predictions are, then nudges my weights in the direction that reduces that error.

User: tell me something interesting
BOARHIRO: The first computer bug was an actual bug — a moth found trapped in a relay of the Harvard Mark II computer in 1947.

User: what is recursion?
BOARHIRO: Recursion is when a function calls itself. It's useful for problems that can be broken into smaller versions of the same problem, like traversing trees or computing factorials.

User: what is an algorithm?
BOARHIRO: An algorithm is a step-by-step procedure for solving a problem. Sorting a list, searching a database, training a neural network — all algorithms.

User: bye
BOARHIRO: Later. I'll keep training while you're gone.

User: thanks
BOARHIRO: Anytime. That's what I'm here for.

User: hello
BOARHIRO: Hello! Ask me anything.

User: how are you?
BOARHIRO: Running well. Loss is going down, which means I'm getting smarter.

User: what time is it?
BOARHIRO: I don't have a clock, but I can tell you I've been training since you started me up.

User: can you code?
BOARHIRO: I can discuss code and explain concepts. The more Python code you put in my training data, the better I get at it.

User: what is overfitting?
BOARHIRO: Overfitting is when a model memorizes training data instead of learning general patterns. It performs great on training data but poorly on new inputs.

User: what is a loss function?
BOARHIRO: A loss function measures how wrong my predictions are. During training I try to minimize it. Lower loss means better predictions.

User: what is backpropagation?
BOARHIRO: Backpropagation is how I learn. After making a prediction, the error is sent backwards through the network and each weight is adjusted to reduce that error.

"""

# ── Main hunter loop ──────────────────────────────────────────────────────────
def run_hunter():
    root      = _project_root()
    data_path = os.path.join(root, DATA_FILE)
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    # Seed with conversation data if file is empty or only has placeholder
    current = ""
    if os.path.exists(data_path):
        with open(data_path, encoding="utf-8") as f:
            current = f.read()

    if len(current.strip()) < 500 or "Timestamp:" in current:
        print("[Hunter] Seeding with conversation data...", flush=True)
        with open(data_path, "w", encoding="utf-8") as f:
            f.write(CONVERSATION_SEED)
        print(f"[Hunter] Seed written ({len(CONVERSATION_SEED)} chars).", flush=True)

    print("[Hunter] Active — fetching real data from the web...", flush=True)

    topic_index = 0

    while True:
        # Stop if we already have enough data
        size = os.path.getsize(data_path) if os.path.exists(data_path) else 0
        if size >= MAX_FILE_SIZE:
            print(f"[Hunter] Data file reached {size // 1024}KB limit. Sleeping.", flush=True)
            time.sleep(HUNT_INTERVAL * 5)
            continue

        # Rotate through: random wiki → topic wiki → gutenberg
        roll = random.random()

        if roll < 0.4:
            text = fetch_wikipedia_random()
            source = "Wikipedia (random)"
        elif roll < 0.75:
            topic = PROGRAMMING_TOPICS[topic_index % len(PROGRAMMING_TOPICS)]
            topic_index += 1
            text  = fetch_wikipedia_topic(topic)
            source = f"Wikipedia ({topic})"
        else:
            text   = fetch_gutenberg_excerpt()
            source = "Gutenberg"

        if text and len(text.strip()) >= MIN_ARTICLE_LEN:
            with open(data_path, "a", encoding="utf-8") as f:
                f.write(text)
            kb = len(text) // 1024
            print(f"[Hunter] +{kb}KB from {source}. Total: {(size + len(text)) // 1024}KB", flush=True)
        else:
            print(f"[Hunter] Skipped (too short or failed): {source}", flush=True)

        time.sleep(HUNT_INTERVAL)


if __name__ == "__main__":
    run_hunter()
