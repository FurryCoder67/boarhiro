# BOARHIRO API Reference

Complete API documentation for the modular BOARHIRO architecture.

## Configuration API

### `AgentConfig`

Main agent configuration dataclass.

```python
from boarhiro.config import AgentConfig

config = AgentConfig(
    agent_name="boarhiro-prod",
    server_url="http://localhost:5000",
    enable_training=True,
    enable_job_polling=False,
    debug=False,
    json_logs=False,
)

# Access properties
print(config.agent_name)       # "boarhiro-prod"
print(config.server_url)       # "http://localhost:5000"
print(config.tags)             # {"os": "local", "arch": "cpu"}
```

**Properties:**

- `agent_name: str` — Agent identifier (default: "boarhiro-agent")
- `agent_token: Optional[str]` — Authentication token (default: None)
- `build_path: str` — Working directory (default: "/tmp/boarhiro-builds")
- `model_path: str` — Model file path (default: "boarhiro_brain.pt")
- `data_path: str` — Training data path (default: "data/input.txt")
- `server_url: str` — Server base URL (default: "http://localhost:5000")
- `server_port: int` — Server port (default: 5000)
- `tags: Dict[str, str]` — Metadata tags (default: {"os": "local", "arch": "cpu"})
- `metadata: Dict[str, str]` — Custom metadata (default: {})
- `enable_training: bool` — Enable training (default: True)
- `enable_job_polling: bool` — Enable job polling (default: False)
- `no_hunter: bool` — Disable data hunting (default: False)
- `debug: bool` — Debug mode (default: False)
- `json_logs: bool` — JSON log output (default: False)

### `WorkerConfig`

Worker pool configuration dataclass.

```python
from boarhiro.config import WorkerConfig

config = WorkerConfig(
    worker_id="worker-0",
    max_concurrent_jobs=1,
    job_poll_interval_seconds=5.0,
    job_execution_timeout_seconds=3600.0,
)
```

**Properties:**

- `worker_id: str` — Worker identifier (default: "worker-0")
- `max_concurrent_jobs: int` — Concurrent job limit (default: 1)
- `job_poll_interval_seconds: float` — Poll frequency (default: 5.0)
- `job_execution_timeout_seconds: float` — Job timeout (default: 3600.0)
- `heartbeat_interval_seconds: float` — Heartbeat frequency (default: 30.0)
- `max_retries: int` — Retry count (default: 3)
- `retry_backoff_seconds: float` — Retry delay (default: 5.0)
- `capture_stdout: bool` — Capture output (default: True)
- `stream_logs: bool` — Stream logs (default: True)

---

## Logging API

### `StructuredLogger`

Core logger class for structured output.

```python
from boarhiro.logger import StructuredLogger, LogLevel

logger = StructuredLogger(
    name="trainer",
    json_output=False,
    debug=True,
)

logger.debug("Debug message", epoch=1)
logger.info("Training started", loss=0.5)
logger.warning("High loss detected", loss=1.2)
logger.error("Training failed", reason="CUDA error")
logger.fatal("Unrecoverable error", code=1)
```

**Methods:**

- `debug(message: str, **kwargs) -> None` — Log debug message
- `info(message: str, **kwargs) -> None` — Log info message
- `warning(message: str, **kwargs) -> None` — Log warning message
- `error(message: str, **kwargs) -> None` — Log error message
- `fatal(message: str, **kwargs) -> None` — Log fatal message

**Parameters:**

- `message`: Log message text
- `**kwargs`: Additional structured fields (key=value pairs)

### `get_logger(name: str) -> StructuredLogger`

Get or create a named logger instance (cached).

```python
from boarhiro.logger import get_logger

logger = get_logger("my_module")  # Creates once, reused thereafter
logger.info("Module started")
```

### `configure_logging(json_output: bool = False, debug: bool = False) -> None`

Configure global logging behavior for all loggers.

```python
from boarhiro.logger import configure_logging

configure_logging(json_output=False, debug=True)
logger = get_logger("app")
logger.debug("Debug enabled globally")  # Now logs at DEBUG level
```

**Parameters:**

- `json_output: bool` — Enable JSON output format
- `debug: bool` — Enable DEBUG level logging

### `LogLevel` Enum

Log level enumeration.

