from fastapi import APIRouter, HTTPException, Query
from starlette import status
from backend.schemas.event import PaginatedEventResponse

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.get(
    "/",
    response_model=PaginatedEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Поиск событий",
)
async def search_events(
    q: str = Query(..., description="Поисковый запрос"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> PaginatedEventResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )