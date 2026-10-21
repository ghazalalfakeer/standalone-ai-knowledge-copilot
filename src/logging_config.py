"""Structured JSON logging helper for the application."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format each application log record as a JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field in ("event", "path", "result_count"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = str(value) if field == "path" else value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def get_structured_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a logger configured with one-line JSON output."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    has_copilot_handler = any(
        getattr(handler, "_copilot_json_handler", False)
        for handler in logger.handlers
    )

    if not has_copilot_handler:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        handler._copilot_json_handler = True  # type: ignore[attr-defined]
        logger.addHandler(handler)

    return logger
