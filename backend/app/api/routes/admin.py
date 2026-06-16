from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.social import Notification
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services.credit_service import service as credit_service
from app.services.dashboard_service import service as dashboard_service
from app.services.report_service import service as report_service

router = APIRouter()


@router.get('/dashboard', response_model=ApiResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ApiResponse:
    stats = dashboard_service.get_dashboard_stats(db)
    return ApiResponse(message='获取后台统计成功', data=stats.model_dump(mode='json'))


@router.get('/reports', response_model=ApiResponse)
def list_reports(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ApiResponse:
    reports = report_service.list_user_reports(db)
    return ApiResponse(
        message='获取举报队列成功',
        data=[report.model_dump(mode='json') for report in reports],
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


@router.patch('/users/{user_id}/block', response_model=ApiResponse)
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> ApiResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    if user.user_id == current_admin.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='不能拉黑当前管理员账号')
    if user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='不能拉黑管理员账号')

    user.status = 'blocked'
    db.add(user)
    db.add(Notification(receiver_id=user.user_id, content='你的账号已被管理员拉黑，普通交易功能将被限制。'))
    db.commit()
    db.refresh(user)
    return ApiResponse(
        message='用户已拉黑',
        data={'user_id': user.user_id, 'user_name': user.user_name, 'status': user.status},
    )


@router.patch('/users/{user_id}/unblock', response_model=ApiResponse)
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ApiResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')

    user.status = 'active'
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(
        message='用户已恢复',
        data={'user_id': user.user_id, 'user_name': user.user_name, 'status': user.status},
    )
