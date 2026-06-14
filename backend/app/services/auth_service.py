from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.user_service import service as user_service

settings = get_settings()


class AuthService:
    def register(self, db: Session, payload: RegisterRequest) -> User:
        student_exists = db.scalar(
            select(User).where(User.student_no == payload.student_no)
        )
        if student_exists:
            raise ValueError('该学号已注册')

        email_exists = db.scalar(select(User).where(User.email == payload.email))
        if email_exists:
            raise ValueError('该邮箱已注册')

        user = User(
            student_no=payload.student_no,
            user_name=payload.user_name,
            gender=payload.gender,
            phone=payload.phone,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role='student',
            credit_score=100,
            status='active',
            verify_status='verified',
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, payload: LoginRequest) -> TokenResponse:
        user = db.scalar(
            select(User).where(
                or_(User.student_no == payload.account, User.email == payload.account)
            )
        )
        if not user or not verify_password(payload.password, user.password_hash):
            raise ValueError('账号或密码错误')

        if user.status != 'active':
            raise ValueError('当前账号不可登录')

        user.last_login_time = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)

        return TokenResponse(
            access_token=create_access_token(user.user_id, user.role),
            expires_in=settings.jwt_expire_minutes * 60,
            user=user_service.get_profile(db, user),
        )


service = AuthService()