```python
from boarhiro.logger import LogLevel

LogLevel.DEBUG      # "DEBUG"
LogLevel.INFO       # "INFO"
LogLevel.WARNING    # "WARNING"
LogLevel.ERROR      # "ERROR"
LogLevel.FATAL      # "FATAL"
```

---

## Agent API

### `AgentWorker`

Core agent worker orchestration class.

```python
from boarhiro.agent import AgentWorker
from boarhiro.config import AgentConfig, WorkerConfig

agent_config = AgentConfig(agent_name="worker-1")
worker_config = WorkerConfig(worker_id="w-1")

worker = AgentWorker(agent_config, worker_config)

# Start worker (async)
import asyncio
await worker.start()

# Get status
status = worker.get_status()
print(status["is_running"])
print(status["jobs_completed"])

# Stop worker (async)
await worker.stop()
```

**Methods:**

- `async start() -> None` — Start the worker
- `async stop() -> None` — Stop the worker gracefully
- `get_status() -> dict` — Get current status

**Status Dictionary:**

```python
{
    "worker_id": "w-1",
    "is_running": True,
    "jobs_completed": 42,
    "jobs_successful": 40,
    "current_job": None,
}
```

### `AgentLifecycle`

Manages agent lifecycle and signal handling.

```python
from boarhiro.agent.lifecycle import AgentLifecycle

lifecycle = AgentLifecycle()

# Setup signal handlers (SIGINT, SIGTERM, etc.)
lifecycle.setup_signal_handlers()

# Register cleanup callbacks
async def cleanup():
    print("Cleaning up...")

lifecycle.register_shutdown_handler(cleanup)

# Perform shutdown
await lifecycle.shutdown()
```

**Methods:**

- `setup_signal_handlers() -> None` — Install OS signal handlers
- `register_shutdown_handler(handler: Callable) -> None` — Register shutdown callback
- `async shutdown() -> None` — Execute shutdown sequence

**Properties:**

- `is_shutting_down: bool` — Check if shutdown initiated

---

## API Client

### `ServerClient`

HTTP client for server communication.

```python
from boarhiro.api import ServerClient

client = ServerClient(
    server_url="http://localhost:5000",
    timeout=30.0,
)

# Generate response
response = client.generate(
    prompt="Hello, world!",
    temperature=0.7,
)
print(response)

# Health check
is_healthy = client.health_check()
if is_healthy:
    print("Server is online")
```

**Methods:**

- `generate(prompt: str, temperature: float = 0.7) -> str` — Generate response
  - Raises: `ServerError` if request fails
  
- `health_check() -> bool` — Check server health
  - Returns: True if server responds, False otherwise

**Exceptions:**

Raises `boarhiro.utils.ServerError` on communication failure:

```python
from boarhiro.api import ServerClient
from boarhiro.utils import ServerError

client = ServerClient("http://invalid-host:5000")

try:
    response = client.generate("test")
except ServerError as e:
    print(f"Server error: {e.message}")
    print(f"Context: {e.context}")
```

---

## Error Handling

### Error Hierarchy

```python
from boarhiro.utils import (
    BoarhiroError,
    ConfigError,
    ProcessError,
    ModelError,
    ServerError,
    JobError,
)

# Base exception
try:
    ...
except BoarhiroError as e:
    print(e.message)
    print(e.context)

# Specific exceptions
try:
    config = AgentConfig()
except ConfigError as e:
    # Configuration validation failed
    pass

try:
    client.generate("test")
except ServerError as e:
    # Server communication failed
    pass
```

**Exception Classes:**

- `BoarhiroError` — Base exception with message and context
- `ConfigError` — Configuration error
- `ProcessError` — Process execution error
- `ModelError` — Model operation error
- `ServerError` — Server communication error
- `JobError` — Job execution error

**Properties:**

- `message: str` — Error message
- `context: dict` — Additional context information

---

## Interface Components

### UI Rendering

```python
from boarhiro.interface.ui import (
    render_banner,
    render_status_panel,
    render_metrics_panel,
    render_help_table,
    render_jobs_table,
    render_error,
    render_success,
    render_info,
)

# Render banner
banner = render_banner()
console.print(banner)

# Render status panel
status_panel = render_status_panel({
    "agent_name": "boarhiro-prod",
    "trainer_running": True,
    "server_running": True,
    "watcher_running": True,
    "model_status": "Ready",
})
console.print(status_panel)

# Render metrics
metrics_panel = render_metrics_panel({
    "jobs_completed": 100,
    "jobs_successful": 98,
    "success_rate": "98%",
    "avg_exec_time": "5.2s",
})
console.print(metrics_panel)

# Messages
render_error("Something went wrong")
render_success("Operation completed")
render_info("Information message")
```

