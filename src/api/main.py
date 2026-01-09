"""Main FastAPI application."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.slots import router as slots_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown operations.
    """
    # Startup
    logger.info("🚀 Starting horas-registro-civil API")
    logger.info("Real-time Playwright scraping enabled")

    yield

    # Shutdown
    logger.info("Shutting down API")


app = FastAPI(
    title="horas-registro-civil",
    description="FastAPI backend for Chile's SRCEI civil registry appointment slots with real-time Playwright scraping",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - allow all origins (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Include routers
app.include_router(slots_router)


@app.get("/")
def read_root() -> dict:
    """Root endpoint - health check and API info."""
    return {
        "message": "horas-registro-civil API",
        "status": "healthy",
        "version": "0.1.0",
        "endpoints": {
            "slots": "GET /slots?procedure_id=6&region_id=13",
            "docs": "GET /docs",
        },
    }
