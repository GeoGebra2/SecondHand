from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.user import User
from app.models.user_report import UserReport
from app.schemas.report import UserReportCreateRequest, UserReportResponse


class ReportService:
    def create_user_report(
        self,
        db: Session,
        reporter: User,
        payload: UserReportCreateRequest,
    ) -> UserReportResponse:
        if reporter.user_id == payload.reported_user_id:
            raise ValueError('不能举报自己')

        reported_user = db.get(User, payload.reported_user_id)
        if reported_user is None:
            raise ValueError('被举报用户不存在')

        report = UserReport(
            reporter_id=reporter.user_id,
            reported_user_id=payload.reported_user_id,
            reason=payload.reason,
            description=payload.description,
            status='PENDING',
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return self._build_report_response(db, report.report_id)

    def list_user_reports(self, db: Session) -> list[UserReportResponse]:
        rows = db.execute(self._build_report_query().order_by(UserReport.create_time.desc())).mappings().all()
        return [UserReportResponse.model_validate(row) for row in rows]

    def _build_report_response(self, db: Session, report_id: int) -> UserReportResponse:
        row = db.execute(self._build_report_query().where(UserReport.report_id == report_id)).mappings().first()
        if row is None:
            raise ValueError('举报记录不存在')
        return UserReportResponse.model_validate(row)

    def _build_report_query(self):
        reporter = aliased(User)
        reported_user = aliased(User)
        return (
            select(
                UserReport.report_id,
                UserReport.reporter_id,
                reporter.user_name.label('reporter_name'),
                UserReport.reported_user_id,
                reported_user.user_name.label('reported_user_name'),
                UserReport.reason,
                UserReport.description,
                UserReport.status,
                UserReport.create_time,
                UserReport.update_time,
            )
            .join(reporter, reporter.user_id == UserReport.reporter_id)
            .join(reported_user, reported_user.user_id == UserReport.reported_user_id)
        )


service = ReportService()
