from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.connections import router as connections_router
from app.core.config import get_settings
from app.db.indexes import create_indexes
from app.db.mongodb import mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    await mongodb.connect()
    await create_indexes()

    yield

    await mongodb.disconnect()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(
    connections_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }