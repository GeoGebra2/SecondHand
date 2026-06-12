from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.social import FavoriteCreateRequest, NotificationCreateRequest
from app.services.social_service import service as social_service

router = APIRouter()


@router.get('/favorites', response_model=ApiResponse)
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    favorites = social_service.list_favorites(db, current_user)
    return ApiResponse(
        message='获取收藏列表成功',
        data=[favorite.model_dump(mode='json') for favorite in favorites],
    )


@router.post('/favorites', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_favorite(
    payload: FavoriteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        social_service.add_favorite(db, current_user, payload.product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(message='收藏成功', data={'product_id': payload.product_id})


@router.delete('/favorites/{product_id}', response_model=ApiResponse)
def delete_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        social_service.remove_favorite(db, current_user, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(message='取消收藏成功', data={'product_id': product_id})


@router.get('/notifications', response_model=ApiResponse)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    notifications = social_service.list_notifications(db, current_user)
    return ApiResponse(
        message='获取通知成功',
        data=[notification.model_dump(mode='json') for notification in notifications],
    )


@router.post('/notifications', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        notification = social_service.create_notification(db, payload.receiver_id, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(
        message='通知发送成功',
        data=notification.model_dump(mode='json'),
    )
