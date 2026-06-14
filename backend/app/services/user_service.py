from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.schemas.user import NotificationResponse, UserProfileResponse, UserProfileUpdateRequest, UserStatusResponse
from app.services.credit_service import service as credit_service


class UserService:
    def get_profile(self, db: Session, user: User) -> UserProfileResponse:
        profile = UserProfileResponse.model_validate(user)
        risk_profile = credit_service.get_user_risk_profile(db, user.user_id)
        profile.credit_score = risk_profile.computed_score
        return profile

    def get_status(self, db: Session, user: User) -> UserStatusResponse:
        profile = self.get_profile(db, user)
        risk_profile = credit_service.get_user_risk_profile(db, user.user_id)
        notifications = db.scalars(
            select(Notification)
            .where(Notification.receiver_id == user.user_id)
            .order_by(Notification.create_time.desc())
            .limit(20)
        ).all()
        return UserStatusResponse(
            user=profile,
            computed_score=risk_profile.computed_score,
            credit_level=risk_profile.credit_level,
            risk_level=risk_profile.risk_level,
            warning_reasons=risk_profile.warning_reasons,
            notifications=[NotificationResponse.model_validate(notification) for notification in notifications],
        )

    def update_profile(
        self,
        db: Session,
        user: User,
        payload: UserProfileUpdateRequest,
    ) -> UserProfileResponse:
        updates = payload.model_dump(exclude_unset=True)

        if 'email' in updates and updates['email'] != user.email:
            existing_user = db.scalar(
                select(User).where(
                    User.email == updates['email'],
                    User.user_id != user.user_id,
                )
            )
            if existing_user:
                raise ValueError('该邮箱已被其他用户使用')

        for field, value in updates.items():
            setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return self.get_profile(db, user)


service = UserService()
