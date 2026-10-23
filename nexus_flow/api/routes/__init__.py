"""API route blueprints for NEXUS Flow AI."""

from nexus_flow.api.routes.leads import router as leads_router
from nexus_flow.api.routes.support import router as support_router
from nexus_flow.api.routes.invoices import router as invoices_router
from nexus_flow.api.routes.orchestration import router as orchestration_router
from nexus_flow.api.routes.webhooks import router as webhooks_router
from nexus_flow.api.routes.metrics import router as metrics_router

__all__ = [
    "leads_router",
    "support_router",
    "invoices_router",
    "orchestration_router",
    "webhooks_router",
    "metrics_router",
]
