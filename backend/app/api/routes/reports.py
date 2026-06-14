from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.report import UserReportCreateRequest
from app.services.report_service import service as report_service

router = APIRouter()


@router.post('/users', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_user_report(
    payload: UserReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        report = report_service.create_user_report(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(
        message='举报提交成功',
        data=report.model_dump(mode='json'),
    )
