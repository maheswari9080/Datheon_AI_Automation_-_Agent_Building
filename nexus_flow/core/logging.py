"""Structured operational and audit logging for NEXUS Flow AI."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class JSONLogFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if hasattr(record, "execution_id"):
            log_data["execution_id"] = record.execution_id
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logger(name: str = "nexus_flow", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONLogFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = setup_logger()

def log_audit_event(
    event_type: str,
    action: str,
    status: str,
    entity_id: Optional[str] = None,
    duration_ms: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Convenience helper to output uniform structured audit events."""
    payload = {
        "event_type": event_type,
        "action": action,
        "status": status,
        "entity_id": entity_id,
        "duration_ms": duration_ms,
        "details": details or {},
    }
    logger.info(
        f"AUDIT: [{event_type}] {action} -> {status} (id={entity_id})",
        extra={
            "event_type": event_type,
            "duration_ms": duration_ms,
            "extra_data": payload,
        },
    )
