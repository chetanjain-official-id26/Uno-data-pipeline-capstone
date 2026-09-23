from fastapi import APIRouter, HTTPException, status

from src.schema.request_response_schema.transform import (
    PreviewRequest,
    PreviewResponse,
)
from src.services.preview_service import PreviewService

router = APIRouter(
    tags=["Preview"],
)


@router.post(
    "/connections/{connection_id}/transformations/{step_order}/preview",
    response_model=PreviewResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_transformation(
    connection_id: str,
    step_order: int,
    request: PreviewRequest,
):
    """Preview a specific transformation step for a connection."""
    if not connection_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    if step_order < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step order must be greater than or equal to 1",
        )

    service = PreviewService()

    try:
        result = await service.preview(
            connection_id=connection_id,
            step_order=step_order,
            preview_limit=request.limit,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc