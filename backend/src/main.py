
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from core.config import get_settings
from src.utils.logging import setup_logging
from database import create_indexes
from database import mongodb

from src.exceptions.exception_handlers import (
    app_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from src.exceptions.exceptions import AppException

from src.middleware.request_id import (
    RequestIDMiddleware,
)

from src.routers.connections import (
    router as connections_router,
)
from src.routers.deployment import (
    router as deployments_router,
)
from src.routers.pipelines import (
    router as pipelines_router,
)
from src.routers.preview import (
    router as preview_router,
)
from src.routers.run import (
    router as runs_router,
)
from src.routers.targets import (
    router as targets_router,
)
from src.routers.transformations import (
    router as transformations_router,
)


settings = get_settings()

API_PREFIX = "/api/v1"


# =========================================================
# Application lifecycle
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.

    Startup:
    - Connect to MongoDB.
    - Create required indexes.

    Shutdown:
    - Disconnect from MongoDB.
    """

    await mongodb.connect()

    setup_logging()
    await create_indexes()

    yield

    await mongodb.disconnect()


# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)


# =========================================================
# Middleware
# =========================================================

app.add_middleware(
    RequestIDMiddleware,
)


# =========================================================
# Exception handlers
# =========================================================

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


# =========================================================
# Core APIs
# =========================================================

app.include_router(
    connections_router,
    prefix=API_PREFIX,
)

app.include_router(
    pipelines_router,
    prefix=API_PREFIX,
)

app.include_router(
    transformations_router,
    prefix=API_PREFIX,
)

app.include_router(
    preview_router,
    prefix=API_PREFIX,
)

app.include_router(
    targets_router,
    prefix=API_PREFIX,
)


# =========================================================
# Deployment API
# =========================================================
#
# Example:
#
# POST /api/v1/pipelines/{pipeline_id}/deploy
#
# Responsible for:
# - validating pipeline configuration
# - building pipeline wheel
# - creating deployment manifest
# - uploading artifact to S3
# - creating/updating Airflow DAG
# - preparing Databricks execution configuration
#

app.include_router(
    deployments_router,
    prefix=API_PREFIX,
)


# =========================================================
# Run API
# =========================================================
#
# Example:
#
# POST /api/v1/pipelines/{pipeline_id}/run
#
# Responsible for:
# - validating that pipeline is deployed
# - creating a pipeline run
# - triggering Airflow
# - returning the run ID
#
# Status can subsequently be queried using the run API.
#

app.include_router(
    runs_router,
    prefix=API_PREFIX,
)


# =========================================================
# Health
# =========================================================

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }

