"""Base integration adapter abstraction with latency tracking and mock/live routing."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from nexus_flow.core.config import get_settings
from nexus_flow.core.logging import logger

class BaseAdapter(ABC):
    """
    Abstract Base Class for all external third-party integration adapters.
    Guarantees deterministic mock responses when live credentials are absent.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.settings = get_settings()

    @property
    def is_live_mode(self) -> bool:
        return self.settings.live_mode

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Verify integration readiness and report status."""
        pass

    def execute_with_telemetry(self, operation_name: str, func, *args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Adapter [{self.service_name}] operation '{operation_name}' succeeded in {duration_ms:.2f}ms"
            )
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Adapter [{self.service_name}] operation '{operation_name}' failed after {duration_ms:.2f}ms: {str(e)}"
            )
            raise
