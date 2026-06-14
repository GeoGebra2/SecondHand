from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services.dashboard_service import service as dashboard_service

router = APIRouter()


@router.get('/dashboard', response_model=ApiResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ApiResponse:
    stats = dashboard_service.get_dashboard_stats(db)
    return ApiResponse(message='获取后台统计成功', data=stats.model_dump(mode='json'))


@router.get('/reports', response_model=ApiResponse)
def list_reports(_: User = Depends(get_current_admin)) -> ApiResponse:
    return ApiResponse(
        message='获取举报队列成功',
        data=[
            {'id': 101, 'reason': '虚假图片', 'status': 'PENDING'},
            {'id': 102, 'reason': '疑似刷单', 'status': 'REVIEWING'},
        ],
    )
