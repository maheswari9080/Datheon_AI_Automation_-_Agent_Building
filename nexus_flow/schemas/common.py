"""Common API and audit response contracts."""

from typing import Any, Generic, List, Optional, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

DataT = TypeVar("DataT")

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None

class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[DataT] = None
    errors: Optional[List[ErrorDetail]] = None
    execution_time_ms: Optional[float] = None

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"
    mode: str = "demo"  # or 'live'
    uptime_seconds: float = 0.0
    database_connected: bool = True
    services: dict = Field(default_factory=dict)

class AuditEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    action: str
    status: str
    entity_id: Optional[str] = None
    duration_ms: Optional[float] = None
    details_json: Optional[str] = None
    created_at: datetime

