# BOARHIRO Agent Architecture

## Overview

BOARHIRO v0.2.0 introduces a modular agent architecture inspired by Buildkite Agent, while maintaining compatibility with existing Python-based training and inference systems.

The new architecture is organized into self-contained, well-defined packages following Go/Rust patterns translated to Python:

- **Struct-like configuration** via `dataclasses`
- **Context-aware functions** with explicit error handling
- **Modular packages** with clear separation of concerns
- **Typed errors** for different failure modes

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    BOARHIRO CLI                         │
│              (boarhiro, trainboarhiro, etc.)            │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐  ┌─────▼─────┐  ┌────▼─────────┐
│   Interface  │  │   Config  │  │    Logger    │
│  (pkg.ui)    │  │  (pkg.config) │ (pkg.logger) │
└───────┬──────┘  └─────┬─────┘  └────┬─────────┘
        │               │             │
        └───────────────┼─────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐  ┌─────▼─────┐  ┌────▼─────────┐
│    Agent     │  │    API    │  │    Utils     │
│ (pkg.agent)  │  │ (pkg.api) │  │ (pkg.utils)  │
└───────┬──────┘  └─────┬─────┘  └────┬─────────┘
        │               │             │
        └───────────────┼─────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────────┐      ┌──────────▼────────┐
│  Core Services     │      │   Future: Jobs    │
│ (trainer, server,  │      │  (pkg.job)        │
│  downloader)       │      │  [Placeholder]    │
└────────────────────┘      └───────────────────┘
```

## Package Structure

```
src/boarhiro/
├── __init__.py              # Main package exports
├── interface.py             # CLI entry point (legacy, unchanged)
├── trainer.py               # Training loop (unchanged)
├── server.py                # Inference server (unchanged)
├── downloader.py            # Model bootstrapping (unchanged)
├── stopper.py               # Process termination (unchanged)
│
├── interface/               # NEW: Refactored UI components
│   ├── __init__.py
│   ├── main.py             # CLI event loop
│   ├── ui.py               # Rendering components
│   ├── commands.py         # Command handlers
│   └── status.py           # Status dashboard
│
├── agent/                   # NEW: Agent infrastructure
│   ├── __init__.py
│   ├── config.py           # Combined agent config
│   ├── worker.py           # Core worker (polling, execution)
│   └── lifecycle.py        # Startup, shutdown, signal handling
│
├── config/                  # NEW: Configuration management
│   ├── __init__.py
│   └── agent_config.py     # AgentConfig & WorkerConfig dataclasses
│
├── logger/                  # NEW: Structured logging
│   ├── __init__.py
│   └── structured.py       # JSON & text logging
│
├── api/                     # NEW: HTTP client
│   ├── __init__.py
│   └── client.py           # ServerClient class
│
├── job/                     # NEW: Job execution (placeholder)
│   └── __init__.py
│
└── utils/                   # NEW: Utilities
    ├── __init__.py
    └── errors.py           # Error hierarchy
```

## Key Components

### Configuration (`config.agent_config`)

**Purpose:** Centralized configuration using dataclasses (struct-like patterns)

```python
@dataclass
class AgentConfig:
    """Core agent configuration."""
    agent_name: str = "boarhiro-agent"
    agent_token: Optional[str] = None
    server_url: str = "http://localhost:5000"
    enable_training: bool = True
    enable_job_polling: bool = False  # Future
    debug: bool = False
    json_logs: bool = False

@dataclass
class WorkerConfig:
    """Worker pool configuration."""
    worker_id: str = "worker-0"
    max_concurrent_jobs: int = 1
    job_poll_interval_seconds: float = 5.0
```

### Logging (`logger.structured`)

**Purpose:** Structured logging with both plain-text and JSON output

Features:
- Four log levels: DEBUG, INFO, WARNING, ERROR, FATAL
- JSON output mode for machine parsing
- Plain-text mode for human readability
- Global configuration via `configure_logging()`
- Per-logger instances via `get_logger(name)`

Example:
```python
from boarhiro.logger import get_logger, configure_logging

configure_logging(json_output=False, debug=True)
logger = get_logger("trainer")
logger.info("Starting training", epoch=1, loss=0.5)
# Output: [2026-05-13T...] [INFO] [trainer] Starting training (epoch=1, loss=0.5)
```

### Agent Worker (`agent.worker`)

**Purpose:** Core worker orchestration (currently infrastructure, job polling is future)

```python
class AgentWorker:
    """Manages job lifecycle and worker state."""
    
    async def start(self) -> None:
        """Start worker - initializes model, begins polling."""
    
    async def stop(self) -> None:
        """Graceful shutdown."""
    
    def get_status(self) -> dict:
        """Current worker metrics."""
