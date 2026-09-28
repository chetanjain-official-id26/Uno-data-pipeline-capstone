
import logging

from fastapi import APIRouter, HTTPException

from src.schema.request_response_schema.preview import (
    PreviewRequest,
    PreviewResponse,
)
from src.services.preview_service import (
    PreviewService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/preview",
    tags=["Preview"],
)


service = PreviewService()


@router.post(
    "",
    response_model=PreviewResponse,
)
async def preview(
    request: PreviewRequest,
) -> PreviewResponse:

    try:

        result = await service.preview(
            connection_id=request.connection_id,
        )

        return PreviewResponse(
            **result
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "preview_execution_failed",
            extra={
                "connection_id": (
                    request.connection_id
                ),
            },
        )

        # Keep actual error visible while debugging.
        raise HTTPException(
            status_code=500,
            detail=f"Preview failed: {exc}",
        ) from exc

