# BOARHIRO

A transformer-based neural AI that trains itself continuously and gets smarter the longer it runs.

## Install

```
pip install boarhiro
```

## Usage

```
boarhiro
```

That's it. On first run it automatically:
- Starts a local inference server
- Starts background training (runs forever, saves checkpoints)
- Starts a data hunter that fetches real text from the web
- Opens the chat interface

## Commands

| Command | Description |
|---|---|
| `help` | Show all commands |
| `status` | Show server + trainer status |
| `seturl <url>` | Point to a remote server |
| `update` | Upgrade to latest version |
| `exit` | Quit |

## Train manually

```
trainboarhiro              # runs forever in background
trainboarhiro --no-hunter  # use your own data/input.txt
stopboarhiro               # stop background training
```

## How it works

BOARHIRO is a character-level transformer trained locally on your machine. The longer it runs, the more data it collects and the better its responses get. No API keys, no cloud, no cost.

## Requirements

- Python 3.10+
- PyTorch (CPU or CUDA)

## License

MIT
