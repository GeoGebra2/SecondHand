from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.post('/login', response_model=ApiResponse)
def login() -> ApiResponse:
    return ApiResponse(
        message='login endpoint placeholder',
        data={'token': 'demo-token', 'role': 'student'},
    )


@router.post('/register', response_model=ApiResponse)
def register() -> ApiResponse:
    return ApiResponse(
        message='register endpoint placeholder',
        data={'status': 'pending_verification'},
    )