```

**Current State:** Infrastructure ready, job polling disabled (future)
**Future:** Enable `_polling_loop()` to start polling Buildkite-compatible job server

### Agent Lifecycle (`agent.lifecycle`)

**Purpose:** Signal handling, startup/shutdown coordination

Features:
- Cross-platform signal handling (Windows/Unix)
- Graceful shutdown with handler callbacks
- Shutdown state tracking

```python
lifecycle = AgentLifecycle()
lifecycle.setup_signal_handlers()
lifecycle.register_shutdown_handler(cleanup_database)
await lifecycle.shutdown()
```

### Error Hierarchy (`utils.errors`)

**Purpose:** Typed exceptions for different failure modes

```python
class BoarhiroError(Exception): pass
class ConfigError(BoarhiroError): pass
class ProcessError(BoarhiroError): pass
class ModelError(BoarhiroError): pass
class ServerError(BoarhiroError): pass
class JobError(BoarhiroError): pass
```

### API Client (`api.client`)

**Purpose:** HTTP client for server communication

```python
client = ServerClient("http://localhost:5000")
response = client.generate("Hello, world!", temperature=0.7)
is_healthy = client.health_check()
```

### Interface Components (`interface.*`)

**Purpose:** Modern CLI with modular UI rendering

- `ui.py`: Panel rendering, tables, status displays
- `commands.py`: Command implementations (help, status, jobs, metrics, etc.)
- `status.py`: Live status dashboard
- `main.py`: CLI event loop

## Design Decisions

### 1. Dataclasses for Configuration

**Why:** Type hints, validation, immutability options, clean serialization

```python
# Before: Plain dict with string keys
config = {"server_url": "...", "debug": False}

# After: Type-checked, self-documenting
config = AgentConfig(server_url="...", debug=False)
config.server_url  # IDE autocomplete, type checking
```

### 2. Async-Ready Architecture

**Why:** Prepare for concurrent job execution and polling

```python
# Even though currently single-threaded, infrastructure supports:
async def main():
    worker = AgentWorker(agent_config, worker_config)
    await worker.start()  # Scalable to multiple workers
```

### 3. Structured Logging

**Why:** Better debuggability, machine-parseable for log aggregation

```python
# Text: Readable for human logs
logger.info("Job started", job_id=123, duration=5.2)
# [2026-05-13T10:30:00Z] [INFO] [worker] Job started (job_id=123, duration=5.2)

# JSON: Parseable for elk/splunk
logger.info("Job started", job_id=123, duration=5.2)
# {"timestamp": "2026-05-13T10:30:00Z", "level": "INFO", "message": "...", "job_id": 123}
```

### 4. Backward Compatibility

**Why:** Existing code continues to work without modification

- Original `interface.py` entry point unchanged
- `trainer.py`, `server.py` unchanged
- New modules are additive, not replacing

```python
# Old code still works:
from boarhiro.trainer import main
from boarhiro.interface import run_cli

# New code can use new modules:
from boarhiro.config import AgentConfig
from boarhiro.logger import get_logger
from boarhiro.agent import AgentWorker
```

## Future Extensions

### 1. Job Polling (Phase N)

Uncomment in `agent/worker.py:_polling_loop()` to enable:

```python
# Connect to Buildkite-compatible job server
jobs = await self._poll_jobs()
for job in jobs:
    await self._execute_job(job)
```

### 2. Persistent Agent State

Track job history, metrics, and worker state in a database:

```python
metrics = {
    "jobs_completed": 1024,
    "success_rate": 0.98,
    "avg_execution_time": 12.5,
}
```

### 3. Multi-Worker Pool

Scale horizontally with coordinated worker pool:

```python
workers = [AgentWorker(config, WorkerConfig(worker_id=f"w-{i}"))
           for i in range(4)]
await asyncio.gather(w.start() for w in workers)
```

### 4. Remote Job Execution

Execute training/inference jobs on remote hardware via job system

## Migration Guide

**For existing code:** No changes needed! All original entry points work.

**To use new modules:**

```python
# Configuration
from boarhiro.config import AgentConfig, WorkerConfig

# Logging
from boarhiro.logger import get_logger, configure_logging
configure_logging(debug=True)
logger = get_logger("mymodule")

# Agent infrastructure
from boarhiro.agent import AgentWorker
from boarhiro.agent.lifecycle import AgentLifecycle

# Error handling
from boarhiro.utils import BoarhiroError, ConfigError, ServerError

# API client
from boarhiro.api import ServerClient
client = ServerClient("http://localhost:5000")
```

## Testing

Run the new modules:

```bash
# Test imports
python -c "from boarhiro.agent import AgentWorker; print('✓')"

# Test configuration
python -c "from boarhiro.config import AgentConfig; c = AgentConfig(); print(c.agent_name)"

# Test logging
python -c "from boarhiro.logger import get_logger; l = get_logger('test'); l.info('OK')"
```

## Version History

- **v0.1.0**: Initial character-level transformer with self-training
- **v0.2.0**: Modular agent architecture, structured logging, improved CLI
- **v0.3.0** (future): Job polling and Buildkite integration
- **v1.0.0** (future): Multi-worker pool, remote execution, production hardening
