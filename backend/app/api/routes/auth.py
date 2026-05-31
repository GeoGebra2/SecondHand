from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.common import ApiResponse
from app.schemas.user import UserProfileResponse, UserProfileUpdateRequest
from app.services.auth_service import service as auth_service
from app.services.user_service import service as user_service

router = APIRouter()


@router.post('/register', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    try:
        user = auth_service.register(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='注册成功',
        data=UserProfileResponse.model_validate(user).model_dump(mode='json'),
    )


@router.post('/login', response_model=ApiResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    try:
        token = auth_service.login(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='登录成功',
        data=token.model_dump(mode='json'),
    )


@router.get('/me', response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)) -> ApiResponse:
    return ApiResponse(
        message='获取个人资料成功',
        data=user_service.get_profile(current_user).model_dump(mode='json'),
    )


@router.put('/me', response_model=ApiResponse)
def update_me(
    payload: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        updated_user = user_service.update_profile(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='个人资料更新成功',
        data=UserProfileResponse.model_validate(updated_user).model_dump(mode='json'),
    )


@router.post('/logout', response_model=ApiResponse)
def logout(_: User = Depends(get_current_user)) -> ApiResponse:
    return ApiResponse(
        message='退出登录成功',
        data={'logged_out': True},
    )
