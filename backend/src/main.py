from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.routers.connections import (
    router as connections_router,
)
from src.routers.targets import (
    router as targets_router,
)
from src.routers.transformations import (
    router as transformations_router,
)

from src.routers.pipelines import (
    router as pipelines_router,
)

from src.routers.preview import (
    router as preview_router,
)

from core.config import get_settings
from src.exceptions.exception_handlers import (
    app_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from src.exceptions.exceptions import AppException

from database import create_indexes
from database import mongodb
from src.middleware.request_id import (
    RequestIDMiddleware,
)




settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    await mongodb.connect()

    await create_indexes()

    yield

    await mongodb.disconnect()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)


app.add_middleware(
    RequestIDMiddleware
)


app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)


app.include_router(
    connections_router,
    prefix="/api/v1",
)

app.include_router(
    pipelines_router,
    prefix="/api/v1",
)

app.include_router(
    transformations_router,
    prefix="/api/v1",
)

app.include_router(
    preview_router,
    prefix="/api/v1",
)
app.include_router(
    targets_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "service": settings.app_name,
    }