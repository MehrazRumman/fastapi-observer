# Handlers

The package currently ships with console and file logging handlers.

## Console handler

`build_console_handler(formatter)` returns a standard `logging.StreamHandler` configured with the provided formatter.

## File handler

`build_file_handler(config, formatter)` returns a rotating file handler.

- `config.file_path` is required
- `config.file_max_bytes` controls rotation size
- `config.file_backup_count` controls retained backups

## Handler order

`build_handlers(config, formatter)` preserves the order from `config.handlers`.

```python
from fastapi_inspector import ObserverConfig
from fastapi_inspector.handlers import build_handlers
from fastapi_inspector.formatters import JsonFormatter

config = ObserverConfig(handlers=["file", "console"], file_path="logs/api.log")
handlers = build_handlers(config, JsonFormatter())
```
