from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.get('', response_model=ApiResponse)
def health_check() -> ApiResponse:
    return ApiResponse(message='service is healthy', data={'status': 'ok'})
