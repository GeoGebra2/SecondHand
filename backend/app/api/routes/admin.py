from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services.credit_service import service as credit_service
from app.services.dashboard_service import service as dashboard_service

router = APIRouter()


@router.get('/dashboard', response_model=ApiResponse)
def get_dashboard() -> ApiResponse:
    cards = [card.model_dump() for card in dashboard_service.get_dashboard_cards()]
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


@router.get('/credit-analysis', response_model=ApiResponse)
def get_credit_analysis(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ApiResponse:
    analyses = credit_service.analyze_users(db)
    return ApiResponse(
        message='获取用户信用评估与异常行为分析成功',
        data=[analysis.model_dump(mode='json') for analysis in analyses],
    )