### Command Handler

```python
from boarhiro.interface.commands import CommandHandler
from rich.console import Console

console = Console()
handler = CommandHandler(console, project_root="/path/to/boarhiro")

# Handle commands
handler.handle_help()
handler.handle_status()
handler.handle_jobs()
handler.handle_metrics()
handler.handle_seturl("http://remote-server:5000")
handler.handle_update()

# Job tracking
handler.add_job(
    job_id="job-123",
    status="success",
    duration="5.2s",
    output="Response text...",
)
```

### Status Dashboard

```python
from boarhiro.interface.status import StatusDashboard
from rich.console import Console

console = Console()
dashboard = StatusDashboard(console)

dashboard.update_status({
    "agent_name": "boarhiro",
    "trainer_running": True,
    "server_running": True,
    "watcher_running": True,
    "model_status": "Ready",
})

dashboard.update_metrics({
    "jobs_completed": 42,
    "jobs_successful": 40,
    "success_rate": "95%",
    "avg_exec_time": "4.8s",
})

dashboard.display()
```

---

## Examples

### Complete Agent Setup

```python
import asyncio
from boarhiro.config import AgentConfig, WorkerConfig
from boarhiro.agent import AgentWorker
from boarhiro.agent.lifecycle import AgentLifecycle
from boarhiro.logger import get_logger, configure_logging

async def main():
    # Configure logging
    configure_logging(json_output=False, debug=True)
    logger = get_logger("main")
    
    # Setup configs
    agent_config = AgentConfig(
        agent_name="boarhiro-prod",
        debug=True,
    )
    worker_config = WorkerConfig(
        worker_id="w-1",
        max_concurrent_jobs=1,
    )
    
    # Create agent
    worker = AgentWorker(agent_config, worker_config)
    
    # Setup lifecycle
    lifecycle = AgentLifecycle()
    lifecycle.setup_signal_handlers()
    lifecycle.register_shutdown_handler(worker.stop)
    
    try:
        logger.info("Starting agent", agent=agent_config.agent_name)
        await worker.start()
        
        # Keep running...
        while True:
            status = worker.get_status()
            logger.debug("Worker status", **status)
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        await lifecycle.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Logging with Structured Data

```python
from boarhiro.logger import get_logger, configure_logging

configure_logging(json_output=False, debug=False)
logger = get_logger("trainer")

logger.info("Training started", 
    epoch=1,
    learning_rate=0.001,
    batch_size=32,
    model="boarhiro-brain",
)

logger.warning("High loss detected",
    loss=1.5,
    threshold=1.0,
    epoch=5,
)
```

### Server Communication

```python
from boarhiro.api import ServerClient
from boarhiro.utils import ServerError

client = ServerClient("http://localhost:5000")

try:
    # Check health
    if not client.health_check():
        print("Server offline")
        exit(1)
    
    # Generate response
    response = client.generate("What is AI?", temperature=0.7)
    print(f"Response: {response}")
    
except ServerError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.context}")
```

---

## Testing

Test the API:

```bash
# Test imports
python -c "from boarhiro.config import AgentConfig; print(AgentConfig())"
python -c "from boarhiro.logger import get_logger; l = get_logger('test'); l.info('OK')"
python -c "from boarhiro.agent import AgentWorker; print('✓')"
python -c "from boarhiro.api import ServerClient; print('✓')"

# Test configuration validation
python -c "
from boarhiro.config import AgentConfig, WorkerConfig
try:
    WorkerConfig(max_concurrent_jobs=0)
except ValueError as e:
    print(f'Validation: {e}')
"
```

---

## Backward Compatibility

All new APIs are additive. Existing code continues to work:

```python
# Legacy imports still work
from boarhiro.trainer import main as train_main
from boarhiro.server import app
from boarhiro.interface import run_cli

# New modules available
from boarhiro.config import AgentConfig
from boarhiro.logger import get_logger
from boarhiro.agent import AgentWorker
```

---

## Version

- **API Version:** 0.2.0
- **Python Version:** 3.10+
- **Last Updated:** 2026-05-13
