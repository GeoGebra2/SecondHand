from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.review import ReviewCreateRequest
from app.services.review_service import service as review_service

router = APIRouter()


@router.post('', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        review = review_service.create_review(db, current_user, payload)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(
        message='评价提交成功',
        data=review.model_dump(mode='json'),
    )


@router.get('/order/{order_id}', response_model=ApiResponse)
def list_order_reviews(
    order_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse:
    reviews = review_service.list_order_reviews(db, order_id)
    return ApiResponse(
        message='获取订单评价成功',
        data=[review.model_dump(mode='json') for review in reviews],
    )
