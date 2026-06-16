from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_optional_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.recommendation import BrowseRecordRequest
from app.services.recommendation_service import service as recommendation_service

router = APIRouter()


@router.get('/recommendations', response_model=ApiResponse)
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> ApiResponse:
    payload = recommendation_service.get_recommendations(db, current_user)
    return ApiResponse(
        message='获取智能推荐成功',
        data=payload.model_dump(mode='json'),
    )


@router.post('/recommendations/browse-history', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_browse_history(
    payload: BrowseRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        recorded_count = recommendation_service.record_browse_history(db, current_user, payload.product_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(
        message='浏览行为记录成功',
        data={'recorded_count': recorded_count},
    )
