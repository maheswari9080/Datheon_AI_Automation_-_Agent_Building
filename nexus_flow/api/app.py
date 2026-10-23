"""FastAPI application factory for NEXUS Flow AI."""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from nexus_flow.core.config import get_settings
from nexus_flow.core.logging import logger
from nexus_flow.db.session import init_db
from nexus_flow.api.routes import (
    leads_router,
    support_router,
    invoices_router,
    orchestration_router,
    webhooks_router,
    metrics_router,
)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure SQLite tables exist
    init_db()
    logger.info(f"NEXUS Flow AI v{settings.app_version} initialized. Mode: {'LIVE' if settings.live_mode else 'DEMO/MOCK'}")
    yield
    # Shutdown
    logger.info("NEXUS Flow AI shutting down.")

app = FastAPI(
    title="NEXUS Flow AI — Intelligent Business Automation Hub",
    description="Autonomous enterprise operations platform integrating Lead, Support, Invoice, and Enterprise Orchestration.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(leads_router, prefix="/api/v1")
app.include_router(support_router, prefix="/api/v1")
app.include_router(invoices_router, prefix="/api/v1")
app.include_router(orchestration_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")

# Mount Static UI Files if static directory exists
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(static_dir / "index.html")

def run():
    import uvicorn
    uvicorn.run("nexus_flow.api.app:app", host=settings.host, port=settings.port, reload=settings.debug)

if __name__ == "__main__":
    run()
