"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.logging import RequestLoggingMiddleware, configure_logging
from app.routers import backups, dashboard, devices, identity, incidents, integrations, tasks

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    configure_logging(settings.log_level)
    logger.info("Starting CyberShield Control Center API — env=%s", settings.environment)

    # Initialize database schema
    from app.database import init_db

    await init_db()
    logger.info("Database initialized")

    # Seed demo data if running in development and DB is empty
    if settings.environment == "development":
        from app.seed import seed_demo_data

        await seed_demo_data()

    # Start background sync scheduler
    from app.services.sync_jobs import start_scheduler

    start_scheduler()

    yield

    # Shutdown
    from app.services.sync_jobs import stop_scheduler

    stop_scheduler()
    logger.info("Scheduler stopped. Shutdown complete.")


app = FastAPI(
    title="CyberShield Control Center",
    description="Small business cybersecurity dashboard API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow Next.js dev server and configured frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# Routers
app.include_router(dashboard.router)
app.include_router(identity.router)
app.include_router(devices.router)
app.include_router(backups.router)
app.include_router(incidents.router)
app.include_router(tasks.router)
app.include_router(integrations.router)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for load balancers and container orchestration."""
    from app.database import engine

    # Verify DB connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.environment,
    }


@app.get("/")
async def root() -> dict:
    return {
        "name": "CyberShield Control Center API",
        "version": "1.0.0",
        "docs": "/docs",
    }
