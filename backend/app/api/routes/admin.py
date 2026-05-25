from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services.dashboard_service import service

router = APIRouter()


@router.get('/dashboard', response_model=ApiResponse)
def get_dashboard() -> ApiResponse:
    cards = [card.model_dump() for card in service.get_dashboard_cards()]
    return ApiResponse(message='admin dashboard placeholder', data=cards)


@router.get('/reports', response_model=ApiResponse)
def list_reports() -> ApiResponse:
    return ApiResponse(
        message='report queue placeholder',
        data=[
            {'id': 101, 'reason': '虚假图片', 'status': 'PENDING'},
            {'id': 102, 'reason': '疑似刷单', 'status': 'REVIEWING'},
        ],
    )
