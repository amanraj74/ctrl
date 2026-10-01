"""FastAPI application entry point — routes, CORS, startup/shutdown."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import batch, export, health, jobs, trends
from app.config import settings
from app.core.worker import start_workers, stop_workers
from app.db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown tasks."""
    # Startup
    logger.info("═══ QoneqtForge Backend Starting ═══")
    init_db()
    await start_workers()
    logger.info("═══ QoneqtForge Backend Ready ═══")

    yield

    # Shutdown
    logger.info("═══ QoneqtForge Backend Shutting Down ═══")
    await stop_workers()


# Create FastAPI app
app = FastAPI(
    title="QoneqtForge",
    description="LLM-Powered Content Pipeline for Qoneqt",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jobs.router)
app.include_router(batch.router)
app.include_router(trends.router)
app.include_router(export.router)
app.include_router(health.router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "QoneqtForge",
        "version": "1.0.0",
        "description": "LLM-Powered Content Pipeline for Qoneqt",
        "docs": "/docs",
        "health": "/api/health",
    }
